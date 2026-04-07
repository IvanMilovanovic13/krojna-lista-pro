# -*- coding: utf-8 -*-
from __future__ import annotations

from test_export_consistency import build_sample_kitchen
from ui_assembly import assembly_instructions


def run_assembly_language_polish_check() -> tuple[bool, str]:
    kitchen = build_sample_kitchen()
    modules = {module["template_id"]: module for module in kitchen["modules"]}

    sr_expected = {
        "BASE_2DOOR": ["Leva bočna ploča", "Leđna ploča", "Nosač radne ploče"],
        "SINK_BASE": ["Vrata ispod sudopere", "Gornja puna ploča se ne ugrađuje", "radnoj ploči obeležite otvor"],
        "BASE_COOKING_UNIT": ["Leva bočna ploča", "Gornja ploča", "šablonu ploče za kuvanje"],
    }
    sr_forbidden = ["bocna ploca", "ledjna ploca", "radnoj ploci", "montaze sudopere", "pre secenja"]

    for template_id, expected_parts in sr_expected.items():
        text = "\n".join(
            assembly_instructions(template_id, modules[template_id]["zone"], m=modules[template_id], kitchen=kitchen, lang="sr")
        )
        lowered = text.lower()
        for expected in expected_parts:
            if expected not in text:
                return False, f"sr_missing:{template_id}:{expected}"
        for bad in sr_forbidden:
            if bad in lowered:
                return False, f"sr_unpolished:{template_id}:{bad}"

    en_text = "\n".join(
        assembly_instructions("SINK_BASE", modules["SINK_BASE"]["zone"], m=modules["SINK_BASE"], kitchen=kitchen, lang="en")
    )
    en_expected = ["Left side panel", "Back panel", "worktop", "Do not fit a full top panel", "Run water and check whether the trap, tap and all connections leak."]
    for expected in en_expected:
        if expected not in en_text:
            return False, f"en_missing:{expected}"

    return True, "ok"
