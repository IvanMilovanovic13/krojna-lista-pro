# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
os.chdir(r"C:\Users\Korisnik\krojna_lista_pro")

# Test 1: JSON loads correctly and has WALL_UPPER templates
from module_templates import get_templates
templates = get_templates()
wu_templates = {k: v for k, v in templates.items() if v.get('zone') == 'wall_upper'}
assert len(wu_templates) == 4, f"Treba 4 WALL_UPPER templata, ima: {len(wu_templates)}"
print(f"OK: {len(wu_templates)} WALL_UPPER templata: {list(wu_templates.keys())}")

# Test 2: layout_engine - available_space_in_zone za wall_upper
from layout_engine import available_space_in_zone, find_first_free_x, suggest_wall_upper_height, layout_audit

kitchen = {
    "wall": {"length_mm": 2400, "height_mm": 2600},
    "foot_height_mm": 100,
    "base_korpus_h_mm": 720,
    "vertical_gap_mm": 600,
    "worktop": {"thickness": 3.8, "width": 600},
    "manufacturing": {"profile": "EU_SRB"},
    "zones": {
        "base": {"height_mm": 720},
        "wall": {"height_mm": 720, "gap_from_base_mm": 1458},
        "tall": {"height_mm": 2450},
    },
    "modules": [
        {"id": 1, "template_id": "WALL_1DOOR", "zone": "wall",
         "label": "Gornji 1", "w_mm": 600, "h_mm": 720, "d_mm": 350, "x_mm": 5, "gap_after_mm": 0, "params": {}},
        {"id": 2, "template_id": "WALL_2DOOR", "zone": "wall",
         "label": "Gornji 2", "w_mm": 800, "h_mm": 720, "d_mm": 350, "x_mm": 605, "gap_after_mm": 0, "params": {}},
    ]
}

# Test 3: available_space_in_zone for wall_upper
free = available_space_in_zone(kitchen, "wall_upper")
assert free > 0, f"Treba biti slobodnog mesta za wall_upper, dobijeno: {free}"
print(f"OK: slobodan prostor za wall_upper = {free}mm")

# Test 4: find_first_free_x za wall_upper
fx = find_first_free_x(kitchen, "wall_upper", 600)
assert fx == 5, f"Treba da vrati X=5 (X prvog wall elementa), dobijeno: {fx}"
print(f"OK: find_first_free_x za wall_upper = {fx}")

# Test 5: suggest_wall_upper_height
free_h = suggest_wall_upper_height(kitchen, 1)
# wall_gap=1458, wall_h_elem=720, wall_upper_y_start=2178, available=2600-2178-5=417
expected_h = 2600 - (1458 + 720) - 5
assert free_h == expected_h, f"Treba {expected_h}mm slobodnog, dobijeno: {free_h}"
print(f"OK: suggest_wall_upper_height za wall id=1 = {free_h}mm (ocekivano {expected_h}mm)")

# Test 6: layout_audit - wall_upper iznad wall
kitchen_with_wu = dict(kitchen)
kitchen_with_wu["modules"] = list(kitchen["modules"]) + [
    {"id": 3, "template_id": "WALL_UPPER_1DOOR", "zone": "wall_upper",
     "label": "Gornji 2. red", "w_mm": 600, "h_mm": 400, "d_mm": 350, "x_mm": 5, "gap_after_mm": 0, "params": {}}
]
ok, msg = layout_audit(kitchen_with_wu)
assert ok, f"Audit treba proci za wall_upper iznad wall: {msg}"
print(f"OK: layout_audit proso za wall_upper iznad wall")

# Test 7: layout_audit - wall_upper bez wall ispod (treba da FAIL)
kitchen_no_wall = dict(kitchen)
kitchen_no_wall["modules"] = [
    {"id": 3, "template_id": "WALL_UPPER_1DOOR", "zone": "wall_upper",
     "label": "Gornji 2. red", "w_mm": 600, "h_mm": 400, "d_mm": 350, "x_mm": 5, "gap_after_mm": 0, "params": {}}
]
ok2, msg2 = layout_audit(kitchen_no_wall)
assert not ok2, f"Audit treba FAIL ako wall_upper nema wall ispod: {msg2}"
print(f"OK: layout_audit ispravno odbio wall_upper bez wall ispod: {msg2[:60]}")

# Test 8: cutlist generise wall_upper
from cutlist import build_cutlist_sections
kitchen_for_cl = dict(kitchen_with_wu)
kitchen_for_cl["materials"] = {
    "carcass_material": "Iverica", "carcass_thk": 18,
    "front_material": "MDF", "front_thk": 18,
    "back_thk": 8, "edge_abs_thk": 2
}
secs = build_cutlist_sections(kitchen_for_cl)
carcass = secs.get("carcass")
assert carcass is not None and not carcass.empty, "Carcass ne sme biti prazna"
wu_rows = carcass[carcass["TYPE"] == "WALL_UPPER"] if "TYPE" in carcass.columns else carcass[carcass["ID"] == 3]
assert len(wu_rows) > 0, f"Treba da ima WALL_UPPER redova u carcass, ima: {len(wu_rows)}"
print(f"OK: cutlist generise {len(wu_rows)} redova za WALL_UPPER element")

# Provjeri da wall_upper ima plafon
wu_parts = wu_rows["Deo"].tolist() if "Deo" in wu_rows.columns else []
assert "Plafon" in wu_parts, f"WALL_UPPER treba imati Plafon, ima: {wu_parts}"
print(f"OK: WALL_UPPER ima Plafon u krojnoj listi")

print("\nSVE PROVERE PROSLE!")

