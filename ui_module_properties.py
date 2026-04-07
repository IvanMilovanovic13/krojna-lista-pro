# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Callable
from i18n import tr

from i18n import (
    BTN_OBRISI_ELEMENT,
    BTN_PRIMENI,
    BTN_ZATVORI,
    DEPTH_MODE_CUSTOM,
    DEPTH_MODE_STANDARD,
    GRAIN_HORZ,
    GRAIN_NONE,
    GRAIN_VERT,
    LBL_3D_GRESKA,
    LBL_DUBINA_MM,
    LBL_GAP_MM,
    LBL_KLIKNI_NA_ELEMENT,
    LBL_NAZIV,
    LBL_NAZIV_ELEMENTA_PLACEHOLDER,
    LBL_PANEL_GRESKA,
    LBL_RAZMAK_MM,
    LBL_SIRINA_MM,
    LBL_SMER_GODA,
    LBL_SVOJSTVA,
    LBL_UREDI_ELEMENT,
    LBL_VISINA_MAX_ONLY_FMT,
    LBL_ZA_UREDJIVANJE_OSOBINA,
    NOTIFY_ELEMENT_DELETED,
    NOTIFY_ERROR_FMT,
    SEC_DIMENZIJE,
    SEC_DUBINA_MODE,
    SEC_NAZIV,
    SEC_SMER_GODA,
)
from ui_panels_helpers import format_user_error
from ui_catalog_config import translate_template_label


def render_module_properties_panel(
    *,
    ui: Any,
    state: Any,
    logger: Any,
    nacrt_refresh: Callable[[], None],
    sidebar_refresh: Callable[[], None],
    max_allowed_h_for_zone: Callable[[str], int],
    render_element_preview: Callable[[dict, dict], tuple[str, str]],
    update_module_local: Callable[..., Any],
    delete_module_local: Callable[[int], Any],
    solve_layout: Callable[..., Any],
) -> None:
    _lang = str(getattr(state, 'language', 'sr') or 'sr').lower().strip()
    def _t(key: str, **fmt: object) -> str:
        return tr(key, _lang, **fmt)
    try:
        _module_properties_panel_inner(
            ui=ui,
            state=state,
            _tr_fn=_t,
            logger=logger,
            nacrt_refresh=nacrt_refresh,
            sidebar_refresh=sidebar_refresh,
            max_allowed_h_for_zone=max_allowed_h_for_zone,
            render_element_preview=render_element_preview,
            update_module_local=update_module_local,
            delete_module_local=delete_module_local,
            solve_layout=solve_layout,
        )
    except Exception as panel_err:
        import traceback as tb
        tb.print_exc()
        with ui.column().classes('w-full p-4 gap-2'):
            ui.icon('error').classes('text-3xl text-red-400')
            ui.label(LBL_PANEL_GRESKA).classes('text-xs font-bold text-red-500')
            ui.label(str(panel_err)).classes('text-xs text-red-400 break-all')


def _module_properties_panel_inner(
    *,
    ui: Any,
    state: Any,
    _tr_fn: Callable[..., str],
    logger: Any,
    nacrt_refresh: Callable[[], None],
    sidebar_refresh: Callable[[], None],
    max_allowed_h_for_zone: Callable[[str], int],
    render_element_preview: Callable[[dict, dict], tuple[str, str]],
    update_module_local: Callable[..., Any],
    delete_module_local: Callable[[int], Any],
    solve_layout: Callable[..., Any],
) -> None:
    _lang = str(getattr(state, 'language', 'sr') or 'sr').lower().strip()
    def _txt(sr: str, en: str) -> str:
        return en if _lang == 'en' else sr

    if state.selected_edit_id <= 0:
        with ui.column().classes(
            'w-full h-full flex flex-col items-center justify-center p-6 gap-3'
        ):
            ui.icon('ads_click').classes('text-5xl text-gray-200')
            ui.label(LBL_KLIKNI_NA_ELEMENT).classes(
                'text-sm font-semibold text-gray-400 text-center mt-1'
            )
            ui.label(LBL_ZA_UREDJIVANJE_OSOBINA).classes(
                'text-xs text-gray-300 text-center'
            )
        return

    mods = state.kitchen.get('modules', []) or []
    m = next((mm for mm in mods if int(mm.get('id', -1)) == state.selected_edit_id), None)
    if not m:
        state.selected_edit_id = 0
        state.mode = "add"
        return

    mid = state.selected_edit_id
    zone_m = str(m.get('zone', 'base')).lower()
    max_h = max_allowed_h_for_zone(zone_m)
    params = m.get('params') or {}

    zone_badge = {
        'base': (_txt('Donji', 'Base'), '#DCFCE7', '#166534'),
        'wall': (_txt('Gornji', 'Wall'), '#DBEAFE', '#1E40AF'),
        'wall_upper': (_txt('Gornji+', 'Wall+'), '#CFFAFE', '#155E75'),
        'tall': (_txt('Visoki', 'Tall'), '#F3E8FF', '#6B21A8'),
    }.get(zone_m, (zone_m.upper(), '#F3F4F6', '#374151'))

    cur_grain = str(params.get('grain_dir', 'V') or 'V').upper()
    if cur_grain not in ('H', 'V', 'N'):
        cur_grain = 'V'

    cur_dm = str(params.get('depth_mode', m.get('depth_mode', 'STANDARD'))).upper()
    if cur_dm not in ('STANDARD', 'CUSTOM'):
        cur_dm = 'STANDARD'
    cur_tid = str(m.get('template_id', '')).upper()
    is_wardrobe = bool(params.get('wardrobe', False)) or ('WARDROBE' in cur_tid)
    _s_min, _s_max = (0, 12)
    _d_min, _d_max = (0, 8)
    _h_min, _h_max = (0, 3)
    _th_min, _th_max = (120, max_h)
    _th_max = max(_th_min, min(_th_max, max_h))

    uri_3d = None
    uri_3d_err = None
    try:
        uri_3d = render_element_preview(m, state.kitchen)[1]
    except Exception as e3d:
        uri_3d_err = str(e3d)

    with ui.column().classes('w-full h-full flex flex-col overflow-hidden bg-white'):
        with ui.element('div').classes(
            'px-4 py-3 bg-gray-50 border-b border-gray-200 shrink-0'
        ):
            with ui.row().classes('w-full items-center justify-between'):
                with ui.row().classes('items-center gap-2'):
                    zl, zbg, ztxt = zone_badge
                    ui.element('span').classes('text-[10px] font-bold px-2 py-0.5 rounded').style(
                        f'background:{zbg};color:{ztxt};'
                    ).text = zl
                    ui.label(_txt('Svojstva', 'Properties')).classes('text-sm font-bold text-gray-700')
                ui.button(
                    icon='close',
                    on_click=lambda: (
                        setattr(state, 'selected_edit_id', 0),
                        setattr(state, 'mode', 'add'),
                        nacrt_refresh(),
                        sidebar_refresh(),
                    )
                ).props('flat round dense').classes('text-gray-400')
            tmpl_label = translate_template_label(str(m.get('label', m.get('template_id', '?'))), _lang)
            ui.label(tmpl_label).classes('text-xs text-gray-500 mt-0.5 truncate w-full')
            dims_txt = f"{m.get('w_mm','?')} x {m.get('h_mm','?')} x {m.get('d_mm','?')} mm"
            ui.label(dims_txt).classes('text-[10px] text-gray-400 font-mono mt-0.5')

        if uri_3d:
            with ui.element('div').classes('w-full px-3 pt-3 pb-1 shrink-0 bg-gray-50'):
                ui.image(uri_3d).classes('w-full rounded').style(
                    'border:1px solid #E5E7EB; border-radius:6px; display:block;'
                )
        elif uri_3d_err:
            with ui.element('div').classes('px-3 pt-2 pb-1 shrink-0'):
                ui.label(f'{LBL_3D_GRESKA}: {uri_3d_err}').classes(
                    'text-[10px] text-red-400 font-mono break-all'
                )

        with ui.scroll_area().classes('flex-1 w-full'):
            with ui.column().classes('p-4 gap-5 w-full'):
                wardrobe_front_sel = None
                wardrobe_door_mode_sel = None
                wardrobe_shelves_inp = None
                wardrobe_shelves_sld = None
                wardrobe_drawers_inp = None
                wardrobe_drawers_sld = None
                wardrobe_hangers_inp = None
                wardrobe_hangers_sld = None
                sec_left_pct = None
                sec_left_pct_sld = None
                sec_center_pct = None
                sec_center_pct_sld = None
                sec_right_pct = None
                sec_right_pct_sld = None
                sec_top_h = None
                sec_top_h_sld = None
                sec_left_shelves = None
                sec_left_shelves_sld = None
                sec_left_drawers = None
                sec_left_drawers_sld = None
                sec_center_hangers = None
                sec_center_hangers_sld = None
                sec_right_shelves = None
                sec_right_shelves_sld = None
                sec_right_drawers = None
                sec_right_drawers_sld = None
                sec_right_hangers = None
                sec_right_hangers_sld = None
                sec_top_shelves = None
                sec_top_shelves_sld = None
                sec_locked = None

                with ui.column().classes('w-full gap-1.5'):
                    ui.label(_txt('Naziv', 'Name')).classes(
                        'text-[9px] font-bold uppercase tracking-widest text-gray-400'
                    )
                    lbl_inp = ui.input(
                        value=str(m.get('label', '')),
                        placeholder=_txt('Naziv elementa', 'Unit name'),
                    ).props('outlined dense').classes('w-full')

                with ui.column().classes('w-full gap-1.5'):
                    ui.label(_txt('Dimenzije', 'Dimensions')).classes(
                        'text-[9px] font-bold uppercase tracking-widest text-gray-400'
                    )
                    with ui.grid(columns=2).classes('w-full gap-2'):
                        with ui.column().classes('gap-0.5'):
                            ui.label(_txt('Širina [mm]', 'Width [mm]')).classes('text-[10px] text-gray-500')
                            w_inp = ui.number(
                                value=int(m.get('w_mm', 0)),
                                min=100, max=3000, step=10,
                            ).props('outlined dense').classes('w-full')
                        with ui.column().classes('gap-0.5'):
                            ui.label(_txt(f'Visina ≤{max_h}', f'Height ≤{max_h}')).classes('text-[10px] text-gray-500')
                            h_inp = ui.number(
                                value=min(int(m.get('h_mm', 0)), max_h),
                                min=100, max=max_h, step=10,
                            ).props('outlined dense').classes('w-full')
                        with ui.column().classes('gap-0.5'):
                            ui.label(_txt('Dubina [mm]', 'Depth [mm]')).classes('text-[10px] text-gray-500')
                            d_inp = ui.number(
                                value=int(m.get('d_mm', 0)),
                                min=100, max=2000, step=10,
                            ).props('outlined dense').classes('w-full')
                        with ui.column().classes('gap-0.5'):
                            ui.label(_txt('Razmak [mm]', 'Gap [mm]')).classes('text-[10px] text-gray-500')
                            g_inp = ui.number(
                                value=int(m.get('gap_after_mm', 0)),
                                min=0, max=500, step=1,
                            ).props('outlined dense').classes('w-full')

                with ui.column().classes('w-full gap-1.5'):
                    ui.label(_txt('Režim dubine', 'Depth mode')).classes(
                        'text-[9px] font-bold uppercase tracking-widest text-gray-400'
                    )
                    depth_mode_sel = ui.select(
                        {'STANDARD': DEPTH_MODE_STANDARD, 'CUSTOM': DEPTH_MODE_CUSTOM},
                        value=cur_dm,
                    ).props('outlined dense').classes('w-full')

                with ui.column().classes('w-full gap-1.5'):
                    ui.label(_txt('Smer goda', 'Grain direction')).classes(
                        'text-[9px] font-bold uppercase tracking-widest text-gray-400'
                    )
                    grain_sel = ui.select(
                        {'V': GRAIN_VERT, 'H': GRAIN_HORZ, 'N': GRAIN_NONE},
                        value=cur_grain,
                    ).props('outlined dense').classes('w-full')

                if is_wardrobe:
                    with ui.column().classes('w-full gap-1.5'):
                        ui.label(_tr_fn('elements.wardrobe_layout')).classes(
                            'text-[9px] font-bold uppercase tracking-widest text-gray-400'
                        )
                        wardrobe_front_sel = ui.select(
                            {'doors': _tr_fn('elements.front_outside'), 'inside': _tr_fn('elements.front_inside'), 'both': _tr_fn('elements.front_both')},
                            value=str(params.get('front_style', 'both') or 'both'),
                        ).props('outlined dense').classes('w-full')
                        wardrobe_door_mode_sel = ui.select(
                            {'hinged': _tr_fn('elements.doors_hinged'), 'sliding': _tr_fn('elements.doors_sliding')},
                            value=str(params.get('door_mode', 'sliding' if 'SLIDING' in cur_tid else 'hinged') or 'hinged'),
                        ).props('outlined dense').classes('w-full')
                        with ui.grid(columns=2).classes('w-full gap-2'):
                            with ui.column().classes('gap-0.5'):
                                ui.label(_tr_fn('elements.shelves')).classes('text-[10px] text-gray-500')
                                _ws = int(params.get('n_shelves', 4))
                                wardrobe_shelves_inp = ui.number(
                                    value=_ws,
                                    min=_s_min, max=_s_max, step=1,
                                ).props('outlined dense').classes('w-full')
                                wardrobe_shelves_sld = ui.slider(
                                    min=_s_min, max=_s_max, value=_ws, step=1
                                ).props('label-always').classes('w-full -mt-1')
                            with ui.column().classes('gap-0.5'):
                                ui.label(_tr_fn('elements.drawers')).classes('text-[10px] text-gray-500')
                                _wd = int(params.get('n_drawers', 2))
                                wardrobe_drawers_inp = ui.number(
                                    value=_wd,
                                    min=_d_min, max=_d_max, step=1,
                                ).props('outlined dense').classes('w-full')
                                wardrobe_drawers_sld = ui.slider(
                                    min=_d_min, max=_d_max, value=_wd, step=1
                                ).props('label-always').classes('w-full -mt-1')
                            with ui.column().classes('gap-0.5'):
                                ui.label(_tr_fn('elements.hanging')).classes('text-[10px] text-gray-500')
                                _wh = int(params.get('hanger_sections', 1))
                                wardrobe_hangers_inp = ui.number(
                                    value=_wh,
                                    min=_h_min, max=_h_max, step=1,
                                ).props('outlined dense').classes('w-full')
                                wardrobe_hangers_sld = ui.slider(
                                    min=_h_min, max=_h_max, value=_wh, step=1
                                ).props('label-always').classes('w-full -mt-1')

                    _sec = params.get('american_sections') if isinstance(params.get('american_sections'), dict) else {}
                    if ('AMERICAN' in cur_tid) or bool(_sec):
                        _sec = dict(_sec or {})
                        _left = dict(_sec.get('left') or {})
                        _center = dict(_sec.get('center') or {})
                        _right = dict(_sec.get('right') or {})
                        _top = dict(_sec.get('top') or {})
                        with ui.column().classes('w-full gap-1.5'):
                            ui.label(_tr_fn('elements.sections_title')).classes(
                                'text-[9px] font-bold uppercase tracking-widest text-gray-400'
                            )
                            with ui.grid(columns=2).classes('w-full gap-2'):
                                with ui.column().classes('gap-0.5'):
                                    ui.label(_tr_fn('elements.left_pct')).classes('text-[10px] text-gray-500')
                                    sec_left_pct = ui.number(value=int(_sec.get('left_pct', 33)), min=10, max=80, step=1).props('outlined dense').classes('w-full')
                                    sec_left_pct_sld = ui.slider(min=10, max=80, value=int(_sec.get('left_pct', 33)), step=1).props('label-always').classes('w-full -mt-1')
                                with ui.column().classes('gap-0.5'):
                                    ui.label(_tr_fn('elements.center_pct')).classes('text-[10px] text-gray-500')
                                    sec_center_pct = ui.number(value=int(_sec.get('center_pct', 34)), min=10, max=80, step=1).props('outlined dense').classes('w-full')
                                    sec_center_pct_sld = ui.slider(min=10, max=80, value=int(_sec.get('center_pct', 34)), step=1).props('label-always').classes('w-full -mt-1')
                                with ui.column().classes('gap-0.5'):
                                    ui.label(_tr_fn('elements.right_pct')).classes('text-[10px] text-gray-500')
                                    sec_right_pct = ui.number(value=int(_sec.get('right_pct', 33)), min=10, max=80, step=1).props('outlined dense').classes('w-full')
                                    sec_right_pct_sld = ui.slider(min=10, max=80, value=int(_sec.get('right_pct', 33)), step=1).props('label-always').classes('w-full -mt-1')
                                with ui.column().classes('gap-0.5'):
                                    ui.label(_tr_fn('elements.top_box_h')).classes('text-[10px] text-gray-500')
                                    sec_top_h = ui.number(value=int(_sec.get('top_h_mm', 420)), min=_th_min, max=_th_max, step=10).props('outlined dense').classes('w-full')
                                    sec_top_h_sld = ui.slider(min=_th_min, max=_th_max, value=int(_sec.get('top_h_mm', 420)), step=10).props('label-always').classes('w-full -mt-1')
                            with ui.grid(columns=3).classes('w-full gap-2'):
                                with ui.column().classes('gap-0.5'):
                                    ui.label(_tr_fn('elements.left_shelves')).classes('text-[10px] text-gray-500')
                                    sec_left_shelves = ui.number(value=int(_left.get('shelves', 4)), min=0, max=12, step=1).props('outlined dense').classes('w-full')
                                    sec_left_shelves_sld = ui.slider(min=0, max=12, value=int(_left.get('shelves', 4)), step=1).props('label-always').classes('w-full -mt-1')
                                with ui.column().classes('gap-0.5'):
                                    ui.label(_tr_fn('elements.left_drawers')).classes('text-[10px] text-gray-500')
                                    sec_left_drawers = ui.number(value=int(_left.get('drawers', 1)), min=0, max=8, step=1).props('outlined dense').classes('w-full')
                                    sec_left_drawers_sld = ui.slider(min=0, max=8, value=int(_left.get('drawers', 1)), step=1).props('label-always').classes('w-full -mt-1')
                                with ui.column().classes('gap-0.5'):
                                    ui.label(_tr_fn('elements.center_hanging')).classes('text-[10px] text-gray-500')
                                    sec_center_hangers = ui.number(value=int(_center.get('hangers', 2)), min=0, max=3, step=1).props('outlined dense').classes('w-full')
                                    sec_center_hangers_sld = ui.slider(min=0, max=3, value=int(_center.get('hangers', 2)), step=1).props('label-always').classes('w-full -mt-1')
                                with ui.column().classes('gap-0.5'):
                                    ui.label(_tr_fn('elements.right_shelves')).classes('text-[10px] text-gray-500')
                                    sec_right_shelves = ui.number(value=int(_right.get('shelves', 2)), min=0, max=12, step=1).props('outlined dense').classes('w-full')
                                    sec_right_shelves_sld = ui.slider(min=0, max=12, value=int(_right.get('shelves', 2)), step=1).props('label-always').classes('w-full -mt-1')
                                with ui.column().classes('gap-0.5'):
                                    ui.label(_tr_fn('elements.right_drawers')).classes('text-[10px] text-gray-500')
                                    sec_right_drawers = ui.number(value=int(_right.get('drawers', 3)), min=0, max=8, step=1).props('outlined dense').classes('w-full')
                                    sec_right_drawers_sld = ui.slider(min=0, max=8, value=int(_right.get('drawers', 3)), step=1).props('label-always').classes('w-full -mt-1')
                                with ui.column().classes('gap-0.5'):
                                    ui.label(_tr_fn('elements.right_hanging')).classes('text-[10px] text-gray-500')
                                    sec_right_hangers = ui.number(value=int(_right.get('hangers', 1)), min=0, max=3, step=1).props('outlined dense').classes('w-full')
                                    sec_right_hangers_sld = ui.slider(min=0, max=3, value=int(_right.get('hangers', 1)), step=1).props('label-always').classes('w-full -mt-1')
                            with ui.row().classes('w-full items-center gap-2'):
                                with ui.column().classes('gap-0.5 flex-1'):
                                    ui.label(_tr_fn('elements.top_box_shelves')).classes('text-[10px] text-gray-500')
                                    sec_top_shelves = ui.number(value=int(_top.get('shelves', 2)), min=0, max=8, step=1).props('outlined dense').classes('w-full')
                                    sec_top_shelves_sld = ui.slider(min=0, max=8, value=int(_top.get('shelves', 2)), step=1).props('label-always').classes('w-full -mt-1')
                                sec_locked = ui.switch(_tr_fn('elements.lock_layout'), value=bool(_sec.get('locked', False))).classes('pt-4')

                def _bind_num_slider(num_el, sld_el):
                    if (num_el is None) or (sld_el is None):
                        return
                    def _num_to_sld(e):
                        try:
                            sld_el.set_value(int(float(e.value)))
                        except Exception:
                            pass
                    def _sld_to_num(e):
                        try:
                            num_el.set_value(int(float(e.value)))
                        except Exception:
                            pass
                    num_el.on_change(_num_to_sld)
                    sld_el.on_change(_sld_to_num)

                _bind_num_slider(wardrobe_shelves_inp, wardrobe_shelves_sld)
                _bind_num_slider(wardrobe_drawers_inp, wardrobe_drawers_sld)
                _bind_num_slider(wardrobe_hangers_inp, wardrobe_hangers_sld)
                _bind_num_slider(sec_left_pct, sec_left_pct_sld)
                _bind_num_slider(sec_center_pct, sec_center_pct_sld)
                _bind_num_slider(sec_right_pct, sec_right_pct_sld)
                _bind_num_slider(sec_top_h, sec_top_h_sld)
                _bind_num_slider(sec_left_shelves, sec_left_shelves_sld)
                _bind_num_slider(sec_left_drawers, sec_left_drawers_sld)
                _bind_num_slider(sec_center_hangers, sec_center_hangers_sld)
                _bind_num_slider(sec_right_shelves, sec_right_shelves_sld)
                _bind_num_slider(sec_right_drawers, sec_right_drawers_sld)
                _bind_num_slider(sec_right_hangers, sec_right_hangers_sld)
                _bind_num_slider(sec_top_shelves, sec_top_shelves_sld)

        with ui.element('div').classes(
            'px-4 py-3 border-t border-gray-200 bg-gray-50 shrink-0'
        ):
            def _do_delete():
                try:
                    delete_module_local(mid)
                    ui.notify(NOTIFY_ELEMENT_DELETED, type='warning', timeout=1500)
                    state.selected_edit_id = 0
                    state.mode = "add"
                    nacrt_refresh()
                    sidebar_refresh()
                except Exception as ex:
                    ui.notify(NOTIFY_ERROR_FMT.format(err=ex), type='negative')

            ui.button(BTN_OBRISI_ELEMENT, on_click=_do_delete).classes(
                'w-full text-sm rounded btn-wrap'
            ).props('flat dense')

    def _save_to_state(_=None):
        if state.active_tab != 'elementi':
            return
        try:
            new_w = int(w_inp.value or 0)
            new_h = int(h_inp.value or 0)
            new_d = int(d_inp.value or 0)
            new_g = int(g_inp.value or 0)
            if not (100 <= new_w <= 3000):
                return
            if not (100 <= new_h <= max_h):
                return
            if not (100 <= new_d <= 2000):
                return
            if not (0 <= new_g <= 500):
                return

            new_params = dict(m.get('params') or {})
            new_params['grain_dir'] = str(grain_sel.value or 'V')
            new_params['depth_mode'] = str(depth_mode_sel.value or 'STANDARD').upper()
            if is_wardrobe:
                new_params['wardrobe'] = True
                if wardrobe_front_sel is not None:
                    new_params['front_style'] = str(wardrobe_front_sel.value or 'both')
                if wardrobe_door_mode_sel is not None:
                    new_params['door_mode'] = str(wardrobe_door_mode_sel.value or 'hinged')
                if wardrobe_shelves_inp is not None:
                    new_params['n_shelves'] = int(wardrobe_shelves_inp.value or 0)
                if wardrobe_drawers_inp is not None:
                    new_params['n_drawers'] = int(wardrobe_drawers_inp.value or 0)
                if wardrobe_hangers_inp is not None:
                    new_params['hanger_sections'] = int(wardrobe_hangers_inp.value or 0)
                if sec_left_pct is not None:
                    _lp = int(sec_left_pct.value or 33)
                    _cp = int(sec_center_pct.value or 34) if sec_center_pct is not None else 34
                    _rp = int(sec_right_pct.value or 33) if sec_right_pct is not None else 33
                    # normalizuj da zbir ne bude 0
                    if (_lp + _cp + _rp) <= 0:
                        _lp, _cp, _rp = 33, 34, 33
                    new_params['american_sections'] = {
                        'left_pct': _lp,
                        'center_pct': _cp,
                        'right_pct': _rp,
                        'top_h_mm': int(sec_top_h.value or 420) if sec_top_h is not None else 420,
                        'left': {
                            'shelves': int(sec_left_shelves.value or 0) if sec_left_shelves is not None else 0,
                            'drawers': int(sec_left_drawers.value or 0) if sec_left_drawers is not None else 0,
                            'hangers': 0,
                        },
                        'center': {
                            'shelves': 0,
                            'drawers': 0,
                            'hangers': int(sec_center_hangers.value or 0) if sec_center_hangers is not None else 0,
                        },
                        'right': {
                            'shelves': int(sec_right_shelves.value or 0) if sec_right_shelves is not None else 0,
                            'drawers': int(sec_right_drawers.value or 0) if sec_right_drawers is not None else 0,
                            'hangers': int(sec_right_hangers.value or 0) if sec_right_hangers is not None else 0,
                        },
                        'top': {
                            'shelves': int(sec_top_shelves.value or 0) if sec_top_shelves is not None else 0,
                            'drawers': 0,
                            'hangers': 0,
                        },
                        'locked': bool(sec_locked.value) if sec_locked is not None else False,
                    }
            update_module_local(
                mid,
                x_mm=int(m.get('x_mm', 0)),
                w_mm=new_w, h_mm=new_h, d_mm=new_d, gap_after_mm=new_g,
                label=str(lbl_inp.value or '').strip() or str(m.get('label', '')),
                template_id=str(m.get('template_id', '')),
                params=new_params,
            )
            try:
                _wk = str(m.get("wall_key", "A") or "A").upper()
                solve_layout(state.kitchen, zone=zone_m, mode="pack", wall_key=_wk)
            except Exception as ex:
                logger.debug("Inline quick-save solve_layout failed: %s", ex)
            nacrt_refresh()
        except Exception as ex:
            ui.notify(
                NOTIFY_ERROR_FMT.format(
                    err=format_user_error(ex, getattr(state, 'language', 'sr'))
                ),
                type='negative',
                timeout=2500,
            )

    try:
        def _bind_commit(el):
            if el is None:
                return
            try:
                el.on('blur', _save_to_state)
            except Exception:
                pass
            try:
                el.on('keydown.enter', _save_to_state)
            except Exception:
                pass

        _bind_commit(w_inp)
        _bind_commit(h_inp)
        _bind_commit(d_inp)
        _bind_commit(g_inp)
        _bind_commit(lbl_inp)
        grain_sel.on_change(_save_to_state)
        depth_mode_sel.on_change(_save_to_state)
        if is_wardrobe:
            if wardrobe_front_sel is not None:
                wardrobe_front_sel.on_change(_save_to_state)
            if wardrobe_door_mode_sel is not None:
                wardrobe_door_mode_sel.on_change(_save_to_state)
            if wardrobe_shelves_inp is not None:
                wardrobe_shelves_inp.on_change(_save_to_state)
            if wardrobe_shelves_sld is not None:
                wardrobe_shelves_sld.on_change(_save_to_state)
            if wardrobe_drawers_inp is not None:
                wardrobe_drawers_inp.on_change(_save_to_state)
            if wardrobe_drawers_sld is not None:
                wardrobe_drawers_sld.on_change(_save_to_state)
            if wardrobe_hangers_inp is not None:
                wardrobe_hangers_inp.on_change(_save_to_state)
            if wardrobe_hangers_sld is not None:
                wardrobe_hangers_sld.on_change(_save_to_state)
            if sec_left_pct is not None:
                sec_left_pct.on_change(_save_to_state)
            if sec_left_pct_sld is not None:
                sec_left_pct_sld.on_change(_save_to_state)
            if sec_center_pct is not None:
                sec_center_pct.on_change(_save_to_state)
            if sec_center_pct_sld is not None:
                sec_center_pct_sld.on_change(_save_to_state)
            if sec_right_pct is not None:
                sec_right_pct.on_change(_save_to_state)
            if sec_right_pct_sld is not None:
                sec_right_pct_sld.on_change(_save_to_state)
            if sec_top_h is not None:
                sec_top_h.on_change(_save_to_state)
            if sec_top_h_sld is not None:
                sec_top_h_sld.on_change(_save_to_state)
            if sec_left_shelves is not None:
                sec_left_shelves.on_change(_save_to_state)
            if sec_left_shelves_sld is not None:
                sec_left_shelves_sld.on_change(_save_to_state)
            if sec_left_drawers is not None:
                sec_left_drawers.on_change(_save_to_state)
            if sec_left_drawers_sld is not None:
                sec_left_drawers_sld.on_change(_save_to_state)
            if sec_center_hangers is not None:
                sec_center_hangers.on_change(_save_to_state)
            if sec_center_hangers_sld is not None:
                sec_center_hangers_sld.on_change(_save_to_state)
            if sec_right_shelves is not None:
                sec_right_shelves.on_change(_save_to_state)
            if sec_right_shelves_sld is not None:
                sec_right_shelves_sld.on_change(_save_to_state)
            if sec_right_drawers is not None:
                sec_right_drawers.on_change(_save_to_state)
            if sec_right_drawers_sld is not None:
                sec_right_drawers_sld.on_change(_save_to_state)
            if sec_right_hangers is not None:
                sec_right_hangers.on_change(_save_to_state)
            if sec_right_hangers_sld is not None:
                sec_right_hangers_sld.on_change(_save_to_state)
            if sec_top_shelves is not None:
                sec_top_shelves.on_change(_save_to_state)
            if sec_top_shelves_sld is not None:
                sec_top_shelves_sld.on_change(_save_to_state)
            if sec_locked is not None:
                sec_locked.on_change(_save_to_state)
    except Exception as ex:
        logger.debug("Module properties: failed to attach change handlers: %s", ex)

