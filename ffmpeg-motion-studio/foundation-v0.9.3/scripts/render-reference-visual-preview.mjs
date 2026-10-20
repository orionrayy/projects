import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const REFERENCE_VISUAL_SPEC = Object.freeze({
  width: 720,
  height: 1280,
  fps: 30,
  durationSeconds: 8,
  frameCount: 240,
  colors: Object.freeze({
    background: '#080A0E',
    white: '#F5F5F5',
    muted: '#A5ABB6',
    line: '#626A76',
    red: '#F0444F',
    gold: '#E7B56D',
    card: '#11151C'
  }),
  shots: Object.freeze(['room-wide', 'object-detail', 'rule-card', 'evidence-diagram']),
  safeZones: Object.freeze({ left: 40, right: 40, headerTop: 32, headerBottom: 132, captionTop: 1060, footerBottom: 1250 })
});

const { width: W, height: H, fps: FPS, durationSeconds: DURATION, frameCount: FRAME_COUNT, colors: C } = REFERENCE_VISUAL_SPEC;
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
const smoothstep = (v) => { const t = clamp(v, 0, 1); return t * t * (3 - 2 * t); };
const fmt = (v) => Number.isFinite(v) ? Number(v).toFixed(2) : '0.00';
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&apos;');

function text(x, y, value, size, color = C.white, anchor = 'start', weight = 600, extra = '') {
  return '<text x="' + fmt(x) + '" y="' + fmt(y) + '" font-family="Inter,Arial,sans-serif" font-size="' + size + '" font-weight="' + weight + '" fill="' + color + '" text-anchor="' + anchor + '" ' + extra + '>' + esc(value) + '</text>';
}
function line(x1, y1, x2, y2, color = C.line, width = 2, extra = '') {
  return '<path d="M ' + fmt(x1) + ' ' + fmt(y1) + ' L ' + fmt(x2) + ' ' + fmt(y2) + '" fill="none" stroke="' + color + '" stroke-width="' + width + '" stroke-linecap="round" ' + extra + '/>';
}
function rect(x, y, w, h, radius = 0, fill = 'none', stroke = C.line, strokeWidth = 2, extra = '') {
  return '<rect x="' + fmt(x) + '" y="' + fmt(y) + '" width="' + fmt(w) + '" height="' + fmt(h) + '" rx="' + radius + '" fill="' + fill + '" stroke="' + stroke + '" stroke-width="' + strokeWidth + '" ' + extra + '/>';
}
function circle(cx, cy, r, fill = 'none', stroke = C.white, strokeWidth = 2, extra = '') {
  return '<circle cx="' + fmt(cx) + '" cy="' + fmt(cy) + '" r="' + fmt(r) + '" fill="' + fill + '" stroke="' + stroke + '" stroke-width="' + strokeWidth + '" ' + extra + '/>';
}
function poly(points, color = C.white, width = 3, extra = '') {
  return '<polyline points="' + points.map((p) => fmt(p[0]) + ',' + fmt(p[1])).join(' ') + '" fill="none" stroke="' + color + '" stroke-width="' + width + '" stroke-linejoin="round" stroke-linecap="round" ' + extra + '/>';
}
function iconSpeaker(cx, cy, scale = 1, t = 0) {
  const w = 118 * scale, h = 176 * scale;
  const pulse = 0.5 + 0.5 * Math.sin(t * Math.PI * 2);
  let s = '<g data-visual-element="smart-speaker" transform="translate(' + fmt(cx - w / 2) + ' ' + fmt(cy - h / 2) + ') scale(' + scale + ')">';
  s += '<ellipse cx="59" cy="176" rx="78" ry="13" fill="#000000" opacity="0.35"/>';
  s += rect(0, 0, 118, 176, 21, '#171C24', '#AAB1BC', 3);
  s += rect(11, 12, 96, 152, 15, '#0D1117', '#3F4855', 1);
  s += circle(59, 49, 7, C.red, C.red, 1, 'opacity="' + fmt(0.65 + 0.3 * pulse) + '"');
  s += circle(59, 100, 27, 'none', '#747D89', 2);
  s += circle(59, 100, 15, 'none', '#444C58', 2);
  for (let i = 0; i < 6; i++) s += line(36 + i * 9, 139, 36 + i * 9, 145, '#747D89', 2);
  s += '</g>';
  return s;
}
function drawRoom(t) {
  let s = '<g data-visual-element="room-wide-set">';
  s += rect(48, 218, 624, 700, 10, '#0B0E13', '#59616E', 2);
  s += line(48, 918, 672, 918, '#8F97A3', 3);
  s += rect(96, 325, 142, 108, 2, '#10151D', '#B5BBC5', 3);
  s += line(167, 325, 167, 433, '#B5BBC5', 2);
  s += line(96, 378, 238, 378, '#B5BBC5', 2);
  s += circle(201, 350, 15, 'none', C.gold, 2);
  s += rect(530, 369, 106, 493, 2, '#10141B', '#D1D5DC', 3);
  s += circle(612, 623, 5, C.gold, C.gold, 1);
  s += line(126, 754, 470, 754, '#BBC1CA', 4);
  s += rect(126, 754, 344, 124, 3, '#111720', '#AAB1BC', 2);
  s += rect(146, 770, 122, 35, 3, '#252B35', '#7E8793', 1);
  s += line(128, 846, 466, 846, '#59616E', 2);
  s += line(145, 878, 145, 918, '#BBC1CA', 5);
  s += line(451, 878, 451, 918, '#BBC1CA', 5);
  s += '<g data-visual-element="sleeping-silhouette" stroke="#F5F5F5" fill="none" stroke-linecap="round" stroke-linejoin="round">';
  s += circle(287, 748, 15, C.white, C.white, 2);
  s += line(301, 752, 355, 766, C.white, 12);
  s += line(341, 764, 386, 773, C.white, 9);
  s += line(319, 760, 344, 786, C.white, 5);
  s += line(355, 766, 391, 752, C.white, 5);
  s += '</g>';
  s += rect(454, 804, 76, 82, 2, '#171C24', '#9CA4AF', 2);
  s += line(462, 816, 522, 816, '#737D89', 2);
  s += iconSpeaker(492, 756, 0.44, t);
  s += circle(492, 722, 5 + 2 * Math.sin(t * Math.PI * 2), 'none', C.red, 2, 'opacity="' + fmt(0.55 + 0.35 * (0.5 + 0.5 * Math.sin(t * Math.PI * 2))) + '"');
  s += text(84, 953, 'WIDE SHOT  /  ESTABLISH THE ROOM', 15, C.muted, 'start', 600, 'letter-spacing="1.2"');
  s += '</g>';
  return s;
}
function drawObjectDetail(t) {
  const ring = 1 + 0.12 * (0.5 + 0.5 * Math.sin(t * Math.PI * 2));
  let s = '<g data-visual-element="object-detail">';
  s += circle(360, 585, 182 * ring, 'none', C.red, 2, 'opacity="0.35"');
  s += circle(360, 585, 150 * ring, 'none', '#6F2E36', 2, 'opacity="0.55"');
  s += iconSpeaker(360, 590, 1.65, t);
  s += line(438, 500, 555, 418, C.red, 2);
  s += circle(438, 500, 5, C.red, C.red, 1);
  s += text(563, 412, 'MIC / ACTIVE', 17, C.red, 'start', 700, 'letter-spacing="1"');
  s += line(424, 655, 549, 714, C.gold, 2);
  s += circle(424, 655, 4, C.gold, C.gold, 1);
  s += text(555, 719, 'STATUS LED', 16, C.gold, 'start', 650, 'letter-spacing="0.8"');
  s += rect(125, 840, 470, 74, 10, '#10141B', '#414A56', 2);
  s += text(360, 871, 'DEVICE STATUS', 15, C.muted, 'middle', 650, 'letter-spacing="2"');
  s += text(360, 897, 'LISTENING  /  03:04 AM', 19, C.white, 'middle', 750, 'letter-spacing="0.5"');
  s += '</g>';
  return s;
}
function drawRuleCard(t) {
  const enter = 16 * (1 - smoothstep(t / 0.24));
  let s = '<g data-visual-element="rule-card" transform="translate(0 ' + fmt(enter) + ')">';
  s += rect(54, 376, 612, 388, 8, C.card, '#4D5663', 2);
  s += rect(82, 410, 126, 57, 5, C.red, C.red, 1);
  s += text(145, 448, 'RULE 04', 23, C.background, 'middle', 850, 'letter-spacing="1"');
  s += line(82, 504, 638, 504, '#3B434F', 2);
  s += text(360, 581, 'DO NOT', 35, C.white, 'middle', 800, 'letter-spacing="2"');
  s += text(360, 633, 'ANSWER IT', 43, C.white, 'middle', 850, 'letter-spacing="1.4"');
  s += rect(176, 675, 368, 5, 2, '#3B434F', '#3B434F', 0);
  s += rect(176, 675, 368 * smoothstep(t / 1.5), 5, 2, C.red, C.red, 0);
  for (let i = 0; i < 7; i++) s += rect(246 + i * 34, 711, 22, 8, 3, i === 3 ? C.red : '#4B535E', i === 3 ? C.red : '#4B535E', 0);
  s += '</g>';
  return s;
}
function drawEvidenceDiagram(t) {
  let s = '<g data-visual-element="evidence-diagram">';
  const cards = [
    { x: 42, title: 'ROOM', sub: '03:04 AM' },
    { x: 267, title: 'DEVICE', sub: 'ACTIVE' },
    { x: 492, title: 'SIGNAL', sub: 'REPEATING' }
  ];
  for (let i = 0; i < cards.length; i++) {
    const c = cards[i];
    s += rect(c.x, 395, 186, 262, 7, '#10141B', '#4C5562', 2);
    s += circle(c.x + 93, 455, 32, 'none', i === 1 ? C.red : '#9EA6B1', 2);
    if (i === 0) {
      s += rect(c.x + 70, 439, 46, 34, 1, 'none', C.white, 2);
      s += line(c.x + 93, 439, c.x + 93, 473, C.white, 1);
      s += line(c.x + 70, 456, c.x + 116, 456, C.white, 1);
    } else if (i === 1) {
      s += rect(c.x + 81, 425, 24, 60, 6, '#171C24', C.white, 2);
      s += circle(c.x + 93, 438, 3.5, C.red, C.red, 1);
    } else {
      const wave = 8 + 10 * (0.5 + 0.5 * Math.sin(t * Math.PI * 4));
      s += poly([[c.x + 55,455],[c.x + 71,455],[c.x + 80,455-wave],[c.x + 91,455+wave],[c.x + 103,455-wave],[c.x + 114,455],[c.x + 132,455]], C.gold, 3);
    }
    s += text(c.x + 93, 534, c.title, 21, C.white, 'middle', 750, 'letter-spacing="1"');
    s += text(c.x + 93, 568, c.sub, 15, C.muted, 'middle', 650, 'letter-spacing="0.7"');
    s += line(c.x + 34, 597, c.x + 152, 597, '#3C4450', 1);
  }
  s += line(230, 526, 257, 526, C.red, 3);
  s += line(455, 526, 482, 526, C.red, 3);
  s += circle(241 + 225 * (t / 2 - Math.floor(t / 2)), 526, 5, C.gold, C.gold, 1);
  s += rect(116, 710, 488, 98, 5, 'none', '#505966', 2);
  s += text(360, 748, 'ONE VISUAL IDEA PER SHOT', 21, C.white, 'middle', 750, 'letter-spacing="1"');
  s += text(360, 780, 'SHOW THE CAUSE  /  SHOW THE EVIDENCE', 14, C.gold, 'middle', 650, 'letter-spacing="0.3"');
  s += '</g>';
  return s;
}
function drawShot(index, localSeconds) {
  const names = REFERENCE_VISUAL_SPEC.shots;
  let body = '';
  if (index === 0) body = drawRoom(localSeconds);
  else if (index === 1) body = drawObjectDetail(localSeconds);
  else if (index === 2) body = drawRuleCard(localSeconds);
  else body = drawEvidenceDiagram(localSeconds);
  return '<g data-visual-shot="' + names[index] + '">' + body + '</g>';
}
const captions = [
  ['IT MAY ALREADY BE LISTENING.', 'Keep the scene quiet. Give the viewer one focal point.'],
  ['THE STATUS LIGHT IS NOT DECORATION.', 'A small accent identifies the important object.'],
  ['RULE 04  /  DO NOT ANSWER IT.', 'Typography becomes a deliberate story beat.'],
  ['SHOW THE CAUSE.  SHOW THE EVIDENCE.', 'Connect the object, the signal, and the consequence.']
];

export function renderReferenceVisualFrame(frameIndex) {
  if (!Number.isInteger(frameIndex) || frameIndex < 0 || frameIndex >= FRAME_COUNT) {
    throw new RangeError('Frame is outside the reference visual preview.');
  }
  const time = frameIndex / FPS;
  const shotIndex = Math.min(3, Math.floor(time / 2));
  const localSeconds = time - shotIndex * 2;
  const progress = frameIndex / (FRAME_COUNT - 1);
  const shotFade = shotIndex === 0 ? 1 : smoothstep(localSeconds / 0.18);
  let stage = '';
  if (shotIndex > 0 && localSeconds < 0.18) {
    stage += '<g opacity="' + fmt(1 - shotFade) + '">' + drawShot(shotIndex - 1, 2) + '</g>';
  }
  stage += '<g opacity="' + fmt(shotFade) + '">' + drawShot(shotIndex, localSeconds) + '</g>';
  const caption = captions[shotIndex];
  let svg = '<svg xmlns="http://www.w3.org/2000/svg" width="' + W + '" height="' + H + '" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="Motion Studio vertical visual reference proof">';
  svg += '<rect width="' + W + '" height="' + H + '" fill="' + C.background + '"/>';
  svg += '<g data-safe-zone="top-header">';
  svg += text(40, 48, 'IF YOUR SMART SPEAKER TALKS AT 03:04 AM', 20, C.white, 'start', 800, 'letter-spacing="0.45"');
  svg += text(40, 83, 'DON’T ANSWER IT', 20, C.red, 'start', 800, 'letter-spacing="1.2"');
  svg += line(40, 111, 680, 111, '#323944', 1);
  svg += rect(40, 125, 640, 3, 1, '#252B35', '#252B35', 0);
  svg += rect(40, 125, 640 * progress, 3, 1, C.red, C.red, 0);
  svg += text(680, 151, 'VISUAL LAB  /  ' + String(shotIndex + 1).padStart(2, '0'), 12, C.muted, 'end', 600, 'letter-spacing="1"');
  svg += '</g>';
  svg += '<g data-safe-zone="main-stage">' + stage + '</g>';
  svg += '<g data-safe-zone="caption">';
  svg += line(40, 1067, 680, 1067, '#323944', 1);
  svg += text(40, 1103, caption[0], 24, C.white, 'start', 800, 'letter-spacing="0.15"');
  svg += text(40, 1138, caption[1], 16, C.muted, 'start', 500);
  svg += '</g>';
  svg += '<g data-safe-zone="footer">';
  svg += line(40, 1206, 680, 1206, '#242A33', 1);
  svg += text(40, 1238, 'MOTION STUDIO  /  REFERENCE VISUAL LAB', 12, C.muted, 'start', 600, 'letter-spacing="1.1"');
  svg += text(680, 1238, String(frameIndex).padStart(4, '0') + ' / ' + FRAME_COUNT, 12, C.muted, 'end', 600);
  svg += '</g></svg>';
  return svg;
}

export function summarizeReferenceVisualSequence() {
  return {
    width: W, height: H, fps: FPS, durationSeconds: DURATION, frameCount: FRAME_COUNT,
    shots: [...REFERENCE_VISUAL_SPEC.shots],
    colorTokens: { ...C },
    safeZones: { ...REFERENCE_VISUAL_SPEC.safeZones },
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
