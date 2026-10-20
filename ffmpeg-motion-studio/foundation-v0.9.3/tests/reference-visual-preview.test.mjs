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

test('vertical visual proof has the exact portrait profile and four shot families', () => {
  const spec = summarizeReferenceVisualSequence();
  assert.deepEqual([spec.width, spec.height, spec.fps, spec.frameCount], [720, 1280, 30, 240]);
  assert.equal(spec.durationSeconds, 8);
  assert.deepEqual(spec.shots, ['room-wide', 'object-detail', 'rule-card', 'evidence-diagram']);
  assert.equal(spec.audioIncluded, false);
  assert.equal(spec.humanFullSpeedAcceptance, 'pending');
});

test('keyframes preserve the persistent title, instruction accent and safe zones', () => {
  for (const frameIndex of [0, 59, 60, 119, 120, 179, 180, 239]) {
    const svg = renderReferenceVisualFrame(frameIndex);
    assert.match(svg, /width="720" height="1280"/);
    assert.match(svg, /IF YOUR SMART SPEAKER TALKS AT 03:04 AM/);
    assert.match(svg, /data-safe-zone="top-header"/);
    assert.match(svg, /data-safe-zone="main-stage"/);
    assert.match(svg, /data-safe-zone="caption"/);
    assert.match(svg, /data-safe-zone="footer"/);
    assert.doesNotMatch(svg, /\b(?:NaN|Infinity)\b/);
  }
});

test('shot transitions are deterministic and all composition variants render', () => {
  const frames = [0, 60, 120, 180];
  const markers = ['room-wide', 'object-detail', 'rule-card', 'evidence-diagram'];
  for (let i = 0; i < frames.length; i++) {
    const a = renderReferenceVisualFrame(frames[i]);
    assert.equal(a, renderReferenceVisualFrame(frames[i]));
    assert.ok(a.includes('data-visual-shot="' + markers[i] + '"'));
  }
  assert.throws(() => renderReferenceVisualFrame(-1), RangeError);
  assert.throws(() => renderReferenceVisualFrame(240), RangeError);
});

test('palette maintains strong contrast for primary instructional text', () => {
  const { background, white, muted, red, gold } = REFERENCE_VISUAL_SPEC.colors;
  assert.ok(contrastRatio(white, background) >= 12, 'primary text contrast must remain high');
  assert.ok(contrastRatio(muted, background) >= 5, 'secondary text must remain legible');
  assert.ok(contrastRatio(red, background) >= 5, 'warning accent must remain identifiable');
  assert.ok(contrastRatio(gold, background) >= 7, 'secondary accent must remain legible');
});
