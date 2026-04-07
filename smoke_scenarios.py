# -*- coding: utf-8 -*-
from __future__ import annotations

"""
Minimalni smoke scenariji bez pokretanja UI servera.
Ne menja logiku, služi za brzu proveru da su 2D/3D renderi i state tokovi stabilni.
"""

from module_templates import get_templates
from ui_catalog_config import get_palette_tabs
from cutlist import _manufacturing_warnings, generate_cutlist, build_service_packet
from state_logic import _default_kitchen, _default_room, add_module_instance_local, update_module_local, state, reset_state
from state_logic import suggest_corner_neighbor_guidance
from visualization import render_element_preview
from layout_engine import layout_audit
from ui_room_helpers import ensure_room_walls, get_room_wall
from drawer_logic import redistribute_drawers_equal
import matplotlib
import pandas as pd
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from visualization import _render


def smoke_all_template_previews() -> tuple[int, int]:
    k = _default_kitchen()
    ok = 0
    err = 0
    for tid, t in get_templates().items():
        m = {
            "id": 1,
            "template_id": tid,
            "label": t.get("label", tid),
            "zone": t.get("zone", "base"),
            "x_mm": 0,
            "w_mm": int(t.get("w_mm", 600)),
            "h_mm": int(t.get("h_mm", 720)),
            "d_mm": int(t.get("d_mm", 560)),
            "params": {},
        }
        try:
            u2, u3 = render_element_preview(m, k)
            if not (isinstance(u2, str) and u2.startswith("data:image")):
                raise RuntimeError("2D preview invalid")
            if not (isinstance(u3, str) and u3.startswith("data:image")):
                raise RuntimeError("3D preview invalid")
            ok += 1
        except Exception:
            err += 1
    return ok, err


def smoke_palette_scope_and_panel_previews() -> tuple[bool, str]:
    tabs = get_palette_tabs("kitchen")
    active_tids: set[str] = set()
    for tab in tabs:
        for sg in tab.get("subgroups", []) or []:
            active_tids.update(str(t) for t in (sg.get("tids", []) or []))
    if "BASE_HOB" in active_tids:
        return False, "FAIL_base_hob_still_in_palette"

    k = _default_kitchen()
    for tid in ("FILLER_PANEL", "END_PANEL"):
        tmpl = get_templates().get(tid)
        if not tmpl:
            return False, f"FAIL_missing_template_{tid}"
        m = {
            "id": 1,
            "template_id": tid,
            "label": tmpl.get("label", tid),
            "zone": tmpl.get("zone", "base"),
            "x_mm": 0,
            "w_mm": int(tmpl.get("w_mm", 80 if tid == "FILLER_PANEL" else 600)),
            "h_mm": int(tmpl.get("h_mm", 720)),
            "d_mm": int(tmpl.get("d_mm", 18)),
            "params": {},
        }
        try:
            u2, u3 = render_element_preview(m, k)
            if not (isinstance(u2, str) and u2.startswith("data:image")):
                return False, f"FAIL_panel_2d_preview_{tid}"
            if not (isinstance(u3, str) and u3.startswith("data:image")):
                return False, f"FAIL_panel_3d_preview_{tid}"
        except Exception as ex:
            return False, f"FAIL_panel_preview_{tid}:{ex}"
    return True, "OK"


def smoke_mixed_appliance_previews() -> tuple[bool, str]:
    k = _default_kitchen()
    check_tids = (
        "BASE_COOKING_UNIT",
        "BASE_DISHWASHER",
        "TALL_FRIDGE",
        "TALL_FRIDGE_FREEZER",
        "TALL_OVEN",
        "TALL_OVEN_MICRO",
    )
    for tid in check_tids:
        tmpl = get_templates().get(tid)
        if not tmpl:
            return False, f"FAIL_missing_template_{tid}"
        m = {
            "id": 1,
            "template_id": tid,
            "label": tmpl.get("label", tid),
            "zone": tmpl.get("zone", "base"),
            "x_mm": 0,
            "w_mm": int(tmpl.get("w_mm", 600)),
            "h_mm": int(tmpl.get("h_mm", 720)),
            "d_mm": int(tmpl.get("d_mm", 560)),
            "params": {},
        }
        try:
            u2, u3 = render_element_preview(m, k)
            if not (isinstance(u2, str) and u2.startswith("data:image")):
                return False, f"FAIL_mixed_2d_preview_{tid}"
            if not (isinstance(u3, str) and u3.startswith("data:image")):
                return False, f"FAIL_mixed_3d_preview_{tid}"
        except Exception as ex:
            return False, f"FAIL_mixed_preview_{tid}:{ex}"
    return True, "OK"


def smoke_upper_appliance_previews() -> tuple[bool, str]:
    k = _default_kitchen()
    check_tids = ("WALL_MICRO", "WALL_HOOD")
    for tid in check_tids:
        tmpl = get_templates().get(tid)
        if not tmpl:
            return False, f"FAIL_missing_template_{tid}"
        m = {
            "id": 1,
            "template_id": tid,
            "label": tmpl.get("label", tid),
            "zone": tmpl.get("zone", "wall"),
            "x_mm": 0,
            "w_mm": int(tmpl.get("w_mm", 600)),
            "h_mm": int(tmpl.get("h_mm", 500)),
            "d_mm": int(tmpl.get("d_mm", 350)),
            "params": {},
        }
        try:
            u2, u3 = render_element_preview(m, k)
            if not (isinstance(u2, str) and u2.startswith("data:image")):
                return False, f"FAIL_upper_appliance_2d_{tid}"
            if not (isinstance(u3, str) and u3.startswith("data:image")):
                return False, f"FAIL_upper_appliance_3d_{tid}"
        except Exception as ex:
            return False, f"FAIL_upper_appliance_preview_{tid}:{ex}"
    return True, "OK"


def smoke_active_kitchen_palette_previews() -> tuple[bool, str]:
    tabs = get_palette_tabs("kitchen")
    active_tids: list[str] = []
    for tab in tabs:
        for sg in tab.get("subgroups", []) or []:
            for tid in (sg.get("tids", []) or []):
                active_tids.append(str(tid))

    k = _default_kitchen()
    for tid in active_tids:
        tmpl = get_templates().get(tid)
        if not tmpl:
            return False, f"FAIL_missing_active_template_{tid}"
        m = {
            "id": 1,
            "template_id": tid,
            "label": tmpl.get("label", tid),
            "zone": tmpl.get("zone", "base"),
            "x_mm": 0,
            "w_mm": int(tmpl.get("w_mm", 600)),
            "h_mm": int(tmpl.get("h_mm", 720)),
            "d_mm": int(tmpl.get("d_mm", 560)),
            "params": {},
        }
        try:
            u2, u3 = render_element_preview(m, k)
            if not (isinstance(u2, str) and u2.startswith("data:image")):
                return False, f"FAIL_active_palette_2d_{tid}"
            if not (isinstance(u3, str) and u3.startswith("data:image")):
                return False, f"FAIL_active_palette_3d_{tid}"
        except Exception as ex:
            return False, f"FAIL_active_palette_preview_{tid}:{ex}"
    return True, "OK"


def smoke_representative_render_cutlist_parity() -> tuple[bool, str]:
    """Representative parity checks: preview works and cutlist shape matches module intent."""
    k = _default_kitchen()
    cases = [
        ("BASE_1DOOR", {"zone": "base", "w_mm": 600, "h_mm": 720, "d_mm": 560}, {"carcass": True, "fronts": True, "backs": True}),
        ("BASE_2DOOR", {"zone": "base", "w_mm": 800, "h_mm": 720, "d_mm": 560}, {"carcass": True, "fronts": True, "backs": True}),
        ("BASE_OPEN", {"zone": "base", "w_mm": 600, "h_mm": 720, "d_mm": 560}, {"carcass": True, "fronts": False, "backs": True}),
        ("BASE_DRAWERS", {"zone": "base", "w_mm": 600, "h_mm": 720, "d_mm": 560, "params": {"n_drawers": 3}}, {"carcass": True, "fronts": True, "drawer_boxes": True}),
        ("BASE_DRAWERS_3", {"zone": "base", "w_mm": 600, "h_mm": 720, "d_mm": 560, "params": {"n_drawers": 3}}, {"carcass": True, "fronts": True, "drawer_boxes": True}),
        ("BASE_DOOR_DRAWER", {"zone": "base", "w_mm": 600, "h_mm": 720, "d_mm": 560, "params": {"n_drawers": 1, "drawer_heights": [130]}}, {"carcass": True, "fronts": True, "drawer_boxes": True}),
        ("BASE_NARROW", {"zone": "base", "w_mm": 300, "h_mm": 720, "d_mm": 560}, {"carcass": True, "fronts": True, "backs": True}),
        ("FILLER_PANEL", {"zone": "base", "w_mm": 80, "h_mm": 720, "d_mm": 18}, {"carcass": True, "fronts": False, "backs": False}),
        ("END_PANEL", {"zone": "base", "w_mm": 600, "h_mm": 720, "d_mm": 18}, {"carcass": True, "fronts": False, "backs": False}),
        ("BASE_CORNER", {"zone": "base", "w_mm": 900, "h_mm": 720, "d_mm": 560}, {"carcass": True, "fronts": True, "backs": True}),
        ("BASE_DISHWASHER", {"zone": "base", "w_mm": 600, "h_mm": 720, "d_mm": 560}, {"fronts": True}),
        ("BASE_DISHWASHER_FREESTANDING", {"zone": "base", "w_mm": 600, "h_mm": 850, "d_mm": 600}, {"carcass": False, "fronts": False, "backs": False}),
        ("BASE_COOKING_UNIT", {"zone": "base", "w_mm": 600, "h_mm": 720, "d_mm": 560, "params": {"has_drawer": True}}, {"carcass": True, "fronts": True, "drawer_boxes": True}),
        ("BASE_OVEN_HOB_FREESTANDING", {"zone": "base", "w_mm": 600, "h_mm": 850, "d_mm": 600}, {"carcass": False, "fronts": False, "backs": False}),
        ("SINK_BASE", {"zone": "base", "w_mm": 800, "h_mm": 720, "d_mm": 560}, {"carcass": True, "fronts": True}),
        ("WALL_2DOOR", {"zone": "wall", "w_mm": 800, "h_mm": 720, "d_mm": 320}, {"carcass": True, "fronts": True, "backs": True}),
        ("WALL_GLASS", {"zone": "wall", "w_mm": 600, "h_mm": 720, "d_mm": 320}, {"carcass": True, "fronts": True, "backs": True}),
        ("WALL_LIFTUP", {"zone": "wall", "w_mm": 600, "h_mm": 360, "d_mm": 320}, {"carcass": True, "fronts": True, "backs": True}),
        ("WALL_OPEN", {"zone": "wall", "w_mm": 600, "h_mm": 720, "d_mm": 320}, {"carcass": True, "fronts": False, "backs": True}),
        ("WALL_CORNER", {"zone": "wall", "w_mm": 900, "h_mm": 720, "d_mm": 320}, {"carcass": True, "fronts": True, "backs": True}),
        ("WALL_NARROW", {"zone": "wall", "w_mm": 300, "h_mm": 720, "d_mm": 320}, {"carcass": True, "fronts": True, "backs": True}),
        ("WALL_HOOD", {"zone": "wall", "w_mm": 600, "h_mm": 500, "d_mm": 320}, {"carcass": True, "fronts": False}),
        ("WALL_MICRO", {"zone": "wall", "w_mm": 600, "h_mm": 500, "d_mm": 320}, {"carcass": True}),
        ("TALL_FRIDGE", {"zone": "tall", "w_mm": 600, "h_mm": 2100, "d_mm": 560}, {"carcass": True, "fronts": True, "backs": True}),
        ("TALL_FRIDGE_FREESTANDING", {"zone": "tall", "w_mm": 600, "h_mm": 2000, "d_mm": 650}, {"carcass": False, "fronts": False, "backs": False}),
        ("TALL_FRIDGE_FREEZER", {"zone": "tall", "w_mm": 600, "h_mm": 2100, "d_mm": 560}, {"carcass": True, "fronts": True, "backs": True}),
        ("TALL_PANTRY", {"zone": "tall", "w_mm": 600, "h_mm": 2100, "d_mm": 560}, {"carcass": True, "fronts": True, "backs": True}),
        ("TALL_DOORS", {"zone": "tall", "w_mm": 600, "h_mm": 2100, "d_mm": 560}, {"carcass": True, "fronts": True, "backs": True}),
        ("TALL_GLASS", {"zone": "tall", "w_mm": 600, "h_mm": 2100, "d_mm": 560}, {"carcass": True, "fronts": True, "backs": True}),
        ("TALL_OPEN", {"zone": "tall", "w_mm": 600, "h_mm": 2100, "d_mm": 560}, {"carcass": True, "fronts": False, "backs": True}),
        ("TALL_OVEN", {"zone": "tall", "w_mm": 600, "h_mm": 2100, "d_mm": 560}, {"carcass": True, "fronts": True, "backs": True}),
        ("TALL_OVEN_MICRO", {"zone": "tall", "w_mm": 600, "h_mm": 2100, "d_mm": 560}, {"carcass": True, "fronts": True, "backs": True}),
        ("WALL_UPPER_1DOOR", {"zone": "wall_upper", "w_mm": 600, "h_mm": 360, "d_mm": 300}, {"carcass": True, "fronts": True}),
        ("WALL_UPPER_2DOOR", {"zone": "wall_upper", "w_mm": 800, "h_mm": 360, "d_mm": 300}, {"carcass": True, "fronts": True, "backs": True}),
        ("WALL_UPPER_OPEN", {"zone": "wall_upper", "w_mm": 600, "h_mm": 360, "d_mm": 300}, {"carcass": True, "fronts": False, "backs": True}),
        ("TALL_TOP_DOORS", {"zone": "tall_top", "w_mm": 600, "h_mm": 400, "d_mm": 560}, {"carcass": True, "fronts": True}),
        ("TALL_TOP_OPEN", {"zone": "tall_top", "w_mm": 600, "h_mm": 400, "d_mm": 560}, {"carcass": True, "fronts": False, "backs": True}),
    ]

    for idx, (tid, dims, expected) in enumerate(cases, start=1):
        m = {
            "id": idx,
            "template_id": tid,
            "label": tid,
            "wall_key": "A",
            "x_mm": 0,
            "gap_after_mm": 0,
            "params": dims.get("params", {}),
            **{k: v for k, v in dims.items() if k != "params"},
        }
        try:
            u2, u3 = render_element_preview(m, k)
            if not (isinstance(u2, str) and u2.startswith("data:image")):
                return False, f"FAIL_parity_preview_2d_{tid}"
            if not (isinstance(u3, str) and u3.startswith("data:image")):
                return False, f"FAIL_parity_preview_3d_{tid}"
        except Exception as ex:
            return False, f"FAIL_parity_preview_{tid}:{ex}"

        k_case = _default_kitchen()
        k_case["modules"] = [m]
        try:
            sections = generate_cutlist(k_case)
        except Exception as ex:
            return False, f"FAIL_parity_cutlist_{tid}:{ex}"

        for sec_name, should_exist in expected.items():
            df = sections.get(sec_name)
            exists = df is not None and not df.empty
            if bool(should_exist) != exists:
                return False, f"FAIL_parity_{tid}_{sec_name}_{'missing' if should_exist else 'unexpected'}"

    return True, "OK"


def smoke_front_and_drawer_quantities() -> tuple[bool, str]:
    """Stricter quantity parity for selected mixed modules."""
    cases = [
        ("BASE_DRAWERS_3", {"zone": "base", "w_mm": 600, "h_mm": 720, "d_mm": 560, "params": {"n_drawers": 3}}, {"fronts_qty": 3, "drawer_box_count": 3}),
        ("BASE_DOOR_DRAWER", {"zone": "base", "w_mm": 600, "h_mm": 720, "d_mm": 560, "params": {"n_drawers": 1, "drawer_heights": [130]}}, {"fronts_qty": 2, "drawer_box_count": 1}),
        ("BASE_2DOOR", {"zone": "base", "w_mm": 800, "h_mm": 720, "d_mm": 560}, {"fronts_qty": 2}),
        ("WALL_2DOOR", {"zone": "wall", "w_mm": 800, "h_mm": 720, "d_mm": 320}, {"fronts_qty": 2}),
        ("TALL_FRIDGE_FREEZER", {"zone": "tall", "w_mm": 600, "h_mm": 2100, "d_mm": 560}, {"fronts_qty": 2}),
        ("TALL_OVEN_MICRO", {"zone": "tall", "w_mm": 600, "h_mm": 2100, "d_mm": 560}, {"fronts_qty": 1}),
        ("BASE_COOKING_UNIT", {"zone": "base", "w_mm": 600, "h_mm": 720, "d_mm": 560, "params": {"has_drawer": True}}, {"fronts_qty": 1, "drawer_box_count": 1}),
        ("BASE_DISHWASHER", {"zone": "base", "w_mm": 600, "h_mm": 720, "d_mm": 560}, {"fronts_qty": 1}),
    ]
    for idx, (tid, dims, expected) in enumerate(cases, start=1):
        k_case = _default_kitchen()
        k_case["modules"] = [{
            "id": idx,
            "template_id": tid,
            "label": tid,
            "wall_key": "A",
            "x_mm": 0,
            "gap_after_mm": 0,
            "params": dims.get("params", {}),
            **{k: v for k, v in dims.items() if k != "params"},
        }]
        try:
            sections = generate_cutlist(k_case)
        except Exception as ex:
            return False, f"FAIL_qty_cutlist_{tid}:{ex}"

        if "fronts_qty" in expected:
            df_fronts = sections.get("fronts")
            front_qty = 0 if df_fronts is None or df_fronts.empty else int(df_fronts["Kol."].fillna(0).sum())
            if front_qty != int(expected["fronts_qty"]):
                return False, f"FAIL_qty_fronts_{tid}_{front_qty}_expected_{expected['fronts_qty']}"

        if "drawer_box_count" in expected:
            df_drawers = sections.get("drawer_boxes")
            if df_drawers is None or df_drawers.empty:
                return False, f"FAIL_qty_drawer_boxes_missing_{tid}"
            box_count = int(df_drawers["Deo"].astype(str).str.contains("Dno sanduka", case=False, na=False).sum())
            if box_count != int(expected["drawer_box_count"]):
                return False, f"FAIL_qty_drawer_boxes_{tid}_{box_count}_expected_{expected['drawer_box_count']}"

    return True, "OK"


def smoke_special_front_types() -> tuple[bool, str]:
    """Ensure special modules keep distinctive front semantics, not generic fallback names."""
    def _norm_name(text: str) -> str:
        return " ".join(str(text).replace("—", " ").replace("-", " ").split()).casefold()

    cases = [
        ("WALL_GLASS", {"zone": "wall", "w_mm": 600, "h_mm": 720, "d_mm": 320}, [(["staklena", "vrata"], 2)]),
        ("WALL_LIFTUP", {"zone": "wall", "w_mm": 600, "h_mm": 360, "d_mm": 320}, [(["vrata"], 2)]),
        ("TALL_FRIDGE", {"zone": "tall", "w_mm": 600, "h_mm": 2100, "d_mm": 560}, [(["front", "integrisanog", "frižidera"], 1)]),
        ("TALL_FRIDGE_FREEZER", {"zone": "tall", "w_mm": 600, "h_mm": 2100, "d_mm": 560}, [(["gornji", "front", "frižidera"], 1), (["donji", "front", "zamrzivača"], 1)]),
        ("BASE_DISHWASHER", {"zone": "base", "w_mm": 600, "h_mm": 720, "d_mm": 560}, [(["front", "sudove"], 1)]),
        ("BASE_COOKING_UNIT", {"zone": "base", "w_mm": 600, "h_mm": 720, "d_mm": 560, "params": {"has_drawer": True}}, [(["front", "fioke"], 1)]),
        ("TALL_OVEN", {"zone": "tall", "w_mm": 600, "h_mm": 2100, "d_mm": 560}, [(["donji", "servisni", "front"], 1)]),
        ("TALL_OVEN_MICRO", {"zone": "tall", "w_mm": 600, "h_mm": 2100, "d_mm": 560}, [(["donji", "servisni", "front"], 1)]),
    ]
    for idx, (tid, dims, expected_rows) in enumerate(cases, start=1):
        k_case = _default_kitchen()
        k_case["modules"] = [{
            "id": idx,
            "template_id": tid,
            "label": tid,
            "wall_key": "A",
            "x_mm": 0,
            "gap_after_mm": 0,
            "params": dims.get("params", {}),
            **{k: v for k, v in dims.items() if k != "params"},
        }]
        try:
            df_fronts = generate_cutlist(k_case).get("fronts")
        except Exception as ex:
            return False, f"FAIL_special_fronts_cutlist_{tid}:{ex}"
        if df_fronts is None or df_fronts.empty:
            return False, f"FAIL_special_fronts_missing_{tid}"
        actual_rows = [(_norm_name(r.get("Deo", "")), int(r.get("Kol.", 0))) for _, r in df_fronts.iterrows()]
        if len(actual_rows) != len(expected_rows):
            return False, f"FAIL_special_fronts_count_{tid}_{actual_rows!r}"
        for (actual_name, actual_qty), (expected_tokens, expected_qty) in zip(actual_rows, expected_rows):
            if actual_qty != expected_qty:
                return False, f"FAIL_special_fronts_qty_{tid}_{actual_rows!r}"
            if not all(_norm_name(token) in actual_name for token in expected_tokens):
                return False, f"FAIL_special_fronts_name_{tid}_{actual_rows!r}"
    return True, "OK"


def smoke_add_edit_layout() -> tuple[bool, str]:
    reset_state()
    state.kitchen = _default_kitchen()
    state.room = _default_room()
    _ = add_module_instance_local(
        template_id="BASE_1DOOR",
        zone="base",
        x_mm=0,
        w_mm=600,
        h_mm=720,
        d_mm=560,
        gap_after_mm=0,
        label="Donji (1 vrata)",
        params={},
    )
    _ = add_module_instance_local(
        template_id="WALL_2DOOR",
        zone="wall",
        x_mm=0,
        w_mm=800,
        h_mm=720,
        d_mm=350,
        gap_after_mm=0,
        label="Gornji (2 vrata)",
        params={},
    )
    return layout_audit(state.kitchen)


def smoke_drawer_flow() -> tuple[bool, str]:
    reset_state()
    state.kitchen = _default_kitchen()
    state.room = _default_room()

    mod = add_module_instance_local(
        template_id="BASE_DRAWERS_3",
        zone="base",
        x_mm=0,
        w_mm=600,
        h_mm=720,
        d_mm=560,
        gap_after_mm=0,
        label="Donji (fioke)",
        params={
            "n_drawers": 4,
            "drawer_heights": [170, 170, 170, 170],
            "drawers": [
                {"height": 170, "locked": False},
                {"height": 170, "locked": False},
                {"height": 170, "locked": False},
                {"height": 170, "locked": False},
            ],
        },
    )

    p = mod.get("params", {}) or {}
    if int(p.get("n_drawers", 0) or 0) != 4:
        return False, f"FAIL_drawer_count_not_preserved:{p.get('n_drawers')}"
    dh = list(p.get("drawer_heights", []) or [])
    if dh != [170, 170, 170, 170]:
        return False, f"FAIL_drawer_heights_not_preserved:{dh}"
    dr = list(p.get("drawers", []) or [])
    if len(dr) != 4:
        return False, f"FAIL_drawers_model_len:{len(dr)}"

    redistributed = redistribute_drawers_equal(
        [170, 170, 170, 170],
        changed_idx=0,
        requested_height=185,
        locks={},
        total_target=680,
    )
    if redistributed != [185, 165, 165, 165]:
        return False, f"FAIL_drawer_redistribute_equal:{redistributed}"

    redistributed_locked = redistribute_drawers_equal(
        [185, 165, 165, 165],
        changed_idx=1,
        requested_height=175,
        locks={0: True},
        total_target=680,
    )
    if redistributed_locked != [185, 175, 160, 160]:
        return False, f"FAIL_drawer_redistribute_locked:{redistributed_locked}"

    return True, "OK"


def smoke_room_openings_walls() -> tuple[bool, str]:
    room = _default_room()
    ensure_room_walls(room)

    wa = get_room_wall(room, "A")
    wb = get_room_wall(room, "B")
    wc = get_room_wall(room, "C")

    wa.setdefault("openings", []).append({"type": "prozor", "wall": "A", "x_mm": 300, "y_mm": 900, "width_mm": 1200, "height_mm": 1000})
    wb.setdefault("openings", []).append({"type": "vrata", "wall": "B", "x_mm": 100, "y_mm": 0, "width_mm": 900, "height_mm": 2100})
    wc.setdefault("fixtures", []).append({"type": "voda", "wall": "C", "x_mm": 600, "y_mm": 450})

    checks = [
        (len(wa.get("openings", [])) == 1, "A openings"),
        (len(wb.get("openings", [])) == 1, "B openings"),
        (len(wc.get("fixtures", [])) == 1, "C fixtures"),
        (wa.get("openings", [{}])[0].get("wall") == "A", "A wall tag"),
        (wb.get("openings", [{}])[0].get("wall") == "B", "B wall tag"),
        (wc.get("fixtures", [{}])[0].get("wall") == "C", "C wall tag"),
    ]

    failed = [name for ok, name in checks if not ok]
    if failed:
        return False, f"FAIL: {', '.join(failed)}"
    return True, "OK"


def smoke_grid_modes() -> tuple[bool, str]:
    """Render stability for grid step edge-cases (1/5/10 mm)."""
    k = _default_kitchen()
    k["modules"] = [
        {
            "id": 1, "template_id": "BASE_1DOOR", "label": "Donji (1 vrata)",
            "zone": "base", "x_mm": 0, "w_mm": 600, "h_mm": 720, "d_mm": 560, "params": {},
        },
        {
            "id": 2, "template_id": "BASE_1DOOR", "label": "Donji (1 vrata)",
            "zone": "base", "x_mm": 600, "w_mm": 600, "h_mm": 720, "d_mm": 560, "params": {},
        },
    ]
    try:
        for g in (1, 5, 10):
            fig = plt.figure(figsize=(12, 5))
            ax = fig.add_subplot(111)
            _render(
                ax=ax, kitchen=k, view_mode="Tehnički",
                show_grid=True, grid_mm=g, show_bounds=True,
                kickboard=True, ceiling_filler=False,
            )
            fig.tight_layout(pad=0.2)
            plt.close(fig)
        return True, "OK"
    except Exception as ex:
        return False, f"FAIL: {ex}"


def smoke_bounds_toggle_modes() -> tuple[bool, str]:
    """Zone overlay toggle must affect both catalog and technical 2D views."""
    k = _default_kitchen()
    k["max_element_height"] = 2400
    k["modules"] = [
        {
            "id": 1, "template_id": "BASE_1DOOR", "label": "Donji (1 vrata)",
            "zone": "base", "x_mm": 0, "w_mm": 600, "h_mm": 720, "d_mm": 560, "params": {},
        },
        {
            "id": 2, "template_id": "WALL_1DOOR", "label": "Gornji (1 vrata)",
            "zone": "wall", "x_mm": 0, "w_mm": 600, "h_mm": 720, "d_mm": 320, "params": {},
        },
    ]
    try:
        results: dict[str, tuple[int, int]] = {}
        for view in ("Katalog", "Tehnički"):
            for bounds in (False, True):
                fig = plt.figure(figsize=(12, 5))
                ax = fig.add_subplot(111)
                _render(
                    ax=ax, kitchen=k, view_mode=view,
                    show_grid=True, grid_mm=5, show_bounds=bounds,
                    kickboard=True, ceiling_filler=False,
                )
                results[f"{view}:{bounds}"] = (len(ax.lines), len(ax.patches))
                plt.close(fig)

        if results["Katalog:True"][0] <= results["Katalog:False"][0]:
            return False, "FAIL_catalog_bounds_toggle_no_effect"
        if results["Tehnički:True"][0] <= results["Tehnički:False"][0]:
            return False, "FAIL_technical_bounds_toggle_no_effect"
        return True, "OK"
    except Exception as ex:
        return False, f"FAIL: {ex}"


def smoke_blocking_validations() -> tuple[bool, str]:
    reset_state()
    state.kitchen = _default_kitchen()
    state.room = _default_room()

    checks = []

    try:
        add_module_instance_local(
            template_id="BASE_1DOOR",
            zone="base",
            x_mm=0,
            w_mm=600,
            h_mm=720,
            d_mm=400,
            label="Los donji",
            params={},
        )
        checks.append("FAIL_base_depth")
    except Exception:
        pass

    try:
        add_module_instance_local(
            template_id="BASE_1DOOR",
            zone="base",
            x_mm=5,
            w_mm=600,
            h_mm=720,
            d_mm=560,
            label="Levi zid - losa sarka",
            params={"handle_side": "right"},
        )
        checks.append("FAIL_side_wall_opening")
    except Exception:
        pass

    try:
        add_module_instance_local(
            template_id="WALL_UPPER_1DOOR",
            zone="wall_upper",
            x_mm=0,
            w_mm=600,
            h_mm=360,
            d_mm=300,
            label="Gornji drugi red",
            params={},
        )
        checks.append("FAIL_wall_upper_support")
    except Exception:
        pass

    try:
        add_module_instance_local(
            template_id="TALL_TOP_DOORS",
            zone="tall_top",
            x_mm=0,
            w_mm=600,
            h_mm=400,
            d_mm=560,
            label="Top dopuna",
            params={},
        )
        checks.append("FAIL_tall_top_support")
    except Exception:
        pass

    try:
        _wall_ok = add_module_instance_local(
            template_id="WALL_1DOOR",
            zone="wall",
            x_mm=0,
            w_mm=600,
            h_mm=720,
            d_mm=320,
            label="Gornji 1 vrata",
            params={},
        )
        add_module_instance_local(
            template_id="WALL_UPPER_1DOOR",
            zone="wall_upper",
            x_mm=int(_wall_ok.get("x_mm", 0)),
            w_mm=600,
            h_mm=360,
            d_mm=300,
            label="Gornji drugi red",
            params={},
        )
    except Exception as ex:
        checks.append(f"FAIL_valid_wall_upper:{ex}")

    try:
        add_module_instance_local(
            template_id="WALL_1DOOR",
            zone="wall",
            x_mm=700,
            w_mm=600,
            h_mm=720,
            d_mm=320,
            label="Gornji 1 vrata B",
            params={},
        )
        add_module_instance_local(
            template_id="WALL_UPPER_2DOOR",
            zone="wall_upper",
            x_mm=0,
            w_mm=800,
            h_mm=360,
            d_mm=300,
            label="Predug drugi red",
            params={},
        )
        checks.append("FAIL_wall_upper_full_support")
    except Exception:
        pass

    try:
        add_module_instance_local(
            template_id="TALL_OVEN",
            zone="tall",
            x_mm=0,
            w_mm=600,
            h_mm=2100,
            d_mm=520,
            label="Visoki rerna",
            params={},
        )
        checks.append("FAIL_tall_oven_depth")
    except Exception:
        pass

    try:
        add_module_instance_local(
            template_id="BASE_CORNER",
            zone="base",
            x_mm=0,
            w_mm=700,
            h_mm=720,
            d_mm=560,
            label="Los ugaoni",
            params={},
        )
        checks.append("FAIL_corner_width")
    except Exception:
        pass

    try:
        add_module_instance_local(
            template_id="WALL_HOOD",
            zone="wall",
            x_mm=700,
            w_mm=500,
            h_mm=400,
            d_mm=280,
            label="Losa napa",
            params={},
        )
        checks.append("FAIL_wall_hood_size")
    except Exception:
        pass

    try:
        add_module_instance_local(
            template_id="TALL_FRIDGE_FREESTANDING",
            zone="tall",
            x_mm=1400,
            w_mm=600,
            h_mm=2000,
            d_mm=550,
            label="Los samostojeci frizider",
            params={},
        )
        checks.append("FAIL_freestanding_fridge_depth")
    except Exception:
        pass

    reset_state()
    state.kitchen = _default_kitchen()
    state.room = _default_room()
    try:
        add_module_instance_local(
            template_id="TALL_DOORS",
            zone="tall",
            x_mm=0,
            w_mm=600,
            h_mm=2100,
            d_mm=560,
            label="Visoki 1",
            params={},
        )
        add_module_instance_local(
            template_id="TALL_DOORS",
            zone="tall",
            x_mm=700,
            w_mm=600,
            h_mm=2100,
            d_mm=560,
            label="Visoki 2",
            params={},
        )
        add_module_instance_local(
            template_id="TALL_TOP_DOORS",
            zone="tall_top",
            x_mm=0,
            w_mm=800,
            h_mm=360,
            d_mm=560,
            label="Siroka top dopuna",
            params={},
        )
        checks.append("FAIL_tall_top_full_support")
    except Exception:
        pass

    if checks:
        return False, ", ".join(checks)
    return True, "OK"


def smoke_update_validations() -> tuple[bool, str]:
    reset_state()
    state.kitchen = _default_kitchen()
    state.room = _default_room()

    checks = []

    base = add_module_instance_local(
        template_id="BASE_1DOOR",
        zone="base",
        x_mm=0,
        w_mm=600,
        h_mm=720,
        d_mm=560,
        label="Donji 1 vrata",
        params={},
    )

    try:
        update_module_local(
            int(base.get("id", 0)),
            x_mm=0,
            w_mm=600,
            h_mm=720,
            d_mm=400,
            gap_after_mm=0,
            label="Donji 1 vrata",
            params={},
        )
        checks.append("FAIL_update_base_depth")
    except Exception:
        pass

    combo = add_module_instance_local(
        template_id="BASE_DOOR_DRAWER",
        zone="base",
        x_mm=700,
        w_mm=600,
        h_mm=720,
        d_mm=560,
        label="Vrata + fioka",
        params={"door_height": 420, "drawer_heights": [244], "n_drawers": 1},
    )

    try:
        update_module_local(
            int(combo.get("id", 0)),
            x_mm=700,
            w_mm=600,
            h_mm=720,
            d_mm=560,
            gap_after_mm=0,
            label="Vrata + fioka",
            params={"door_height": 650, "drawer_heights": [50], "n_drawers": 1},
        )
        checks.append("FAIL_update_door_drawer_fronts")
    except Exception:
        pass

    if checks:
        return False, ", ".join(checks)
    return True, "OK"


def smoke_layout_support_audit() -> tuple[bool, str]:
    k = _default_kitchen()
    k["modules"] = [
        {
            "id": 1, "template_id": "WALL_1DOOR", "label": "Gornji",
            "zone": "wall", "wall_key": "A", "x_mm": 5, "w_mm": 600, "h_mm": 720, "d_mm": 320, "params": {},
        },
        {
            "id": 2, "template_id": "WALL_UPPER_2DOOR", "label": "Drugi red",
            "zone": "wall_upper", "wall_key": "A", "x_mm": 5, "w_mm": 800, "h_mm": 360, "d_mm": 300, "params": {},
        },
    ]
    ok, msg = layout_audit(k)
    if ok:
        return False, "FAIL_expected_layout_support_rejection"
    if "WALL_UPPER" not in msg:
        return False, f"FAIL_unexpected_layout_msg:{msg}"
    return True, "OK"


def smoke_room_constraints() -> tuple[bool, str]:
    reset_state()
    state.kitchen = _default_kitchen()
    state.room = _default_room()

    wall_a = next((w for w in (state.room.get("walls", []) or []) if str(w.get("key", "")).upper() == "A"), None)
    if wall_a is None:
        return False, "FAIL_no_wall_A"

    _door = {"type": "vrata", "wall": "A", "x_mm": 100, "y_mm": 0, "width_mm": 900, "height_mm": 2100}
    wall_a.setdefault("openings", []).append(_door)
    state.room.setdefault("openings", []).append(dict(_door))
    wall_a.setdefault("fixtures", []).append({
        "type": "voda", "wall": "A", "x_mm": 1300, "y_mm": 450,
    })

    relocated = add_module_instance_local(
        template_id="BASE_1DOOR",
        zone="base",
        x_mm=150,
        w_mm=600,
        h_mm=720,
        d_mm=560,
        label="Na vratima",
        params={},
        room=state.room,
        wall_key="A",
    )
    rx = int(relocated.get("x_mm", 0))
    if 100 <= rx < 1000:
        return False, "FAIL_door_constraint_relocation"

    reset_state()
    state.kitchen = _default_kitchen()
    state.room = _default_room()
    wall_a = next((w for w in (state.room.get("walls", []) or []) if str(w.get("key", "")).upper() == "A"), None)
    if wall_a is None:
        return False, "FAIL_no_wall_A_after_reset"
    _door2 = {"type": "vrata", "wall": "A", "x_mm": 100, "y_mm": 0, "width_mm": 900, "height_mm": 2100}
    wall_a.setdefault("openings", []).append(_door2)
    state.room.setdefault("openings", []).append(dict(_door2))
    wall_a.setdefault("fixtures", []).append({
        "type": "voda", "wall": "A", "x_mm": 1300, "y_mm": 450,
    })

    mod = add_module_instance_local(
        template_id="BASE_1DOOR",
        zone="base",
        x_mm=1300,
        w_mm=600,
        h_mm=720,
        d_mm=560,
        label="Kod vode",
        params={},
        room=state.room,
        wall_key="A",
    )

    warns = ((mod.get("params") or {}).get("installation_warnings") or [])
    if not warns:
        return False, "FAIL_missing_installation_warning"

    try:
        update_module_local(
            int(mod.get("id", 0)),
            x_mm=150,
            w_mm=600,
            h_mm=720,
            d_mm=560,
            gap_after_mm=0,
            label="Kod vrata",
            params=dict(mod.get("params", {}) or {}),
        )
        return False, "FAIL_door_constraint_update"
    except Exception:
        pass

    return True, "OK"


def smoke_warning_generation() -> tuple[bool, str]:
    modules = [
        {
            "id": 1, "template_id": "WALL_1DOOR", "label": "Gornji",
            "zone": "wall", "wall_key": "A", "x_mm": 5, "w_mm": 600, "h_mm": 720, "d_mm": 320, "params": {},
        },
        {
            "id": 2, "template_id": "WALL_UPPER_2DOOR", "label": "Drugi red",
            "zone": "wall_upper", "wall_key": "A", "x_mm": 5, "w_mm": 800, "h_mm": 360, "d_mm": 300, "params": {},
        },
        {
            "id": 3, "template_id": "BASE_DOOR_DRAWER", "label": "Vrata + fioka",
            "zone": "base", "wall_key": "A", "x_mm": 1000, "w_mm": 600, "h_mm": 720, "d_mm": 560,
            "params": {"door_height": 650, "drawer_heights": [50], "n_drawers": 1},
        },
        {
            "id": 4, "template_id": "BASE_1DOOR", "label": "Kod vode",
            "zone": "base", "wall_key": "A", "x_mm": 1700, "w_mm": 600, "h_mm": 720, "d_mm": 560,
            "params": {"installation_warnings": ["Instalacija u zoni elementa"]},
        },
    ]
    k = _default_kitchen()
    k["modules"] = modules
    rows = _manufacturing_warnings(modules, kitchen=k, wall_h_mm=2600, foot_h_mm=100, front_gap_mm=2)
    codes = {str(r.get("Naziv", "")) for r in rows}
    expected = {
        "UPOZORENJE (WALL_UPPER_SUPPORT)",
        "UPOZORENJE (DRAWER_FRONT_MIN)",
        "UPOZORENJE (DOOR_DRAWER_DRAWER_MIN)",
        "UPOZORENJE (INSTALLATION_ZONE)",
        "UPOZORENJE (SIDE_WALL_DOOR)",
        "UPOZORENJE (CORNER_OPENING_CLEARANCE)",
    }
    modules.append({
        "id": 5, "template_id": "BASE_1DOOR", "label": "Levi zid",
        "zone": "base", "wall_key": "A", "x_mm": 5, "w_mm": 600, "h_mm": 720, "d_mm": 560,
        "params": {"handle_side": "right"},
    })
    modules.append({
        "id": 6, "template_id": "BASE_CORNER", "label": "Cosak",
        "zone": "base", "wall_key": "A", "x_mm": 2305, "w_mm": 900, "h_mm": 720, "d_mm": 560,
        "params": {},
    })
    modules.append({
        "id": 7, "template_id": "BASE_1DOOR", "label": "Sused cosku",
        "zone": "base", "wall_key": "A", "x_mm": 3205, "w_mm": 600, "h_mm": 720, "d_mm": 560,
        "params": {"handle_side": "left"},
    })
    rows = _manufacturing_warnings(modules, kitchen=k, wall_h_mm=2600, foot_h_mm=100, front_gap_mm=2)
    codes = {str(r.get("Naziv", "")) for r in rows}
    missing = sorted(expected - codes)
    if missing:
        return False, f"FAIL_missing_warning_codes:{', '.join(missing)}"
    return True, "OK"


def smoke_shopping_hardware() -> tuple[bool, str]:
    k = _default_kitchen()
    k["modules"] = [
        {
            "id": 1, "template_id": "BASE_1DOOR", "label": "Donji 1",
            "zone": "base", "wall_key": "A", "x_mm": 5, "w_mm": 600, "h_mm": 720, "d_mm": 560,
            "gap_after_mm": 0, "params": {"n_shelves": 1},
        },
        {
            "id": 2, "template_id": "BASE_1DOOR", "label": "Donji 2",
            "zone": "base", "wall_key": "A", "x_mm": 605, "w_mm": 600, "h_mm": 720, "d_mm": 560,
            "gap_after_mm": 0, "params": {"n_shelves": 1},
        },
    ]
    sections = generate_cutlist(k)
    hw = sections.get("hardware")
    if hw is None or hw.empty:
        return False, "FAIL_no_hardware_rows"
    names = set(hw["Naziv"].astype(str).tolist())
    expected_hw = {
        "Spojnica susednih korpusa",
        "Klipsa za soklu",
        "Vijak / ugaonik za radnu ploču",
        "Zaptivna lajsna / silikon uz zid",
    }
    missing_hw = sorted(expected_hw - names)
    if missing_hw:
        return False, f"FAIL_missing_project_hardware:{', '.join(missing_hw)}"

    packet = build_service_packet(k, sections)
    shop = packet.get("shopping_list")
    if shop is None or shop.empty:
        return False, "FAIL_no_shopping_rows"
    shop_names = set(shop["Naziv"].astype(str).tolist())
    missing_shop = sorted(expected_hw - shop_names)
    if missing_shop:
        return False, f"FAIL_missing_project_shopping:{', '.join(missing_shop)}"
    return True, "OK"


def smoke_fastener_and_grouping_hardware() -> tuple[bool, str]:
    k = _default_kitchen()
    k["modules"] = [
        {
            "id": 1, "template_id": "BASE_1DOOR", "label": "Donji sa vratima",
            "zone": "base", "wall_key": "A", "x_mm": 5, "w_mm": 600, "h_mm": 720, "d_mm": 560,
            "gap_after_mm": 0, "params": {"n_shelves": 1},
        },
        {
            "id": 2, "template_id": "BASE_DRAWERS_3", "label": "Fiokar",
            "zone": "base", "wall_key": "A", "x_mm": 605, "w_mm": 600, "h_mm": 720, "d_mm": 560,
            "gap_after_mm": 0, "params": {"n_drawers": 3, "drawer_heights": [140, 140, 220]},
        },
        {
            "id": 3, "template_id": "WALL_1DOOR", "label": "Viseci",
            "zone": "wall", "wall_key": "A", "x_mm": 5, "w_mm": 600, "h_mm": 720, "d_mm": 320,
            "gap_after_mm": 0, "params": {"n_shelves": 1},
        },
    ]
    sections = generate_cutlist(k)
    hw = sections.get("hardware")
    if hw is None or hw.empty:
        return False, "FAIL_no_hardware_rows_fasteners"
    names = set(hw["Naziv"].astype(str).tolist())
    expected = {
        "Vijak za sarku",
        "Vijak za klizač",
        "Vijak / ekser za leđa",
        "Vijak za zidni nosač / šinu",
    }
    missing = sorted(expected - names)
    if missing:
        return False, f"FAIL_missing_fasteners:{', '.join(missing)}"

    packet = build_service_packet(k, sections)
    shop = packet.get("shopping_list")
    if shop is None or shop.empty:
        return False, "FAIL_no_shopping_rows_fasteners"
    groups = set(shop["Grupa"].astype(str).tolist())
    expected_groups = {
        "Projektni potrosni materijal",
        "Montaza na zid",
        "Okovi i mehanizmi po elementu",
    }
    missing_groups = sorted(expected_groups - groups)
    if missing_groups:
        return False, f"FAIL_missing_shopping_groups:{', '.join(missing_groups)}"
    return True, "OK"


def smoke_appliance_and_tall_hardware() -> tuple[bool, str]:
    k = _default_kitchen()
    k["modules"] = [
        {
            "id": 1, "template_id": "TALL_DOORS", "label": "Visoki pantry",
            "zone": "tall", "wall_key": "A", "x_mm": 5, "w_mm": 600, "h_mm": 2100, "d_mm": 560,
            "gap_after_mm": 0, "params": {"n_shelves": 4},
        },
        {
            "id": 2, "template_id": "BASE_DISHWASHER", "label": "MZS",
            "zone": "base", "wall_key": "A", "x_mm": 605, "w_mm": 600, "h_mm": 720, "d_mm": 560,
            "gap_after_mm": 0, "params": {},
        },
        {
            "id": 3, "template_id": "BASE_COOKING_UNIT", "label": "Rerna + ploca",
            "zone": "base", "wall_key": "A", "x_mm": 1205, "w_mm": 600, "h_mm": 720, "d_mm": 560,
            "gap_after_mm": 0, "params": {"has_drawer": True},
        },
    ]
    sections = generate_cutlist(k)
    hw = sections.get("hardware")
    if hw is None or hw.empty:
        return False, "FAIL_no_hardware_rows_appliance"
    names = set(hw["Naziv"].astype(str).tolist())
    expected = {
        "Anti-tip set",
        "Montažni set za front MZS",
        "Nosač fronta fioke",
        "Klizač za fioku",
    }
    missing = sorted(expected - names)
    if missing:
        return False, f"FAIL_missing_appliance_hardware:{', '.join(missing)}"
    return True, "OK"


def smoke_cooking_unit_drawer() -> tuple[bool, str]:
    k = _default_kitchen()
    k["modules"] = [
        {
            "id": 1, "template_id": "BASE_COOKING_UNIT", "label": "Rerna + ploca",
            "zone": "base", "wall_key": "A", "x_mm": 5, "w_mm": 600, "h_mm": 720, "d_mm": 560,
            "gap_after_mm": 0, "params": {"has_drawer": True, "drawer_heights": [130], "n_drawers": 1},
        },
    ]
    sections = generate_cutlist(k)
    fronts = sections.get("fronts")
    drawers = sections.get("drawer_boxes")
    hw = sections.get("hardware")
    if fronts is None or fronts.empty:
        return False, "FAIL_no_cooking_front"
    if drawers is None or drawers.empty:
        return False, "FAIL_no_cooking_drawer_box"
    hw_names = set(hw["Naziv"].astype(str).tolist()) if hw is not None and not hw.empty else set()
    if "Klizač za fioku" not in hw_names:
        return False, "FAIL_no_cooking_drawer_slide"
    if "Nosač fronta fioke" not in hw_names:
        return False, "FAIL_no_cooking_front_support"
    return True, "OK"


def smoke_door_drawer_preview() -> tuple[bool, str]:
    k = _default_kitchen()
    m = {
        "id": 1,
        "template_id": "BASE_DOOR_DRAWER",
        "label": "Donji (vrata + fioka)",
        "zone": "base",
        "wall_key": "A",
        "x_mm": 5,
        "w_mm": 600,
        "h_mm": 720,
        "d_mm": 560,
        "gap_after_mm": 0,
        "params": {"n_drawers": 1, "drawer_heights": [130]},
    }
    try:
        u2, u3 = render_element_preview(m, k)
        if not (isinstance(u2, str) and u2.startswith("data:image")):
            return False, "FAIL_door_drawer_2d_preview"
        if not (isinstance(u3, str) and u3.startswith("data:image")):
            return False, "FAIL_door_drawer_3d_preview"
    except Exception as ex:
        return False, f"FAIL_door_drawer_preview:{ex}"
    return True, "OK"


def smoke_appliances_not_listed_as_products() -> tuple[bool, str]:
    k = _default_kitchen()
    k["modules"] = [
        {"id": 1, "template_id": "TALL_FRIDGE", "label": "Ugradni frizider", "zone": "tall", "wall_key": "A", "x_mm": 5, "w_mm": 600, "h_mm": 2100, "d_mm": 560, "gap_after_mm": 0, "params": {}},
        {"id": 2, "template_id": "TALL_FRIDGE_FREESTANDING", "label": "Samostojeci frizider", "zone": "tall", "wall_key": "A", "x_mm": 605, "w_mm": 600, "h_mm": 2000, "d_mm": 650, "gap_after_mm": 0, "params": {}},
        {"id": 3, "template_id": "BASE_COOKING_UNIT", "label": "Rerna + ploca", "zone": "base", "wall_key": "A", "x_mm": 1205, "w_mm": 600, "h_mm": 720, "d_mm": 560, "gap_after_mm": 0, "params": {"has_drawer": True}},
        {"id": 4, "template_id": "BASE_OVEN_HOB_FREESTANDING", "label": "Samostojeci sporet", "zone": "base", "wall_key": "A", "x_mm": 1805, "w_mm": 600, "h_mm": 850, "d_mm": 600, "gap_after_mm": 0, "params": {}},
        {"id": 5, "template_id": "BASE_DISHWASHER", "label": "Ugradna MZS", "zone": "base", "wall_key": "A", "x_mm": 2405, "w_mm": 600, "h_mm": 720, "d_mm": 560, "gap_after_mm": 0, "params": {}},
        {"id": 6, "template_id": "BASE_DISHWASHER_FREESTANDING", "label": "Samostojeca MZS", "zone": "base", "wall_key": "A", "x_mm": 3005, "w_mm": 600, "h_mm": 850, "d_mm": 600, "gap_after_mm": 0, "params": {}},
    ]
    sections = generate_cutlist(k)
    hw = sections.get("hardware")
    if hw is None:
        return False, "FAIL_no_hardware_for_appliance_product_test"
    names = set(hw["Naziv"].astype(str).tolist()) if not hw.empty else set()
    forbidden = {
        "Ugradni frižider",
        "Ugradni frižider sa zamrzivačem",
        "Ugradna rerna",
        "Ploča za kuvanje",
        "Ugradna mikrotalasna",
        "Samostojeća mašina za sudove",
        "Samostojeći šporet",
        "Samostojeći frižider",
        "Ugradna mašina za sudove",
        "Aspirator / napa",
        "Mikrotalasna",
    }
    found = sorted(forbidden & names)
    if found:
        return False, f"FAIL_appliance_products_still_listed:{', '.join(found)}"
    packet = build_service_packet(k, sections)
    shop = packet.get("shopping_list")
    shop_names = set(shop["Naziv"].astype(str).tolist()) if shop is not None and not shop.empty else set()
    found_shop = sorted(forbidden & shop_names)
    if found_shop:
        return False, f"FAIL_appliance_products_in_shopping:{', '.join(found_shop)}"
    return True, "OK"


def smoke_service_processing_packet() -> tuple[bool, str]:
    k = _default_kitchen()
    k["modules"] = [
        {"id": 1, "template_id": "SINK_BASE", "label": "Sudopera", "zone": "base", "wall_key": "A", "x_mm": 5, "w_mm": 800, "h_mm": 720, "d_mm": 560, "gap_after_mm": 0, "params": {}},
        {"id": 2, "template_id": "BASE_COOKING_UNIT", "label": "Rerna + ploca", "zone": "base", "wall_key": "A", "x_mm": 805, "w_mm": 600, "h_mm": 720, "d_mm": 560, "gap_after_mm": 0, "params": {"has_drawer": True}},
        {"id": 3, "template_id": "BASE_DISHWASHER", "label": "Ugradna MZS", "zone": "base", "wall_key": "A", "x_mm": 1405, "w_mm": 600, "h_mm": 720, "d_mm": 560, "gap_after_mm": 0, "params": {}},
        {"id": 4, "template_id": "WALL_HOOD", "label": "Napa", "zone": "wall", "wall_key": "A", "x_mm": 805, "w_mm": 600, "h_mm": 500, "d_mm": 320, "gap_after_mm": 0, "params": {}},
        {"id": 5, "template_id": "WALL_MICRO", "label": "Mikrotalasna", "zone": "wall", "wall_key": "A", "x_mm": 1405, "w_mm": 600, "h_mm": 500, "d_mm": 320, "gap_after_mm": 0, "params": {}},
        {"id": 6, "template_id": "TALL_FRIDGE", "label": "Ugradni frizider", "zone": "tall", "wall_key": "A", "x_mm": 2005, "w_mm": 600, "h_mm": 2100, "d_mm": 560, "gap_after_mm": 0, "params": {}},
    ]
    sections = generate_cutlist(k)
    packet = build_service_packet(k, sections)
    proc = packet.get("service_processing")
    instr = packet.get("service_instructions")
    if proc is None or proc.empty:
        return False, "FAIL_no_service_processing"
    if instr is None or instr.empty:
        return False, "FAIL_no_service_instructions"

    proc_types = set(proc["Tip obrade"].astype(str).tolist()) if "Tip obrade" in proc.columns else set()
    missing_types = {
        "Otvor za sudoperu",
        "Otvor za plocu",
        "Instalacioni prolaz",
        "Ventilacija / otvor",
        "Prolaz za kabl",
    } - proc_types
    if missing_types:
        return False, f"FAIL_missing_processing_types:{', '.join(sorted(missing_types))}"

    if "Izvodi" not in proc.columns:
        return False, "FAIL_missing_processing_executor"
    if "Osnov izvođenja" not in proc.columns:
        return False, "FAIL_missing_processing_basis"
    executors = set(proc["Izvodi"].astype(str).tolist())
    if "Servis" not in executors:
        return False, "FAIL_missing_service_executor"
    if "Kuća / lice mesta" not in executors:
        return False, "FAIL_missing_home_executor"
    bases = set(proc["Osnov izvođenja"].astype(str).tolist())
    if "Po šablonu proizvođača" not in bases:
        return False, "FAIL_missing_manufacturer_template_basis"

    if len(instr.index) < 8:
        return False, "FAIL_service_instructions_too_short"
    if "Instrukcija" not in instr.columns:
        return False, "FAIL_missing_instruction_text"
    return True, "OK"


def smoke_partcode_preview_annotations() -> tuple[bool, str]:
    k = _default_kitchen()
    m = {
        "id": 1,
        "template_id": "BASE_DOOR_DRAWER",
        "label": "Vrata + fioka",
        "zone": "base",
        "wall_key": "A",
        "x_mm": 0,
        "w_mm": 1000,
        "h_mm": 720,
        "d_mm": 560,
        "gap_after_mm": 0,
        "params": {},
    }
    k["modules"] = [m]
    sections = generate_cutlist(k)
    frames = [df for key, df in sections.items() if key != "hardware" and df is not None and not df.empty]
    if not frames:
        return False, "FAIL_no_part_frames"
    parts = pd.concat(frames, ignore_index=True)
    part_rows = parts[parts["ID"] == 1].to_dict("records")
    if not part_rows:
        return False, "FAIL_no_module_parts"
    u2, u3 = render_element_preview(m, k, label_mode="part_codes", part_rows=part_rows)
    if not (str(u2).startswith("data:image/png;base64,") and str(u3).startswith("data:image/png;base64,")):
        return False, "FAIL_preview_not_rendered"
    front_codes = [str(r.get("PartCode", "")) for r in part_rows if str(r.get("PartCode", "")).startswith("M1-F")]
    if len(front_codes) < 2:
        return False, "FAIL_missing_front_codes_for_preview"
    return True, "OK"


def smoke_multiwall_l_basic() -> tuple[bool, str]:
    reset_state()
    state.kitchen_layout = "l_oblik"
    state.room["active_wall"] = "A"
    walls = state.room.get("walls", []) or []
    wall_a = next((w for w in walls if str(w.get("key", "")).upper() == "A"), None)
    wall_b = next((w for w in walls if str(w.get("key", "")).upper() == "B"), None)
    if wall_a is None or wall_b is None:
        return False, "FAIL_missing_room_walls"
    wall_a["length_mm"] = 3000
    wall_b["length_mm"] = 2100
    wall_a["height_mm"] = 2600
    wall_b["height_mm"] = 2600

    add_module_instance_local(
        template_id="BASE_2DOOR",
        zone="base",
        x_mm=0,
        w_mm=800,
        h_mm=720,
        d_mm=560,
        label="A base",
        params={},
        room=state.room,
        wall_key="A",
    )
    add_module_instance_local(
        template_id="BASE_2DOOR",
        zone="base",
        x_mm=0,
        w_mm=900,
        h_mm=720,
        d_mm=560,
        label="B base",
        params={},
        room=state.room,
        wall_key="B",
    )
    mods = state.kitchen.get("modules", []) or []
    if len(mods) != 2:
        return False, "FAIL_missing_multiwall_modules"
    a_mod = next((m for m in mods if str(m.get("wall_key", "A")).upper() == "A"), None)
    b_mod = next((m for m in mods if str(m.get("wall_key", "A")).upper() == "B"), None)
    if a_mod is None or b_mod is None:
        return False, "FAIL_wall_key_not_saved"
    if int(b_mod.get("x_mm", -1)) < 0:
        return False, "FAIL_invalid_wall_b_position"
    ok, msg = layout_audit(state.kitchen)
    if not ok:
        return False, f"FAIL_layout_audit:{msg}"
    return True, "OK"


def smoke_multiwall_cutlist_segments() -> tuple[bool, str]:
    reset_state()
    state.kitchen_layout = "l_oblik"
    state.room["active_wall"] = "A"
    walls = state.room.get("walls", []) or []
    wall_a = next((w for w in walls if str(w.get("key", "")).upper() == "A"), None)
    wall_b = next((w for w in walls if str(w.get("key", "")).upper() == "B"), None)
    if wall_a is None or wall_b is None:
        return False, "FAIL_missing_room_walls"
    wall_a["length_mm"] = 3200
    wall_b["length_mm"] = 2400

    add_module_instance_local(
        template_id="BASE_2DOOR",
        zone="base",
        x_mm=0,
        w_mm=1200,
        h_mm=720,
        d_mm=560,
        label="A base",
        params={},
        room=state.room,
        wall_key="A",
    )
    add_module_instance_local(
        template_id="BASE_2DOOR",
        zone="base",
        x_mm=0,
        w_mm=1000,
        h_mm=720,
        d_mm=560,
        label="B base",
        params={},
        room=state.room,
        wall_key="B",
    )
    sections = generate_cutlist(state.kitchen)
    plinth_df = sections.get("plinth")
    worktop_df = sections.get("worktop")
    if plinth_df is None or plinth_df.empty or worktop_df is None or worktop_df.empty:
        return False, "FAIL_missing_multiwall_sections"
    _pl_walls = set(plinth_df.get("Zid", pd.Series(dtype=str)).astype(str))
    _wt_walls = set(worktop_df.get("Zid", pd.Series(dtype=str)).astype(str))
    if not {"Zid A", "Zid B"}.issubset(_pl_walls):
        return False, "FAIL_plinth_not_split_by_wall"
    if not {"Zid A", "Zid B"}.issubset(_wt_walls):
        return False, "FAIL_worktop_not_split_by_wall"
    packet = build_service_packet(state.kitchen, sections)
    _svc = packet.get("service_cuts")
    if _svc is None or _svc.empty:
        return False, "FAIL_missing_service_cuts"
    _svc_walls = set(_svc.get("Zid", pd.Series(dtype=str)).astype(str))
    if not {"Zid A", "Zid B"}.issubset(_svc_walls):
        return False, "FAIL_service_not_split_by_wall"
    return True, "OK"


def smoke_corner_rules() -> tuple[bool, str]:
    k = _default_kitchen()
    k["wall_lengths_mm"] = {"A": 3000, "B": 2200}
    k["wall_heights_mm"] = {"A": 2600, "B": 2600}
    k["modules"] = [
        {
            "id": 1, "template_id": "BASE_2DOOR", "label": "A1",
            "zone": "base", "wall_key": "A", "x_mm": 5, "w_mm": 900, "h_mm": 720, "d_mm": 560, "params": {},
        },
        {
            "id": 2, "template_id": "BASE_CORNER", "label": "A cosak",
            "zone": "base", "wall_key": "A", "x_mm": 2095, "w_mm": 900, "h_mm": 720, "d_mm": 560, "params": {},
        },
        {
            "id": 3, "template_id": "BASE_CORNER", "label": "B cosak",
            "zone": "base", "wall_key": "B", "x_mm": 5, "w_mm": 900, "h_mm": 720, "d_mm": 560, "params": {},
        },
        {
            "id": 4, "template_id": "BASE_2DOOR", "label": "B1",
            "zone": "base", "wall_key": "B", "x_mm": 905, "w_mm": 800, "h_mm": 720, "d_mm": 560, "params": {},
        },
    ]
    ok, msg = layout_audit(k)
    if not ok:
        return False, f"FAIL_valid_corner_layout:{msg}"

    reset_state()
    state.kitchen_layout = "l_oblik"
    state.room["active_wall"] = "A"
    walls = state.room.get("walls", []) or []
    wall_a = next((w for w in walls if str(w.get("key", "")).upper() == "A"), None)
    if wall_a is None:
        return False, "FAIL_missing_wall_a"
    wall_a["length_mm"] = 3000
    add_module_instance_local(
        template_id="BASE_2DOOR",
        zone="base",
        x_mm=5,
        w_mm=900,
        h_mm=720,
        d_mm=560,
        label="A1",
        params={},
        room=state.room,
        wall_key="A",
    )
    mod = add_module_instance_local(
        template_id="BASE_CORNER",
        zone="base",
        x_mm=1000,
        w_mm=900,
        h_mm=720,
        d_mm=560,
        label="Los cosak",
        params={},
        room=state.room,
        wall_key="A",
    )
    if int(mod.get("x_mm", -1)) != 2095:
        return False, f"FAIL_corner_should_anchor_{mod.get('x_mm')}"
    return True, "OK"


def smoke_corner_door_swing_rules() -> tuple[bool, str]:
    reset_state()
    state.kitchen_layout = "l_oblik"
    state.room["active_wall"] = "A"
    walls = state.room.get("walls", []) or []
    wall_a = next((w for w in walls if str(w.get("key", "")).upper() == "A"), None)
    if wall_a is None:
        return False, "FAIL_missing_wall_a"
    wall_a["length_mm"] = 3000

    add_module_instance_local(
        template_id="BASE_CORNER",
        zone="base",
        x_mm=2095,
        w_mm=900,
        h_mm=720,
        d_mm=560,
        label="Cosak",
        params={},
        room=state.room,
        wall_key="A",
    )
    try:
        add_module_instance_local(
            template_id="BASE_1DOOR",
            zone="base",
            x_mm=1495,
            w_mm=600,
            h_mm=720,
            d_mm=560,
            label="Lose vrata",
            params={"handle_side": "left"},
            room=state.room,
            wall_key="A",
        )
        return False, "FAIL_corner_door_swing_should_block"
    except Exception:
        pass

    try:
        add_module_instance_local(
            template_id="BASE_1DOOR",
            zone="base",
            x_mm=1495,
            w_mm=600,
            h_mm=720,
            d_mm=560,
            label="Preširoka dobra vrata",
            params={"handle_side": "right"},
            room=state.room,
            wall_key="A",
        )
        return False, "FAIL_corner_door_width_should_block"
    except Exception:
        pass

    add_module_instance_local(
        template_id="BASE_NARROW",
        zone="base",
        x_mm=1645,
        w_mm=450,
        h_mm=720,
        d_mm=560,
        label="Dobra vrata",
        params={"handle_side": "right"},
        room=state.room,
        wall_key="A",
    )
    return True, "OK"


def smoke_corner_guidance_helper() -> tuple[bool, str]:
    reset_state()
    state.kitchen_layout = "l_oblik"
    state.room["active_wall"] = "A"
    walls = state.room.get("walls", []) or []
    wall_a = next((w for w in walls if str(w.get("key", "")).upper() == "A"), None)
    if wall_a is None:
        return False, "FAIL_missing_wall_a"
    wall_a["length_mm"] = 3000
    add_module_instance_local(
        template_id="BASE_CORNER",
        zone="base",
        x_mm=2095,
        w_mm=900,
        h_mm=720,
        d_mm=560,
        label="Cosak",
        params={},
        room=state.room,
        wall_key="A",
    )
    info = suggest_corner_neighbor_guidance("base", "A", "BASE_NARROW")
    if not info.get("active"):
        return False, "FAIL_guidance_not_active"
    if str(info.get("recommended_handle_side", "")) != "right":
        return False, "FAIL_wrong_handle_side"
    if "BASE_NARROW" not in list(info.get("recommended_templates", [])):
        return False, "FAIL_missing_recommended_template"
    return True, "OK"


def smoke_l_left_corner_mode() -> tuple[bool, str]:
    reset_state()
    state.kitchen_layout = "l_oblik"
    state.l_corner_side = "left"
    state.kitchen["layout"] = "l_oblik"
    state.kitchen["l_corner_side"] = "left"
    state.room["active_wall"] = "A"
    walls = state.room.get("walls", []) or []
    wall_a = next((w for w in walls if str(w.get("key", "")).upper() == "A"), None)
    if wall_a is None:
        return False, "FAIL_missing_wall_a"
    wall_a["length_mm"] = 3000
    add_module_instance_local(
        template_id="BASE_CORNER",
        zone="base",
        x_mm=5,
        w_mm=900,
        h_mm=720,
        d_mm=560,
        label="Levi cosak",
        params={},
        room=state.room,
        wall_key="A",
    )
    try:
        add_module_instance_local(
            template_id="BASE_CORNER",
            zone="base",
            x_mm=2095,
            w_mm=900,
            h_mm=720,
            d_mm=560,
            label="Pogresan cosak",
            params={},
            room=state.room,
            wall_key="A",
        )
        return False, "FAIL_left_mode_should_reject_right_corner"
    except Exception:
        pass
    info = suggest_corner_neighbor_guidance("base", "A", "BASE_NARROW")
    if str(info.get("recommended_handle_side", "")) != "left":
        return False, "FAIL_left_mode_handle_hint"
    return True, "OK"


def smoke_wall_corner_autoplace() -> tuple[bool, str]:
    reset_state()
    state.kitchen_layout = "l_oblik"
    state.kitchen["layout"] = "l_oblik"
    state.kitchen["l_corner_side"] = "right"
    state.room = _default_room()
    state.room["active_wall"] = "B"
    walls = state.room.get("walls", []) or []
    wall_b = next((w for w in walls if str(w.get("key", "")).upper() == "B"), None)
    if wall_b is None:
        return False, "FAIL_missing_wall_b"
    wall_b["length_mm"] = 2100
    state.kitchen["wall_lengths_mm"] = {"A": 3000, "B": 2100}
    mod = add_module_instance_local(
        template_id="WALL_CORNER",
        zone="wall",
        x_mm=900,
        w_mm=600,
        h_mm=720,
        d_mm=350,
        label="Viseci cosak",
        params={},
        room=state.room,
        wall_key="B",
    )
    if int(mod.get("x_mm", -1)) != 5:
        return False, f"FAIL_wall_corner_anchor_{mod.get('x_mm')}"
    return True, "OK"


def smoke_diagonal_corner_preview_distinct() -> tuple[bool, str]:
    k = _default_kitchen()
    base_common = {
        "id": 1,
        "label": "Cosak",
        "zone": "base",
        "x_mm": 0,
        "w_mm": 900,
        "h_mm": 720,
        "d_mm": 560,
        "params": {},
    }
    l_mod = dict(base_common, template_id="BASE_CORNER")
    d_mod = dict(base_common, id=2, template_id="BASE_CORNER_DIAGONAL")
    try:
        l_uri_2d, _ = render_element_preview(l_mod, k)
        d_uri_2d, _ = render_element_preview(d_mod, k)
    except Exception as ex:
        return False, f"FAIL_corner_preview_render:{ex}"
    if not l_uri_2d or not d_uri_2d:
        return False, "FAIL_corner_preview_missing_uri"
    if l_uri_2d == d_uri_2d:
        return False, "FAIL_corner_preview_same"
    return True, "OK"


def smoke_diagonal_corner_preview_3d_distinct() -> tuple[bool, str]:
    k = _default_kitchen()
    common = {
        "label": "Cosak",
        "zone": "base",
        "x_mm": 0,
        "w_mm": 900,
        "h_mm": 720,
        "d_mm": 560,
        "params": {},
    }
    l_mod = dict(common, id=1, template_id="BASE_CORNER")
    d_mod = dict(common, id=2, template_id="BASE_CORNER_DIAGONAL")
    try:
        _, l_uri_3d = render_element_preview(l_mod, k)
        _, d_uri_3d = render_element_preview(d_mod, k)
    except Exception as ex:
        return False, f"FAIL_corner_preview_3d_render:{ex}"
    if not l_uri_3d or not d_uri_3d:
        return False, "FAIL_corner_preview_3d_missing_uri"
    if l_uri_3d == d_uri_3d:
        return False, "FAIL_corner_preview_3d_same"
    return True, "OK"


def smoke_l_corner_offset_no_collision() -> tuple[bool, str]:
    """
    P2A-4: Regularni Wall B moduli moraju početi na x >= dubina_zida_A (560mm).
    Bez ugaonog modula — provjera da find_first_free_x i compact ne postavljaju module
    na x < 560mm (= zone kolizije s Zidom A).
    """
    reset_state()
    state.kitchen_layout = "l_oblik"
    state.kitchen["layout"] = "l_oblik"
    state.kitchen["kitchen_layout"] = "l_oblik"
    state.kitchen["l_corner_side"] = "right"
    state.l_corner_side = "right"
    state.room["active_wall"] = "B"

    ensure_room_walls(state.room)
    walls = state.room.get("walls", []) or []
    wall_a = next((w for w in walls if str(w.get("key", "")).upper() == "A"), None)
    wall_b = next((w for w in walls if str(w.get("key", "")).upper() == "B"), None)
    if wall_a is None or wall_b is None:
        return False, "FAIL_missing_room_walls"
    wall_a["length_mm"] = 3000
    wall_b["length_mm"] = 2400
    wall_a["height_mm"] = 2600
    wall_b["height_mm"] = 2600
    state.kitchen.setdefault("wall_lengths_mm", {})["A"] = 3000
    state.kitchen.setdefault("wall_lengths_mm", {})["B"] = 2400

    # Dodaj 2 regularna Base modula na Wall B (nema ugaonog modula)
    add_module_instance_local(
        template_id="BASE_2DOOR",
        zone="base",
        x_mm=0,  # namjerno 0 — layout mora ispraviti na >=560
        w_mm=600,
        h_mm=720,
        d_mm=560,
        label="B base 1",
        params={},
        room=state.room,
        wall_key="B",
    )
    add_module_instance_local(
        template_id="BASE_2DOOR",
        zone="base",
        x_mm=0,  # namjerno 0
        w_mm=600,
        h_mm=720,
        d_mm=560,
        label="B base 2",
        params={},
        room=state.room,
        wall_key="B",
    )

    mods_b = [
        m for m in (state.kitchen.get("modules", []) or [])
        if str(m.get("wall_key", "A")).upper() == "B"
    ]
    if len(mods_b) < 2:
        return False, f"FAIL_modules_not_added (got {len(mods_b)})"

    # Provjeri da nijedan modul na Wall B ne počinje prije 560mm
    # (dubina Wall A base zone = 560mm po defaultu)
    _min_expected_x = 560
    for m in mods_b:
        _x = int(m.get("x_mm", 0))
        if _x < _min_expected_x:
            return False, (
                f"FAIL_corner_offset_violation: Wall B modul id={m.get('id')} "
                f"na x={_x}mm, treba >={_min_expected_x}mm"
            )

    ok, msg = layout_audit(state.kitchen)
    if not ok:
        return False, f"FAIL_layout_audit:{msg}"
    return True, "OK"


def smoke_l_corner_offset_with_corner_mod() -> tuple[bool, str]:
    """
    P2A-4: Kad postoji ugaoni modul na Wall B (anchor lijevo),
    on ostaje na x=0, a regularni moduli počinju tek iza njega (> corner_width).
    """
    reset_state()
    state.kitchen_layout = "l_oblik"
    state.kitchen["layout"] = "l_oblik"
    state.kitchen["kitchen_layout"] = "l_oblik"
    state.kitchen["l_corner_side"] = "right"
    state.l_corner_side = "right"
    state.room["active_wall"] = "B"

    ensure_room_walls(state.room)
    walls = state.room.get("walls", []) or []
    wall_a = next((w for w in walls if str(w.get("key", "")).upper() == "A"), None)
    wall_b = next((w for w in walls if str(w.get("key", "")).upper() == "B"), None)
    if wall_a is None or wall_b is None:
        return False, "FAIL_missing_room_walls"
    wall_a["length_mm"] = 3000
    wall_b["length_mm"] = 2400
    state.kitchen.setdefault("wall_lengths_mm", {})["A"] = 3000
    state.kitchen.setdefault("wall_lengths_mm", {})["B"] = 2400

    # Ugaoni modul na Wall B (anchor=lijevo jer je l_corner_side='right')
    add_module_instance_local(
        template_id="BASE_CORNER",
        zone="base",
        x_mm=0,
        w_mm=900,
        h_mm=720,
        d_mm=560,
        label="B corner",
        params={},
        room=state.room,
        wall_key="B",
    )
    # Regularni modul iza ugaonog
    add_module_instance_local(
        template_id="BASE_2DOOR",
        zone="base",
        x_mm=0,  # namjerno 0 — mora biti postavljen iza ugaonog
        w_mm=600,
        h_mm=720,
        d_mm=560,
        label="B regular",
        params={},
        room=state.room,
        wall_key="B",
    )

    mods_b = [
        m for m in (state.kitchen.get("modules", []) or [])
        if str(m.get("wall_key", "A")).upper() == "B"
    ]
    corner_b = next((m for m in mods_b if "CORNER" in str(m.get("template_id", "")).upper()), None)
    regular_b = [m for m in mods_b if "CORNER" not in str(m.get("template_id", "")).upper()]

    if corner_b is None:
        return False, "FAIL_corner_module_missing"
    if not regular_b:
        return False, "FAIL_regular_module_missing"

    # Ugaoni modul mora biti na anchor poziciji lijevo (x <= left_clearance+5, obično 0..10mm)
    # Ne smije biti pomjeren na 560mm (corner offset zone) od strane compact algoritma
    _cx = int(corner_b.get("x_mm", -1))
    _max_anchor_x = 15  # left_clearance (tipično 5mm) + tolerancija
    if _cx > _max_anchor_x:
        return False, (
            f"FAIL_corner_moved_from_anchor: x={_cx}, "
            f"ugaoni modul mora biti na lijevom anchoru (x<={_max_anchor_x})"
        )

    # Regularni modul mora biti iza ugaonog (x >= 900)
    _corner_end = int(corner_b.get("x_mm", 0)) + int(corner_b.get("w_mm", 900))
    for m in regular_b:
        _rx = int(m.get("x_mm", 0))
        if _rx < _corner_end:
            return False, (
                f"FAIL_regular_inside_corner_span: id={m.get('id')} "
                f"x={_rx} < corner_end={_corner_end}"
            )

    ok, msg = layout_audit(state.kitchen)
    if not ok:
        return False, f"FAIL_layout_audit:{msg}"
    return True, "OK"


def smoke_l_corner_offset_audit_catches_violation() -> tuple[bool, str]:
    """
    P2A-4: layout_audit mora da uhvati modul koji je ručno postavljen unutar ugaone zone.
    Ovo testira negativni slučaj — audit se MORA buniti.
    Modul se postavlja na x=100 (unutar bounds, ali unutar ugaone zone 0..560).
    """
    reset_state()
    state.kitchen_layout = "l_oblik"
    state.kitchen["layout"] = "l_oblik"
    state.kitchen["kitchen_layout"] = "l_oblik"
    state.kitchen["l_corner_side"] = "right"
    state.l_corner_side = "right"
    state.room["active_wall"] = "B"

    ensure_room_walls(state.room)
    walls = state.room.get("walls", []) or []
    wall_b = next((w for w in walls if str(w.get("key", "")).upper() == "B"), None)
    if wall_b is None:
        return False, "FAIL_missing_room_walls"
    wall_b["length_mm"] = 2400
    state.kitchen.setdefault("wall_lengths_mm", {})["A"] = 3000
    state.kitchen.setdefault("wall_lengths_mm", {})["B"] = 2400

    # Direktno dodaj modul na x=100 (unutar bounds ali unutar ugaone zone!)
    # x=100 je >= left_clear (5mm) pa neće pasti na out-of-bounds,
    # ali je < 560mm (corner offset) pa MORA pasti na corner offset check.
    mods = state.kitchen.setdefault("modules", [])
    mods.append({
        "id": 9999,
        "template_id": "BASE_2DOOR",
        "zone": "base",
        "wall_key": "B",
        "x_mm": 100,   # NAMJERNO u ugaonoj zoni (100 < 560)!
        "w_mm": 600,
        "h_mm": 720,
        "d_mm": 560,
        "label": "Violation modul",
        "params": {},
    })

    ok, msg = layout_audit(state.kitchen)
    # Audit MORA da otkrije kršenje
    if ok:
        return False, "FAIL_audit_did_not_catch_corner_violation"
    if "corner offset" not in msg.lower() and "Corner offset" not in msg:
        return False, f"FAIL_audit_wrong_error_message: {msg}"
    return True, "OK"


def smoke_wardrobe_hardware() -> tuple[bool, str]:
    """
    P1-6a: Wardrobe moduli moraju dobiti ispravne okove:
    - TALL_WARDROBE_2DOOR_SLIDING, TALL_WARDROBE_CORNER_SLIDING, TALL_WARDROBE_AMERICAN
      → 'Klizni sistem vrata' red + 'Set tockica' red
    - TALL_WARDROBE_INT_HANG
      → 'Sipka za vesanje' red + 'Nosaci sipke' red
    """
    def make_mod(mid, tid, w=1800, h=2400, d=620):
        return {
            "id": mid, "template_id": tid, "zone": "tall",
            "label": tid, "w_mm": w, "h_mm": h, "d_mm": d,
            "params": {}, "wall_key": "A", "x_mm": (mid - 1) * w,
        }

    k = _default_kitchen()
    k["modules"] = [
        make_mod(1, "TALL_WARDROBE_2DOOR_SLIDING", w=1800),
        make_mod(2, "TALL_WARDROBE_CORNER_SLIDING", w=1400),
        make_mod(3, "TALL_WARDROBE_AMERICAN", w=2400),
        make_mod(4, "TALL_WARDROBE_INT_HANG", w=800),
    ]
    k["manufacturing"] = {"profile": "EU_SRB_BLUM"}

    result = generate_cutlist(k)
    hw = result["hardware"]

    # Filtriraj samo okove (ne potrosni, ne warning)
    okovi = hw[hw["Kategorija"] == "okov"]

    # Provjeri klizni sistem za M1 i M2
    for mid, label, exp_panels in [(1, "TALL_WARDROBE_2DOOR_SLIDING", 2),
                                    (2, "TALL_WARDROBE_CORNER_SLIDING", 2),
                                    (3, "TALL_WARDROBE_AMERICAN", 3)]:
        mod_hw = okovi[okovi["ID"] == mid]
        klizni = mod_hw[mod_hw["Naziv"].str.contains("Klizni sistem", na=False)]
        if klizni.empty:
            return False, f"FAIL: {label} nema 'Klizni sistem' u hardware-u"
        tockici = mod_hw[mod_hw["Naziv"].str.contains("tockic", na=False)]
        if tockici.empty:
            return False, f"FAIL: {label} nema 'Set tockica' u hardware-u"
        n_tockici = int(tockici.iloc[0]["Kol."])
        if n_tockici != exp_panels:
            return False, f"FAIL: {label} treba {exp_panels} seta tockica, dobijeno {n_tockici}"

    # Provjeri sipku za vesanje za M4
    hang_hw = okovi[okovi["ID"] == 4]
    sipka = hang_hw[hang_hw["Naziv"].str.contains("Sipka", na=False)]
    if sipka.empty:
        return False, "FAIL: TALL_WARDROBE_INT_HANG nema 'Sipka za vesanje' u hardware-u"
    nosaci = hang_hw[hang_hw["Naziv"].str.contains("Nosaci sipke", na=False)]
    if nosaci.empty:
        return False, "FAIL: TALL_WARDROBE_INT_HANG nema 'Nosaci sipke' u hardware-u"
    n_nosaca = int(nosaci.iloc[0]["Kol."])
    if n_nosaca != 2:
        return False, f"FAIL: Ocekivana 2 nosaca, dobijeno {n_nosaca}"

    return True, "OK"


def smoke_freestanding_appliance_validation() -> tuple[bool, str]:
    """
    P1-6b: Freestanding aparati koji su premaleni moraju imati manufacturing warning.
    - BASE_DISHWASHER_FREESTANDING w=400 < 600 -> DISHWASHER_WIDTH
    - TALL_FRIDGE_FREESTANDING w=400 < 600 -> FRIDGE_WIDTH
    - BASE_OVEN_HOB_FREESTANDING w=400 < 600 -> COOKING_WIDTH
    - BASE_HOB w=300 < 450 -> HOB_WIDTH
    """
    k = _default_kitchen()
    modules = [
        {
            "id": 1, "template_id": "BASE_DISHWASHER_FREESTANDING",
            "zone": "base", "w_mm": 400, "h_mm": 820, "d_mm": 580,
            "label": "MZS free", "params": {}, "wall_key": "A", "x_mm": 0,
        },
        {
            "id": 2, "template_id": "TALL_FRIDGE_FREESTANDING",
            "zone": "tall", "w_mm": 400, "h_mm": 2000, "d_mm": 620,
            "label": "Friz free", "params": {}, "wall_key": "A", "x_mm": 400,
        },
        {
            "id": 3, "template_id": "BASE_OVEN_HOB_FREESTANDING",
            "zone": "base", "w_mm": 400, "h_mm": 820, "d_mm": 600,
            "label": "Stednjak free", "params": {}, "wall_key": "A", "x_mm": 800,
        },
        {
            "id": 4, "template_id": "BASE_HOB",
            "zone": "base", "w_mm": 300, "h_mm": 720, "d_mm": 560,
            "label": "Ploca", "params": {}, "wall_key": "A", "x_mm": 1200,
        },
    ]
    k["modules"] = modules
    rows = _manufacturing_warnings(
        modules, kitchen=k, wall_h_mm=2600, foot_h_mm=100, front_gap_mm=2
    )
    codes = {str(r.get("Naziv", "")) for r in rows}

    expected_codes = {
        "UPOZORENJE (DISHWASHER_WIDTH)",
        "UPOZORENJE (FRIDGE_WIDTH)",
        "UPOZORENJE (COOKING_WIDTH)",
        "UPOZORENJE (HOB_WIDTH)",
    }
    missing = sorted(expected_codes - codes)
    if missing:
        return False, f"FAIL_missing_freestanding_warnings: {', '.join(missing)}"
    return True, "OK"


def smoke_hardware_counts_standard() -> tuple[bool, str]:
    """
    P1-6c: Provjeri tacne hardware row-ove za najcesca scenarija:
    - BASE_1DOOR w=600 h=720 -> 2 sarke (h<=900 -> 2/vrata), 1 rucka
    - WALL_2DOOR w=800 h=720 -> 4 sarke (2 vrata x 2 sarke), 2 rucke
    - BASE_DRAWERS_3 w=600 h=720 -> 3 klizaca, 3 rucke
    - WALL_LIFTUP w=800 h=400 -> 1 liftup par, 1 rucka
    """
    k = _default_kitchen()
    k["modules"] = [
        {
            "id": 1, "template_id": "BASE_1DOOR", "zone": "base",
            "label": "Jednokrilni", "w_mm": 600, "h_mm": 720, "d_mm": 560,
            "params": {}, "wall_key": "A", "x_mm": 0,
        },
        {
            "id": 2, "template_id": "WALL_2DOOR", "zone": "wall",
            "label": "Gornji dvokrilni", "w_mm": 800, "h_mm": 720, "d_mm": 300,
            "params": {}, "wall_key": "A", "x_mm": 0,
        },
        {
            "id": 3, "template_id": "BASE_DRAWERS_3", "zone": "base",
            "label": "Fiokar 3", "w_mm": 600, "h_mm": 720, "d_mm": 560,
            "params": {"n_drawers": 3}, "wall_key": "A", "x_mm": 600,
        },
        {
            "id": 4, "template_id": "WALL_LIFTUP", "zone": "wall",
            "label": "Liftup gornji", "w_mm": 800, "h_mm": 400, "d_mm": 300,
            "params": {}, "wall_key": "A", "x_mm": 800,
        },
    ]
    k["manufacturing"] = {"profile": "EU_SRB_BLUM"}

    result = generate_cutlist(k)
    hw = result["hardware"]
    okovi = hw[hw["Kategorija"] == "okov"]

    # Helperi za nalazenje redova (ASCII-safe pattern matching):
    # - sarke: "arka" je substring "Šarka" (Š + arka) ✓
    # - rucke: koristimo "pull" koji je ASCII u "Ručka / pull" ✓
    # - klizaci: "za fioku" je ASCII-safe u "Klizač za fioku" ✓
    # - liftup: "ift" je ASCII-safe u "Lift-up" ✓

    # M1: BASE_1DOOR — 2 sarke, 1 rucka
    m1_hw = okovi[okovi["ID"] == 1]
    sarke_m1 = m1_hw[m1_hw["Naziv"].str.contains("arka", na=False)]
    if sarke_m1.empty:
        return False, "FAIL: BASE_1DOOR nema sarki"
    n_sarke_m1 = int(sarke_m1.iloc[0]["Kol."])
    if n_sarke_m1 != 2:
        return False, f"FAIL: BASE_1DOOR treba 2 sarke, dobijeno {n_sarke_m1}"
    rucke_m1 = m1_hw[m1_hw["Naziv"].str.contains("pull", na=False)]
    if rucke_m1.empty or int(rucke_m1.iloc[0]["Kol."]) != 1:
        n = int(rucke_m1.iloc[0]["Kol."]) if not rucke_m1.empty else 0
        return False, f"FAIL: BASE_1DOOR treba 1 rucku, dobijeno {n}"

    # M2: WALL_2DOOR — 4 sarke (2 vrata × 2 sarke/vrata za h=720), 2 rucke
    m2_hw = okovi[okovi["ID"] == 2]
    sarke_m2 = m2_hw[m2_hw["Naziv"].str.contains("arka", na=False)]
    if sarke_m2.empty:
        return False, "FAIL: WALL_2DOOR nema sarki"
    n_sarke_m2 = int(sarke_m2.iloc[0]["Kol."])
    if n_sarke_m2 != 4:
        return False, f"FAIL: WALL_2DOOR treba 4 sarke, dobijeno {n_sarke_m2}"
    rucke_m2 = m2_hw[m2_hw["Naziv"].str.contains("pull", na=False)]
    if rucke_m2.empty or int(rucke_m2.iloc[0]["Kol."]) != 2:
        n = int(rucke_m2.iloc[0]["Kol."]) if not rucke_m2.empty else 0
        return False, f"FAIL: WALL_2DOOR treba 2 rucke, dobijeno {n}"

    # M3: BASE_DRAWERS_3 — 3 klizaca, 3 rucke
    m3_hw = okovi[okovi["ID"] == 3]
    klizaci = m3_hw[m3_hw["Naziv"].str.contains("za fioku", na=False)]
    if klizaci.empty or int(klizaci.iloc[0]["Kol."]) != 3:
        n = int(klizaci.iloc[0]["Kol."]) if not klizaci.empty else 0
        return False, f"FAIL: BASE_DRAWERS_3 treba 3 klizaca, dobijeno {n}"
    rucke_m3 = m3_hw[m3_hw["Naziv"].str.contains("pull", na=False)]
    if rucke_m3.empty or int(rucke_m3.iloc[0]["Kol."]) != 3:
        n = int(rucke_m3.iloc[0]["Kol."]) if not rucke_m3.empty else 0
        return False, f"FAIL: BASE_DRAWERS_3 treba 3 rucke, dobijeno {n}"

    # M4: WALL_LIFTUP — 1 liftup par, 1 rucka
    m4_hw = okovi[okovi["ID"] == 4]
    liftup = m4_hw[m4_hw["Naziv"].str.contains("ift", na=False)]
    if liftup.empty or int(liftup.iloc[0]["Kol."]) != 1:
        n = int(liftup.iloc[0]["Kol."]) if not liftup.empty else 0
        return False, f"FAIL: WALL_LIFTUP treba 1 liftup, dobijeno {n}"
    rucke_m4 = m4_hw[m4_hw["Naziv"].str.contains("pull", na=False)]
    if rucke_m4.empty or int(rucke_m4.iloc[0]["Kol."]) != 1:
        n = int(rucke_m4.iloc[0]["Kol."]) if not rucke_m4.empty else 0
        return False, f"FAIL: WALL_LIFTUP treba 1 rucku, dobijeno {n}"

    return True, "OK"


    ok, err = smoke_all_template_previews()
    print(f"TEMPLATE_PREVIEWS_OK={ok}")
    print(f"TEMPLATE_PREVIEWS_ERR={err}")
    panel_ok, panel_msg = smoke_palette_scope_and_panel_previews()
    print(f"PALETTE_PANEL_OK={panel_ok}")
    print(f"PALETTE_PANEL_MSG={panel_msg}")
    mixed_ok, mixed_msg = smoke_mixed_appliance_previews()
    print(f"MIXED_APPLIANCE_PREVIEWS_OK={mixed_ok}")
    print(f"MIXED_APPLIANCE_PREVIEWS_MSG={mixed_msg}")
    upper_ok, upper_msg = smoke_upper_appliance_previews()
    print(f"UPPER_APPLIANCE_PREVIEWS_OK={upper_ok}")
    print(f"UPPER_APPLIANCE_PREVIEWS_MSG={upper_msg}")
    active_ok, active_msg = smoke_active_kitchen_palette_previews()
    print(f"ACTIVE_KITCHEN_PALETTE_PREVIEWS_OK={active_ok}")
    print(f"ACTIVE_KITCHEN_PALETTE_PREVIEWS_MSG={active_msg}")
    parity_ok, parity_msg = smoke_representative_render_cutlist_parity()
    print(f"RENDER_CUTLIST_PARITY_OK={parity_ok}")
    print(f"RENDER_CUTLIST_PARITY_MSG={parity_msg}")
    qty_ok, qty_msg = smoke_front_and_drawer_quantities()
    print(f"FRONT_DRAWER_QUANTITIES_OK={qty_ok}")
    print(f"FRONT_DRAWER_QUANTITIES_MSG={qty_msg}")
    sfront_ok, sfront_msg = smoke_special_front_types()
    print(f"SPECIAL_FRONT_TYPES_OK={sfront_ok}")
    print(f"SPECIAL_FRONT_TYPES_MSG={sfront_msg}")
    valid, msg = smoke_add_edit_layout()
    print(f"LAYOUT_AUDIT_OK={valid}")
    print(f"LAYOUT_AUDIT_MSG={msg}")
    room_ok, room_msg = smoke_room_openings_walls()
    print(f"ROOM_OPENINGS_WALLS_OK={room_ok}")
    print(f"ROOM_OPENINGS_WALLS_MSG={room_msg}")
    grid_ok, grid_msg = smoke_grid_modes()
    print(f"GRID_MODES_OK={grid_ok}")
    print(f"GRID_MODES_MSG={grid_msg}")
    block_ok, block_msg = smoke_blocking_validations()
    print(f"BLOCKING_VALIDATIONS_OK={block_ok}")
    print(f"BLOCKING_VALIDATIONS_MSG={block_msg}")
    update_ok, update_msg = smoke_update_validations()
    print(f"UPDATE_VALIDATIONS_OK={update_ok}")
    print(f"UPDATE_VALIDATIONS_MSG={update_msg}")
    audit_ok, audit_msg = smoke_layout_support_audit()
    print(f"LAYOUT_SUPPORT_AUDIT_OK={audit_ok}")
    print(f"LAYOUT_SUPPORT_AUDIT_MSG={audit_msg}")
    roomc_ok, roomc_msg = smoke_room_constraints()
    print(f"ROOM_CONSTRAINTS_OK={roomc_ok}")
    print(f"ROOM_CONSTRAINTS_MSG={roomc_msg}")
    warn_ok, warn_msg = smoke_warning_generation()
    print(f"WARNING_GENERATION_OK={warn_ok}")
    print(f"WARNING_GENERATION_MSG={warn_msg}")
    shop_ok, shop_msg = smoke_shopping_hardware()
    print(f"SHOPPING_HARDWARE_OK={shop_ok}")
    print(f"SHOPPING_HARDWARE_MSG={shop_msg}")
    fast_ok, fast_msg = smoke_fastener_and_grouping_hardware()
    print(f"FASTENER_GROUPING_OK={fast_ok}")
    print(f"FASTENER_GROUPING_MSG={fast_msg}")
    app_ok, app_msg = smoke_appliance_and_tall_hardware()
    print(f"APPLIANCE_TALL_HARDWARE_OK={app_ok}")
    print(f"APPLIANCE_TALL_HARDWARE_MSG={app_msg}")
    app_prod_ok, app_prod_msg = smoke_appliances_not_listed_as_products()
    print(f"APPLIANCES_NOT_LISTED_OK={app_prod_ok}")
    print(f"APPLIANCES_NOT_LISTED_MSG={app_prod_msg}")
    svc_ok, svc_msg = smoke_service_processing_packet()
    print(f"SERVICE_PROCESSING_OK={svc_ok}")
    print(f"SERVICE_PROCESSING_MSG={svc_msg}")
    pcode_ok, pcode_msg = smoke_partcode_preview_annotations()
    print(f"PARTCODE_PREVIEW_OK={pcode_ok}")
    print(f"PARTCODE_PREVIEW_MSG={pcode_msg}")
    mw_ok, mw_msg = smoke_multiwall_l_basic()
    print(f"MULTIWALL_L_BASIC_OK={mw_ok}")
    print(f"MULTIWALL_L_BASIC_MSG={mw_msg}")
    mwc_ok, mwc_msg = smoke_multiwall_cutlist_segments()
    print(f"MULTIWALL_CUTLIST_OK={mwc_ok}")
    print(f"MULTIWALL_CUTLIST_MSG={mwc_msg}")
    corner_ok, corner_msg = smoke_corner_rules()
    print(f"CORNER_RULES_OK={corner_ok}")
    print(f"CORNER_RULES_MSG={corner_msg}")
    corner_swing_ok, corner_swing_msg = smoke_corner_door_swing_rules()
    print(f"CORNER_DOOR_SWING_OK={corner_swing_ok}")
    print(f"CORNER_DOOR_SWING_MSG={corner_swing_msg}")
    corner_guidance_ok, corner_guidance_msg = smoke_corner_guidance_helper()
    print(f"CORNER_GUIDANCE_OK={corner_guidance_ok}")
    print(f"CORNER_GUIDANCE_MSG={corner_guidance_msg}")
    l_left_ok, l_left_msg = smoke_l_left_corner_mode()
    print(f"L_LEFT_CORNER_OK={l_left_ok}")
    print(f"L_LEFT_CORNER_MSG={l_left_msg}")
    wall_corner_ok, wall_corner_msg = smoke_wall_corner_autoplace()
    print(f"WALL_CORNER_AUTOPLACE_OK={wall_corner_ok}")
    print(f"WALL_CORNER_AUTOPLACE_MSG={wall_corner_msg}")
    diag_corner_ok, diag_corner_msg = smoke_diagonal_corner_preview_distinct()
    print(f"DIAGONAL_CORNER_PREVIEW_OK={diag_corner_ok}")
    print(f"DIAGONAL_CORNER_PREVIEW_MSG={diag_corner_msg}")
    diag_corner_3d_ok, diag_corner_3d_msg = smoke_diagonal_corner_preview_3d_distinct()
    print(f"DIAGONAL_CORNER_PREVIEW_3D_OK={diag_corner_3d_ok}")
    print(f"DIAGONAL_CORNER_PREVIEW_3D_MSG={diag_corner_3d_msg}")
    dd_ok, dd_msg = smoke_door_drawer_preview()
    print(f"DOOR_DRAWER_PREVIEW_OK={dd_ok}")
    print(f"DOOR_DRAWER_PREVIEW_MSG={dd_msg}")
    cook_ok, cook_msg = smoke_cooking_unit_drawer()
    print(f"COOKING_UNIT_DRAWER_OK={cook_ok}")
    print(f"COOKING_UNIT_DRAWER_MSG={cook_msg}")
    co_ok, co_msg = smoke_l_corner_offset_no_collision()
    print(f"L_CORNER_OFFSET_NO_COLLISION_OK={co_ok}")
    print(f"L_CORNER_OFFSET_NO_COLLISION_MSG={co_msg}")
    co2_ok, co2_msg = smoke_l_corner_offset_with_corner_mod()
    print(f"L_CORNER_OFFSET_WITH_CORNER_MOD_OK={co2_ok}")
    print(f"L_CORNER_OFFSET_WITH_CORNER_MOD_MSG={co2_msg}")
    co3_ok, co3_msg = smoke_l_corner_offset_audit_catches_violation()
    print(f"L_CORNER_OFFSET_AUDIT_VIOLATION_OK={co3_ok}")
    print(f"L_CORNER_OFFSET_AUDIT_VIOLATION_MSG={co3_msg}")
