import copy,json,unittest
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
SCENE=json.loads((ROOT/"scenes/scene-001.json").read_text(encoding="utf-8"));SCHEMA=json.loads((ROOT/"schemas/scene.schema.json").read_text(encoding="utf-8"))
class SceneContractTests(unittest.TestCase):
 def test_schema_is_valid(self): Draft202012Validator.check_schema(SCHEMA)
 def test_sample_is_valid(self): Draft202012Validator(SCHEMA).validate(SCENE)
 def test_unknown_field_rejected(self):
  bad=copy.deepcopy(SCENE);bad["handwavy_quality_score"]=100;self.assertTrue(list(Draft202012Validator(SCHEMA).iter_errors(bad)))
 def test_bad_color_rejected(self):
  bad=copy.deepcopy(SCENE);bad["palette"]["accent"]="orange";self.assertTrue(list(Draft202012Validator(SCHEMA).iter_errors(bad)))
 def test_nonpositive_rig_length_rejected(self):
  bad=copy.deepcopy(SCENE);bad["character"]["upper_arm_length"]=0;self.assertTrue(list(Draft202012Validator(SCHEMA).iter_errors(bad)))
if __name__=="__main__": unittest.main(verbosity=2)