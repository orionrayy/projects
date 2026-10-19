/**
 * Deterministic, phase-coupled whole-body motion channels.
 *
 * This is a motion planner, not captured human data or a claim of biomechanical perfection.
 * Displacements scale with scale; angles remain radians. carryWeight blends between a free-arm
 * walk and a constrained carry, where hand targets are expected to be locked to a prop.
 */
const clamp = (value, low, high) => Math.min(high, Math.max(low, value));
const finite = (value, name) => {
  if (!Number.isFinite(value)) throw new TypeError(`${name} must be finite.`);
  return value;
};

export function phaseFromTravel(travelDistance, strideLength, phaseOffset = 0) {
  finite(travelDistance, "travelDistance");
  finite(strideLength, "strideLength");
  finite(phaseOffset, "phaseOffset");
  if (!(strideLength > 0)) throw new RangeError("strideLength must be positive.");
  return (2 * Math.PI * travelDistance) / strideLength + phaseOffset;
}

export function evaluateWholeBodyMotion({
  phase,
  scale = 1,
  facing = 1,
  carryWeight = 0,
} = {}) {
  finite(phase, "phase");
  finite(scale, "scale");
  finite(facing, "facing");
  finite(carryWeight, "carryWeight");
  if (!(scale > 0)) throw new RangeError("scale must be positive.");
  const f = facing >= 0 ? 1 : -1;
  const c = clamp(carryWeight, 0, 1);
  const p = phase;
  const free = 1 - c;
  const gaitPhase = ((p % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI);

  const bodyBob = scale * 0.68 * (1 - Math.cos(2 * p));
  const pelvisSway = f * scale * 0.90 * Math.sin(p - 0.22);
  const shoulderSway = f * scale * 1.75 * Math.sin(p + 0.18);
  const torsoPitch = 0.018 + 0.040 * Math.sin(p - 0.34) + 0.009 * Math.sin(2 * p + 0.25);
  const headCounterSway = -f * scale * 1.45 * Math.sin(p - 0.48);
  const headNod = 0.016 * Math.sin(2 * p - 0.55);
  const armSwingLeft = free * 0.19 * Math.sin(p + 0.25);
  const armSwingRight = -free * 0.19 * Math.sin(p + 0.25);
  const carryOffsetX = c * scale * 3.0 * Math.sin(p - 0.66);
  const carryOffsetY = c * scale * 1.45 * Math.sin(2 * p - 0.72);
  const carryRotation = c * 0.038 * Math.sin(p - 0.62);
  const elbowResponse = c * scale * 1.40 * Math.sin(p - 0.88);

  return {
    phase: p,
    support: {
      left: gaitPhase < Math.PI ? "stance" : "swing",
      right: gaitPhase >= Math.PI ? "stance" : "swing",
    },
    pelvis: { swayX: pelvisSway, bounceY: bodyBob },
    torso: { pitch: torsoPitch, shoulderSwayX: shoulderSway },
    head: { counterSwayX: headCounterSway, nod: headNod },
    arms: { leftSwing: armSwingLeft, rightSwing: armSwingRight, elbowResponse },
    carriedProp: { offsetX: carryOffsetX, offsetY: carryOffsetY, rotation: carryRotation, weight: c },
  };
}
