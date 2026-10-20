import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { evaluateLocomotion } from '../src/locomotion.mjs';
import { renderSvgFrame } from './render-preview.mjs';

export const REFERENCE_VISUAL_SPEC = Object.freeze({
  width: 720,
  height: 1280,
  fps: 30,
  durationSeconds: 10,
  frameCount: 300,
  colors: Object.freeze({
    background: '#080A0E',
    panel: '#10151D',
    white: '#F3F5F8',
    muted: '#ADB5C2',
    line: '#596373',
    red: '#FF4C58',
    gold: '#FFC66D',
    card: '#111720',
    deepRed: '#3A1118'
  }),
  shots: Object.freeze(['hook-time', 'room-tracking-walk', 'device-impact', 'kinetic-rule', 'walk-to-settle', 'cause-evidence']),
  safeZones: Object.freeze({ left: 40, right: 40, headerTop: 28, headerBottom: 138, captionTop: 995, uiAvoidanceBottom: 1120 })
});

const { width: W, height: H, fps: FPS, durationSeconds: DURATION, frameCount: FRAME_COUNT, colors: C } = REFERENCE_VISUAL_SPEC;
const FLOOR_SCREEN = 930;
const BASE_SCALE = 1.52;
const TRANSITION_FRAMES = 5;
const SHOT_STARTS = [0, 33, 114, 158, 201, 257, 300];
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
const smoothstep = (v) => { const t = clamp(v, 0, 1); return t * t * (3 - 2 * t); };
const smootherstep = (v) => { const t = clamp(v, 0, 1); return t * t * t * (t * (t * 6 - 15) + 10); };
const outCubic = (v) => { const t = clamp(v, 0, 1); return 1 - (1 - t) ** 3; };
const fmt = (v) => Number.isFinite(v) ? Number(v).toFixed(2) : '0.00';
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&apos;');

const baseScene = JSON.parse(fs.readFileSync(new URL('../scenes/locomotion-free.json', import.meta.url), 'utf8'));
const GAIT_SCENE = {
  ...baseScene,
  fps: FPS,
  duration_frames: FRAME_COUNT,
  character: {
    ...baseScene.character,
    knee_reach_ease_bias: 0.10
  },
  motion: {
    ...baseScene.motion,
    cycle_seconds: 1.33,
    stance_fraction: 0.6,
    screen_stride_scale: 0.64,
    root_y: 411,
    start_ramp_seconds: 0.48,
    stop_ramp_seconds: 2.8
  }
};

function text(x, y, value, size, color = C.white, anchor = 'start', weight = 700, extra = '') {
  return '<text x="' + fmt(x) + '" y="' + fmt(y) + '" font-family="Inter,Arial,sans-serif" font-size="' + size + '" font-weight="' + weight + '" fill="' + color + '" text-anchor="' + anchor + '" ' + extra + '>' + esc(value) + '</text>';
}
function line(x1, y1, x2, y2, color = C.line, width = 2, extra = '') {
  return '<path d="M ' + fmt(x1) + ' ' + fmt(y1) + ' L ' + fmt(x2) + ' ' + fmt(y2) + '" fill="none" stroke="' + color + '" stroke-width="' + width + '" stroke-linecap="round" ' + extra + '/>';
}
function rect(x, y, w, h, radius = 0, fill = 'none', stroke = 'none', strokeWidth = 0, extra = '') {
  return '<rect x="' + fmt(x) + '" y="' + fmt(y) + '" width="' + fmt(w) + '" height="' + fmt(h) + '" rx="' + radius + '" fill="' + fill + '" stroke="' + stroke + '" stroke-width="' + strokeWidth + '" ' + extra + '/>';
}
function circle(cx, cy, r, fill = 'none', stroke = C.white, strokeWidth = 2, extra = '') {
  return '<circle cx="' + fmt(cx) + '" cy="' + fmt(cy) + '" r="' + fmt(r) + '" fill="' + fill + '" stroke="' + stroke + '" stroke-width="' + strokeWidth + '" ' + extra + '/>';
}
function poly(points, color = C.white, width = 3, extra = '') {
  return '<polyline points="' + points.map((p) => fmt(p[0]) + ',' + fmt(p[1])).join(' ') + '" fill="none" stroke="' + color + '" stroke-width="' + width + '" stroke-linejoin="round" stroke-linecap="round" ' + extra + '/>';
}
function extractCharacter(frameIndex) {
  const svg = renderSvgFrame(GAIT_SCENE, frameIndex, 'free');
  const start = svg.indexOf('<g id="characterRig"');
  const end = svg.indexOf('<!--CHARACTER-RIG-END-->', start);
  if (start < 0 || end < 0) throw new Error('Character rig group was not emitted by render-preview.');
  return svg.slice(start, end);
}
function speakerGlyph(cx, cy, scale = 1, alert = 0) {
  const w = 118 * scale, h = 176 * scale;
  let s = '<g data-prop="smart-speaker" transform="translate(' + fmt(cx - w / 2) + ' ' + fmt(cy - h / 2) + ') scale(' + scale + ')">';
  s += '<ellipse cx="59" cy="176" rx="76" ry="12" fill="#000000" opacity="0.30"/>';
  s += rect(0, 0, 118, 176, 20, '#171D27', '#D5DAE2', 2.5);
  s += rect(10, 11, 98, 154, 14, '#0D1118', '#46505F', 1.2);
  s += circle(59, 45, 7, C.red, C.red, 1, 'opacity="' + fmt(0.55 + alert * 0.45) + '"');
  s += circle(59, 100, 28, 'none', '#9AA4B3', 2);
  s += circle(59, 100, 16, 'none', '#5F6979', 2);
  for (let i = 0; i < 6; i++) s += line(36 + i * 9, 139, 36 + i * 9, 145, '#8590A0', 2);
  s += '</g>';
  return s;
}
function drawWorldAndCharacter(seconds, frameIndex, phase = 'walk') {
  const pose = evaluateLocomotion(GAIT_SCENE, frameIndex, 'free');
  const movement = Math.max(0, pose.pelvis.x - GAIT_SCENE.motion.start_x);
  const progress = clamp(seconds / DURATION, 0, 1);
  const zoom = BASE_SCALE + 0.055 * smoothstep(Math.min(seconds / 4.2, 1)) - 0.018 * smoothstep((seconds - 6.8) / 2.8);
  const tx = W / 2 - pose.pelvis.x * zoom;
  const ty = FLOOR_SCREEN - GAIT_SCENE.background.horizon_y * zoom;
  let s = '<defs><linearGradient id="night-wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#151B26"/><stop offset="1" stop-color="#080A0E"/></linearGradient></defs>';
  s += '<rect width="' + W + '" height="' + H + '" fill="url(#night-wall)"/>';
  // Far wall: slower parallax, restrained architectural lines, no random decoration.
  s += '<g data-depth="far" transform="translate(' + fmt(-movement * zoom * 0.20) + ' 0)">';
  s += rect(-140, 206, 1250, 620, 0, '#0C1119', '#2D3541', 2);
  s += rect(70, 270, 148, 130, 1, '#111925', '#9AA3B1', 2.6);
  s += line(144, 270, 144, 400, '#8B95A3', 1.5);
  s += line(70, 334, 218, 334, '#8B95A3', 1.5);
  s += circle(191, 298, 15, 'none', C.gold, 2);
  s += line(-25, 824, 760, 824, '#2B3441', 1);
  s += '</g>';
  // Near layer and the character share the same world-space camera, preserving foot/ground contact.
  s += '<g data-depth="world" transform="translate(' + fmt(tx) + ' ' + fmt(ty) + ') scale(' + fmt(zoom) + ')">';
  s += rect(-320, 170, 1570, 400, 4, 'none', '#414B5B', 2.1);
  s += line(-320, 570, 1250, 570, '#C3CAD4', 2.6);
  for (let i = -7; i < 18; i++) s += line(i * 100 + 15, 598, i * 100 + 68, 598, '#414A57', 1.2);
  // Bed / furniture establishes the room, with a readable silhouette.
  s += rect(32, 484, 228, 58, 4, '#141B25', '#7C8796', 2.4);
  s += rect(43, 466, 84, 26, 7, '#26303D', '#8993A0', 1.5);
  s += rect(37, 537, 11, 33, 1, '#707B88', '#707B88', 0);
  s += rect(242, 537, 11, 33, 1, '#707B88', '#707B88', 0);
  s += line(54, 515, 232, 515, '#3C4654', 1.3);
  // Door and bedside table remain pinned in the same scene coordinates.
  s += rect(600, 275, 100, 295, 2, '#0A0E14', '#B5BDC8', 2.8);
  s += line(620, 295, 620, 547, '#3B4654', 1.6);
  s += circle(680, 425, 5, C.gold, C.gold, 1);
  s += rect(448, 506, 104, 64, 2, '#161D27', '#AAB3BE', 2.4);
  s += line(444, 506, 556, 506, '#D3D8DF', 3.6);
  s += line(458, 570, 458, 585, '#B3BBC5', 3);
  s += line(540, 570, 540, 585, '#B3BBC5', 3);
  s += speakerGlyph(500, 459, 0.46, 0.4 + 0.6 * smoothstep((seconds - 2.5) / 0.45));
  const rig = extractCharacter(frameIndex);
  s += '<g data-rig-stage="portrait-walk">' + rig + '</g>';
  s += '</g>';
  if (phase === 'hook') {
    const u = outCubic(seconds / 0.55);
    const y = 338 + 22 * (1 - u);
    const reveal = smoothstep((seconds - 0.1) / 0.7);
    s += '<g data-visual-element="hook-time" transform="translate(0 ' + fmt(y - 338) + ')">';
    s += rect(38, 330, 644, 198, 10, C.panel, '#596373', 1.6, '');
    s += rect(38, 330, 8, 198, 2, C.red, C.red, 0);
    s += text(74, 420, '03:04', 106, C.white, 'start', 850, 'letter-spacing="-2.5"');
    s += text(378, 418, 'AM', 32, C.red, 'start', 850, 'letter-spacing="1.5"');
    s += text(76, 474, 'PERANGKATNYA MENYALA SENDIRI', 18, C.muted, 'start', 650, 'opacity="' + fmt(reveal) + '" letter-spacing="0.7"');
    s += rect(76, 495, 566 * smoothstep(seconds / 0.95), 4, 2, C.red, C.red, 0);
    s += '</g>';
  }
  return s;
}
function drawHeader(frameIndex, shotIndex) {
  const progress = frameIndex / (FRAME_COUNT - 1);
  let s = '<g data-safe-zone="top-header">';
  s += text(40, 51, 'PUKUL 03:04', 18, C.white, 'start', 850, 'letter-spacing="1.4"');
  s += text(40, 83, 'JANGAN JAWAB', 22, C.red, 'start', 850, 'letter-spacing="1.5"');
  s += line(40, 108, 680, 108, '#38414E', 1.5);
  s += rect(40, 125, 640, 4, 2, '#242B36', '#242B36', 0);
  s += rect(40, 125, 640 * progress, 4, 2, C.red, C.red, 0);
  s += text(680, 151, 'MOTION STUDY  /  ' + String(shotIndex + 1).padStart(2, '0'), 11, C.muted, 'end', 650, 'letter-spacing="0.9"');
  s += '</g>';
  return s;
}
function drawCaption(main, sub, reveal = 1) {
  let s = '<g data-safe-zone="caption">';
  s += line(40, 991, 680, 991, '#394250', 1.6);
  s += text(40, 1034, main, 25, C.white, 'start', 820, 'opacity="' + fmt(reveal) + '" letter-spacing="0.15"');
  s += text(40, 1072, sub, 16, C.muted, 'start', 500, 'opacity="' + fmt(reveal) + '"');
  s += '</g>';
  return s;
}
function drawDeviceImpact(seconds) {
  const u = clamp(seconds / 1.45, 0, 1);
  const pulse = smoothstep(u);
  const radius = 112 + 106 * u;
  let s = '<rect width="' + W + '" height="' + H + '" fill="' + C.background + '"/>';
  s += '<g data-depth="device-background">';
  for (let i = 0; i < 9; i++) {
    const angle = (i / 9) * Math.PI * 2 - 0.4;
    const x1 = 360 + Math.cos(angle) * 180, y1 = 600 + Math.sin(angle) * 180;
    const x2 = 360 + Math.cos(angle) * 272, y2 = 600 + Math.sin(angle) * 272;
    s += line(x1, y1, x2, y2, i % 3 === 0 ? '#5A2932' : '#27303C', i % 3 === 0 ? 2 : 1);
  }
  s += circle(360, 600, radius, 'none', C.red, 2.5, 'opacity="' + fmt(1 - 0.88 * u) + '"');
  s += circle(360, 600, radius * 0.72, 'none', '#72323A', 1.5, 'opacity="' + fmt(0.8 - 0.65 * u) + '"');
  s += '</g>';
  s += speakerGlyph(360, 590, 1.62, 1 - 0.4 * u);
  s += line(439, 510, 558, 434, C.red, 2.2);
  s += circle(439, 510, 5, C.red, C.red, 1);
  s += text(514, 430, 'MIKROFON AKTIF', 14, C.red, 'start', 800, 'letter-spacing="0.3"');
  s += line(416, 653, 548, 714, C.gold, 2);
  s += circle(416, 653, 4, C.gold, C.gold, 1);
  s += text(552, 720, 'LED STATUS', 17, C.gold, 'start', 750, 'letter-spacing="0.7"');
  s += rect(86, 805, 548, 72, 8, C.panel, '#3E4857', 1.5);
  s += text(360, 836, 'STATUS PERANGKAT', 14, C.muted, 'middle', 650, 'letter-spacing="2"');
  s += text(360, 864, 'MENDENGARKAN', 23, C.white, 'middle', 850, 'letter-spacing="1.2"');
  return s;
}
function drawKineticRule(seconds) {
  const u = clamp(seconds / 1.43, 0, 1);
  const enterA = outCubic(u / 0.42);
  const enterB = outCubic((u - 0.18) / 0.48);
  let s = '<rect width="' + W + '" height="' + H + '" fill="' + C.background + '"/>';
  s += '<g opacity="0.24" data-background="quiet-line-grid">';
  for (let i = 0; i < 7; i++) s += line(36, 300 + i * 82, 684, 300 + i * 82, '#343D49', 1);
  s += '</g>';
  s += rect(42, 345, 636, 406, 10, C.panel, '#4D5868', 2);
  s += rect(72, 376, 140, 51, 4, C.red, C.red, 0);
  s += text(142, 409, 'PETUNJUK 01', 18, C.background, 'middle', 900, 'letter-spacing="1"');
  s += line(72, 453, 648, 453, '#343D49', 1.6);
  s += '<g data-visual-element="kinetic-word-one" transform="translate(' + fmt(-84 * (1 - enterA)) + ' 0)" opacity="' + fmt(enterA) + '">';
  s += text(356, 545, 'JANGAN', 64, C.white, 'middle', 900, 'letter-spacing="0.6"');
  s += '</g>';
  s += '<g data-visual-element="kinetic-word-two" transform="translate(' + fmt(98 * (1 - enterB)) + ' 0)" opacity="' + fmt(enterB) + '">';
  s += text(356, 627, 'JAWAB DIA.', 58, C.red, 'middle', 900, 'letter-spacing="0.3"');
  s += '</g>';
  s += rect(101, 677, 518, 5, 2, '#333D4A', '#333D4A', 0);
  s += rect(101, 677, 518 * smoothstep((u - 0.22) / 0.68), 5, 2, C.red, C.red, 0);
  s += text(360, 720, 'TENANGKAN VISUAL. TEGASKAN PESAN.', 13, C.muted, 'middle', 650, 'letter-spacing="0.7"');
  return s;
}
function drawEvidence(seconds) {
  const u = clamp(seconds / 1.43, 0, 1);
  const nodes = [
    { y: 324, title: 'RUANG', sub: '03:04 PAGI', kind: 'room' },
    { y: 510, title: 'PERANGKAT', sub: 'LED AKTIF', kind: 'device' },
    { y: 696, title: 'SINYAL', sub: 'POLA BERULANG', kind: 'signal' }
  ];
  let s = '<rect width="' + W + '" height="' + H + '" fill="' + C.background + '"/>';
  s += text(40, 222, 'HUBUNGKAN', 36, C.white, 'start', 900, 'letter-spacing="-0.2"');
  s += text(40, 265, 'PETUNJUKNYA.', 36, C.red, 'start', 900, 'letter-spacing="-0.2"');
  s += line(102, 364, 102, 736, '#4B5564', 2.5);
  s += line(102, 364, 102, 364 + 372 * smoothstep(u), C.red, 3.5);
  s += circle(102, 364 + 372 * smoothstep(u), 6, C.gold, C.gold, 1);
  for (let i = 0; i < nodes.length; i++) {
    const node = nodes[i];
    const local = smoothstep((u - i * 0.16) / 0.47);
    const dx = 36 * (1 - outCubic((u - i * 0.16) / 0.36));
    s += '<g data-evidence-node="' + node.kind + '" transform="translate(' + fmt(dx) + ' 0)" opacity="' + fmt(0.3 + 0.7 * local) + '">';
    s += rect(138, node.y, 532, 132, 8, C.card, '#515C6D', 1.8);
    s += circle(187, node.y + 50, 26, 'none', i === 1 ? C.red : '#BBC4D0', 2);
    if (node.kind === 'room') {
      s += rect(172, node.y + 39, 30, 22, 1, 'none', C.white, 1.7);
      s += line(187, node.y + 39, 187, node.y + 61, C.white, 1.1);
      s += line(172, node.y + 50, 202, node.y + 50, C.white, 1.1);
    } else if (node.kind === 'device') {
      s += rect(178, node.y + 26, 18, 48, 4, '#171D27', C.white, 1.7);
      s += circle(187, node.y + 38, 3.6, C.red, C.red, 1);
    } else {
      const wave = 8 + 9 * smoothstep(u);
      s += poly([[159,node.y+51],[169,node.y+51],[175,node.y+51-wave],[183,node.y+51+wave],[192,node.y+51-wave],[200,node.y+51],[214,node.y+51]], C.gold, 2.5);
    }
    s += text(232, node.y + 55, node.title, 23, C.white, 'start', 850, 'letter-spacing="1"');
    s += text(232, node.y + 88, node.sub, 15, C.muted, 'start', 650, 'letter-spacing="0.7"');
    s += '</g>';
  }
  s += text(138, 894, 'KONTEKS', 13, C.muted, 'start', 750, 'letter-spacing="0.9"');
  s += text(360, 894, 'SUMBER', 13, C.muted, 'middle', 750, 'letter-spacing="0.9"');
  s += text(670, 894, 'SINYAL', 13, C.muted, 'end', 750, 'letter-spacing="0.9"');
  return s;
}

const captions = [
  ['PUKUL 03:04 PAGI.', 'Perangkat menyala sebelum ruangan berubah.'],
  ['RUANGAN INI TADI SUNYI.', 'Kamera mengikuti langkah, bukan mengguncang dunia.'],
  ['SATU PETUNJUK KECIL.', 'Perhatikan indikatornya, bukan efeknya.'],
  ['JANGAN JAWAB DIA.', 'Teks bergerak hanya saat maknanya berubah.'],
  ['SUARANYA BUKAN KEBETULAN.', 'Gerakan mereda. Satu detail tetap menyala.'],
  ['TUNJUKKAN SEBAB DAN BUKTI.', 'Konteks → sumber → sinyal.']
];

function shotForFrame(frameIndex) {
  for (let i = 0; i < SHOT_STARTS.length - 1; i++) {
    if (frameIndex >= SHOT_STARTS[i] && frameIndex < SHOT_STARTS[i + 1]) {
      return { index: i, localFrame: frameIndex - SHOT_STARTS[i], length: SHOT_STARTS[i + 1] - SHOT_STARTS[i] };
    }
  }
  return { index: SHOT_STARTS.length - 2, localFrame: 0, length: 1 };
}
function drawShot(index, seconds, frameIndex) {
  if (index === 0) return drawWorldAndCharacter(seconds, frameIndex, 'hook');
  if (index === 1) return drawWorldAndCharacter(seconds, frameIndex, 'walk');
  if (index === 2) return drawDeviceImpact(seconds);
  if (index === 3) return drawKineticRule(seconds);
  if (index === 4) return drawWorldAndCharacter(seconds, frameIndex, 'settle');
  return drawEvidence(seconds);
}
export function renderReferenceVisualFrame(frameIndex) {
  if (!Number.isInteger(frameIndex) || frameIndex < 0 || frameIndex >= FRAME_COUNT) {
    throw new RangeError('Frame is outside the reference visual preview.');
  }
  const seconds = frameIndex / FPS;
  const shot = shotForFrame(frameIndex);
  let stage = '<g data-visual-shot="' + REFERENCE_VISUAL_SPEC.shots[shot.index] + '">' + drawShot(shot.index, shot.localFrame / FPS, frameIndex) + '</g>';
  const caption = captions[shot.index];
  let svg = '<svg xmlns="http://www.w3.org/2000/svg" width="' + W + '" height="' + H + '" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="Motion Studio kinetic portrait visual and gait proof">';
  svg += stage;
  svg += drawHeader(frameIndex, shot.index);
  svg += drawCaption(caption[0], caption[1], smoothstep(shot.localFrame / 8));
  if (shot.index > 0 && shot.localFrame < TRANSITION_FRAMES) {
    const transition = 1 - shot.localFrame / TRANSITION_FRAMES;
    const y = 180 + 750 * (shot.localFrame / (TRANSITION_FRAMES - 1));
    svg += line(0, y, W, y, C.red, 3.2, 'opacity="' + fmt(0.85 * transition) + '"');
  }
  svg += '</svg>';
  return svg;
}
function summarizePortraitGait() {
  let maxKneeStepPx = 0;
  let maxAnkleClampErrorPx = 0;
  let maxAnkleClampDetail = null;
  let maxBoneLengthErrorPx = 0;
  let maxStanceFootDriftPerFramePx = 0;
  let minStanceKneeAngleDegrees = Infinity;
  let previous = null;
  for (let frame = 0; frame < FRAME_COUNT; frame++) {
    const pose = evaluateLocomotion(GAIT_SCENE, frame, 'free');
    maxBoneLengthErrorPx = Math.max(maxBoneLengthErrorPx, pose.diagnostics.boneLengthErrorPx);
    for (const [side, foot, leg] of [['left', pose.leftFoot, pose.leftLeg], ['right', pose.rightFoot, pose.rightLeg]]) {
      if (leg.endpointClampErrorPx > maxAnkleClampErrorPx) {
        maxAnkleClampErrorPx = leg.endpointClampErrorPx;
        maxAnkleClampDetail = {
          frame, side, phase: foot.phase, inStance: foot.inStance,
          hip: leg.root, requestedReachPx: leg.requestedReachPx, solvedReachPx: leg.solvedReachPx,
          target: { x: foot.x, y: foot.y }, solvedAnkle: leg.end,
          endpointClampErrorPx: leg.endpointClampErrorPx
        };
      }
      if (foot.inStance) minStanceKneeAngleDegrees = Math.min(minStanceKneeAngleDegrees, leg.jointAngleDegrees);
    }
    if (previous) {
      for (const [side, footKey, legKey] of [
        ['left', 'leftFoot', 'leftLeg'],
        ['right', 'rightFoot', 'rightLeg']
      ]) {
        const oldFoot = previous[footKey], newFoot = pose[footKey];
        if (oldFoot.inStance && newFoot.inStance) {
          maxStanceFootDriftPerFramePx = Math.max(maxStanceFootDriftPerFramePx,
            Math.hypot(newFoot.x - oldFoot.x, newFoot.y - oldFoot.y));
        }
        const oldKnee = previous[legKey].knee, newKnee = pose[legKey].knee;
        maxKneeStepPx = Math.max(maxKneeStepPx, Math.hypot(newKnee.x - oldKnee.x, newKnee.y - oldKnee.y));
      }
    }
    previous = pose;
  }
  return {
    effectiveStridePx: GAIT_SCENE.motion.stride_length_px * GAIT_SCENE.motion.screen_stride_scale,
    gaitCycleSeconds: GAIT_SCENE.motion.cycle_seconds,
    cadenceStepsPerMinute: 120 / GAIT_SCENE.motion.cycle_seconds,
    maxKneeStepPx,
    minStanceKneeAngleDegrees,
    maxAnkleClampErrorPx,
    maxAnkleClampDetail,
    maxBoneLengthErrorPx,
    maxStanceFootDriftPerFramePx
  };
}

export function summarizeReferenceVisualSequence() {
  return {
    width: W, height: H, fps: FPS, durationSeconds: DURATION, frameCount: FRAME_COUNT,
    shots: [...REFERENCE_VISUAL_SPEC.shots],
    colorTokens: { ...C },
    safeZones: { ...REFERENCE_VISUAL_SPEC.safeZones },
    integratedGaitRig: true,
    portraitReachEaseBias: GAIT_SCENE.character.knee_reach_ease_bias,
    cameraMode: 'tracking camera with world-space scene parallax',
    motionDesign: ['hook-first typography', 'meaningful camera tracking', 'single prop alert pulse', 'staggered kinetic type', 'motion settles at end', 'stacked cause-evidence reveal'],
    secondaryMotionPolicy: 'reduced and phase-coupled; gait remains the primary motion',
    portraitGaitDiagnostics: summarizePortraitGait(),
    humanFullSpeedAcceptance: 'pending',
    audioIncluded: false,
    browserFfmpegParity: 'not_verified'
  };
}
export function renderReferenceVisualPreview(outputDirectory) {
  const outDir = path.resolve(outputDirectory || '.working/reference-visual');
  fs.mkdirSync(outDir, { recursive: true });
  for (let frame = 0; frame < FRAME_COUNT; frame++) {
    const filename = 'frame-' + String(frame).padStart(4, '0') + '.svg';
    fs.writeFileSync(path.join(outDir, filename), renderReferenceVisualFrame(frame), 'utf8');
  }
  return { outputDirectory: outDir, ...summarizeReferenceVisualSequence() };
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const out = process.argv[2] || '.working/reference-visual';
  const summary = renderReferenceVisualPreview(out);
  process.stdout.write(JSON.stringify(summary, null, 2) + '\n');
}
