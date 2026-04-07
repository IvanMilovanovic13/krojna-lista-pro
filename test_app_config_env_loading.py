# -*- coding: utf-8 -*-
from __future__ import annotations

import os

import app_config


def run_app_config_env_loading_check() -> tuple[bool, str]:
    base_env = app_config.BASE_DIR / ".env"
    staging_env = app_config.BASE_DIR / ".env.staging"
    staging_local_env = app_config.BASE_DIR / ".env.staging.local"
    original_values = {key: os.environ.get(key) for key in ("APP_ENV", "BASE_URL", "SECRET_KEY", "WEB_WORKERS")}
    original_base = base_env.read_text(encoding="utf-8") if base_env.exists() else None
    original_staging = staging_env.read_text(encoding="utf-8") if staging_env.exists() else None
    original_staging_local = staging_local_env.read_text(encoding="utf-8") if staging_local_env.exists() else None
    try:
        for key in ("APP_ENV", "BASE_URL", "SECRET_KEY", "WEB_WORKERS"):
            os.environ.pop(key, None)

        base_env.write_text(
            "APP_ENV=staging\nBASE_URL=http://base.example\nSECRET_KEY=base-secret\nWEB_WORKERS=1\n",
            encoding="utf-8",
        )
        staging_env.write_text(
            "BASE_URL=https://staging.example\nSECRET_KEY=staging-secret\nWEB_WORKERS=4\n",
            encoding="utf-8",
        )
        staging_local_env.write_text(
            "BASE_URL=https://staging-local.example\nSECRET_KEY=staging-local-secret\nWEB_WORKERS=5\n",
            encoding="utf-8",
        )

        app_config._ENV_LOADED = False
        cfg = app_config.get_app_config()
        if str(cfg.app_env) != "staging":
            return False, f"FAIL_app_env_from_base:{cfg.app_env}"
        if str(cfg.base_url) != "https://staging-local.example":
            return False, f"FAIL_staging_local_base_url_override:{cfg.base_url}"
        if str(cfg.secret_key) != "staging-local-secret":
            return False, f"FAIL_staging_local_secret_override:{cfg.secret_key}"
        if int(cfg.web_workers) != 5:
            return False, f"FAIL_staging_local_workers_override:{cfg.web_workers}"

        os.environ["BASE_URL"] = "https://explicit.example"
        app_config._ENV_LOADED = False
        cfg_explicit = app_config.get_app_config()
        if str(cfg_explicit.base_url) != "https://explicit.example":
            return False, f"FAIL_explicit_env_priority:{cfg_explicit.base_url}"
        return True, "OK"
    finally:
        app_config._ENV_LOADED = False
        for key, value in original_values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        if original_base is None:
            try:
                if base_env.exists():
                    base_env.unlink()
            except Exception:
                pass
        else:
            base_env.write_text(original_base, encoding="utf-8")
        if original_staging is None:
            try:
                if staging_env.exists():
                    staging_env.unlink()
            except Exception:
                pass
        else:
            staging_env.write_text(original_staging, encoding="utf-8")
        if original_staging_local is None:
            try:
                if staging_local_env.exists():
                    staging_local_env.unlink()
            except Exception:
                pass
        else:
            staging_local_env.write_text(original_staging_local, encoding="utf-8")
