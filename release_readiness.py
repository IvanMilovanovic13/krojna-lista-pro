# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from app_config import get_app_config, get_public_runtime_config
from lemon_squeezy_service import get_billing_runtime_status
from project_store import get_project_store_runtime_info


DEFAULT_SECRET_KEYS = {
    "",
    "dev-secret-key-change-me",
    "change-me-in-production",
}


@dataclass(frozen=True)
class ReadinessCheck:
    key: str
    label: str
    ok: bool
    severity: str
    detail: str


def _is_true(value: object) -> bool:
    return str(value or "").strip().lower() == "true"


def _is_https_url(value: str) -> bool:
    raw = str(value or "").strip()
    if not raw:
        return False
    parsed = urlparse(raw)
    return str(parsed.scheme or "").lower() == "https" and bool(str(parsed.netloc or "").strip())


def _is_http_url(value: str) -> bool:
    raw = str(value or "").strip()
    if not raw:
        return False
    parsed = urlparse(raw)
    return str(parsed.scheme or "").lower() in {"http", "https"} and bool(str(parsed.netloc or "").strip())


def _matches_base_origin(url_value: str, base_url: str) -> bool:
    raw_url = str(url_value or "").strip()
    raw_base = str(base_url or "").strip()
    if not raw_url or not raw_base:
        return False
    parsed_url = urlparse(raw_url)
    parsed_base = urlparse(raw_base)
    url_scheme = str(parsed_url.scheme or "").lower().strip()
    base_scheme = str(parsed_base.scheme or "").lower().strip()
    url_netloc = str(parsed_url.netloc or "").strip().lower()
    base_netloc = str(parsed_base.netloc or "").strip().lower()
    if not url_scheme or not base_scheme or not url_netloc or not base_netloc:
        return False
    return url_scheme == base_scheme and url_netloc == base_netloc


def _make_check(key: str, label: str, ok: bool, severity: str, detail: str) -> ReadinessCheck:
    return ReadinessCheck(
        key=str(key),
        label=str(label),
        ok=bool(ok),
        severity=str(severity),
        detail=str(detail),
    )


def get_release_readiness_report(*, target: str = "production") -> dict[str, object]:
    clean_target = str(target or "production").strip().lower()
    if clean_target not in {"development", "staging", "production"}:
        clean_target = "production"

    cfg = get_app_config()
    public_cfg = get_public_runtime_config()
    store_runtime = get_project_store_runtime_info()
    stripe_runtime = get_billing_runtime_status()

    checks: list[ReadinessCheck] = []

    base_url = str(cfg.base_url or "").strip()
    is_prod_like = clean_target in {"staging", "production"}
    require_https = clean_target in {"staging", "production"}

    checks.append(
        _make_check(
            "app_env",
            "APP_ENV matches target",
            str(cfg.app_env) == clean_target,
            "warning" if clean_target == "staging" else "blocker",
            f"APP_ENV={cfg.app_env}, target={clean_target}",
        )
    )
    checks.append(
        _make_check(
            "base_url_present",
            "BASE_URL is set",
            bool(base_url),
            "blocker",
            base_url or "BASE_URL is empty.",
        )
    )
    checks.append(
        _make_check(
            "base_url_valid",
            "BASE_URL is a valid HTTP(S) URL",
            _is_http_url(base_url),
            "blocker",
            base_url or "BASE_URL is empty.",
        )
    )
    checks.append(
        _make_check(
            "base_url_https",
            "BASE_URL uses HTTPS",
            _is_https_url(base_url) if require_https else _is_http_url(base_url),
            "blocker" if require_https else "warning",
            base_url or "BASE_URL is empty.",
        )
    )

    secret_key = str(cfg.secret_key or "").strip()
    checks.append(
        _make_check(
            "secret_key_custom",
            "SECRET_KEY is custom",
            secret_key not in DEFAULT_SECRET_KEYS,
            "blocker",
            "SECRET_KEY is still default." if secret_key in DEFAULT_SECRET_KEYS else "Custom SECRET_KEY detected.",
        )
    )

    db_backend = str(store_runtime.get("backend", "") or "").strip().lower()
    db_ready = _is_true(store_runtime.get("ready", "false"))
    checks.append(
        _make_check(
            "database_ready",
            "Database backend is ready",
            db_ready,
            "blocker",
            f"backend={db_backend or 'unknown'} ready={store_runtime.get('ready', '')}",
        )
    )
    checks.append(
        _make_check(
            "database_backend",
            "Production-like target uses Postgres",
            db_backend == "postgres" if is_prod_like else db_backend in {"sqlite", "postgres"},
            "blocker" if is_prod_like else "warning",
            f"backend={db_backend or 'unknown'}",
        )
    )

    checks.append(
        _make_check(
            "billing_api_key",
            "Lemon Squeezy API key is configured",
            _is_true(stripe_runtime.get("has_api_key")),
            "blocker",
            f"has_api_key={stripe_runtime.get('has_api_key', 'false')}",
        )
    )
    checks.append(
        _make_check(
            "billing_store_id",
            "Lemon Squeezy store ID is configured",
            _is_true(stripe_runtime.get("has_store_id")),
            "blocker",
            f"has_store_id={stripe_runtime.get('has_store_id', 'false')}",
        )
    )
    checks.append(
        _make_check(
            "billing_store_subdomain",
            "Lemon Squeezy store subdomain is configured",
            _is_true(stripe_runtime.get("has_store_subdomain")),
            "blocker",
            f"has_store_subdomain={stripe_runtime.get('has_store_subdomain', 'false')}",
        )
    )
    checks.append(
        _make_check(
            "billing_webhook_secret",
            "Lemon Squeezy webhook secret is configured",
            _is_true(stripe_runtime.get("has_webhook_secret")),
            "blocker",
            f"has_webhook_secret={stripe_runtime.get('has_webhook_secret', 'false')}",
        )
    )
    checks.append(
        _make_check(
            "billing_variant_weekly",
            "Lemon Squeezy weekly variant ID is configured",
            _is_true(stripe_runtime.get("has_variant_id_weekly")),
            "blocker",
            f"has_variant_id_weekly={stripe_runtime.get('has_variant_id_weekly', 'false')}",
        )
    )
    checks.append(
        _make_check(
            "billing_variant_monthly",
            "Lemon Squeezy monthly variant ID is configured",
            _is_true(stripe_runtime.get("has_variant_id_monthly")),
            "warning",
            f"has_variant_id_monthly={stripe_runtime.get('has_variant_id_monthly', 'false')}",
        )
    )
    checks.append(
        _make_check(
            "billing_checkout_success_url",
            "Lemon Squeezy checkout success URL is valid",
            _is_http_url(str(cfg.lemon_squeezy_checkout_success_url or "")),
            "blocker",
            str(cfg.lemon_squeezy_checkout_success_url or ""),
        )
    )
    checks.append(
        _make_check(
            "billing_checkout_success_origin",
            "Lemon Squeezy checkout success URL matches BASE_URL origin",
            _matches_base_origin(str(cfg.lemon_squeezy_checkout_success_url or ""), base_url),
            "blocker" if is_prod_like else "warning",
            str(cfg.lemon_squeezy_checkout_success_url or ""),
        )
    )

    blockers = [check for check in checks if not check.ok and check.severity == "blocker"]
    warnings = [check for check in checks if not check.ok and check.severity != "blocker"]
    passed = [check for check in checks if check.ok]

    return {
        "target": clean_target,
        "ready": len(blockers) == 0,
        "summary": {
            "total_checks": len(checks),
            "passed": len(passed),
            "blockers": len(blockers),
            "warnings": len(warnings),
        },
        "checks": [
            {
                "key": check.key,
                "label": check.label,
                "ok": check.ok,
                "severity": check.severity,
                "detail": check.detail,
            }
            for check in checks
        ],
        "blockers": [
            {
                "key": check.key,
                "label": check.label,
                "detail": check.detail,
            }
            for check in blockers
        ],
        "warnings": [
            {
                "key": check.key,
                "label": check.label,
                "detail": check.detail,
            }
            for check in warnings
        ],
        "runtime": {
            "app_config": public_cfg,
            "project_store": store_runtime,
            "stripe": stripe_runtime,
        },
    }
