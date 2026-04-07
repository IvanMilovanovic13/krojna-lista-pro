# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def run_ops_billing_runtime_check() -> tuple[bool, str]:
    state_logic = Path(__file__).with_name("state_logic.py").read_text(encoding="utf-8")
    admin_tab = Path(__file__).with_name("ui_admin_tab.py").read_text(encoding="utf-8")
    i18n = Path(__file__).with_name("i18n.py").read_text(encoding="utf-8")

    required_state_logic = [
        'from export_jobs import get_export_runtime_summary',
        'get_auth_runtime_summary,',
        'auth_runtime = get_auth_runtime_summary()',
        'export_jobs = get_export_runtime_summary()',
        'export_job_counts = get_export_job_summary()',
        '"billing_events": get_billing_event_summary(),',
        '"runtime_health": {',
    ]
    missing_state_logic = [item for item in required_state_logic if item not in state_logic]
    if missing_state_logic:
        return False, f"FAIL_ops_billing_state_logic:{', '.join(missing_state_logic)}"

    required_admin = [
        'runtime.get("billing_events", {})',
        'runtime.get("export_jobs", {})',
        'runtime.get("export_job_counts", {})',
        'runtime.get("auth_runtime", {})',
        'runtime.get("runtime_health", {})',
        'tr_fn("ops.runtime_health_title")',
        'tr_fn("ops.runtime_health_ok")',
        'tr_fn("ops.runtime_billing")',
        'tr_fn("ops.runtime_host", value=app_cfg.get("host", "-"))',
        'tr_fn("ops.runtime_port", value=app_cfg.get("port", "-"))',
        'tr_fn("ops.runtime_web_workers", value=app_cfg.get("web_workers", "-"))',
        'tr_fn("ops.runtime_debug", value=app_cfg.get("debug", "-"))',
        'tr_fn("ops.runtime_store_production_ready", ready=store.get("production_ready", "-"))',
        'tr_fn("ops.runtime_store_deployment_note", note=store.get("deployment_note", "-"))',
        'tr_fn("ops.runtime_auth")',
        'tr_fn("ops.runtime_auth_sessions", count=auth_runtime.get("active_sessions", 0))',
        'tr_fn("ops.runtime_auth_reset_tokens", count=auth_runtime.get("active_reset_tokens", 0))',
        'tr_fn("ops.runtime_auth_failed_attempts", count=auth_runtime.get("failed_login_attempts", 0))',
        'tr_fn("ops.runtime_export")',
        'tr_fn("ops.runtime_export_max_active_per_user", value=export_jobs.get("max_active_jobs_per_user", "-"))',
        'tr_fn("ops.runtime_export_worker_alive", value=export_jobs.get("worker_alive", "-"))',
        'tr_fn("ops.runtime_export_worker_heartbeat_at", value=export_jobs.get("worker_heartbeat_at", "-"))',
        'tr_fn("ops.runtime_export_total", count=export_counts.get("total", 0))',
        'tr_fn("ops.runtime_export_queued", count=export_counts.get("queued", 0))',
        'tr_fn("ops.runtime_export_running", count=export_counts.get("running", 0))',
        'tr_fn("ops.runtime_export_done", count=export_counts.get("done", 0))',
        'tr_fn("ops.runtime_export_failed", count=export_counts.get("failed", 0))',
        'tr_fn("ops.runtime_export_production_ready", ready=export_jobs.get("production_ready", "-"))',
        'tr_fn("ops.runtime_export_note", note=export_jobs.get("note", "-"))',
        'tr_fn("ops.runtime_billing_provider")',
        'tr_fn("ops.runtime_billing_provider_name", value=stripe.get("provider", "-"))',
        'tr_fn("ops.runtime_billing_total", count=billing.get("total", 0))',
        'tr_fn("ops.runtime_billing_processed", count=billing.get("processed", 0))',
        'tr_fn("ops.runtime_billing_failed", count=billing.get("failed", 0))',
    ]
    missing_admin = [item for item in required_admin if item not in admin_tab]
    if missing_admin:
        return False, f"FAIL_ops_billing_admin:{', '.join(missing_admin)}"

    required_i18n = [
        '"ops.runtime_billing": "Billing eventi"',
        '"ops.runtime_health_title": "Runtime health"',
        '"ops.runtime_health_ok": "Nema aktivnih runtime blockera ni upozorenja."',
        '"ops.runtime_host": "HOST: {value}"',
        '"ops.runtime_web_workers": "WEB_WORKERS: {value}"',
        '"ops.runtime_store_production_ready": "production ready: {ready}"',
        '"ops.runtime_store_deployment_note": "deploy: {note}"',
        '"ops.runtime_auth": "Auth i session"',
        '"ops.runtime_auth_sessions": "aktivne sesije: {count}"',
        '"ops.runtime_auth_reset_tokens": "aktivni reset tokeni: {count}"',
        '"ops.runtime_auth_failed_attempts": "failed login attempts: {count}"',
        '"ops.runtime_export": "Export worker"',
        '"ops.runtime_export_total": "ukupno: {count}"',
        '"ops.runtime_export_queued": "queued: {count}"',
        '"ops.runtime_export_running": "running: {count}"',
        '"ops.runtime_export_done": "done: {count}"',
        '"ops.runtime_export_failed": "failed: {count}"',
        '"ops.runtime_export_production_ready": "production ready: {ready}"',
        '"ops.runtime_export_note": "worker: {note}"',
        '"ops.runtime_billing_provider": "Billing provider"',
        '"ops.runtime_billing_total": "ukupno: {count}"',
        '"ops.runtime_billing_failed": "greske: {count}"',
        '"ops.runtime_billing": "Billing events"',
        '"ops.runtime_health_title": "Runtime health"',
        '"ops.runtime_health_ok": "There are no active runtime blockers or warnings."',
        '"ops.runtime_host": "HOST: {value}"',
        '"ops.runtime_web_workers": "WEB_WORKERS: {value}"',
        '"ops.runtime_store_production_ready": "production ready: {ready}"',
        '"ops.runtime_store_deployment_note": "deploy: {note}"',
        '"ops.runtime_auth": "Auth and session"',
        '"ops.runtime_auth_sessions": "active sessions: {count}"',
        '"ops.runtime_auth_reset_tokens": "active reset tokens: {count}"',
        '"ops.runtime_auth_failed_attempts": "failed login attempts: {count}"',
        '"ops.runtime_export": "Export worker"',
        '"ops.runtime_export_total": "total: {count}"',
        '"ops.runtime_export_queued": "queued: {count}"',
        '"ops.runtime_export_running": "running: {count}"',
        '"ops.runtime_export_done": "done: {count}"',
        '"ops.runtime_export_failed": "failed: {count}"',
        '"ops.runtime_export_production_ready": "production ready: {ready}"',
        '"ops.runtime_export_note": "worker: {note}"',
        '"ops.runtime_billing_provider": "Billing provider"',
        '"ops.runtime_billing_total": "total: {count}"',
        '"ops.runtime_billing_failed": "failed: {count}"',
    ]
    missing_i18n = [item for item in required_i18n if item not in i18n]
    if missing_i18n:
        return False, f"FAIL_ops_billing_i18n:{', '.join(missing_i18n)}"

    return True, "OK"
