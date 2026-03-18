# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from typing import Any, Callable

from i18n import (
    BTN_OTKAZI,
    BTN_PRIMENI,
    SETTINGS_BASE_PARAMS_TITLE,
    SETTINGS_BTN_ONLY_FUTURE,
    SETTINGS_BTN_YES_UPDATE,
    SETTINGS_DEPTH_ALREADY_FMT,
    SETTINGS_DEPTH_DIALOG_ASK,
    SETTINGS_DEPTH_DIALOG_NOTE,
    SETTINGS_DEPTH_DIALOG_TITLE_FMT,
    SETTINGS_DEPTH_STD_DESC,
    SETTINGS_DEPTH_STD_TITLE,
    SETTINGS_FRONT_DECOR_TITLE,
    SETTINGS_GLOBAL_FRONT_DESC,
    SETTINGS_GLOBAL_FRONT_TITLE,
    SETTINGS_MATERIALS_TITLE,
    SETTINGS_NOTIFY_FUTURE_FMT,
    SETTINGS_NOTIFY_UPDATED_FMT,
    SETTINGS_ROOM_DIM_TITLE,
    SETTINGS_TITLE,
    SETTINGS_UPPER_BOTTOM_FMT,
    SETTINGS_UPPER_HEIGHT_FMT,
    SETTINGS_WALL_PARAMS_TITLE,
    SETTINGS_WORKTOP_TOP_EDGE_FMT,
    SETTINGS_ZONE_BASE,
    SETTINGS_ZONE_TALL,
    SETTINGS_ZONE_WALL,
    SETTINGS_ZONE_WALL_UPPER,
)

_LOG = logging.getLogger(__name__)


def render_settings_tab(
    *,
    ui: Any,
    state: Any,
    get_zone_depth_standard: Callable[[str], int],
    set_zone_depth_standard: Callable[[str, int], int],
    nacrt_refresh: Callable[[], None],
    main_content_refresh: Callable[[], None],
    set_front_color: Callable[[str], None],
    set_material: Callable[[str, Any], None],
    set_wall_length: Callable[[int], None],
    set_wall_height: Callable[[int], None],
    set_foot_height: Callable[[int], None],
    set_worktop_thickness: Callable[[float], None],
    set_base_height: Callable[[int], None],
    set_worktop_width: Callable[[float], None],
    set_vertical_gap: Callable[[int], None],
    set_max_element_height: Callable[[int], None],
    render_color_picker: Callable[..., None],
) -> None:
    def _refresh_after_dimension_change() -> None:
        try:
            nacrt_refresh()
        except Exception as ex:
            _LOG.debug("Settings tab: nacrt refresh failed after dimension change: %s", ex)
        main_content_refresh()

    def _on_foot_change(v: Any) -> None:
        set_foot_height(int(v))
        _refresh_after_dimension_change()

    def _on_worktop_thk_change(v: Any) -> None:
        set_worktop_thickness(float(v))
        _refresh_after_dimension_change()

    def _on_base_h_change(v: Any) -> None:
        set_base_height(int(v))
        _refresh_after_dimension_change()

    ui.label(SETTINGS_TITLE).classes('text-2xl font-bold mb-4')
    with ui.row().classes('w-full gap-4 flex-wrap'):
        with ui.card().classes('w-full p-4 mb-2 border border-gray-300 bg-white'):
            ui.label(SETTINGS_DEPTH_STD_TITLE).classes('font-bold text-base mb-1 text-gray-800')
            ui.label(SETTINGS_DEPTH_STD_DESC).classes('text-xs text-gray-500 mb-3')

            _depth_zone_keys = [
                ("base", SETTINGS_ZONE_BASE),
                ("wall", SETTINGS_ZONE_WALL),
                ("wall_upper", SETTINGS_ZONE_WALL_UPPER),
                ("tall", SETTINGS_ZONE_TALL),
            ]

            for _dz_key, _dz_label in _depth_zone_keys:
                _cur_std = get_zone_depth_standard(_dz_key)
                with ui.row().classes('w-full items-center gap-3 mb-2'):
                    ui.label(_dz_label).classes('text-sm font-medium w-48')
                    _dz_inp = ui.number(
                        value=_cur_std, min=100, max=2000, step=10
                    ).props('dense outlined').classes('w-28')
                    _dz_key_cap = _dz_key.upper()

                    def _apply_zone_std(zone_k=_dz_key, zone_lbl=_dz_key_cap, inp=_dz_inp):
                        new_val = int(inp.value)
                        cur_std = get_zone_depth_standard(zone_k)
                        if new_val == cur_std:
                            ui.notify(SETTINGS_DEPTH_ALREADY_FMT.format(zone=zone_lbl, val=new_val), type='info')
                            return
                        with ui.dialog() as _dlg_std:
                            with ui.card().classes('p-4 gap-2 min-w-80'):
                                ui.label(
                                    SETTINGS_DEPTH_DIALOG_TITLE_FMT.format(
                                        zone=zone_lbl, old=cur_std, new=new_val
                                    )
                                ).classes('font-bold text-sm')
                                ui.label(SETTINGS_DEPTH_DIALOG_ASK).classes('text-sm text-gray-600 mt-1')
                                ui.label(SETTINGS_DEPTH_DIALOG_NOTE).classes('text-xs text-gray-400')
                                with ui.row().classes('w-full mt-3 gap-2'):
                                    def _yes(zk=zone_k, nv=new_val, lbl=zone_lbl, dlg=_dlg_std):
                                        n = set_zone_depth_standard(zk, nv, update_existing=True)
                                        dlg.close()
                                        ui.notify(
                                            SETTINGS_NOTIFY_UPDATED_FMT.format(
                                                zone=lbl, val=nv, count=n
                                            ),
                                            type='positive'
                                        )
                                        nacrt_refresh()
                                        main_content_refresh()

                                    def _no(zk=zone_k, nv=new_val, lbl=zone_lbl, dlg=_dlg_std):
                                        set_zone_depth_standard(zk, nv, update_existing=False)
                                        dlg.close()
                                        ui.notify(
                                            SETTINGS_NOTIFY_FUTURE_FMT.format(zone=lbl, val=nv),
                                            type='info'
                                        )
                                        main_content_refresh()

                                    def _cancel_std(dlg=_dlg_std):
                                        dlg.close()

                                    ui.button(SETTINGS_BTN_YES_UPDATE, on_click=_yes).classes('flex-1 text-xs')
                                    ui.button(SETTINGS_BTN_ONLY_FUTURE, on_click=_no).classes(
                                        'flex-1 bg-gray-100 text-xs'
                                    )
                                    ui.button(BTN_OTKAZI, on_click=_cancel_std).classes('text-xs')
                        _dlg_std.open()

            ui.button(BTN_PRIMENI, on_click=_apply_zone_std).props('dense').classes('text-xs px-3 btn-wrap')

    with ui.row().classes('w-full gap-4 flex-wrap'):
        with ui.card().classes('flex-1 min-w-80 p-4'):
            ui.label(SETTINGS_GLOBAL_FRONT_TITLE).classes('font-bold text-base mb-2')
            ui.label(SETTINGS_GLOBAL_FRONT_DESC).classes('text-xs text-gray-500 mb-2')

            _global_color_ref = {
                "value": str(state.front_color or state.kitchen.get("front_color", "#FDFDFB"))
            }

            def _on_global_front_change():
                set_front_color(str(_global_color_ref.get("value", "#FDFDFB")))
                try:
                    nacrt_refresh()
                except Exception as ex:
                    _LOG.debug("Settings tab: nacrt refresh failed after front color change: %s", ex)
                main_content_refresh()

            _global_color_ref["_on_change"] = _on_global_front_change
            render_color_picker(
                _global_color_ref,
                title=SETTINGS_FRONT_DECOR_TITLE,
                columns=6,
                swatch_h=36,
            )

        with ui.card().classes('flex-1 min-w-80 p-4'):
            ui.label(SETTINGS_MATERIALS_TITLE).classes('font-bold text-base mb-3')
            mats = state.kitchen.get('materials', {})

            with ui.row().classes('w-full gap-2'):
                ui.select(
                    ['Iverica', 'MDF', 'Šper ploča', 'Puno drvo'],
                    value=mats.get('carcass_material', 'Iverica'),
                    label='Materijal korpusa',
                    on_change=lambda e: set_material('carcass_material', e.value)
                ).classes('flex-1')
                ui.select(
                    ['MDF', 'Iverica', 'Akril', 'Furnir', 'Lakobel'],
                    value=mats.get('front_material', 'MDF'),
                    label='Materijal fronta',
                    on_change=lambda e: set_material('front_material', e.value)
                ).classes('flex-1')

            with ui.row().classes('w-full gap-2 mt-2'):
                ui.select(
                    [16, 18, 22, 25],
                    value=mats.get('carcass_thk', 18),
                    label='Debljina korpusa [mm]',
                    on_change=lambda e: set_material('carcass_thk', e.value)
                ).classes('flex-1')
                ui.select(
                    [16, 18, 22, 25],
                    value=mats.get('front_thk', 18),
                    label='Debljina fronta [mm]',
                    on_change=lambda e: set_material('front_thk', e.value)
                ).classes('flex-1')

            with ui.row().classes('w-full gap-2 mt-2'):
                ui.select(
                    [3, 4, 6, 8],
                    value=mats.get('back_thk', 8),
                    label='Debljina leđne ploče [mm]',
                    on_change=lambda e: set_material('back_thk', e.value)
                ).classes('flex-1')
                ui.select(
                    [0.4, 1, 2, 3],
                    value=mats.get('edge_abs_thk', 2),
                    label='Debljina ABS trake [mm]',
                    on_change=lambda e: set_material('edge_abs_thk', e.value)
                ).classes('flex-1')

        with ui.card().classes('flex-1 min-w-80 p-4'):
            ui.label(SETTINGS_ROOM_DIM_TITLE).classes('font-bold text-base mb-3')
            with ui.row().classes('w-full gap-2'):
                ui.number(
                    label='Širina zida [mm]',
                    value=state.kitchen.get('wall', {}).get('length_mm', 3000),
                    min=500, max=10000, step=10,
                    on_change=lambda e: set_wall_length(e.value)
                ).classes('flex-1')
                ui.number(
                    label='Visina zida/plafona [mm]',
                    value=state.kitchen.get('wall', {}).get('height_mm', 2600),
                    min=2000, max=3500, step=10,
                    on_change=lambda e: set_wall_height(e.value)
                ).classes('flex-1')

        with ui.card().classes('flex-1 min-w-80 p-4'):
            ui.label(SETTINGS_BASE_PARAMS_TITLE).classes('font-bold text-base mb-3')
            with ui.column().classes('w-full gap-2'):
                ui.number(
                    label='Visina stopice [mm]',
                    value=state.kitchen.get('foot_height_mm', 100),
                    min=0, max=200, step=10,
                    on_change=lambda e: _on_foot_change(e.value)
                ).classes('w-full')
                ui.select(
                    [2.5, 3.0, 3.5, 3.8, 4.0, 4.5, 5.0],
                    value=state.kitchen.get('worktop', {}).get('thickness', 3.8),
                    label='Debljina radne ploče (cm)',
                    on_change=lambda e: _on_worktop_thk_change(e.value)
                ).classes('w-full')
                ui.number(
                    label='Visina korpusa donjih elemenata [mm]',
                    value=state.kitchen.get('base_korpus_h_mm', 720),
                    min=500, max=1000, step=10,
                    on_change=lambda e: _on_base_h_change(e.value)
                ).classes('w-full')
                ui.number(
                    label='Širina radne ploče [mm]',
                    value=state.kitchen.get('worktop', {}).get('width', 600),
                    min=400, max=900, step=10,
                    on_change=lambda e: set_worktop_width(e.value)
                ).classes('w-full')
            foot = state.kitchen.get('foot_height_mm', 100)
            base = state.kitchen.get('base_korpus_h_mm', 720)
            wt = int(round(float(state.kitchen.get('worktop', {}).get('thickness', 3.8)) * 10))
            ui.label(
                SETTINGS_WORKTOP_TOP_EDGE_FMT.format(total=foot + base + wt, foot=foot, base=base, wt=wt)
            ).classes('text-xs text-gray-700 mt-2')

        with ui.card().classes('flex-1 min-w-80 p-4'):
            ui.label(SETTINGS_WALL_PARAMS_TITLE).classes('font-bold text-base mb-3')
            with ui.row().classes('w-full gap-2'):
                ui.number(
                    label='Razmak iznad radne ploče [mm]',
                    value=state.kitchen.get('vertical_gap_mm', 600),
                    min=400, max=1000, step=10,
                    on_change=lambda e: set_vertical_gap(e.value)
                ).classes('flex-1')
                ui.number(
                    label='Maksimalna visina elemenata [mm]',
                    value=state.kitchen.get(
                        'max_element_height',
                        state.kitchen.get('wall', {}).get('height_mm', 2600) - 50,
                    ),
                    min=1000, max=3000, step=10,
                    on_change=lambda e: set_max_element_height(e.value)
                ).classes('flex-1')
            foot = state.kitchen.get('foot_height_mm', 100)
            base = state.kitchen.get('base_korpus_h_mm', 720)
            wt = int(round(float(state.kitchen.get('worktop', {}).get('thickness', 3.8)) * 10))
            gap = state.kitchen.get('vertical_gap_mm', 600)
            wall_bottom = foot + base + wt + gap
            wall_h = state.kitchen.get('wall', {}).get('height_mm', 2600)
            max_h = state.kitchen.get('max_element_height', wall_h - 50)
            ui.label(SETTINGS_UPPER_BOTTOM_FMT.format(val=wall_bottom)).classes('text-xs text-gray-700 mt-1')
            ui.label(
                SETTINGS_UPPER_HEIGHT_FMT.format(h=max_h - wall_bottom, bottom=wall_bottom, max_h=max_h)
            ).classes('text-xs text-gray-700')
