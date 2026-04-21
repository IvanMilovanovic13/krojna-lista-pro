# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from html import escape
from typing import Tuple

import requests

from app_config import get_app_config


_LOG = logging.getLogger(__name__)
_RESEND_SEND_URL = "https://api.resend.com/emails"


def _format_from_header() -> str:
    cfg = get_app_config()
    from_email = str(cfg.email_from or "").strip()
    from_name = str(cfg.email_from_name or "").strip()
    if from_name and from_email:
        return f"{from_name} <{from_email}>"
    return from_email


def is_email_delivery_enabled() -> bool:
    cfg = get_app_config()
    provider = str(cfg.email_provider or "").strip().lower()
    api_key = str(cfg.email_api_key or "").strip()
    from_email = str(cfg.email_from or "").strip()
    return bool(cfg.email_enabled and provider == "resend" and api_key and from_email)


def send_email(
    *,
    to_email: str,
    subject: str,
    html_body: str,
    text_body: str = "",
) -> Tuple[bool, str]:
    cfg = get_app_config()
    provider = str(cfg.email_provider or "").strip().lower()
    api_key = str(cfg.email_api_key or "").strip()
    from_header = _format_from_header()
    reply_to = str(cfg.email_reply_to or "").strip()

    if not bool(cfg.email_enabled):
        return False, "email_disabled"
    if provider != "resend":
        return False, f"unsupported_email_provider:{provider or 'missing'}"
    if not api_key:
        return False, "missing_email_api_key"
    if not from_header:
        return False, "missing_email_from"

    payload = {
        "from": from_header,
        "to": [str(to_email or "").strip()],
        "subject": str(subject or "").strip(),
        "html": str(html_body or "").strip(),
    }
    if str(text_body or "").strip():
        payload["text"] = str(text_body or "").strip()
    if reply_to:
        payload["reply_to"] = reply_to

    try:
        response = requests.post(
            _RESEND_SEND_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=20,
        )
    except Exception as ex:
        _LOG.warning("Resend request failed: %s", ex)
        return False, f"email_request_failed:{ex}"

    try:
        response_payload = response.json()
    except Exception:
        response_payload = {}

    if 200 <= int(response.status_code) < 300:
        message_id = str(response_payload.get("id", "") or "").strip()
        return True, message_id or "email_sent"

    detail = (
        str(response_payload.get("message", "") or "").strip()
        or str(response_payload.get("error", "") or "").strip()
        or str(response.text or "").strip()
        or f"status_{response.status_code}"
    )
    _LOG.warning("Resend send failed: %s", detail)
    return False, detail


def send_verification_email(*, to_email: str, verification_url: str, display_name: str = "") -> Tuple[bool, str]:
    safe_name = escape(str(display_name or "").strip() or "Zdravo")
    safe_url = escape(str(verification_url or "").strip())
    subject = "Potvrdi email adresu - Krojna Lista PRO"
    html_body = (
        "<div style=\"font-family:Segoe UI,Arial,sans-serif;font-size:14px;color:#111827;line-height:1.6;\">"
        f"<p>{safe_name},</p>"
        "<p>Tvoj nalog je napravljen. Potvrdi email adresu klikom na dugme ispod.</p>"
        f"<p><a href=\"{safe_url}\" "
        "style=\"display:inline-block;background:#111827;color:#ffffff;text-decoration:none;padding:10px 16px;border-radius:8px;\">"
        "Potvrdi email"
        "</a></p>"
        f"<p>Ako dugme ne radi, otvori ovaj link:</p><p><a href=\"{safe_url}\">{safe_url}</a></p>"
        "<p>Ovaj email je poslat za pristup aplikaciji Krojna Lista PRO.</p>"
        "</div>"
    )
    text_body = (
        f"{display_name or 'Zdravo'},\n\n"
        "Tvoj nalog je napravljen. Potvrdi email adresu preko ovog linka:\n"
        f"{verification_url}\n\n"
        "Ako nisi ti napravio nalog, slobodno ignorisi ovu poruku."
    )
    return send_email(
        to_email=to_email,
        subject=subject,
        html_body=html_body,
        text_body=text_body,
    )


def send_password_reset_email(*, to_email: str, reset_url: str, display_name: str = "") -> Tuple[bool, str]:
    safe_name = escape(str(display_name or "").strip() or "Zdravo")
    safe_url = escape(str(reset_url or "").strip())
    subject = "Reset lozinke - Krojna Lista PRO"
    html_body = (
        "<div style=\"font-family:Segoe UI,Arial,sans-serif;font-size:14px;color:#111827;line-height:1.6;\">"
        f"<p>{safe_name},</p>"
        "<p>Primili smo zahtev za promenu lozinke. Klikni na dugme ispod da postavis novu lozinku.</p>"
        f"<p><a href=\"{safe_url}\" "
        "style=\"display:inline-block;background:#111827;color:#ffffff;text-decoration:none;padding:10px 16px;border-radius:8px;\">"
        "Postavi novu lozinku"
        "</a></p>"
        f"<p>Ako dugme ne radi, otvori ovaj link:</p><p><a href=\"{safe_url}\">{safe_url}</a></p>"
        "<p>Ako nisi ti trazio reset lozinke, ignorisi ovu poruku.</p>"
        "</div>"
    )
    text_body = (
        f"{display_name or 'Zdravo'},\n\n"
        "Primili smo zahtev za promenu lozinke. Otvori ovaj link da postavis novu lozinku:\n"
        f"{reset_url}\n\n"
        "Ako nisi ti trazio reset lozinke, ignorisi ovu poruku."
    )
    return send_email(
        to_email=to_email,
        subject=subject,
        html_body=html_body,
        text_body=text_body,
    )
