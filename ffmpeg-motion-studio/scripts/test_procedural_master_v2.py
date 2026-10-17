#!/usr/bin/env python3
import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import render_procedural_master_v2 as m
class V2Tests(unittest.TestCase):
 def test_unique_scenes(self):
  self.assertEqual([s["id"] for s in m.SCENES],list(range(1,38)))
  self.assertEqual(len({s["title"] for s in m.SCENES}),37)
 def test_exact_runtime(self):
  self.assertEqual(m.DURATIONS,[11]*20+[10]*17); self.assertEqual(m.TOTAL,390); self.assertEqual(m.TOTAL*m.base.FPS,9360)
 def test_entry_to_exit_story_order(self):
  motifs=[s["motif"] for s in m.SCENES]
  self.assertEqual(motifs[0],"store_front"); self.assertEqual(motifs[1],"door_entry")
  for must in ("shelf_search","price_compare","weigh_produce","checkout_queue","barcode_scan","payment_approved","receipt_print","bag_items","exit_door","walk_outside","end_walk"):
   self.assertIn(must,motifs)
  self.assertLess(motifs.index("payment_approved"),motifs.index("receipt_print"))
  self.assertLess(motifs.index("receipt_print"),motifs.index("exit_door"))
  self.assertLess(motifs.index("exit_door"),motifs.index("walk_outside"))
 def test_three_scheduled_beats_every_scene(self):
  self.assertEqual(len(m.BEAT_GUIDE),37)
  for s,d in zip(m.SCENES,m.DURATIONS):
   beats=m.BEAT_GUIDE[str(s["id"])]
   self.assertEqual(len(beats),3)
   self.assertTrue(all(0<=b["at"]<d and b["action"] and b["fx"] for b in beats))
 def test_voiceover_word_budget_for_scene_pace(self):
  for scene in m.SCENES:
   n=len(scene["narration"].split())
   if scene["id"]==35:
    self.assertLessEqual(n,8,scene["id"])
   else:
    self.assertGreaterEqual(n,9,scene["id"])
    self.assertLessEqual(n,19,scene["id"])
 def test_no_reference_assets(self):
  self.assertEqual(m.REFERENCE_IMAGES_USED,0); self.assertEqual(m.EXTERNAL_VISUAL_ASSETS_USED,0)
 def test_procedural_audio_cues_exist(self):
  self.assertTrue({"scan_beep","receipt_printer","door_chime","footsteps","nfc_tap","bag_rustle"}.issubset(m.SFX_INFO))
  self.assertTrue(all(k in m.SFX_DURATION for s in m.SCENES for b in m.BEAT_GUIDE[str(s["id"])] for k in [b["sfx"]] if k))
  self.assertEqual(sum(1 for s in m.SCENES for b in m.BEAT_GUIDE[str(s["id"])] if b["sfx"]),105)
 def test_receipt_audit_voiceover_is_short(self):
  self.assertLessEqual(len(m.SCENES[34]["narration"].split()),8)
  self.assertIn("diaudit",m.SCENES[34]["narration"])
 def test_receipt_math(self):
  self.assertEqual(54000-5400,48600); self.assertIn("48.600",m.SCENES[22]["narration"])
 def test_caption_phrase_split(self):
  t="Satu dua tiga empat lima enam tujuh delapan sembilan sepuluh sebelas dua belas."
  chunks=m.caption_chunks(t); self.assertGreaterEqual(len(chunks),2)
  self.assertEqual(" ".join(" ".join(c) for c in chunks),t)
 def test_deterministic_render(self):
  sc=m.SCENES[13]; a=m.caption_frame(sc,2.0,m.DURATIONS[12]); b=m.caption_frame(sc,2.0,m.DURATIONS[12])
  self.assertEqual(a.size,(1280,720)); self.assertEqual(a.tobytes(),b.tobytes())
if __name__=="__main__": unittest.main(verbosity=2)
