export function rotatePoint(point, pivot, radians) {
  const dx = point.x - pivot.x;
  const dy = point.y - pivot.y;
  const c = Math.cos(radians);
  const s = Math.sin(radians);
  return {
    x: pivot.x + dx * c - dy * s,
    y: pivot.y + dx * s + dy * c,
  };
}

export function createCharacterRig(scene, { rootX, torsoAngle = 0, headNod = 0 } = {}) {
  const character = scene.character;
  const origin = character.origin;
  const x = Number.isFinite(rootX) ? rootX : origin.x;
  const root = { x, y: origin.y };
  const pelvis = { x, y: origin.y + character.pelvis_y };
  const localToWorld = (point) => rotatePoint(point, pelvis, torsoAngle);
  const headLocal = {
    x: x + character.head.offset_x,
    y: origin.y + character.head.offset_y,
  };
  const rightShoulder = localToWorld({
    x: x + character.shoulder.offset_x,
    y: origin.y + character.shoulder.offset_y,
  });
  const leftArm = character.far_arm;
  const leftShoulder = localToWorld({
    x: x + leftArm.shoulder_offset_x,
    y: origin.y + leftArm.shoulder_offset_y,
  });

  return {
    root,
    pelvis,
    // Anatomical naming is avoided in this front-three-quarter master until a
    // camera/view convention is explicit. Screen-left and screen-right are unambiguous.
    screenLeftShoulder: leftShoulder,
    screenRightShoulder: rightShoulder,
    screenLeftRestWrist: localToWorld({
      x: x + leftArm.rest_wrist_offset_x,
      y: origin.y + leftArm.rest_wrist_offset_y,
    }),
    screenRightRestWrist: localToWorld({
      x: x + character.rest_pose.wrist_offset_x,
      y: origin.y + character.rest_pose.wrist_offset_y,
    }),
    head: localToWorld(headLocal),
    neckBase: localToWorld({ x: x + 8, y: origin.y + 20 }),
    neckTop: localToWorld({ x: headLocal.x + 5, y: headLocal.y + character.head.radius - 2 }),
    torsoAngle,
    headAngle: torsoAngle * 0.62 + headNod,
  };
}

// A pole target selects one of the two valid elbow solutions. It controls
// branch preference only; joint limits and silhouette collision checks are separate.
export function suggestElbowPole(shoulder, wrist, upperLength, bend = 1) {
  const dx = wrist.x - shoulder.x;
  const dy = wrist.y - shoulder.y;
  const length = Math.max(1e-8, Math.hypot(dx, dy));
  const ux = dx / length;
  const uy = dy / length;
  const side = bend >= 0 ? 1 : -1;
  const along = upperLength * 0.5;
  const lateral = upperLength * 0.72 * side;
  return {
    x: shoulder.x + ux * along - uy * lateral,
    y: shoulder.y + uy * along + ux * lateral,
  };
}
