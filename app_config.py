# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_SQLITE_PATH = DATA_DIR / "project_store.db"
_ENV_LOADED = False


@dataclass(frozen=True)
class DatabaseConfig:
    backend: str
    url: str
    sqlite_path: Path | None


@dataclass(frozen=True)
class AppConfig:
    app_env: str
    base_url: str
    host: str
    port: int
    web_workers: int
    export_worker_mode: str
    export_worker_poll_seconds: int
    secret_key: str
    database_url: str
    lemon_squeezy_api_key: str
    lemon_squeezy_webhook_secret: str
    lemon_squeezy_store_id: str
    lemon_squeezy_store_subdomain: str
    lemon_squeezy_variant_id_weekly: str
    lemon_squeezy_variant_id_monthly: str
    lemon_squeezy_checkout_success_url: str
    email_provider: str
    email_enabled: bool
    email_api_key: str
    email_from: str
    email_from_name: str
    email_reply_to: str
    debug: bool


def _apply_env_file(
    path: Path,
    *,
    original_env_keys: set[str],
    loaded_keys: set[str],
    allow_override: bool,
) -> None:
    if not path.exists() or not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = str(raw_line or "").strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        clean_key = str(key or "").strip()
        if not clean_key:
            continue
        if clean_key in original_env_keys:
            continue
        if clean_key in os.environ and (not allow_override or clean_key not in loaded_keys):
            continue
        clean_value = str(value or "").strip().strip('"').strip("'")
        os.environ[clean_key] = clean_value
        loaded_keys.add(clean_key)


def _load_dotenv_files() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    original_env_keys = set(os.environ.keys())
    loaded_keys: set[str] = set()

    for path in (BASE_DIR / ".env", BASE_DIR / ".env.local"):
        try:
            _apply_env_file(
                path,
                original_env_keys=original_env_keys,
                loaded_keys=loaded_keys,
                allow_override=False,
            )
        except Exception:
            continue

    env_hint = str(os.getenv("APP_ENV", "") or "").strip().lower()
    if env_hint:
        for path in (BASE_DIR / f".env.{env_hint}", BASE_DIR / f".env.{env_hint}.local"):
            try:
                _apply_env_file(
                    path,
                    original_env_keys=original_env_keys,
                    loaded_keys=loaded_keys,
                    allow_override=True,
                )
            except Exception:
                continue
    _ENV_LOADED = True


def get_database_config() -> DatabaseConfig:
    _load_dotenv_files()
    raw = str(os.getenv("DATABASE_URL", "") or "").strip()
    if not raw:
        return DatabaseConfig(
            backend="sqlite",
            url=f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}",
            sqlite_path=DEFAULT_SQLITE_PATH,
        )

    parsed = urlparse(raw)
    scheme = str(parsed.scheme or "").lower().strip()

    if scheme == "sqlite":
        if parsed.netloc and parsed.path:
            sqlite_path = Path(f"{parsed.netloc}{parsed.path}")
        else:
            sqlite_path = Path(parsed.path or "")
        if not sqlite_path.is_absolute():
            sqlite_path = (BASE_DIR / sqlite_path).resolve()
        return DatabaseConfig(
            backend="sqlite",
            url=raw,
            sqlite_path=sqlite_path,
        )

    if scheme in ("postgres", "postgresql"):
        return DatabaseConfig(
            backend="postgres",
            url=raw,
            sqlite_path=None,
        )

    return DatabaseConfig(
        backend="unknown",
        url=raw,
        sqlite_path=None,
    )


def _env(name: str, default: str = "") -> str:
    return str(os.getenv(name, default) or "").strip()


def _env_int(name: str, default: int) -> int:
    raw = str(os.getenv(name, "") or "").strip()
    if not raw:
        return int(default)
    try:
        return int(raw)
    except Exception:
        return int(default)


def _env_bool(name: str, default: bool = False) -> bool:
    raw = str(os.getenv(name, "") or "").strip().lower()
    if not raw:
        return bool(default)
    return raw in {"1", "true", "yes", "on"}


def _is_placeholder_like(value: str, *, kind: str = "") -> bool:
    raw = str(value or "").strip()
    if not raw:
        return True
    lowered = raw.lower()
    generic_tokens = {
        "...",
        "changeme",
        "change-me",
        "placeholder",
        "example",
        "tvoj-domen.rs",
        "user:pass@host:5432/dbname",
    }
    if lowered in generic_tokens:
        return True
    if any(token in lowered for token in ("promeni-me", "change-me", "example", "placeholder", "tvoj-domen")):
        return True
    if kind == "lemonsqueezy_api_key":
        return lowered.endswith("...") or (lowered.startswith("eyj") is False and lowered in {"api_key", "test_api_key", "live_api_key"})
    if kind == "lemonsqueezy_webhook_secret":
        return lowered in {"webhook_secret", "signing_secret"} or lowered.endswith("...")
    if kind == "store_id":
        return lowered in {"store_id", "12345"}
    if kind == "store_subdomain":
        return lowered in {"your-store", "store-subdomain"}
    if kind == "variant_id":
        return lowered in {"variant_id", "123456"} or lowered.endswith("...")
    if kind == "email_api_key":
        return lowered in {"email_api_key", "re_xxxxxxxxx", "resend_api_key"} or "xxxxxxxxx" in lowered
    if kind == "email_from":
        return "tvoj-domen" in lowered or lowered in {"noreply@example.com", "sender@example.com"}
    return False


def get_app_config() -> AppConfig:
    _load_dotenv_files()
    app_env = _env("APP_ENV", "development").lower()
    if app_env not in ("development", "staging", "production", "test"):
        app_env = "development"

    secret_key = _env("SECRET_KEY")
    if not secret_key:
        secret_key = "dev-secret-key-change-me"

    database = get_database_config()
    base_url_default = "http://localhost:8080" if app_env != "production" else ""
    host_default = "127.0.0.1" if app_env != "production" else "0.0.0.0"
    port_default = 8080
    web_workers_default = 0 if app_env in ("development", "test") else 2

    return AppConfig(
        app_env=app_env,
        base_url=_env("BASE_URL", base_url_default),
        host=_env("HOST", host_default),
        port=max(1, _env_int("PORT", port_default)),
        web_workers=max(0, _env_int("WEB_WORKERS", web_workers_default)),
        export_worker_mode=_env("EXPORT_WORKER_MODE", "in_process").lower(),
        export_worker_poll_seconds=max(1, _env_int("EXPORT_WORKER_POLL_SECONDS", 2)),
        secret_key=secret_key,
        database_url=str(database.url),
        lemon_squeezy_api_key=_env("LEMON_SQUEEZY_API_KEY"),
        lemon_squeezy_webhook_secret=_env("LEMON_SQUEEZY_WEBHOOK_SECRET"),
        lemon_squeezy_store_id=_env("LEMON_SQUEEZY_STORE_ID"),
        lemon_squeezy_store_subdomain=_env("LEMON_SQUEEZY_STORE_SUBDOMAIN"),
        lemon_squeezy_variant_id_weekly=_env("LEMON_SQUEEZY_VARIANT_ID_WEEKLY"),
        lemon_squeezy_variant_id_monthly=_env("LEMON_SQUEEZY_VARIANT_ID_MONTHLY"),
        lemon_squeezy_checkout_success_url=_env("LEMON_SQUEEZY_CHECKOUT_SUCCESS_URL", f"{_env('BASE_URL', base_url_default)}/login?checkout=success"),
        email_provider=_env("EMAIL_PROVIDER", "resend").lower(),
        email_enabled=_env_bool("EMAIL_ENABLED", default=False),
        email_api_key=_env("EMAIL_API_KEY") or _env("RESEND_API_KEY"),
        email_from=_env("EMAIL_FROM"),
        email_from_name=_env("EMAIL_FROM_NAME", "Krojna Lista PRO"),
        email_reply_to=_env("EMAIL_REPLY_TO"),
        debug=app_env in ("development", "test"),
    )


def get_public_runtime_config() -> dict[str, str]:
    cfg = get_app_config()
    return {
        "app_env": str(cfg.app_env),
        "base_url": str(cfg.base_url),
        "host": str(cfg.host),
        "port": str(cfg.port),
        "web_workers": str(cfg.web_workers),
        "export_worker_mode": str(cfg.export_worker_mode),
        "export_worker_poll_seconds": str(cfg.export_worker_poll_seconds),
        "database_url": str(cfg.database_url),
        "debug": "true" if cfg.debug else "false",
        "has_secret_key": "true" if bool(cfg.secret_key) else "false",
        "billing_provider": "lemonsqueezy",
        "has_billing_api_key": "true" if not _is_placeholder_like(cfg.lemon_squeezy_api_key, kind="lemonsqueezy_api_key") else "false",
        "has_billing_webhook_secret": "true" if not _is_placeholder_like(cfg.lemon_squeezy_webhook_secret, kind="lemonsqueezy_webhook_secret") else "false",
        "has_billing_store_id": "true" if not _is_placeholder_like(cfg.lemon_squeezy_store_id, kind="store_id") else "false",
        "has_billing_store_subdomain": "true" if not _is_placeholder_like(cfg.lemon_squeezy_store_subdomain, kind="store_subdomain") else "false",
        "has_billing_variant_id_weekly": "true" if not _is_placeholder_like(cfg.lemon_squeezy_variant_id_weekly, kind="variant_id") else "false",
        "has_billing_variant_id_monthly": "true" if not _is_placeholder_like(cfg.lemon_squeezy_variant_id_monthly, kind="variant_id") else "false",
        "email_provider": str(cfg.email_provider),
        "email_enabled": "true" if bool(cfg.email_enabled) else "false",
        "has_email_api_key": "true" if not _is_placeholder_like(cfg.email_api_key, kind="email_api_key") else "false",
        "has_email_from": "true" if not _is_placeholder_like(cfg.email_from, kind="email_from") else "false",
    }
