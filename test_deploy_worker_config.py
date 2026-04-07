# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def run_deploy_worker_config_check() -> tuple[bool, str]:
    app_config = Path(__file__).with_name("app_config.py").read_text(encoding="utf-8")
    app_py = Path(__file__).with_name("app.py").read_text(encoding="utf-8")
    compose = Path(__file__).with_name("docker-compose.production.yml").read_text(encoding="utf-8")
    production_config = Path(__file__).with_name("PRODUCTION_CONFIG.md").read_text(encoding="utf-8")
    deploy_doc = Path(__file__).with_name("DEPLOY_PRODUCTION.md").read_text(encoding="utf-8")

    required_app_config = [
        "host: str",
        "port: int",
        "web_workers: int",
        "export_worker_mode: str",
        "export_worker_poll_seconds: int",
        'host=_env("HOST", host_default)',
        'port=max(1, _env_int("PORT", port_default))',
        'web_workers=max(0, _env_int("WEB_WORKERS", web_workers_default))',
        'export_worker_mode=_env("EXPORT_WORKER_MODE", "in_process").lower()',
        'export_worker_poll_seconds=max(1, _env_int("EXPORT_WORKER_POLL_SECONDS", 2))',
        '"web_workers": str(cfg.web_workers)',
        '"export_worker_mode": str(cfg.export_worker_mode)',
    ]
    missing_app_config = [item for item in required_app_config if item not in app_config]
    if missing_app_config:
        return False, f"FAIL_deploy_worker_app_config:{', '.join(missing_app_config)}"

    required_app_py = [
        "host=str(cfg.host or '127.0.0.1')",
        "port=int(cfg.port)",
        "workers=int(cfg.web_workers)",
    ]
    missing_app_py = [item for item in required_app_py if item not in app_py]
    if missing_app_py:
        return False, f"FAIL_deploy_worker_app_py:{', '.join(missing_app_py)}"

    required_compose = [
        "HOST: 0.0.0.0",
        "PORT: 8080",
        "WEB_WORKERS: ${WEB_WORKERS:-2}",
        "EXPORT_WORKER_MODE: dedicated_process",
        'command: ["python", "export_worker_cli.py"]',
        "krojna-lista-pro-export-worker:",
    ]
    missing_compose = [item for item in required_compose if item not in compose]
    if missing_compose:
        return False, f"FAIL_deploy_worker_compose:{', '.join(missing_compose)}"

    required_docs = [
        "WEB_WORKERS",
        "EXPORT_WORKER_MODE",
        "HOST=0.0.0.0",
        "PORT=8080",
        "WEB_WORKERS=2",
        "EXPORT_WORKER_MODE=dedicated_process",
        "export_worker_cli.py",
    ]
    missing_docs = [item for item in required_docs if item not in production_config or item not in deploy_doc]
    if missing_docs:
        return False, f"FAIL_deploy_worker_docs:{', '.join(missing_docs)}"

    return True, "OK"
