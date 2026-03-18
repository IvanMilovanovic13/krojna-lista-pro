# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Callable

from i18n import (
    BADGE_GORNJI_RED,
    BADGE_NADSTRESNI,
    BTN_DODAJ,
    BTN_OTKAZI,
    LBL_DODAJ_IZNAD_VISOKOG,
    LBL_DODAJ_RED_IZNAD,
    LBL_DUBINA_LABEL_MM,
    LBL_ISPOD_INFO,
    LBL_SIRINA_POZ_AUTO,
    LBL_TIP_ELEMENTA,
    LBL_VISINA_MAX_FMT,
    MSG_ELEMENT_NIJE_PRONADJEN,
    MSG_NEMA_TEMPLATE_GORNJI_RED,
    MSG_NEMA_TEMPLATE_NADSTRESNI,
    NOTIFY_ADDED_ABOVE_FMT,
    NOTIFY_ERR_SHORT_FMT,
)
from ui_panels_helpers import format_user_error


def open_add_above_tall_dialog(
    *,
    ui: Any,
    state: Any,
    templates: dict,
    tall_module_id: int,
    max_allowed_h_for_zone: Callable[[str], int],
    add_module_instance_local: Callable[..., Any],
    nacrt_refresh: Callable[[], None],
    sidebar_refresh: Callable[[], None],
) -> None:
    mods = state.kitchen.get('modules', []) or []
    tall_m = next((mm for mm in mods if int(mm.get('id', -1)) == tall_module_id), None)
    if not tall_m:
        ui.notify(MSG_ELEMENT_NIJE_PRONADJEN, type='negative')
        return

    tall_x = int(tall_m.get('x_mm', 0))
    tall_w = int(tall_m.get('w_mm', 0))
    tall_lbl = str(tall_m.get('label', f'#{tall_module_id}'))

    tt_tids = [t for t in ['TALL_TOP_DOORS', 'TALL_TOP_OPEN'] if templates.get(t)]
    if not tt_tids:
        ui.notify(MSG_NEMA_TEMPLATE_NADSTRESNI, type='warning')
        return
    tt_labels = {templates[t].get('label', t): t for t in tt_tids}

    max_h = max_allowed_h_for_zone('tall_top')
    def_h = min(400, max(200, max_h))

    with ui.dialog().classes('z-50') as dlg:
        with ui.card().classes('min-w-72 p-4 gap-2'):
            with ui.row().classes('w-full items-center justify-between mb-1'):
                ui.label(LBL_DODAJ_IZNAD_VISOKOG).classes('font-bold text-base')
                ui.badge(BADGE_NADSTRESNI).classes(
                    'text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-800'
                )
            ui.label(LBL_ISPOD_INFO.format(label=tall_lbl, w=tall_w, x=tall_x)).classes(
                'text-xs text-gray-500 mb-2'
            )
            ui.separator()

            tid_sel = ui.select(
                list(tt_labels.keys()),
                value=list(tt_labels.keys())[0],
                label=LBL_TIP_ELEMENTA,
            ).classes('w-full').props('outlined dense')

            with ui.row().classes('w-full gap-2'):
                h_inp = ui.number(
                    LBL_VISINA_MAX_FMT.format(max_h=max_h),
                    value=def_h, min=150, max=max_h, step=10,
                ).classes('flex-1').props('outlined dense')

                def_d = int((templates.get(tt_tids[0], {}).get('defaults', {}) or {}).get('d_mm', 350))
                d_inp = ui.number(
                    LBL_DUBINA_LABEL_MM,
                    value=def_d, min=150, max=700, step=10,
                ).classes('flex-1').props('outlined dense')

            ui.label(LBL_SIRINA_POZ_AUTO.format(w=tall_w)).classes('text-xs text-gray-700 mt-1')

            def _potvrdi():
                try:
                    tid = tt_labels[str(tid_sel.value)]
                    tmpl = templates.get(tid, {})
                    new_h = int(h_inp.value)
                    new_d = int(d_inp.value)
                    new_lbl = str(tmpl.get('label', tid))

                    _new_mod = add_module_instance_local(
                        template_id=tid,
                        zone='tall_top',
                        x_mm=tall_x,
                        w_mm=tall_w,
                        h_mm=new_h,
                        d_mm=new_d,
                        label=new_lbl,
                    )
                    ui.notify(NOTIFY_ADDED_ABOVE_FMT.format(label=new_lbl, id=tall_module_id), type='positive')
                    dlg.close()
                    state.selected_edit_id = int((_new_mod or {}).get('id', 0))
                    state.mode = "edit"
                    nacrt_refresh()
                    sidebar_refresh()
                except Exception as e:
                    ui.notify(NOTIFY_ERR_SHORT_FMT.format(err=format_user_error(e)), type='negative')

            with ui.row().classes('w-full mt-3 gap-2'):
                ui.button(BTN_DODAJ, on_click=_potvrdi).classes(
                    'flex-1 bg-white text-[#111] border border-[#111] font-bold'
                )
                ui.button(BTN_OTKAZI, on_click=dlg.close).classes('flex-1')

    dlg.open()


def open_add_above_dialog(
    *,
    ui: Any,
    state: Any,
    templates: dict,
    wall_module_id: int,
    max_allowed_h_for_zone: Callable[[str], int],
    add_module_instance_local: Callable[..., Any],
    nacrt_refresh: Callable[[], None],
    sidebar_refresh: Callable[[], None],
) -> None:
    mods = state.kitchen.get('modules', []) or []
    wall_m = next((mm for mm in mods if int(mm.get('id', -1)) == wall_module_id), None)
    if not wall_m:
        ui.notify(MSG_ELEMENT_NIJE_PRONADJEN, type='negative')
        return

    wall_x = int(wall_m.get('x_mm', 0))
    wall_w = int(wall_m.get('w_mm', 0))
    wall_lbl = str(wall_m.get('label', f'#{wall_module_id}'))

    wu_tids = [t for t in ['WALL_UPPER_1DOOR', 'WALL_UPPER_2DOOR'] if templates.get(t)]
    if not wu_tids:
        ui.notify(MSG_NEMA_TEMPLATE_GORNJI_RED, type='warning')
        return
    wu_labels = {templates[t].get('label', t): t for t in wu_tids}

    max_h = max_allowed_h_for_zone('wall_upper')
    def_h = min(400, max(200, max_h))

    with ui.dialog().classes('z-50') as dlg:
        with ui.card().classes('min-w-72 p-5 gap-2'):
            with ui.row().classes('w-full items-center justify-between mb-1'):
                ui.label(LBL_DODAJ_RED_IZNAD).classes('font-bold text-base')
                ui.badge(BADGE_GORNJI_RED).classes(
                    'text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-800'
                )
            ui.label(LBL_ISPOD_INFO.format(label=wall_lbl, w=wall_w, x=wall_x)).classes(
                'text-xs text-gray-500 mb-2'
            )
            ui.separator()

            tid_sel = ui.select(
                list(wu_labels.keys()),
                value=list(wu_labels.keys())[0],
                label=LBL_TIP_ELEMENTA,
            ).classes('w-full').props('outlined dense')

            with ui.row().classes('w-full gap-2'):
                h_inp = ui.number(
                    LBL_VISINA_MAX_FMT.format(max_h=max_h),
                    value=def_h, min=150, max=max_h, step=10,
                ).classes('flex-1').props('outlined dense')

                def_d = int((templates.get(wu_tids[0], {}).get('defaults', {}) or {}).get('d_mm', 350))
                d_inp = ui.number(
                    LBL_DUBINA_LABEL_MM,
                    value=def_d, min=150, max=700, step=10,
                ).classes('flex-1').props('outlined dense')

            ui.label(LBL_SIRINA_POZ_AUTO.format(w=wall_w)).classes('text-xs text-gray-700 mt-1')

            def _potvrdi():
                try:
                    tid = wu_labels[str(tid_sel.value)]
                    tmpl = templates.get(tid, {})
                    new_h = int(h_inp.value)
                    new_d = int(d_inp.value)
                    new_lbl = str(tmpl.get('label', tid))

                    _new_mod = add_module_instance_local(
                        template_id=tid,
                        zone='wall_upper',
                        x_mm=wall_x,
                        w_mm=wall_w,
                        h_mm=new_h,
                        d_mm=new_d,
                        label=new_lbl,
                    )
                    ui.notify(NOTIFY_ADDED_ABOVE_FMT.format(label=new_lbl, id=wall_module_id), type='positive')
                    dlg.close()
                    state.selected_edit_id = int((_new_mod or {}).get('id', 0))
                    state.mode = "edit"
                    nacrt_refresh()
                    sidebar_refresh()
                except Exception as e:
                    ui.notify(NOTIFY_ERR_SHORT_FMT.format(err=format_user_error(e)), type='negative')

            with ui.row().classes('w-full mt-3 gap-2'):
                ui.button(BTN_DODAJ, on_click=_potvrdi).classes(
                    'flex-1 bg-white text-[#111] border border-[#111] font-bold'
                )
                ui.button(BTN_OTKAZI, on_click=dlg.close).classes('flex-1')

    dlg.open()
