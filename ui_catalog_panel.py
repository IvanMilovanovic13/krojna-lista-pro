# -*- coding: utf-8 -*-
from __future__ import annotations

import base64
from typing import Any, Dict

from ui_catalog_config import translate_palette_label, translate_template_label

_ICON_PREVIEW_CACHE: dict[str, str] = {}
_ICON_PREVIEW_CACHE_VERSION = "v6"
_CATALOG_2D_PRIORITY_TIDS = {
    # Panels and mixed appliance modules are easier to understand in 2D front view.
    "SINK_BASE",
    "BASE_HOB",
    "BASE_COOKING_UNIT",
    "BASE_DISHWASHER",
    "BASE_OPEN",
    "BASE_NARROW",
    "BASE_CORNER",
    "BASE_CORNER_DIAGONAL",
    "WALL_OPEN",
    "WALL_UPPER_OPEN",
    "WALL_CORNER_DIAGONAL",
    "FILLER_PANEL",
    "END_PANEL",
    "WALL_GLASS",
    "WALL_HOOD",
    "WALL_LIFTUP",
    "WALL_MICRO",
    "WALL_NARROW",
    "WALL_CORNER",
    "TALL_OPEN",
    "TALL_TOP_OPEN",
    "TALL_OVEN",
    "TALL_OVEN_MICRO",
    "TALL_FRIDGE",
    "TALL_FRIDGE_FREEZER",
    "BASE_OVEN_HOB_FREESTANDING",
    "BASE_DISHWASHER_FREESTANDING",
}

_PALETTE_IMAGE_PRIORITY_TIDS = {
    "BASE_OVEN_HOB_FREESTANDING",
    "BASE_DISHWASHER_FREESTANDING",
}


def select_template(*, state, tid: str, render_variants_refresh, params_panel_refresh) -> None:
    state.selected_tid = tid
    render_variants_refresh()
    params_panel_refresh()


def render_palette(*, ui, render_variants_fn) -> None:
    """Render only variant list body (without tab strip)."""
    with ui.column().classes('w-full px-2 pb-2 gap-0'):
        render_variants_fn()


def render_variants(
    *,
    ui,
    state,
    templates,
    palette_tab_map,
    svg_for_tid,
    render_element_preview_fn,
    on_select_template,
) -> None:
    _lang = str(getattr(state, "language", "sr") or "sr").lower().strip()

    def _svg_markup_to_data_uri(svg_markup: str) -> str | None:
        raw = str(svg_markup or "").strip()
        if not raw.lower().startswith("<svg"):
            return None
        encoded = base64.b64encode(raw.encode("utf-8")).decode("ascii")
        return f"data:image/svg+xml;base64,{encoded}"

    def _make_preview_uri(tid: str, tmpl: Dict[str, Any]) -> str | None:
        if render_element_preview_fn is None:
            return None
        _front = str((state.kitchen.get('front_color') or state.front_color or '#FDFDFB'))
        _cache_key = f"{_ICON_PREVIEW_CACHE_VERSION}|{tid}|{_front}"
        if _cache_key in _ICON_PREVIEW_CACHE:
            return _ICON_PREVIEW_CACHE[_cache_key]
        try:
            _features = tmpl.get('features', {}) or {}
            _params: Dict[str, Any] = {}
            if _features.get('n_drawers') is not None:
                _params['n_drawers'] = int(_features.get('n_drawers') or 0)
            if _features.get('open') or _features.get('pantry') or _features.get('doors'):
                _params['n_shelves'] = int(_features.get('n_shelves', 3) or 3)
            if _features.get('oven'):
                _params['oven_h'] = 595
            _m = {
                'id': 0,
                'template_id': tid,
                'label': tmpl.get('label', tid),
                'zone': tmpl.get('zone', 'base'),
                'x_mm': 0,
                'w_mm': int(tmpl.get('w_mm', 600)),
                'h_mm': int(tmpl.get('h_mm', 720)),
                'd_mm': int(tmpl.get('d_mm', 560)),
                'gap_after_mm': 0,
                'params': _params,
            }
            _uri_2d, _uri_3d = render_element_preview_fn(_m, state.kitchen)
            if tid in _CATALOG_2D_PRIORITY_TIDS:
                _uri = _uri_2d or _uri_3d
            else:
                _uri = _uri_3d or _uri_2d
            if _uri:
                _ICON_PREVIEW_CACHE[_cache_key] = _uri
                return _uri
        except Exception:
            return None
        return None

    active_key = state.active_group if state.active_group in palette_tab_map else "donji"
    tab = palette_tab_map[active_key]

    for sg in tab["subgroups"]:
        sg_tids = [t for t in sg["tids"] if templates.get(t)]
        if not sg_tids:
            continue
        ui.label(translate_palette_label(sg["label"], _lang)).classes(
            'text-[9px] font-bold uppercase tracking-widest '
            'text-gray-400 px-1 pt-3 pb-1 w-full'
        )
        for tid in sg_tids:
            tmpl = templates.get(tid)
            if not tmpl:
                continue
            label = translate_template_label(tmpl.get("label", tid), _lang, tmpl.get("label_i18n"))
            is_selected = state.selected_tid == tid
            if is_selected:
                row_cls = (
                    'w-full items-center gap-2 px-2 py-1.5 rounded cursor-pointer '
                    'bg-gray-50 border border-gray-400 shadow-sm'
                )
                lbl_cls = 'text-[12px] font-semibold text-gray-800 leading-tight'
            else:
                row_cls = (
                    'w-full items-center gap-2 px-2 py-1.5 rounded cursor-pointer '
                    'bg-white border border-gray-100 hover:border-gray-300 hover:bg-gray-50'
                )
                lbl_cls = 'text-[12px] font-medium text-gray-700 leading-tight'
            with ui.row().classes(row_cls).on('click', lambda t=tid: on_select_template(t)):
                _preview_uri = _make_preview_uri(tid, tmpl) if tid in _PALETTE_IMAGE_PRIORITY_TIDS else None
                with ui.element('div').style(
                    'width:76px;min-width:76px;height:84px;'
                    'display:flex;align-items:center;justify-content:center;'
                    'padding:4px;border:1px solid #d8d6d2;border-radius:6px;background:#fff;overflow:hidden;'
                ):
                    if _preview_uri:
                        ui.image(_preview_uri).props('fit=contain no-spinner').classes('w-full h-full').style(
                            'width:100%;height:100%;max-width:100%;max-height:100%;display:block;'
                        )
                    else:
                        _svg_html = svg_for_tid(tid)
                        _svg_uri = _svg_markup_to_data_uri(_svg_html)
                        if _svg_uri:
                            ui.image(_svg_uri).props('fit=contain no-spinner').classes('w-full h-full').style(
                                'width:100%;height:100%;max-width:100%;max-height:100%;display:block;'
                            )
                        else:
                            ui.html(_svg_html).style(
                                'width:100%;height:100%;max-width:100%;max-height:100%;'
                                'display:flex;align-items:center;justify-content:center;overflow:hidden;'
                            )
                ui.label(label).classes(lbl_cls)
