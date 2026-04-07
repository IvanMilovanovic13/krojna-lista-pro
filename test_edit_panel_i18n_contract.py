# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def run_edit_panel_i18n_contract() -> tuple[bool, str]:
    text = Path(__file__).with_name("ui_edit_panel.py").read_text(encoding="utf-8")

    forbidden = [
        "Kuhinjska jedinica",
        "Sudopera - izrez u radnoj ploči",
        "Ploča za kuvanje - izrez u radnoj ploči",
        "Ugradna mašina za sudove",
        "Sortirnik / kante za otpad",
        "Ugaoni donji element",
        "Završna bočna ploča",
        "Visoka kolona za frižider",
        "Visoka kolona za uređaje",
        "click ↺",
        "klikni ↺",
    ]
    hits = [item for item in forbidden if item in text]
    if hits:
        return False, f"FAIL_edit_panel_inline_labels:{', '.join(hits)}"

    required = [
        "_t('edit.cooking_unit_title')",
        "_t('edit.sink_cutout_title')",
        "_t('edit.hob_cutout_title')",
        "_t('edit.dishwasher_title')",
        "_t('edit.trash_title')",
        "_t('edit.corner_title')",
        "_t('edit.end_panel_title')",
        "_t('edit.filler_title')",
        "_t('edit.fridge_title')",
        "_t('edit.tall_appliance_title')",
        "_t('edit.drawer_warn_click_recalc')",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        return False, f"FAIL_edit_panel_missing_i18n:{', '.join(missing)}"

    return True, "OK"


if __name__ == "__main__":
    ok, message = run_edit_panel_i18n_contract()
    print(message)
    raise SystemExit(0 if ok else 1)
