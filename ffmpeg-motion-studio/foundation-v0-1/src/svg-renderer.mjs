import { evaluateFrame } from "./motion-core.mjs";

const n = (value) => Number(value.toFixed(3));
const esc = (value) => String(value)
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;");

const line = (a, b, color, width, extra = "") =>
  '<line x1="' + n(a.x) + '" y1="' + n(a.y)
  + '" x2="' + n(b.x) + '" y2="' + n(b.y)
  + '" stroke="' + color + '" stroke-width="' + width
  + '" stroke-linecap="round" ' + extra + '/>';

const circle = (point, radius, fill, stroke = "none", width = 0) =>
  '<circle cx="' + n(point.x) + '" cy="' + n(point.y)
  + '" r="' + radius + '" fill="' + fill
  + '" stroke="' + stroke + '" stroke-width="' + width + '"/>';

const txt = (x, y, value, size, color, weight = 400, extra = "") =>
  '<text x="' + x + '" y="' + y
  + '" font-family="Inter,system-ui,sans-serif" font-size="' + size
  + '" font-weight="' + weight + '" fill="' + color
  + '" ' + extra + '>' + esc(value) + "</text>";

function renderLegs(scene, state) {
  const palette = scene.palette;
  const character = scene.character;
  const root = state.root;
  const pelvis = state.pelvis;
  const leftHip = { x: pelvis.x - 13, y: pelvis.y };
  const rightHip = { x: pelvis.x + 16, y: pelvis.y };
  const leftKnee = { x: root.x - 7, y: pelvis.y + 78 };
  const rightKnee = { x: root.x + 36, y: pelvis.y + 78 };
  const leftFoot = { x: root.x - 25, y: pelvis.y + character.leg_length };
  const rightFoot = { x: root.x + 53, y: pelvis.y + character.leg_length };

  return '<g id="legs">'
    + line(leftHip, leftKnee, palette.ink, 32)
    + line(leftHip, leftKnee, palette.pants, 24)
    + line(leftKnee, leftFoot, palette.ink, 29)
    + line(leftKnee, leftFoot, palette.pants, 21)
    + line(rightHip, rightKnee, palette.ink, 32)
    + line(rightHip, rightKnee, palette.pants, 24)
    + line(rightKnee, rightFoot, palette.ink, 29)
    + line(rightKnee, rightFoot, palette.pants, 21)
    + line({ x: leftFoot.x - 10, y: leftFoot.y }, { x: leftFoot.x + 15, y: leftFoot.y }, palette.ink, 15)
    + line({ x: rightFoot.x - 10, y: rightFoot.y }, { x: rightFoot.x + 15, y: rightFoot.y }, palette.ink, 15)
    + circle(leftKnee, 10, palette.pants, palette.ink, 2)
    + circle(rightKnee, 10, palette.pants, palette.ink, 2)
    + "</g>";
}

function renderNeck(scene, state) {
  const palette = scene.palette;
  const start = { x: state.head.x + 10, y: state.head.y + 37 };
  const end = { x: state.root.x + 14, y: state.root.y + 22 };

  return '<g id="neck">'
    + line(start, end, palette.ink, 21)
    + line(start, end, palette.skin, 14)
    + "</g>";
}

function renderTorso(scene, state) {
  const palette = scene.palette;
  const root = state.root;
  const pelvis = state.pelvis;

  return '<g id="torso">'
    + '<path d="M ' + n(root.x - 3) + " " + n(root.y + 3)
    + " Q " + n(root.x - 15) + " " + n(root.y + 71)
    + " " + n(root.x + 3) + " " + n(pelvis.y)
    + " Q " + n(root.x + 22) + " " + n(pelvis.y + 9)
    + " " + n(root.x + 39) + " " + n(root.y + 65)
    + " L " + n(root.x + 46) + " " + n(root.y + 8)
    + ' Z" fill="' + palette.ink + '"/>'
    + '<path d="M ' + n(root.x + 2) + " " + n(root.y + 10)
    + " Q " + n(root.x - 5) + " " + n(root.y + 77)
    + " " + n(root.x + 6) + " " + n(pelvis.y - 3)
    + " Q " + n(root.x + 21) + " " + n(pelvis.y + 3)
    + " " + n(root.x + 34) + " " + n(root.y + 67)
    + " L " + n(root.x + 38) + " " + n(root.y + 13)
    + ' Z" fill="' + palette.shirt + '"/>'
    + '<path d="M ' + n(root.x + 7) + " " + n(root.y + 19)
    + " L " + n(root.x + 25) + " " + n(root.y + 19)
    + " L " + n(root.x + 19) + " " + n(root.y + 34)
    + ' Z" fill="#FFFFFF"/>'
    + "</g>";
}

function renderHead(scene, state) {
  const palette = scene.palette;
  const head = state.head;
  const radius = scene.character.head.radius;

  const hairPath = '<path d="M ' + n(head.x - radius + 2) + " " + n(head.y + 2)
    + " Q " + n(head.x - radius - 5) + " " + n(head.y - radius + 4)
    + " " + n(head.x - 8) + " " + n(head.y - radius - 2)
    + " Q " + n(head.x + radius + 8) + " " + n(head.y - radius - 4)
    + " " + n(head.x + radius - 1) + " " + n(head.y + 6)
    + " L " + n(head.x + 20) + " " + n(head.y - 2)
    + " L " + n(head.x + 7) + " " + n(head.y + 8)
    + " L " + n(head.x - 4) + " " + n(head.y - 1)
    + " L " + n(head.x - 20) + " " + n(head.y + 10)
    + ' Z" fill="' + palette.hair + '"/>';

  return '<g id="head">'
    + circle(head, radius, palette.skin, palette.ink, 3)
    + hairPath
    + circle({ x: head.x + 3, y: head.y + 10 }, 3.1, palette.ink)
    + circle({ x: head.x + 14, y: head.y + 11 }, 3.3, palette.ink)
    + "</g>";
}

function renderUpperArm(scene, state) {
  const palette = scene.palette;

  // Draw the upper arm after the torso so its connection at the outer shoulder
  // remains visible instead of disappearing behind the body silhouette.
  return '<g id="upper-arm">'
    + line(state.shoulder, state.elbow, palette.ink, 29)
    + line(state.shoulder, state.elbow, palette.skin, 21)
    + circle(state.shoulder, 13.5, palette.skin, palette.ink, 2.5)
    + circle(state.shoulder, 4.2, palette.skin)
    + "</g>";
}

function renderForearmAndHand(scene, state) {
  const palette = scene.palette;
  const forearm = line(state.elbow, state.wrist, palette.ink, 24)
    + line(state.elbow, state.wrist, palette.skin, 17);
  const hand = line(state.wrist, state.fingerTip, palette.ink, 11)
    + line(state.wrist, state.fingerTip, palette.skin, 6)
    + circle(state.elbow, 10.5, palette.skin, palette.ink, 2)
    + circle(state.wrist, 10, palette.skin, palette.ink, 2)
    + circle(state.fingerTip, 3.1, palette.skin, palette.ink, 1.2);

  return '<g id="forearm-hand">' + forearm + hand + "</g>";
}

function renderCharacter(scene, state) {
  return '<g id="character">'
    + renderLegs(scene, state)
    + renderNeck(scene, state)
    + renderTorso(scene, state)
    + renderUpperArm(scene, state)
    + renderHead(scene, state)
    + renderForearmAndHand(scene, state)
    + "</g>";
}

function renderBoard(scene, state) {
  const palette = scene.palette;
  const board = scene.board;
  const contactLimit = scene.quality_contract.max_target_error_px;
  const isContact = state.diagnostics.targetErrorPx <= contactLimit;
  const targetLabel = isContact ? "TARGET CONTACT" : "TARGET AHEAD";
  const targetDetail = isContact
    ? "Contact tolerance met · deterministic by frame"
    : (state.phase === "anticipate" ? "Preparing gesture · " : "Reaching target · ")
      + Math.round(state.diagnostics.targetErrorPx) + " px from contact";

  return '<g id="board" filter="url(#shadow)">'
    + '<rect x="' + board.x + '" y="' + board.y + '" width="' + board.width + '" height="' + board.height
    + '" rx="28" fill="' + palette.panel + '" stroke="' + palette.panel_border + '" stroke-width="2"/>'
    + '<rect x="' + (board.x + 26) + '" y="' + (board.y + 23) + '" width="124" height="28" rx="14" fill="' + palette.accent_soft + '"/>'
    + txt(board.x + 88, board.y + 42, "LIVE SCENE", 12, palette.accent, 750, 'text-anchor="middle" letter-spacing="1"')
    + txt(board.x + 140, board.y + 94, "One target.", 34, palette.ink, 750)
    + txt(board.x + 140, board.y + 133, "One deterministic pose.", 24, palette.muted, 450)
    + '<path d="M ' + (board.x + 27) + " " + (board.y + 163) + " H " + (board.x + board.width - 27)
    + '" stroke="' + palette.panel_border + '" stroke-width="1.5"/>'
    + '<rect x="' + (board.x + 27) + '" y="' + (board.y + 186) + '" width="' + (board.width - 54)
    + '" height="112" rx="18" fill="#F7F8FA"/>'
    + txt(board.x + 140, board.y + 216, targetLabel, 12, palette.muted, 750, 'letter-spacing="1.2"')
    + txt(board.x + 140, board.y + 254, "Frame-indexed IK", 22, palette.ink, 700)
    + txt(board.x + 140, board.y + 278, targetDetail, 14, palette.muted, 450)
    + circle({ x: board.target_x, y: board.target_y }, 23, palette.accent_soft)
    + circle({ x: board.target_x, y: board.target_y }, 12, "none", palette.accent, 2.5)
    + '<path d="M ' + (board.target_x - 31) + " " + board.target_y
    + " H " + (board.target_x + 31)
    + " M " + board.target_x + " " + (board.target_y - 31)
    + " V " + (board.target_y + 31)
    + '" stroke="' + palette.accent + '" stroke-width="1.5" stroke-linecap="round"/>'
    + txt(board.x + board.width - 28, board.y + board.height - 26,
      "FRAME " + String(state.frameIndex).padStart(2, "0"), 12, palette.muted, 700,
      'text-anchor="end" letter-spacing="1"')
    + "</g>";
}

export function renderSceneSvg(scene, frameIndex, options = {}) {
  const state = evaluateFrame(scene, frameIndex);
  const palette = scene.palette;
  const width = scene.canvas.width;
  const height = scene.canvas.height;
  const board = scene.board;
  const phase = state.phase.toUpperCase();

  const diagnostics = options.showDiagnostics
    ? '<g id="diagnostics">'
      + line(state.shoulder, state.wrist, "#00A3FF", 1.5, 'stroke-dasharray="5 5"')
      + [state.shoulder, state.elbow, state.wrist, state.fingerTip]
        .map((point, index) => circle(point, 5,
          ["#00A3FF", "#FFB000", "#FF4D6D", "#00B894"][index], "#FFFFFF", 1.5)
          + txt(point.x + 8, point.y - 9,
            ["shoulder", "elbow", "wrist", "tip"][index], 11, palette.ink, 700))
        .join("")
      + txt(42, 616,
        "IK reachable: " + state.diagnostics.reachable
        + " · upper error: " + state.diagnostics.upperSegmentErrorPx.toFixed(3)
        + "px · lower error: " + state.diagnostics.lowerSegmentErrorPx.toFixed(3) + "px",
        12, palette.ink, 700)
      + "</g>"
    : "";

  const timelineWidth = (width - 88) * state.frameIndex / Math.max(1, scene.duration_frames - 1);

  return '<svg xmlns="http://www.w3.org/2000/svg" width="' + width + '" height="' + height
    + '" viewBox="0 0 ' + width + " " + height
    + '" role="img" aria-label="' + esc(scene.title) + ", frame " + frameIndex + '">'
    + '<defs><filter id="shadow" x="-20%" y="-20%" width="140%" height="150%">'
    + '<feDropShadow dx="0" dy="9" stdDeviation="13" flood-color="#253247" flood-opacity=".09"/>'
    + "</filter></defs>"
    + '<rect width="' + width + '" height="' + height + '" fill="' + palette.background + '"/>'
    + '<circle cx="' + (width - 80) + '" cy="80" r="96" fill="#E9E6DF" opacity=".5"/>'
    + txt(42, 47, "MOTION STUDIO / FOUNDATION", 13, palette.muted, 750, 'letter-spacing="1.5"')
    + txt(42, 82, "A motion should survive every frame.", 27, palette.ink, 750)
    + txt(42, 108, "Deterministic geometry · Inspectable gesture · Shared preview/export core", 14, palette.muted, 450)
    + renderBoard(scene, state)
    + renderCharacter(scene, state)
    + txt(44, 664, "PHASE / " + phase, 12, palette.ink, 700, 'letter-spacing="1"')
    + txt(width - 42, 664,
      String(frameIndex).padStart(2, "0") + " / " + (scene.duration_frames - 1) + " · " + scene.fps + " FPS",
      12, palette.muted, 600, 'text-anchor="end"')
    + '<rect x="44" y="680" width="' + (width - 88) + '" height="4" rx="2" fill="#DDE2E8"/>'
    + '<rect x="44" y="680" width="' + Math.max(3, timelineWidth)
    + '" height="4" rx="2" fill="' + palette.accent + '"/>'
    + diagnostics
    + "</svg>";
}
