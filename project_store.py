# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import threading
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from typing import Any, Iterable, Optional

from postgres_store_migration import get_postgres_schema_sql
from storage_backend import get_store_backend, get_store_backend_name, get_store_runtime_info_dict

LOCAL_USER_EMAIL = "local@krojnalistapro"
PASSWORD_SCHEME = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 120_000
DEFAULT_PRIVILEGED_PASSWORD = "CabinetCut_Auth_2026!"
DEFAULT_ADMIN_EMAILS = [
    "admin1@cabinetcutpro.invalid",
    "admin2@cabinetcutpro.invalid",
    "admin3@cabinetcutpro.invalid",
]
DEFAULT_PRIVILEGED_TEST_EMAILS = [
    "testpaid1@cabinetcutpro.invalid",
    "testpaid2@cabinetcutpro.invalid",
    "testpaid3@cabinetcutpro.invalid",
    "testpaid4@cabinetcutpro.invalid",
    "testpaid5@cabinetcutpro.invalid",
]
_SEEDING_PRIVILEGED_ACCOUNTS = False
_PRIVILEGED_SEED_LOCK = threading.Lock()
_PRIVILEGED_SEED_DONE = False
_PROJECT_STORE_INIT_LOCK = threading.Lock()
_PROJECT_STORE_READY = False


@dataclass(frozen=True)
class UserRecord:
    id: int
    email: str
    display_name: str
    auth_mode: str
    access_tier: str
    status: str
    email_verified: bool
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class ProjectRecord:
    id: int
    user_id: int
    name: str
    project_type: str
    kitchen_layout: str
    language: str
    source: str
    is_demo: bool
    is_autosave: bool
    created_at: str
    updated_at: str
    last_opened_at: str


@dataclass(frozen=True)
class SubscriptionRecord:
    id: int
    user_id: int
    provider: str
    plan_code: str
    billing_status: str
    customer_id: str
    subscription_id: str
    checkout_url: str
    portal_url: str
    current_period_end: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class AuthSessionRecord:
    id: int
    user_id: int
    session_token: str
    session_kind: str
    auth_provider: str
    status: str
    created_at: str
    updated_at: str
    expires_at: str
    revoked_at: str


@dataclass(frozen=True)
class PasswordResetTokenRecord:
    id: int
    user_id: int
    reset_token: str
    status: str
    created_at: str
    expires_at: str
    used_at: str


@dataclass(frozen=True)
class EmailVerificationTokenRecord:
    id: int
    user_id: int
    email: str
    verification_token: str
    status: str
    created_at: str
    expires_at: str
    used_at: str


@dataclass(frozen=True)
class AuditLogRecord:
    id: int
    user_id: int
    event_type: str
    status: str
    detail: str
    created_at: str


@dataclass(frozen=True)
class ExportJobRecord:
    id: int
    user_id: int
    project_id: int
    job_type: str
    status: str
    request_payload_json: str
    result_ref: str
    error_message: str
    created_at: str
    started_at: str
    finished_at: str
    updated_at: str


@dataclass(frozen=True)
class BillingEventRecord:
    id: int
    provider: str
    provider_event_id: str
    event_type: str
    user_id: int
    email: str
    status: str
    payload_json: str
    billing_status: str
    plan_code: str
    error_message: str
    created_at: str
    updated_at: str
    processed_at: str


SQLITE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL DEFAULT '',
    password_hash TEXT NOT NULL DEFAULT '',
    auth_mode TEXT NOT NULL DEFAULT 'local',
    access_tier TEXT NOT NULL DEFAULT 'local_beta',
    status TEXT NOT NULL DEFAULT 'local_active',
    email_verified INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    project_type TEXT NOT NULL DEFAULT 'kitchen',
    kitchen_layout TEXT NOT NULL DEFAULT 'jedan_zid',
    language TEXT NOT NULL DEFAULT 'sr',
    source TEXT NOT NULL DEFAULT 'local',
    is_demo INTEGER NOT NULL DEFAULT 0,
    is_autosave INTEGER NOT NULL DEFAULT 0,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_opened_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    provider TEXT NOT NULL DEFAULT 'lemon_squeezy',
    plan_code TEXT NOT NULL DEFAULT 'trial',
    billing_status TEXT NOT NULL DEFAULT 'trial',
    customer_id TEXT NOT NULL DEFAULT '',
    subscription_id TEXT NOT NULL DEFAULT '',
    checkout_url TEXT NOT NULL DEFAULT '',
    portal_url TEXT NOT NULL DEFAULT '',
    current_period_end TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS billing_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL DEFAULT 'lemon_squeezy',
    provider_event_id TEXT NOT NULL UNIQUE,
    event_type TEXT NOT NULL DEFAULT '',
    user_id INTEGER NOT NULL DEFAULT 0,
    email TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'received',
    payload_json TEXT NOT NULL DEFAULT '',
    billing_status TEXT NOT NULL DEFAULT '',
    plan_code TEXT NOT NULL DEFAULT '',
    error_message TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS auth_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token TEXT NOT NULL UNIQUE,
    session_kind TEXT NOT NULL DEFAULT 'browser',
    auth_provider TEXT NOT NULL DEFAULT 'password',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT NOT NULL,
    revoked_at TEXT NOT NULL DEFAULT '',
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    reset_token TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT NOT NULL,
    used_at TEXT NOT NULL DEFAULT '',
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS email_verification_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    email TEXT NOT NULL DEFAULT '',
    verification_token TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT NOT NULL,
    used_at TEXT NOT NULL DEFAULT '',
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS login_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    success INTEGER NOT NULL DEFAULT 0,
    attempted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL DEFAULT 0,
    event_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'info',
    detail TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS export_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL DEFAULT 0,
    job_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    request_payload_json TEXT NOT NULL DEFAULT '',
    result_ref TEXT NOT NULL DEFAULT '',
    error_message TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TEXT NOT NULL DEFAULT '',
    finished_at TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_last_opened_at ON projects(last_opened_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_projects_autosave_per_user
ON projects(user_id, is_autosave)
WHERE is_autosave = 1;
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_billing_events_provider_event_id ON billing_events(provider_event_id);
CREATE INDEX IF NOT EXISTS idx_billing_events_email_created_at ON billing_events(email, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_id ON auth_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_token ON auth_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens(reset_token);
CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_user_id ON email_verification_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_token ON email_verification_tokens(verification_token);
CREATE INDEX IF NOT EXISTS idx_login_attempts_email_time ON login_attempts(email, attempted_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_export_jobs_user_id ON export_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_export_jobs_status_created ON export_jobs(status, created_at DESC);
"""


def _connect():
    return get_store_backend().connect()


def _get_backend_name() -> str:
    return str(get_store_backend_name())


def init_project_store() -> None:
    global _SEEDING_PRIVILEGED_ACCOUNTS, _PRIVILEGED_SEED_DONE, _PROJECT_STORE_READY
    if _PROJECT_STORE_READY:
        return
    with _PROJECT_STORE_INIT_LOCK:
        if _PROJECT_STORE_READY:
            return
        get_store_backend().assert_ready()
        with _connect() as conn:
            if _get_backend_name() == "postgres":
                conn.executescript(get_postgres_schema_sql())
            else:
                conn.executescript(SQLITE_SCHEMA_SQL)
            _ensure_users_schema(conn)
            _ensure_auth_runtime_schema(conn)
            _ensure_email_verification_schema(conn)
        _PROJECT_STORE_READY = True
        if not _SEEDING_PRIVILEGED_ACCOUNTS and not _PRIVILEGED_SEED_DONE:
            ensure_privileged_seed_accounts()


def get_project_store_runtime_info() -> dict[str, str]:
    info = get_store_runtime_info_dict()
    backend = str(info.get("backend", "") or "").strip().lower()
    ready = str(info.get("ready", "") or "").strip().lower() == "true"
    production_ready = backend == "postgres" and ready
    info["production_ready"] = "true" if production_ready else "false"
    if production_ready:
        info["deployment_note"] = "Postgres backend je spreman za produkcioni multi-user rad."
    elif backend == "sqlite":
        info["deployment_note"] = "SQLite je dobar za lokalni rad i beta proveru, ali nije finalni production backend."
    elif backend == "postgres":
        info["deployment_note"] = "Postgres je prepoznat, ali backend jos nije potpuno spreman."
    else:
        info["deployment_note"] = "Storage backend nije spreman za produkcioni rad."
    return info


def _ensure_users_schema(conn) -> None:
    if _get_backend_name() == "postgres":
        rows = conn.execute(
            """
            SELECT column_name AS name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'users'
            """
        ).fetchall()
        existing = {str(row["name"]) for row in rows}
        if "display_name" not in existing:
            conn.execute("ALTER TABLE users ADD COLUMN display_name TEXT NOT NULL DEFAULT ''")
        if "auth_mode" not in existing:
            conn.execute("ALTER TABLE users ADD COLUMN auth_mode TEXT NOT NULL DEFAULT 'local'")
        if "access_tier" not in existing:
            conn.execute("ALTER TABLE users ADD COLUMN access_tier TEXT NOT NULL DEFAULT 'local_beta'")
        if "email_verified" not in existing:
            conn.execute("ALTER TABLE users ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT FALSE")
        conn.execute(
            """
            UPDATE users
            SET display_name = CASE
                    WHEN COALESCE(display_name, '') = '' THEN split_part(email, '@', 1)
                    ELSE display_name
                END,
                auth_mode = CASE
                    WHEN COALESCE(auth_mode, '') = '' THEN 'local'
                    ELSE auth_mode
                END,
                access_tier = CASE
                    WHEN COALESCE(access_tier, '') = '' THEN
                        CASE
                            WHEN status = 'local_active' THEN 'local_beta'
                            WHEN status = 'trial_active' THEN 'trial'
                            WHEN status = 'paid_active' THEN 'paid'
                            WHEN status = 'admin_active' THEN 'admin'
                            ELSE 'blocked'
                        END
                    ELSE access_tier
                END,
                email_verified = CASE
                    WHEN status IN ('local_active', 'trial_active', 'paid_active', 'admin_active') THEN TRUE
                    ELSE COALESCE(email_verified, FALSE)
                END
            """
        )
        return

    rows = conn.execute("PRAGMA table_info(users)").fetchall()
    existing = {str(row["name"]) for row in rows}
    if "display_name" not in existing:
        conn.execute("ALTER TABLE users ADD COLUMN display_name TEXT NOT NULL DEFAULT ''")
    if "auth_mode" not in existing:
        conn.execute("ALTER TABLE users ADD COLUMN auth_mode TEXT NOT NULL DEFAULT 'local'")
    if "access_tier" not in existing:
        conn.execute("ALTER TABLE users ADD COLUMN access_tier TEXT NOT NULL DEFAULT 'local_beta'")
    if "email_verified" not in existing:
        conn.execute("ALTER TABLE users ADD COLUMN email_verified INTEGER NOT NULL DEFAULT 0")
    conn.execute(
        """
        UPDATE users
        SET display_name = CASE
                WHEN COALESCE(display_name, '') = '' THEN substr(email, 1, instr(email, '@') - 1)
                ELSE display_name
            END,
            auth_mode = CASE
                WHEN COALESCE(auth_mode, '') = '' THEN 'local'
                ELSE auth_mode
            END,
            access_tier = CASE
                WHEN COALESCE(access_tier, '') = '' THEN
                    CASE
                        WHEN status = 'local_active' THEN 'local_beta'
                        WHEN status = 'trial_active' THEN 'trial'
                        WHEN status = 'paid_active' THEN 'paid'
                        WHEN status = 'admin_active' THEN 'admin'
                        ELSE 'blocked'
                    END
                ELSE access_tier
            END,
            email_verified = CASE
                WHEN status IN ('local_active', 'trial_active', 'paid_active', 'admin_active') THEN 1
                ELSE COALESCE(email_verified, 0)
            END
        """
    )


def _ensure_email_verification_schema(conn) -> None:
    if _get_backend_name() == "postgres":
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS email_verification_tokens (
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                email TEXT NOT NULL DEFAULT '',
                verification_token TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'active',
                created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMPTZ NOT NULL,
                used_at TIMESTAMPTZ,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
    else:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS email_verification_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                email TEXT NOT NULL DEFAULT '',
                verification_token TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT NOT NULL,
                used_at TEXT NOT NULL DEFAULT '',
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_user_id ON email_verification_tokens(user_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_token ON email_verification_tokens(verification_token)"
    )


def _ensure_auth_runtime_schema(conn) -> None:
    if _get_backend_name() != "postgres":
        return
    auth_rows = conn.execute(
        """
        SELECT column_name AS name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'auth_sessions'
        """
    ).fetchall()
    auth_columns = {str(row["name"]): row for row in auth_rows}
    revoked_row = auth_columns.get("revoked_at")
    if revoked_row is not None:
        revoked_type = str(revoked_row["data_type"] or "").strip().lower()
        revoked_nullable = str(revoked_row["is_nullable"] or "").strip().upper()
        conn.execute("ALTER TABLE auth_sessions ALTER COLUMN revoked_at DROP DEFAULT")
        if revoked_nullable != "YES":
            conn.execute("ALTER TABLE auth_sessions ALTER COLUMN revoked_at DROP NOT NULL")
        if revoked_type != "timestamp with time zone":
            conn.execute(
                """
                ALTER TABLE auth_sessions
                ALTER COLUMN revoked_at TYPE TIMESTAMPTZ
                USING NULLIF(revoked_at::text, '')::timestamptz
                """
            )

    reset_rows = conn.execute(
        """
        SELECT column_name AS name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'password_reset_tokens'
        """
    ).fetchall()
    reset_columns = {str(row["name"]): row for row in reset_rows}
    used_row = reset_columns.get("used_at")
    if used_row is not None:
        used_type = str(used_row["data_type"] or "").strip().lower()
        used_nullable = str(used_row["is_nullable"] or "").strip().upper()
        conn.execute("ALTER TABLE password_reset_tokens ALTER COLUMN used_at DROP DEFAULT")
        if used_nullable != "YES":
            conn.execute("ALTER TABLE password_reset_tokens ALTER COLUMN used_at DROP NOT NULL")
        if used_type != "timestamp with time zone":
            conn.execute(
                """
                ALTER TABLE password_reset_tokens
                ALTER COLUMN used_at TYPE TIMESTAMPTZ
                USING NULLIF(used_at::text, '')::timestamptz
                """
            )


def ensure_local_user() -> UserRecord:
    init_project_store()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT id, email, display_name, auth_mode, access_tier, status, email_verified, created_at, updated_at
            FROM users
            WHERE email = ?
            """,
            (LOCAL_USER_EMAIL,),
        ).fetchone()
        if row is None:
            conn.execute(
                """
                INSERT INTO users (email, display_name, password_hash, auth_mode, access_tier, status, email_verified)
                VALUES (?, 'local', '', 'local', 'local_beta', 'local_active', 1)
                """,
                (LOCAL_USER_EMAIL,),
            )
            row = conn.execute(
                """
                SELECT id, email, display_name, auth_mode, access_tier, status, email_verified, created_at, updated_at
                FROM users
                WHERE email = ?
                """,
                (LOCAL_USER_EMAIL,),
            ).fetchone()
        assert row is not None
        return UserRecord(
            id=int(row["id"]),
            email=str(row["email"]),
            display_name=str(row["display_name"]),
            auth_mode=str(row["auth_mode"]),
            access_tier=str(row["access_tier"]),
            status=str(row["status"]),
            email_verified=bool(int(row["email_verified"])) if str(row["email_verified"]).strip().isdigit() else bool(row["email_verified"]),
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
        )


def _user_record_from_row(row: Any) -> UserRecord:
    return UserRecord(
        id=int(row["id"]),
        email=str(row["email"]),
        display_name=str(row["display_name"]),
        auth_mode=str(row["auth_mode"]),
        access_tier=str(row["access_tier"]),
        status=str(row["status"]),
        email_verified=bool(int(row["email_verified"])) if str(row["email_verified"]).strip().isdigit() else bool(row["email_verified"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


def _email_verification_token_from_row(row: Any) -> EmailVerificationTokenRecord:
    return EmailVerificationTokenRecord(
        id=int(row["id"]),
        user_id=int(row["user_id"]),
        email=str(row["email"]),
        verification_token=str(row["verification_token"]),
        status=str(row["status"]),
        created_at=str(row["created_at"]),
        expires_at=str(row["expires_at"]),
        used_at=str(row["used_at"] or ""),
    )


def _audit_log_record_from_row(row: Any) -> AuditLogRecord:
    return AuditLogRecord(
        id=int(row["id"]),
        user_id=int(row["user_id"]),
        event_type=str(row["event_type"]),
        status=str(row["status"]),
        detail=str(row["detail"]),
        created_at=str(row["created_at"]),
    )


def _export_job_record_from_row(row: Any) -> ExportJobRecord:
    return ExportJobRecord(
        id=int(row["id"]),
        user_id=int(row["user_id"]),
        project_id=int(row["project_id"]),
        job_type=str(row["job_type"]),
        status=str(row["status"]),
        request_payload_json=str(row["request_payload_json"]),
        result_ref=str(row["result_ref"]),
        error_message=str(row["error_message"]),
        created_at=str(row["created_at"]),
        started_at=str(row["started_at"]),
        finished_at=str(row["finished_at"]),
        updated_at=str(row["updated_at"]),
    )


def get_user_by_email(email: str) -> Optional[UserRecord]:
    init_project_store()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT id, email, display_name, auth_mode, access_tier, status, email_verified, created_at, updated_at
            FROM users
            WHERE lower(email) = lower(?)
            """,
            (str(email).strip(),),
        ).fetchone()
    if row is None:
        return None
    return _user_record_from_row(row)


def get_user_by_id(user_id: int) -> Optional[UserRecord]:
    init_project_store()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT id, email, display_name, auth_mode, access_tier, status, email_verified, created_at, updated_at
            FROM users
            WHERE id = ?
            """,
            (int(user_id),),
        ).fetchone()
    if row is None:
        return None
    return _user_record_from_row(row)


def append_audit_log(
    *,
    event_type: str,
    status: str = "info",
    detail: str = "",
    user_id: int = 0,
) -> AuditLogRecord:
    init_project_store()
    clean_event_type = str(event_type or "").strip() or "unknown"
    clean_status = str(status or "").strip() or "info"
    clean_detail = str(detail or "").strip()
    clean_user_id = max(0, int(user_id or 0))
    with _connect() as conn:
        if _get_backend_name() == "postgres":
            row = conn.execute(
                """
                INSERT INTO audit_logs (user_id, event_type, status, detail, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                RETURNING id, user_id, event_type, status, detail, created_at
                """,
                (clean_user_id, clean_event_type, clean_status, clean_detail),
            ).fetchone()
        else:
            conn.execute(
                """
                INSERT INTO audit_logs (user_id, event_type, status, detail, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (clean_user_id, clean_event_type, clean_status, clean_detail),
            )
            row = conn.execute(
                """
                SELECT id, user_id, event_type, status, detail, created_at
                FROM audit_logs
                WHERE id = last_insert_rowid()
                """
            ).fetchone()
    assert row is not None
    return _audit_log_record_from_row(row)


def list_recent_audit_logs(*, user_id: int | None = None, limit: int = 50) -> list[AuditLogRecord]:
    init_project_store()
    clean_limit = max(1, min(500, int(limit or 50)))
    query = """
        SELECT id, user_id, event_type, status, detail, created_at
        FROM audit_logs
    """
    params: list[Any] = []
    if user_id is not None:
        query += " WHERE user_id = ?"
        params.append(int(user_id))
    query += " ORDER BY id DESC LIMIT ?"
    params.append(clean_limit)
    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [_audit_log_record_from_row(row) for row in rows]


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        str(password).encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_ITERATIONS,
    ).hex()
    return f"{PASSWORD_SCHEME}${PASSWORD_ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    raw = str(stored_hash or "").strip()
    if not raw:
        return False
    try:
        scheme, iterations_raw, salt, digest = raw.split("$", 3)
        if scheme != PASSWORD_SCHEME:
            return False
        iterations = int(iterations_raw)
    except Exception:
        return False
    probe = hashlib.pbkdf2_hmac(
        "sha256",
        str(password).encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    ).hex()
    return hmac.compare_digest(probe, digest)


def _split_seed_emails(raw: str, fallback: list[str]) -> list[str]:
    if not str(raw or "").strip():
        return list(fallback)
    return [item.strip().lower() for item in str(raw).replace(";", ",").split(",") if item.strip()]


def ensure_privileged_seed_accounts() -> dict[str, list[str]]:
    global _SEEDING_PRIVILEGED_ACCOUNTS, _PRIVILEGED_SEED_DONE
    if _PRIVILEGED_SEED_DONE:
        seed_password = str(os.getenv("APP_PRIVILEGED_SEED_PASSWORD", DEFAULT_PRIVILEGED_PASSWORD) or DEFAULT_PRIVILEGED_PASSWORD)
        return {
            "admins": list(_split_seed_emails(os.getenv("APP_ADMIN_EMAILS", ""), DEFAULT_ADMIN_EMAILS)[:3]),
            "tests": list(_split_seed_emails(os.getenv("APP_PRIVILEGED_TEST_EMAILS", ""), DEFAULT_PRIVILEGED_TEST_EMAILS)[:5]),
            "seed_password": [seed_password],
        }
    with _PRIVILEGED_SEED_LOCK:
        if _PRIVILEGED_SEED_DONE:
            seed_password = str(os.getenv("APP_PRIVILEGED_SEED_PASSWORD", DEFAULT_PRIVILEGED_PASSWORD) or DEFAULT_PRIVILEGED_PASSWORD)
            return {
                "admins": list(_split_seed_emails(os.getenv("APP_ADMIN_EMAILS", ""), DEFAULT_ADMIN_EMAILS)[:3]),
                "tests": list(_split_seed_emails(os.getenv("APP_PRIVILEGED_TEST_EMAILS", ""), DEFAULT_PRIVILEGED_TEST_EMAILS)[:5]),
                "seed_password": [seed_password],
            }
        admin_emails = _split_seed_emails(os.getenv("APP_ADMIN_EMAILS", ""), DEFAULT_ADMIN_EMAILS)[:3]
        test_emails = _split_seed_emails(os.getenv("APP_PRIVILEGED_TEST_EMAILS", ""), DEFAULT_PRIVILEGED_TEST_EMAILS)[:5]
        seed_password = str(os.getenv("APP_PRIVILEGED_SEED_PASSWORD", DEFAULT_PRIVILEGED_PASSWORD) or DEFAULT_PRIVILEGED_PASSWORD)
        password_hash = hash_password(seed_password)
        created_admins: list[str] = []
        created_tests: list[str] = []
        _SEEDING_PRIVILEGED_ACCOUNTS = True
        try:
            for email in admin_emails:
                existing = get_user_by_email(email)
                create_user_record(
                    email=email,
                    display_name=email.split("@", 1)[0],
                    password_hash=password_hash if existing is None else "",
                    auth_mode="password",
                    access_tier="admin",
                    status="admin_active",
                    email_verified=True,
                )
                created_admins.append(email)
            for email in test_emails:
                existing = get_user_by_email(email)
                create_user_record(
                    email=email,
                    display_name=email.split("@", 1)[0],
                    password_hash=password_hash if existing is None else "",
                    auth_mode="password",
                    access_tier="paid",
                    status="paid_active",
                    email_verified=True,
                )
                created_tests.append(email)
            _PRIVILEGED_SEED_DONE = True
        finally:
            _SEEDING_PRIVILEGED_ACCOUNTS = False
        return {
            "admins": created_admins,
            "tests": created_tests,
            "seed_password": [seed_password],
        }


def get_password_hash_by_email(email: str) -> str:
    init_project_store()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT password_hash
            FROM users
            WHERE lower(email) = lower(?)
            """,
            (str(email).strip(),),
        ).fetchone()
    if row is None:
        return ""
    return str(row["password_hash"] or "")


def create_user_record(
    *,
    email: str,
    display_name: str = "",
    password_hash: str = "",
    auth_mode: str = "password",
    access_tier: str = "trial",
    status: str = "trial_active",
    email_verified: bool = False,
) -> UserRecord:
    init_project_store()
    clean_email = str(email).strip().lower()
    clean_display = str(display_name).strip() or clean_email.split("@", 1)[0]
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO users (
                email, display_name, password_hash, auth_mode, access_tier, status, email_verified, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(email) DO UPDATE SET
                display_name = excluded.display_name,
                password_hash = CASE
                    WHEN excluded.password_hash <> '' THEN excluded.password_hash
                    ELSE users.password_hash
                END,
                auth_mode = excluded.auth_mode,
                access_tier = excluded.access_tier,
                status = excluded.status,
                email_verified = excluded.email_verified,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                clean_email,
                clean_display,
                str(password_hash),
                str(auth_mode),
                str(access_tier),
                str(status),
                bool(email_verified) if _get_backend_name() == "postgres" else (1 if email_verified else 0),
            ),
        )
    user = get_user_by_email(clean_email)
    assert user is not None
    return user


def authenticate_user(email: str, password: str) -> Optional[UserRecord]:
    user = get_user_by_email(email)
    if user is None:
        return None
    password_hash = get_password_hash_by_email(email)
    if not verify_password(password, password_hash):
        return None
    return user


def record_login_attempt(*, email: str, success: bool) -> None:
    init_project_store()
    clean_email = str(email or "").strip().lower()
    if not clean_email:
        return
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO login_attempts (email, success, attempted_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            """,
            (clean_email, bool(success) if _get_backend_name() == "postgres" else (1 if success else 0)),
        )


def clear_failed_login_attempts(email: str) -> None:
    init_project_store()
    clean_email = str(email or "").strip().lower()
    if not clean_email:
        return
    failed_false_sql = "FALSE" if _get_backend_name() == "postgres" else "0"
    with _connect() as conn:
        conn.execute(
            f"""
            DELETE FROM login_attempts
            WHERE lower(email) = lower(?) AND success = {failed_false_sql}
            """,
            (clean_email,),
        )


def get_login_rate_limit_status(
    email: str,
    *,
    max_failed_attempts: int = 5,
    window_minutes: int = 15,
    lock_minutes: int = 10,
) -> dict[str, Any]:
    init_project_store()
    clean_email = str(email or "").strip().lower()
    status = {
        "email": clean_email,
        "failed_attempts": 0,
        "is_locked": False,
        "retry_after_minutes": 0,
    }
    if not clean_email:
        return status
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT success, attempted_at
            FROM login_attempts
            WHERE lower(email) = lower(?)
            ORDER BY id DESC
            LIMIT 20
            """,
            (clean_email,),
        ).fetchall()
    now = datetime.now(timezone.utc)
    latest_failed_at: datetime | None = None
    for row in rows:
        raw_success = row["success"]
        success = bool(int(raw_success)) if str(raw_success).strip().isdigit() else bool(raw_success)
        if success:
            break
        attempted_at = _parse_datetime_guess(str(row["attempted_at"]))
        if attempted_at is None or attempted_at < now - timedelta(minutes=window_minutes):
            continue
        status["failed_attempts"] += 1
        if latest_failed_at is None:
            latest_failed_at = attempted_at
    if status["failed_attempts"] >= int(max_failed_attempts) and latest_failed_at is not None:
        unlock_at = latest_failed_at + timedelta(minutes=lock_minutes)
        if unlock_at > now:
            status["is_locked"] = True
            status["retry_after_minutes"] = max(1, int((unlock_at - now).total_seconds() // 60) + 1)
    return status


def set_user_access_status(
    *,
    email: str,
    access_tier: str,
    status: str,
    auth_mode: str | None = None,
) -> Optional[UserRecord]:
    init_project_store()
    with _connect() as conn:
        if auth_mode is None:
            conn.execute(
                """
                UPDATE users
                SET access_tier = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE lower(email) = lower(?)
                """,
                (str(access_tier), str(status), str(email).strip()),
            )
        else:
            conn.execute(
                """
                UPDATE users
                SET auth_mode = ?, access_tier = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE lower(email) = lower(?)
                """,
                (str(auth_mode), str(access_tier), str(status), str(email).strip()),
            )
    return get_user_by_email(email)


def set_user_email_verification(email: str, *, email_verified: bool, status: str | None = None) -> Optional[UserRecord]:
    init_project_store()
    params: list[Any] = [
        bool(email_verified) if _get_backend_name() == "postgres" else (1 if email_verified else 0),
    ]
    query = """
        UPDATE users
        SET email_verified = ?,
            updated_at = CURRENT_TIMESTAMP
    """
    if status is not None:
        query += ", status = ?"
        params.append(str(status))
    query += " WHERE lower(email) = lower(?)"
    params.append(str(email).strip())
    with _connect() as conn:
        conn.execute(query, params)
    return get_user_by_email(email)


def list_users(*, limit: int = 200) -> list[UserRecord]:
    init_project_store()
    clean_limit = max(1, min(1000, int(limit or 200)))
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, email, display_name, auth_mode, access_tier, status, email_verified, created_at, updated_at
            FROM users
            ORDER BY id ASC
            LIMIT ?
            """,
            (clean_limit,),
        ).fetchall()
    return [_user_record_from_row(row) for row in rows]


def get_user_subscription(user_id: int) -> Optional[SubscriptionRecord]:
    init_project_store()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT id, user_id, provider, plan_code, billing_status, customer_id,
                   subscription_id, checkout_url, portal_url, current_period_end,
                   created_at, updated_at
            FROM subscriptions
            WHERE user_id = ?
            """,
            (int(user_id),),
        ).fetchone()
    if row is None:
        return None
    return _subscription_record_from_row(row)


def upsert_user_subscription(
    *,
    user_id: int,
    provider: str = "lemon_squeezy",
    plan_code: str = "trial",
    billing_status: str = "trial",
    customer_id: str = "",
    subscription_id: str = "",
    checkout_url: str = "",
    portal_url: str = "",
    current_period_end: str = "",
) -> SubscriptionRecord:
    init_project_store()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO subscriptions (
                user_id, provider, plan_code, billing_status, customer_id, subscription_id,
                checkout_url, portal_url, current_period_end, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                provider = excluded.provider,
                plan_code = excluded.plan_code,
                billing_status = excluded.billing_status,
                customer_id = CASE
                    WHEN excluded.customer_id <> '' THEN excluded.customer_id
                    ELSE subscriptions.customer_id
                END,
                subscription_id = CASE
                    WHEN excluded.subscription_id <> '' THEN excluded.subscription_id
                    ELSE subscriptions.subscription_id
                END,
                checkout_url = CASE
                    WHEN excluded.checkout_url <> '' THEN excluded.checkout_url
                    ELSE subscriptions.checkout_url
                END,
                portal_url = CASE
                    WHEN excluded.portal_url <> '' THEN excluded.portal_url
                    ELSE subscriptions.portal_url
                END,
                current_period_end = CASE
                    WHEN excluded.current_period_end <> '' THEN excluded.current_period_end
                    ELSE subscriptions.current_period_end
                END,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                int(user_id),
                str(provider),
                str(plan_code),
                str(billing_status),
                str(customer_id),
                str(subscription_id),
                str(checkout_url),
                str(portal_url),
                str(current_period_end),
            ),
        )
    record = get_user_subscription(int(user_id))
    assert record is not None
    return record


def get_billing_event(provider_event_id: str) -> Optional[BillingEventRecord]:
    init_project_store()
    clean_event_id = str(provider_event_id or "").strip()
    if not clean_event_id:
        return None
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT id, provider, provider_event_id, event_type, user_id, email, status,
                   payload_json, billing_status, plan_code, error_message,
                   created_at, updated_at, processed_at
            FROM billing_events
            WHERE provider_event_id = ?
            """,
            (clean_event_id,),
        ).fetchone()
    if row is None:
        return None
    return _billing_event_record_from_row(row)


def record_billing_event(
    *,
    provider: str = "lemon_squeezy",
    provider_event_id: str,
    event_type: str = "",
    user_id: int = 0,
    email: str = "",
    payload_json: str = "",
) -> BillingEventRecord:
    init_project_store()
    clean_event_id = str(provider_event_id or "").strip()
    if not clean_event_id:
        raise ValueError("provider_event_id is required.")
    existing = get_billing_event(clean_event_id)
    if existing is not None:
        return existing
    with _connect() as conn:
        if _get_backend_name() == "postgres":
            row = conn.execute(
                """
                INSERT INTO billing_events (
                    provider, provider_event_id, event_type, user_id, email, status,
                    payload_json, billing_status, plan_code, error_message,
                    created_at, updated_at, processed_at
                )
                VALUES (?, ?, ?, ?, ?, 'received', ?, '', '', '', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '')
                ON CONFLICT (provider_event_id) DO NOTHING
                RETURNING id, provider, provider_event_id, event_type, user_id, email, status,
                          payload_json, billing_status, plan_code, error_message,
                          created_at, updated_at, processed_at
                """,
                (
                    str(provider or "lemon_squeezy"),
                    clean_event_id,
                    str(event_type or ""),
                    int(user_id),
                    str(email or "").strip().lower(),
                    str(payload_json or ""),
                ),
            ).fetchone()
            if row is None:
                row = conn.execute(
                    """
                    SELECT id, provider, provider_event_id, event_type, user_id, email, status,
                           payload_json, billing_status, plan_code, error_message,
                           created_at, updated_at, processed_at
                    FROM billing_events
                    WHERE provider_event_id = ?
                    """,
                    (clean_event_id,),
                ).fetchone()
        else:
            conn.execute(
                """
                INSERT OR IGNORE INTO billing_events (
                    provider, provider_event_id, event_type, user_id, email, status,
                    payload_json, billing_status, plan_code, error_message,
                    created_at, updated_at, processed_at
                )
                VALUES (?, ?, ?, ?, ?, 'received', ?, '', '', '', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '')
                """,
                (
                    str(provider or "lemon_squeezy"),
                    clean_event_id,
                    str(event_type or ""),
                    int(user_id),
                    str(email or "").strip().lower(),
                    str(payload_json or ""),
                ),
            )
            row = conn.execute(
                """
                SELECT id, provider, provider_event_id, event_type, user_id, email, status,
                       payload_json, billing_status, plan_code, error_message,
                       created_at, updated_at, processed_at
                FROM billing_events
                WHERE provider_event_id = ?
                """,
                (clean_event_id,),
            ).fetchone()
    assert row is not None
    return _billing_event_record_from_row(row)


def update_billing_event_status(
    provider_event_id: str,
    *,
    status: str,
    user_id: int = 0,
    email: str = "",
    billing_status: str = "",
    plan_code: str = "",
    error_message: str = "",
) -> Optional[BillingEventRecord]:
    init_project_store()
    clean_event_id = str(provider_event_id or "").strip()
    if not clean_event_id:
        return None
    clean_status = str(status or "").strip().lower() or "received"
    clean_email = str(email or "").strip().lower()
    clean_billing_status = str(billing_status or "").strip().lower()
    clean_plan_code = str(plan_code or "").strip()
    processed_at = _utc_now_iso() if clean_status in ("processed", "ignored") else ""
    with _connect() as conn:
        conn.execute(
            """
            UPDATE billing_events
            SET status = ?,
                user_id = CASE WHEN ? > 0 THEN ? ELSE user_id END,
                email = CASE WHEN ? <> '' THEN ? ELSE email END,
                billing_status = CASE WHEN ? <> '' THEN ? ELSE billing_status END,
                plan_code = CASE WHEN ? <> '' THEN ? ELSE plan_code END,
                error_message = ?,
                processed_at = CASE WHEN ? <> '' THEN ? ELSE processed_at END,
                updated_at = CURRENT_TIMESTAMP
            WHERE provider_event_id = ?
            """,
            (
                clean_status,
                int(user_id),
                int(user_id),
                clean_email,
                clean_email,
                clean_billing_status,
                clean_billing_status,
                clean_plan_code,
                clean_plan_code,
                str(error_message or ""),
                processed_at,
                processed_at,
                clean_event_id,
            ),
        )
    return get_billing_event(clean_event_id)


def list_recent_billing_events(
    *,
    user_id: int | None = None,
    status: str = "",
    limit: int = 50,
) -> list[BillingEventRecord]:
    init_project_store()
    clean_limit = max(1, min(500, int(limit or 50)))
    clean_status = str(status or "").strip().lower()
    query = """
        SELECT id, provider, provider_event_id, event_type, user_id, email, status,
               payload_json, billing_status, plan_code, error_message,
               created_at, updated_at, processed_at
        FROM billing_events
    """
    clauses: list[str] = []
    params: list[Any] = []
    if user_id is not None:
        clauses.append("user_id = ?")
        params.append(int(user_id))
    if clean_status:
        clauses.append("lower(status) = ?")
        params.append(clean_status)
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(clean_limit)
    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [_billing_event_record_from_row(row) for row in rows]


def get_billing_event_summary() -> dict[str, int]:
    init_project_store()
    with _connect() as conn:
        total = conn.execute("SELECT COUNT(*) AS c FROM billing_events").fetchone()
        processed = conn.execute(
            "SELECT COUNT(*) AS c FROM billing_events WHERE status = 'processed'"
        ).fetchone()
        failed = conn.execute(
            "SELECT COUNT(*) AS c FROM billing_events WHERE status = 'failed'"
        ).fetchone()
        ignored = conn.execute(
            "SELECT COUNT(*) AS c FROM billing_events WHERE status = 'ignored'"
        ).fetchone()
        received = conn.execute(
            "SELECT COUNT(*) AS c FROM billing_events WHERE status = 'received'"
        ).fetchone()
    return {
        "total": int(total["c"]) if total is not None else 0,
        "processed": int(processed["c"]) if processed is not None else 0,
        "failed": int(failed["c"]) if failed is not None else 0,
        "ignored": int(ignored["c"]) if ignored is not None else 0,
        "received": int(received["c"]) if received is not None else 0,
    }


def cleanup_billing_events(
    *,
    keep_processed_days: int = 180,
    keep_failed_days: int = 30,
    keep_ignored_days: int = 30,
) -> dict[str, int]:
    init_project_store()
    now = datetime.now(timezone.utc)
    processed_cutoff = (now - timedelta(days=max(1, int(keep_processed_days)))).replace(microsecond=0).isoformat()
    failed_cutoff = (now - timedelta(days=max(1, int(keep_failed_days)))).replace(microsecond=0).isoformat()
    ignored_cutoff = (now - timedelta(days=max(1, int(keep_ignored_days)))).replace(microsecond=0).isoformat()
    with _connect() as conn:
        before = conn.execute("SELECT COUNT(*) AS c FROM billing_events").fetchone()
        conn.execute(
            """
            DELETE FROM billing_events
            WHERE (status = 'processed' AND updated_at < ?)
               OR (status = 'failed' AND updated_at < ?)
               OR (status = 'ignored' AND updated_at < ?)
            """,
            (processed_cutoff, failed_cutoff, ignored_cutoff),
        )
        after = conn.execute("SELECT COUNT(*) AS c FROM billing_events").fetchone()
    pruned = max(0, int(before["c"]) - int(after["c"])) if before is not None and after is not None else 0
    return {
        "pruned_billing_events": pruned,
        "remaining_billing_events": int(after["c"]) if after is not None else 0,
    }


def create_export_job(
    *,
    user_id: int,
    project_id: int = 0,
    job_type: str,
    request_payload_json: str = "",
) -> ExportJobRecord:
    init_project_store()
    clean_job_type = str(job_type or "").strip().lower() or "unknown"
    with _connect() as conn:
        if _get_backend_name() == "postgres":
            row = conn.execute(
                """
                INSERT INTO export_jobs (
                    user_id, project_id, job_type, status, request_payload_json,
                    result_ref, error_message, created_at, started_at, finished_at, updated_at
                )
                VALUES (?, ?, ?, 'queued', ?, '', '', CURRENT_TIMESTAMP, '', '', CURRENT_TIMESTAMP)
                RETURNING id, user_id, project_id, job_type, status, request_payload_json,
                          result_ref, error_message, created_at, started_at, finished_at, updated_at
                """,
                (int(user_id), int(project_id), clean_job_type, str(request_payload_json or "")),
            ).fetchone()
        else:
            conn.execute(
                """
                INSERT INTO export_jobs (
                    user_id, project_id, job_type, status, request_payload_json,
                    result_ref, error_message, created_at, started_at, finished_at, updated_at
                )
                VALUES (?, ?, ?, 'queued', ?, '', '', CURRENT_TIMESTAMP, '', '', CURRENT_TIMESTAMP)
                """,
                (int(user_id), int(project_id), clean_job_type, str(request_payload_json or "")),
            )
            row = conn.execute(
                """
                SELECT id, user_id, project_id, job_type, status, request_payload_json,
                       result_ref, error_message, created_at, started_at, finished_at, updated_at
                FROM export_jobs
                WHERE id = last_insert_rowid()
                """
            ).fetchone()
    assert row is not None
    return _export_job_record_from_row(row)


def get_export_job(job_id: int, *, user_id: int | None = None) -> Optional[ExportJobRecord]:
    init_project_store()
    params: list[Any] = [int(job_id)]
    query = """
            SELECT id, user_id, project_id, job_type, status, request_payload_json,
                   result_ref, error_message, created_at, started_at, finished_at, updated_at
            FROM export_jobs
            WHERE id = ?
            """
    if user_id is not None:
        query += " AND user_id = ?"
        params.append(int(user_id))
    with _connect() as conn:
        row = conn.execute(query, params).fetchone()
    if row is None:
        return None
    return _export_job_record_from_row(row)


def claim_next_export_job() -> Optional[ExportJobRecord]:
    init_project_store()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT id, user_id, project_id, job_type, status, request_payload_json,
                   result_ref, error_message, created_at, started_at, finished_at, updated_at
            FROM export_jobs
            WHERE status = 'queued'
            ORDER BY id ASC
            LIMIT 1
            """
        ).fetchone()
        if row is None:
            return None
        conn.execute(
            """
            UPDATE export_jobs
            SET status = 'running',
                started_at = CASE
                    WHEN COALESCE(started_at, '') = '' THEN ?
                    ELSE started_at
                END,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND status = 'queued'
            """,
            (_utc_now_iso(), int(row["id"])),
        )
    return get_export_job(int(row["id"]))


def update_export_job_status(
    job_id: int,
    *,
    status: str,
    result_ref: str | None = None,
    error_message: str | None = None,
) -> Optional[ExportJobRecord]:
    init_project_store()
    clean_status = str(status or "").strip().lower() or "queued"
    started_at = _utc_now_iso() if clean_status == "running" else None
    finished_at = _utc_now_iso() if clean_status in {"done", "failed", "canceled"} else None
    update_fields = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
    params: list[Any] = [clean_status]
    if result_ref is not None:
        update_fields.append("result_ref = ?")
        params.append(str(result_ref or ""))
    if error_message is not None:
        update_fields.append("error_message = ?")
        params.append(str(error_message or ""))
    if started_at is not None:
        update_fields.append(
            """
            started_at = CASE
                WHEN COALESCE(started_at, '') = '' THEN ?
                ELSE started_at
            END
            """
        )
        params.append(str(started_at or ""))
    if finished_at is not None:
        update_fields.append("finished_at = ?")
        params.append(str(finished_at or ""))
    params.append(int(job_id))
    with _connect() as conn:
        conn.execute(
            f"""
            UPDATE export_jobs
            SET {", ".join(update_fields)}
            WHERE id = ?
            """,
            params,
        )
    return get_export_job(int(job_id))


def list_export_jobs_for_user(user_id: int, *, limit: int = 20) -> list[ExportJobRecord]:
    init_project_store()
    clean_limit = max(1, min(200, int(limit or 20)))
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, user_id, project_id, job_type, status, request_payload_json,
                   result_ref, error_message, created_at, started_at, finished_at, updated_at
            FROM export_jobs
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (int(user_id), clean_limit),
        ).fetchall()
    return [_export_job_record_from_row(row) for row in rows]


def count_active_export_jobs_for_user(user_id: int) -> int:
    init_project_store()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT COUNT(*) AS c
            FROM export_jobs
            WHERE user_id = ? AND status IN ('queued', 'running')
            """,
            (int(user_id),),
        ).fetchone()
    return int(row["c"]) if row is not None else 0


def expire_stale_export_jobs_for_user(
    user_id: int,
    *,
    queued_timeout_minutes: int = 15,
    running_timeout_minutes: int = 30,
) -> dict[str, int]:
    init_project_store()
    queued_cutoff = datetime.now(timezone.utc) - timedelta(minutes=max(1, int(queued_timeout_minutes or 15)))
    running_cutoff = datetime.now(timezone.utc) - timedelta(minutes=max(1, int(running_timeout_minutes or 30)))
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, status, updated_at, created_at, started_at
            FROM export_jobs
            WHERE user_id = ? AND status IN ('queued', 'running')
            """,
            (int(user_id),),
        ).fetchall()

    expired_queued = 0
    expired_running = 0
    for row in rows:
        status = str(row["status"] or "").strip().lower()
        probe = ""
        cutoff = queued_cutoff
        if status == "running":
            probe = str(row["started_at"] or row["updated_at"] or row["created_at"] or "")
            cutoff = running_cutoff
        else:
            probe = str(row["updated_at"] or row["created_at"] or "")
        stamp = _parse_datetime_guess(probe)
        if stamp is None or stamp > cutoff:
            continue
        message = (
            "Export job je automatski zatvoren jer je predugo ostao u obradi."
            if status == "running"
            else "Export job je automatski zatvoren jer je predugo ostao na cekanju."
        )
        updated = update_export_job_status(int(row["id"]), status="failed", error_message=message)
        if updated is None:
            continue
        if status == "running":
            expired_running += 1
        else:
            expired_queued += 1

    return {
        "expired_queued": int(expired_queued),
        "expired_running": int(expired_running),
        "expired_total": int(expired_queued + expired_running),
    }


def get_export_job_summary() -> dict[str, int]:
    init_project_store()
    with _connect() as conn:
        total = conn.execute("SELECT COUNT(*) AS c FROM export_jobs").fetchone()
        queued = conn.execute(
            "SELECT COUNT(*) AS c FROM export_jobs WHERE status = 'queued'"
        ).fetchone()
        running = conn.execute(
            "SELECT COUNT(*) AS c FROM export_jobs WHERE status = 'running'"
        ).fetchone()
        done = conn.execute(
            "SELECT COUNT(*) AS c FROM export_jobs WHERE status = 'done'"
        ).fetchone()
        failed = conn.execute(
            "SELECT COUNT(*) AS c FROM export_jobs WHERE status = 'failed'"
        ).fetchone()
        canceled = conn.execute(
            "SELECT COUNT(*) AS c FROM export_jobs WHERE status = 'canceled'"
        ).fetchone()
    return {
        "total": int(total["c"]) if total is not None else 0,
        "queued": int(queued["c"]) if queued is not None else 0,
        "running": int(running["c"]) if running is not None else 0,
        "done": int(done["c"]) if done is not None else 0,
        "failed": int(failed["c"]) if failed is not None else 0,
        "canceled": int(canceled["c"]) if canceled is not None else 0,
    }


def cleanup_export_jobs(
    *,
    keep_done_days: int = 30,
    keep_failed_days: int = 30,
    keep_canceled_days: int = 14,
) -> dict[str, int]:
    init_project_store()
    now = datetime.now(timezone.utc)
    done_cutoff = (now - timedelta(days=max(1, int(keep_done_days)))).replace(microsecond=0).isoformat()
    failed_cutoff = (now - timedelta(days=max(1, int(keep_failed_days)))).replace(microsecond=0).isoformat()
    canceled_cutoff = (now - timedelta(days=max(1, int(keep_canceled_days)))).replace(microsecond=0).isoformat()
    with _connect() as conn:
        before = conn.execute("SELECT COUNT(*) AS c FROM export_jobs").fetchone()
        conn.execute(
            """
            DELETE FROM export_jobs
            WHERE (status = 'done' AND updated_at < ?)
               OR (status = 'failed' AND updated_at < ?)
               OR (status = 'canceled' AND updated_at < ?)
            """,
            (done_cutoff, failed_cutoff, canceled_cutoff),
        )
        after = conn.execute("SELECT COUNT(*) AS c FROM export_jobs").fetchone()
    pruned = max(0, int(before["c"]) - int(after["c"])) if before is not None and after is not None else 0
    return {
        "pruned_export_jobs": pruned,
        "remaining_export_jobs": int(after["c"]) if after is not None else 0,
    }


def _project_record_from_row(row: Any) -> ProjectRecord:
    return ProjectRecord(
        id=int(row["id"]),
        user_id=int(row["user_id"]),
        name=str(row["name"]),
        project_type=str(row["project_type"]),
        kitchen_layout=str(row["kitchen_layout"]),
        language=str(row["language"]),
        source=str(row["source"]),
        is_demo=bool(row["is_demo"]),
        is_autosave=bool(row["is_autosave"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
        last_opened_at=str(row["last_opened_at"]),
    )


def _subscription_record_from_row(row: Any) -> SubscriptionRecord:
    return SubscriptionRecord(
        id=int(row["id"]),
        user_id=int(row["user_id"]),
        provider=str(row["provider"]),
        plan_code=str(row["plan_code"]),
        billing_status=str(row["billing_status"]),
        customer_id=str(row["customer_id"]),
        subscription_id=str(row["subscription_id"]),
        checkout_url=str(row["checkout_url"]),
        portal_url=str(row["portal_url"]),
        current_period_end=str(row["current_period_end"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


def _billing_event_record_from_row(row: Any) -> BillingEventRecord:
    return BillingEventRecord(
        id=int(row["id"]),
        provider=str(row["provider"]),
        provider_event_id=str(row["provider_event_id"]),
        event_type=str(row["event_type"]),
        user_id=int(row["user_id"]),
        email=str(row["email"]),
        status=str(row["status"]),
        payload_json=str(row["payload_json"]),
        billing_status=str(row["billing_status"]),
        plan_code=str(row["plan_code"]),
        error_message=str(row["error_message"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
        processed_at=str(row["processed_at"]),
    )


def _auth_session_record_from_row(row: Any) -> AuthSessionRecord:
    return AuthSessionRecord(
        id=int(row["id"]),
        user_id=int(row["user_id"]),
        session_token=str(row["session_token"]),
        session_kind=str(row["session_kind"]),
        auth_provider=str(row["auth_provider"]),
        status=str(row["status"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
        expires_at=str(row["expires_at"]),
        revoked_at=str(row["revoked_at"] or ""),
    )


def _password_reset_token_from_row(row: Any) -> PasswordResetTokenRecord:
    return PasswordResetTokenRecord(
        id=int(row["id"]),
        user_id=int(row["user_id"]),
        reset_token=str(row["reset_token"]),
        status=str(row["status"]),
        created_at=str(row["created_at"]),
        expires_at=str(row["expires_at"]),
        used_at=str(row["used_at"] or ""),
    )


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _future_utc_iso(*, days: int = 14) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=int(days))).replace(microsecond=0).isoformat()


def _future_utc_iso_minutes(*, minutes: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(minutes=int(minutes))).replace(microsecond=0).isoformat()


def _parse_datetime_guess(value: str) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        normalized = raw.replace("Z", "+00:00")
        probe = datetime.fromisoformat(normalized)
        if probe.tzinfo is None:
            return probe.replace(tzinfo=timezone.utc)
        return probe.astimezone(timezone.utc)
    except Exception:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
        except Exception:
            continue
    return None


def save_project_record(
    *,
    user_id: int,
    name: str,
    payload_json: str,
    project_type: str = "kitchen",
    kitchen_layout: str = "jedan_zid",
    language: str = "sr",
    source: str = "local",
    is_demo: bool = False,
    is_autosave: bool = False,
    replace_source: bool = False,
) -> ProjectRecord:
    init_project_store()
    autosave_true_sql = "TRUE" if _get_backend_name() == "postgres" else "1"
    with _connect() as conn:
        if is_autosave:
            conn.execute(
                f"""
                DELETE FROM projects
                WHERE user_id = ? AND is_autosave = {autosave_true_sql}
                """,
                (int(user_id),),
            )
        if replace_source:
            conn.execute(
                """
                DELETE FROM projects
                WHERE user_id = ? AND source = ?
                """,
                (int(user_id), str(source)),
            )
        if _get_backend_name() == "postgres":
            row = conn.execute(
                """
                INSERT INTO projects (
                    user_id, name, project_type, kitchen_layout, language, source,
                    is_demo, is_autosave, payload_json, created_at, updated_at, last_opened_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id, user_id, name, project_type, kitchen_layout, language, source,
                          is_demo, is_autosave, created_at, updated_at, last_opened_at
                """,
                (
                    int(user_id),
                    str(name),
                    str(project_type),
                    str(kitchen_layout),
                    str(language),
                    str(source),
                    bool(is_demo),
                    bool(is_autosave),
                    str(payload_json),
                ),
            ).fetchone()
        else:
            conn.execute(
                """
                INSERT INTO projects (
                    user_id, name, project_type, kitchen_layout, language, source,
                    is_demo, is_autosave, payload_json, created_at, updated_at, last_opened_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                (
                    int(user_id),
                    str(name),
                    str(project_type),
                    str(kitchen_layout),
                    str(language),
                    str(source),
                    1 if is_demo else 0,
                    1 if is_autosave else 0,
                    str(payload_json),
                ),
            )
            row = conn.execute(
                """
                SELECT id, user_id, name, project_type, kitchen_layout, language, source,
                       is_demo, is_autosave, created_at, updated_at, last_opened_at
                FROM projects
                WHERE id = last_insert_rowid()
                """
            ).fetchone()
        assert row is not None
        return _project_record_from_row(row)


def create_auth_session(
    *,
    user_id: int,
    session_kind: str = "browser",
    auth_provider: str = "password",
    expires_in_days: int = 14,
) -> AuthSessionRecord:
    init_project_store()
    session_token = secrets.token_urlsafe(32)
    expires_at = _future_utc_iso(days=max(1, int(expires_in_days)))
    with _connect() as conn:
        if _get_backend_name() == "postgres":
            row = conn.execute(
                """
                INSERT INTO auth_sessions (
                    user_id, session_token, session_kind, auth_provider, status,
                    created_at, updated_at, expires_at, revoked_at
                )
                VALUES (?, ?, ?, ?, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, NULL)
                RETURNING id, user_id, session_token, session_kind, auth_provider,
                          status, created_at, updated_at, expires_at, revoked_at
                """,
                (
                    int(user_id),
                    session_token,
                    str(session_kind),
                    str(auth_provider),
                    expires_at,
                ),
            ).fetchone()
        else:
            conn.execute(
                """
                INSERT INTO auth_sessions (
                    user_id, session_token, session_kind, auth_provider, status,
                    created_at, updated_at, expires_at, revoked_at
                )
                VALUES (?, ?, ?, ?, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, '')
                """,
                (
                    int(user_id),
                    session_token,
                    str(session_kind),
                    str(auth_provider),
                    expires_at,
                ),
            )
            row = conn.execute(
                """
                SELECT id, user_id, session_token, session_kind, auth_provider,
                       status, created_at, updated_at, expires_at, revoked_at
                FROM auth_sessions
                WHERE id = last_insert_rowid()
                """
            ).fetchone()
    assert row is not None
    return _auth_session_record_from_row(row)


def get_auth_session(session_token: str) -> Optional[AuthSessionRecord]:
    init_project_store()
    clean_token = str(session_token or "").strip()
    if not clean_token:
        return None
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT id, user_id, session_token, session_kind, auth_provider,
                   status, created_at, updated_at, expires_at, revoked_at
            FROM auth_sessions
            WHERE session_token = ?
            """,
            (clean_token,),
        ).fetchone()
    if row is None:
        return None
    return _auth_session_record_from_row(row)


def revoke_auth_session(session_token: str) -> Optional[AuthSessionRecord]:
    init_project_store()
    clean_token = str(session_token or "").strip()
    if not clean_token:
        return None
    revoked_at = _utc_now_iso()
    with _connect() as conn:
        conn.execute(
            """
            UPDATE auth_sessions
            SET status = 'revoked',
                revoked_at = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE session_token = ?
            """,
            (revoked_at, clean_token),
        )
    return get_auth_session(clean_token)


def revoke_user_auth_sessions(user_id: int, *, exclude_session_token: str = "") -> int:
    init_project_store()
    clean_exclude = str(exclude_session_token or "").strip()
    revoked_at = _utc_now_iso()
    with _connect() as conn:
        if clean_exclude:
            before = conn.execute(
                """
                SELECT COUNT(*) AS c
                FROM auth_sessions
                WHERE user_id = ? AND status = 'active' AND session_token <> ?
                """,
                (int(user_id), clean_exclude),
            ).fetchone()
            conn.execute(
                """
                UPDATE auth_sessions
                SET status = 'revoked',
                    revoked_at = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND status = 'active' AND session_token <> ?
                """,
                (revoked_at, int(user_id), clean_exclude),
            )
        else:
            before = conn.execute(
                """
                SELECT COUNT(*) AS c
                FROM auth_sessions
                WHERE user_id = ? AND status = 'active'
                """,
                (int(user_id),),
            ).fetchone()
            conn.execute(
                """
                UPDATE auth_sessions
                SET status = 'revoked',
                    revoked_at = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND status = 'active'
                """,
                (revoked_at, int(user_id)),
            )
    return int(before["c"]) if before is not None else 0


def expire_auth_session(session_token: str) -> Optional[AuthSessionRecord]:
    init_project_store()
    clean_token = str(session_token or "").strip()
    if not clean_token:
        return None
    revoked_at = _utc_now_iso()
    with _connect() as conn:
        conn.execute(
            """
            UPDATE auth_sessions
            SET status = 'expired',
                revoked_at = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE session_token = ? AND status = 'active'
            """,
            (revoked_at, clean_token),
        )
    return get_auth_session(clean_token)


def touch_auth_session(session_token: str) -> Optional[AuthSessionRecord]:
    init_project_store()
    clean_token = str(session_token or "").strip()
    if not clean_token:
        return None
    with _connect() as conn:
        conn.execute(
            """
            UPDATE auth_sessions
            SET updated_at = CURRENT_TIMESTAMP
            WHERE session_token = ? AND status = 'active'
            """,
            (clean_token,),
        )
    return get_auth_session(clean_token)


def get_effective_auth_session(session_token: str) -> Optional[AuthSessionRecord]:
    record = get_auth_session(session_token)
    if record is None:
        return None
    expires_at = _parse_datetime_guess(str(record.expires_at))
    if expires_at is not None and expires_at <= datetime.now(timezone.utc):
        record = expire_auth_session(session_token)
    return record


def create_password_reset_token(
    *,
    email: str,
    expires_in_minutes: int = 30,
) -> Optional[PasswordResetTokenRecord]:
    user = get_user_by_email(email)
    if user is None:
        return None
    init_project_store()
    reset_token = secrets.token_urlsafe(24)
    expires_at = _future_utc_iso_minutes(minutes=max(5, int(expires_in_minutes)))
    with _connect() as conn:
        conn.execute(
            """
            UPDATE password_reset_tokens
            SET status = 'replaced',
                used_at = ?
            WHERE user_id = ? AND status = 'active'
            """,
            (_utc_now_iso(), int(user.id)),
        )
        if _get_backend_name() == "postgres":
            row = conn.execute(
                """
                INSERT INTO password_reset_tokens (
                    user_id, reset_token, status, created_at, expires_at, used_at
                )
                VALUES (?, ?, 'active', CURRENT_TIMESTAMP, ?, NULL)
                RETURNING id, user_id, reset_token, status, created_at, expires_at, used_at
                """,
                (int(user.id), reset_token, expires_at),
            ).fetchone()
        else:
            conn.execute(
                """
                INSERT INTO password_reset_tokens (
                    user_id, reset_token, status, created_at, expires_at, used_at
                )
                VALUES (?, ?, 'active', CURRENT_TIMESTAMP, ?, '')
                """,
                (int(user.id), reset_token, expires_at),
            )
            row = conn.execute(
                """
                SELECT id, user_id, reset_token, status, created_at, expires_at, used_at
                FROM password_reset_tokens
                WHERE id = last_insert_rowid()
                """
            ).fetchone()
    if row is None:
        return None
    return _password_reset_token_from_row(row)


def get_password_reset_token(reset_token: str) -> Optional[PasswordResetTokenRecord]:
    init_project_store()
    clean_token = str(reset_token or "").strip()
    if not clean_token:
        return None
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT id, user_id, reset_token, status, created_at, expires_at, used_at
            FROM password_reset_tokens
            WHERE reset_token = ?
            """,
            (clean_token,),
        ).fetchone()
    if row is None:
        return None
    return _password_reset_token_from_row(row)


def get_effective_password_reset_token(reset_token: str) -> Optional[PasswordResetTokenRecord]:
    record = get_password_reset_token(reset_token)
    if record is None:
        return None
    expires_at = _parse_datetime_guess(str(record.expires_at))
    if str(record.status).lower() != "active":
        return record
    if expires_at is not None and expires_at <= datetime.now(timezone.utc):
        with _connect() as conn:
            conn.execute(
                """
                UPDATE password_reset_tokens
                SET status = 'expired',
                    used_at = ?
                WHERE reset_token = ? AND status = 'active'
                """,
                (_utc_now_iso(), str(reset_token)),
            )
        return get_password_reset_token(reset_token)
    return record


def use_password_reset_token(*, reset_token: str, new_password_hash: str) -> Optional[UserRecord]:
    token_record = get_effective_password_reset_token(reset_token)
    if token_record is None:
        return None
    if str(token_record.status).lower() != "active":
        return None
    with _connect() as conn:
        conn.execute(
            """
            UPDATE users
            SET password_hash = ?,
                auth_mode = 'password',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (str(new_password_hash), int(token_record.user_id)),
        )
        conn.execute(
            """
            UPDATE password_reset_tokens
            SET status = 'used',
                used_at = ?
            WHERE reset_token = ? AND status = 'active'
            """,
            (_utc_now_iso(), str(reset_token)),
        )
        conn.execute(
            """
            UPDATE auth_sessions
            SET status = 'revoked',
                revoked_at = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND status = 'active'
            """,
            (_utc_now_iso(), int(token_record.user_id)),
        )
    return get_user_by_id(int(token_record.user_id))


def create_email_verification_token(
    *,
    email: str,
    expires_in_minutes: int = 1440,
    reuse_existing_active: bool = False,
) -> Optional[EmailVerificationTokenRecord]:
    user = get_user_by_email(email)
    if user is None:
        return None
    init_project_store()
    if reuse_existing_active:
        with _connect() as conn:
            row = conn.execute(
                """
                SELECT id, user_id, email, verification_token, status, created_at, expires_at, used_at
                FROM email_verification_tokens
                WHERE user_id = ? AND status = 'active'
                ORDER BY id DESC
                LIMIT 1
                """,
                (int(user.id),),
            ).fetchone()
        if row is not None:
            existing = _email_verification_token_from_row(row)
            expires_at = _parse_datetime_guess(str(existing.expires_at))
            if expires_at is None or expires_at > datetime.now(timezone.utc):
                return existing
    verification_token = secrets.token_urlsafe(32)
    expires_at = _future_utc_iso_minutes(minutes=max(10, int(expires_in_minutes or 1440)))
    with _connect() as conn:
        conn.execute(
            """
            UPDATE email_verification_tokens
            SET status = 'replaced',
                used_at = ?
            WHERE user_id = ? AND status = 'active'
            """,
            (_utc_now_iso(), int(user.id)),
        )
        if _get_backend_name() == "postgres":
            row = conn.execute(
                """
                INSERT INTO email_verification_tokens (
                    user_id, email, verification_token, status, created_at, expires_at, used_at
                )
                VALUES (?, ?, ?, 'active', CURRENT_TIMESTAMP, ?, NULL)
                RETURNING id, user_id, email, verification_token, status, created_at, expires_at, used_at
                """,
                (int(user.id), str(user.email), verification_token, expires_at),
            ).fetchone()
        else:
            conn.execute(
                """
                INSERT INTO email_verification_tokens (
                    user_id, email, verification_token, status, created_at, expires_at, used_at
                )
                VALUES (?, ?, ?, 'active', CURRENT_TIMESTAMP, ?, '')
                """,
                (int(user.id), str(user.email), verification_token, expires_at),
            )
            row = conn.execute(
                """
                SELECT id, user_id, email, verification_token, status, created_at, expires_at, used_at
                FROM email_verification_tokens
                WHERE id = last_insert_rowid()
                """
            ).fetchone()
    if row is None:
        return None
    return _email_verification_token_from_row(row)


def get_email_verification_token(verification_token: str) -> Optional[EmailVerificationTokenRecord]:
    init_project_store()
    clean_token = str(verification_token or "").strip()
    if not clean_token:
        return None
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT id, user_id, email, verification_token, status, created_at, expires_at, used_at
            FROM email_verification_tokens
            WHERE verification_token = ?
            """,
            (clean_token,),
        ).fetchone()
    if row is None:
        return None
    return _email_verification_token_from_row(row)


def get_effective_email_verification_token(verification_token: str) -> Optional[EmailVerificationTokenRecord]:
    record = get_email_verification_token(verification_token)
    if record is None:
        return None
    expires_at = _parse_datetime_guess(str(record.expires_at))
    if str(record.status).lower() != "active":
        return record
    if expires_at is not None and expires_at <= datetime.now(timezone.utc):
        with _connect() as conn:
            conn.execute(
                """
                UPDATE email_verification_tokens
                SET status = 'expired',
                    used_at = ?
                WHERE verification_token = ? AND status = 'active'
                """,
                (_utc_now_iso(), str(verification_token)),
            )
        return get_email_verification_token(verification_token)
    return record


def _active_status_for_access_tier(access_tier: str) -> str:
    clean_tier = str(access_tier or "").strip().lower()
    if clean_tier == "admin":
        return "admin_active"
    if clean_tier in {"paid", "pro"}:
        return "paid_active"
    if clean_tier == "local_beta":
        return "local_active"
    return "trial_active"


def use_email_verification_token(*, verification_token: str) -> Optional[UserRecord]:
    token_record = get_effective_email_verification_token(verification_token)
    if token_record is None:
        return None
    if str(token_record.status).lower() != "active":
        return None
    user = get_user_by_id(int(token_record.user_id))
    if user is None:
        return None
    next_status = _active_status_for_access_tier(str(user.access_tier))
    with _connect() as conn:
        conn.execute(
            """
            UPDATE users
            SET email_verified = ?,
                status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                True if _get_backend_name() == "postgres" else 1,
                next_status,
                int(token_record.user_id),
            ),
        )
        conn.execute(
            """
            UPDATE email_verification_tokens
            SET status = 'used',
                used_at = ?
            WHERE verification_token = ? AND status = 'active'
            """,
            (_utc_now_iso(), str(verification_token)),
        )
    return get_user_by_id(int(token_record.user_id))


def cleanup_auth_artifacts(
    *,
    keep_login_attempts_days: int = 30,
    keep_reset_tokens_days: int = 7,
    keep_verification_tokens_days: int = 7,
    keep_revoked_sessions_days: int = 30,
) -> dict[str, int]:
    init_project_store()
    now = datetime.now(timezone.utc)
    reset_cutoff = (now - timedelta(days=max(1, int(keep_reset_tokens_days)))).replace(microsecond=0).isoformat()
    verification_cutoff = (now - timedelta(days=max(1, int(keep_verification_tokens_days)))).replace(microsecond=0).isoformat()
    login_cutoff = (now - timedelta(days=max(1, int(keep_login_attempts_days)))).replace(microsecond=0).isoformat()
    session_cutoff = (now - timedelta(days=max(1, int(keep_revoked_sessions_days)))).replace(microsecond=0).isoformat()

    expired_sessions = 0
    expired_resets = 0
    expired_verifications = 0
    pruned_attempts = 0
    pruned_sessions = 0
    pruned_resets = 0
    pruned_verifications = 0

    with _connect() as conn:
        session_rows = conn.execute(
            """
            SELECT session_token, expires_at
            FROM auth_sessions
            WHERE status = 'active'
            """
        ).fetchall()
        for row in session_rows:
            expires_at = _parse_datetime_guess(str(row["expires_at"]))
            if expires_at is not None and expires_at <= now:
                conn.execute(
                    """
                    UPDATE auth_sessions
                    SET status = 'expired',
                        revoked_at = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE session_token = ? AND status = 'active'
                    """,
                    (_utc_now_iso(), str(row["session_token"])),
                )
                expired_sessions += 1

        reset_rows = conn.execute(
            """
            SELECT reset_token, expires_at
            FROM password_reset_tokens
            WHERE status = 'active'
            """
        ).fetchall()
        for row in reset_rows:
            expires_at = _parse_datetime_guess(str(row["expires_at"]))
            if expires_at is not None and expires_at <= now:
                conn.execute(
                    """
                    UPDATE password_reset_tokens
                    SET status = 'expired',
                        used_at = ?
                    WHERE reset_token = ? AND status = 'active'
                    """,
                    (_utc_now_iso(), str(row["reset_token"])),
                )
                expired_resets += 1

        verification_rows = conn.execute(
            """
            SELECT verification_token, expires_at
            FROM email_verification_tokens
            WHERE status = 'active'
            """
        ).fetchall()
        for row in verification_rows:
            expires_at = _parse_datetime_guess(str(row["expires_at"]))
            if expires_at is not None and expires_at <= now:
                conn.execute(
                    """
                    UPDATE email_verification_tokens
                    SET status = 'expired',
                        used_at = ?
                    WHERE verification_token = ? AND status = 'active'
                    """,
                    (_utc_now_iso(), str(row["verification_token"])),
                )
                expired_verifications += 1

        attempts_before = conn.execute("SELECT COUNT(*) AS c FROM login_attempts").fetchone()
        conn.execute(
            """
            DELETE FROM login_attempts
            WHERE attempted_at < ?
            """,
            (login_cutoff,),
        )
        attempts_after = conn.execute("SELECT COUNT(*) AS c FROM login_attempts").fetchone()
        pruned_attempts = max(0, int(attempts_before["c"]) - int(attempts_after["c"]))

        sessions_before = conn.execute("SELECT COUNT(*) AS c FROM auth_sessions").fetchone()
        conn.execute(
            """
            DELETE FROM auth_sessions
            WHERE status IN ('revoked', 'expired') AND updated_at < ?
            """,
            (session_cutoff,),
        )
        sessions_after = conn.execute("SELECT COUNT(*) AS c FROM auth_sessions").fetchone()
        pruned_sessions = max(0, int(sessions_before["c"]) - int(sessions_after["c"]))

        resets_before = conn.execute("SELECT COUNT(*) AS c FROM password_reset_tokens").fetchone()
        conn.execute(
            """
            DELETE FROM password_reset_tokens
            WHERE status IN ('used', 'expired', 'replaced') AND created_at < ?
            """,
            (reset_cutoff,),
        )
        resets_after = conn.execute("SELECT COUNT(*) AS c FROM password_reset_tokens").fetchone()
        pruned_resets = max(0, int(resets_before["c"]) - int(resets_after["c"]))

        verifications_before = conn.execute("SELECT COUNT(*) AS c FROM email_verification_tokens").fetchone()
        conn.execute(
            """
            DELETE FROM email_verification_tokens
            WHERE status IN ('used', 'expired', 'replaced') AND created_at < ?
            """,
            (verification_cutoff,),
        )
        verifications_after = conn.execute("SELECT COUNT(*) AS c FROM email_verification_tokens").fetchone()
        pruned_verifications = max(0, int(verifications_before["c"]) - int(verifications_after["c"]))

    return {
        "expired_sessions": expired_sessions,
        "expired_reset_tokens": expired_resets,
        "expired_verification_tokens": expired_verifications,
        "pruned_login_attempts": pruned_attempts,
        "pruned_sessions": pruned_sessions,
        "pruned_reset_tokens": pruned_resets,
        "pruned_verification_tokens": pruned_verifications,
    }


def get_auth_runtime_summary() -> dict[str, int]:
    init_project_store()
    failed_false_sql = "FALSE" if _get_backend_name() == "postgres" else "0"
    with _connect() as conn:
        active_sessions = conn.execute(
            "SELECT COUNT(*) AS c FROM auth_sessions WHERE status = 'active'"
        ).fetchone()
        reset_tokens = conn.execute(
            "SELECT COUNT(*) AS c FROM password_reset_tokens WHERE status = 'active'"
        ).fetchone()
        verification_tokens = conn.execute(
            "SELECT COUNT(*) AS c FROM email_verification_tokens WHERE status = 'active'"
        ).fetchone()
        failed_login_attempts = conn.execute(
            f"SELECT COUNT(*) AS c FROM login_attempts WHERE success = {failed_false_sql}"
        ).fetchone()
    return {
        "active_sessions": int(active_sessions["c"]) if active_sessions is not None else 0,
        "active_reset_tokens": int(reset_tokens["c"]) if reset_tokens is not None else 0,
        "active_verification_tokens": int(verification_tokens["c"]) if verification_tokens is not None else 0,
        "failed_login_attempts": int(failed_login_attempts["c"]) if failed_login_attempts is not None else 0,
    }


def list_projects_for_user(user_id: int, *, include_autosave: bool = False) -> list[ProjectRecord]:
    init_project_store()
    autosave_false_sql = "FALSE" if _get_backend_name() == "postgres" else "0"
    query = """
        SELECT id, user_id, name, project_type, kitchen_layout, language, source,
               is_demo, is_autosave, created_at, updated_at, last_opened_at
        FROM projects
        WHERE user_id = ?
    """
    params: list[Any] = [int(user_id)]
    if not include_autosave:
        query += f" AND is_autosave = {autosave_false_sql}"
    query += " ORDER BY last_opened_at DESC, id DESC"
    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [_project_record_from_row(row) for row in rows]


def list_projects_for_user_by_source(
    user_id: int,
    *,
    source: str,
    include_autosave: bool = False,
    limit: int = 20,
) -> list[ProjectRecord]:
    init_project_store()
    clean_limit = max(1, min(200, int(limit or 20)))
    autosave_false_sql = "FALSE" if _get_backend_name() == "postgres" else "0"
    query = """
        SELECT id, user_id, name, project_type, kitchen_layout, language, source,
               is_demo, is_autosave, created_at, updated_at, last_opened_at
        FROM projects
        WHERE user_id = ? AND source = ?
    """
    params: list[Any] = [int(user_id), str(source)]
    if not include_autosave:
        query += f" AND is_autosave = {autosave_false_sql}"
    query += " ORDER BY last_opened_at DESC, id DESC LIMIT ?"
    params.append(clean_limit)
    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [_project_record_from_row(row) for row in rows]


def get_user_autosave_project(user_id: int) -> Optional[ProjectRecord]:
    init_project_store()
    autosave_true_sql = "TRUE" if _get_backend_name() == "postgres" else "1"
    with _connect() as conn:
        row = conn.execute(
            f"""
            SELECT id, user_id, name, project_type, kitchen_layout, language, source,
                   is_demo, is_autosave, created_at, updated_at, last_opened_at
            FROM projects
            WHERE user_id = ? AND is_autosave = {autosave_true_sql}
            ORDER BY updated_at DESC, id DESC
            LIMIT 1
            """,
            (int(user_id),),
        ).fetchone()
    if row is None:
        return None
    return _project_record_from_row(row)


def get_project_payload(project_id: int, *, user_id: int | None = None) -> Optional[str]:
    init_project_store()
    params: list[Any] = [int(project_id)]
    query = """
            SELECT payload_json
            FROM projects
            WHERE id = ?
            """
    if user_id is not None:
        query += " AND user_id = ?"
        params.append(int(user_id))
    with _connect() as conn:
        row = conn.execute(query, params).fetchone()
    if row is None:
        return None
    return str(row["payload_json"])


def get_project_record(project_id: int, *, user_id: int | None = None) -> Optional[ProjectRecord]:
    init_project_store()
    params: list[Any] = [int(project_id)]
    query = """
            SELECT id, user_id, name, project_type, kitchen_layout, language, source,
                   is_demo, is_autosave, created_at, updated_at, last_opened_at
            FROM projects
            WHERE id = ?
            """
    if user_id is not None:
        query += " AND user_id = ?"
        params.append(int(user_id))
    with _connect() as conn:
        row = conn.execute(query, params).fetchone()
    if row is None:
        return None
    return _project_record_from_row(row)


def touch_project_opened(project_id: int, *, user_id: int | None = None) -> bool:
    init_project_store()
    params: list[Any] = [int(project_id)]
    query = """
            UPDATE projects
            SET last_opened_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """
    if user_id is not None:
        query += " AND user_id = ?"
        params.append(int(user_id))
    with _connect() as conn:
        result = conn.execute(query, params)
    return int(getattr(result, "rowcount", 0) or 0) > 0


def save_payload_from_bytes(
    *,
    user_id: int,
    name: str,
    payload_bytes: bytes,
    source: str = "local",
    is_demo: bool = False,
    is_autosave: bool = False,
    replace_source: bool = False,
) -> ProjectRecord:
    payload = json.loads(payload_bytes.decode("utf-8"))
    kitchen = payload.get("kitchen", {}) if isinstance(payload, dict) else {}
    return save_project_record(
        user_id=user_id,
        name=name,
        payload_json=json.dumps(payload, ensure_ascii=False, indent=2),
        project_type=str(payload.get("project_type", "kitchen") or "kitchen"),
        kitchen_layout=str(payload.get("kitchen_layout", kitchen.get("layout", "jedan_zid")) or "jedan_zid"),
        language=str(payload.get("language", "sr") or "sr"),
        source=source,
        is_demo=is_demo,
        is_autosave=is_autosave,
        replace_source=replace_source,
    )


def bootstrap_demo_and_autosave(
    *,
    demo_payload_bytes: bytes | None = None,
    autosave_payload_bytes: bytes | None = None,
) -> dict[str, int]:
    user = ensure_local_user()
    created: dict[str, int] = {"user_id": user.id}
    if demo_payload_bytes:
        demo = save_payload_from_bytes(
            user_id=user.id,
            name="Demo primer",
            payload_bytes=demo_payload_bytes,
            source="seed_demo",
            is_demo=True,
            is_autosave=False,
            replace_source=True,
        )
        created["demo_project_id"] = demo.id
    if autosave_payload_bytes:
        autosave = save_payload_from_bytes(
            user_id=user.id,
            name="Auto-save",
            payload_bytes=autosave_payload_bytes,
            source="seed_autosave",
            is_demo=False,
            is_autosave=True,
            replace_source=True,
        )
        created["autosave_project_id"] = autosave.id
    return created


def export_store_snapshot() -> dict[str, Any]:
    init_project_store()
    with _connect() as conn:
        users = conn.execute(
            """
            SELECT id, email, display_name, auth_mode, access_tier, status, email_verified, created_at, updated_at
            FROM users
            ORDER BY id ASC
            """
        ).fetchall()
        projects = conn.execute(
            """
            SELECT id, user_id, name, project_type, kitchen_layout, language, source,
                   is_demo, is_autosave, created_at, updated_at, last_opened_at, payload_json
            FROM projects
            ORDER BY user_id ASC, id ASC
            """
        ).fetchall()
        subscriptions = conn.execute(
            """
            SELECT id, user_id, provider, plan_code, billing_status, customer_id,
                   subscription_id, checkout_url, portal_url, current_period_end,
                   created_at, updated_at
            FROM subscriptions
            ORDER BY user_id ASC, id ASC
            """
        ).fetchall()
        billing_events = conn.execute(
            """
            SELECT id, provider, provider_event_id, event_type, user_id, email, status,
                   payload_json, billing_status, plan_code, error_message,
                   created_at, updated_at, processed_at
            FROM billing_events
            ORDER BY id ASC
            """
        ).fetchall()
        auth_sessions = conn.execute(
            """
            SELECT id, user_id, session_token, session_kind, auth_provider,
                   status, created_at, updated_at, expires_at, revoked_at
            FROM auth_sessions
            ORDER BY user_id ASC, id ASC
            """
        ).fetchall()
        password_reset_tokens = conn.execute(
            """
            SELECT id, user_id, reset_token, status, created_at, expires_at, used_at
            FROM password_reset_tokens
            ORDER BY user_id ASC, id ASC
            """
        ).fetchall()
        email_verification_tokens = conn.execute(
            """
            SELECT id, user_id, email, verification_token, status, created_at, expires_at, used_at
            FROM email_verification_tokens
            ORDER BY user_id ASC, id ASC
            """
        ).fetchall()
        login_attempts = conn.execute(
            """
            SELECT id, email, success, attempted_at
            FROM login_attempts
            ORDER BY id ASC
            """
        ).fetchall()
        export_jobs = conn.execute(
            """
            SELECT id, user_id, project_id, job_type, status, request_payload_json,
                   result_ref, error_message, created_at, started_at, finished_at, updated_at
            FROM export_jobs
            ORDER BY user_id ASC, id ASC
            """
        ).fetchall()
        audit_logs = conn.execute(
            """
            SELECT id, user_id, event_type, status, detail, created_at
            FROM audit_logs
            ORDER BY id ASC
            """
        ).fetchall()
    return {
        "runtime": get_project_store_runtime_info(),
        "users": [dict(row) for row in users],
        "projects": [dict(row) for row in projects],
        "subscriptions": [dict(row) for row in subscriptions],
        "billing_events": [dict(row) for row in billing_events],
        "auth_sessions": [dict(row) for row in auth_sessions],
        "password_reset_tokens": [dict(row) for row in password_reset_tokens],
        "email_verification_tokens": [dict(row) for row in email_verification_tokens],
        "login_attempts": [dict(row) for row in login_attempts],
        "export_jobs": [dict(row) for row in export_jobs],
        "audit_logs": [dict(row) for row in audit_logs],
    }


def write_store_snapshot_file(path: str) -> str:
    target = str(path or "").strip()
    if not target:
        raise ValueError("Path for store snapshot is required.")
    payload = export_store_snapshot()
    from pathlib import Path
    out_path = Path(target)
    if not out_path.is_absolute():
        out_path = out_path.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return str(out_path)
