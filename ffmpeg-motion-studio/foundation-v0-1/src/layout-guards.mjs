// Geometric reservations are hard checks, not a subjective aesthetic score.
export function inspectSceneLayout(scene){
 const b=scene.board,r=23,divider=b.y+163,labelX=b.x+140,cardY=b.y+186,cardBottom=cardY+112,issues=[],add=(code,message)=>issues.push({code,message});
 if(b.target_x-r<b.x||b.target_x+r>b.x+b.width||b.target_y-r<b.y||b.target_y+r>b.y+b.height)add("TARGET_OUTSIDE_PANEL","Target marker is not fully inside the board.");
 if(Math.abs(b.target_y-divider)<r+4)add("TARGET_OVERLAPS_SEPARATOR","Target marker collides with divider reservation.");
 const l=b.target_x-r,rr=b.target_x+r,top=b.target_y-r,bot=b.target_y+r,tl=labelX-8,tr=b.x+b.width-24;
 if(rr>=tl&&l<=tr&&bot>=b.y+58&&top<=b.y+145)add("TARGET_OVERLAPS_HEADLINE","Target marker collides with headline reservation.");
 if(rr>=tl&&l<=tr&&bot>=cardY+18&&top<=cardBottom-12)add("TARGET_OVERLAPS_CARD_COPY","Target marker collides with instructional copy.");
 if(labelX>=b.x+b.width-100)add("BOARD_TEXT_NO_ROOM","Board text column is too narrow.");
 return issues;
}
export function assertSceneLayout(scene){const issues=inspectSceneLayout(scene);if(issues.length)throw new Error("Scene layout contract failed:\n"+issues.map(x=>x.code+": "+x.message).join("\n"));return {ok:true,issue_count:0};}