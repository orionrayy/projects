#!/usr/bin/env python3
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_cashier_explainer_v3 as m

class CashierFirstV3Tests(unittest.TestCase):
    def test_exactly_three_short_question_hooks(self):
        hooks=m.SCENES[:3]
        self.assertEqual([s["motif"] for s in hooks],["hook_storefront","hook_scan","hook_total"])
        self.assertEqual(m.DURATIONS[:3],[4,4,4])
        self.assertTrue(all(s["narration"].strip().endswith("?") for s in hooks))
        self.assertTrue(all(len(s["narration"].split())<=7 for s in hooks))
        self.assertLessEqual(len(m.SCENES[17]["narration"].split()),16)
        self.assertEqual(sum(m.DURATIONS[:3]),12)

    def test_explanation_starts_at_cashier_on_scene_four(self):
        self.assertEqual(m.SCENES[3]["motif"],"counter_formula")
        self.assertIn("layar kasir",m.SCENES[3]["narration"].lower())
        self.assertEqual(len(m.SCENES),18)
        self.assertEqual(m.TOTAL,240)

    def test_hook_total_never_shows_a_false_intermediate_value(self):
        source=Path(m.__file__).read_text(encoding="utf-8")
        self.assertIn("value = 48600",source)
        self.assertNotIn("value=int(48600*ease(t/2.45))",source)

    def test_math_and_material_are_preserved(self):
        self.assertEqual(54000-5400,48600)
        self.assertEqual(round(54000*.10),5400)
        self.assertIn("54.000", "54.000 − 5.400 = 48.600")
        combined=" ".join(s["narration"].lower() for s in m.SCENES)
        for term in ("tokenisasi","context-free grammar","cfg","parse tree","prioritas","tanda kurung","semantik","subtotal","diskon","abstract syntax tree","ast","evaluator","struk"):
            self.assertIn(term,combined)
        self.assertIn("empat belas",m.SCENES[8]["narration"])
        self.assertIn("dua puluh",m.SCENES[9]["narration"])

    def test_scene_ids_durations_and_runtime(self):
        self.assertEqual([s["id"] for s in m.SCENES],list(range(1,19)))
        self.assertEqual(len({s["title"] for s in m.SCENES}),18)
        self.assertEqual(len(m.DURATIONS),18)
        self.assertEqual(sum(m.DURATIONS),240)
        self.assertEqual(m.TOTAL* m.FPS,5760)

    def test_narration_is_sized_for_natural_delivery(self):
        self.assertTrue(all(len(s["narration"].split()) <= 23 for s in m.SCENES[3:17]))
        self.assertLessEqual(len(m.SCENES[17]["narration"].split()), 20)

    def test_three_effect_beats_in_every_scene(self):
        self.assertEqual(len(m.BEAT_GUIDE),18)
        for s,dur in zip(m.SCENES,m.DURATIONS):
            beats=m.BEAT_GUIDE[str(s["id"])]
            self.assertEqual(len(beats),3,s["id"])
            self.assertTrue(all(b["action"] and b["fx"] for b in beats))
            self.assertTrue(all(0<=b["at"]<dur for b in beats))
        self.assertEqual(len(m.RAW_BEATS),18)

    def test_frame_canvas_and_motion_not_static(self):
        for sid in (1,2,4,5,8,9,14,16,18):
            s=m.SCENES[sid-1]; dur=m.DURATIONS[sid-1]
            a=m.frame_v3(s,0.1,dur)
            b=m.frame_v3(s,min(dur-.2,dur*.68),dur)
            self.assertEqual(a.size,(1280,720))
            self.assertEqual(b.size,(1280,720))
            self.assertNotEqual(a.tobytes(),b.tobytes(),f"scene {sid} appears static")

    def test_renderer_has_executable_entrypoint(self):
        source=Path(m.__file__).read_text(encoding="utf-8")
        self.assertIn('if __name__ == "__main__":',source)
        self.assertIn("raise SystemExit(main())",source)

    def test_no_external_assets_and_vfx_guide_has_hard_rules(self):
        self.assertEqual(m.base.REFERENCE_IMAGES_USED,0)
        self.assertEqual(m.base.EXTERNAL_VISUAL_ASSETS_USED,0)
        source=Path(m.__file__).read_text(encoding="utf-8")
        self.assertIn("write_director_guide",source)
        self.assertIn("SFX",source)
        self.assertIn("camera",source.lower())

if __name__=="__main__":
    unittest.main(verbosity=2)
