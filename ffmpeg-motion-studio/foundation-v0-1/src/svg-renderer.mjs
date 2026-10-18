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
  const legLength = character.leg_length;
  const leftHip = { x: root.x - 14, y: pelvis.y - 2 };
  const rightHip = { x: root.x + 14, y: pelvis.y - 2 };
  const leftKnee = { x: root.x - 21, y: pelvis.y + 72 };
  const rightKnee = { x: root.x + 21, y: pelvis.y + 72 };
  const leftAnkle = { x: root.x - 25, y: pelvis.y + legLength - 14 };
  const rightAnkle = { x: root.x + 25, y: pelvis.y + legLength - 14 };
  const leftFoot = { x: root.x - 25, y: pelvis.y + legLength };
  const rightFoot = { x: root.x + 25, y: pelvis.y + legLength };

  return '<g id="legs">'
    + line(leftHip, leftKnee, palette.ink, 29)
    + line(leftHip, leftKnee, palette.pants, 21)
    + line(leftKnee, leftAnkle, palette.ink, 25)
    + line(leftKnee, leftAnkle, palette.pants, 17)
    + line(rightHip, rightKnee, palette.ink, 29)
    + line(rightHip, rightKnee, palette.pants, 21)
    + line(rightKnee, rightAnkle, palette.ink, 25)
    + line(rightKnee, rightAnkle, palette.pants, 17)
    + circle(leftKnee, 8, palette.pants)
    + circle(rightKnee, 8, palette.pants)
    + line({ x: leftFoot.x - 11, y: leftFoot.y }, { x: leftFoot.x + 13, y: leftFoot.y }, palette.ink, 15)
    + line({ x: rightFoot.x - 11, y: rightFoot.y }, { x: rightFoot.x + 13, y: rightFoot.y }, palette.ink, 15)
    + "</g>";
}

function renderNeck(scene, state) {
  const palette = scene.palette;
  return '<g id="neck">'
    + line(state.neckTop, state.neckBase, palette.ink, 20)
    + line(state.neckTop, state.neckBase, palette.skin, 13)
    + "</g>";
}

function renderTorso(scene, state) {
  const palette = scene.palette;
  const root = state.root;
  const pelvis = state.pelvis;
  const angle = state.torsoAngle * 180 / Math.PI;

  return '<g id="torso" transform="rotate(' + n(angle) + ' ' + n(pelvis.x) + ' ' + n(pelvis.y) + ')">'
    + '<path d="M ' + n(root.x - 29) + " " + n(root.y + 8)
    + " Q " + n(root.x - 35) + " " + n(root.y - 1) + " " + n(root.x - 18) + " " + n(root.y + 1)
    + " L " + n(root.x + 18) + " " + n(root.y + 1)
    + " Q " + n(root.x + 34) + " " + n(root.y + 1) + " " + n(root.x + 35) + " " + n(root.y + 14)
    + " L " + n(root.x + 31) + " " + n(root.y + 67)
    + " Q " + n(root.x + 28) + " " + n(root.y + 107) + " " + n(root.x + 24) + " " + n(pelvis.y - 5)
    + " Q " + n(root.x + 15) + " " + n(pelvis.y + 5) + " " + n(root.x + 5) + " " + n(pelvis.y)
    + " Q " + n(root.x) + " " + n(pelvis.y + 2) + " " + n(root.x - 5) + " " + n(pelvis.y)
    + " Q " + n(root.x - 16) + " " + n(pelvis.y + 5) + " " + n(root.x - 24) + " " + n(pelvis.y - 5)
    + " Q " + n(root.x - 29) + " " + n(root.y + 107) + " " + n(root.x - 31) + " " + n(root.y + 67)
    + " L " + n(root.x - 35) + " " + n(root.y + 22)
    + " Q " + n(root.x - 36) + " " + n(root.y + 12) + " " + n(root.x - 29) + " " + n(root.y + 8)
    + ' Z" fill="' + palette.ink + '"/>'
    + '<path d="M ' + n(root.x - 25) + " " + n(root.y + 15)
    + " Q " + n(root.x - 22) + " " + n(root.y + 9) + " " + n(root.x - 13) + " " + n(root.y + 10)
    + " L " + n(root.x + 13) + " " + n(root.y + 10)
    + " Q " + n(root.x + 24) + " " + n(root.y + 10) + " " + n(root.x + 26) + " " + n(root.y + 18)
    + " L " + n(root.x + 23) + " " + n(root.y + 67)
    + " Q " + n(root.x + 20) + " " + n(root.y + 110) + " " + n(root.x + 17) + " " + n(pelvis.y - 13)
    + " Q " + n(root.x + 7) + " " + n(pelvis.y - 6) + " " + n(root.x) + " " + n(pelvis.y - 10)
    + " Q " + n(root.x - 10) + " " + n(pelvis.y - 6) + " " + n(root.x - 17) + " " + n(pelvis.y - 13)
    + " Q " + n(root.x - 22) + " " + n(root.y + 110) + " " + n(root.x - 23) + " " + n(root.y + 67)
    + ' Z" fill="' + palette.shirt + '"/>'
    + '<path d="M ' + n(root.x - 8) + " " + n(root.y + 15)
    + " L " + n(root.x) + " " + n(root.y + 25)
    + " L " + n(root.x + 8) + " " + n(root.y + 15)
    + ' Z" fill="#F7F4ED"/>'
    + circle({ x: root.x + 2, y: root.y + 49 }, 1.8, palette.panel_border)
    + circle({ x: root.x + 2, y: root.y + 66 }, 1.8, palette.panel_border)
    + "</g>";
}

function renderHead(scene, state) {
  const palette = scene.palette;
  const head = state.head;
  const radius = scene.character.head.radius;
  const angle = state.headAngle * 180 / Math.PI;
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

  return '<g id="head" transform="rotate(' + n(angle) + ' ' + n(head.x) + ' ' + n(head.y) + ')">'
    + circle(head, radius, palette.skin, palette.ink, 3)
    + hairPath
    + circle({ x: head.x - 8, y: head.y + 10 }, 3.2, palette.ink)
    + circle({ x: head.x + 9, y: head.y + 11 }, 3.3, palette.ink)
    + '<path d="M ' + n(head.x + 15) + " " + n(head.y + 15)
    + " L " + n(head.x + 20) + " " + n(head.y + 17)
    + '" stroke="' + palette.ink + '" stroke-width="1.8" stroke-linecap="round" fill="none"/>'
    + '<path d="M ' + n(head.x + 1) + " " + n(head.y + 25)
    + " Q " + n(head.x + 8) + " " + n(head.y + 29) + " " + n(head.x + 16) + " " + n(head.y + 25)
    + '" stroke="' + palette.ink + '" stroke-width="1.8" stroke-linecap="round" fill="none"/>'
    + "</g>";
}

function renderUpperArm(scene, state) {
  const palette = scene.palette;
  return '<g id="upper-arm">'
    + line(state.shoulder, state.elbow, palette.ink, 29)
    + line(state.shoulder, state.elbow, palette.skin, 21)
    + circle(state.shoulder, 11.5, palette.skin)
    + "</g>";
}

function renderForearmAndHand(scene, state) {
  const palette = scene.palette;
  const scaleX = scene.character.hand_length / 25;
  const angleDegrees = state.handAngle * 180 / Math.PI;
  const forearm = line(state.elbow, state.wrist, palette.ink, 24)
    + line(state.elbow, state.wrist, palette.skin, 17)
    + circle(state.elbow, 8.5, palette.skin)
    + circle(state.wrist, 7.5, palette.skin);
  const indexFinger = '<g id="index-finger">'
    + '<path d="M 7 -1.8 L 25 0 L 24.7 2.1 L 7 1.8 Z" fill="' + palette.ink + '"/>'
    + '<path d="M 7 -0.7 L 25 0 L 24.7 1.0 L 7 0.7 Z" fill="' + palette.skin + '"/>'
    + circle({x:25,y:0}, 1.5, palette.skin, palette.ink, 0.7)
    + "</g>";
  const palm = '<path id="palm" d="M 2 -2.8 C 1 -5.3 3 -6.6 5.8 -5.9 L 10 -4.8 C 12 -4.1 13 -2.3 13 -0.2 L 13 2.4 C 12.8 4.8 10.7 6 8.2 5.1 L 3.2 4.1 C 1.4 3.6 1 0 2 -2.8 Z" fill="' + palette.skin + '" stroke="' + palette.ink + '" stroke-width="1.8" stroke-linejoin="round"/>';
  const thumb = '<g id="thumb">'
    + line({x:4.6,y:-4.8},{x:10.2,y:-8},palette.ink,4.5)
    + line({x:4.6,y:-4.8},{x:10.2,y:-8},palette.skin,2.8)
    + "</g>";
  const folded = '<g id="folded-fingers">'
    + line({x:6.2,y:0.6},{x:10.9,y:1.5},palette.ink,2.8)
    + line({x:6.2,y:0.6},{x:10.9,y:1.5},palette.skin,1.5)
    + line({x:5.6,y:2.8},{x:9.9,y:3.5},palette.ink,2.8)
    + line({x:5.6,y:2.8},{x:9.9,y:3.5},palette.skin,1.5)
    + "</g>";
  const hand = '<g id="pointing-hand" transform="translate(' + n(state.wrist.x) + " " + n(state.wrist.y) + ') rotate(' + n(angleDegrees) + ') scale(' + n(scaleX) + ' 1)">'
    + palm + folded + thumb + indexFinger + "</g>";
  return '<g id="forearm-hand">' + forearm + hand + "</g>";
}

function renderScreenLeftArm(scene, state) {
  const palette = scene.palette;
  const arm = state.screenLeftArm;
  const far = scene.character.far_arm;
  const angleDegrees = arm.handAngle * 180 / Math.PI;
  const scaleX = far.hand_length / 24;
  const limb = line(arm.shoulder, arm.elbow, palette.ink, 22)
    + line(arm.shoulder, arm.elbow, palette.skin, 15)
    + line(arm.elbow, arm.wrist, palette.ink, 19)
    + line(arm.elbow, arm.wrist, palette.skin, 13)
    + circle(arm.elbow, 7.5, palette.skin);
  const relaxedHand = '<g id="screen-left-hand" transform="translate(' + n(arm.wrist.x) + " " + n(arm.wrist.y) + ') rotate(' + n(angleDegrees) + ') scale(' + n(scaleX) + ' .88)">'
    + '<path d="M 1 -4 C -1 -1 0 3 3 5 L 10 7 C 15 7 19 4 19 0 C 18 -3 15 -5 12 -5 L 8 -4 C 6 -7 3 -7 1 -4 Z"'
    + ' fill="' + palette.skin + '" stroke="' + palette.ink + '" stroke-width="1.7" stroke-linejoin="round"/>'
    + '<path d="M 5 -3 L 11 -1" stroke="' + palette.ink + '" stroke-width="1" stroke-linecap="round" opacity=".55"/>'
    + "</g>";
  return '<g id="screen-left-arm">' + limb + relaxedHand + "</g>";
}

function renderCharacter(scene, state) {
  return '<g id="character">'
    + renderLegs(scene, state)
    + renderScreenLeftArm(scene, state)
    + renderNeck(scene, state)
    + renderTorso(scene, state)
    + '<g id="screen-right-arm">'
    + renderUpperArm(scene, state)
    + renderForearmAndHand(scene, state)
    + "</g>"
    + renderHead(scene, state)
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
