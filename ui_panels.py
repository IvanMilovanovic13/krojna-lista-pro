# -*- coding: utf-8 -*-
from __future__ import annotations
import logging
import pandas as pd
import matplotlib.pyplot as plt
from nicegui import ui

from cutlist import build_cutlist_sections, generate_cutlist_excel, generate_cutlist_pdf
from module_templates import get_templates
from state_logic import state, reset_state, _max_allowed_h_for_zone, add_module_instance_local, update_module_local, delete_module_local, clear_all_local, _set_view_mode, _set_show_grid, _set_grid_mm, _set_show_bounds, _set_ceiling_filler, _set_wall_length, _set_wall_height, _set_foot_height, _set_base_height, _set_vertical_gap, _set_material, _set_front_color, _set_worktop_thickness, _set_worktop_width, _set_worktop_reserve_mm, _set_worktop_front_overhang_mm, _set_worktop_field_cut, _set_worktop_edge_protection, _set_worktop_edge_protection_type, _set_worktop_joint_type, _set_max_element_height, get_zone_depth_standard, set_zone_depth_standard, _get_depth_mode, _is_independent_depth, suggest_corner_neighbor_guidance, save_project_json, load_project_json, build_demo_project_json, save_local_recent_project, list_recent_projects, load_recent_project, list_user_store_projects, load_project_from_store, get_autosave_info, load_autosave_project, login_user_session, register_trial_user_session, restore_local_session_state, logout_current_session, build_forgot_password_message, reset_password_with_token, get_current_billing_summary, get_cutlist_access_state, build_checkout_start_message, build_customer_portal_message, get_release_readiness_summary, get_ops_runtime_summary, get_visible_audit_logs, get_visible_users, _set_language, get_effective_access_context
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
from ui_auth_tab import render_auth_tab
from ui_admin_tab import render_admin_tab
from ui_help_tab import render_help_tab
from ui_access_gate import render_access_gate
from ui_wizard_tab import render_wizard_tab
from ui_add_above_dialogs import open_add_above_dialog, open_add_above_tall_dialog
from ui_edit_panel import render_edit_panel
from ui_canvas_2d import render_nacrt
from ui_main_content import render_main_content_inner
from ui_room_helpers import (
    ROOM_OPENING_TYPES,
    ROOM_FIXTURE_TYPES,
    get_room_opening_types,
    get_room_fixture_types,
    ensure_room_walls as _ensure_room_walls,
    get_room_wall as _get_room_wall,
)
from ui_assembly import assembly_instructions as _assembly_instructions
from ui_image_utils import fig_to_data_uri_exact
from i18n import (
    ERR_TAB_RENDER,
    OPT_TEHNICKI,
    get_language_options,
    tr,
)

templates = get_templates()
_LOG = logging.getLogger(__name__)


def _set_sidebar_primary_action(handler=None, label: str | None = None) -> None:
    _label = label
    if not _label:
        _label = _tr("elements.add_to_wall")
    _set_sidebar_primary_action_helper(
        ui=ui,
        logger=_LOG,
        impl=_set_sidebar_primary_action_impl,
        label=_label,
        handler=handler,
    )


def _run_sidebar_primary_action() -> None:
    _run_sidebar_primary_action_helper(
        ui=ui,
        impl=_run_sidebar_primary_action_impl,
        label_fallback=_tr("elements.add_to_wall"),
        notify_empty=_tr("elements.select_from_list"),
    )


def _tr(key: str, **fmt: object) -> str:
    return tr(key, getattr(state, "language", "sr"), **fmt)


def _change_language(lang: str) -> None:
    _current = str(getattr(state, "language", "sr") or "sr").strip().lower()
    _target = str(lang or "sr").strip().lower()
    if _target == _current:
        return
    _set_language(lang)
    render_toolbar.refresh()
    if str(getattr(state, "active_tab", "") or "") == "elementi":
        canvas_toolbar_panel.refresh()
        sidebar_content.refresh()
        return
    if str(getattr(state, "active_tab", "") or "") == "nova":
        nova_panel.refresh()
        return
    main_content.refresh()

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
    title: str | None = None,
    *,
    columns: int = 4,
    swatch_h: int = 28,
    lang: str | None = None,
) -> None:
    _render_color_picker_wrapper(
        ui=ui,
        render_color_picker_fn=render_color_picker,
        presets=_FRONT_COLOR_PRESETS,
        color_ref=color_ref,
        title=title or _tr("elements.material_color"),
        columns=columns,
        swatch_h=swatch_h,
        lang=lang or getattr(state, "language", "sr"),
    )


@ui.refreshable
def render_toolbar() -> None:
    _effective_access = get_effective_access_context()
    tabs = [
        ("wizard",    _tr("tab.wizard"),    "home"),
        ("elementi",  _tr("tab.elements"),  "grid_view"),
        ("krojna", _tr("tab.cutlist"), "table_rows"),
        ("pomoc",     _tr("tab.help"),      "help"),
    ]
    _tier = str(_effective_access.get("access_tier", "") or "").strip().lower()
    if _tier == "admin":
        tabs.insert(5, ("ops", _tr("tab.ops"), "admin_panel_settings"))

    from state_logic import account_save_current_project, list_user_store_projects, load_project_from_store

    _raw_toolbar_save, _raw_toolbar_load = make_toolbar_actions(
        ui=ui,
        state=state,
        logger=_LOG,
        tr_fn=_tr,
        save_project_json=save_project_json,
        load_project_json=load_project_json,
        main_content_refresh=main_content.refresh,
        save_to_account=account_save_current_project,
        list_account_projects=list_user_store_projects,
        load_from_account=load_project_from_store,
    )

    def _redirect_locked_toolbar_action() -> None:
        _access = get_cutlist_access_state()
        state.active_tab = "nalog"
        state.account_upgrade_focus = True
        ui.notify(str(_access.get("reason", "") or _tr("toolbar.pro_redirect")), type='warning', timeout=5000)
        main_content.refresh()
        ui.timer(0.05, lambda: ui.run_javascript('window.scrollTo({top: 0, behavior: "auto"})'), once=True)
        ui.timer(0.05, render_toolbar.refresh, once=True)

    def _toolbar_save() -> None:
        if str(get_cutlist_access_state().get("allowed", "")).lower() != "true":
            _redirect_locked_toolbar_action()
            return
        _raw_toolbar_save()

    def _toolbar_load() -> None:
        if str(get_cutlist_access_state().get("allowed", "")).lower() != "true":
            _redirect_locked_toolbar_action()
            return
        _raw_toolbar_load()

    def _toolbar_reset() -> None:
        with ui.dialog() as _dlg:
            with ui.card().classes('p-6 min-w-96 gap-3'):
                ui.label(_tr("toolbar.reset")).classes('text-lg font-bold')
                ui.label(_tr("nova.warn_clear")).classes('text-sm text-gray-500')
                with ui.row().classes('w-full gap-2'):
                    ui.button(_tr("nova.confirm"), on_click=lambda: (
                        reset_state(),
                        _dlg.close(),
                        render_toolbar.refresh(),
                        main_content.refresh(),
                        ui.notify(f'{_tr("toolbar.reset")}: OK', type='positive'),
                    )).classes('flex-1 bg-white text-[#111] border border-[#111]')
                    ui.button(_tr("common.cancel"), on_click=_dlg.close).classes('flex-1')
            _dlg.open()

    def _toolbar_logout() -> None:
        ok, err = logout_current_session()
        if ok:
            render_toolbar.refresh()
            main_content.refresh()
            ui.notify(_tr("nova.auth_logout_ok"), type='positive')
            ui.navigate.to("/login")
        else:
            ui.notify(err, type='negative', timeout=5000)

    _session_email = str(getattr(state, "current_user_email", "") or "")
    _session_tier = str(_effective_access.get("access_tier", "") or "")
    _session_label = ""
    if _session_email:
        _session_label = _tr("toolbar.session_fmt", email=_session_email, tier=_session_tier or "-")

    render_toolbar_layout(
        ui=ui,
        tabs=tabs,
        active_tab=state.active_tab,
        on_tab_click=switch_tab,
        on_save_click=_toolbar_save,
        on_load_click=_toolbar_load,
        on_reset_click=_toolbar_reset,
        language_label=_tr("toolbar.language"),
        language_options=get_language_options(),
        current_language=getattr(state, "language", "sr"),
        on_language_change=_change_language,
        toolbar_app_name=_tr("toolbar.app_name"),
        toolbar_app_sub=_tr("toolbar.app_sub"),
        toolbar_save_label=_tr("toolbar.save"),
        toolbar_load_label=_tr("toolbar.load"),
        toolbar_reset_label=_tr("toolbar.reset"),
        toolbar_save_tooltip=_tr("toolbar.save_tooltip"),
        toolbar_load_tooltip=_tr("toolbar.load_tooltip"),
        toolbar_reset_tooltip=_tr("toolbar.reset_tooltip"),
        session_label=_session_label,
        account_label=_tr("toolbar.account"),
        logout_label=_tr("toolbar.logout"),
        on_account_click=lambda: switch_tab("nalog"),
        on_logout_click=_toolbar_logout,
    )


def switch_tab(key: str) -> None:
    _switch_tab(
        ui=ui,
        state=state,
        key=key,
        msg_podesi_prostoriju_prvo=_tr("room.setup_first"),
        main_content_refresh=main_content.refresh,
        render_toolbar_refresh=render_toolbar.refresh,
        logger=_LOG,
    )


def render_palette() -> None:
    _render_palette(ui=ui, render_variants_fn=render_variants)


def select_palette_tab(key: str) -> None:
    _tab_map = _palette_tab_map_current()
    state.active_group = key if key in _tab_map else (next(iter(_tab_map.keys()), "donji"))
    _changed_view = str(getattr(state, "view_mode", "") or "") != str(OPT_TEHNICKI)
    if _changed_view:
        _set_view_mode(OPT_TEHNICKI)
        main_content.refresh()
        return
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
        l_odaberi_element=_tr("elements.select_from_list"),
        l_sirina_mm=_tr("params.width_mm"),
        l_visina_mm=_tr("params.height_mm"),
        l_dubina_mm=_tr("params.depth_mm"),
        l_smer_goda=_tr("params.grain_label"),
        l_naziv=_tr("params.name"),
        l_strana_rucke=_tr("params.handle_side"),
        l_iznad_kog_gornjeg=_tr("params.above_which_wall"),
        m_nema_gornjih_1_red=_tr("elements.no_first_row_wall"),
        b_dodaj_na_zid=_tr("elements.add_to_wall"),
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
        tr_fn=_tr,
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


@ui.refreshable
def canvas_toolbar_panel() -> None:
    render_canvas_toolbar(
        ui=ui,
        state=state,
        tr_fn=_tr,
        nacrt_refresh=nacrt.refresh,
        main_content_refresh=main_content.refresh,
        set_view_mode=_set_view_mode,
        set_show_grid=_set_show_grid,
        set_grid_mm=_set_grid_mm,
        set_show_bounds=_set_show_bounds,
        set_ceiling_filler=_set_ceiling_filler,
    )


@ui.refreshable
def nova_panel() -> None:
    render_nova_tab(
        ui=ui,
        state=state,
        tr_fn=_tr,
        main_content_refresh=main_content.refresh,
        render_toolbar_refresh=render_toolbar.refresh,
        switch_tab=switch_tab,
        clear_all_local=clear_all_local,
        save_project_json=save_project_json,
        load_project_json=load_project_json,
        build_demo_project_json=build_demo_project_json,
        save_local_recent_project=save_local_recent_project,
        list_recent_projects=list_recent_projects,
        load_recent_project=load_recent_project,
        list_user_store_projects=list_user_store_projects,
        load_project_from_store=load_project_from_store,
        get_autosave_info=get_autosave_info,
        load_autosave_project=load_autosave_project,
        login_user_session=login_user_session,
        register_trial_user_session=register_trial_user_session,
        restore_local_session_state=restore_local_session_state,
        logout_current_session=logout_current_session,
        build_forgot_password_message=build_forgot_password_message,
        reset_password_with_token=reset_password_with_token,
        get_current_billing_summary=get_current_billing_summary,
        build_checkout_start_message=build_checkout_start_message,
        build_customer_portal_message=build_customer_portal_message,
    )


def _build_pdf_bytes(kitchen: dict) -> bytes:
    # Jedinstvena PDF putanja: cutlist.generate_cutlist_pdf
    return generate_cutlist_pdf(kitchen, lang=str(getattr(state, 'language', 'sr') or 'sr'))


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
            ui.button(f'↻ {_tr("common.retry")}', on_click=main_content.refresh).classes(
                'mt-4 bg-white text-[#111] border border-[#111] px-6 py-2 rounded'
            )


def _main_content_inner() -> None:
    render_main_content_inner(
        ui=ui,
        state=state,
        tr_fn=_tr,
        sidebar_content=sidebar_content,
        render_toolbar_refresh=render_toolbar.refresh,
        render_canvas_toolbar=canvas_toolbar_panel,
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
        cutlist_tr=_tr,
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
        settings_tr=_tr,
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
        set_worktop_reserve_mm=_set_worktop_reserve_mm,
        set_worktop_front_overhang_mm=_set_worktop_front_overhang_mm,
        set_worktop_field_cut=_set_worktop_field_cut,
        set_worktop_edge_protection=_set_worktop_edge_protection,
        set_worktop_edge_protection_type=_set_worktop_edge_protection_type,
        set_worktop_joint_type=_set_worktop_joint_type,
        set_vertical_gap=_set_vertical_gap,
        set_max_element_height=_set_max_element_height,
        render_color_picker=_render_color_picker,
        render_nova_panel=nova_panel,
        nova_tr=_tr,
        switch_tab=switch_tab,
        clear_all_local=clear_all_local,
        save_project_json=save_project_json,
        load_project_json=load_project_json,
        build_demo_project_json=build_demo_project_json,
        save_local_recent_project=save_local_recent_project,
        list_recent_projects=list_recent_projects,
        load_recent_project=load_recent_project,
        list_user_store_projects=list_user_store_projects,
        load_project_from_store=load_project_from_store,
        get_autosave_info=get_autosave_info,
        load_autosave_project=load_autosave_project,
        login_user_session=login_user_session,
        register_trial_user_session=register_trial_user_session,
        restore_local_session_state=restore_local_session_state,
        logout_current_session=logout_current_session,
        build_forgot_password_message=build_forgot_password_message,
        reset_password_with_token=reset_password_with_token,
        get_current_billing_summary=get_current_billing_summary,
        build_checkout_start_message=build_checkout_start_message,
        build_customer_portal_message=build_customer_portal_message,
        render_auth_tab=render_auth_tab,
        render_admin_tab=render_admin_tab,
        render_access_gate=render_access_gate,
        render_help_tab=render_help_tab,
        help_tr=_tr,
        render_wizard_tab=render_wizard_tab,
        wizard_tr=_tr,
        main_content=main_content,
        render_room_setup_step3=render_room_setup_step3,
        ensure_room_walls=_ensure_room_walls,
        get_room_wall=_get_room_wall,
        room_opening_types=get_room_opening_types(getattr(state, "language", "sr")),
        room_fixture_types=get_room_fixture_types(getattr(state, "language", "sr")),
        get_release_readiness_summary=get_release_readiness_summary,
        get_ops_runtime_summary=get_ops_runtime_summary,
        get_visible_audit_logs=get_visible_audit_logs,
        get_visible_users=get_visible_users,
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
        btn_dodaj_na_zid=_tr("elements.add_to_wall"),
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
