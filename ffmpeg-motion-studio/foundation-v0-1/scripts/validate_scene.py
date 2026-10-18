import json,sys
from pathlib import Path
from jsonschema import Draft202012Validator
if len(sys.argv)!=3: raise SystemExit("usage: validate_scene.py SCENE.json SCHEMA.json")
scene=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"));schema=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
Draft202012Validator.check_schema(schema)
errors=sorted(Draft202012Validator(schema).iter_errors(scene),key=lambda e:list(map(str,e.absolute_path)))
if errors:
 for err in errors: print("/"+"/".join(map(str,err.absolute_path))+": "+err.message)
 raise SystemExit(1)
print("SCHEMA_PASS scene="+scene["scene_id"]+" schema_id="+schema.get("$id","anonymous"))