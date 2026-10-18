export function rotatePoint(point, pivot, radians) {
  const dx=point.x-pivot.x, dy=point.y-pivot.y, c=Math.cos(radians), s=Math.sin(radians);
  return {x:pivot.x+dx*c-dy*s,y:pivot.y+dx*s+dy*c};
}
export function createCharacterRig(scene,{rootX,torsoAngle=0,headNod=0}={}) {
  const c=scene.character,o=c.origin,x=Number.isFinite(rootX)?rootX:o.x;
  const root={x,y:o.y},pelvis={x:x+4,y:o.y+c.pelvis_y};
  const world=p=>rotatePoint(p,pelvis,torsoAngle);
  const headBase={x:x+c.head.offset_x,y:o.y+c.head.offset_y};
  return {
    root,pelvis,
    shoulder:world({x:x+c.shoulder.offset_x,y:o.y+c.shoulder.offset_y}),
    head:world(headBase),
    neckBase:world({x:x+14,y:o.y+22}),
    neckTop:world({x:headBase.x+10,y:headBase.y+37}),
    torsoAngle,headAngle:torsoAngle*.62+headNod
  };
}
export function suggestElbowPole(shoulder,wrist,upperLength,bend=1) {
  const dx=wrist.x-shoulder.x,dy=wrist.y-shoulder.y,d=Math.max(1e-8,Math.hypot(dx,dy));
  const ux=dx/d,uy=dy/d,side=bend>=0?1:-1,along=upperLength*.5,lateral=upperLength*.72*side;
  return {x:shoulder.x+ux*along-uy*lateral,y:shoulder.y+uy*along+ux*lateral};
}
