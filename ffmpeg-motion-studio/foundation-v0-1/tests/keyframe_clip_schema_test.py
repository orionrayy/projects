import json, unittest
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
class KeyframeClipSchemaTests(unittest.TestCase):
 def setUp(self):
  self.schema=json.loads((ROOT/"schemas"/"keyframe-clip.schema.json").read_text())
  self.clip=json.loads((ROOT/"reference-data"/"stickman-step"/"clip.json").read_text())
 def test_reference_matches_schema(self):
  errors=sorted(Draft202012Validator(self.schema).iter_errors(self.clip),key=lambda e:list(e.path))
  self.assertEqual([],["/"+"/".join(map(str,e.path))+": "+e.message for e in errors])
 def test_source_fps_is_unknown_separately_from_render_fps(self):
  self.assertIsNone(self.clip["source"]["source_frame_rate"])
  self.assertEqual(24,self.clip["render_settings"]["fps"])
  self.assertIn("Motion Studio render setting",self.clip["source"]["source_frame_rate_status"])
 def test_pose_landmarks_and_ids_are_stable(self):
  names=set(self.clip["keyframes"][0]["landmarks"])
  for i,k in enumerate(self.clip["keyframes"]):
   self.assertEqual(names,set(k["landmarks"]))
   self.assertEqual(i,k["source_frame_id"])
 def test_source_hash_has_sha256_shape(self):
  self.assertRegex(self.clip["source"]["sha256"],r"^[a-f0-9]{64}$")
if __name__=="__main__": unittest.main()