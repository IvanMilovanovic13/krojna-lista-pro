# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio

from fastapi import Request
from nicegui import ui

from i18n import get_language_options, tr
from state_logic import (
    _set_language,
    build_forgot_password_message,
    ensure_runtime_state_initialized,
    refresh_current_session_access,
    login_user_session,
    register_trial_user_session,
    reset_password_with_token,
)


PUBLIC_PAGE_STYLE = """
<style>
  .public-shell {
    min-height: 100vh;
    background: #ffffff;
  }
  .public-brand {
    font-size: 22px;
    font-weight: 800;
    line-height: 0.95;
    letter-spacing: 0.02em;
    color: #111827;
  }
  .public-brand-sub {
    color: #9ca3af;
  }
  .public-lang {
    min-width: 132px;
  }
  .public-hero-title {
    font-size: 34px;
    line-height: 1.08;
    font-weight: 800;
    color: #111827;
    text-align: center;
  }
  .public-hero-text {
    font-size: 15px;
    color: #6b7280;
    text-align: center;
  }
  .public-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
  }
  .public-card.auth-card {
    width: 100%;
    max-width: 360px;
    padding: 28px 24px;
    border-radius: 12px;
    box-shadow: none;
  }
  .public-card.info-card {
    width: 100%;
    max-width: 980px;
    padding: 40px 28px;
  }
  .public-auth-title {
    font-size: 17px;
    font-weight: 700;
    color: #111827;
    text-align: center;
  }
  .public-auth-links {
    font-size: 13px;
    color: #6b7280;
  }
  .public-auth-links a {
    color: #111827;
    text-decoration: none;
    font-weight: 600;
  }
  .public-auth-links a:hover {
    text-decoration: underline;
  }
  .public-auth-icon {
    width: 42px;
    height: 42px;
    border: 1px solid #111827;
    border-radius: 9999px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 4px;
  }
  .public-footer {
    font-size: 12px;
    color: #9ca3af;
    text-align: center;
  }
</style>
"""


def _public_shell() -> None:
    ensure_runtime_state_initialized(allow_local_fallback=False)
    ui.add_head_html(PUBLIC_PAGE_STYLE)
    ui.query("body").style("margin: 0; background: #f8fafc;")


def _tr(key: str, **fmt: object) -> str:
    from state_logic import state

    return tr(key, str(getattr(state, "language", "sr") or "sr"), **fmt)


def _brand() -> None:
    ui.label(_tr("wizard.title_app")).classes("public-brand ml-2")


def _split_brand_title() -> tuple[str, str]:
    title = str(_tr("wizard.title_app") or "").strip()
    if title.upper().endswith(" PRO"):
        return title[:-4].strip(), "PRO"
    return title, ""


def _hero_brand(caption: str = "") -> None:
    brand_main, brand_badge = _split_brand_title()
    with ui.column().classes("w-full items-center gap-2"):
        with ui.row().classes("items-start justify-center gap-2"):
            ui.label(brand_main).classes(
                "text-[52px] font-black tracking-[-0.05em] leading-none text-[#6d8ee8] "
                "drop-shadow-[0_8px_24px_rgba(109,142,232,0.18)] max-md:text-[36px]"
            )
            if brand_badge:
                ui.label(brand_badge).classes(
                    "mt-1 rounded-[10px] border-2 border-[#6d8ee8] px-2 py-0.5 text-[18px] font-black "
                    "leading-none tracking-[-0.02em] text-[#6d8ee8] max-md:text-[14px]"
                )
        if caption:
            ui.label(caption).classes(
                "text-xs font-semibold uppercase tracking-[0.28em] text-[#b4bfdc] text-center"
            )


def _topbar(*, action_label: str, action_target: str, current_path: str) -> None:
    from state_logic import state

    with ui.row().classes("public-topbar w-full items-center justify-between px-5 py-4"):
        ui.element("div").classes("min-w-[120px]")
        with ui.row().classes("items-center gap-2"):
            _language_options = get_language_options()
            _current_language = str(getattr(state, "language", "sr") or "sr")
            ui.select(
                _language_options,
                value=_current_language if _current_language in _language_options else "sr",
                on_change=lambda e: (_set_language(str(e.value or "sr")), ui.navigate.to(current_path)),
            ).props("dense outlined").classes("public-lang")
            ui.button(_tr("public.home_btn"), on_click=lambda: ui.navigate.to("/pricing")).props("flat")
            ui.button(action_label, on_click=lambda: ui.navigate.to(action_target)).classes(
                "bg-[#111827] text-white"
            )


def _pricing_feature_card(title: str, desc: str, icon: str = "check_circle") -> None:
    with ui.column().classes("public-card grow p-6 gap-3"):
        ui.icon(icon).classes("text-[#2563eb] text-[28px]")
        ui.label(title).classes("text-lg font-bold text-slate-900")
        ui.label(desc).classes("text-sm text-slate-600 leading-relaxed")


def _plan_feature(text: str, included: bool = True) -> None:
    with ui.row().classes("w-full items-start gap-2"):
        ui.icon("check" if included else "remove").classes(
            f"text-[16px] mt-0.5 {'text-[#2563eb]' if included else 'text-gray-300'}"
        )
        ui.label(text).classes(f"text-sm {'text-gray-700' if included else 'text-gray-400'}")


def render_pricing_page() -> None:
    _public_shell()
    with ui.column().classes("public-shell w-full"):
        _topbar(action_label=_tr("public.login_btn"), action_target="/login", current_path="/pricing")

        # ── Hero ──────────────────────────────────────────────────────────
        with ui.column().classes("w-full items-center bg-white px-6 pt-16 pb-12 gap-6"):
            _hero_brand()
            ui.label(_tr("public.pricing_title")).classes(
                "text-[36px] font-black text-slate-900 text-center leading-tight max-w-3xl max-md:text-[26px]"
            )
            ui.label(_tr("public.pricing_desc")).classes(
                "text-[16px] text-slate-500 text-center max-w-2xl leading-relaxed"
            )
            with ui.row().classes("gap-3 flex-wrap justify-center mt-2"):
                ui.button(
                    _tr("public.create_account_btn"),
                    on_click=lambda: ui.navigate.to("/register"),
                ).classes("bg-[#2563eb] text-white px-8 py-3 text-base font-semibold")
                ui.button(
                    _tr("public.have_account_btn"),
                    on_click=lambda: ui.navigate.to("/login"),
                ).props("outline color=dark").classes("px-6 py-3 text-base")

        # ── Kako radi ─────────────────────────────────────────────────────
        with ui.column().classes("w-full items-center bg-[#f8fafc] px-6 py-14 gap-8"):
            ui.label(_tr("public.how_it_works_title")).classes(
                "text-2xl font-black text-slate-900 uppercase tracking-wide text-center"
            )
            with ui.row().classes("w-full max-w-5xl gap-6 justify-center max-md:flex-col"):
                for step_title, step_desc, icon_name in (
                    (_tr("public.how_step1_title"), _tr("public.how_step1_desc"), "straighten"),
                    (_tr("public.how_step2_title"), _tr("public.how_step2_desc"), "kitchen"),
                    (_tr("public.how_step3_title"), _tr("public.how_step3_desc"), "file_download"),
                ):
                    with ui.column().classes("public-card flex-1 p-7 gap-3 items-center text-center"):
                        ui.icon(icon_name).classes("text-[#2563eb] text-[40px]")
                        ui.label(step_title).classes("text-base font-bold text-slate-900")
                        ui.label(step_desc).classes("text-sm text-slate-500 leading-relaxed")

        # ── Feature cards ─────────────────────────────────────────────────
        with ui.column().classes("w-full items-center bg-white px-6 py-14 gap-8"):
            with ui.row().classes("w-full max-w-5xl items-stretch gap-6 max-md:flex-col"):
                _pricing_feature_card(
                    _tr("public.feature_easy_title"),
                    _tr("public.feature_easy_desc"),
                    "touch_app",
                )
                _pricing_feature_card(
                    _tr("public.feature_workshop_title"),
                    _tr("public.feature_workshop_desc"),
                    "content_cut",
                )
                _pricing_feature_card(
                    _tr("public.feature_saas_title"),
                    _tr("public.feature_saas_desc"),
                    "cloud_done",
                )

        # ── Planovi ───────────────────────────────────────────────────────
        with ui.column().classes("w-full items-center bg-[#f8fafc] px-6 py-14 gap-8"):
            ui.label(_tr("public.pricing_plans_title")).classes(
                "text-2xl font-black text-slate-900 uppercase tracking-wide text-center"
            )
            with ui.row().classes("w-full max-w-3xl gap-6 justify-center max-md:flex-col"):
                # Trial plan
                with ui.column().classes("public-card flex-1 p-8 gap-4"):
                    ui.label(_tr("public.plan_trial_title")).classes("text-xl font-black text-slate-900")
                    ui.label("Besplatno").classes("text-3xl font-black text-slate-900")
                    ui.label(_tr("public.plan_trial_desc")).classes("text-sm text-slate-500")
                    ui.separator()
                    _plan_feature(_tr("public.plan_trial_feature1"))
                    _plan_feature(_tr("public.plan_trial_feature2"))
                    _plan_feature(_tr("public.plan_trial_feature3"))
                    _plan_feature(_tr("public.plan_pro_feature1"), included=False)
                    _plan_feature(_tr("public.plan_pro_feature2"), included=False)
                    ui.button(
                        _tr("public.create_account_btn"),
                        on_click=lambda: ui.navigate.to("/register"),
                    ).classes("w-full bg-white text-[#111] border border-[#111] mt-auto")

                # PRO plan
                with ui.column().classes(
                    "public-card flex-1 p-8 gap-4 border-2 border-[#2563eb] relative overflow-hidden"
                ):
                    with ui.element("div").classes(
                        "absolute top-4 right-4 bg-[#2563eb] text-white text-xs font-bold px-3 py-1 rounded-full"
                    ):
                        ui.label("PRO")
                    ui.label(_tr("public.plan_pro_title")).classes("text-xl font-black text-[#2563eb]")
                    ui.label(_tr("public.plan_pro_price")).classes("text-xl font-black text-slate-900")
                    ui.label(_tr("public.plan_pro_desc")).classes("text-sm text-slate-500")
                    ui.separator()
                    _plan_feature(_tr("public.plan_trial_feature1"))
                    _plan_feature(_tr("public.plan_trial_feature2"))
                    _plan_feature(_tr("public.plan_trial_feature3"))
                    _plan_feature(_tr("public.plan_pro_feature1"))
                    _plan_feature(_tr("public.plan_pro_feature2"))
                    _plan_feature(_tr("public.plan_pro_feature3"))
                    _plan_feature(_tr("public.plan_pro_feature4"))
                    ui.button(
                        _tr("public.create_account_btn"),
                        on_click=lambda: ui.navigate.to("/register"),
                    ).classes("w-full bg-[#2563eb] text-white mt-auto")

        # ── CTA na dnu ────────────────────────────────────────────────────
        with ui.column().classes("w-full items-center bg-[#111827] px-6 py-16 gap-5"):
            ui.label(_tr("public.pricing_cta_title")).classes(
                "text-3xl font-black text-white text-center"
            )
            ui.label(_tr("public.pricing_cta_desc")).classes(
                "text-base text-gray-400 text-center"
            )
            ui.button(
                _tr("public.create_account_btn"),
                on_click=lambda: ui.navigate.to("/register"),
            ).classes("bg-white text-[#111827] px-10 py-3 text-base font-bold")

        # ── Footer ────────────────────────────────────────────────────────
        with ui.row().classes(
            "w-full justify-center items-center gap-4 py-6 bg-white"
            " border-t border-gray-100"
        ):
            ui.html('<span style="font-size:12px;color:#9ca3af;">CabinetCutPro &copy; 2026</span>')
            ui.html('<span style="color:#e5e7eb;">|</span>')
            ui.html(
                '<a href="/privacy" style="font-size:12px;color:#6b7280;'
                'text-decoration:none;">Privacy Policy</a>'
            )
            ui.html('<span style="color:#e5e7eb;">|</span>')
            ui.html(
                '<a href="/terms" style="font-size:12px;color:#6b7280;'
                'text-decoration:none;">Terms of Service</a>'
            )
            ui.html('<span style="color:#e5e7eb;">|</span>')
            ui.html(
                '<a href="mailto:ivan_milovanovic@live.com" style="font-size:12px;'
                'color:#6b7280;text-decoration:none;">Contact</a>'
            )


def _auth_footer() -> None:
    with ui.row().classes("justify-center items-center gap-3 flex-wrap"):
        ui.html('<span style="font-size:12px;color:#9ca3af;">CabinetCutPro &copy; 2026</span>')
        ui.html(
            '<a href="/privacy" style="font-size:12px;color:#9ca3af;text-decoration:none;">'
            'Privacy</a>'
        )
        ui.html(
            '<a href="/terms" style="font-size:12px;color:#9ca3af;text-decoration:none;">'
            'Terms</a>'
        )


def render_login_page(request: Request | None = None) -> None:
    _public_shell()
    checkout_state = ""
    if request is not None:
        try:
            checkout_state = str(request.query_params.get("checkout", "") or "").strip().lower()
        except Exception:
            checkout_state = ""
    if checkout_state == "success":
        refresh_current_session_access()
    with ui.column().classes("public-shell w-full"):
        _topbar(action_label=_tr("public.create_account_btn"), action_target="/register", current_path="/login")
        with ui.column().classes("w-full items-center justify-center px-6 py-14 gap-6"):
            with ui.column().classes("w-full items-center gap-3"):
                _hero_brand("Dashboard / Projekti")
                ui.label(_tr("public.login_title")).classes("public-hero-title")
                ui.label(_tr("nova.auth_login_desc")).classes("public-hero-text max-w-xl")

            if checkout_state == "success":
                with ui.column().classes("public-card auth-card items-center gap-2 bg-[#eefbf3] border border-[#b7e4c7]"):
                    ui.label(_tr("public.checkout_success_title")).classes("text-base font-bold text-[#166534]")
                    ui.label(_tr("public.checkout_success_desc")).classes("text-sm text-[#166534] text-center")
                    from state_logic import state
                    if str(getattr(state, "current_user_email", "") or "").strip() and str(getattr(state, "current_auth_mode", "") or "").strip().lower() != "local":
                        ui.button(_tr("nova.paid_success_continue_btn"), on_click=lambda: ui.navigate.to("/app")).classes(
                            "w-full bg-[#166534] text-white"
                        )
            elif checkout_state == "cancel":
                with ui.column().classes("public-card auth-card items-center gap-2 bg-[#fff7ed] border border-[#fed7aa]"):
                    ui.label(_tr("public.checkout_cancel_title")).classes("text-base font-bold text-[#9a3412]")
                    ui.label(_tr("public.checkout_cancel_desc")).classes("text-sm text-[#9a3412] text-center")

            with ui.column().classes("public-card auth-card items-center gap-4"):
                with ui.element("div").classes("public-auth-icon"):
                    ui.icon("lock", size="20px").classes("text-[#111827]")
                ui.label(_tr("public.sign_in_card_title")).classes("public-auth-title")
                login_email = ui.input(label=_tr("public.email_label")).props("id=public-login-email autocomplete=username").classes("w-full")
                login_password = ui.input(
                    label=_tr("public.password_label"),
                    password=True,
                    password_toggle_button=True,
                ).props("id=public-login-password autocomplete=current-password").classes("w-full")
                async def _resolve_input_value(element_id: str, fallback: str = "") -> str:
                    try:
                        value = await ui.run_javascript(
                            f"""
                            (() => {{
                                const root = document.getElementById('{element_id}');
                                if (!root) return '';
                                const input = root.querySelector('input');
                                return input ? (input.value || '') : '';
                            }})()
                            """
                        )
                        clean = str(value or "").strip()
                        return clean if clean else str(fallback or "").strip()
                    except Exception:
                        return str(fallback or "").strip()

                async def _login() -> None:
                    email_value = await _resolve_input_value("public-login-email", str(login_email.value or ""))
                    password_value = await _resolve_input_value("public-login-password", str(login_password.value or ""))
                    ok, err = await asyncio.to_thread(login_user_session, email_value, password_value)
                    if ok:
                        ui.notify(_tr("public.login_success"), type="positive")
                        ui.navigate.to("/app")
                    else:
                        ui.notify(err, type="negative", timeout=5000)

                async def _forgot() -> None:
                    email_value = await _resolve_input_value("public-login-email", str(login_email.value or ""))
                    ok, msg = await asyncio.to_thread(build_forgot_password_message, str(email_value or ""))
                    ui.notify(msg, type="info" if ok else "negative", timeout=6000)

                ui.button(_tr("public.sign_in_btn"), on_click=_login).classes("w-full bg-[#111827] text-white")
                with ui.row().classes("w-full items-center justify-between public-auth-links"):
                    ui.link(_tr("public.forgot_password_link"), "#").on("click", lambda _e: _forgot())
                    ui.label("")
                    ui.link(_tr("public.sign_up_link"), "/register")
                _auth_footer()


def render_register_page() -> None:
    _public_shell()
    with ui.column().classes("public-shell w-full"):
        _topbar(action_label=_tr("public.login_btn"), action_target="/login", current_path="/register")
        with ui.column().classes("w-full items-center justify-center px-6 py-14 gap-6"):
            with ui.column().classes("w-full items-center gap-3"):
                _hero_brand("Dashboard / Projekti")
                ui.label(_tr("public.register_title")).classes("public-hero-title")
                ui.label(_tr("public.register_desc")).classes("public-hero-text")

            with ui.column().classes("public-card auth-card items-center gap-4"):
                with ui.element("div").classes("public-auth-icon"):
                    ui.icon("lock", size="20px").classes("text-[#111827]")
                ui.label(_tr("public.sign_up_card_title")).classes("public-auth-title")
                first_name = ui.input(label=_tr("public.first_name_label")).props("id=public-register-first-name autocomplete=given-name").classes("w-full")
                last_name = ui.input(label=_tr("public.last_name_label")).props("id=public-register-last-name autocomplete=family-name").classes("w-full")
                register_username = ui.input(label=_tr("public.username_label")).props("id=public-register-username autocomplete=username").classes("w-full")
                register_email = ui.input(label=_tr("public.email_address_label")).props("id=public-register-email autocomplete=email").classes("w-full")
                register_password = ui.input(
                    label=_tr("public.password_label"), password=True, password_toggle_button=True
                ).props("id=public-register-password autocomplete=new-password").classes("w-full")

                async def _register() -> None:
                    first_name_value = await ui.run_javascript(
                        """
                        (() => {
                            const root = document.getElementById('public-register-first-name');
                            const input = root ? root.querySelector('input') : null;
                            return input ? (input.value || '') : '';
                        })()
                        """
                    )
                    last_name_value = await ui.run_javascript(
                        """
                        (() => {
                            const root = document.getElementById('public-register-last-name');
                            const input = root ? root.querySelector('input') : null;
                            return input ? (input.value || '') : '';
                        })()
                        """
                    )
                    register_email_value = await ui.run_javascript(
                        """
                        (() => {
                            const root = document.getElementById('public-register-email');
                            const input = root ? root.querySelector('input') : null;
                            return input ? (input.value || '') : '';
                        })()
                        """
                    )
                    register_username_value = await ui.run_javascript(
                        """
                        (() => {
                            const root = document.getElementById('public-register-username');
                            const input = root ? root.querySelector('input') : null;
                            return input ? (input.value || '') : '';
                        })()
                        """
                    )
                    register_password_value = await ui.run_javascript(
                        """
                        (() => {
                            const root = document.getElementById('public-register-password');
                            const input = root ? root.querySelector('input') : null;
                            return input ? (input.value || '') : '';
                        })()
                        """
                    )
                    display_name = " ".join(
                        [
                            part
                            for part in [
                                str(first_name_value or first_name.value or "").strip(),
                                str(last_name_value or last_name.value or "").strip(),
                            ]
                            if part
                        ]
                    ).strip()
                    ok, err = await asyncio.to_thread(
                        register_trial_user_session,
                        str(register_email_value or register_email.value or ""),
                        display_name,
                        str(register_password_value or register_password.value or ""),
                        str(register_username_value or register_username.value or ""),
                    )
                    if ok:
                        ui.notify(str(err or _tr("public.register_success")), type="positive", timeout=9000)
                        ui.navigate.to("/login")
                    else:
                        ui.notify(err, type="negative", timeout=5000)

                ui.button(_tr("public.sign_up_btn"), on_click=_register).classes("w-full bg-[#111827] text-white")
                with ui.row().classes("w-full justify-center public-auth-links"):
                    ui.link(_tr("public.already_have_account_link"), "/login")
                _auth_footer()


def render_verify_email_page(request: Request | None = None) -> None:
    from state_logic import verify_email_with_token

    _public_shell()
    token = ""
    if request is not None:
        try:
            token = str(request.query_params.get("token", "") or "").strip()
        except Exception:
            token = ""
    ok, msg = verify_email_with_token(token) if token else (False, "Verifikacioni token nedostaje.")
    with ui.column().classes("public-shell w-full"):
        _topbar(action_label=_tr("public.login_btn"), action_target="/login", current_path="/verify-email")
        with ui.column().classes("w-full items-center justify-center px-6 py-14 gap-6"):
            with ui.column().classes("public-card auth-card items-center gap-4"):
                with ui.element("div").classes("public-auth-icon"):
                    ui.icon("verified" if ok else "warning", size="20px").classes("text-[#111827]")
                ui.label(_tr("public.verify_email_title")).classes("public-auth-title")
                ui.label(str(msg or "")).classes("text-sm text-slate-700 text-center")
                ui.button(_tr("public.login_btn"), on_click=lambda: ui.navigate.to("/login")).classes(
                    "w-full bg-[#111827] text-white"
                )
                _auth_footer()


def render_reset_password_page(request: Request | None = None) -> None:
    token = ""
    if request is not None:
        try:
            token = str(request.query_params.get("token", "") or "").strip()
        except Exception:
            token = ""

    _public_shell()
    with ui.column().classes("public-shell w-full"):
        _topbar(action_label=_tr("public.login_btn"), action_target="/login", current_path="/reset-password")
        with ui.column().classes("w-full items-center justify-center px-6 py-14 gap-6"):
            with ui.column().classes("w-full items-center gap-3"):
                _hero_brand("Dashboard / Projekti")
                ui.label(_tr("public.reset_password_title")).classes("public-hero-title")
                ui.label(_tr("public.reset_password_desc")).classes("public-hero-text max-w-xl")

            with ui.column().classes("public-card auth-card items-center gap-4"):
                with ui.element("div").classes("public-auth-icon"):
                    ui.icon("lock_reset", size="20px").classes("text-[#111827]")
                if not token:
                    ui.label(_tr("public.reset_password_missing_token")).classes("public-auth-title")
                    ui.button(_tr("public.login_btn"), on_click=lambda: ui.navigate.to("/login")).classes(
                        "w-full bg-[#111827] text-white"
                    )
                    _auth_footer()
                    return

                ui.label(_tr("public.reset_password_card_title")).classes("public-auth-title")
                new_password = ui.input(
                    label=_tr("public.new_password_label"),
                    password=True,
                    password_toggle_button=True,
                ).props("id=public-reset-password autocomplete=new-password").classes("w-full")
                confirm_password = ui.input(
                    label=_tr("public.confirm_password_label"),
                    password=True,
                    password_toggle_button=True,
                ).props("id=public-reset-confirm-password autocomplete=new-password").classes("w-full")

                async def _resolve_input_value(element_id: str, fallback: str = "") -> str:
                    try:
                        value = await ui.run_javascript(
                            f"""
                            (() => {{
                                const root = document.getElementById('{element_id}');
                                const input = root ? root.querySelector('input') : null;
                                return input ? (input.value || '') : '';
                            }})()
                            """
                        )
                        clean = str(value or "").strip()
                        return clean if clean else str(fallback or "").strip()
                    except Exception:
                        return str(fallback or "").strip()

                async def _reset() -> None:
                    new_password_value = await _resolve_input_value(
                        "public-reset-password",
                        str(new_password.value or ""),
                    )
                    confirm_password_value = await _resolve_input_value(
                        "public-reset-confirm-password",
                        str(confirm_password.value or ""),
                    )
                    if new_password_value != confirm_password_value:
                        ui.notify(_tr("public.password_mismatch"), type="negative", timeout=5000)
                        return
                    ok, msg = await asyncio.to_thread(reset_password_with_token, token, new_password_value)
                    if ok:
                        ui.notify(_tr("public.reset_password_success"), type="positive", timeout=6000)
                        ui.navigate.to("/login")
                    else:
                        ui.notify(str(msg or ""), type="negative", timeout=6000)

                ui.button(_tr("public.reset_password_btn"), on_click=_reset).classes("w-full bg-[#111827] text-white")
                _auth_footer()
