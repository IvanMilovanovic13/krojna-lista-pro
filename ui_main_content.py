# -*- coding: utf-8 -*-
from __future__ import annotations


def render_main_content_inner(
    *,
    ui,
    state,
    tr_fn,
    sidebar_content,
    render_toolbar_refresh,
    render_canvas_toolbar,
    nacrt_render,
    main_content_refresh,
    set_view_mode,
    set_show_grid,
    set_grid_mm,
    set_show_bounds,
    set_ceiling_filler,
    render_kitchen_elements_scene_3d,
    wall_len_h,
    zone_baseline_and_height,
    get_zone_depth_standard,
    render_elements_tab,
    render_cutlist_tab,
    cutlist_tr,
    pd,
    plt,
    build_cutlist_sections,
    generate_cutlist_excel,
    build_pdf_bytes,
    render_fn,
    fig_to_data_uri_exact,
    render_element_preview,
    svg_for_tid,
    assembly_instructions,
    render_settings_tab,
    settings_tr,
    set_zone_depth_standard,
    nacrt_refresh,
    set_front_color,
    set_material,
    set_wall_length,
    set_wall_height,
    set_foot_height,
    set_worktop_thickness,
    set_base_height,
    set_worktop_width,
    set_worktop_reserve_mm,
    set_worktop_front_overhang_mm,
    set_worktop_field_cut,
    set_worktop_edge_protection,
    set_worktop_edge_protection_type,
    set_worktop_joint_type,
    set_vertical_gap,
    set_max_element_height,
    render_color_picker,
    render_nova_panel,
    nova_tr,
    switch_tab,
    clear_all_local,
    save_project_json,
    load_project_json,
    build_demo_project_json,
    save_local_recent_project,
    list_recent_projects,
    load_recent_project,
    list_user_store_projects,
    load_project_from_store,
    get_autosave_info,
    load_autosave_project,
    login_user_session,
    register_trial_user_session,
    restore_local_session_state,
    logout_current_session,
    build_forgot_password_message,
    reset_password_with_token,
    get_current_billing_summary,
    build_checkout_start_message,
    build_customer_portal_message,
    get_release_readiness_summary,
    get_ops_runtime_summary,
    get_visible_audit_logs,
    get_visible_users,
    render_auth_tab,
    render_admin_tab,
    render_access_gate,
    render_help_tab,
    help_tr,
    render_wizard_tab,
    wizard_tr,
    main_content,
    render_room_setup_step3,
    ensure_room_walls,
    get_room_wall,
    room_opening_types,
    room_fixture_types,
) -> None:
    from state_logic import get_effective_access_context

    effective_access = get_effective_access_context()
    gate_blocked = (
        not bool(effective_access.get("can_access_app", True))
        and state.active_tab not in ("nova", "pomoc")
    )
    if gate_blocked:
        render_access_gate(
            ui=ui,
            state=state,
            tr_fn=nova_tr,
            get_current_billing_summary=get_current_billing_summary,
            build_checkout_start_message=build_checkout_start_message,
            build_customer_portal_message=build_customer_portal_message,
        )
        return

    if state.active_tab == "elementi":
        render_elements_tab(
            ui=ui,
            state=state,
            tr_fn=tr_fn,
            sidebar_content=sidebar_content,
            render_canvas_toolbar=render_canvas_toolbar,
            nacrt_render=nacrt_render,
            main_content_refresh=main_content_refresh,
            set_view_mode=set_view_mode,
            set_show_grid=set_show_grid,
            set_grid_mm=set_grid_mm,
            set_show_bounds=set_show_bounds,
            set_ceiling_filler=set_ceiling_filler,
            render_kitchen_elements_scene_3d=render_kitchen_elements_scene_3d,
            wall_len_h=wall_len_h,
            zone_baseline_and_height=zone_baseline_and_height,
            get_zone_depth_standard=get_zone_depth_standard,
        )
    elif state.active_tab == "krojna":
        render_cutlist_tab(
            ui=ui,
            state=state,
            tr_fn=cutlist_tr,
            pd=pd,
            plt=plt,
            build_cutlist_sections=build_cutlist_sections,
            generate_cutlist_excel=generate_cutlist_excel,
            build_pdf_bytes=build_pdf_bytes,
            wall_len_h=wall_len_h,
            render_fn=render_fn,
            fig_to_data_uri_exact=fig_to_data_uri_exact,
            render_element_preview=render_element_preview,
            svg_for_tid=svg_for_tid,
            assembly_instructions=assembly_instructions,
        )
        return
    elif state.active_tab == "podesavanja":
        render_settings_tab(
            ui=ui,
            state=state,
            tr_fn=settings_tr,
            get_zone_depth_standard=get_zone_depth_standard,
            set_zone_depth_standard=set_zone_depth_standard,
            nacrt_refresh=nacrt_refresh,
            main_content_refresh=main_content_refresh,
            set_front_color=set_front_color,
            set_material=set_material,
            set_wall_length=set_wall_length,
            set_wall_height=set_wall_height,
            set_foot_height=set_foot_height,
            set_worktop_thickness=set_worktop_thickness,
            set_base_height=set_base_height,
            set_worktop_width=set_worktop_width,
            set_worktop_reserve_mm=set_worktop_reserve_mm,
            set_worktop_front_overhang_mm=set_worktop_front_overhang_mm,
            set_worktop_field_cut=set_worktop_field_cut,
            set_worktop_edge_protection=set_worktop_edge_protection,
            set_worktop_edge_protection_type=set_worktop_edge_protection_type,
            set_worktop_joint_type=set_worktop_joint_type,
            set_vertical_gap=set_vertical_gap,
            set_max_element_height=set_max_element_height,
            render_color_picker=render_color_picker,
        )
        return
    elif state.active_tab == "nova":
        render_nova_panel()
        return
    elif state.active_tab == "nalog":
        render_auth_tab(
            ui=ui,
            state=state,
            tr_fn=nova_tr,
            main_content_refresh=main_content_refresh,
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
        return
    elif state.active_tab == "ops":
        _tier = str(getattr(state, "current_access_tier", "") or "").strip().lower()
        if _tier != "admin":
            with ui.column().classes("w-full p-6 gap-2"):
                ui.label(nova_tr("ops.denied_title")).classes("text-xl font-bold text-red-700")
                ui.label(nova_tr("ops.denied_desc")).classes("text-sm text-slate-600")
            return
        render_admin_tab(
            ui=ui,
            tr_fn=nova_tr,
            get_release_readiness_summary=get_release_readiness_summary,
            get_ops_runtime_summary=get_ops_runtime_summary,
            get_visible_audit_logs=get_visible_audit_logs,
            get_visible_users=get_visible_users,
        )
        return
    elif state.active_tab == "pomoc":
        render_help_tab(ui=ui, tr_fn=help_tr)
        return
    elif state.active_tab == "wizard":
        is_authenticated = bool(str(getattr(state, 'current_user_email', '') or '').strip())
        if is_authenticated and int(getattr(state, 'wizard_step', 1) or 1) == 1:
            render_nova_panel()
            return
        render_wizard_tab(
            ui=ui,
            state=state,
            tr_fn=wizard_tr,
            main_content=main_content,
            main_content_refresh=main_content_refresh,
            switch_tab=switch_tab,
            render_room_setup_step3=render_room_setup_step3,
            plt=plt,
            ensure_room_walls=ensure_room_walls,
            get_room_wall=get_room_wall,
            set_wall_length=set_wall_length,
            set_wall_height=set_wall_height,
            room_opening_types=room_opening_types,
            room_fixture_types=room_fixture_types,
        )
        return
