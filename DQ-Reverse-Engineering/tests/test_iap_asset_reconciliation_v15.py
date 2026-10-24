from __future__ import annotations

import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from tools.reconcile_iap_asset_tables_v15 import audit

IAP_NAMES = [
"autoreveal","crystal","exp","gold","gold1","gold2","gold3","gold4","gold5","hires","hunter","luck","multi","multiboost","mythstone",
"package1","package10","package11","package12","package13","package14","package15","package16","package17","package18","package19","package2","package3","package4","package5","package6","package7","package8","package9",
"pet1","pet2","pet3","pet4","pet5","pet6","petboost","pickup","pstash","randomdog","randomfairy","randomimp","slot","slot1","slot2","slot3","slot4","slot5","slot6","special","special2","stash",
"vanity1","vanity2","vanity3","vanity4","vanity5","vanity6","vanity7","vanity8","vanity9","vanity10","vanity11","vanity12","vanity13","vanity14","vanity15","vanity16","vanity17","vanity18","vanity19","vanity20","vanity21","vanity22","vanity24","vanity25","vanity26","vanity27","vanity28","vanity29","vanity30","vanity31","vanity32","vanity33","vanity56","vanity57","vanity58","randomslime","poisonslime","vanity64","vanity65","vanity66","vanity67","vanity68","vanity69","vanity70","vanity71","vanity72","vanity73","vanity74","angelicslime","special3","demonicslime"
]
XML_ONLY={"angelicslime","demonicslime","poisonslime","vanity72","vanity73"}
DEX_ONLY={"package20","package21"}
VANITY_IDS=sorted(int(n[6:]) for n in IAP_NAMES if n.startswith("vanity") and n[6:].isdigit())


def write_table(root: Path, name: str, rows: list[dict[str, str | None]]) -> None:
    path=root/"Resources"/"XML"/name
    path.parent.mkdir(parents=True,exist_ok=True)
    element=ET.Element(Path(name).stem)
    ET.SubElement(element,"Schema")
    for row_id, values in enumerate(rows,1):
        row=ET.SubElement(element,"Row",id=str(row_id))
        for key,value in values.items():
            cell=ET.SubElement(row,key)
            cell.text=value
    ET.ElementTree(element).write(path,encoding="utf-8",xml_declaration=True)


def build_fixture(root: Path, patched: bool) -> None:
    write_table(root,"IAP.xml",[{"Name":name} for name in IAP_NAMES])
    vanity=[]
    for i in range(1,75):
        no_gold_source=(i in {1,2,32,33,56,57,58,64,65,66,67,68,69,70,71,72,73,74})
        gold=None if no_gold_source and not patched else ("500000" if i in VANITY_IDS else None)
        if patched and i==72: gold="500000"
        if patched and i==73: gold="250000"
        vanity.append({"Name":f"vanity-{i}","Gold":gold,"Price":None})
    write_table(root,"Vanity.xml",vanity)
    extras=[23,34,35,36,37,38,39]
    refs=sorted(set(VANITY_IDS)-{72,73})+extras
    if patched: refs += [72,73]
    write_table(root,"Shop.xml",[{"Tab1":None,"Tab2":None,"Tab3":str(ref)} for ref in refs])
    write_table(root,"Items.xml",[{"Name":"unchanged"}])
    write_table(root,"Dictionary.xml",[{"Name":"unchanged"}])


def build_matrix(path: Path) -> None:
    row_map={name:i+1 for i,name in enumerate(IAP_NAMES)}
    ids=IAP_NAMES+["package20","package21"]
    records=[]
    for name in ids:
        records.append({
            "legacy_id":name,
            "xml_entry":{"present":name in row_map,"row_id":row_map.get(name),"name":name if name in row_map else None},
            "dex_entry":{"present_as_static_literal":name not in XML_ONLY},
            "status":"STATIC-DIRECT",
            "test_status":{"runtime":"NOT-RUNTIME-VERIFIED"}
        })
    path.write_text(json.dumps({"records":records},indent=2),encoding="utf-8")


class IAPAssetReconciliationV15Tests(unittest.TestCase):
    def test_full_synthetic_tables_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source=root/"source"; patched=root/"patched"; matrix=root/"matrix.json"
            build_fixture(source,False); build_fixture(patched,True); build_matrix(matrix)
            report=audit(source,patched,matrix,None)
        self.assertEqual(report["status"],"PASS",report["discrepancies"])
        self.assertEqual(report["counts"]["iap_xml_rows"],107)
        self.assertEqual(report["counts"]["dex_static_sku_identifiers"],104)
        self.assertEqual(report["counts"]["shared_identifiers"],102)
        self.assertEqual(report["patch_summary"]["source_shop_rows"],51)
        self.assertEqual(report["patch_summary"]["patched_shop_rows"],53)
        self.assertEqual(report["patch_summary"]["patched_iap_vanity_missing_gold_or_shop_route"],[])
        self.assertTrue(report["patch_summary"]["iap_xml_unchanged"])

    def test_wrong_xml_row_id_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source=root/"source"; matrix=root/"matrix.json"
            build_fixture(source,False); build_matrix(matrix)
            data=json.loads(matrix.read_text()); data["records"][44]["xml_entry"]["row_id"]=46
            matrix.write_text(json.dumps(data),encoding="utf-8")
            report=audit(source,None,matrix,None)
        self.assertEqual(report["status"],"FAIL")
        self.assertTrue(any(d.get("field")=="xml_entry.row_id" for d in report["discrepancies"]))

    def test_non_allowlisted_table_change_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source=root/"source"; patched=root/"patched"; matrix=root/"matrix.json"
            build_fixture(source,False); build_fixture(patched,True); build_matrix(matrix)
            write_table(patched,"Items.xml",[{"Name":"unexpected change"}])
            report=audit(source,patched,matrix,None)
        self.assertEqual(report["status"],"FAIL")
        self.assertTrue(any(d.get("field")=="changed_table_allowlist" for d in report["discrepancies"]))

    def test_missing_earnability_route_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source=root/"source"; patched=root/"patched"; matrix=root/"matrix.json"
            build_fixture(source,False); build_fixture(patched,True); build_matrix(matrix)
            rows=[{"Name":f"vanity-{i}","Gold":None if i==72 else "100","Price":None} for i in range(1,75)]
            write_table(patched,"Vanity.xml",rows)
            report=audit(source,patched,matrix,None)
        self.assertEqual(report["status"],"FAIL")
        self.assertTrue(any(d.get("field")=="iap_vanity_earnability_routes" for d in report["discrepancies"]))


if __name__ == "__main__":
    unittest.main()
