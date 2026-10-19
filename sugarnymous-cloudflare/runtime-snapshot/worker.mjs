
const ORIGIN = "https://sugarnymous-prerelease.floot.app";
const MAX_BODY_BYTES = 1_000_000;
let appPromise;

function json(body, status = 200) {
  return Response.json(body, {
    status,
    headers: { "Cache-Control": "no-store", "X-Sugarnymous-Backend": "cloudflare-native" }
  });
}

function constantTimeEqual(expected, received) {
  if (typeof expected !== "string" || !expected || typeof received !== "string") return false;
  const encoder = new TextEncoder();
  const left = encoder.encode(expected);
  const right = encoder.encode(received);
  let diff = left.length ^ right.length;
  const max = Math.max(left.length, right.length);
  for (let i = 0; i < max; i += 1) diff |= (left[i] ?? 0) ^ (right[i] ?? 0);
  return diff === 0;
}

function configureRuntime(env) {
  if (typeof globalThis.process === "undefined") {
    Object.defineProperty(globalThis, "process", { value: { env: Object.create(null) }, configurable: true });
  }
  const processEnv = globalThis.process.env || (globalThis.process.env = Object.create(null));
  processEnv.TELEGRAM_BOT_TOKEN = env.TELEGRAM_BOT_TOKEN || "";
  processEnv.TELEGRAM_WEBHOOK_SECRET = env.TELEGRAM_WEBHOOK_SECRET || "";
  processEnv.TELEGRAM_SETUP_SECRET = env.TELEGRAM_SETUP_SECRET || "";
  globalThis.__SUGARNYMOUS_DB_URL = env.HYPERDRIVE?.connectionString || "";
}

async function loadApp(env) {
  configureRuntime(env);
  if (!env.HYPERDRIVE?.connectionString) throw new Error("Hyperdrive is not configured");
  if (!appPromise) appPromise = import("./telegramBundle.mjs");
  return await appPromise;
}

function withTimeout(promise, milliseconds, reason) {
  let timer;
  return Promise.race([
    promise,
    new Promise((_, reject) => { timer = setTimeout(() => reject(new Error(reason)), milliseconds); })
  ]).finally(() => clearTimeout(timer));
}

// This isolate-local queue protects the mutable Kysely export from concurrent
// request swaps. Cloudflare may run concurrent fetch events in one isolate.
let databaseQueue = Promise.resolve();
function withDatabaseLock(task) {
  const operation = databaseQueue.then(task, task);
  databaseQueue = operation.then(() => undefined, () => undefined);
  return operation;
}

async function closeRequestDatabase(app) {
  if (!app || typeof app.closeDatabase !== "function") return;
  // postgres.js end({timeout}) rejects pending queries and destroys sockets.
  // Bound the outer wait as well; a timed-out query must not hold the queue forever.
  await withTimeout(app.closeDatabase(), 2000, "database_close_timeout").catch(() => {});
}

// Admin-only functional smoke test. It uses temporary synthetic rows and
// replaces this isolate's Telegram API fetch with a local stub. The DB lock
// prevents a real webhook in this isolate from observing the stub.
async function nativeSmoke(request, env) {
  if (request.method !== "POST") return json({ ok: false, stage: "cloudflare-native-smoke", reason: "method_not_allowed" }, 405);
  if (!env.TELEGRAM_SETUP_SECRET) return json({ ok: false, stage: "cloudflare-native-smoke", reason: "smoke_secret_unconfigured" }, 503);
  const received = request.headers.get("x-sugarnymous-smoke-secret") || "";
  if (!constantTimeEqual(env.TELEGRAM_SETUP_SECRET, received)) return json({ ok: false, stage: "cloudflare-native-smoke", reason: "unauthorized" }, 401);

  let app;
  try {
    app = await withTimeout(loadApp(env), 10000, "runtime_init_timeout");
  } catch {
    return json({ ok: false, stage: "cloudflare-native-smoke", reason: "runtime_init_failed" }, 503);
  }

  const checks = {
    runtimeLoaded: false,
    databaseRead: false,
    outboxStateContract: false,
    updateIdUniqueness: false,
    idempotentDuplicateUpdate: false,
    outboxSingleDelivery: false,
    outboxRetryRetainsPayload: false,
    bilingualMenuFlows: false,
    bilingualPrivacyFlows: false,
    syntheticRowsCleaned: false,
    syntheticUsersCleaned: false
  };
  const cleanupIds = [];
  const cleanupUserIds = [];
  let sql;
  let databaseConfigured = false;
  let originalFetch;
  let fetchReplaced = false;
  const mockCallCounts = Object.create(null);
  const mockTelegramPayloads = [];

  await withDatabaseLock(async () => {
    try {
      await app.resetDatabase(env.HYPERDRIVE.connectionString);
      databaseConfigured = true;
      checks.runtimeLoaded = typeof app.telegramBot?.processUpdate === "function"
        && typeof app.telegramBot?.flushOutbox === "function";

      await app.db.selectFrom("users").select("telegramId").limit(1).executeTakeFirst();
      await app.db.selectFrom("botOutbox").select("status").limit(1).executeTakeFirst();
      checks.databaseRead = true;

      sql = app.createPostgres(env.HYPERDRIVE.connectionString, {
        prepare: true, fetch_types: false, max: 1, idle_timeout: 10, connect_timeout: 15
      });
      const constraints = await sql.unsafe(
        "SELECT conname, pg_get_constraintdef(oid) AS definition FROM pg_constraint WHERE conrelid IN ('public.bot_outbox'::regclass, 'public.telegram_updates'::regclass)",
        [], { prepare: true, simple: false }
      );
      const statusDefinition = String(constraints.find((row) => row.conname === "bot_outbox_status_check")?.definition ?? "");
      checks.outboxStateContract = ["pending", "sending", "indeterminate", "sent", "failed"]
        .every((state) => statusDefinition.includes("'" + state + "'"));
      checks.updateIdUniqueness = constraints.some((row) => row.conname === "telegram_updates_pkey" && /PRIMARY KEY \(update_id\)/.test(String(row.definition)))
        && constraints.some((row) => row.conname === "bot_outbox_update_id_key" && /UNIQUE \(update_id\)/.test(String(row.definition)));

      // The minimal update has no message or callback: claim once, recognize
      // the redelivery as a duplicate, and avoid any Telegram API call.
      const syntheticNumericId = 8000000000000 + (Date.now() % 1000000000);
      const syntheticUpdateId = String(syntheticNumericId);
      cleanupIds.push(syntheticUpdateId);
      const firstUpdate = await app.telegramBot.processUpdate({ update_id: syntheticNumericId }, new URL(request.url).origin);
      const duplicateUpdate = await app.telegramBot.processUpdate({ update_id: syntheticNumericId }, new URL(request.url).origin);
      const claimedRows = await app.db.selectFrom("telegramUpdates").select("updateId")
        .where("updateId", "=", syntheticUpdateId).execute();
      checks.idempotentDuplicateUpdate = firstUpdate?.outcome === "empty" && duplicateUpdate?.outcome === "empty" && claimedRows.length === 1;

      const singleDeliveryId = "smoke-single-" + Date.now() + "-" + Math.floor(Math.random() * 1000000000);
      const retryDeliveryId = "smoke-retry-" + Date.now() + "-" + Math.floor(Math.random() * 1000000000);
      cleanupIds.push(singleDeliveryId, retryDeliveryId);
      for (const updateId of [singleDeliveryId, retryDeliveryId]) {
        await app.db.insertInto("telegramUpdates").values({ updateId }).execute();
      }
      await app.db.insertInto("botOutbox").values({
        updateId: singleDeliveryId,
        payload: { method: "sendMessage", data: { chat_id: "0", text: "SMOKE_SINGLE_DELIVERY" } },
        status: "pending"
      }).execute();
      await app.db.insertInto("botOutbox").values({
        updateId: retryDeliveryId,
        payload: { method: "sendMessage", data: { chat_id: "0", text: "SMOKE_RATE_LIMIT" } },
        status: "pending"
      }).execute();

      originalFetch = globalThis.fetch;
      const mockFetch = async (input, init) => {
        const target = typeof input === "string" ? input : input instanceof Request ? input.url : String(input);
        if (!target.startsWith("https://api.telegram.org/bot")) return originalFetch(input, init);
        let payload = {};
        try { payload = JSON.parse(typeof init?.body === "string" ? init.body : "{}"); } catch {}
        const key = String(payload.text ?? "unknown");
        mockCallCounts[key] = (mockCallCounts[key] ?? 0) + 1;
        mockTelegramPayloads.push({ method: target.split("/").pop(), payload });
        if (key === "SMOKE_RATE_LIMIT" && mockCallCounts[key] === 1) {
          return new Response(JSON.stringify({ ok: false, error_code: 429, description: "Too Many Requests" }), {
            status: 200, headers: { "Content-Type": "application/json" }
          });
        }
        return new Response(JSON.stringify({ ok: true, result: { message_id: 1 } }), {
          status: 200, headers: { "Content-Type": "application/json" }
        });
      };
      globalThis.fetch = mockFetch;
      fetchReplaced = true;

      const sendFirst = await app.telegramBot.flushOutbox(singleDeliveryId);
      const sendSecond = await app.telegramBot.flushOutbox(singleDeliveryId);
      const sentRow = await app.db.selectFrom("botOutbox").selectAll().where("updateId", "=", singleDeliveryId).executeTakeFirst();
      checks.outboxSingleDelivery = sendFirst?.outcome === "sent" && sendSecond?.outcome === "sent"
        && mockCallCounts.SMOKE_SINGLE_DELIVERY === 1 && sentRow?.status === "sent"
        && JSON.stringify(sentRow?.payload ?? null) === "{}";

      const retryFirst = await app.telegramBot.flushOutbox(retryDeliveryId);
      const pendingRow = await app.db.selectFrom("botOutbox").selectAll().where("updateId", "=", retryDeliveryId).executeTakeFirst();
      const payloadRetained = pendingRow?.status === "pending" && pendingRow?.attempts === 1
        && pendingRow?.payload?.data?.text === "SMOKE_RATE_LIMIT";
      const retrySecond = await app.telegramBot.flushOutbox(retryDeliveryId);
      const retriedRow = await app.db.selectFrom("botOutbox").selectAll().where("updateId", "=", retryDeliveryId).executeTakeFirst();
      checks.outboxRetryRetainsPayload = retryFirst?.outcome === "retry_pending" && payloadRetained
        && retrySecond?.outcome === "sent" && mockCallCounts.SMOKE_RATE_LIMIT === 2
        && retriedRow?.status === "sent" && retriedRow?.attempts === 2
        && JSON.stringify(retriedRow?.payload ?? null) === "{}";

      // Exercise real command handlers for both configured languages. These
      // synthetic user IDs never belong to a real Telegram user, and every
      // outbound request remains intercepted by the local API stub above.
      const stamp = Date.now() % 1000000000;
      const englishUserId = 7000000000000 + stamp;
      const indonesianUserId = 7100000000000 + stamp;
      cleanupUserIds.push(String(englishUserId), String(indonesianUserId));
      const commandFlows = [
        { language: "en", command: "/menu", userId: englishUserId, updateId: 8200000000000 + stamp },
        { language: "en", command: "/privacy", userId: englishUserId, updateId: 8200000001000 + stamp },
        { language: "id", command: "/menu", userId: indonesianUserId, updateId: 8200000002000 + stamp },
        { language: "id", command: "/privacy", userId: indonesianUserId, updateId: 8200000003000 + stamp },
      ];
      const flowResults = [];
      for (let index = 0; index < commandFlows.length; index += 1) {
        const flow = commandFlows[index];
        cleanupIds.push(String(flow.updateId));
        const result = await app.telegramBot.processUpdate({
          update_id: flow.updateId,
          message: {
            message_id: index + 1,
            chat: { id: flow.userId, type: "private" },
            from: { id: flow.userId, language_co --- TRUNCATED --- 25,996 chars