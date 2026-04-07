# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def run_ops_access_scope_check() -> tuple[bool, str]:
    ui_panels = Path(__file__).with_name("ui_panels.py").read_text(encoding="utf-8")
    ui_main_content = Path(__file__).with_name("ui_main_content.py").read_text(encoding="utf-8")
    i18n = Path(__file__).with_name("i18n.py").read_text(encoding="utf-8")

    required_ui_panels = [
        'if _tier == "admin":',
        'tabs.insert(5, ("ops", _tr("tab.ops"), "admin_panel_settings"))',
    ]
    missing_ui_panels = [item for item in required_ui_panels if item not in ui_panels]
    if missing_ui_panels:
        return False, f"FAIL_ops_access_ui_panels:{', '.join(missing_ui_panels)}"
    if 'if _tier in ("local_beta", "admin"):' in ui_panels:
        return False, "FAIL_ops_access_local_beta_tab_still_present"

    required_main = [
        'elif state.active_tab == "ops":',
        '_tier != "admin"',
        'nova_tr("ops.denied_title")',
        'nova_tr("ops.denied_desc")',
    ]
    missing_main = [item for item in required_main if item not in ui_main_content]
    if missing_main:
        return False, f"FAIL_ops_access_main_content:{', '.join(missing_main)}"

    required_i18n = [
        '"ops.denied_title": "Ops ekran je dostupan samo administratoru."',
        '"ops.denied_desc": "Ovaj ekran prikazuje globalne runtime, auth i billing podatke i nije dostupan local_beta ili obicnim korisnicima."',
        '"ops.denied_title": "The Ops screen is available only to administrators."',
        '"ops.denied_desc": "This screen shows global runtime, auth, and billing data and is not available to local_beta or regular users."',
    ]
    missing_i18n = [item for item in required_i18n if item not in i18n]
    if missing_i18n:
        return False, f"FAIL_ops_access_i18n:{', '.join(missing_i18n)}"

    return True, "OK"
