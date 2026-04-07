# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any
import logging
from i18n import tr

_LOG = logging.getLogger(__name__)


_COLOR_PRESET_NAMES_EN = {
    "Beli dekor": "White decor",
    "Svetli drvni dekor": "Light wood decor",
    "Bukva": "Beech",
    "Jela": "Fir",
    "Hrast": "Oak",
    "Bor": "Pine",
    "Aris": "Aris",
    "Mahagoni": "Mahogany",
    "Tresnja": "Cherry",
    "Kesten": "Chestnut",
    "Tik": "Teak",
    "Palisander": "Rosewood",
    "Orah": "Walnut",
    "Maslina": "Olive",
    "Zelena": "Green",
    "Bagrem": "Acacia",
    "Ebanovina": "Ebony",
}
_COLOR_PRESET_NAMES_SR = {str(v): str(k) for k, v in _COLOR_PRESET_NAMES_EN.items()}


def _translate_preset_name(name: str, lang: str) -> str:
    txt = str(name or "")
    if str(lang or "sr").lower().strip() == "en":
        return _COLOR_PRESET_NAMES_EN.get(txt, txt)
    return _COLOR_PRESET_NAMES_SR.get(txt, txt)


def is_dark_hex(hex_c: str) -> bool:
    """True ako je boja tamna (brightness < 140) - za kontrast teksta."""
    h = str(hex_c).lstrip("#")
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return (r * 299 + g * 587 + b * 114) / 1000 < 140
    except Exception as ex:
        _LOG.debug("Invalid hex color '%s': %s", hex_c, ex)
        return False


def render_color_picker(
    *,
    ui: Any,
    presets: list[dict],
    color_ref: dict,
    title: str = "Boja fronta",
    columns: int = 4,
    swatch_h: int = 28,
    lang: str = "sr",
) -> None:
    """Renderuje color/dekor picker u trenutnom NiceGUI kontekstu."""
    _preview = [None]
    _default_hex = "#FDFDFB"

    def _pick(hex_c: str) -> None:
        if not hex_c:
            hex_c = _default_hex
        color_ref["value"] = hex_c
        _cb = color_ref.get("_on_change")
        if callable(_cb):
            _cb()
        if _preview[0] is None:
            return
        fg = "#fff" if is_dark_hex(hex_c) else "#222"
        _preview[0].set_text(hex_c)
        _preview[0].style(
            f"display:inline-block;padding:1px 7px;border-radius:3px;font-size:10px;"
            f"background:{hex_c};color:{fg};border:1px solid #bbb;font-family:monospace;"
        )

    with ui.column().classes("w-full gap-1 mt-1 px-1.5 py-1 border border-gray-200 rounded bg-gray-50"):
        with ui.row().classes("w-full items-center gap-2 mb-1"):
            ui.label(title).classes("text-xs font-semibold text-gray-600 shrink-0")
            _init = str(color_ref.get("value", _default_hex) or _default_hex)
            _init_fg = "#fff" if is_dark_hex(_init) else "#222"
            _preview[0] = ui.label(_init).style(
                f"display:inline-block;padding:1px 7px;border-radius:3px;font-size:10px;"
                f"background:{_init};color:{_init_fg};border:1px solid #bbb;font-family:monospace;"
            )

        _selected = str(color_ref.get("value", _default_hex) or _default_hex).upper()
        with ui.element("div").style(
            f"display:grid;grid-template-columns:repeat({max(2, int(columns))},minmax(0,1fr));gap:6px;width:100%;"
        ):
            for _entry in presets:
                _hex = str(_entry.get("hex", "") or "").strip()
                _name = _translate_preset_name(str(_entry.get("name", "") or "").strip(), lang)
                _bg = str(_entry.get("swatch", _hex) or _hex).strip()
                _sel = _selected == _hex.upper()
                _border = "2px solid #111" if _sel else "1px solid #c7c7c7"
                with ui.element("div").classes("w-full").style(
                    "display:flex;flex-direction:column;align-items:center;gap:3px;"
                ):
                    ui.element("div").style(
                        f"width:100%;height:{max(22, int(swatch_h))}px;border-radius:6px;cursor:pointer;"
                        f"background:{_bg};border:{_border};"
                        "box-shadow:inset 0 0 0 1px rgba(255,255,255,0.20);"
                    ).on("click", lambda h=_hex: _pick(h)).tooltip(f"{_name} ({_hex})")
                    ui.label(_name).classes(
                        "text-[10px] text-gray-700 text-center leading-tight"
                    ).style("max-width:100%;")

        with ui.row().classes("w-full items-center gap-1 mt-1"):
            ui.button(tr("common.cancel", lang), on_click=lambda: _pick(_default_hex)).props("dense flat").classes(
                "text-xs text-gray-400 px-1"
            ).tooltip(tr("common.cancel", lang))
            _custom_inp = ui.input(placeholder="#RRGGBB").props(
                "dense outlined"
            ).classes("flex-1 text-xs font-mono")
            if color_ref.get("value"):
                _custom_inp.value = color_ref["value"]
            ui.button(tr("edit.apply", lang), on_click=lambda: _pick(str(_custom_inp.value).strip())).props(
                "dense flat"
            ).classes("text-xs px-1 text-gray-700").tooltip(tr("edit.apply", lang))
