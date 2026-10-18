import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

const scene = JSON.parse(fs.readFileSync(new URL("../scenes/scene-001.json", import.meta.url), "utf8"));
class FakeElement {
  constructor(id) {
    this.id = id; this.value = ""; this.textContent = ""; this.innerHTML = "";
    this.hidden = false; this.disabled = false; this.style = {}; this.attributes = {};
    this.listeners = new Map(); this.classes = new Set();
    this.classList = { toggle: (name, on) => on ? this.classes.add(name) : this.classes.delete(name) };
  }
  addEventListener(type, fn) { if (!this.listeners.has(type)) this.listeners.set(type, []); this.listeners.get(type).push(fn); }
  setAttribute(name, value) { this.attributes[name] = value; }
  dispatch(type) { for (const fn of this.listeners.get(type) || []) fn({ target: this, currentTarget: this }); }
}

test("preview UI applies parameters, warns on invalid reach/layout, compares A/B and resets", async () => {
  const elements = new Map();
  globalThis.document = { getElementById(id) { if (!elements.has(id)) elements.set(id, new FakeElement(id)); return elements.get(id); } };
  globalThis.fetch = async () => ({ ok: true, status: 200, statusText: "OK", json: async () => structuredClone(scene) });
  globalThis.requestAnimationFrame = () => 1;
  globalThis.cancelAnimationFrame = () => {};
  const el = (id) => elements.get(id);
  await import("../preview/app.mjs?interaction-test=1");
  await new Promise((resolve) => setImmediate(resolve));

  assert.match(el("viewport").innerHTML, /frame 0/);
  assert.equal(el("target-x-value").textContent, "590");
  assert.equal(el("layout-status").textContent, "PASS");

  el("save-a").dispatch("click");
  el("target-x").value = "560"; el("target-x").dispatch("input");
  assert.equal(el("target-x-value").textContent, "560");
  assert.match(el("viewport").innerHTML, /cx="560" cy="380" r="23"/);
  el("toggle-ab").dispatch("click");
  assert.equal(el("compare-section").hidden, false);
  assert.match(el("viewport-a").innerHTML, /cx="590" cy="380" r="23"/);
  assert.match(el("viewport-b").innerHTML, /cx="560" cy="380" r="23"/);

  el("target-y").value = "350"; el("target-y").dispatch("input");
  assert.match(el("status").textContent, /TARGET_OVERLAPS_SEPARATOR/);
  assert.match(el("layout-status").textContent, /ISSUE/);

  el("target-x").value = "610"; el("target-x").dispatch("input");
  el("target-y").value = "380"; el("target-y").dispatch("input");
  el("upper").value = "90"; el("upper").dispatch("input");
  el("forearm").value = "90"; el("forearm").dispatch("input");
  el("frame").value = "95"; el("frame").dispatch("input");
  assert.match(el("reachability").textContent, /NO/);
  assert.match(el("status").textContent, /IK UNREACHABLE/);

  el("reset").dispatch("click");
  assert.equal(el("target-x-value").textContent, "590");
  assert.equal(el("upper-value").textContent, "116 px");
  assert.match(el("viewport").innerHTML, /cx="590" cy="380" r="23"/);
});