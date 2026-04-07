# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Callable


def render_admin_tab(
    *,
    ui: Any,
    tr_fn: Callable[[str], str],
    get_release_readiness_summary: Callable[[str], dict[str, Any]],
    get_ops_runtime_summary: Callable[[], dict[str, Any]],
    get_visible_audit_logs: Callable[[int], list[dict[str, Any]]],
) -> None:
    runtime = get_ops_runtime_summary() or {}
    staging = get_release_readiness_summary("staging") or {}
    production = get_release_readiness_summary("production") or {}
    audit_logs = get_visible_audit_logs(20)

    def _render_readiness_card(title: str, payload: dict[str, Any]) -> None:
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        ready = bool(payload.get("ready", False))
        badge = tr_fn("ops.ready_yes") if ready else tr_fn("ops.ready_no")
        badge_classes = "text-green-700 bg-green-100" if ready else "text-red-700 bg-red-100"
        with ui.card().classes("w-full p-4 gap-3"):
            with ui.row().classes("w-full items-center justify-between"):
                ui.label(title).classes("text-lg font-bold")
                ui.label(badge).classes(f"px-2 py-1 rounded text-xs font-bold {badge_classes}")
            with ui.row().classes("w-full gap-3"):
                ui.label(tr_fn("ops.summary_passed_fmt", count=summary.get("passed", 0))).classes("text-sm text-slate-700")
                ui.label(tr_fn("ops.summary_blockers_fmt", count=summary.get("blockers", 0))).classes("text-sm text-slate-700")
                ui.label(tr_fn("ops.summary_warnings_fmt", count=summary.get("warnings", 0))).classes("text-sm text-slate-700")
            blockers = payload.get("blockers", []) if isinstance(payload.get("blockers", []), list) else []
            warnings = payload.get("warnings", []) if isinstance(payload.get("warnings", []), list) else []
            if blockers:
                ui.label(tr_fn("ops.blockers")).classes("text-sm font-semibold text-red-700")
                for item in blockers[:5]:
                    ui.label(f"- {item.get('label', '')}: {item.get('detail', '')}").classes("text-xs text-red-600")
            if warnings:
                ui.label(tr_fn("ops.warnings")).classes("text-sm font-semibold text-amber-700")
                for item in warnings[:3]:
                    ui.label(f"- {item.get('label', '')}: {item.get('detail', '')}").classes("text-xs text-amber-700")

    with ui.column().classes("w-full p-4 gap-4"):
        ui.label(tr_fn("ops.title")).classes("text-2xl font-bold")
        ui.label(tr_fn("ops.desc")).classes("text-sm text-slate-600")

        runtime_health = runtime.get("runtime_health", {}) if isinstance(runtime, dict) else {}
        health_ready = bool(runtime_health.get("ready", False))
        health_badge = tr_fn("ops.ready_yes") if health_ready else tr_fn("ops.ready_no")
        health_badge_classes = "text-green-700 bg-green-100" if health_ready else "text-red-700 bg-red-100"
        with ui.card().classes("w-full p-4 gap-3"):
            with ui.row().classes("w-full items-center justify-between"):
                ui.label(tr_fn("ops.runtime_health_title")).classes("text-lg font-bold")
                ui.label(health_badge).classes(f"px-2 py-1 rounded text-xs font-bold {health_badge_classes}")
            blockers = runtime_health.get("blockers", []) if isinstance(runtime_health.get("blockers", []), list) else []
            warnings = runtime_health.get("warnings", []) if isinstance(runtime_health.get("warnings", []), list) else []
            if blockers:
                ui.label(tr_fn("ops.blockers")).classes("text-sm font-semibold text-red-700")
                for item in blockers[:5]:
                    ui.label(f"- {item}").classes("text-xs text-red-600")
            if warnings:
                ui.label(tr_fn("ops.warnings")).classes("text-sm font-semibold text-amber-700")
                for item in warnings[:5]:
                    ui.label(f"- {item}").classes("text-xs text-amber-700")
            if not blockers and not warnings:
                ui.label(tr_fn("ops.runtime_health_ok")).classes("text-sm text-green-700")

        with ui.row().classes("w-full gap-4 items-stretch max-md:flex-col"):
            _render_readiness_card(tr_fn("ops.readiness_staging"), staging)
            _render_readiness_card(tr_fn("ops.readiness_production"), production)

        with ui.card().classes("w-full p-4 gap-3"):
            ui.label(tr_fn("ops.runtime_title")).classes("text-lg font-bold")
            app_cfg = runtime.get("app_config", {}) if isinstance(runtime, dict) else {}
            store = runtime.get("project_store", {}) if isinstance(runtime, dict) else {}
            auth_runtime = runtime.get("auth_runtime", {}) if isinstance(runtime, dict) else {}
            stripe = runtime.get("stripe", {}) if isinstance(runtime, dict) else {}
            with ui.row().classes("w-full gap-6 max-md:flex-col"):
                with ui.column().classes("gap-1"):
                    ui.label(tr_fn("ops.runtime_app")).classes("text-sm font-semibold")
                    ui.label(tr_fn("ops.runtime_app_env", value=app_cfg.get("app_env", "-"))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_base_url", value=app_cfg.get("base_url", "-"))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_host", value=app_cfg.get("host", "-"))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_port", value=app_cfg.get("port", "-"))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_web_workers", value=app_cfg.get("web_workers", "-"))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_debug", value=app_cfg.get("debug", "-"))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_database_url", value=app_cfg.get("database_url", "-"))).classes("text-xs text-slate-700 break-all")
                with ui.column().classes("gap-1"):
                    ui.label(tr_fn("ops.runtime_store")).classes("text-sm font-semibold")
                    ui.label(tr_fn("ops.runtime_store_backend", value=store.get("backend", "-"))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_store_ready", value=store.get("ready", "-"))).classes("text-xs text-slate-700")
                    ui.label(
                        tr_fn("ops.runtime_store_production_ready", ready=store.get("production_ready", "-"))
                    ).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_store_note", value=store.get("note", "-"))).classes("text-xs text-slate-700")
                    ui.label(
                        tr_fn("ops.runtime_store_deployment_note", note=store.get("deployment_note", "-"))
                    ).classes("text-xs text-slate-700")
                with ui.column().classes("gap-1"):
                    export_jobs = runtime.get("export_jobs", {}) if isinstance(runtime, dict) else {}
                    export_counts = runtime.get("export_job_counts", {}) if isinstance(runtime, dict) else {}
                    ui.label(tr_fn("ops.runtime_export")).classes("text-sm font-semibold")
                    ui.label(tr_fn("ops.runtime_export_mode", value=export_jobs.get("mode", "-"))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_export_max_workers", value=export_jobs.get("max_workers", "-"))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_export_max_active_per_user", value=export_jobs.get("max_active_jobs_per_user", "-"))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_export_worker_alive", value=export_jobs.get("worker_alive", "-"))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_export_worker_heartbeat_at", value=export_jobs.get("worker_heartbeat_at", "-"))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_export_total", count=export_counts.get("total", 0))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_export_queued", count=export_counts.get("queued", 0))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_export_running", count=export_counts.get("running", 0))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_export_done", count=export_counts.get("done", 0))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_export_failed", count=export_counts.get("failed", 0))).classes("text-xs text-slate-700")
                    ui.label(
                        tr_fn("ops.runtime_export_production_ready", ready=export_jobs.get("production_ready", "-"))
                    ).classes("text-xs text-slate-700")
                    ui.label(
                        tr_fn("ops.runtime_export_note", note=export_jobs.get("note", "-"))
                    ).classes("text-xs text-slate-700")
                with ui.column().classes("gap-1"):
                    ui.label(tr_fn("ops.runtime_auth")).classes("text-sm font-semibold")
                    ui.label(tr_fn("ops.runtime_auth_sessions", count=auth_runtime.get("active_sessions", 0))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_auth_reset_tokens", count=auth_runtime.get("active_reset_tokens", 0))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_auth_failed_attempts", count=auth_runtime.get("failed_login_attempts", 0))).classes("text-xs text-slate-700")
                with ui.column().classes("gap-1"):
                    ui.label(tr_fn("ops.runtime_billing_provider")).classes("text-sm font-semibold")
                    ui.label(tr_fn("ops.runtime_billing_provider_name", value=stripe.get("provider", "-"))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_billing_provider_api_key", value=stripe.get("has_api_key", stripe.get("has_secret_key", "-")))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_billing_provider_store", value=stripe.get("has_store_id", "-"))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_billing_provider_webhook", value=stripe.get("has_webhook_secret", "-"))).classes("text-xs text-slate-700")
                with ui.column().classes("gap-1"):
                    billing = runtime.get("billing_events", {}) if isinstance(runtime, dict) else {}
                    ui.label(tr_fn("ops.runtime_billing")).classes("text-sm font-semibold")
                    ui.label(tr_fn("ops.runtime_billing_total", count=billing.get("total", 0))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_billing_processed", count=billing.get("processed", 0))).classes("text-xs text-slate-700")
                    ui.label(tr_fn("ops.runtime_billing_failed", count=billing.get("failed", 0))).classes("text-xs text-slate-700")

        with ui.card().classes("w-full p-4 gap-3"):
            ui.label(tr_fn("ops.audit_title")).classes("text-lg font-bold")
            if not audit_logs:
                ui.label(tr_fn("ops.audit_empty")).classes("text-sm text-slate-500")
            else:
                columns = [
                    {"name": "created_at", "label": tr_fn("ops.audit_created"), "field": "created_at", "align": "left"},
                    {"name": "event_type", "label": tr_fn("ops.audit_event"), "field": "event_type", "align": "left"},
                    {"name": "status", "label": tr_fn("ops.audit_status"), "field": "status", "align": "left"},
                    {"name": "detail", "label": tr_fn("ops.audit_detail"), "field": "detail", "align": "left"},
                ]
                ui.table(columns=columns, rows=audit_logs, row_key="created_at").classes("w-full")
