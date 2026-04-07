# -*- coding: utf-8 -*-
"""
run_all_tests.py — Pokretac svih automatskih testova KrojnaListaPRO

Pokreni:
    python run_all_tests.py           # samo padovi
    python run_all_tests.py -v        # sve (i PASS)
    python run_all_tests.py --quick   # samo smoke (brzo, bez PDF/Excel)

Izlaz:
    exit 0 = sve proslo
    exit 1 = ima padova
"""
from __future__ import annotations
import sys, time, argparse
sys.path.insert(0, ".")


def _p(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", errors="replace").decode("ascii"))


# ─── BLOK 1: smoke_scenarios (logika, 2D/3D, layout, room) ──────────────────

def run_smoke(verbose: bool) -> tuple[int, int]:
    from smoke_scenarios import (
        smoke_all_template_previews,
        smoke_palette_scope_and_panel_previews,
        smoke_mixed_appliance_previews,
        smoke_upper_appliance_previews,
        smoke_active_kitchen_palette_previews,
        smoke_representative_render_cutlist_parity,
        smoke_front_and_drawer_quantities,
        smoke_special_front_types,
        smoke_add_edit_layout,
        smoke_room_openings_walls,
        smoke_grid_modes,
        smoke_bounds_toggle_modes,
        smoke_blocking_validations,
        smoke_update_validations,
        smoke_layout_support_audit,
        smoke_room_constraints,
        smoke_warning_generation,
        smoke_shopping_hardware,
        smoke_fastener_and_grouping_hardware,
    )

    tests = [
        ("Template previews (57 tpl)",  smoke_all_template_previews),
        ("Palette scope + panel",        smoke_palette_scope_and_panel_previews),
        ("Mixed appliance previews",     smoke_mixed_appliance_previews),
        ("Upper appliance previews",     smoke_upper_appliance_previews),
        ("Active palette previews",      smoke_active_kitchen_palette_previews),
        ("Render + cutlist parity",      smoke_representative_render_cutlist_parity),
        ("Front + drawer quantities",    smoke_front_and_drawer_quantities),
        ("Special front types",          smoke_special_front_types),
        ("Add / edit layout",            smoke_add_edit_layout),
        ("Room openings + walls",        smoke_room_openings_walls),
        ("Grid modes (1/5/10mm)",        smoke_grid_modes),
        ("Bounds toggle (catalog/tech)", smoke_bounds_toggle_modes),
        ("Blocking validations",         smoke_blocking_validations),
        ("Update validations",           smoke_update_validations),
        ("Layout support audit",         smoke_layout_support_audit),
        ("Room constraints",             smoke_room_constraints),
        ("Warning generation",           smoke_warning_generation),
        ("Shopping + hardware",          smoke_shopping_hardware),
        ("Fastener + grouping hw",       smoke_fastener_and_grouping_hardware),
    ]

    passed = failed = 0
    for name, fn in tests:
        try:
            r1, r2 = fn()
            if isinstance(r1, bool):
                ok = bool(r1)
                msg = "" if ok else str(r2)
            elif isinstance(r1, int):
                ok = (r2 == 0)
                msg = f"{r1} ok" if ok else f"{r2} greske"
            else:
                ok = bool(r1)
                msg = "" if ok else str(r2)
        except Exception as ex:
            ok, msg = False, f"EXCEPTION: {ex}"

        if ok:
            passed += 1
            if verbose:
                _p(f"    [PASS] {name}")
        else:
            failed += 1
            _p(f"    [FAIL] {name}  ->  {msg}")

    return passed, failed


# ─── BLOK 2: test_geometry (dimenzije, overlap, krojna lista, okovi) ─────────

def run_geometry(verbose: bool) -> tuple[int, int]:
    import test_geometry as tg

    # Resetuj globalni results
    tg._results.clear()

    for fn in tg.ALL_TESTS:
        before = len(tg._results)
        try:
            fn()
        except Exception as ex:
            tg._log(False, fn.__name__, f"EXCEPTION: {ex}")
        after = len(tg._results)

        for ok, name, msg in tg._results[before:after]:
            if ok:
                if verbose:
                    _p(f"    [PASS] {name}")
            else:
                _p(f"    [FAIL] {name}  ->  {msg}")

    passed = sum(1 for ok, _, _ in tg._results if ok)
    failed = sum(1 for ok, _, _ in tg._results if not ok)
    return passed, failed


# ─── BLOK 3: PDF + Excel generisanje (integracioni test) ────────────────────

def run_export_tests(verbose: bool) -> tuple[int, int]:
    from cutlist import generate_cutlist, build_cutlist_pdf_bytes, generate_cutlist_excel, generate_cutlist_summary
    from state_logic import _default_kitchen
    from test_export_consistency import (
        run_cutout_warning_check,
        run_corner_neighbor_warning_check,
        run_corner_door_swing_warning_check,
        run_drawer_backs_in_detail_summary_check,
        run_drawer_front_min_warning_check,
        run_drawer_stack_warning_check,
        run_dishwasher_width_warning_check,
        run_door_drawer_warning_check,
        run_drawer_depth_warning_check,
        run_cooking_width_warning_check,
        run_english_service_translation_check,
        run_english_summary_translation_check,
        run_excel_intro_sheet_check,
        run_export_consistency_check,
        run_export_sanitization_check,
        run_base_alignment_warning_check,
        run_base_depth_warning_check,
        run_front_gap_warning_check,
        run_filler_warning_check,
        run_freestanding_depth_warning_check,
        run_freestanding_fridge_depth_warning_check,
        run_fridge_width_warning_check,
        run_hob_width_warning_check,
        run_invalid_dimensions_warning_check,
        run_invalid_wall_warning_check,
        run_left_out_of_bounds_warning_check,
        run_liftup_width_warning_check,
        run_module_out_of_bounds_warning_check,
        run_missing_template_warning_check,
        run_overlap_warning_check,
        run_panel_service_processing_check,
        run_pdf_note_formatting_check,
        run_pdf_warning_priority_check,
        run_side_wall_door_warning_check,
        run_single_door_width_warning_check,
        run_sink_width_warning_check,
        run_tall_appliance_width_warning_check,
        run_tall_appliance_depth_warning_check,
        run_tall_height_warning_check,
        run_tall_depth_warning_check,
        run_tall_top_height_warning_check,
        run_tall_top_support_warning_check,
        run_wall_depth_warning_check,
        run_wall_appliance_depth_warning_check,
        run_wall_appliance_width_warning_check,
        run_wall_upper_height_warning_check,
        run_wall_upper_support_warning_check,
        run_reference_linear_kitchen_check,
        run_reference_l_kitchen_check,
        run_reference_galley_kitchen_check,
        run_reference_u_kitchen_check,
        run_reference_raised_dishwasher_kitchen_check,
        run_reference_tall_block_kitchen_check,
        run_reference_utility_kitchen_check,
        run_raised_dishwasher_cutlist_check,
        run_raised_dishwasher_height_consistency_check,
        run_raised_dishwasher_translation_check,
        run_serbian_export_text_check,
        run_summary_detail_structure_check,
        run_validation_warning_check,
        run_warning_translation_check,
        run_worktop_excel_sheet_check,
        run_worktop_pdf_instruction_check,
        run_worktop_warning_check,
    )
    from test_export_unicode_hygiene import run_export_unicode_hygiene_check
    from test_label_cleanup import run_label_cleanup_consistency_check
    from test_assembly_language import run_assembly_language_polish_check
    from test_access_gate_billing import run_access_gate_billing_check
    from test_auth_tab_wiring import run_auth_tab_wiring_check
    from test_nova_tab_wiring import run_nova_tab_wiring_check
    from test_auth_session_hardening import run_auth_session_hardening_check
    from test_auth_atomic_session_switch import run_auth_atomic_session_switch_check
    from test_logout_resilience import run_logout_resilience_check
    from test_local_session_project_cleanup import run_local_session_project_cleanup_check
    from test_local_billing_guard import run_local_billing_guard_check
    from test_session_identity_project_reset import run_session_identity_project_reset_check
    from test_session_refresh_fallback import run_session_refresh_fallback_check
    from test_session_refresh_resilience import run_session_refresh_resilience_check
    from test_session_restore_resilience import run_session_restore_resilience_check
    from test_internal_auth_autofill import run_internal_auth_autofill_check
    from test_public_auth_autofill import run_public_auth_autofill_check
    from test_billing_storage_stability import (
        run_sqlite_backend_stability_check,
        run_subscription_upsert_preserves_fields_check,
    )
    from test_billing_event_ops import run_billing_event_ops_check
    from test_billing_runtime_guard import run_billing_runtime_guard_check
    from test_billing_ui_runtime_guard import run_billing_ui_runtime_guard_check
    from test_billing_state_ux import run_billing_state_ux_check
    from test_billing_webhook_idempotency import run_billing_webhook_idempotency_check
    from test_cutlist_export_jobs_ui import run_cutlist_export_jobs_ui_check
    from test_checkout_return_flow import run_checkout_return_flow_check
    from test_deploy_worker_config import run_deploy_worker_config_check
    from test_app_config_env_loading import run_app_config_env_loading_check
    from test_audit_visibility_scope import run_audit_visibility_scope_check
    from test_export_jobs_background import run_export_jobs_background_check
    from test_export_job_ops import run_export_job_ops_check
    from test_export_job_store import (
        run_export_job_store_check,
        run_export_job_user_isolation_check,
    )
    from test_export_job_stale_cleanup import run_export_job_stale_cleanup_check
    from test_export_worker_mode import run_export_worker_mode_check
    from test_postgres_export_jobs_migration import run_postgres_export_jobs_migration_check
    from test_post_login_dashboard import run_post_login_dashboard_contract_check
    from test_ops_billing_runtime import run_ops_billing_runtime_check
    from test_ops_access_scope import run_ops_access_scope_check
    from test_ops_runtime_scope import run_ops_runtime_scope_check
    from test_project_store_recent_autosave import (
        run_project_touch_user_isolation_check,
        run_project_store_recent_autosave_check,
        run_project_store_user_isolation_check,
    )
    from test_public_site_language import run_public_site_language_check
    from test_readiness_scope import run_readiness_scope_check
    from test_release_readiness_url_scope import run_release_readiness_url_scope_check
    from test_session_billing_refresh import run_session_billing_refresh_check
    from test_stripe_customer_persist_resilience import run_stripe_customer_persist_resilience_check
    from test_worktop_ui_contract import run_worktop_dataset_contract_check
    from test_staging_runner_contract import run_staging_runner_contract_check
    from test_stripe_placeholder_readiness import run_stripe_placeholder_readiness_check
    from test_stripe_action_persist_resilience import run_stripe_action_persist_resilience_check

    passed = failed = 0

    def _ok(name: str, msg: str = "OK"):
        nonlocal passed
        passed += 1
        if verbose:
            _p(f"    [PASS] {name}  {msg}")

    def _fail(name: str, msg: str):
        nonlocal failed
        failed += 1
        _p(f"    [FAIL] {name}  ->  {msg}")

    # Kuhinja za test
    k = _default_kitchen()
    k["wall"]["length_mm"] = 3000
    k["wall"]["height_mm"] = 2600
    k["foot_height_mm"] = 150
    k["worktop"] = {"enabled": True, "material": "Granit", "thickness": 4.0, "depth_mm": 600}
    k["materials"] = {
        "carcass_material": "Iver 18mm", "carcass_thk": 18,
        "front_material": "MDF 19mm", "front_thk": 19,
        "back_material": "Iver 8mm", "back_thk": 8,
        "edge_abs_thk": 2.0,
    }
    k["modules"] = [
        {"id":1,"template_id":"BASE_2DOOR","zone":"base","x_mm":5,"w_mm":800,"h_mm":720,"d_mm":560,"label":"Donji 2V","params":{},"wall_key":"A","gap_after_mm":0},
        {"id":2,"template_id":"BASE_DRAWERS_3","zone":"base","x_mm":805,"w_mm":600,"h_mm":720,"d_mm":560,"label":"Fiokar","params":{"n_drawers":3},"wall_key":"A","gap_after_mm":0},
        {"id":3,"template_id":"WALL_2DOOR","zone":"wall","x_mm":5,"w_mm":800,"h_mm":700,"d_mm":320,"label":"Gornji 2V","params":{},"wall_key":"A","gap_after_mm":0},
        {"id":4,"template_id":"TALL_PANTRY","zone":"tall","x_mm":1405,"w_mm":600,"h_mm":2100,"d_mm":560,"label":"Visoki","params":{},"wall_key":"A","gap_after_mm":0},
    ]

    try:
        sections = generate_cutlist(k)
        _ok("generate_cutlist", f"{sum(len(v) for v in sections.values() if v is not None)} ukupno redova")
    except Exception as ex:
        _fail("generate_cutlist", str(ex))
        return passed, failed  # nema smisla nastaviti

    try:
        pdf = build_cutlist_pdf_bytes(k, sections, "Test export")
        if len(pdf) < 10000:
            _fail("pdf_export_size", f"PDF premali: {len(pdf)}B")
        else:
            _ok("pdf_export", f"{len(pdf)//1024}kB")
    except Exception as ex:
        _fail("pdf_export", str(ex))

    try:
        xl = generate_cutlist_excel(k, sections)
        if len(xl) < 5000:
            _fail("excel_export_size", f"Excel premali: {len(xl)}B")
        else:
            _ok("excel_export", f"{len(xl)//1024}kB")
    except Exception as ex:
        _fail("excel_export", str(ex))

    try:
        summary = generate_cutlist_summary(sections)
        sa = summary.get("summary_all")
        if sa is None or sa.empty:
            _fail("summary_all_not_empty", "summary_all je prazan")
        else:
            _ok("summary_all", f"{len(sa)} redova")
        det = summary.get("summary_detaljna")
        if det is None or det.empty:
            _fail("summary_detaljna_not_empty", "summary_detaljna je prazan")
        else:
            _ok("summary_detaljna", f"{len(det)} redova")
    except Exception as ex:
        _fail("summary_generation", str(ex))

    try:
        ok, msg = run_export_consistency_check("en")
        if ok:
            _ok("export_consistency", msg)
        else:
            _fail("export_consistency", msg)
    except Exception as ex:
        _fail("export_consistency", str(ex))

    try:
        ok, msg = run_drawer_backs_in_detail_summary_check()
        if ok:
            _ok("drawer_backs_in_detail_summary", msg)
        else:
            _fail("drawer_backs_in_detail_summary", msg)
    except Exception as ex:
        _fail("drawer_backs_in_detail_summary", str(ex))

    try:
        ok, msg = run_label_cleanup_consistency_check()
        if ok:
            _ok("label_cleanup_consistency", msg)
        else:
            _fail("label_cleanup_consistency", msg)
    except Exception as ex:
        _fail("label_cleanup_consistency", str(ex))

    try:
        ok, msg = run_export_unicode_hygiene_check()
        if ok:
            _ok("export_unicode_hygiene", msg)
        else:
            _fail("export_unicode_hygiene", msg)
    except Exception as ex:
        _fail("export_unicode_hygiene", str(ex))

    try:
        ok, msg = run_assembly_language_polish_check()
        if ok:
            _ok("assembly_language_polish", msg)
        else:
            _fail("assembly_language_polish", msg)
    except Exception as ex:
        _fail("assembly_language_polish", str(ex))

    try:
        ok, msg = run_access_gate_billing_check()
        if ok:
            _ok("access_gate_billing", msg)
        else:
            _fail("access_gate_billing", msg)
    except Exception as ex:
        _fail("access_gate_billing", str(ex))

    try:
        ok, msg = run_auth_tab_wiring_check()
        if ok:
            _ok("auth_tab_wiring", msg)
        else:
            _fail("auth_tab_wiring", msg)
    except Exception as ex:
        _fail("auth_tab_wiring", str(ex))

    try:
        ok, msg = run_nova_tab_wiring_check()
        if ok:
            _ok("nova_tab_wiring", msg)
        else:
            _fail("nova_tab_wiring", msg)
    except Exception as ex:
        _fail("nova_tab_wiring", str(ex))

    try:
        ok, msg = run_public_auth_autofill_check()
        if ok:
            _ok("public_auth_autofill", msg)
        else:
            _fail("public_auth_autofill", msg)
    except Exception as ex:
        _fail("public_auth_autofill", str(ex))

    try:
        ok, msg = run_internal_auth_autofill_check()
        if ok:
            _ok("internal_auth_autofill", msg)
        else:
            _fail("internal_auth_autofill", msg)
    except Exception as ex:
        _fail("internal_auth_autofill", str(ex))

    try:
        ok, msg = run_auth_session_hardening_check()
        if ok:
            _ok("auth_session_hardening", msg)
        else:
            _fail("auth_session_hardening", msg)
    except Exception as ex:
        _fail("auth_session_hardening", str(ex))

    try:
        ok, msg = run_auth_atomic_session_switch_check()
        if ok:
            _ok("auth_atomic_session_switch", msg)
        else:
            _fail("auth_atomic_session_switch", msg)
    except Exception as ex:
        _fail("auth_atomic_session_switch", str(ex))

    try:
        ok, msg = run_logout_resilience_check()
        if ok:
            _ok("logout_resilience", msg)
        else:
            _fail("logout_resilience", msg)
    except Exception as ex:
        _fail("logout_resilience", str(ex))

    try:
        ok, msg = run_local_session_project_cleanup_check()
        if ok:
            _ok("local_session_project_cleanup", msg)
        else:
            _fail("local_session_project_cleanup", msg)
    except Exception as ex:
        _fail("local_session_project_cleanup", str(ex))

    try:
        ok, msg = run_local_billing_guard_check()
        if ok:
            _ok("local_billing_guard", msg)
        else:
            _fail("local_billing_guard", msg)
    except Exception as ex:
        _fail("local_billing_guard", str(ex))

    try:
        ok, msg = run_session_identity_project_reset_check()
        if ok:
            _ok("session_identity_project_reset", msg)
        else:
            _fail("session_identity_project_reset", msg)
    except Exception as ex:
        _fail("session_identity_project_reset", str(ex))

    try:
        ok, msg = run_session_refresh_fallback_check()
        if ok:
            _ok("session_refresh_fallback", msg)
        else:
            _fail("session_refresh_fallback", msg)
    except Exception as ex:
        _fail("session_refresh_fallback", str(ex))

    try:
        ok, msg = run_session_refresh_resilience_check()
        if ok:
            _ok("session_refresh_resilience", msg)
        else:
            _fail("session_refresh_resilience", msg)
    except Exception as ex:
        _fail("session_refresh_resilience", str(ex))

    try:
        ok, msg = run_session_restore_resilience_check()
        if ok:
            _ok("session_restore_resilience", msg)
        else:
            _fail("session_restore_resilience", msg)
    except Exception as ex:
        _fail("session_restore_resilience", str(ex))

    try:
        ok, msg = run_public_site_language_check()
        if ok:
            _ok("public_site_language", msg)
        else:
            _fail("public_site_language", msg)
    except Exception as ex:
        _fail("public_site_language", str(ex))

    try:
        ok, msg = run_session_billing_refresh_check()
        if ok:
            _ok("session_billing_refresh", msg)
        else:
            _fail("session_billing_refresh", msg)
    except Exception as ex:
        _fail("session_billing_refresh", str(ex))

    try:
        ok, msg = run_checkout_return_flow_check()
        if ok:
            _ok("checkout_return_flow", msg)
        else:
            _fail("checkout_return_flow", msg)
    except Exception as ex:
        _fail("checkout_return_flow", str(ex))

    try:
        ok, msg = run_deploy_worker_config_check()
        if ok:
            _ok("deploy_worker_config", msg)
        else:
            _fail("deploy_worker_config", msg)
    except Exception as ex:
        _fail("deploy_worker_config", str(ex))

    try:
        ok, msg = run_app_config_env_loading_check()
        if ok:
            _ok("app_config_env_loading", msg)
        else:
            _fail("app_config_env_loading", msg)
    except Exception as ex:
        _fail("app_config_env_loading", str(ex))

    try:
        ok, msg = run_staging_runner_contract_check()
        if ok:
            _ok("staging_runner_contract", msg)
        else:
            _fail("staging_runner_contract", msg)
    except Exception as ex:
        _fail("staging_runner_contract", str(ex))

    try:
        ok, msg = run_readiness_scope_check()
        if ok:
            _ok("readiness_scope", msg)
        else:
            _fail("readiness_scope", msg)
    except Exception as ex:
        _fail("readiness_scope", str(ex))

    try:
        ok, msg = run_release_readiness_url_scope_check()
        if ok:
            _ok("release_readiness_url_scope", msg)
        else:
            _fail("release_readiness_url_scope", msg)
    except Exception as ex:
        _fail("release_readiness_url_scope", str(ex))

    try:
        ok, msg = run_stripe_placeholder_readiness_check()
        if ok:
            _ok("stripe_placeholder_readiness", msg)
        else:
            _fail("stripe_placeholder_readiness", msg)
    except Exception as ex:
        _fail("stripe_placeholder_readiness", str(ex))

    try:
        ok, msg = run_sqlite_backend_stability_check()
        if ok:
            _ok("sqlite_backend_stability", msg)
        else:
            _fail("sqlite_backend_stability", msg)
    except Exception as ex:
        _fail("sqlite_backend_stability", str(ex))

    try:
        ok, msg = run_subscription_upsert_preserves_fields_check()
        if ok:
            _ok("subscription_upsert_preserves_fields", msg)
        else:
            _fail("subscription_upsert_preserves_fields", msg)
    except Exception as ex:
        _fail("subscription_upsert_preserves_fields", str(ex))

    try:
        ok, msg = run_billing_webhook_idempotency_check()
        if ok:
            _ok("billing_webhook_idempotency", msg)
        else:
            _fail("billing_webhook_idempotency", msg)
    except Exception as ex:
        _fail("billing_webhook_idempotency", str(ex))

    try:
        ok, msg = run_billing_state_ux_check()
        if ok:
            _ok("billing_state_ux", msg)
        else:
            _fail("billing_state_ux", msg)
    except Exception as ex:
        _fail("billing_state_ux", str(ex))

    try:
        ok, msg = run_billing_event_ops_check()
        if ok:
            _ok("billing_event_ops", msg)
        else:
            _fail("billing_event_ops", msg)
    except Exception as ex:
        _fail("billing_event_ops", str(ex))

    try:
        ok, msg = run_billing_runtime_guard_check()
        if ok:
            _ok("billing_runtime_guard", msg)
        else:
            _fail("billing_runtime_guard", msg)
    except Exception as ex:
        _fail("billing_runtime_guard", str(ex))

    try:
        ok, msg = run_billing_ui_runtime_guard_check()
        if ok:
            _ok("billing_ui_runtime_guard", msg)
        else:
            _fail("billing_ui_runtime_guard", msg)
    except Exception as ex:
        _fail("billing_ui_runtime_guard", str(ex))

    try:
        ok, msg = run_stripe_action_persist_resilience_check()
        if ok:
            _ok("stripe_action_persist_resilience", msg)
        else:
            _fail("stripe_action_persist_resilience", msg)
    except Exception as ex:
        _fail("stripe_action_persist_resilience", str(ex))

    try:
        ok, msg = run_export_job_stale_cleanup_check()
        if ok:
            _ok("export_job_stale_cleanup", msg)
        else:
            _fail("export_job_stale_cleanup", msg)
    except Exception as ex:
        _fail("export_job_stale_cleanup", str(ex))

    try:
        ok, msg = run_stripe_customer_persist_resilience_check()
        if ok:
            _ok("stripe_customer_persist_resilience", msg)
        else:
            _fail("stripe_customer_persist_resilience", msg)
    except Exception as ex:
        _fail("stripe_customer_persist_resilience", str(ex))

    try:
        ok, msg = run_post_login_dashboard_contract_check()
        if ok:
            _ok("post_login_dashboard_contract", msg)
        else:
            _fail("post_login_dashboard_contract", msg)
    except Exception as ex:
        _fail("post_login_dashboard_contract", str(ex))

    try:
        ok, msg = run_ops_billing_runtime_check()
        if ok:
            _ok("ops_billing_runtime", msg)
        else:
            _fail("ops_billing_runtime", msg)
    except Exception as ex:
        _fail("ops_billing_runtime", str(ex))

    try:
        ok, msg = run_ops_access_scope_check()
        if ok:
            _ok("ops_access_scope", msg)
        else:
            _fail("ops_access_scope", msg)
    except Exception as ex:
        _fail("ops_access_scope", str(ex))

    try:
        ok, msg = run_ops_runtime_scope_check()
        if ok:
            _ok("ops_runtime_scope", msg)
        else:
            _fail("ops_runtime_scope", msg)
    except Exception as ex:
        _fail("ops_runtime_scope", str(ex))

    try:
        ok, msg = run_audit_visibility_scope_check()
        if ok:
            _ok("audit_visibility_scope", msg)
        else:
            _fail("audit_visibility_scope", msg)
    except Exception as ex:
        _fail("audit_visibility_scope", str(ex))

    try:
        ok, msg = run_project_store_recent_autosave_check()
        if ok:
            _ok("project_store_recent_autosave", msg)
        else:
            _fail("project_store_recent_autosave", msg)
    except Exception as ex:
        _fail("project_store_recent_autosave", str(ex))

    try:
        ok, msg = run_project_store_user_isolation_check()
        if ok:
            _ok("project_store_user_isolation", msg)
        else:
            _fail("project_store_user_isolation", msg)
    except Exception as ex:
        _fail("project_store_user_isolation", str(ex))

    try:
        ok, msg = run_project_touch_user_isolation_check()
        if ok:
            _ok("project_touch_user_isolation", msg)
        else:
            _fail("project_touch_user_isolation", msg)
    except Exception as ex:
        _fail("project_touch_user_isolation", str(ex))

    try:
        ok, msg = run_export_job_store_check()
        if ok:
            _ok("export_job_store", msg)
        else:
            _fail("export_job_store", msg)
    except Exception as ex:
        _fail("export_job_store", str(ex))

    try:
        ok, msg = run_export_job_user_isolation_check()
        if ok:
            _ok("export_job_user_isolation", msg)
        else:
            _fail("export_job_user_isolation", msg)
    except Exception as ex:
        _fail("export_job_user_isolation", str(ex))

    try:
        ok, msg = run_postgres_export_jobs_migration_check()
        if ok:
            _ok("postgres_export_jobs_migration", msg)
        else:
            _fail("postgres_export_jobs_migration", msg)
    except Exception as ex:
        _fail("postgres_export_jobs_migration", str(ex))

    try:
        ok, msg = run_cutlist_export_jobs_ui_check()
        if ok:
            _ok("cutlist_export_jobs_ui", msg)
        else:
            _fail("cutlist_export_jobs_ui", msg)
    except Exception as ex:
        _fail("cutlist_export_jobs_ui", str(ex))

    try:
        ok, msg = run_export_jobs_background_check()
        if ok:
            _ok("export_jobs_background", msg)
        else:
            _fail("export_jobs_background", msg)
    except Exception as ex:
        _fail("export_jobs_background", str(ex))

    try:
        ok, msg = run_export_job_ops_check()
        if ok:
            _ok("export_job_ops", msg)
        else:
            _fail("export_job_ops", msg)
    except Exception as ex:
        _fail("export_job_ops", str(ex))

    try:
        ok, msg = run_export_worker_mode_check()
        if ok:
            _ok("export_worker_mode", msg)
        else:
            _fail("export_worker_mode", msg)
    except Exception as ex:
        _fail("export_worker_mode", str(ex))

    try:
        ok, msg = run_worktop_dataset_contract_check()
        if ok:
            _ok("worktop_dataset_contract", msg)
        else:
            _fail("worktop_dataset_contract", msg)
    except Exception as ex:
        _fail("worktop_dataset_contract", str(ex))

    try:
        ok, msg = run_english_summary_translation_check()
        if ok:
            _ok("english_summary_translation", msg)
        else:
            _fail("english_summary_translation", msg)
    except Exception as ex:
        _fail("english_summary_translation", str(ex))

    try:
        ok, msg = run_english_service_translation_check()
        if ok:
            _ok("english_service_translation", msg)
        else:
            _fail("english_service_translation", msg)
    except Exception as ex:
        _fail("english_service_translation", str(ex))

    try:
        ok, msg = run_export_sanitization_check()
        if ok:
            _ok("export_sanitization", msg)
        else:
            _fail("export_sanitization", msg)
    except Exception as ex:
        _fail("export_sanitization", str(ex))

    try:
        ok, msg = run_validation_warning_check()
        if ok:
            _ok("validation_warning_layer", msg)
        else:
            _fail("validation_warning_layer", msg)
    except Exception as ex:
        _fail("validation_warning_layer", str(ex))

    try:
        ok, msg = run_missing_template_warning_check()
        if ok:
            _ok("missing_template_warning", msg)
        else:
            _fail("missing_template_warning", msg)
    except Exception as ex:
        _fail("missing_template_warning", str(ex))

    try:
        ok, msg = run_invalid_dimensions_warning_check()
        if ok:
            _ok("invalid_dimensions_warning", msg)
        else:
            _fail("invalid_dimensions_warning", msg)
    except Exception as ex:
        _fail("invalid_dimensions_warning", str(ex))

    try:
        ok, msg = run_invalid_wall_warning_check()
        if ok:
            _ok("invalid_wall_warning", msg)
        else:
            _fail("invalid_wall_warning", msg)
    except Exception as ex:
        _fail("invalid_wall_warning", str(ex))

    try:
        ok, msg = run_left_out_of_bounds_warning_check()
        if ok:
            _ok("left_out_of_bounds_warning", msg)
        else:
            _fail("left_out_of_bounds_warning", msg)
    except Exception as ex:
        _fail("left_out_of_bounds_warning", str(ex))

    try:
        ok, msg = run_base_alignment_warning_check()
        if ok:
            _ok("base_alignment_warning", msg)
        else:
            _fail("base_alignment_warning", msg)
    except Exception as ex:
        _fail("base_alignment_warning", str(ex))

    try:
        ok, msg = run_overlap_warning_check()
        if ok:
            _ok("overlap_warning_layer", msg)
        else:
            _fail("overlap_warning_layer", msg)
    except Exception as ex:
        _fail("overlap_warning_layer", str(ex))

    try:
        ok, msg = run_worktop_warning_check()
        if ok:
            _ok("worktop_too_short_warning", msg)
        else:
            _fail("worktop_too_short_warning", msg)
    except Exception as ex:
        _fail("worktop_too_short_warning", str(ex))

    try:
        ok, msg = run_cutout_warning_check()
        if ok:
            _ok("cutout_out_of_bounds_warning", msg)
        else:
            _fail("cutout_out_of_bounds_warning", msg)
    except Exception as ex:
        _fail("cutout_out_of_bounds_warning", str(ex))

    try:
        ok, msg = run_corner_neighbor_warning_check()
        if ok:
            _ok("corner_neighbor_warning", msg)
        else:
            _fail("corner_neighbor_warning", msg)
    except Exception as ex:
        _fail("corner_neighbor_warning", str(ex))

    try:
        ok, msg = run_corner_door_swing_warning_check()
        if ok:
            _ok("corner_door_swing_warning", msg)
        else:
            _fail("corner_door_swing_warning", msg)
    except Exception as ex:
        _fail("corner_door_swing_warning", str(ex))

    try:
        ok, msg = run_side_wall_door_warning_check()
        if ok:
            _ok("side_wall_door_warning", msg)
        else:
            _fail("side_wall_door_warning", msg)
    except Exception as ex:
        _fail("side_wall_door_warning", str(ex))

    try:
        ok, msg = run_front_gap_warning_check()
        if ok:
            _ok("front_gap_warning", msg)
        else:
            _fail("front_gap_warning", msg)
    except Exception as ex:
        _fail("front_gap_warning", str(ex))

    try:
        ok, msg = run_drawer_stack_warning_check()
        if ok:
            _ok("drawer_stack_warning", msg)
        else:
            _fail("drawer_stack_warning", msg)
    except Exception as ex:
        _fail("drawer_stack_warning", str(ex))

    try:
        ok, msg = run_drawer_front_min_warning_check()
        if ok:
            _ok("drawer_front_min_warning", msg)
        else:
            _fail("drawer_front_min_warning", msg)
    except Exception as ex:
        _fail("drawer_front_min_warning", str(ex))

    try:
        ok, msg = run_door_drawer_warning_check()
        if ok:
            _ok("door_drawer_warning", msg)
        else:
            _fail("door_drawer_warning", msg)
    except Exception as ex:
        _fail("door_drawer_warning", str(ex))

    try:
        ok, msg = run_drawer_depth_warning_check()
        if ok:
            _ok("drawer_depth_warning", msg)
        else:
            _fail("drawer_depth_warning", msg)
    except Exception as ex:
        _fail("drawer_depth_warning", str(ex))

    try:
        ok, msg = run_base_depth_warning_check()
        if ok:
            _ok("base_depth_warning", msg)
        else:
            _fail("base_depth_warning", msg)
    except Exception as ex:
        _fail("base_depth_warning", str(ex))

    try:
        ok, msg = run_dishwasher_width_warning_check()
        if ok:
            _ok("dishwasher_width_warning", msg)
        else:
            _fail("dishwasher_width_warning", msg)
    except Exception as ex:
        _fail("dishwasher_width_warning", str(ex))

    try:
        ok, msg = run_freestanding_depth_warning_check()
        if ok:
            _ok("freestanding_depth_warning", msg)
        else:
            _fail("freestanding_depth_warning", msg)
    except Exception as ex:
        _fail("freestanding_depth_warning", str(ex))

    try:
        ok, msg = run_freestanding_fridge_depth_warning_check()
        if ok:
            _ok("freestanding_fridge_depth_warning", msg)
        else:
            _fail("freestanding_fridge_depth_warning", msg)
    except Exception as ex:
        _fail("freestanding_fridge_depth_warning", str(ex))

    try:
        ok, msg = run_cooking_width_warning_check()
        if ok:
            _ok("cooking_width_warning", msg)
        else:
            _fail("cooking_width_warning", msg)
    except Exception as ex:
        _fail("cooking_width_warning", str(ex))

    try:
        ok, msg = run_fridge_width_warning_check()
        if ok:
            _ok("fridge_width_warning", msg)
        else:
            _fail("fridge_width_warning", msg)
    except Exception as ex:
        _fail("fridge_width_warning", str(ex))

    try:
        ok, msg = run_liftup_width_warning_check()
        if ok:
            _ok("liftup_width_warning", msg)
        else:
            _fail("liftup_width_warning", msg)
    except Exception as ex:
        _fail("liftup_width_warning", str(ex))

    try:
        ok, msg = run_hob_width_warning_check()
        if ok:
            _ok("hob_width_warning", msg)
        else:
            _fail("hob_width_warning", msg)
    except Exception as ex:
        _fail("hob_width_warning", str(ex))

    try:
        ok, msg = run_sink_width_warning_check()
        if ok:
            _ok("sink_width_warning", msg)
        else:
            _fail("sink_width_warning", msg)
    except Exception as ex:
        _fail("sink_width_warning", str(ex))

    try:
        ok, msg = run_tall_appliance_width_warning_check()
        if ok:
            _ok("tall_appliance_width_warning", msg)
        else:
            _fail("tall_appliance_width_warning", msg)
    except Exception as ex:
        _fail("tall_appliance_width_warning", str(ex))

    try:
        ok, msg = run_tall_appliance_depth_warning_check()
        if ok:
            _ok("tall_appliance_depth_warning", msg)
        else:
            _fail("tall_appliance_depth_warning", msg)
    except Exception as ex:
        _fail("tall_appliance_depth_warning", str(ex))

    try:
        ok, msg = run_tall_height_warning_check()
        if ok:
            _ok("tall_height_warning", msg)
        else:
            _fail("tall_height_warning", msg)
    except Exception as ex:
        _fail("tall_height_warning", str(ex))

    try:
        ok, msg = run_tall_depth_warning_check()
        if ok:
            _ok("tall_depth_warning", msg)
        else:
            _fail("tall_depth_warning", msg)
    except Exception as ex:
        _fail("tall_depth_warning", str(ex))

    try:
        ok, msg = run_wall_depth_warning_check()
        if ok:
            _ok("wall_depth_warning", msg)
        else:
            _fail("wall_depth_warning", msg)
    except Exception as ex:
        _fail("wall_depth_warning", str(ex))

    try:
        ok, msg = run_wall_appliance_width_warning_check()
        if ok:
            _ok("wall_appliance_width_warning", msg)
        else:
            _fail("wall_appliance_width_warning", msg)
    except Exception as ex:
        _fail("wall_appliance_width_warning", str(ex))

    try:
        ok, msg = run_wall_appliance_depth_warning_check()
        if ok:
            _ok("wall_appliance_depth_warning", msg)
        else:
            _fail("wall_appliance_depth_warning", msg)
    except Exception as ex:
        _fail("wall_appliance_depth_warning", str(ex))

    try:
        ok, msg = run_single_door_width_warning_check()
        if ok:
            _ok("single_door_width_warning", msg)
        else:
            _fail("single_door_width_warning", msg)
    except Exception as ex:
        _fail("single_door_width_warning", str(ex))

    try:
        ok, msg = run_module_out_of_bounds_warning_check()
        if ok:
            _ok("module_out_of_bounds_warning", msg)
        else:
            _fail("module_out_of_bounds_warning", msg)
    except Exception as ex:
        _fail("module_out_of_bounds_warning", str(ex))

    try:
        ok, msg = run_wall_upper_support_warning_check()
        if ok:
            _ok("wall_upper_support_warning", msg)
        else:
            _fail("wall_upper_support_warning", msg)
    except Exception as ex:
        _fail("wall_upper_support_warning", str(ex))

    try:
        ok, msg = run_tall_top_support_warning_check()
        if ok:
            _ok("tall_top_support_warning", msg)
        else:
            _fail("tall_top_support_warning", msg)
    except Exception as ex:
        _fail("tall_top_support_warning", str(ex))

    try:
        ok, msg = run_filler_warning_check()
        if ok:
            _ok("filler_too_wide_warning", msg)
        else:
            _fail("filler_too_wide_warning", msg)
    except Exception as ex:
        _fail("filler_too_wide_warning", str(ex))

    try:
        ok, msg = run_panel_service_processing_check()
        if ok:
            _ok("panel_service_processing", msg)
        else:
            _fail("panel_service_processing", msg)
    except Exception as ex:
        _fail("panel_service_processing", str(ex))

    try:
        ok, msg = run_pdf_note_formatting_check()
        if ok:
            _ok("pdf_note_formatting", msg)
        else:
            _fail("pdf_note_formatting", msg)
    except Exception as ex:
        _fail("pdf_note_formatting", str(ex))

    try:
        ok, msg = run_pdf_warning_priority_check()
        if ok:
            _ok("pdf_warning_priority", msg)
        else:
            _fail("pdf_warning_priority", msg)
    except Exception as ex:
        _fail("pdf_warning_priority", str(ex))

    try:
        ok, msg = run_tall_top_height_warning_check()
        if ok:
            _ok("tall_top_height_warning", msg)
        else:
            _fail("tall_top_height_warning", msg)
    except Exception as ex:
        _fail("tall_top_height_warning", str(ex))

    try:
        ok, msg = run_wall_upper_height_warning_check()
        if ok:
            _ok("wall_upper_height_warning", msg)
        else:
            _fail("wall_upper_height_warning", msg)
    except Exception as ex:
        _fail("wall_upper_height_warning", str(ex))

    try:
        ok, msg = run_reference_linear_kitchen_check()
        if ok:
            _ok("reference_linear_kitchen", msg)
        else:
            _fail("reference_linear_kitchen", msg)
    except Exception as ex:
        _fail("reference_linear_kitchen", str(ex))

    try:
        ok, msg = run_reference_tall_block_kitchen_check()
        if ok:
            _ok("reference_tall_block_kitchen", msg)
        else:
            _fail("reference_tall_block_kitchen", msg)
    except Exception as ex:
        _fail("reference_tall_block_kitchen", str(ex))

    try:
        ok, msg = run_reference_utility_kitchen_check()
        if ok:
            _ok("reference_utility_kitchen", msg)
        else:
            _fail("reference_utility_kitchen", msg)
    except Exception as ex:
        _fail("reference_utility_kitchen", str(ex))

    try:
        ok, msg = run_reference_l_kitchen_check()
        if ok:
            _ok("reference_l_kitchen", msg)
        else:
            _fail("reference_l_kitchen", msg)
    except Exception as ex:
        _fail("reference_l_kitchen", str(ex))

    try:
        ok, msg = run_reference_galley_kitchen_check()
        if ok:
            _ok("reference_galley_kitchen", msg)
        else:
            _fail("reference_galley_kitchen", msg)
    except Exception as ex:
        _fail("reference_galley_kitchen", str(ex))

    try:
        ok, msg = run_reference_u_kitchen_check()
        if ok:
            _ok("reference_u_kitchen", msg)
        else:
            _fail("reference_u_kitchen", msg)
    except Exception as ex:
        _fail("reference_u_kitchen", str(ex))

    try:
        ok, msg = run_reference_raised_dishwasher_kitchen_check()
        if ok:
            _ok("reference_raised_dishwasher_kitchen", msg)
        else:
            _fail("reference_raised_dishwasher_kitchen", msg)
    except Exception as ex:
        _fail("reference_raised_dishwasher_kitchen", str(ex))

    try:
        ok, msg = run_summary_detail_structure_check()
        if ok:
            _ok("summary_detail_structure", msg)
        else:
            _fail("summary_detail_structure", msg)
    except Exception as ex:
        _fail("summary_detail_structure", str(ex))

    try:
        ok, msg = run_raised_dishwasher_cutlist_check()
        if ok:
            _ok("raised_dishwasher_cutlist", msg)
        else:
            _fail("raised_dishwasher_cutlist", msg)
    except Exception as ex:
        _fail("raised_dishwasher_cutlist", str(ex))

    try:
        ok, msg = run_raised_dishwasher_translation_check()
        if ok:
            _ok("raised_dishwasher_translation", msg)
        else:
            _fail("raised_dishwasher_translation", msg)
    except Exception as ex:
        _fail("raised_dishwasher_translation", str(ex))

    try:
        ok, msg = run_raised_dishwasher_height_consistency_check()
        if ok:
            _ok("raised_dishwasher_height_consistency", msg)
        else:
            _fail("raised_dishwasher_height_consistency", msg)
    except Exception as ex:
        _fail("raised_dishwasher_height_consistency", str(ex))

    try:
        ok, msg = run_serbian_export_text_check()
        if ok:
            _ok("serbian_export_text", msg)
        else:
            _fail("serbian_export_text", msg)
    except Exception as ex:
        _fail("serbian_export_text", str(ex))

    try:
        ok, msg = run_worktop_excel_sheet_check()
        if ok:
            _ok("worktop_excel_sheet", msg)
        else:
            _fail("worktop_excel_sheet", msg)
    except Exception as ex:
        _fail("worktop_excel_sheet", str(ex))

    try:
        ok, msg = run_worktop_pdf_instruction_check()
        if ok:
            _ok("worktop_pdf_instruction", msg)
        else:
            _fail("worktop_pdf_instruction", msg)
    except Exception as ex:
        _fail("worktop_pdf_instruction", str(ex))

    try:
        ok, msg = run_excel_intro_sheet_check()
        if ok:
            _ok("excel_intro_sheet", msg)
        else:
            _fail("excel_intro_sheet", msg)
    except Exception as ex:
        _fail("excel_intro_sheet", str(ex))

    try:
        ok, msg = run_warning_translation_check()
        if ok:
            _ok("warning_translation", msg)
        else:
            _fail("warning_translation", msg)
    except Exception as ex:
        _fail("warning_translation", str(ex))

    return passed, failed


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="KrojnaListaPRO - svi automatski testovi")
    parser.add_argument("-v", "--verbose", action="store_true", help="Prikazi i PASS redove")
    parser.add_argument("--quick", action="store_true", help="Samo smoke (brzo)")
    args = parser.parse_args()

    t0 = time.time()

    _p("")
    _p("=" * 68)
    _p("  KrojnaListaPRO - automatski testovi")
    _p("=" * 68)

    total_pass = total_fail = 0

    # BLOK 1 — Smoke
    _p("")
    _p("  [1/3] SMOKE — logika, 2D/3D preview, room, layout")
    _p("  " + "-" * 50)
    sp, sf = run_smoke(args.verbose)
    total_pass += sp; total_fail += sf
    _p(f"  Smoke: {sp}/{sp+sf} PASS")

    if not args.quick:
        # BLOK 2 — Geometrija
        _p("")
        _p("  [2/3] GEOMETRIJA — dimenzije, overlap, krojna lista, okovi")
        _p("  " + "-" * 50)
        gp, gf = run_geometry(args.verbose)
        total_pass += gp; total_fail += gf
        _p(f"  Geometrija: {gp}/{gp+gf} PASS")

        # BLOK 3 — Export
        _p("")
        _p("  [3/3] EXPORT — PDF, Excel, sumarna KL")
        _p("  " + "-" * 50)
        ep, ef = run_export_tests(args.verbose)
        total_pass += ep; total_fail += ef
        _p(f"  Export: {ep}/{ep+ef} PASS")

    elapsed = time.time() - t0

    _p("")
    _p("=" * 68)
    if total_fail == 0:
        _p(f"  *** UKUPNO: {total_pass} PASS / 0 FAIL  ({elapsed:.1f}s)  SVE OK ***")
    else:
        _p(f"  *** UKUPNO: {total_pass} PASS / {total_fail} FAIL  ({elapsed:.1f}s) ***")
        _p(f"  Pogledaj FAIL redove iznad.")
    _p("=" * 68)
    _p("")

    sys.exit(0 if total_fail == 0 else 1)


if __name__ == "__main__":
    main()
