# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import Request
from nicegui import ui

from i18n import get_language_options, tr
from state_logic import (
    _set_language,
    build_forgot_password_message,
    ensure_runtime_state_initialized,
    login_user_session,
    register_trial_user_session,
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
    with ui.column().classes("gap-0 ml-2"):
        ui.label("KROJNA").classes("public-brand")
        ui.label("LISTA PRO").classes("public-brand public-brand-sub")


def _topbar(*, action_label: str, action_target: str, current_path: str) -> None:
    from state_logic import state

    with ui.row().classes("public-topbar w-full items-center justify-between px-5 py-4"):
        _brand()
        with ui.row().classes("items-center gap-2"):
            ui.select(
                get_language_options(),
                value=str(getattr(state, "language", "sr") or "sr"),
                on_change=lambda e: (_set_language(str(e.value or "sr")), ui.navigate.to(current_path)),
            ).props("dense outlined").classes("public-lang")
            ui.button(_tr("public.home_btn"), on_click=lambda: ui.navigate.to("/pricing")).props("flat")
            ui.button(action_label, on_click=lambda: ui.navigate.to(action_target)).classes(
                "bg-[#111827] text-white"
            )


def _pricing_feature_card(title: str, desc: str) -> None:
    with ui.column().classes("public-card grow p-6 gap-2"):
        ui.label(title).classes("text-lg font-bold text-slate-900")
        ui.label(desc).classes("text-sm text-slate-600")


def render_pricing_page() -> None:
    _public_shell()
    with ui.column().classes("public-shell w-full"):
        _topbar(action_label=_tr("public.login_btn"), action_target="/login", current_path="/pricing")
        with ui.column().classes("w-full items-center px-6 py-12 gap-8"):
            with ui.column().classes("public-card info-card items-center gap-5"):
                ui.label(_tr("public.pricing_title")).classes("public-hero-title")
                ui.label(_tr("public.pricing_desc")).classes("public-hero-text max-w-3xl")
                with ui.row().classes("w-full justify-center gap-3 max-md:flex-col"):
                    ui.button(_tr("public.create_account_btn"), on_click=lambda: ui.navigate.to("/register")).classes(
                        "bg-[#2563eb] text-white px-8"
                    )
                    ui.button(_tr("public.have_account_btn"), on_click=lambda: ui.navigate.to("/login")).props("outline color=dark")
            with ui.row().classes("w-full max-w-6xl items-stretch gap-6 max-md:flex-col"):
                _pricing_feature_card(_tr("public.feature_easy_title"), _tr("public.feature_easy_desc"))
                _pricing_feature_card(_tr("public.feature_workshop_title"), _tr("public.feature_workshop_desc"))
                _pricing_feature_card(_tr("public.feature_saas_title"), _tr("public.feature_saas_desc"))


def _auth_footer() -> None:
    ui.label(_tr("public.footer")).classes("public-footer")


def render_login_page(request: Request | None = None) -> None:
    _public_shell()
    checkout_state = ""
    if request is not None:
        try:
            checkout_state = str(request.query_params.get("checkout", "") or "").strip().lower()
        except Exception:
            checkout_state = ""
    with ui.column().classes("public-shell w-full"):
        with ui.column().classes("w-full items-center justify-center px-6 py-14 gap-6"):
            with ui.column().classes("w-full items-center gap-1"):
                ui.label("KROJNA LISTA PRO").classes("text-[14px] font-bold tracking-[0.22em] text-slate-500")
                ui.label(_tr("public.login_title")).classes("public-hero-title")

            if checkout_state == "success":
                with ui.column().classes("public-card auth-card items-center gap-2 bg-[#eefbf3] border border-[#b7e4c7]"):
                    ui.label(_tr("public.checkout_success_title")).classes("text-base font-bold text-[#166534]")
                    ui.label(_tr("public.checkout_success_desc")).classes("text-sm text-[#166534] text-center")
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
                    ok, err = login_user_session(email_value, password_value)
                    if ok:
                        ui.notify(_tr("public.login_success"), type="positive")
                        ui.navigate.to("/app")
                    else:
                        ui.notify(err, type="negative", timeout=5000)

                async def _forgot() -> None:
                    email_value = await _resolve_input_value("public-login-email", str(login_email.value or ""))
                    ok, msg = build_forgot_password_message(str(email_value or ""))
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
        with ui.column().classes("w-full items-center justify-center px-6 py-14 gap-6"):
            with ui.column().classes("w-full items-center gap-2"):
                ui.label("KROJNA LISTA PRO").classes("text-[14px] font-bold tracking-[0.22em] text-slate-500")
                ui.label(_tr("public.register_title")).classes("public-hero-title")
                ui.label(_tr("public.register_desc")).classes("public-hero-text")

            with ui.column().classes("public-card auth-card items-center gap-4"):
                with ui.element("div").classes("public-auth-icon"):
                    ui.icon("lock", size="20px").classes("text-[#111827]")
                ui.label(_tr("public.sign_up_card_title")).classes("public-auth-title")
                first_name = ui.input(label=_tr("public.first_name_label")).props("id=public-register-first-name autocomplete=given-name").classes("w-full")
                last_name = ui.input(label=_tr("public.last_name_label")).props("id=public-register-last-name autocomplete=family-name").classes("w-full")
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
                    ok, err = register_trial_user_session(
                        str(register_email_value or register_email.value or ""),
                        display_name,
                        str(register_password_value or register_password.value or ""),
                    )
                    if ok:
                        ui.notify(_tr("public.register_success"), type="positive")
                        ui.navigate.to("/app")
                    else:
                        ui.notify(err, type="negative", timeout=5000)

                ui.button(_tr("public.sign_up_btn"), on_click=_register).classes("w-full bg-[#111827] text-white")
                with ui.row().classes("w-full justify-center public-auth-links"):
                    ui.link(_tr("public.already_have_account_link"), "/login")
                _auth_footer()
