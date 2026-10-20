import { evaluateLocomotion, solveTwoBoneIK } from "../../foundation-v0.8.0/src/locomotion.mjs";

const finitePoint = p => !!p && Number.isFinite(p.x) && Number.isFinite(p.y);
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
const length = p => Math.hypot(p.x, p.y) || 1;
const sub = (a, b) => ({ x: a.x - b.x, y: a.y - b.y });
const add = (a, b) => ({ x: a.x + b.x, y: a.y + b.y });
const mul = (a, k) => ({ x: a.x * k, y: a.y * k });
const mix = (a, b, t) => ({ x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t });
const unit = p => mul(p, 1 / length(p));
const normal = p => ({ x: -p.y, y: p.x });
const fmt = v => {
  if (!Number.isFinite(v)) throw new TypeError("Anatomy geometry must be finite");
  return Number(v.toFixed(3)).toString();
};
const pt = p => fmt(p.x) + "," + fmt(p.y);
const safeColor = (v, fallback) => typeof v === "string" && /^#[0-9a-fA-F]{6}$/.test(v) ? v : fallback;
const esc = s => String(s).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");

/** Tapered limb volume with smooth, rounded end caps. Radii describe proximal and distal anatomy. */
export function taperedCapsulePath(start, end, startRadius, endRadius) {
  if (!finitePoint(start) || !finitePoint(end) || ![startRadius, endRadius].every(Number.isFinite) ||
      startRadius <= 0 || endRadius <= 0) throw new TypeError("Capsule needs finite points and positive radii");
  const axis = unit(sub(end, start)), n = normal(axis), a = Math.max(0.1, startRadius), b = Math.max(0.1, endRadius);
  const a1 = add(start, mul(n, a)), b1 = add(end, mul(n, b));
  const b2 = sub(end, mul(n, b)), a2 = sub(start, mul(n, a));
  return "M " + pt(a1) + " L " + pt(b1) + " Q " + pt(add(end, mul(axis, b))) + " " + pt(b2) +
    " L " + pt(a2) + " Q " + pt(sub(start, mul(axis, a))) + " " + pt(a1) + " Z";
}

function circle(p, r, fill, stroke = "#27323A", sw = 1.4, extra = "") {
  return '<circle cx="' + fmt(p.x) + '" cy="' + fmt(p.y) + '" r="' + fmt(r) + '" fill="' + fill +
    '" stroke="' + stroke + '" stroke-width="' + fmt(sw) + '" ' + extra + '/>';
}
function line(a, b, color, width, extra = "") {
  return '<path d="M ' + pt(a) + " L " + pt(b) + '" fill="none" stroke="' + color +
    '" stroke-width="' + fmt(width) + '" stroke-linecap="round" ' + extra + '/>';
}
function ellipse(p, rx, ry, fill, stroke = "#27323A", sw = 1.4, angle = 0, extra = "") {
  return '<ellipse cx="' + fmt(p.x) + '" cy="' + fmt(p.y) + '" rx="' + fmt(rx) + '" ry="' + fmt(ry) +
    '" fill="' + fill + '" stroke="' + stroke + '" stroke-width="' + fmt(sw) +
    '" transform="rotate(' + fmt(angle * 180 / Math.PI) + " " + fmt(p.x) + " " + fmt(p.y) + ')" ' + extra + '/>';
}
function limb(a, b, r1, r2, fill, outline = "#29343B", highlight = null) {
  const d = taperedCapsulePath(a, b, r1, r2), axis = unit(sub(b, a)), n = normal(axis);
  const mid = mix(a, b, 0.48), h0 = add(mid, mul(n, Math.min(r1, r2) * 0.25));
  const h1 = add(mix(a, b, 0.8), mul(n, Math.min(r1, r2) * 0.25));
  return '<path d="' + d + '" fill="' + fill + '" stroke="' + outline + '" stroke-width="1.5" stroke-linejoin="round"/>' +
    (highlight ? line(h0, h1, highlight, Math.max(1.1, Math.min(r1, r2) * 0.18), 'opacity="0.45"') : "");
}
function smoothClosedPath(points) {
  const mid = (a, b) => mix(a, b, 0.5);
  let d = "M " + pt(mid(points[points.length - 1], points[0]));
  for (let i = 0; i < points.length; i++) {
    const a = points[i], b = mid(a, points[(i + 1) % points.length]);
    d += " Q " + pt(a) + " " + pt(b);
  }
  return d + " Z";
}
export function buildAnatomicalGeometry(scene, pose) {
  const c = scene.character, chest = pose.chest, pelvis = pose.pelvis;
  const axis = unit(sub(pelvis, chest)), n = normal(axis), h = length(sub(pelvis, chest));
  const scale = clamp(((c.upper_leg_px || 79) + (c.lower_leg_px || 81)) / 160, 0.75, 1.3);
  const stations = [
    { t: -0.22, w: (c.shoulder_half_width_px || 25) * 0.55 * scale },
    { t: 0.02, w: (c.shoulder_half_width_px || 25) * 0.82 * scale },
    { t: 0.18, w: (c.shoulder_half_width_px || 25) * scale },
    { t: 0.38, w: 22 * scale },
    { t: 0.62, w: (c.waist_half_width_px || 16) * scale },
    { t: 0.84, w: 18 * scale },
    { t: 1, w: (c.hip_half_width_px || 22) * scale }
  ];
  const left = stations.map(v => add(add(chest, mul(axis, h * v.t)), mul(n, v.w)));
  const right = stations.slice().reverse().map(v => sub(add(chest, mul(axis, h * v.t)), mul(n, v.w)));
  const all = [...left, ...right];
  const path = smoothClosedPath(all);
  const headRadius = c.head_radius_px || 29;
  return { path, axis, n, height: h, scale, shoulderWidth: 2 * (c.shoulder_half_width_px || 25) * scale,
    headWidth: headRadius * 1.64, headHeight: headRadius * 2 };
}

/** Produce the same pinned locomotion pose with anatomical shoulder placement and freshly solved arms. */
export function evaluateAnatomyPose(scene, frameIndex, armMode = scene.motion.arm_mode || "carry") {
  const pose = evaluateLocomotion(scene, frameIndex, armMode), c = scene.character;
  // Shorten the exposed neck without deforming the pinned torso or changing root motion.
  const headDrop = Number.isFinite(c.head_drop_px) ? c.head_drop_px : 8;
  pose.head = { ...pose.head, y: pose.head.y + headDrop };
  pose.headLocal = { ...pose.headLocal, y: pose.headLocal.y + headDrop };
  pose.neck = { ...pose.neck, y: pose.neck.y + headDrop };
  const half = c.shoulder_half_width_px || 25;
  const rotatePoint = (p, pivot, a) => {
    const dx = p.x - pivot.x, dy = p.y - pivot.y, co = Math.cos(a), si = Math.sin(a);
    return { x: pivot.x + dx * co - dy * si, y: pivot.y + dx * si + dy * co };
  };
  const shoulders = {
    near: rotatePoint({ x: pose.chestLocal.x + half * 0.88, y: pose.chestLocal.y + 5 }, pose.pelvis, pose.torsoAngle),
    far: rotatePoint({ x: pose.chestLocal.x - half * 0.82, y: pose.chestLocal.y + 7 }, pose.pelvis, pose.torsoAngle)
  };
  const targets = armMode === "carry"
    ? { near: pose.basket.handleRight, far: pose.basket.handleLeft }
    : {
      near: add(pose.nearArm.wrist, sub(shoulders.near, pose.nearArm.shoulder)),
      far: add(pose.farArm.wrist, sub(shoulders.far, pose.farArm.shoulder))
    };
  const solveArm = (side, shoulder, wrist) => {
    const old = side === "near" ? pose.nearArm : pose.farArm;
    const pole = armMode === "carry"
      ? { x: (shoulder.x + wrist.x) / 2 + (side === "near" ? -3 : 5), y: (shoulder.y + wrist.y) / 2 + 14 }
      : { x: (shoulder.x + wrist.x) / 2 - 12, y: (shoulder.y + wrist.y) / 2 + 3 };
    const ik = solveTwoBoneIK(shoulder, wrist, c.upper_arm_px, c.forearm_px, pole, -1);
    return { ...old, ...ik, shoulder, elbow: ik.joint, wrist: ik.end, target: wrist,
      elbowAngleDegrees: ik.jointAngleDegrees };
  };
  const nearArm = solveArm("near", shoulders.near, targets.near);
  const farArm = solveArm("far", shoulders.far, targets.far);
  const contact = armMode === "carry" ? Math.max(
    Math.hypot(nearArm.wrist.x - pose.basket.handleRight.x, nearArm.wrist.y - pose.basket.handleRight.y),
    Math.hypot(farArm.wrist.x - pose.basket.handleLeft.x, farArm.wrist.y - pose.basket.handleLeft.y)) : 0;
  return { ...pose, shoulders, nearArm, farArm, diagnostics: { ...pose.diagnostics,
    basketContactErrorPx: contact, anatomyShoulderWidthPx: Math.hypot(shoulders.near.x - shoulders.far.x, shoulders.near.y - shoulders.far.y) } };
}

function drawLeg(leg, foot, c, scale, near = true) {
  const pants = safeColor(c.pants, "#34445A"), shoe = safeColor(c.shoe, "#29313D");
  const thigh = limb(leg.hip, leg.knee, (near ? 11.4 : 10.7) * scale, (near ? 9.1 : 8.7) * scale,
    pants, "#273343", near ? "#69788A" : "#536175");
  const shin = limb(leg.knee, leg.ankle, (near ? 8.3 : 8.1) * scale, 6.2 * scale,
    pants, "#273343", near ? "#69788A" : "#536175");
  const sx = foot.x + 5.4 * scale, sy = foot.y - 3.9 * scale, angle = (foot.angle || 0) * 180 / Math.PI;
  const shoeSvg = '<g transform="rotate(' + fmt(angle) + " " + fmt(sx) + " " + fmt(sy) + ')">' +
    '<path d="M ' + fmt(sx - 9 * scale) + " " + fmt(sy - 4.5 * scale) + " Q " +
    fmt(sx - 5 * scale) + " " + fmt(sy - 8 * scale) + " " + fmt(sx + 3 * scale) + " " +
    fmt(sy - 5.2 * scale) + " L " + fmt(sx + 15 * scale) + " " + fmt(sy - 2.7 * scale) +
    " Q " + fmt(sx + 19 * scale) + " " + fmt(sy + 0.2 * scale) + " " + fmt(sx + 15 * scale) + " " +
    fmt(sy + 4 * scale) + " L " + fmt(sx - 7 * scale) + " " + fmt(sy + 4 * scale) + " Q " +
    fmt(sx - 12 * scale) + " " + fmt(sy + scale) + " " + fmt(sx - 9 * scale) + " " + fmt(sy - 4.5 * scale) +
    ' Z" fill="' + shoe + '" stroke="#202934" stroke-width="1.5"/><path d="M ' + fmt(sx - 7 * scale) +
    " " + fmt(sy + 2.5 * scale) + " Q " + fmt(sx + 2 * scale) + " " + fmt(sy + 4.5 * scale) +
    " " + fmt(sx + 15 * scale) + " " + fmt(sy + 2 * scale) + '" fill="none" stroke="#C5C9C8" stroke-width="1.6" stroke-linecap="round"/></g>';
  return thigh + shin + circle(leg.knee, 7.2 * scale, pants, pants, 0.6) + shoeSvg;
}
function drawArm(arm, c, near = true) {
  const skin = safeColor(c.skin, "#DDA985"), shirt = safeColor(c.shirt, "#3B7892");
  const upper = limb(arm.shoulder, arm.elbow, near ? 9.9 : 9.2, 7.3, shirt, "#253D4A", near ? "#7FA9B5" : "#5E8797");
  const elbow = circle(arm.elbow, 5.8, skin, skin, 0.7);
  const fore = limb(arm.elbow, arm.wrist, 6.1, 4.9, skin, "#765645", "#F0C6A4");
  return upper + elbow + fore;
}
function drawTorso(scene, pose, geo) {
  const c = scene.character, shirt = safeColor(c.shirt, "#3B7892"), shadow = safeColor(c.shirt_shadow, "#28566C");
  const pants = safeColor(c.pants, "#34445A"), axis = geo.axis, n = geo.n, chest = pose.chest, pelvis = pose.pelvis, h = geo.height;
  const seamA = add(add(chest, mul(axis, h * 0.2)), mul(n, -8)), seamB = add(add(chest, mul(axis, h * 0.73)), mul(n, -11));
  const beltY = add(chest, mul(axis, h * 0.81));
  const collarA = add(add(chest, mul(axis, -14)), mul(n, -11));
  const collarCenter = add(chest, mul(axis, 8));
  const collarB = add(add(chest, mul(axis, -14)), mul(n, 11));
  const hipA = add(pelvis, mul(n, -9)), hipB = add(pelvis, mul(n, 8));
  return '<path d="' + geo.path + '" fill="' + shirt + '" stroke="#253C49" stroke-width="2" stroke-linejoin="round"/>' +
    line(seamA, seamB, shadow, 3.2, 'opacity="0.62"') +
    line(add(beltY, mul(n, -15)), add(beltY, mul(n, 15)), "#27313C", 4.5) +
    line(add(beltY, mul(n, -13)), add(beltY, mul(n, 13)), "#A5ABB0", 1.2) +
    line(collarA, collarCenter, "#D2E5E7", 2.1) + line(collarCenter, collarB, "#D2E5E7", 2.1) +
    line(hipA, hipB, pants, 2.4);
}
function drawHead(scene, pose) {
  const c = scene.character, skin = safeColor(c.skin, "#DDA985"), hair = safeColor(c.hair, "#26302A");
  const r = c.head_radius_px || 29, h = pose.head, rx = r * 0.82, ry = r;
  const rot = (pose.headAngle || 0) * 180 / Math.PI;
  return '<g transform="rotate(' + fmt(rot) + " " + fmt(h.x) + " " + fmt(h.y) + ')">' +
    ellipse({ x: h.x - 19, y: h.y + 2 }, 4.6, 7.5, skin, "#8A5F4B", 1.2, -0.1) +
    ellipse({ x: h.x + 19, y: h.y + 2 }, 4.6, 7.5, skin, "#8A5F4B", 1.2, 0.1) +
    '<path d="M ' + fmt(h.x) + " " + fmt(h.y - ry) + " C " + fmt(h.x + rx * 0.8) + " " +
    fmt(h.y - ry * 0.98) + " " + fmt(h.x + rx * 1.03) + " " + fmt(h.y - ry * 0.35) + " " +
    fmt(h.x + rx * 0.83) + " " + fmt(h.y + ry * 0.35) + " Q " + fmt(h.x + rx * 0.58) + " " +
    fmt(h.y + ry * 0.94) + " " + fmt(h.x) + " " + fmt(h.y + ry) + " Q " +
    fmt(h.x - rx * 0.65) + " " + fmt(h.y + ry * 0.88) + " " + fmt(h.x - rx * 0.85) + " " +
    fmt(h.y + ry * 0.32) + " C " + fmt(h.x - rx * 1.05) + " " + fmt(h.y - ry * 0.36) + " " +
    fmt(h.x - rx * 0.72) + " " + fmt(h.y - ry * 0.95) + " " + fmt(h.x) + " " + fmt(h.y - ry) +
    ' Z" fill="' + skin + '" stroke="#815B49" stroke-width="1.5"/>' +
    '<path d="M ' + fmt(h.x - rx * 0.91) + " " + fmt(h.y - ry * 0.15) + " C " +
    fmt(h.x - rx * 1.05) + " " + fmt(h.y - ry * 0.92) + " " + fmt(h.x - rx * 0.4) + " " +
    fmt(h.y - ry * 1.08) + " " + fmt(h.x + 2) + " " + fmt(h.y - ry * 0.94) + " C " +
    fmt(h.x + rx * 0.82) + " " + fmt(h.y - ry * 0.9) + " " + fmt(h.x + rx * 1.02) + " " +
    fmt(h.y - ry * 0.35) + " " + fmt(h.x + rx * 0.78) + " " + fmt(h.y - ry * 0.02) + " L " +
    fmt(h.x + rx * 0.46) + " " + fmt(h.y - ry * 0.27) + " Q " + fmt(h.x) + " " +
    fmt(h.y - ry * 0.45) + " " + fmt(h.x - rx * 0.35) + " " + fmt(h.y - ry * 0.16) +
    " L " + fmt(h.x - rx * 0.72) + " " + fmt(h.y + ry * 0.05) + ' Z" fill="' + hair +
    '" stroke="#202B26" stroke-width="1.5"/>' +
    ellipse({ x: h.x - 7.3, y: h.y + 1 }, 3.3, 4.1, "#F8F1E7", "#624C40", 0.8) +
    ellipse({ x: h.x + 7.2, y: h.y + 1 }, 3.3, 4.1, "#F8F1E7", "#624C40", 0.8) +
    ellipse({ x: h.x - 6.2, y: h.y + 1.4 }, 1.8, 2.7, "#26302A", "none", 0) +
    ellipse({ x: h.x + 8.2, y: h.y + 1.4 }, 1.8, 2.7, "#26302A", "none", 0) +
    '<path d="M ' + fmt(h.x - 11) + " " + fmt(h.y - 5.2) + " Q " + fmt(h.x - 7) + " " +
    fmt(h.y - 7.3) + " " + fmt(h.x - 3.5) + " " + fmt(h.y - 5.2) + " M " +
    fmt(h.x + 3.4) + " " + fmt(h.y - 5.2) + " Q " + fmt(h.x + 7.5) + " " +
    fmt(h.y - 7.3) + " " + fmt(h.x + 11) + " " + fmt(h.y - 5.2) +
    '" stroke="#43392F" stroke-width="1.6" fill="none" stroke-linecap="round"/></g>';
}
function drawHands(p, sign) {
  return '<g transform="translate(' + fmt(p.x + 2.8 * sign) + " " + fmt(p.y + 1.2) + ') rotate(' + fmt(sign * 18) + ')">' +
    '<path d="M -5 -4 Q -1 -7 4 -4 L 6 1 Q 5 5 0 5 L -4 3 Q -7 1 -5 -4 Z" fill="#DDA985" stroke="#765645" stroke-width="1.1"/>' +
    '<path d="M 2 -3 Q 5 -2 6 1 M -1 -2 Q 2 0 3 3" fill="none" stroke="#F0C7A5" stroke-width="1.1" stroke-linecap="round"/></g>';
}
function drawBasket(scene, pose) {
  const b = pose.basket, c = scene.prop, color = safeColor(c.basket_color, "#E9923A");
  const handle = safeColor(c.handle_color, "#8A542C"), cx = b.x + b.width / 2, top = b.y, bottom = b.y + b.height;
  return '<path d="M ' + pt({ x: b.handleLeft.x, y: b.handleLeft.y + 4 }) + " Q " + fmt(cx) + " " + fmt(top - 26) +
    " " + pt({ x: b.handleRight.x, y: b.handleRight.y + 4 }) + '" fill="none" stroke="' + handle + '" stroke-width="4.1" stroke-linecap="round"/>' +
    '<path d="M ' + fmt(b.x + 3) + " " + fmt(top + 2) + " L " + fmt(b.x + b.width - 3) + " " + fmt(top + 2) +
    " L " + fmt(b.x + b.width - 8) + " " + fmt(bottom) + " L " + fmt(b.x + 8) + " " + fmt(bottom) +
    ' Z" fill="' + color + '" stroke="#7A4C2D" stroke-width="1.8"/>' +
    '<path d="M ' + fmt(b.x + 6) + " " + fmt(top + 11) + " L " + fmt(b.x + b.width - 6) + " " + fmt(top + 11) +
    " M " + fmt(b.x + 7) + " " + fmt(top + 21) + " L " + fmt(b.x + b.width - 7) + " " + fmt(top + 21) +
    " M " + fmt(b.x + 9) + " " + fmt(top + 31) + " L " + fmt(b.x + b.width - 9) + " " + fmt(top + 31) +
    '" stroke="#C7762F" stroke-width="2.2" opacity="0.9"/>' +
    '<path d="M ' + fmt(cx) + " " + fmt(top + 3) + " L " + fmt(cx) + " " + fmt(bottom - 2) +
    '" stroke="#F7BD70" stroke-width="1.2" opacity="0.8"/>';
}

/** Full SVG preview renderer for anatomy review; uses the pinned v0.8.0 locomotion scene contract. */
export function renderAnatomySvg(scene, pose, armMode = scene.motion.arm_mode || "carry") {
  const geo = buildAnatomicalGeometry(scene, pose), c = scene.character, W = scene.canvas.width, H = scene.canvas.height;
  const horizon = scene.background.horizon_y, floor = safeColor(scene.background.floor, "#E8E3D4");
  const bg = safeColor(scene.background.color, "#F4F2E8");
  const farLeg = drawLeg(pose.rightLeg, pose.rightFoot, c, geo.scale, false);
  const nearLeg = drawLeg(pose.leftLeg, pose.leftFoot, c, geo.scale, true);
  const farArm = drawArm(pose.farArm, c, false);
  const neckEnd = mix(pose.neck, pose.chest, 0.58);
  const neck = limb(pose.neck, neckEnd, 7.2, 8.1, safeColor(c.skin, "#DDA985"), "#815B49", "#F0C7A5");
  const shadow = '<ellipse cx="' + fmt((pose.leftFoot.x + pose.rightFoot.x) / 2) +
    '" cy="' + fmt(horizon + 2) + '" rx="44" ry="6.5" fill="#47504A" opacity="0.12"/>';
  const accessory = '<path d="M ' + fmt(pose.chest.x - 12) + " " + fmt(pose.chest.y + 9) +
    " Q " + fmt(pose.chest.x) + " " + fmt(pose.chest.y + 18) + " " + fmt(pose.chest.x + 11) + " " +
    fmt(pose.chest.y + 9) + '" fill="none" stroke="#D5E3E4" stroke-width="2.5" stroke-linecap="round"/>';
  const basket = armMode === "carry" ? drawBasket(scene, pose) : "";
  const nearArm = drawArm(pose.nearArm, c, true);
  const hands = drawHands(pose.nearArm.wrist, 1) + drawHands(pose.farArm.wrist, -1);
  return '<svg xmlns="http://www.w3.org/2000/svg" width="' + W + '" height="' + H + '" viewBox="0 0 ' + W + ' ' + H +
    '" role="img" aria-label="Stylized anatomy locomotion study" data-frame="' + pose.frameIndex +
    '" data-profile="' + esc(c.anatomy_profile || "stylized-natural-v1") + '">' +
    '<title>Motion Studio anatomy refinement - ' + esc(armMode) + ' - frame ' + pose.frameIndex + '</title>' +
    '<rect width="' + W + '" height="' + H + '" fill="' + bg + '"/>' +
    '<rect y="' + horizon + '" width="' + W + '" height="' + (H - horizon) + '" fill="' + floor + '"/>' +
    '<path d="M 0 ' + horizon + ' H ' + W + '" stroke="#D6D0C3" stroke-width="2"/>' +
    shadow + farLeg + nearLeg + farArm + neck + drawTorso(scene, pose, geo) + drawHead(scene, pose) +
    accessory + basket + nearArm + hands +
    '<g transform="translate(28 30)"><rect width="232" height="34" rx="8" fill="#FFFFFF" opacity="0.82"/>' +
    '<text x="14" y="22" font-family="sans-serif" font-size="14" font-weight="600" fill="#34414A">ANATOMY STUDY / v0.8.2</text></g></svg>';
}
