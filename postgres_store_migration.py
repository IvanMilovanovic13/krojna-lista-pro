# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app_config import get_database_config


POSTGRES_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL DEFAULT '',
    password_hash TEXT NOT NULL DEFAULT '',
    auth_mode TEXT NOT NULL DEFAULT 'local',
    access_tier TEXT NOT NULL DEFAULT 'local_beta',
    status TEXT NOT NULL DEFAULT 'local_active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    project_type TEXT NOT NULL DEFAULT 'kitchen',
    kitchen_layout TEXT NOT NULL DEFAULT 'jedan_zid',
    language TEXT NOT NULL DEFAULT 'sr',
    source TEXT NOT NULL DEFAULT 'local',
    is_demo BOOLEAN NOT NULL DEFAULT FALSE,
    is_autosave BOOLEAN NOT NULL DEFAULT FALSE,
    payload_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_opened_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    provider TEXT NOT NULL DEFAULT 'lemon_squeezy',
    plan_code TEXT NOT NULL DEFAULT 'trial',
    billing_status TEXT NOT NULL DEFAULT 'trial',
    customer_id TEXT NOT NULL DEFAULT '',
    subscription_id TEXT NOT NULL DEFAULT '',
    checkout_url TEXT NOT NULL DEFAULT '',
    portal_url TEXT NOT NULL DEFAULT '',
    current_period_end TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS billing_events (
    id BIGSERIAL PRIMARY KEY,
    provider TEXT NOT NULL DEFAULT 'lemon_squeezy',
    provider_event_id TEXT NOT NULL UNIQUE,
    event_type TEXT NOT NULL DEFAULT '',
    user_id BIGINT NOT NULL DEFAULT 0,
    email TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'received',
    payload_json TEXT NOT NULL DEFAULT '',
    billing_status TEXT NOT NULL DEFAULT '',
    plan_code TEXT NOT NULL DEFAULT '',
    error_message TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS auth_sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token TEXT NOT NULL UNIQUE,
    session_kind TEXT NOT NULL DEFAULT 'browser',
    auth_provider TEXT NOT NULL DEFAULT 'password',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_last_opened_at ON projects(last_opened_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_projects_autosave_per_user ON projects(user_id, is_autosave) WHERE is_autosave = TRUE;
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_billing_events_provider_event_id ON billing_events(provider_event_id);
CREATE INDEX IF NOT EXISTS idx_billing_events_email_created_at ON billing_events(email, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_id ON auth_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_token ON auth_sessions(session_token);

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reset_token TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS login_attempts (
    id BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    success BOOLEAN NOT NULL DEFAULT FALSE,
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL DEFAULT 0,
    event_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'info',
    detail TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS export_jobs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id BIGINT NOT NULL DEFAULT 0,
    job_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    request_payload_json TEXT NOT NULL DEFAULT '',
    result_ref TEXT NOT NULL DEFAULT '',
    error_message TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TEXT NOT NULL DEFAULT '',
    finished_at TEXT NOT NULL DEFAULT '',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens(reset_token);
CREATE INDEX IF NOT EXISTS idx_login_attempts_email_time ON login_attempts(email, attempted_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_export_jobs_user_id ON export_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_export_jobs_status_created ON export_jobs(status, created_at DESC);
"""


def get_postgres_schema_sql() -> str:
    return POSTGRES_SCHEMA_SQL.strip() + "\n"


def _load_snapshot(snapshot_path: str) -> dict[str, Any]:
    path = Path(snapshot_path)
    return json.loads(path.read_text(encoding="utf-8"))


def _clean_timestamp(value: Any, *, fallback_now: bool = False) -> str | None:
    text = str(value or "").strip()
    if text:
        return text
    if fallback_now:
        return datetime.now(timezone.utc).isoformat()
    return None


def import_snapshot_to_postgres(*, snapshot_path: str, database_url: str = "") -> dict[str, str]:
    try:
        import psycopg
    except Exception as ex:
        return {
            "ok": "false",
            "message": f"psycopg nije dostupan: {ex}",
        }

    target_url = str(database_url or "").strip() or str(get_database_config().url)
    if not target_url.startswith(("postgres://", "postgresql://")):
        return {
            "ok": "false",
            "message": "Za import je potreban postgres DATABASE_URL.",
        }

    payload = _load_snapshot(snapshot_path)
    users = payload.get("users", []) if isinstance(payload.get("users", []), list) else []
    projects = payload.get("projects", []) if isinstance(payload.get("projects", []), list) else []
    subscriptions = payload.get("subscriptions", []) if isinstance(payload.get("subscriptions", []), list) else []
    billing_events = payload.get("billing_events", []) if isinstance(payload.get("billing_events", []), list) else []
    auth_sessions = payload.get("auth_sessions", []) if isinstance(payload.get("auth_sessions", []), list) else []
    password_reset_tokens = payload.get("password_reset_tokens", []) if isinstance(payload.get("password_reset_tokens", []), list) else []
    login_attempts = payload.get("login_attempts", []) if isinstance(payload.get("login_attempts", []), list) else []
    export_jobs = payload.get("export_jobs", []) if isinstance(payload.get("export_jobs", []), list) else []
    audit_logs = payload.get("audit_logs", []) if isinstance(payload.get("audit_logs", []), list) else []

    known_user_ids = {
        int(user.get("id", 0) or 0)
        for user in users
        if int(user.get("id", 0) or 0) > 0
    }
    referenced_user_ids: set[int] = set()
    for rows in (projects, subscriptions, auth_sessions, password_reset_tokens, export_jobs):
        for row in rows:
            user_id = int(row.get("user_id", 0) or 0)
            if user_id > 0:
                referenced_user_ids.add(user_id)
    missing_user_ids = sorted(referenced_user_ids - known_user_ids)
    placeholder_users = [
        {
            "id": user_id,
            "email": f"migrated_user_{user_id}@local.invalid",
            "display_name": f"Migrated User {user_id}",
            "auth_mode": "migration_placeholder",
            "access_tier": "local_beta",
            "status": "migration_placeholder",
            "created_at": "",
            "updated_at": "",
        }
        for user_id in missing_user_ids
    ]
    all_users = [*users, *placeholder_users]

    try:
        with psycopg.connect(target_url) as conn:
            with conn.cursor() as cur:
                cur.execute(get_postgres_schema_sql())

                for user in all_users:
                    cur.execute(
                        """
                        INSERT INTO users (id, email, display_name, auth_mode, access_tier, status, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (email) DO UPDATE SET
                            display_name = EXCLUDED.display_name,
                            auth_mode = EXCLUDED.auth_mode,
                            access_tier = EXCLUDED.access_tier,
                            status = EXCLUDED.status,
                            updated_at = EXCLUDED.updated_at
                        """,
                        (
                            int(user.get("id", 0) or 0),
                            str(user.get("email", "") or ""),
                            str(user.get("display_name", "") or ""),
                            str(user.get("auth_mode", "") or "local"),
                            str(user.get("access_tier", "") or "local_beta"),
                            str(user.get("status", "") or "local_active"),
                            _clean_timestamp(user.get("created_at"), fallback_now=True),
                            _clean_timestamp(user.get("updated_at"), fallback_now=True),
                        ),
                    )

                for project in projects:
                    payload_json = project.get("payload_json", {})
                    if isinstance(payload_json, str):
                        payload_text = payload_json
                    else:
                        payload_text = json.dumps(payload_json, ensure_ascii=False)
                    cur.execute(
                        """
                        INSERT INTO projects (
                            id, user_id, name, project_type, kitchen_layout, language, source,
                            is_demo, is_autosave, created_at, updated_at, last_opened_at, payload_json
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                        ON CONFLICT (id) DO UPDATE SET
                            name = EXCLUDED.name,
                            project_type = EXCLUDED.project_type,
                            kitchen_layout = EXCLUDED.kitchen_layout,
                            language = EXCLUDED.language,
                            source = EXCLUDED.source,
                            is_demo = EXCLUDED.is_demo,
                            is_autosave = EXCLUDED.is_autosave,
                            updated_at = EXCLUDED.updated_at,
                            last_opened_at = EXCLUDED.last_opened_at,
                            payload_json = EXCLUDED.payload_json
                        """,
                        (
                            int(project.get("id", 0) or 0),
                            int(project.get("user_id", 0) or 0),
                            str(project.get("name", "") or ""),
                            str(project.get("project_type", "") or "kitchen"),
                            str(project.get("kitchen_layout", "") or "jedan_zid"),
                            str(project.get("language", "") or "sr"),
                            str(project.get("source", "") or "local"),
                            bool(project.get("is_demo", False)),
                            bool(project.get("is_autosave", False)),
                            _clean_timestamp(project.get("created_at"), fallback_now=True),
                            _clean_timestamp(project.get("updated_at"), fallback_now=True),
                            _clean_timestamp(project.get("last_opened_at"), fallback_now=True),
                            payload_text,
                        ),
                    )

                for subscription in subscriptions:
                    cur.execute(
                        """
                        INSERT INTO subscriptions (
                            id, user_id, provider, plan_code, billing_status, customer_id,
                            subscription_id, checkout_url, portal_url, current_period_end,
                            created_at, updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (user_id) DO UPDATE SET
                            provider = EXCLUDED.provider,
                            plan_code = EXCLUDED.plan_code,
                            billing_status = EXCLUDED.billing_status,
                            customer_id = EXCLUDED.customer_id,
                            subscription_id = EXCLUDED.subscription_id,
                            checkout_url = EXCLUDED.checkout_url,
                            portal_url = EXCLUDED.portal_url,
                            current_period_end = EXCLUDED.current_period_end,
                            updated_at = EXCLUDED.updated_at
                        """,
                        (
                            int(subscription.get("id", 0) or 0),
                            int(subscription.get("user_id", 0) or 0),
                            str(subscription.get("provider", "") or "stripe"),
                            str(subscription.get("plan_code", "") or "trial"),
                            str(subscription.get("billing_status", "") or "trial"),
                            str(subscription.get("customer_id", "") or ""),
                            str(subscription.get("subscription_id", "") or ""),
                            str(subscription.get("checkout_url", "") or ""),
                            str(subscription.get("portal_url", "") or ""),
                            str(subscription.get("current_period_end", "") or ""),
                            _clean_timestamp(subscription.get("created_at"), fallback_now=True),
                            _clean_timestamp(subscription.get("updated_at"), fallback_now=True),
                        ),
                        )

                for billing_event in billing_events:
                    cur.execute(
                        """
                        INSERT INTO billing_events (
                            id, provider, provider_event_id, event_type, user_id, email, status,
                            payload_json, billing_status, plan_code, error_message,
                            created_at, updated_at, processed_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (provider_event_id) DO UPDATE SET
                            event_type = EXCLUDED.event_type,
                            user_id = EXCLUDED.user_id,
                            email = EXCLUDED.email,
                            status = EXCLUDED.status,
                            payload_json = EXCLUDED.payload_json,
                            billing_status = EXCLUDED.billing_status,
                            plan_code = EXCLUDED.plan_code,
                            error_message = EXCLUDED.error_message,
                            updated_at = EXCLUDED.updated_at,
                            processed_at = EXCLUDED.processed_at
                        """,
                        (
                            int(billing_event.get("id", 0) or 0),
                            str(billing_event.get("provider", "") or "stripe"),
                            str(billing_event.get("provider_event_id", "") or ""),
                            str(billing_event.get("event_type", "") or ""),
                            int(billing_event.get("user_id", 0) or 0),
                            str(billing_event.get("email", "") or ""),
                            str(billing_event.get("status", "") or "received"),
                            str(billing_event.get("payload_json", "") or ""),
                            str(billing_event.get("billing_status", "") or ""),
                            str(billing_event.get("plan_code", "") or ""),
                            str(billing_event.get("error_message", "") or ""),
                            _clean_timestamp(billing_event.get("created_at"), fallback_now=True),
                            _clean_timestamp(billing_event.get("updated_at"), fallback_now=True),
                            str(billing_event.get("processed_at", "") or ""),
                        ),
                    )

                for auth_session in auth_sessions:
                    cur.execute(
                        """
                        INSERT INTO auth_sessions (
                            id, user_id, session_token, session_kind, auth_provider,
                            status, created_at, updated_at, expires_at, revoked_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (session_token) DO UPDATE SET
                            status = EXCLUDED.status,
                            updated_at = EXCLUDED.updated_at,
                            expires_at = EXCLUDED.expires_at,
                            revoked_at = EXCLUDED.revoked_at
                        """,
                        (
                            int(auth_session.get("id", 0) or 0),
                            int(auth_session.get("user_id", 0) or 0),
                            str(auth_session.get("session_token", "") or ""),
                            str(auth_session.get("session_kind", "") or "browser"),
                            str(auth_session.get("auth_provider", "") or "password"),
                            str(auth_session.get("status", "") or "active"),
                            _clean_timestamp(auth_session.get("created_at"), fallback_now=True),
                            _clean_timestamp(auth_session.get("updated_at"), fallback_now=True),
                            _clean_timestamp(auth_session.get("expires_at"), fallback_now=True),
                            str(auth_session.get("revoked_at", "") or ""),
                        ),
                    )

                for reset_token in password_reset_tokens:
                    cur.execute(
                        """
                        INSERT INTO password_reset_tokens (
                            id, user_id, reset_token, status, created_at, expires_at, used_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (reset_token) DO UPDATE SET
                            status = EXCLUDED.status,
                            expires_at = EXCLUDED.expires_at,
                            used_at = EXCLUDED.used_at
                        """,
                        (
                            int(reset_token.get("id", 0) or 0),
                            int(reset_token.get("user_id", 0) or 0),
                            str(reset_token.get("reset_token", "") or ""),
                            str(reset_token.get("status", "") or "active"),
                            _clean_timestamp(reset_token.get("created_at"), fallback_now=True),
                            _clean_timestamp(reset_token.get("expires_at"), fallback_now=True),
                            str(reset_token.get("used_at", "") or ""),
                        ),
                    )

                for login_attempt in login_attempts:
                    cur.execute(
                        """
                        INSERT INTO login_attempts (
                            id, email, success, attempted_at
                        )
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            email = EXCLUDED.email,
                            success = EXCLUDED.success,
                            attempted_at = EXCLUDED.attempted_at
                        """,
                        (
                            int(login_attempt.get("id", 0) or 0),
                            str(login_attempt.get("email", "") or "").strip().lower(),
                            bool(login_attempt.get("success", False)),
                            _clean_timestamp(login_attempt.get("attempted_at"), fallback_now=True),
                        ),
                    )

                for export_job in export_jobs:
                    cur.execute(
                        """
                        INSERT INTO export_jobs (
                            id, user_id, project_id, job_type, status, request_payload_json,
                            result_ref, error_message, created_at, started_at, finished_at, updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            user_id = EXCLUDED.user_id,
                            project_id = EXCLUDED.project_id,
                            job_type = EXCLUDED.job_type,
                            status = EXCLUDED.status,
                            request_payload_json = EXCLUDED.request_payload_json,
                            result_ref = EXCLUDED.result_ref,
                            error_message = EXCLUDED.error_message,
                            created_at = EXCLUDED.created_at,
                            started_at = EXCLUDED.started_at,
                            finished_at = EXCLUDED.finished_at,
                            updated_at = EXCLUDED.updated_at
                        """,
                        (
                            int(export_job.get("id", 0) or 0),
                            int(export_job.get("user_id", 0) or 0),
                            int(export_job.get("project_id", 0) or 0),
                            str(export_job.get("job_type", "") or "unknown"),
                            str(export_job.get("status", "") or "queued"),
                            str(export_job.get("request_payload_json", "") or ""),
                            str(export_job.get("result_ref", "") or ""),
                            str(export_job.get("error_message", "") or ""),
                            _clean_timestamp(export_job.get("created_at"), fallback_now=True),
                            str(export_job.get("started_at", "") or ""),
                            str(export_job.get("finished_at", "") or ""),
                            _clean_timestamp(export_job.get("updated_at"), fallback_now=True),
                        ),
                    )

                for audit_log in audit_logs:
                    cur.execute(
                        """
                        INSERT INTO audit_logs (
                            id, user_id, event_type, status, detail, created_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            user_id = EXCLUDED.user_id,
                            event_type = EXCLUDED.event_type,
                            status = EXCLUDED.status,
                            detail = EXCLUDED.detail,
                            created_at = EXCLUDED.created_at
                        """,
                        (
                            int(audit_log.get("id", 0) or 0),
                            int(audit_log.get("user_id", 0) or 0),
                            str(audit_log.get("event_type", "") or "unknown"),
                            str(audit_log.get("status", "") or "info"),
                            str(audit_log.get("detail", "") or ""),
                            _clean_timestamp(audit_log.get("created_at"), fallback_now=True),
                        ),
                    )

                cur.execute("SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE((SELECT MAX(id) FROM users), 1), true)")
                cur.execute("SELECT setval(pg_get_serial_sequence('projects', 'id'), COALESCE((SELECT MAX(id) FROM projects), 1), true)")
                cur.execute("SELECT setval(pg_get_serial_sequence('subscriptions', 'id'), COALESCE((SELECT MAX(id) FROM subscriptions), 1), true)")
                cur.execute("SELECT setval(pg_get_serial_sequence('billing_events', 'id'), COALESCE((SELECT MAX(id) FROM billing_events), 1), true)")
                cur.execute("SELECT setval(pg_get_serial_sequence('auth_sessions', 'id'), COALESCE((SELECT MAX(id) FROM auth_sessions), 1), true)")
                cur.execute("SELECT setval(pg_get_serial_sequence('password_reset_tokens', 'id'), COALESCE((SELECT MAX(id) FROM password_reset_tokens), 1), true)")
                cur.execute("SELECT setval(pg_get_serial_sequence('login_attempts', 'id'), COALESCE((SELECT MAX(id) FROM login_attempts), 1), true)")
                cur.execute("SELECT setval(pg_get_serial_sequence('audit_logs', 'id'), COALESCE((SELECT MAX(id) FROM audit_logs), 1), true)")
                cur.execute("SELECT setval(pg_get_serial_sequence('export_jobs', 'id'), COALESCE((SELECT MAX(id) FROM export_jobs), 1), true)")
            conn.commit()
    except Exception as ex:
        return {
            "ok": "false",
            "message": f"Postgres import nije uspeo: {ex}",
            "database_url": target_url,
        }

    return {
        "ok": "true",
        "message": "Snapshot je importovan u Postgres skeleton bazu.",
        "database_url": target_url,
        "users": str(len(all_users)),
        "projects": str(len(projects)),
        "subscriptions": str(len(subscriptions)),
        "billing_events": str(len(billing_events)),
        "auth_sessions": str(len(auth_sessions)),
        "password_reset_tokens": str(len(password_reset_tokens)),
        "login_attempts": str(len(login_attempts)),
        "export_jobs": str(len(export_jobs)),
        "audit_logs": str(len(audit_logs)),
        "placeholder_users": str(len(placeholder_users)),
    }
