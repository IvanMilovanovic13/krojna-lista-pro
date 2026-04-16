# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Callable


def render_access_gate(
    *,
    ui: Any,
    state: Any,
    tr_fn: Callable[[str], str],
    get_current_billing_summary: Callable[[], dict[str, Any] | None],
    build_checkout_start_message: Callable[[], tuple[bool, str]],
    build_customer_portal_message: Callable[[], tuple[bool, str]],
) -> None:
    from state_logic import get_effective_access_context

    effective_access = get_effective_access_context()
    with ui.column().classes('w-full max-w-2xl mx-auto py-12 px-4 gap-4 items-stretch'):
        with ui.card().classes('w-full p-8 border border-red-200 bg-white'):
            ui.label(tr_fn('gate.title')).classes('text-2xl font-bold text-gray-900')
            ui.label(tr_fn('gate.desc')).classes('text-sm text-gray-600')
            ui.separator()
            ui.label(
                tr_fn(
                    'gate.status_fmt',
                    email=str(getattr(state, 'current_user_email', '') or '-'),
                    access_tier=str(effective_access.get('access_tier', '') or '-'),
                    status=str(effective_access.get('subscription_status', '') or '-'),
                )
            ).classes('text-sm text-gray-700')
            ui.label(str(effective_access.get('gate_reason', '') or tr_fn('gate.default_reason'))).classes(
                'text-sm text-red-700 font-semibold'
            )
            ui.separator()
            ui.label(tr_fn('gate.next_title')).classes('text-sm font-bold text-gray-800')
            ui.label(tr_fn('gate.next_1')).classes('text-sm text-gray-600')
            ui.label(tr_fn('gate.next_2')).classes('text-sm text-gray-600')

            billing = get_current_billing_summary()
            if billing:
                stripe_ready = bool(billing.get('stripe_ready', False))
                ui.separator()
                ui.label(tr_fn('gate.billing_title')).classes('text-sm font-bold text-gray-800')
                ui.label(
                    tr_fn(
                        'gate.billing_status_fmt',
                        plan=str(billing.get('plan_code', '-') or '-'),
                        billing_status=str(billing.get('billing_status', '-') or '-'),
                        access_tier=str(billing.get('access_tier', '-') or '-'),
                    )
                ).classes('text-sm text-gray-700')

                def _start_checkout() -> None:
                    ok, msg = build_checkout_start_message()
                    if ok and str(msg or "").startswith(("http://", "https://")):
                        ui.navigate.to(str(msg), new_tab=True)
                        ui.notify(tr_fn('gate.checkout_redirect'), type='positive', timeout=4000)
                    else:
                        ui.notify(str(msg or ''), type='info' if ok else 'negative', timeout=5000)

                def _open_portal() -> None:
                    ok, msg = build_customer_portal_message()
                    if ok and str(msg or "").startswith(("http://", "https://")):
                        ui.navigate.to(str(msg), new_tab=True)
                        ui.notify(tr_fn('gate.portal_redirect'), type='positive', timeout=4000)
                    else:
                        ui.notify(str(msg or ''), type='info' if ok else 'negative', timeout=5000)

                if stripe_ready and (bool(billing.get('has_checkout', False)) or str(billing.get('access_tier', '') or '') != 'paid'):
                    ui.button(tr_fn('gate.checkout_btn'), on_click=_start_checkout).classes(
                        'w-full bg-[#111] text-white mt-3'
                    )
                if stripe_ready and bool(billing.get('has_portal', False)):
                    ui.button(tr_fn('gate.portal_btn'), on_click=_open_portal).classes(
                        'w-full bg-white text-[#111] border border-[#111] mt-2'
                    )
