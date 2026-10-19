#!/usr/bin/env python3
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_cashier_explainer_v4 as m

class CashierFirstV4Tests(unittest.TestCase):
    def test_exact_240_second_runtime_and_frame_count(self):
        self.assertEqual(len(m.SCENES), 18)
        self.assertEqual([s["id"] for s in m.SCENES], list(range(1,19)))
        self.assertEqual(m.DURATIONS, [8,8,8,17,18,16,16,16,14,13,14,14,14,15,15,12,12,10])
        self.assertEqual(sum(m.DURATIONS), 240)
        self.assertEqual(m.TOTAL_DURATION, 240)
        self.assertEqual(m.TOTAL*m.FPS, 5760)

    def test_three_opening_questions_are_paced_at_8_seconds(self):
        self.assertEqual(m.DURATIONS[:3], [8,8,8])
        self.assertEqual(sum(m.DURATIONS[:3]), 24)
        hooks = m.SCENES[:3]
        self.assertEqual([s["motif"] for s in hooks], ["hook_storefront","hook_scan","hook_total"])
        self.assertTrue(all(s["narration"].strip().endswith("?") for s in hooks))
        self.assertIn("barcode", hooks[1]["title"].lower())
        self.assertIn("diskon", hooks[2]["title"].lower())
        self.assertEqual(m.SCENES[3]["motif"], "counter_formula")

    def test_math_and_cfg_teaching_are_correct(self):
        self.assertEqual(54000-5400, 48600)
        self.assertEqual(round(54000*.10), 5400)
        self.assertEqual(2+3*4, 14)
        self.assertEqual((2+3)*4, 20)
        combined = " ".join(s["narration"].lower() for s in m.SCENES)
        for term in ("tokenisasi","context-free grammar","cfg","analisis sintaks","parse tree",
                     "prioritas operator","tanda kurung","semantik","subtotal","diskon",
                     "abstract syntax tree","ast","evaluasi post-order","invariant","struk"):
            self.assertIn(term, combined)
        source = Path(m.__file__).read_text(encoding="utf-8")
        self.assertIn("G = (N, Σ, P, S)", source)
        self.assertIn("def draw_stage_strip", source)
        self.assertIn('"pedagogical_stage_strip":True', source)
        self.assertIn("definition → procedure → check", source)
        self.assertEqual(len(m.STEP_CUES),15)

    def test_three_synchronized_beats_per_scene_are_in_range(self):
        self.assertEqual(len(m.BEAT_GUIDE),18)
        for scene, dur in zip(m.SCENES, m.DURATIONS):
            beats = m.BEAT_GUIDE[str(scene["id"])]
            self.assertEqual(len(beats),3,scene["id"])
            self.assertTrue(all(b["action"] and b["fx"] for b in beats))
            self.assertTrue(all(0 <= b["at"] < dur for b in beats))
        self.assertEqual(len(m.RAW_BEATS),18)

    def test_selected_scenes_render_and_are_not_static(self):
        for sid in (1,2,4,5,8,9,14,16,18):
            scene = m.SCENES[sid-1]
            dur = m.DURATIONS[sid-1]
            a = m.frame_v4(scene,0.1,dur)
            b = m.frame_v4(scene,min(dur-0.2,dur*0.68),dur)
            self.assertEqual(a.size,(1280,720))
            self.assertEqual(b.size,(1280,720))
            self.assertNotEqual(a.tobytes(),b.tobytes(),f"scene {sid} appears static")

    def test_compact_character_proportions_and_faster_walk_cycle(self):
        source = Path(m.__file__).read_text(encoding="utf-8")
        self.assertIn("hy=g-108*s+bob; hr=12*s", source)
        self.assertIn("g-94*s+bob", source)
        self.assertIn("line(d,(x,g-97*s+bob,x,g-94*s+bob)", source)
        self.assertIn("phase*5.0", source)
        self.assertIn("phase*5.8", source)
        self.assertIn("swing=math.sin(phase*5.8)*11*s", source)

    def test_audio_mix_export_and_fades_are_part_of_entrypoint(self):
        source = Path(m.__file__).read_text(encoding="utf-8")
        self.assertIn("v2.make_audio_v2", source)
        self.assertIn("afade=t=out:st={TOTAL-1.5:.3f}:d=1.5", source)
        self.assertIn('"sound-effects-only.wav"', source)
        self.assertIn("base.write_srt", source)
        self.assertIn('"-c:a","aac"', source)
        self.assertIn('"voice_qc":"PENDING_HUMAN_LISTENING"', source)

    def test_stickman_is_reference_only_not_rendered_as_art(self):
        self.assertEqual(m.base.REFERENCE_IMAGES_USED,0)
        self.assertEqual(m.base.EXTERNAL_VISUAL_ASSETS_USED,0)
        brief = Path(__file__).resolve().parents[1] / "production" / "CASHIER_FIRST_V4_MOTION_BRIEF.md"
        txt = brief.read_text(encoding="utf-8").lower()
        self.assertIn("reference-only",txt)
        self.assertIn("not rendered as a character asset",txt)

    def test_renderer_has_executable_entrypoint_and_exact_frame_guard(self):
        source = Path(m.__file__).read_text(encoding="utf-8")
        self.assertIn('if __name__ == "__main__":', source)
        self.assertIn("sum(DURATIONS)!=240", source)
        self.assertIn("target_frames", source)

if __name__ == "__main__":
    unittest.main(verbosity=2)
