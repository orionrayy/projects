import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const root = path.resolve("sugarnymous-cloudflare");
const partsDir = path.join(root, "runtime-snapshot", "parts");
const output = path.join(root, "runtime-snapshot", "telegramBundle.mjs");
const workerPath = path.join(root, "runtime-snapshot", "worker.mjs");
const expected = {
  bundleLength: 287610,
  bundleSha256: "b30510a45d42ab7241510f6ece635b475a239e2a2b0b72310951a9785bd621b2",
  workerLength: 25996,
  workerSha256: "0bc841a59f8fbee8ff031434420abdc13bca278ab6bebb12847a377090e65333",
};

const names = fs.readdirSync(partsDir)
  .filter((name) => /^telegramBundle\.part-\d{3}\.txt$/.test(name))
  .sort();

if (names.length !== 32) {
  throw new Error(`Expected 32 bundle parts, found ${names.length}`);
}

for (let i = 0; i < names.length; i += 1) {
  if (names[i] !== `telegramBundle.part-${String(i).padStart(3, "0")}.txt`) {
    throw new Error(`Missing or out-of-order source part at index ${i}`);
  }
}

const bundle = names.map((name) => fs.readFileSync(path.join(partsDir, name), "utf8")).join("");
const bundleHash = crypto.createHash("sha256").update(bundle, "utf8").digest("hex");
if (bundle.length !== expected.bundleLength || bundleHash !== expected.bundleSha256) {
  throw new Error(`Bundle integrity mismatch: length=${bundle.length}, sha256=${bundleHash}`);
}

const worker = fs.readFileSync(workerPath, "utf8");
const workerHash = crypto.createHash("sha256").update(worker, "utf8").digest("hex");
if (worker.length !== expected.workerLength || workerHash !== expected.workerSha256) {
  throw new Error(`Worker entry integrity mismatch: length=${worker.length}, sha256=${workerHash}`);
}

fs.writeFileSync(output, bundle, "utf8");
console.log(`Restored verified runtime snapshot: worker=${worker.length} chars, bundle=${bundle.length} chars; SHA-256 checks passed.`);
