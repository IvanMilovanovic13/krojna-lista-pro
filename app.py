from __future__ import annotations

import logging
import pkgutil
from pathlib import Path
from importlib.util import find_spec

if not hasattr(pkgutil, "find_loader"):
    def _compat_find_loader(name: str):
        return find_spec(name)
    pkgutil.find_loader = _compat_find_loader

from fastapi import HTTPException, Request
from fastapi.responses import FileResponse
from nicegui import app, ui
from app_config import get_app_config, get_public_runtime_config
from auth_models import restore_session_from_token
from billing_models import get_billing_summary_for_email
from billing_webhooks import process_billing_webhook_payload
from lemon_squeezy_service import get_billing_runtime_status
from export_jobs import EXPORTS_DIR
from project_store import cleanup_auth_artifacts, get_export_job, get_project_store_runtime_info, init_project_store
from release_readiness import get_release_readiness_report
from state_logic import ensure_runtime_state_initialized, refresh_current_session_access, seed_demo_project_store, state
from ui_panels import render_toolbar, main_content
from ui_public_site import render_login_page, render_pricing_page, render_register_page, render_verify_email_page
GLOBAL_UI_STYLE = '''
<style>
  html, body, .nicegui-content {
    font-family: "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif !important;
    font-size: 12px !important;
    overflow-x: hidden !important;
  }

  .q-card,
  .q-expansion-item__container,
  .q-drawer,
  .q-table__container,
  .q-dialog__inner .q-card {
    background: #ffffff !important;
    border: 1px solid #d0d0d0 !important;
    border-radius: 4px !important;
    box-shadow: none !important;
  }

  .q-expansion-item__container > .q-item,
  .q-card > .q-card__section:first-child,
  .q-drawer .q-toolbar {
    background: #f2f4f7 !important;
  }

  .q-card__section,
  .q-item,
  .q-field__control,
  .q-table thead tr th,
  .q-table tbody tr td {
    padding: 8px !important;
  }

  .q-card,
  .q-expansion-item,
  .q-btn,
  .q-field,
  .q-table__container {
    margin: 6px !important;
  }

  .q-btn:not(.q-btn--round):not(.q-btn--fab):not(.toolbar-btn) {
    min-height: 30px !important;
    height: auto !important;
    padding: 4px 12px !important;
    background: #ffffff !important;
    color: #111111 !important;
    border-radius: 4px !important;
    border: 1px solid #111111 !important;
    box-shadow: none !important;
    text-transform: none !important;
    font-weight: 600 !important;
    line-height: 1.2 !important;
    max-width: 100% !important;
  }

  .q-btn:not(.q-btn--round):not(.q-btn--fab):not(.toolbar-btn):hover {
    background: #f2f2f2 !important;
  }

  .q-btn:not(.q-btn--round):not(.q-btn--fab):not(.toolbar-btn):active,
  .q-btn.q-btn--active:not(.q-btn--round):not(.q-btn--fab):not(.toolbar-btn) {
    border: 2px solid #111111 !important;
  }

  .q-btn:not(.q-btn--round):not(.q-btn--fab):not(.toolbar-btn) .q-icon,
  .q-btn:not(.q-btn--round):not(.q-btn--fab):not(.toolbar-btn) .q-btn__content,
  .q-btn:not(.q-btn--round):not(.q-btn--fab):not(.toolbar-btn) .q-btn__content * {
    color: #111111 !important;
  }

  /* Toolbar dugmad — potpuno flat, bez bordera */
  .toolbar-btn.q-btn {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    margin: 0 !important;
    padding: 0 14px !important;
    min-height: 42px !important;
    height: 42px !important;
    min-width: max-content !important;
    font-weight: 500 !important;
    color: #374151 !important;
  }
  .toolbar-btn.q-btn:hover {
    background: #f3f4f6 !important;
  }
  .toolbar-btn.q-btn .q-btn__content {
    gap: 6px !important;
    flex-wrap: nowrap !important;
  }
  .toolbar-btn.q-btn .q-icon,
  .toolbar-btn.q-btn .q-btn__content * {
    color: inherit !important;
  }
  .toolbar-btn--active.q-btn {
    color: #111827 !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #111827 !important;
  }
  .toolbar-btn--action.q-btn {
    border-left: 1px solid #e5e7eb !important;
    padding: 0 14px !important;
  }

  /* Jezik select — isti izgled kao toolbar dugmad */
  .toolbar-lang .q-field__control {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 12px !important;
    min-height: 42px !important;
    height: 42px !important;
  }
  .toolbar-lang .q-field__control:hover {
    background: #f3f4f6 !important;
  }
  .toolbar-lang .q-field__native,
  .toolbar-lang .q-field__input,
  .toolbar-lang .q-select__dropdown-icon {
    color: #374151 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
  }
  .toolbar-lang .q-field__marginal {
    height: 42px !important;
    color: #374151 !important;
  }

  .q-field__label {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    line-height: 1.15 !important;
    max-width: 100% !important;
  }

  .q-btn:not(.q-btn--round):not(.q-btn--fab) .q-btn__content {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 6px !important;
    max-width: 100% !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    line-height: 1.2 !important;
  }

  .q-chip,
  .q-tab,
  .q-tab__label {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    line-height: 1.2 !important;
    max-width: 100% !important;
  }

  .q-field__native,
  .q-field__input,
  .q-item__label,
  .q-select__dropdown-icon {
    line-height: 1.2 !important;
  }

  .q-field,
  .q-input,
  .q-select,
  .q-item,
  .q-card,
  .q-card__section {
    min-width: 0 !important;
    max-width: 100% !important;
  }

  .btn-wrap .q-btn__content {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    text-align: center !important;
    line-height: 1.15 !important;
  }

  .btn-wrap {
    min-height: 34px !important;
    height: auto !important;
  }

  .left-tabs-row .left-tab-btn {
    min-height: 24px !important;
    height: auto !important;
    padding: 3px 4px !important;
    margin: 0 !important;
    font-size: 10px !important;
    line-height: 1 !important;
    border-radius: 4px !important;
    border: 1px solid #d0d0d0 !important;
    box-shadow: none !important;
    text-transform: none !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    min-width: 28% !important;
  }

  .left-tabs-row .left-tab-active {
    background: #ffffff !important;
    color: #111111 !important;
    border: 2px solid #111111 !important;
  }

  /* KL Cut: neutralize blue utility accents used in legacy classes */
  [class*="bg-blue-"] {
    background: #ffffff !important;
    color: #111111 !important;
    border-color: #111111 !important;
  }

  [class*="text-blue-"],
  [class*="border-blue-"] {
    color: #111111 !important;
    border-color: #111111 !important;
  }

  .left-tabs-row .left-tab-inactive {
    background: #ffffff !important;
    color: #111111 !important;
    border-color: #111111 !important;
  }

  .left-tabs-row .q-btn__content {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    font-size: 10px !important;
    justify-content: center !important;
  }

  .left-tabs-row .left-tab-disabled,
  .left-tabs-row .left-tab-btn.q-btn--disabled {
    background: #e5e7eb !important;
    color: #6b7280 !important;
    border-color: #d0d0d0 !important;
    opacity: 1 !important;
  }

  .left-panel-compact .q-card,
  .left-panel-compact .q-expansion-item,
  .left-panel-compact .q-field {
    margin: 2px !important;
  }

  .left-panel-compact .q-card__section,
  .left-panel-compact .q-item,
  .left-panel-compact .q-field__control {
    padding: 4px !important;
  }

  .left-panel-compact .q-expansion-item__content > .q-card {
    margin-top: 2px !important;
    margin-bottom: 2px !important;
  }

  .left-panel-body {
    overflow-y: auto !important;
    overflow-x: hidden !important;
  }

  .left-panel-compact,
  .left-panel-compact * {
    max-width: 100% !important;
    box-sizing: border-box !important;
    overflow-wrap: break-word !important;
    word-break: break-word !important;
  }

  .left-panel-compact .q-scrollarea__content,
  .left-panel-compact .q-scrollarea__container,
  .left-panel-compact .q-scrollarea,
  .left-panel-compact .q-field,
  .left-panel-compact .q-select,
  .left-panel-compact .q-input,
  .left-panel-compact .q-btn,
  .left-panel-compact .q-card,
  .left-panel-compact .q-item {
    max-width: 100% !important;
  }

  .nacrt-fit-image {
    width: 100% !important;
    height: auto !important;
    max-width: 100% !important;
    max-height: 100% !important;
    object-fit: contain !important;
    display: block !important;
  }

  .nacrt-fit-image img,
  .nacrt-fit-image .q-img__image {
    width: 100% !important;
    height: auto !important;
    max-width: 100% !important;
    max-height: 100% !important;
    object-fit: contain !important;
    object-position: center center !important;
  }

  .sidebar-sticky-footer {
    background: #ffffff !important;
    border-top: 1px solid #d0d0d0 !important;
    padding: 8px !important;
    overflow-x: hidden !important;
  }

  /* Canvas toolbar: stop global margins/ellipsis from clipping control text */
  .canvas-toolbar .q-field,
  .canvas-toolbar .q-select,
  .canvas-toolbar .q-input,
  .canvas-toolbar .q-btn,
  .canvas-toolbar .q-checkbox {
    margin: 0 !important;
  }

  .canvas-toolbar .q-field__native,
  .canvas-toolbar .q-field__input,
  .canvas-toolbar .q-btn__content {
    white-space: nowrap !important;
    overflow: visible !important;
    text-overflow: clip !important;
  }

  .canvas-toolbar .q-field__control {
    padding: 0 8px !important;
    min-height: 28px !important;
    height: 28px !important;
    align-items: center !important;
  }

  .canvas-toolbar .q-field__native,
  .canvas-toolbar .q-field__input {
    padding: 0 !important;
    min-height: 0 !important;
    height: auto !important;
    line-height: 1.1 !important;
    display: flex !important;
    align-items: center !important;
  }

  .canvas-toolbar .q-select__dropdown-icon {
    align-self: center !important;
    margin-top: 0 !important;
  }

  .canvas-toolbar .q-field__control,
  .canvas-toolbar .q-btn {
    min-height: 28px !important;
    height: 28px !important;
  }

</style>
'''

app.add_static_files('/assets', str(Path(__file__).resolve().parent / 'assets'))


def _render_app_shell() -> None:
    ensure_runtime_state_initialized(allow_local_fallback=False)
    refresh_current_session_access()
    if not str(getattr(state, "current_user_email", "") or "").strip():
        ui.navigate.to("/login")
        return
    if str(getattr(state, "current_auth_mode", "") or "").strip().lower() == "local":
        ui.navigate.to("/login")
        return
    ui.query('body').style('margin: 0; padding: 0;')
    ui.add_head_html(GLOBAL_UI_STYLE)
    render_toolbar()
    main_content()


@ui.page('/')
def index(request: Request) -> None:
    render_login_page(request)


@ui.page('/app')
def app_entry() -> None:
    _render_app_shell()


@ui.page('/pricing')
def pricing_page() -> None:
    render_pricing_page()


@ui.page('/login')
def login_page(request: Request) -> None:
    render_login_page(request)


@ui.page('/nalog')
def account_compat_page(request: Request) -> None:
    render_login_page(request)


@ui.page('/register')
def register_page() -> None:
    render_register_page()


@ui.page('/verify-email')
def verify_email_page(request: Request) -> None:
    render_verify_email_page(request)


@app.post('/api/billing/webhook')
async def billing_webhook(request: Request) -> dict[str, str]:
    payload_bytes = await request.body()
    webhook_signature = str(request.headers.get('x-signature', '') or '')
    provided_secret = str(request.headers.get('x-webhook-secret', '') or '')
    return process_billing_webhook_payload(
        payload=None,
        provided_secret=provided_secret,
        payload_bytes=payload_bytes,
        webhook_signature=webhook_signature,
    )


@app.get('/exports/{job_id}/{filename}')
async def protected_export_download(job_id: int, filename: str, token: str = "") -> FileResponse:
    clean_token = str(token or "").strip()
    if not clean_token:
        raise HTTPException(status_code=401, detail="auth_required")

    session = restore_session_from_token(clean_token)
    if session is None:
        raise HTTPException(status_code=401, detail="invalid_session")

    tier = str(session.user.access_tier or "").strip().lower()
    billing_summary = get_billing_summary_for_email(str(session.user.email or ""))
    if billing_summary is not None:
        billing_status = str(billing_summary.billing_status or "").strip().lower()
        plan_code = str(billing_summary.plan_code or "").strip().lower()
        summary_tier = str(billing_summary.access_tier or "").strip().lower()
        if summary_tier == "admin":
            tier = "admin"
        elif billing_status in {"active", "paid", "on_trial"} and plan_code not in {"", "trial"}:
            tier = "paid"
    if tier not in {"paid", "admin", "local_beta"}:
        raise HTTPException(status_code=403, detail="paid_access_required")

    job = get_export_job(int(job_id), user_id=int(session.user.user_id))
    if job is None:
        raise HTTPException(status_code=404, detail="export_job_not_found")
    if str(job.status or "").strip().lower() != "done":
        raise HTTPException(status_code=409, detail="export_not_ready")

    safe_name = Path(str(filename or "")).name
    expected_ref = f"/exports/{int(job.id)}/{safe_name}"
    if str(job.result_ref or "").strip() != expected_ref:
        raise HTTPException(status_code=404, detail="export_result_mismatch")

    job_dir_path = EXPORTS_DIR / str(int(job.id))
    file_path = job_dir_path / safe_name
    if (not file_path.exists() or not file_path.is_file()) and str(job_dir_path) != str(EXPORTS_DIR):
        legacy_path = EXPORTS_DIR / safe_name
        if legacy_path.exists() and legacy_path.is_file():
            file_path = legacy_path
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="export_file_missing")

    media_type = "application/octet-stream"
    suffix = str(file_path.suffix or "").lower()
    if suffix == ".pdf":
        media_type = "application/pdf"
    elif suffix == ".xlsx":
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif suffix == ".csv":
        media_type = "text/csv"

    return FileResponse(path=file_path, filename=safe_name, media_type=media_type)


@app.get('/healthz')
async def healthz() -> dict[str, str]:
    cfg = get_app_config()
    runtime = get_project_store_runtime_info()
    return {
        "ok": "true",
        "app_env": str(cfg.app_env),
        "database_backend": str(runtime.get("backend", "")),
        "database_ready": str(runtime.get("ready", "")),
    }


@app.get('/readyz')
async def readyz() -> dict[str, str]:
    cfg = get_app_config()
    runtime = get_project_store_runtime_info()
    return {
        "ok": "true" if str(runtime.get("ready", "")).lower() == "true" else "false",
        "app_env": str(cfg.app_env),
        "database_backend": str(runtime.get("backend", "")),
        "database_ready": str(runtime.get("ready", "")),
        "billing_configured": "true" if bool(str(cfg.lemon_squeezy_api_key or "").strip()) else "false",
    }


@app.get('/ops/runtime')
async def ops_runtime() -> dict[str, object]:
    return {
        "app_config": get_public_runtime_config(),
        "project_store": get_project_store_runtime_info(),
        "stripe": get_billing_runtime_status(),
    }


@app.get('/ops/readiness')
async def ops_readiness(target: str = "production") -> dict[str, object]:
    return get_release_readiness_report(target=str(target))


def run_app() -> None:
    cfg = get_app_config()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    )
    init_project_store()
    cleanup_auth_artifacts()
    seed_demo_project_store()
    ui.run(
        title='krojna lista PRO',
        host=str(cfg.host or '127.0.0.1'),
        port=int(cfg.port),
        reload=False,
        workers=int(cfg.web_workers),
        storage_secret=str(cfg.secret_key),
    )


if __name__ == '__main__':
    run_app()
