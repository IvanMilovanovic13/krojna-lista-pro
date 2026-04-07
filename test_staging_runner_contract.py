# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def run_staging_runner_contract_check() -> tuple[bool, str]:
    readiness = Path(__file__).with_name("RUN_READINESS.ps1").read_text(encoding="utf-8")
    staging = Path(__file__).with_name("RUN_STAGING.ps1").read_text(encoding="utf-8")

    required_readiness = [
        '$target = if ($args.Count -gt 0 -and $args[0]) { $args[0] } else { "staging" }',
        '$env:APP_ENV = $target',
        'ops_diagnostics_cli.py --readiness --target $target',
    ]
    missing_readiness = [item for item in required_readiness if item not in readiness]
    if missing_readiness:
        return False, f"FAIL_staging_runner_readiness:{', '.join(missing_readiness)}"

    required_staging = [
        '$env:APP_ENV = "staging"',
        '& $venvPython app.py',
    ]
    missing_staging = [item for item in required_staging if item not in staging]
    if missing_staging:
        return False, f"FAIL_staging_runner_start:{', '.join(missing_staging)}"

    return True, "OK"
