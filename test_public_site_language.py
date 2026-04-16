# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def run_public_site_language_check() -> tuple[bool, str]:
    path = Path(__file__).with_name("ui_public_site.py")
    text = path.read_text(encoding="utf-8")

    forbidden = [
        'ui.button("Pricing"',
        'ui.button("Pocetna"',
        "desnom dugmetu 'Nalog'",
        "2. Kliknes desno na 'Nalog'",
        "trenutni auth ekran je u aplikaciji",
    ]
    hits = [item for item in forbidden if item in text]
    if hits:
        return False, f"FAIL_public_site_mixed_labels:{', '.join(hits)}"

    required = [
        'from i18n import get_language_options, tr',
        'def _tr(key: str, **fmt: object) -> str:',
        'ui.button(_tr("public.home_btn")',
        '_topbar(action_label=_tr("public.login_btn"), action_target="/login", current_path="/pricing")',
        'def _split_brand_title() -> tuple[str, str]:',
        'def _hero_brand(caption: str = "") -> None:',
        'brand_main, brand_badge = _split_brand_title()',
        'ui.label(brand_main).classes(',
        '_hero_brand("Dashboard / Projekti")',
        'ui.label(_tr("public.login_title"))',
        'ui.label(_tr("public.sign_in_card_title"))',
        'ui.label(_tr("public.register_title"))',
        'ui.label(_tr("public.sign_up_card_title"))',
        'ui.button(_tr("public.sign_in_btn"), on_click=_login)',
        'ui.button(_tr("public.sign_up_btn"), on_click=_register)',
        'ui.navigate.to("/app")',
    ]
    missing = [item for item in required if item not in text]
    if missing:
        return False, f"FAIL_public_site_missing_labels:{', '.join(missing)}"

    return True, "OK"
