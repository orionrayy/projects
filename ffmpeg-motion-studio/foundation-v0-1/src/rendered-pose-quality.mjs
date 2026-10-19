import { evaluateFrame } from "./motion-core.mjs";

const HAND_TRANSFORM = /<g id="pointing-hand" transform="translate\((-?[\d.]+) (-?[\d.]+)\) rotate\((-?[\d.]+)\) scale\((-?[\d.]+) 1\)">/;
const INDEX_FINGER_GROUP = /<g id="index-finger">([\s\S]*?)<\/g>/;
const radians = degrees => degrees * Math.PI / 180;
const degrees = radiansValue => radiansValue * 180 / Math.PI;
const distance = (a,b) => Math.hypot(b.x-a.x,b.y-a.y);
const angularDistance = (a,b) => Math.abs(Math.atan2(Math.sin(a-b),Math.cos(a-b)));

export function evaluateRenderedPoseQuality(scene, frameIndex, svg) {
  const issues = [];
  const state = evaluateFrame(scene, frameIndex);
  const transformMatch = typeof svg === "string" ? svg.match(HAND_TRANSFORM) : null;
  const fingerMatch = typeof svg === "string" ? svg.match(INDEX_FINGER_GROUP) : null;
  const hasTipMarker = Boolean(fingerMatch && /cx="25" cy="0"/.test(fingerMatch[1]));

  if (!transformMatch) issues.push("POINTING_HAND_TRANSFORM_MISSING");
  if (!fingerMatch) issues.push("INDEX_FINGER_GROUP_MISSING");
  if (fingerMatch && !hasTipMarker) issues.push("INDEX_FINGER_TIP_MISSING");

  if (!transformMatch || !fingerMatch || !hasTipMarker) {
    return {
      frameIndex, passed: false, issues,
      renderedAimErrorDegrees: null,
      renderedHandOriginErrorPx: null,
      renderedFingerTipErrorPx: null,
      handScaleError: null
    };
  }

  const [, txRaw, tyRaw, angleRaw, scaleRaw] = transformMatch;
  const renderedOrigin = { x: Number(txRaw), y: Number(tyRaw) };
  const renderedAngle = radians(Number(angleRaw));
  const renderedScaleX = Number(scaleRaw);
  const expectedAngle = Math.atan2(
    state.target.y - state.wrist.y,
    state.target.x - state.wrist.x
  );
  const renderedAimErrorDegrees = degrees(angularDistance(renderedAngle, expectedAngle));
  const renderedHandOriginErrorPx = distance(renderedOrigin, state.wrist);
  const renderedTip = {
    x: renderedOrigin.x + 25 * renderedScaleX * Math.cos(renderedAngle),
    y: renderedOrigin.y + 25 * renderedScaleX * Math.sin(renderedAngle)
  };
  const renderedFingerTipErrorPx = distance(renderedTip, state.fingerTip);
  const expectedScaleX = scene.character.hand_length / 25;
  const handScaleError = Math.abs(renderedScaleX - expectedScaleX);
  const aimTolerance = scene.quality_contract.max_hand_aim_error_degrees;

  if (renderedAimErrorDegrees > aimTolerance) issues.push("RENDERED_HAND_AIM");
  if (renderedHandOriginErrorPx > 0.01) issues.push("RENDERED_HAND_ORIGIN");
  if (renderedFingerTipErrorPx > 0.05) issues.push("RENDERED_FINGER_TIP");
  if (handScaleError > 0.005) issues.push("RENDERED_HAND_SCALE");

  return {
    frameIndex,
    passed: issues.length === 0,
    issues,
    expectedAimDegrees: degrees(expectedAngle),
    renderedAimDegrees: Number(angleRaw),
    renderedAimErrorDegrees: Number(renderedAimErrorDegrees.toFixed(6)),
    renderedHandOriginErrorPx: Number(renderedHandOriginErrorPx.toFixed(6)),
    renderedFingerTipErrorPx: Number(renderedFingerTipErrorPx.toFixed(6)),
    handScaleError: Number(handScaleError.toFixed(6))
  };
}
