# -*- coding: utf-8 -*-
from __future__ import annotations
import logging
import pandas as pd
import matplotlib.pyplot as plt
from nicegui import ui

from cutlist import build_cutlist_sections, generate_cutlist_excel, generate_cutlist_pdf
from module_templates import get_templates
from state_logic import state, reset_state, _max_allowed_h_for_zone, add_module_instance_local, update_module_local, delete_module_local, clear_all_local, _set_view_mode, _set_show_grid, _set_grid_mm, _set_show_bounds, _set_ceiling_filler, _set_wall_length, _set_wall_height, _set_foot_height, _set_base_height, _set_vertical_gap, _set_material, _set_front_color, _set_worktop_thickness, _set_worktop_width, _set_max_element_height, get_zone_depth_standard, set_zone_depth_standard, _get_depth_mode, _is_independent_depth, suggest_corner_neighbor_guidance, save_project_json, load_project_json
from layout_engine import find_first_free_x, solve_layout
from visualization import _render, _wall_len_h, _zone_baseline_and_height, render_element_preview
from svg_icons import svg_for_tid
from room_setup_wizard import render_room_setup_step3
from render_3d import render_kitchen_elements_scene_3d
from ui_toolbar import render_toolbar_layout
from ui_project_io import make_toolbar_actions
from ui_navigation import switch_tab as _switch_tab
from ui_sidebar_actions import (
    get_sidebar_primary_action as _get_sidebar_primary_action,
    set_sidebar_primary_action as _set_sidebar_primary_action_impl,
    run_sidebar_primary_action as _run_sidebar_primary_action_impl,
    set_sidebar_footer_refresh as _set_sidebar_footer_refresh_impl,
)
from ui_panels_helpers import (
    set_sidebar_primary_action as _set_sidebar_primary_action_helper,
    run_sidebar_primary_action as _run_sidebar_primary_action_helper,
    render_color_picker_wrapper as _render_color_picker_wrapper,
)
from ui_catalog_panel import (
    render_palette as _render_palette,
    render_variants as _render_variants,
    select_template as _select_template,
)
from ui_catalog_config import PALETTE_TABS, _FRONT_COLOR_PRESETS, get_palette_tabs
from ui_color_picker import render_color_picker
from ui_sidebar import render_sidebar_content_layout
from ui_sidebar_panel import render_sidebar_content_panel
from ui_params_panel import render_params_panel
from ui_settings_tab import render_settings_tab
from ui_cutlist_tab import render_cutlist_tab
from ui_canvas_toolbar import render_canvas_toolbar
from ui_elements_tab import render_elements_tab
from ui_nova_tab import render_nova_tab
from ui_help_tab import render_help_tab
from ui_wizard_tab import render_wizard_tab
from ui_add_above_dialogs import open_add_above_dialog, open_add_above_tall_dialog
from ui_edit_panel import render_edit_panel
from ui_canvas_2d import render_nacrt
from ui_main_content import render_main_content_inner
from ui_room_helpers import (
    ROOM_OPENING_TYPES,
    ROOM_FIXTURE_TYPES,
    ensure_room_walls as _ensure_room_walls,
    get_room_wall as _get_room_wall,
)
from ui_assembly import assembly_instructions as _assembly_instructions
from ui_image_utils import fig_to_data_uri_exact
from i18n import (
    BTN_RESET_POTVRDI,
    BTN_DODAJ_NA_ZID,
    BTN_OTKAZI,
    BTN_POKUSAJ_PONOVO,
    BTN_RESET_PROJEKTA,
    DLG_RESET_DESC,
    DLG_RESET_TITLE,
    ERR_TAB_RENDER,
    LBL_BOJA_FRONTA,
    LBL_DUBINA_MM,
    LBL_IZNAD_KOG_GORNJEG,
    LBL_NAZIV,
    LBL_ODABERI_ELEMENT_IZ_LISTE,
    LBL_SIRINA_MM,
    LBL_SMER_GODA,
    LBL_STRANA_RUCKE,
    LBL_VISINA_MM,
    MSG_NEMA_GORNJIH_1_RED,
    MSG_PODESI_PROSTORIJU_PRVO,
    TAB_POCETAK,
    TAB_ELEMENTI,
    TAB_KROJNA,
    TAB_PODESAVANJA,
    TAB_POMOC,
)

templates = get_templates()
_LOG = logging.getLogger(__name__)


def _set_sidebar_primary_action(handler=None, label: str = BTN_DODAJ_NA_ZID) -> None:
    _set_sidebar_primary_action_helper(
        ui=ui,
        logger=_LOG,
        impl=_set_sidebar_primary_action_impl,
        label=label,
        handler=handler,
    )


def _run_sidebar_primary_action() -> None:
    _run_sidebar_primary_action_helper(
        ui=ui,
        impl=_run_sidebar_primary_action_impl,
        label_fallback=BTN_DODAJ_NA_ZID,
        notify_empty=LBL_ODABERI_ELEMENT_IZ_LISTE,
    )

def _palette_tabs_current() -> list[dict]:
    # kitchen_layout se cuva kao state.kitchen_layout (atribut) i state.kitchen['layout']
    # koristimo isti pattern kao render_3d.py i state_logic.py
    _kl = str(getattr(state, "kitchen_layout", state.kitchen.get("layout", "")) or "")
    tabs = get_palette_tabs(
        getattr(state, "project_type", "kitchen"),
        getattr(state, "wardrobe_profile", "standard"),
        kitchen_layout=_kl,
    )
    return tabs or PALETTE_TABS


def _palette_tab_map_current() -> dict:
    return {t["key"]: t for t in _palette_tabs_current()}


def _render_color_picker(
    color_ref: dict,
    title: str = LBL_BOJA_FRONTA,
    *,
    columns: int = 4,
    swatch_h: int = 28,
) -> None:
    _render_color_picker_wrapper(
        ui=ui,
        render_color_picker_fn=render_color_picker,
        presets=_FRONT_COLOR_PRESETS,
        color_ref=color_ref,
        title=title,
        columns=columns,
        swatch_h=swatch_h,
    )


@ui.refreshable
def render_toolbar() -> None:
    tabs = [
        ("wizard",    TAB_POCETAK,      "home"),
        ("elementi",  TAB_ELEMENTI,     "grid_view"),
        ("krojna",    TAB_KROJNA,       "table_rows"),
        ("podesavanja", TAB_PODESAVANJA, "settings"),
        ("pomoc",     TAB_POMOC,        "help"),
    ]

    _toolbar_save, _toolbar_load = make_toolbar_actions(
        ui=ui,
        state=state,
        logger=_LOG,
        save_project_json=save_project_json,
        load_project_json=load_project_json,
        main_content_refresh=main_content.refresh,
    )

    def _toolbar_reset() -> None:
        with ui.dialog() as _dlg:
            with ui.card().classes('p-6 min-w-96 gap-3'):
                ui.label(DLG_RESET_TITLE).classes('text-lg font-bold')
                ui.label(DLG_RESET_DESC).classes('text-sm text-gray-500')
                with ui.row().classes('w-full gap-2'):
                    ui.button(BTN_RESET_POTVRDI, on_click=lambda: (
                        reset_state(),
                        _dlg.close(),
                        render_toolbar.refresh(),
                        main_content.refresh(),
                        ui.notify(f'{BTN_RESET_PROJEKTA}: OK', type='positive'),
                    )).classes('flex-1 bg-white text-[#111] border border-[#111]')
                    ui.button(BTN_OTKAZI, on_click=_dlg.close).classes('flex-1')
            _dlg.open()

    render_toolbar_layout(
        ui=ui,
        tabs=tabs,
        active_tab=state.active_tab,
        on_tab_click=switch_tab,
        on_save_click=_toolbar_save,
        on_load_click=_toolbar_load,
        on_reset_click=_toolbar_reset,
    )


def switch_tab(key: str) -> None:
    _switch_tab(
        ui=ui,
        state=state,
        key=key,
        msg_podesi_prostoriju_prvo=MSG_PODESI_PROSTORIJU_PRVO,
        main_content_refresh=main_content.refresh,
        render_toolbar_refresh=render_toolbar.refresh,
        logger=_LOG,
    )


def render_palette() -> None:
    _render_palette(ui=ui, render_variants_fn=render_variants)


def select_palette_tab(key: str) -> None:
    _tab_map = _palette_tab_map_current()
    state.active_group = key if key in _tab_map else (next(iter(_tab_map.keys()), "donji"))
    sidebar_content.refresh()


@ui.refreshable
def render_variants(container=None) -> None:
    _tab_map = _palette_tab_map_current()
    _render_variants(
        ui=ui,
        state=state,
        templates=templates,
        palette_tab_map=_tab_map,
        svg_for_tid=svg_for_tid,
        render_element_preview_fn=render_element_preview,
        on_select_template=select_template,
    )


def select_template(tid: str) -> None:
    _select_template(
        state=state,
        tid=tid,
        render_variants_refresh=render_variants.refresh,
        params_panel_refresh=params_panel.refresh,
    )


@ui.refreshable
def params_panel() -> None:
    render_params_panel(
        ui=ui,
        state=state,
        templates=templates,
        logger=_LOG,
        is_independent_depth=_is_independent_depth,
        get_zone_depth_standard=get_zone_depth_standard,
        max_allowed_h_for_zone=_max_allowed_h_for_zone,
        set_zone_depth_standard=set_zone_depth_standard,
        suggest_corner_neighbor_guidance=suggest_corner_neighbor_guidance,
        find_first_free_x=find_first_free_x,
        add_module_instance_local=add_module_instance_local,
        nacrt_refresh=nacrt.refresh,
        sidebar_refresh=sidebar_content.refresh,
        set_sidebar_primary_action=_set_sidebar_primary_action,
        params_panel_refresh=params_panel.refresh,
        l_odaberi_element=LBL_ODABERI_ELEMENT_IZ_LISTE,
        l_sirina_mm=LBL_SIRINA_MM,
        l_visina_mm=LBL_VISINA_MM,
        l_dubina_mm=LBL_DUBINA_MM,
        l_smer_goda=LBL_SMER_GODA,
        l_naziv=LBL_NAZIV,
        l_strana_rucke=LBL_STRANA_RUCKE,
        l_iznad_kog_gornjeg=LBL_IZNAD_KOG_GORNJEG,
        m_nema_gornjih_1_red=MSG_NEMA_GORNJIH_1_RED,
        b_dodaj_na_zid=BTN_DODAJ_NA_ZID,
    )


def _add_module_with_room(**kwargs):
    """Wrapper koji automatski prosleđuje room i wall_key iz state-a."""
    _room = getattr(state, 'room', None)
    _wk = str(
        (_room or {}).get('active_wall', (_room or {}).get('kitchen_wall', 'A')) or 'A'
    ).upper()
    return add_module_instance_local(**kwargs, room=_room, wall_key=_wk)


def _open_add_above_tall_dialog(tall_module_id: int) -> None:
    open_add_above_tall_dialog(
        ui=ui,
        state=state,
        templates=templates,
        tall_module_id=tall_module_id,
        max_allowed_h_for_zone=_max_allowed_h_for_zone,
        add_module_instance_local=_add_module_with_room,
        nacrt_refresh=nacrt.refresh,
        sidebar_refresh=sidebar_content.refresh,
    )


def _open_add_above_dialog(wall_module_id: int) -> None:
    open_add_above_dialog(
        ui=ui,
        state=state,
        templates=templates,
        wall_module_id=wall_module_id,
        max_allowed_h_for_zone=_max_allowed_h_for_zone,
        add_module_instance_local=_add_module_with_room,
        nacrt_refresh=nacrt.refresh,
        sidebar_refresh=sidebar_content.refresh,
    )


@ui.refreshable
def edit_panel() -> None:
    render_edit_panel(
        ui=ui,
        state=state,
        templates=templates,
        max_allowed_h_for_zone=_max_allowed_h_for_zone,
        get_depth_mode=_get_depth_mode,
        get_zone_depth_standard=get_zone_depth_standard,
        is_independent_depth=_is_independent_depth,
        update_module_local=update_module_local,
        solve_layout=solve_layout,
        set_zone_depth_standard=set_zone_depth_standard,
        delete_module_local=delete_module_local,
        nacrt_refresh=nacrt.refresh,
        edit_panel_refresh=edit_panel.refresh,
        open_add_above_dialog=_open_add_above_dialog,
        open_add_above_tall_dialog=_open_add_above_tall_dialog,
        duplicate_module_local=_add_module_with_room,
        logger=_LOG,
    )


@ui.refreshable
def nacrt() -> None:
    render_nacrt(
        ui=ui,
        state=state,
        plt=plt,
        render_fn=_render,
        wall_len_h=_wall_len_h,
        zone_baseline_and_height=_zone_baseline_and_height,
        ensure_room_walls=_ensure_room_walls,
        get_room_wall=_get_room_wall,
        nacrt_refresh=nacrt.refresh,
        sidebar_refresh=sidebar_content.refresh,
        logger=_LOG,
        add_module_fn=_add_module_with_room,
        templates=templates,
    )


def _build_pdf_bytes(kitchen: dict) -> bytes:
    # Jedinstvena PDF putanja: cutlist.generate_cutlist_pdf
    return generate_cutlist_pdf(kitchen)


@ui.refreshable
def main_content() -> None:
    try:
        _main_content_inner()
    except Exception as _mc_err:
        _LOG.exception("Main content render failed: %s", _mc_err)
        with ui.column().classes('w-full h-full items-center justify-center p-12 gap-4'):
            ui.icon('error_outline').classes('text-6xl text-red-300')
            ui.label(ERR_TAB_RENDER).classes('text-lg font-bold text-red-500')
            ui.label(str(_mc_err)).classes('text-sm font-mono text-red-400 break-all max-w-xl text-center')
            ui.button(f'↻ {BTN_POKUSAJ_PONOVO}', on_click=main_content.refresh).classes(
                'mt-4 bg-white text-[#111] border border-[#111] px-6 py-2 rounded'
            )


def _main_content_inner() -> None:
    render_main_content_inner(
        ui=ui,
        state=state,
        sidebar_content=sidebar_content,
        render_canvas_toolbar=render_canvas_toolbar,
        nacrt_render=nacrt,
        main_content_refresh=main_content.refresh,
        set_view_mode=_set_view_mode,
        set_show_grid=_set_show_grid,
        set_grid_mm=_set_grid_mm,
        set_show_bounds=_set_show_bounds,
        set_ceiling_filler=_set_ceiling_filler,
        render_kitchen_elements_scene_3d=render_kitchen_elements_scene_3d,
        wall_len_h=_wall_len_h,
        zone_baseline_and_height=_zone_baseline_and_height,
        get_zone_depth_standard=get_zone_depth_standard,
        render_elements_tab=render_elements_tab,
        render_cutlist_tab=render_cutlist_tab,
        pd=pd,
        plt=plt,
        build_cutlist_sections=build_cutlist_sections,
        generate_cutlist_excel=generate_cutlist_excel,
        build_pdf_bytes=_build_pdf_bytes,
        render_fn=_render,
        fig_to_data_uri_exact=fig_to_data_uri_exact,
        render_element_preview=render_element_preview,
        svg_for_tid=svg_for_tid,
        assembly_instructions=_assembly_instructions,
        render_settings_tab=render_settings_tab,
        set_zone_depth_standard=set_zone_depth_standard,
        nacrt_refresh=nacrt.refresh,
        set_front_color=_set_front_color,
        set_material=_set_material,
        set_wall_length=_set_wall_length,
        set_wall_height=_set_wall_height,
        set_foot_height=_set_foot_height,
        set_worktop_thickness=_set_worktop_thickness,
        set_base_height=_set_base_height,
        set_worktop_width=_set_worktop_width,
        set_vertical_gap=_set_vertical_gap,
        set_max_element_height=_set_max_element_height,
        render_color_picker=_render_color_picker,
        render_nova_tab=render_nova_tab,
        switch_tab=switch_tab,
        clear_all_local=clear_all_local,
        save_project_json=save_project_json,
        load_project_json=load_project_json,
        render_help_tab=render_help_tab,
        render_wizard_tab=render_wizard_tab,
        main_content=main_content,
        render_room_setup_step3=render_room_setup_step3,
        ensure_room_walls=_ensure_room_walls,
        get_room_wall=_get_room_wall,
        room_opening_types=ROOM_OPENING_TYPES,
        room_fixture_types=ROOM_FIXTURE_TYPES,
    )


@ui.refreshable
def sidebar_content() -> None:
    _tabs = _palette_tabs_current()
    _tab_map = {t["key"]: t for t in _tabs}
    if state.active_group not in _tab_map:
        state.active_group = next(iter(_tab_map.keys()), "donji")
    render_sidebar_content_panel(
        ui=ui,
        state=state,
        templates=templates,
        palette_tabs=_tabs,
        palette_tab_map=_tab_map,
        sidebar_primary_action=_get_sidebar_primary_action(),
        btn_dodaj_na_zid=BTN_DODAJ_NA_ZID,
        render_sidebar_content_layout=render_sidebar_content_layout,
        render_palette=render_palette,
        params_panel=params_panel,
        edit_panel=edit_panel,
        select_palette_tab=select_palette_tab,
        run_sidebar_primary_action=_run_sidebar_primary_action,
        nacrt_refresh=nacrt.refresh,
        sidebar_refresh=sidebar_content.refresh,
        set_sidebar_footer_refresh=lambda fn: _set_sidebar_footer_refresh_impl(
            ui=ui, logger=_LOG, refresh_fn=fn
        ),
    )
