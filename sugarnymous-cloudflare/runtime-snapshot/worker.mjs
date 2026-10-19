
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
            from: { id: flow.userId, language_code: flow.language, first_name: "Synthetic smoke" },
            text: flow.command
          }
        }, new URL(request.url).origin);
        flowResults.push({ language: flow.language, command: flow.command, outcome: result?.outcome });
      }

      const deliveredTexts = mockTelegramPayloads
        .filter((item) => item.method === "sendMessage")
        .map((item) => ({
          text: String(item.payload.text ?? ""),
          buttons: (item.payload.reply_markup?.inline_keyboard ?? []).flat().map((button) => String(button.text ?? ""))
        }));
      const englishMenu = deliveredTexts.find((item) => item.text.includes("Choose a destination below."));
      const indonesianMenu = deliveredTexts.find((item) => item.text.includes("Pilih menu di bawah."));
      checks.bilingualMenuFlows = flowResults.filter((item) => item.command === "/menu").length === 2
        && flowResults.filter((item) => item.command === "/menu").every((item) => item.outcome === "sent")
        && !!englishMenu?.buttons.includes("💌 Early Access")
        && !!indonesianMenu?.buttons.includes("💌 Akses Awal");

      const englishPrivacy = deliveredTexts.find((item) => item.text.includes("PRIVACY & SAFETY"));
      const indonesianPrivacy = deliveredTexts.find((item) => item.text.includes("PRIVASI & KEAMANAN"));
      checks.bilingualPrivacyFlows = flowResults.filter((item) => item.command === "/privacy").length === 2
        && flowResults.filter((item) => item.command === "/privacy").every((item) => item.outcome === "sent")
        && !!englishPrivacy?.buttons.includes("Privacy Policy")
        && !!indonesianPrivacy?.buttons.includes("Kebijakan Privasi");
    } catch {
      // Keep response diagnostics free of row contents, IDs, URLs, and secrets.
    } finally {
      if (fetchReplaced && originalFetch) {
        try { globalThis.fetch = originalFetch; } catch {}
      }
      let cleaned = true;
      try {
        for (const updateId of cleanupIds) await app.db.deleteFrom("botOutbox").where("updateId", "=", updateId).execute();
        for (const updateId of cleanupIds) await app.db.deleteFrom("telegramUpdates").where("updateId", "=", updateId).execute();
        for (const userId of cleanupUserIds) await app.db.deleteFrom("userStates").where("telegramId", "=", userId).execute();
        for (const userId of cleanupUserIds) await app.db.deleteFrom("users").where("telegramId", "=", userId).execute();
        for (const updateId of cleanupIds) {
          const update = await app.db.selectFrom("telegramUpdates").select("updateId").where("updateId", "=", updateId).executeTakeFirst();
          const outbox = await app.db.selectFrom("botOutbox").select("updateId").where("updateId", "=", updateId).executeTakeFirst();
          if (update || outbox) cleaned = false;
        }
        checks.syntheticUsersCleaned = true;
        for (const userId of cleanupUserIds) {
          const user = await app.db.selectFrom("users").select("telegramId").where("telegramId", "=", userId).executeTakeFirst();
          if (user) checks.syntheticUsersCleaned = false;
        }
      } catch {
        cleaned = false;
      }
      checks.syntheticRowsCleaned = cleaned;
      if (sql) await sql.end({ timeout: 1 }).catch(() => {});
      if (databaseConfigured) await closeRequestDatabase(app);
    }
  });

  const ok = Object.values(checks).every(Boolean);
  const mockedTelegramApiCalls = Object.values(mockCallCounts).reduce((total, count) => total + count, 0);
  return json({
    ok,
    stage: "cloudflare-native-smoke",
    checks,
    mockedTelegramApiCalls,
    realTelegramMessagesSent: 0,
    syntheticRowsCleaned: checks.syntheticRowsCleaned,
    productionWebhookChanged: false,
    fullMigration: false
  }, ok ? 200 : 503);
}

async function databaseHealth(env) {
  return withDatabaseLock(async () => {
    let stage = "runtime_init";
    let app;
    let requestDbConfigured = false;
    let started = Date.now();
    const timingsMs = {};
    try {
      // A cold dynamic import can take longer than a normal warm request.
      started = Date.now();
      app = await withTimeout(loadApp(env), 10000, "runtime_init_timeout");
      timingsMs.runtimeInit = Date.now() - started;
      stage = "direct_connection_probe";
      // Distinguish transport connectivity from permissions/table access before
      // invoking Kysely; do not perform an aggregate scan just to test readiness.
      let sql;
      let directStep = "select_one";
      try {
        sql = app.createPostgres(env.HYPERDRIVE.connectionString, {
          prepare: true,
          fetch_types: false,
          max: 1,
          idle_timeout: 10,
          connect_timeout: 15
        });
        started = Date.now();
        await withTimeout(
          sql.unsafe("select 1 as health", [], { prepare: true, simple: false }),
          16000,
          "direct_probe_timeout"
        );
        timingsMs.directSelect1 = Date.now() - started;
        directStep = "table_access";
        started = Date.now();
        await withTimeout(
          sql.unsafe('select 1 as health from "users" limit 1', [], { prepare: true, simple: false }),
          8000,
          "direct_users_probe_timeout"
        );
        timingsMs.directUsersSelect = Date.now() - started;
      } catch (error) {
        const message = error && typeof error.message === "string" ? error.message : "";
        if (directStep === "select_one") {
          if (timingsMs.directSelect1 === undefined) timingsMs.directSelect1 = Date.now() - started;
          if (message === "direct_probe_timeout") throw error;
          throw new Error("direct_probe_failed");
        }
        if (timingsMs.directUsersSelect === undefined) timingsMs.directUsersSelect = Date.now() - started;
        if (message === "direct_users_probe_timeout") throw error;
        throw new Error("direct_users_probe_failed");
      } finally {
        if (sql) {
          started = Date.now();
          // Force-close any still-pending direct probe before creating Kysely's client.
          await withTimeout(sql.end({ timeout: 1 }), 1500, "direct_client_close_timeout").catch(() => {});
          timingsMs.directClientClose = Date.now() - started;
        }
      }

      // postgres.js 3.4.9 on Cloudflare Workers can leave reserve() pending
      // forever when Kysely is the first operation on a cold pool. Warm this
      // request-scoped pool with SELECT 1 before Kysely acquires a reservation.
      stage = "kysely_pool_prime";
      const primeStarted = Date.now();
      const primeDuration = await app.resetDatabase(env.HYPERDRIVE.connectionString);
      requestDbConfigured = true;
      timingsMs.kyselyPoolPrime = typeof primeDuration === "number" ? primeDuration : Date.now() - primeStarted;

      // After priming, run a cheap mapped table read, then the aggregate check.
      stage = "kysely_select";
      started = Date.now();
      await withTimeout(
        app.db.selectFrom("users").select("telegramId").limit(1).executeTakeFirst(),
        8000,
        "kysely_select_timeout"
      );
      timingsMs.kyselySelect = Date.now() - started;
      stage = "kysely_count";
      started = Date.now();
      await withTimeout(
        app.db.selectFrom("users").select(app.db.fn.countAll().as("count")).executeTakeFirst(),
        12000,
        "kysely_query_timeout"
      );
      timingsMs.kyselyCount = Date.now() - started;
      return { ok: true, reason: "ok", timingsMs };
    } catch (error) {
      const message = error && typeof error.message === "string" ? error.message : "";
      if (message === "runtime_init_timeout") {
        timingsMs.runtimeInit = Date.now() - started;
        return { ok: false, reason: "runtime_init_timeout", timingsMs };
      }
      if (message === "direct_probe_timeout") return { ok: false, reason: "direct_probe_timeout", timingsMs };
      if (message === "direct_users_probe_timeout") return { ok: false, reason: "direct_users_probe_timeout", timingsMs };
      if (message === "direct_users_probe_failed") return { ok: false, reason: "direct_users_probe_failed", timingsMs };
      if (message === "kysely_select_timeout") {
        timingsMs.kyselySelect = Date.now() - started;
        return { ok: false, reason: "kysely_select_timeout", timingsMs };
      }
      if (message === "kysely_query_timeout") {
        timingsMs.kyselyCount = Date.now() - started;
        return { ok: false, reason: "kysely_query_timeout", timingsMs };
      }
      if (stage === "kysely_pool_prime") return { ok: false, reason: "kysely_pool_prime_failed", timingsMs };
      if (message === "direct_probe_failed") return { ok: false, reason: "direct_probe_failed", timingsMs };
      if (stage === "kysely_select") return { ok: false, reason: "kysely_select_failed", timingsMs };
      if (stage === "kysely_count") return { ok: false, reason: "kysely_count_failed", timingsMs };
      return { ok: false, reason: stage === "runtime_init" ? "runtime_init_failed" : "database_query_failed", timingsMs };
    } finally {
      if (requestDbConfigured) {
        const started = Date.now();
        await closeRequestDatabase(app);
        timingsMs.kyselyClientClose = Date.now() - started;
      }
    }
  });
}

async function webhook(request, env) {
  if (request.method !== "POST") return new Response("Method not allowed", { status: 405 });
  // Use the already-allowlisted webhook URL for the setup-secret-only smoke
  // path; normal Telegram deliveries never send this separate header.
  if (request.headers.has("x-sugarnymous-smoke-secret")) return nativeSmoke(request, env);
  if (!env.TELEGRAM_WEBHOOK_SECRET || !env.TELEGRAM_BOT_TOKEN) {
    return new Response("Webhook is not configured", { status: 503 });
  }
  const received = request.headers.get("x-telegram-bot-api-secret-token") || "";
  if (!constantTimeEqual(env.TELEGRAM_WEBHOOK_SECRET, received)) {
    return new Response("Unauthorized", { status: 401 });
  }
  const contentLength = Number(request.headers.get("content-length") || 0);
  if (contentLength > MAX_BODY_BYTES) return new Response("Payload too large", { status: 413 });

  let text;
  try {
    text = await request.text();
  } catch {
    return new Response("Could not read request", { status: 400 });
  }
  if (text.length > MAX_BODY_BYTES) return new Response("Payload too large", { status: 413 });

  let update;
  try {
    update = JSON.parse(text);
  } catch {
    return new Response("Invalid JSON", { status: 400 });
  }
  if (!update || typeof update !== "object" || !Number.isSafeInteger(update.update_id) || update.update_id < 0) {
    return new Response("Invalid Telegram update", { status: 400 });
  }

  try {
    const app = await loadApp(env);
    const delivery = await withDatabaseLock(async () => {
      await app.resetDatabase(env.HYPERDRIVE.connectionString);
      try {
        return await app.telegramBot.processUpdate(update, request.url);
      } finally {
        await closeRequestDatabase(app);
      }
    });
    if (delivery?.retryable) {
      // Telegram retries non-2xx webhook responses. update_id dedupe is safe
      // because processUpdate also checks any existing outbox row on duplicates.
      return new Response("Temporary delivery error", { status: 503, headers: { "Cache-Control": "no-store" } });
    }
    return new Response("OK", { status: 200, headers: { "Cache-Control": "no-store" } });
  } catch {
    // No request payloads, database URLs, or tokens are logged. Telegram can retry 5xx responses.
    return new Response("Temporary processing error", { status: 500, headers: { "Cache-Control": "no-store" } });
  }
}

export default {
  async fetch(request, env) {
    const incoming = new URL(request.url);

    if (incoming.pathname === "/_api/telegram-webhook") return webhook(request, env);

    if ((incoming.pathname === "/_cloudflare-stage-health" || incoming.pathname === "/_api/health" || incoming.pathname === "/health") && request.method === "GET") {
      try {
        const health = await databaseHealth(env);
        if (!health.ok) {
          const body = incoming.pathname === "/_api/health" || incoming.pathname === "/health"
            ? { status: "degraded", service: "sugarnymous-cloudflare", database: "error", backend: "cloudflare-worker", reason: health.reason }
            : { ok: false, stage: "cloudflare-native", database: "error", backend: "cloudflare-worker", reason: health.reason, timingsMs: health.timingsMs ?? {}, website: "cloudflare-static-service", productionWebhookChanged: false, fullMigration: false };
          return json(body, 503);
        }
        const body = incoming.pathname === "/_api/health" || incoming.pathname === "/health"
          ? { status: "ok", service: "sugarnymous-cloudflare", database: "ok", backend: "cloudflare-worker" }
          : { ok: true, stage: "cloudflare-native", database: "ok", backend: "cloudflare-worker", timingsMs: health.timingsMs ?? {}, website: "cloudflare-static-service", productionWebhookChanged: false, fullMigration: false };
        return json(body, 200);
      } catch {
        const body = incoming.pathname === "/_api/health" || incoming.pathname === "/health"
          ? { status: "degraded", service: "sugarnymous-cloudflare", database: "error", backend: "cloudflare-worker" }
          : { ok: false, stage: "cloudflare-native", database: "error", backend: "cloudflare-worker", website: "cloudflare-static-service", productionWebhookChanged: false, fullMigration: false };
        return json(body, 503);
      }
    }

    // All public site routes are served by the separate Cloudflare static-site Worker.
    // The Telegram webhook and database health routes are handled above and remain on this Worker.
    if (env.STATIC_SITE && typeof env.STATIC_SITE.fetch === "function") {
      try {
        return await env.STATIC_SITE.fetch(request);
      } catch {
        return json({ error: "Static site temporarily unavailable", backend: "cloudflare-native" }, 502);
      }
    }
    return json({ error: "Static site service binding is not configured", backend: "cloudflare-native" }, 503);
  }
};
