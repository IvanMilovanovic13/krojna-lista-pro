# -*- coding: utf-8 -*-
from __future__ import annotations

from ui_cutlist_tab import _friendly_part_name as cutlist_friendly_part_name
from ui_pdf_export import _friendly_part_name as pdf_friendly_part_name


def run_label_cleanup_consistency_check() -> tuple[bool, str]:
    sr_cases = [
        ("Bo\u010dna plo\u010da", "Bočna stranica sanduka fioke"),
        ("Bo\u00c4\u008dna plo\u00c4\u008da", "Bočna stranica sanduka fioke"),
        ("Bocna ploca", "Bočna stranica sanduka fioke"),
        ("Le\u0111a", "Leđna ploča"),
        ("Ledja", "Leđna ploča"),
    ]
    for raw, expected in sr_cases:
        if pdf_friendly_part_name(raw, "sr") != expected:
            return False, f"pdf_sr_cleanup_failed:{raw}"
        if cutlist_friendly_part_name(raw, "sr") != expected:
            return False, f"cutlist_sr_cleanup_failed:{raw}"

    en_cases = [
        ("Bo\u010dna plo\u010da", "Drawer box side"),
        ("Bo\u00c4\u008dna plo\u00c4\u008da", "Drawer box side"),
        ("Le\u0111a", "Back panel"),
    ]
    for raw, expected in en_cases:
        if pdf_friendly_part_name(raw, "en") != expected:
            return False, f"pdf_en_cleanup_failed:{raw}"
        if cutlist_friendly_part_name(raw, "en") != expected:
            return False, f"cutlist_en_cleanup_failed:{raw}"
    return True, "ok"
