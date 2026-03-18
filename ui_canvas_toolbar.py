# -*- coding: utf-8 -*-
from __future__ import annotations

from i18n import (
    BTN_RESET_PRIKAZA,
    LBL_PRIKAZ,
    LBL_CANVAS,
    LBL_GRID,
    LBL_ZONE,
    LBL_LAJSNA,
    OPT_TEHNICKI,
    OPT_KATALOG,
)


def render_canvas_toolbar(
    ui,
    state,
    nacrt_refresh,
    main_content_refresh,
    set_view_mode,
    set_show_grid,
    set_grid_mm,
    set_show_bounds,
    set_ceiling_filler,
) -> None:
    """Renderuje toolbar iznad 2D/3D canvasa (UI-only, bez promene logike)."""
    _layout_key = str(getattr(state, 'kitchen_layout', '') or '').lower().strip()
    _show_wall_switch = _layout_key in ('l_oblik', 'u_oblik', 'galija')

    with ui.row().classes(
        'canvas-toolbar w-full shrink-0 items-center gap-3 px-3 py-1.5 '
        'bg-white border-b border-gray-200 flex-wrap'
    ):
        if _show_wall_switch:
            _active_wall = str((getattr(state, 'room', {}) or {}).get('active_wall', 'A') or 'A').upper()

            def _switch_wall(wk: str) -> None:
                state.room['active_wall'] = str(wk).upper()
                state.selected_edit_id = 0
                state.mode = 'add'
                main_content_refresh()

            ui.label('Zid').classes('text-xs text-gray-500 font-medium shrink-0')
            for _wk in ('A', 'B', 'C'):
                _is_active = _wk == _active_wall
                _btn_cls = 'text-xs px-2 py-0.5'
                if _is_active:
                    ui.button(
                        f'Zid {_wk}',
                        on_click=lambda wk=_wk: _switch_wall(wk),
                    ).props('dense color=dark').classes(_btn_cls)
                else:
                    ui.button(
                        f'Zid {_wk}',
                        on_click=lambda wk=_wk: _switch_wall(wk),
                    ).props('dense outline color=dark').classes(_btn_cls)
            ui.separator().props('vertical').classes('h-5 mx-1 bg-gray-200')

        ui.label(LBL_PRIKAZ).classes('text-xs text-gray-500 font-medium shrink-0')
        ui.select(
            [OPT_TEHNICKI, OPT_KATALOG], value=state.view_mode,
            on_change=lambda e: (set_view_mode(e.value), nacrt_refresh())
        ).classes('w-36').props('dense outlined options-dense')
        ui.separator().props('vertical').classes('h-5 mx-1 bg-gray-200')
        _is_catalog = str(state.view_mode).strip().lower() == str(OPT_KATALOG).strip().lower()
        if _is_catalog:
            ui.checkbox(
                LBL_GRID, value=state.show_grid,
                on_change=lambda e: (set_show_grid(e.value), nacrt_refresh())
            ).classes('text-xs').props('color=dark')
            ui.select(
                [1, 5, 10], value=state.grid_mm,
                on_change=lambda e: (set_grid_mm(e.value), nacrt_refresh())
            ).classes('w-20').props('dense outlined options-dense')
        else:
            ui.label('Mreza je aktivna samo u Katalog prikazu').classes('text-xs text-gray-400')
        ui.separator().props('vertical').classes('h-5 mx-1 bg-gray-200')
        ui.checkbox(
            LBL_ZONE, value=state.show_bounds,
            on_change=lambda e: (set_show_bounds(e.value), nacrt_refresh())
        ).classes('text-xs').props('color=dark')
        ui.checkbox(
            LBL_LAJSNA, value=state.ceiling_filler,
            on_change=lambda e: (set_ceiling_filler(e.value), nacrt_refresh())
        ).classes('text-xs').props('color=dark')
        ui.button(
            BTN_RESET_PRIKAZA,
            on_click=nacrt_refresh
        ).props('dense outline color=dark').classes('text-xs')
        ui.separator().props('vertical').classes('h-5 mx-1 bg-gray-200')
        ui.label(LBL_CANVAS).classes('text-xs text-gray-500 font-medium shrink-0')
        ui.select(
            ['2D', '3D'],
            value=str(getattr(state, 'element_canvas_mode', '2D') or '2D') if str(getattr(state, 'element_canvas_mode', '2D') or '2D') in ('2D', '3D') else '2D',
            on_change=lambda e: (
                setattr(state, 'element_canvas_mode', str(e.value or '2D')),
                main_content_refresh(),
            ),
        ).classes('w-24').props('dense outlined options-dense')
