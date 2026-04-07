# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from importlib.util import find_spec
from typing import Any

from app_config import DATA_DIR, DatabaseConfig, get_database_config


@dataclass(frozen=True)
class StoreRuntimeInfo:
    backend: str
    database_url: str
    sqlite_path: str
    ready: bool
    note: str


class StoreBackend:
    name: str = "unknown"

    def runtime_info(self) -> StoreRuntimeInfo:
        raise NotImplementedError

    def connect(self):
        raise NotImplementedError

    def assert_ready(self) -> None:
        raise NotImplementedError


class SQLiteStoreBackend(StoreBackend):
    name = "sqlite"

    def __init__(self, config: DatabaseConfig) -> None:
        self.config = config

    def runtime_info(self) -> StoreRuntimeInfo:
        return StoreRuntimeInfo(
            backend="sqlite",
            database_url=str(self.config.url),
            sqlite_path=str(self.config.sqlite_path or ""),
            ready=True,
            note="SQLite storage is active.",
        )

    def connect(self) -> sqlite3.Connection:
        if self.config.sqlite_path is None:
            raise RuntimeError("SQLite path is missing.")
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.config.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(
            self.config.sqlite_path,
            timeout=30.0,
            check_same_thread=False,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA busy_timeout = 30000")
        return _SQLiteCompatConnection(conn)

    def assert_ready(self) -> None:
        return None


class PostgresStoreBackendPlaceholder(StoreBackend):
    name = "postgres"

    def __init__(self, config: DatabaseConfig) -> None:
        self.config = config

    def runtime_info(self) -> StoreRuntimeInfo:
        has_driver = find_spec("psycopg") is not None
        return StoreRuntimeInfo(
            backend="postgres",
            database_url=str(self.config.url),
            sqlite_path="",
            ready=has_driver,
            note=(
                "Postgres storage is active via psycopg compatibility adapter."
                if has_driver
                else (
                    "Postgres config detected, but psycopg is not available in the current interpreter. "
                    "Use the project venv or run SETUP_VENV.ps1."
                )
            ),
        )

    def connect(self):
        try:
            import psycopg
            from psycopg.rows import dict_row
        except Exception as ex:
            raise RuntimeError(f"psycopg nije dostupan: {ex}") from ex
        raw_conn = psycopg.connect(self.config.url, row_factory=dict_row)
        return _PostgresCompatConnection(raw_conn)

    def assert_ready(self) -> None:
        if find_spec("psycopg") is None:
            raise RuntimeError(
                "Postgres konfiguracija je prepoznata, ali psycopg nije dostupan u trenutnom Python interpreteru. "
                "Pokreni projekat i ops komande kroz project venv (`venv\\Scripts\\python.exe`) ili prvo uradi `SETUP_VENV.ps1`."
            )
        return None


class UnknownStoreBackend(StoreBackend):
    def __init__(self, config: DatabaseConfig) -> None:
        self.config = config

    def runtime_info(self) -> StoreRuntimeInfo:
        return StoreRuntimeInfo(
            backend=str(self.config.backend or "unknown"),
            database_url=str(self.config.url),
            sqlite_path="",
            ready=False,
            note="Unsupported DATABASE_URL backend.",
        )

    def connect(self):
        raise RuntimeError(f"Unsupported DATABASE_URL backend: {self.config.backend or 'unknown'}")

    def assert_ready(self) -> None:
        raise RuntimeError(f"Unsupported DATABASE_URL backend: {self.config.backend or 'unknown'}")


def get_store_backend() -> StoreBackend:
    config = get_database_config()
    if config.backend == "sqlite":
        return SQLiteStoreBackend(config)
    if config.backend == "postgres":
        return PostgresStoreBackendPlaceholder(config)
    return UnknownStoreBackend(config)


def get_store_runtime_info_dict() -> dict[str, str]:
    info = get_store_backend().runtime_info()
    return {
        "backend": str(info.backend),
        "database_url": str(info.database_url),
        "sqlite_path": str(info.sqlite_path),
        "ready": "true" if info.ready else "false",
        "note": str(info.note),
    }


def get_store_backend_name() -> str:
    return str(get_store_backend().name)


class _PostgresCompatCursor:
    def __init__(self, rows: list[dict[str, Any]] | None = None) -> None:
        self._rows = list(rows or [])
        self._index = 0

    def fetchone(self):
        if self._index >= len(self._rows):
            return None
        row = self._rows[self._index]
        self._index += 1
        return row

    def fetchall(self):
        if self._index >= len(self._rows):
            return []
        rows = self._rows[self._index :]
        self._index = len(self._rows)
        return rows


class _PostgresCompatConnection:
    def __init__(self, conn: Any) -> None:
        self._conn = conn

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            return self._conn.__exit__(exc_type, exc, tb)
        finally:
            try:
                self._conn.close()
            except Exception:
                pass

    def execute(self, query: str, params: tuple | list | None = None):
        sql = _translate_qmark_sql(query)
        with self._conn.cursor() as cur:
            cur.execute(sql, params or ())
            rows: list[dict[str, Any]] = []
            if cur.description:
                rows = [dict(row) for row in cur.fetchall()]
            return _PostgresCompatCursor(rows)

    def executescript(self, script: str) -> None:
        parts = [part.strip() for part in str(script or "").split(";") if part.strip()]
        with self._conn.cursor() as cur:
            for part in parts:
                cur.execute(part)

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()


class _SQLiteCompatConnection:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            return self._conn.__exit__(exc_type, exc, tb)
        finally:
            try:
                self._conn.close()
            except Exception:
                pass

    def execute(self, query: str, params: tuple | list | None = None):
        return self._retry_locked(self._conn.execute, query, params or ())

    def executescript(self, script: str):
        return self._retry_locked(self._conn.executescript, script)

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def _retry_locked(self, fn, *args):
        delays = (0.05, 0.1, 0.2, 0.35, 0.5)
        last_error: sqlite3.OperationalError | None = None
        for delay in (*delays, 0.0):
            try:
                return fn(*args)
            except sqlite3.OperationalError as ex:
                message = str(ex).lower()
                if "locked" not in message and "busy" not in message:
                    raise
                last_error = ex
                try:
                    self._conn.rollback()
                except Exception:
                    pass
                if delay <= 0:
                    break
                time.sleep(delay)
        assert last_error is not None
        raise last_error


def _translate_qmark_sql(query: str) -> str:
    text = str(query or "")
    if "?" not in text:
        return text
    return text.replace("?", "%s")
