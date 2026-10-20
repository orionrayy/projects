import test from 'node:test';
import assert from 'node:assert/strict';
import {
  REFERENCE_VISUAL_SPEC,
  renderReferenceVisualFrame,
  summarizeReferenceVisualSequence
} from '../scripts/render-reference-visual-preview.mjs';

function luminance(hex) {
  const channels = hex.replace('#', '').match(/.{2}/g).map((v) => parseInt(v, 16) / 255);
  const linear = channels.map((v) => v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
  return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2];
}
function contrastRatio(a, b) {
  const values = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (values[0] + 0.05) / (values[1] + 0.05);
}

test('portrait motion proof uses a full 10s timeline, six distinct shot families and the actual gait rig', () => {
  const spec = summarizeReferenceVisualSequence();
  assert.deepEqual([spec.width, spec.height, spec.fps, spec.frameCount], [720, 1280, 30, 300]);
  assert.equal(spec.durationSeconds, 10);
  assert.deepEqual(spec.shots, ['hook-time', 'room-tracking-walk', 'device-impact', 'kinetic-rule', 'walk-to-settle', 'cause-evidence']);
  assert.equal(spec.integratedGaitRig, true);
  const gait = spec.portraitGaitDiagnostics;
  assert.ok(gait.effectiveStridePx >= 95, 'portrait steps should be larger than the prior 85px cycle');
  assert.ok(gait.cadenceStepsPerMinute >= 88 && gait.cadenceStepsPerMinute <= 96);
  assert.ok(gait.maxKneeStepPx < 13.0, 'portrait knee step spike: ' + gait.maxKneeStepPx);
  assert.ok(gait.minStanceKneeAngleDegrees > 148, 'portrait stance knee collapses: ' + gait.minStanceKneeAngleDegrees);
  assert.ok(gait.maxAnkleClampErrorPx < 1.5, 'portrait ankle reach error: ' + JSON.stringify(gait.maxAnkleClampDetail));
  assert.ok(gait.maxBoneLengthErrorPx < 0.02, 'portrait bone-length error: ' + gait.maxBoneLengthErrorPx);
  assert.ok(gait.maxStanceFootDriftPerFramePx < 0.05, 'portrait stance foot drift: ' + gait.maxStanceFootDriftPerFramePx);
  assert.equal(spec.audioIncluded, false);
  assert.equal(spec.humanFullSpeedAcceptance, 'pending');
});

test('hook, character walk, object impact, kinetic type and evidence all render deterministically', () => {
  const examples = [
    [0, 'hook-time', '03:04'],
    [45, 'room-tracking-walk', 'characterRig'],
    [130, 'device-impact', 'MIKROFON AKTIF'],
    [175, 'kinetic-rule', 'JAWAB DIA.'],
    [225, 'walk-to-settle', 'characterRig'],
    [275, 'cause-evidence', 'data-evidence-node="signal"']
  ];
  for (const [frameIndex, shot, content] of examples) {
    const svg = renderReferenceVisualFrame(frameIndex);
    assert.match(svg, /width="720" height="1280"/);
    assert.ok(svg.includes('data-visual-shot="' + shot + '"'), 'missing shot: ' + shot);
    assert.ok(svg.includes(content), 'missing visible content: ' + content);
    assert.equal((svg.match(/data-safe-zone="caption"/g) || []).length, 1, 'each frame should render one caption track only');
    assert.doesNotMatch(svg, /\b(?:NaN|Infinity|undefined)\b/);
    assert.equal(svg, renderReferenceVisualFrame(frameIndex), 'random-access frame should be deterministic');
  }
});

test('walk and text-animation frames change over time, without forcing all objects to move', () => {
  assert.notEqual(renderReferenceVisualFrame(45), renderReferenceVisualFrame(46));
  assert.notEqual(renderReferenceVisualFrame(175), renderReferenceVisualFrame(176));
  assert.notEqual(renderReferenceVisualFrame(275), renderReferenceVisualFrame(276));
  const walk = renderReferenceVisualFrame(60);
  assert.match(walk, /data-rig-stage="portrait-walk"/);
  assert.match(walk, /data-depth="far"/);
  assert.match(walk, /data-depth="world"/);
  assert.throws(() => renderReferenceVisualFrame(-1), RangeError);
  assert.throws(() => renderReferenceVisualFrame(300), RangeError);
});

test('persistent header/caption safe zones and strong text contrast are preserved', () => {
  for (const frameIndex of [0, 32, 33, 113, 114, 157, 158, 200, 201, 256, 257, 299]) {
    const svg = renderReferenceVisualFrame(frameIndex);
    assert.match(svg, /data-safe-zone="top-header"/);
    assert.match(svg, /data-safe-zone="caption"/);
    assert.match(svg, /PUKUL 03:04/);
    assert.match(svg, /JANGAN JAWAB/);
  }
  const { background, white, muted, red, gold } = REFERENCE_VISUAL_SPEC.colors;
  assert.ok(contrastRatio(white, background) >= 12);
  assert.ok(contrastRatio(muted, background) >= 5);
  assert.ok(contrastRatio(red, background) >= 5);
  assert.ok(contrastRatio(gold, background) >= 7);
});
