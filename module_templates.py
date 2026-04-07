# -*- coding: utf-8 -*-
"""
module_templates.py — Jedini izvor istine za katalog modula.

Čita module_templates.json i izlaže funkcije koje koriste main.py i utils.py.

Da dodaš/izmeniš modul: edituj module_templates.json — bez izmene Python koda.

Napomena (PRO):
- Template može imati "enabled": false da bude sakriven iz UI kataloga,
  ali i dalje može da se učita iz postojećih projekata (backward compat).
"""
from __future__ import annotations

import json
import pathlib
from typing import Any, Dict

_JSON_PATH: pathlib.Path = pathlib.Path(__file__).parent / "module_templates.json"


def _load_all() -> Dict[str, Dict[str, Any]]:
    with open(_JSON_PATH, encoding="utf-8") as f:
        raw: Dict[str, Any] = json.load(f)
    return {k: v for k, v in raw.items() if not k.startswith("_") and isinstance(v, dict)}


_TEMPLATES_ALL: Dict[str, Dict[str, Any]] = _load_all()


def resolve_template(template_id: str) -> Dict[str, Any]:
    """Vraća raw template dict za dati ID. Baca KeyError ako ne postoji."""
    tpl = _TEMPLATES_ALL.get(template_id)
    if not tpl:
        raise KeyError(f"Nepoznat template_id: {template_id!r}. Proveri module_templates.json.")
    return tpl


def get_templates() -> Dict[str, Dict[str, Any]]:
    """
    Vraća UI-friendly dict sa svim modulima koji su ENABLED (default True):
      templates[tid]["label"], ["zone"], ["w_mm"], ["h_mm"], ["d_mm"],
      ["features"], ["icon"], ["face_color"], ["accent_color"], ["texture"]
    """
    out: Dict[str, Dict[str, Any]] = {}
    for tid, tpl in _TEMPLATES_ALL.items():
        # UI filter: skip disabled templates
        if tpl.get("enabled", True) is False:
            continue

        d = tpl.get("defaults") or {}
        vis = tpl.get("visual") or {}
        out[tid] = {
            "id":           tid,
            "label":        tpl.get("label", tid),
            "label_i18n":   tpl.get("label_i18n") or {},
            "zone":         tpl.get("zone", "base"),
            "type":         tpl.get("type", ""),
            "features":     tpl.get("features") or {},
            "params":       tpl.get("params") or {},
            "w_mm":         int(d.get("w_mm", 600)),
            "h_mm":         int(d.get("h_mm", 720)),
            "d_mm":         int(d.get("d_mm", 560)),
            "icon":         vis.get("icon") or "",
            "face_color":   vis.get("face_color"),
            "accent_color": vis.get("accent_color"),
            "texture":      vis.get("texture"),
        }
    return out


def get_template_visual(template_id: str) -> Dict[str, Any]:
    """Vraća visual blok (boje/teksture/ikona) za dati template_id."""
    return dict((resolve_template(template_id) or {}).get("visual") or {})

