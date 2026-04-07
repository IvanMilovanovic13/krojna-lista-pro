from __future__ import annotations

from typing import Any


_FIXED_SHELF_DEFAULTS = {
    "BASE_OPEN": 1,
    "WALL_OPEN": 1,
    "WALL_GLASS": 1,
    "WALL_UPPER_OPEN": 1,
    "TALL_PANTRY": 3,
    "TALL_OPEN": 2,
}

_NO_SHELF_KEYWORDS = (
    "FRIDGE",
    "DISHWASHER",
    "COOKING_UNIT",
    "OVEN_HOB",
    "OVEN",
    "SINK",
    "HOOD",
    "HOB",
    "TRASH",
    "DRAWER",
    "MICRO",
    "FREESTANDING",
)


def module_supports_adjustable_shelves(
    template_id: str,
    *,
    features: dict[str, Any] | None = None,
) -> bool:
    tid = str(template_id or "").upper().strip()
    feats = features or {}
    if any(key in tid for key in _NO_SHELF_KEYWORDS):
        return False
    if tid in _FIXED_SHELF_DEFAULTS:
        return True
    if any(key in tid for key in ("DOOR", "OPEN", "GLASS", "PANTRY", "CORNER", "LIFTUP", "NARROW")):
        return True
    return bool(
        feats.get("doors", False)
        or feats.get("open", False)
        or feats.get("pantry", False)
        or feats.get("glass", False)
    )


def default_shelf_count(
    template_id: str,
    *,
    zone: str = "",
    h_mm: int | float = 0,
    params: dict[str, Any] | None = None,
    features: dict[str, Any] | None = None,
) -> int:
    p = params or {}
    if "n_shelves" in p:
        try:
            return max(0, int(p.get("n_shelves", 0) or 0))
        except Exception:
            return 0

    tid = str(template_id or "").upper().strip()
    if tid in _FIXED_SHELF_DEFAULTS:
        return _FIXED_SHELF_DEFAULTS[tid]

    if not module_supports_adjustable_shelves(tid, features=features):
        return 0

    zone_norm = str(zone or "").lower().strip()
    try:
        inner_h = max(0.0, float(h_mm or 0) - 36.0)
    except Exception:
        inner_h = 0.0

    if zone_norm == "tall":
        return max(2, min(5, int(round(inner_h / 500.0)) or 2))
    if zone_norm in ("wall", "wall_upper", "tall_top"):
        return max(1, min(3, int(round(inner_h / 650.0)) or 1))
    return 2 if inner_h >= 900 else 1


def dishwasher_installation_metrics(
    kitchen: dict[str, Any] | None,
    module: dict[str, Any] | None,
    *,
    standard_body_height: int = 815,
    front_height: int = 720,
) -> dict[str, Any]:
    """Compute raised built-in dishwasher installation metrics.

    Practical rule:
    - plinth remains continuous and unchanged
    - raised mode starts only when carcass/module height exceeds the standard
      integrated dishwasher front height
    - visible lower filler is the extra module height above the standard front
    - platform/support height follows the same constructive raise by default
    """
    k = kitchen or {}
    m = module or {}
    wt = (k.get("worktop", {}) or {})

    try:
        wt_thk_mm = int(round(float(wt.get("thickness", 3.8)) * 10.0))
    except Exception:
        wt_thk_mm = 38
    foot_h_mm = int(k.get("foot_height_mm", 100) or 100)
    module_h_mm = int(m.get("h_mm", 720) or 720)

    available_under_worktop = max(0, foot_h_mm + module_h_mm)
    extra_height = max(0, module_h_mm - int(front_height))
    raised_mode = extra_height > 0

    lower_filler_height = extra_height if raised_mode else 0
    platform_height = extra_height if raised_mode else 0

    return {
        "dishwasher_standard_body_height": int(standard_body_height),
        "dishwasher_front_height": int(front_height),
        "dishwasher_raised_mode": bool(raised_mode),
        "dishwasher_platform_height": int(platform_height),
        "dishwasher_lower_filler_height": int(lower_filler_height),
        "dishwasher_available_height_under_worktop": int(available_under_worktop),
        "dishwasher_extra_height": int(extra_height),
        "dishwasher_plinth_height": int(foot_h_mm),
        "dishwasher_worktop_thickness": int(wt_thk_mm),
        "dishwasher_total_height": int(available_under_worktop + wt_thk_mm),
    }
