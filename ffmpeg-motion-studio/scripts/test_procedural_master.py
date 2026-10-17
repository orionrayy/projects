#!/usr/bin/env python3
"""Fast acceptance-contract tests for the procedural video generator."""
import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import render_procedural_master as m

class MotionMasterTests(unittest.TestCase):
    def test_ids_and_titles(self):
        self.assertEqual([s["id"] for s in m.SCENES],list(range(1,28)))
        self.assertEqual(len({s["title"] for s in m.SCENES}),27)
    def test_exact_timeline(self):
        self.assertEqual(sum(m.DURATIONS),390)
        self.assertEqual(m.TOTAL*m.FPS,9360)
        self.assertEqual(m.DURATIONS,[15]*12+[14]*15)
    def test_renderer_has_all_motifs(self):
        self.assertTrue({s["motif"] for s in m.SCENES}.issubset(m.MOTIFS))
    def test_canonical_math(self):
        self.assertEqual(54000-5400,48600)
        self.assertIn("48.600",m.SCENES[1]["narration"])
        self.assertFalse(any("49.275" in str(s) for s in m.SCENES))
    def test_no_reference_images(self):
        self.assertEqual(m.REFERENCE_IMAGES_USED,0)
        self.assertEqual(m.EXTERNAL_VISUAL_ASSETS_USED,0)
    def test_substantive_narration(self):
        for scene in m.SCENES:
            self.assertGreaterEqual(len(scene["narration"].split()),20,scene["id"])
            self.assertLessEqual(len(scene["narration"].split()),45,scene["id"])
    def test_timeline_end(self):
        self.assertEqual(m.tc(0),"00:00:00,000")
        self.assertEqual(m.tc(390),"00:06:30,000")
    def test_deterministic_frame(self):
        a=m.frame(m.SCENES[12],2.0,m.DURATIONS[12]); b=m.frame(m.SCENES[12],2.0,m.DURATIONS[12])
        self.assertEqual(a.size,(1280,720)); self.assertEqual(a.tobytes(),b.tobytes())

if __name__=="__main__": unittest.main(verbosity=2)
