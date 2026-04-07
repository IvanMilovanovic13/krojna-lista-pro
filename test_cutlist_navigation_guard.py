# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def run_cutlist_navigation_guard_check() -> tuple[bool, str]:
    navigation = Path(__file__).with_name("ui_navigation.py").read_text(encoding="utf-8")
    panels = Path(__file__).with_name("ui_panels.py").read_text(encoding="utf-8")
    cutlist_tab = Path(__file__).with_name("ui_cutlist_tab.py").read_text(encoding="utf-8")
    state_logic = Path(__file__).with_name("state_logic.py").read_text(encoding="utf-8")

    required_navigation = [
        'if key == "krojna":',
        'from state_logic import get_cutlist_access_state',
        'ui.notify(str(cutlist_access.get("reason", "") or "Krojna lista nije dostupna."), type="warning")',
    ]
    missing_navigation = [item for item in required_navigation if item not in navigation]
    if missing_navigation:
        return False, f"FAIL_navigation_guard:{', '.join(missing_navigation)}"

    required_panels = [
        "get_cutlist_access_state",
        'if str(get_cutlist_access_state().get("allowed", "")).lower() == "true":',
        '("krojna", _tr("tab.cutlist"), "table_rows")',
    ]
    missing_panels = [item for item in required_panels if item not in panels]
    if missing_panels:
        return False, f"FAIL_toolbar_guard:{', '.join(missing_panels)}"

    required_cutlist = [
        "from state_logic import get_cutlist_access_state",
        "tr_fn('cutlist.locked_title')",
        "str(_access.get('reason', '') or tr_fn('cutlist.locked_desc'))",
    ]
    missing_cutlist = [item for item in required_cutlist if item not in cutlist_tab]
    if missing_cutlist:
        return False, f"FAIL_cutlist_gate:{', '.join(missing_cutlist)}"

    if "Free pristup dozvoljava dizajn i cuvanje projekta." not in state_logic:
        return False, "FAIL_state_logic_free_reason"

    return True, "OK"
