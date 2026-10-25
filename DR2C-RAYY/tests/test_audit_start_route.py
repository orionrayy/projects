from __future__ import annotations
import sys, tempfile, unittest, zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_start_route import audit_start_route

class StartRouteAuditTests(unittest.TestCase):
    def base_items(self):
        root = "GAME/assets/deathforth/"
        entries = {
            "boot.df": b': boot\n"GAME-MARKER" $anew\n"READY." print\n',
            "boot-end.df": b": boot-end 'menu-go ;\n",
            "events.df": b"defer main-event-do-select <noop>\nMAIN_EVENT_DO_SELECT ?( main-event-do-select );\n",
            "game-info.df": b': game-info "Info" print ;\n',
            "game-select.df": b': select-start "Start" print ;\n: select-boot \'main-event-do-select ;\n',
            "game-start.df": b": game-start-new 1 drop ;\n",
            "game-load.df": b": game-load 1 drop ;\n",
            "game-save.df": b": game-save 1 drop ;\n",
            "game-save-char.df": b": game-save-char 1 drop ;\n",
            "game-save-state.df": b": game-save-state 1 drop ;\n",
            "game-save-team.df": b": game-save-team 1 drop ;\n",
            "minimenu.df": b": minimenu 1 drop ;\n",
            "events/tutorial.df": b"cyoa-choice: tutorchat-1 ;\ncyoa-choice: tutorchat-2 ;\ncyoa-choice: tutorchat-3 ;\n",
        }
        return {root + name: content for name, content in entries.items()}

    def write_zip(self, path: Path, entries: dict[str, bytes]):
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for name, content in entries.items():
                z.writestr(name, content)

    def make_overlay(self, base: dict[str, bytes]):
        out = {}
        for path, content in base.items():
            logical = path.split("assets/deathforth/", 1)[1]
            if logical in ("boot.df", "game-select.df", "game-info.df", "game-start.df", "boot-end.df", "events/tutorial.df"):
                out["PATCH/overlay/assets/deathforth/" + logical] = content
        boot = base["GAME/assets/deathforth/boot.df"].replace(b'"READY."', b'"SIAP."')
        boot += b': id-name-localize ( name -- localized-name ) dup $= if drop "" exit then ;\n'
        out["PATCH/overlay/assets/deathforth/boot.df"] = boot
        out["PATCH/overlay/assets/deathforth/game-select.df"] = base["GAME/assets/deathforth/game-select.df"].replace(b'"Start"', b'"Mulai"')
        return out

    def test_display_localization_preserves_start_route_contract(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); base=root/"base.zip"; overlay=root/"overlay.zip"
            entries=self.base_items()
            self.write_zip(base,entries); self.write_zip(overlay,self.make_overlay(entries))
            result=audit_start_route(base,overlay)
            self.assertTrue(result["summary"]["overall_static_contracts_pass"])
            self.assertEqual(result["summary"]["route_files_static_fail"],0)
            self.assertTrue(result["boot_df_additive_localization_check"]["id_name_localize_helper_added"])

    def test_missing_start_handler_is_flagged(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); base=root/"base.zip"; overlay=root/"overlay.zip"
            entries=self.base_items(); self.write_zip(base,entries)
            layers=self.make_overlay(entries)
            p="PATCH/overlay/assets/deathforth/game-select.df"
            layers[p]=layers[p].replace(b"select-start",b"start-other")
            self.write_zip(overlay,layers)
            result=audit_start_route(base,overlay)
            self.assertFalse(result["summary"]["overall_static_contracts_pass"])
            route=next(x for x in result["route_files"] if x["path"].endswith("game-select.df"))
            self.assertFalse(route["required_tokens"]["select-start"])

    def test_route_code_skeleton_drift_is_flagged(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); base=root/"base.zip"; overlay=root/"overlay.zip"
            entries=self.base_items(); self.write_zip(base,entries)
            layers=self.make_overlay(entries)
            p="PATCH/overlay/assets/deathforth/game-select.df"
            layers[p]=layers[p].replace(b"'main-event-do-select",b"'other-handler")
            self.write_zip(overlay,layers)
            result=audit_start_route(base,overlay)
            self.assertFalse(result["summary"]["overall_static_contracts_pass"])
            route=next(x for x in result["route_files"] if x["path"].endswith("game-select.df"))
            self.assertFalse(route["display_code_skeleton_matches_base"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
