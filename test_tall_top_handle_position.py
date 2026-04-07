# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def run_tall_top_handle_position_check() -> tuple[bool, str]:
    visualization = Path(__file__).with_name("visualization.py").read_text(encoding="utf-8")

    required = [
        'zone_key = str((m or {}).get("zone", "")).lower().strip()',
        'if zone_key == "tall_top":',
        'handle_cy = _clamp_handle_cy(y, h, y + h * 0.50)',
        'handle_cy = _clamp_handle_cy(y, h, y + handle_bottom_off + half_len)',
        'def _draw_tall_doors(ax, x, y, w, h, accent, face, technical, m=None):',
        'handle_cy = _clamp_handle_cy(y, h, y + h * 0.50)',
        'top_cy = _clamp_handle_cy(top_y0, top_h, top_y0 + top_h * 0.50)',
        'bot_cy = _clamp_handle_cy(bot_y0, bot_h, bot_y0 + bot_h * 0.50)',
    ]
    missing = [item for item in required if item not in visualization]
    if missing:
        return False, f"FAIL_tall_top_handle_position:{', '.join(missing)}"
    return True, "OK"
