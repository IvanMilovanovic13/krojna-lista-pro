# -*- coding: utf-8 -*-
from __future__ import annotations

import json

from app_config import get_public_runtime_config


def main() -> int:
    print(json.dumps(get_public_runtime_config(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
