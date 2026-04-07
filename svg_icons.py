# -*- coding: utf-8 -*-
from __future__ import annotations
import base64
from functools import lru_cache
from pathlib import Path
import re

# Ikonice kataloga — raw SVG inner content iz HTML preview fajla.
# Svaki SVG se vraća u prirodnim dimenzijama (direktno iz HTML previewa).

_HERE = Path(__file__).resolve().parent
_ICONS_PREVIEW_NEW = _HERE / "icons_preview_new.html"
_PHOTO_ICON_MAP = {}


@lru_cache(maxsize=64)
def _photo_data_uri(path_str: str) -> str:
    p = Path(path_str)
    raw = p.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _asset_src(path_obj: Path) -> str:
    try:
        rel = path_obj.resolve().relative_to((_HERE / "assets").resolve())
        return "/assets/" + str(rel).replace("\\", "/")
    except Exception:
        return _photo_data_uri(str(path_obj))


@lru_cache(maxsize=1)
def _load_preview_svg_map() -> dict[str, str]:
    if not _ICONS_PREVIEW_NEW.exists():
        return {}

    html = _ICONS_PREVIEW_NEW.read_text(encoding="utf-8", errors="ignore")
    card_pattern = re.compile(
        r'<div class="card"[^>]*>\s*(<svg\b.*?</svg>)\s*'
        r'<div class="card-label">.*?</div>\s*'
        r'<div class="card-id">([^<]+)</div>',
        re.DOTALL | re.IGNORECASE,
    )
    svg_map: dict[str, str] = {}
    for svg_html, card_id in card_pattern.findall(html):
        tid = card_id.strip().upper()
        if tid:
            svg_map[tid] = svg_html.strip()
    return svg_map


def _fit_svg_markup(svg_html: str) -> str:
    return re.sub(
        r"<svg\b",
        '<svg style="display:block;max-width:100%;max-height:100%;width:auto;height:auto;"',
        svg_html,
        count=1,
        flags=re.IGNORECASE,
    )


def svg_for_tid(tid: str) -> str:  # noqa: C901
    t = tid.upper()

    if t == "BASE_OVEN_HOB_FREESTANDING":
        vb = "0 0 54 78"
        body = (
            '<rect x="7" y="2" width="40" height="8" fill="#E8E8E6" stroke="#2C2C2C" stroke-width="1.2"/>'
            '<ellipse cx="17" cy="6" rx="7" ry="2.2" fill="none" stroke="#666" stroke-width="0.8"/>'
            '<ellipse cx="17" cy="6" rx="5" ry="1.4" fill="none" stroke="#888" stroke-width="0.6"/>'
            '<ellipse cx="37" cy="6" rx="7" ry="2.2" fill="none" stroke="#666" stroke-width="0.8"/>'
            '<ellipse cx="37" cy="6" rx="5" ry="1.4" fill="none" stroke="#888" stroke-width="0.6"/>'
            '<ellipse cx="17" cy="10" rx="7" ry="2.2" fill="none" stroke="#666" stroke-width="0.8"/>'
            '<ellipse cx="17" cy="10" rx="5" ry="1.4" fill="none" stroke="#888" stroke-width="0.6"/>'
            '<ellipse cx="37" cy="10" rx="7" ry="2.2" fill="none" stroke="#666" stroke-width="0.8"/>'
            '<ellipse cx="37" cy="10" rx="5" ry="1.4" fill="none" stroke="#888" stroke-width="0.6"/>'
            '<rect x="6" y="10" width="42" height="11" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.2"/>'
            '<circle cx="13" cy="16" r="2.1" fill="none" stroke="#666" stroke-width="0.8"/>'
            '<line x1="13" y1="14" x2="13" y2="18" stroke="#666" stroke-width="0.7"/>'
            '<circle cx="20" cy="16" r="2.1" fill="none" stroke="#666" stroke-width="0.8"/>'
            '<line x1="20" y1="14" x2="20" y2="18" stroke="#666" stroke-width="0.7"/>'
            '<circle cx="27" cy="16" r="2.1" fill="none" stroke="#666" stroke-width="0.8"/>'
            '<line x1="27" y1="14" x2="27" y2="18" stroke="#666" stroke-width="0.7"/>'
            '<rect x="31" y="14" width="9" height="4" rx="0.5" fill="#EDEDEB" stroke="#666" stroke-width="0.7"/>'
            '<line x1="39" y1="15" x2="39" y2="17" stroke="#888" stroke-width="0.5"/>'
            '<circle cx="43" cy="16" r="2.1" fill="none" stroke="#666" stroke-width="0.8"/>'
            '<line x1="43" y1="14" x2="43" y2="18" stroke="#666" stroke-width="0.7"/>'
            '<rect x="6" y="21" width="42" height="36" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.2"/>'
            '<line x1="13" y1="27" x2="41" y2="27" stroke="#444" stroke-width="2"/>'
            '<rect x="12" y="31" width="30" height="18" fill="#9C9C9C" stroke="#444" stroke-width="1"/>'
            '<rect x="13.5" y="32.5" width="27" height="15" fill="#8A8A8A" stroke="#666" stroke-width="0.5"/>'
            '<line x1="18" y1="33" x2="25" y2="46" stroke="#CFCFCF" stroke-width="1" opacity="0.45"/>'
            '<line x1="24" y1="33" x2="31" y2="46" stroke="#DADADA" stroke-width="1" opacity="0.4"/>'
            '<line x1="30" y1="33" x2="37" y2="46" stroke="#E3E3E3" stroke-width="1" opacity="0.35"/>'
            '<rect x="6" y="57" width="42" height="12" fill="#F3F3F1" stroke="#2C2C2C" stroke-width="1.2"/>'
            '<rect x="7" y="69" width="40" height="5" fill="#8C8C8C" stroke="#2C2C2C" stroke-width="1"/>'
            '<rect x="8" y="72" width="4" height="2" rx="0.5" fill="#666"/>'
            '<rect x="42" y="72" width="4" height="2" rx="0.5" fill="#666"/>'
        )
        return (f'<svg viewBox="{vb}" '
                f'style="display:block;max-width:100%;max-height:100%;width:auto;height:auto;" fill="none" xmlns="http://www.w3.org/2000/svg">'
                f'{body}</svg>')

    if t == "BASE_DISHWASHER_FREESTANDING":
        vb = "0 0 44 78"
        body = (
            '<rect x="5" y="2" width="34" height="68" rx="0.8" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.2"/>'
            '<line x1="5" y1="10" x2="39" y2="10" stroke="#2C2C2C" stroke-width="1"/>'
            '<line x1="5" y1="15" x2="39" y2="15" stroke="#B8B8B8" stroke-width="0.8"/>'
            '<line x1="15" y1="12" x2="23" y2="12" stroke="#444" stroke-width="1.7"/>'
            '<line x1="15" y1="13.5" x2="23" y2="13.5" stroke="#666" stroke-width="0.6"/>'
            '<line x1="14" y1="12" x2="15" y2="14.2" stroke="#444" stroke-width="0.8"/>'
            '<line x1="23" y1="12" x2="24" y2="14.2" stroke="#444" stroke-width="0.8"/>'
            '<rect x="28" y="11" width="6" height="2.6" rx="0.4" fill="#F6F6F4" stroke="#666" stroke-width="0.7"/>'
            '<circle cx="36.2" cy="12.3" r="1" fill="none" stroke="#666" stroke-width="0.7"/>'
            '<circle cx="39.2" cy="12.3" r="1" fill="none" stroke="#666" stroke-width="0.7"/>'
            '<line x1="5" y1="70" x2="39" y2="70" stroke="#2C2C2C" stroke-width="1"/>'
            '<rect x="6" y="70" width="32" height="4" fill="#F3F3F1" stroke="#2C2C2C" stroke-width="1"/>'
            '<rect x="7" y="73.5" width="4" height="2" rx="0.5" fill="#666"/>'
            '<rect x="33" y="73.5" width="4" height="2" rx="0.5" fill="#666"/>'
        )
        return (f'<svg viewBox="{vb}" '
                f'style="display:block;max-width:100%;max-height:100%;width:auto;height:auto;" fill="none" xmlns="http://www.w3.org/2000/svg">'
                f'{body}</svg>')

    # 1. Photo icon override (za template-e sa image asset-ima).
    _img_p = _PHOTO_ICON_MAP.get(t)
    if _img_p and _img_p.exists():
        try:
            # BASE_COOKING_UNIT forsiramo kao inline image da ne zavisi od browser/app
            # cache-a ili statičkog route-a. Fajl je već mali i optimizovan za katalog.
            _src = _photo_data_uri(str(_img_p))
            return (
                f'<img src="{_src}" width="80" height="65" '
                'style="display:block; object-fit:contain; border:1px solid #c8c8c8; '
                'border-radius:2px; background:#f5f5f5;" />'
            )
        except Exception:
            pass

    _preview_svg = _load_preview_svg_map().get(t)
    if _preview_svg:
        return _fit_svg_markup(_preview_svg)

    # 2. Mapiranje template ID → SVG body (raw inner SVG content iz HTML preview).

    if "TALL_OVEN_MICRO" in t:
        vb = "0 0 40 90"
        body = (
            '<rect x="2" y="2" width="36" height="86" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="5" y="5" width="30" height="30" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="8" y="9" width="18" height="20" rx="1" fill="#3A3A38" stroke="#555" stroke-width="0.8"/>'
            '<line x1="28" y1="11" x2="32" y2="11" stroke="#888" stroke-width="0.8"/>'
            '<line x1="28" y1="14" x2="32" y2="14" stroke="#888" stroke-width="0.8"/>'
            '<line x1="28" y1="17" x2="32" y2="17" stroke="#888" stroke-width="0.8"/>'
            '<circle cx="30" cy="22" r="3" fill="none" stroke="#888" stroke-width="0.8"/>'
            '<line x1="5" y1="37" x2="35" y2="37" stroke="#2C2C2C" stroke-width="1"/>'
            '<rect x="5" y="39" width="30" height="46" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="8" y="44" width="24" height="26" rx="1" fill="#3A3A38" stroke="#555" stroke-width="1"/>'
            '<rect x="10" y="46" width="20" height="22" rx="1" fill="#2A2A28" stroke="#666" stroke-width="0.5"/>'
            '<line x1="9" y1="75" x2="31" y2="75" stroke="#888" stroke-width="1"/>'
            '<line x1="9" y1="78" x2="31" y2="78" stroke="#888" stroke-width="1"/>'
            '<rect x="10" y="42" width="20" height="1.5" rx="0.75" fill="#1A1A1A"/>'
            '<circle cx="14" cy="83" r="2" fill="none" stroke="#888" stroke-width="1"/>'
            '<circle cx="20" cy="83" r="2" fill="none" stroke="#888" stroke-width="1"/>'
            '<circle cx="26" cy="83" r="2" fill="none" stroke="#888" stroke-width="1"/>'
        )

    elif "TALL_OVEN" in t:
        vb = "0 0 40 90"
        body = (
            '<rect x="2" y="2" width="36" height="86" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="5" y="5" width="30" height="26" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="8" y="10" width="22" height="12" rx="1" fill="#3A3A38" stroke="#555" stroke-width="0.8"/>'
            '<line x1="5" y1="33" x2="35" y2="33" stroke="#2C2C2C" stroke-width="1"/>'
            '<rect x="5" y="35" width="30" height="50" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="8" y="40" width="24" height="28" rx="1" fill="#3A3A38" stroke="#555" stroke-width="1"/>'
            '<rect x="10" y="42" width="20" height="24" rx="1" fill="#2A2A28" stroke="#666" stroke-width="0.5"/>'
            '<line x1="9" y1="72" x2="31" y2="72" stroke="#888" stroke-width="1"/>'
            '<line x1="9" y1="75" x2="31" y2="75" stroke="#888" stroke-width="1"/>'
            '<rect x="10" y="38" width="20" height="1.5" rx="0.75" fill="#1A1A1A"/>'
            '<circle cx="13" cy="79" r="2" fill="none" stroke="#888" stroke-width="1"/>'
            '<circle cx="20" cy="79" r="2" fill="none" stroke="#888" stroke-width="1"/>'
            '<circle cx="27" cy="79" r="2" fill="none" stroke="#888" stroke-width="1"/>'
        )

    elif "TALL_FRIDGE_FREEZER" in t:
        vb = "0 0 40 90"
        body = (
            '<rect x="2" y="2" width="36" height="86" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="5" y="5" width="30" height="52" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<line x1="20" y1="18" x2="20" y2="38" stroke="#5588AA" stroke-width="1.2"/>'
            '<line x1="11" y1="28" x2="29" y2="28" stroke="#5588AA" stroke-width="1.2"/>'
            '<line x1="14" y1="21" x2="26" y2="35" stroke="#5588AA" stroke-width="1"/>'
            '<line x1="26" y1="21" x2="14" y2="35" stroke="#5588AA" stroke-width="1"/>'
            '<rect x="28" y="17" width="2" height="22" rx="1" fill="#1A1A1A"/>'
            '<rect x="5" y="59" width="30" height="26" rx="1" fill="#E8EEF2" stroke="#444" stroke-width="1"/>'
            '<line x1="20" y1="66" x2="20" y2="76" stroke="#5588AA" stroke-width="1"/>'
            '<line x1="15" y1="71" x2="25" y2="71" stroke="#5588AA" stroke-width="1"/>'
            '<rect x="28" y="67" width="2" height="12" rx="1" fill="#1A1A1A"/>'
        )

    elif "TALL_FRIDGE_FREESTANDING" in t:
        vb = "0 0 44 90"
        body = (
            '<rect x="1" y="4" width="3" height="84" rx="1" fill="#E0DDD8" stroke="#AAA" stroke-width="0.8"/>'
            '<rect x="40" y="4" width="3" height="84" rx="1" fill="#E0DDD8" stroke="#AAA" stroke-width="0.8"/>'
            '<rect x="4" y="2" width="36" height="86" rx="3" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="7" y="5" width="30" height="62" rx="2" fill="#F0F0EE" stroke="#444" stroke-width="1"/>'
            '<line x1="22" y1="18" x2="22" y2="46" stroke="#5588AA" stroke-width="1.3"/>'
            '<line x1="9" y1="32" x2="35" y2="32" stroke="#5588AA" stroke-width="1.3"/>'
            '<line x1="13" y1="21" x2="31" y2="43" stroke="#5588AA" stroke-width="1"/>'
            '<line x1="31" y1="21" x2="13" y2="43" stroke="#5588AA" stroke-width="1"/>'
            '<rect x="7" y="69" width="30" height="15" rx="2" fill="#E0EBF2" stroke="#444" stroke-width="1"/>'
            '<rect x="30" y="22" width="2" height="28" rx="1" fill="#1A1A1A"/>'
        )

    elif "TALL_FRIDGE" in t:
        vb = "0 0 40 90"
        body = (
            '<rect x="2" y="2" width="36" height="86" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="5" y="5" width="30" height="68" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<line x1="20" y1="28" x2="20" y2="50" stroke="#5588AA" stroke-width="1.5"/>'
            '<line x1="11" y1="39" x2="29" y2="39" stroke="#5588AA" stroke-width="1.5"/>'
            '<line x1="13" y1="31" x2="27" y2="47" stroke="#5588AA" stroke-width="1.2"/>'
            '<line x1="27" y1="31" x2="13" y2="47" stroke="#5588AA" stroke-width="1.2"/>'
            '<circle cx="20" cy="39" r="3" fill="none" stroke="#5588AA" stroke-width="1"/>'
            '<rect x="5" y="75" width="30" height="10" rx="1" fill="#E8EEF2" stroke="#444" stroke-width="1"/>'
            '<rect x="28" y="24" width="2" height="30" rx="1" fill="#1A1A1A"/>'
        )

    elif "TALL_PANTRY" in t:
        vb = "0 0 40 90"
        body = (
            '<rect x="2" y="2" width="36" height="86" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="5" y="5" width="30" height="80" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="28" y="28" width="2" height="34" rx="1" fill="#1A1A1A"/>'
        )

    elif "TALL_GLASS" in t:
        vb = "0 0 40 90"
        body = (
            '<rect x="2" y="2" width="36" height="86" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="5" y="5" width="30" height="54" rx="1" fill="#C8DCE8" fill-opacity="0.5" stroke="#444" stroke-width="1"/>'
            '<line x1="5" y1="5" x2="35" y2="59" stroke="#5588AA" stroke-width="0.8" opacity="0.4"/>'
            '<line x1="35" y1="5" x2="5" y2="59" stroke="#5588AA" stroke-width="0.8" opacity="0.4"/>'
            '<line x1="7" y1="24" x2="33" y2="24" stroke="#5588AA" stroke-width="0.7" opacity="0.5"/>'
            '<line x1="7" y1="42" x2="33" y2="42" stroke="#5588AA" stroke-width="0.7" opacity="0.5"/>'
            '<rect x="5" y="61" width="30" height="24" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="10" y="71" width="20" height="2" rx="1" fill="#1A1A1A"/>'
        )

    elif "TALL_TOP_OPEN" in t:
        vb = "0 0 80 40"
        body = (
            '<rect x="2" y="2" width="76" height="36" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<line x1="5" y1="20" x2="75" y2="20" stroke="#444" stroke-width="1"/>'
        )

    elif "TALL_TOP" in t:
        vb = "0 0 80 40"
        body = (
            '<rect x="2" y="2" width="76" height="36" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="5" y="5" width="34" height="30" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="41" y="5" width="34" height="30" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="33" y="13" width="2" height="14" rx="1" fill="#1A1A1A"/>'
            '<rect x="45" y="13" width="2" height="14" rx="1" fill="#1A1A1A"/>'
        )

    elif "TALL_OPEN" in t:
        vb = "0 0 40 90"
        body = (
            '<rect x="2" y="2" width="36" height="86" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<line x1="5" y1="22" x2="35" y2="22" stroke="#444" stroke-width="1"/>'
            '<line x1="5" y1="40" x2="35" y2="40" stroke="#444" stroke-width="1"/>'
            '<line x1="5" y1="58" x2="35" y2="58" stroke="#444" stroke-width="1"/>'
            '<line x1="5" y1="74" x2="35" y2="74" stroke="#444" stroke-width="1"/>'
        )

    elif "TALL" in t:
        # TALL_DOORS (2DOOR) ili TALL_1DOOR
        if "2DOOR" in t or "DOORS" in t:
            vb = "0 0 60 90"
            body = (
                '<rect x="2" y="2" width="56" height="86" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
                '<rect x="5" y="5" width="24" height="80" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
                '<rect x="31" y="5" width="24" height="80" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
                '<rect x="26" y="35" width="2" height="20" rx="1" fill="#1A1A1A"/>'
                '<rect x="32" y="35" width="2" height="20" rx="1" fill="#1A1A1A"/>'
            )
        else:
            # TALL_PANTRY (1 door) — default tall 1 door
            vb = "0 0 40 90"
            body = (
                '<rect x="2" y="2" width="36" height="86" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
                '<rect x="5" y="5" width="30" height="80" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
                '<rect x="28" y="28" width="2" height="34" rx="1" fill="#1A1A1A"/>'
            )

    elif "WALL_UPPER" in t:
        if "2DOOR" in t:
            vb = "0 0 80 40"
            body = (
                '<rect x="2" y="2" width="76" height="36" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
                '<rect x="5" y="5" width="34" height="30" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
                '<rect x="41" y="5" width="34" height="30" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
                '<rect x="33" y="13" width="2" height="14" rx="1" fill="#1A1A1A"/>'
                '<rect x="45" y="13" width="2" height="14" rx="1" fill="#1A1A1A"/>'
            )
        elif "OPEN" in t:
            vb = "0 0 80 40"
            body = (
                '<rect x="2" y="2" width="76" height="36" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
                '<line x1="5" y1="20" x2="75" y2="20" stroke="#444" stroke-width="1"/>'
            )
        else:
            # WALL_UPPER_1DOOR
            vb = "0 0 80 40"
            body = (
                '<rect x="2" y="2" width="76" height="36" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
                '<rect x="6" y="5" width="68" height="30" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
                '<rect x="62" y="13" width="2" height="14" rx="1" fill="#1A1A1A"/>'
            )

    elif "WALL_NARROW" in t:
        vb = "0 0 45 55"
        body = (
            '<rect x="2" y="2" width="41" height="51" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="6" y="6" width="33" height="43" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="32" y="19" width="2" height="16" rx="1" fill="#1A1A1A"/>'
        )

    elif "WALL_GLASS" in t:
        vb = "0 0 80 55"
        body = (
            '<rect x="2" y="2" width="76" height="51" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="6" y="6" width="68" height="43" rx="1" fill="#C8DCE8" fill-opacity="0.5" stroke="#444" stroke-width="1"/>'
            '<line x1="6" y1="6" x2="74" y2="49" stroke="#5588AA" stroke-width="0.8" opacity="0.5"/>'
            '<line x1="74" y1="6" x2="6" y2="49" stroke="#5588AA" stroke-width="0.8" opacity="0.5"/>'
            '<line x1="8" y1="20" x2="72" y2="20" stroke="#5588AA" stroke-width="0.7" opacity="0.6"/>'
            '<line x1="8" y1="35" x2="72" y2="35" stroke="#5588AA" stroke-width="0.7" opacity="0.6"/>'
            '<rect x="62" y="19" width="2" height="16" rx="1" fill="#1A1A1A"/>'
        )

    elif "WALL_LIFTUP" in t:
        vb = "0 0 80 55"
        body = (
            '<rect x="2" y="2" width="76" height="51" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="6" y="6" width="68" height="43" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<line x1="40" y1="35" x2="40" y2="13" stroke="#444" stroke-width="1.5"/>'
            '<line x1="40" y1="13" x2="34" y2="20" stroke="#444" stroke-width="1.5"/>'
            '<line x1="40" y1="13" x2="46" y2="20" stroke="#444" stroke-width="1.5"/>'
            '<circle cx="10" cy="8" r="2.5" fill="none" stroke="#1A1A1A" stroke-width="1.2"/>'
            '<circle cx="70" cy="8" r="2.5" fill="none" stroke="#1A1A1A" stroke-width="1.2"/>'
            '<rect x="22" y="43" width="36" height="2" rx="1" fill="#1A1A1A"/>'
        )

    elif "WALL_OPEN" in t:
        vb = "0 0 80 55"
        body = (
            '<rect x="2" y="2" width="76" height="51" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<line x1="5" y1="22" x2="75" y2="22" stroke="#444" stroke-width="1"/>'
            '<line x1="5" y1="40" x2="75" y2="40" stroke="#444" stroke-width="1"/>'
        )

    elif "WALL_MICRO" in t or ("MICRO" in t and "WALL" in t):
        vb = "0 0 80 55"
        body = (
            '<rect x="2" y="2" width="76" height="51" fill="#3A3A38" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="6" y="7" width="48" height="38" rx="2" fill="#2A2A28" stroke="#888" stroke-width="1"/>'
            '<rect x="8" y="9" width="44" height="34" rx="1" fill="#1E1E1C" stroke="#666" stroke-width="0.5"/>'
            '<rect x="58" y="7" width="16" height="38" rx="1" fill="#2C2C2A" stroke="#666" stroke-width="0.8"/>'
            '<circle cx="66" cy="18" r="4" fill="none" stroke="#AAA" stroke-width="1"/>'
            '<line x1="60" y1="28" x2="72" y2="28" stroke="#888" stroke-width="0.8"/>'
            '<line x1="60" y1="32" x2="72" y2="32" stroke="#888" stroke-width="0.8"/>'
            '<line x1="60" y1="36" x2="72" y2="36" stroke="#888" stroke-width="0.8"/>'
            '<rect x="60" y="40" width="12" height="3" rx="1" fill="#5588AA" opacity="0.8"/>'
            '<rect x="6" y="49" width="48" height="2" rx="1" fill="#888"/>'
        )

    elif "HOOD" in t:
        vb = "0 0 80 55"
        body = (
            '<path d="M 8 52 L 72 52 L 62 12 L 18 12 Z" fill="#D8D4CF" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="26" y="2" width="28" height="12" fill="#C8C4BF" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="14" y="26" width="52" height="5" rx="1" fill="#B8B4AF" stroke="#888" stroke-width="0.8"/>'
            '<rect x="14" y="34" width="52" height="5" rx="1" fill="#B8B4AF" stroke="#888" stroke-width="0.8"/>'
            '<circle cx="40" cy="44" r="5" fill="#C0BCB7" stroke="#888" stroke-width="1"/>'
            '<circle cx="40" cy="44" r="2" fill="#A8A4A0" stroke="#888" stroke-width="0.6"/>'
            '<line x1="20" y1="14" x2="60" y2="14" stroke="#888" stroke-width="0.8"/>'
        )

    elif "MICRO" in t:
        # MICRO bez WALL prefiksa — takodje mikrotalasna ikona
        vb = "0 0 80 55"
        body = (
            '<rect x="2" y="2" width="76" height="51" fill="#3A3A38" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="6" y="7" width="48" height="38" rx="2" fill="#2A2A28" stroke="#888" stroke-width="1"/>'
            '<rect x="8" y="9" width="44" height="34" rx="1" fill="#1E1E1C" stroke="#666" stroke-width="0.5"/>'
            '<rect x="58" y="7" width="16" height="38" rx="1" fill="#2C2C2A" stroke="#666" stroke-width="0.8"/>'
            '<circle cx="66" cy="18" r="4" fill="none" stroke="#AAA" stroke-width="1"/>'
            '<line x1="60" y1="28" x2="72" y2="28" stroke="#888" stroke-width="0.8"/>'
            '<line x1="60" y1="32" x2="72" y2="32" stroke="#888" stroke-width="0.8"/>'
            '<line x1="60" y1="36" x2="72" y2="36" stroke="#888" stroke-width="0.8"/>'
            '<rect x="60" y="40" width="12" height="3" rx="1" fill="#5588AA" opacity="0.8"/>'
            '<rect x="6" y="49" width="48" height="2" rx="1" fill="#888"/>'
        )

    elif "WALL" in t:
        if "2DOOR" in t:
            vb = "0 0 80 55"
            body = (
                '<rect x="2" y="2" width="76" height="51" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
                '<rect x="5" y="6" width="34" height="43" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
                '<rect x="41" y="6" width="34" height="43" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
                '<rect x="33" y="19" width="2" height="16" rx="1" fill="#1A1A1A"/>'
                '<rect x="45" y="19" width="2" height="16" rx="1" fill="#1A1A1A"/>'
            )
        else:
            # WALL_1DOOR default
            vb = "0 0 80 55"
            body = (
                '<rect x="2" y="2" width="76" height="51" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
                '<rect x="6" y="6" width="68" height="43" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
                '<rect x="62" y="19" width="2" height="16" rx="1" fill="#1A1A1A"/>'
            )

    elif "COOKING_UNIT" in t:
        vb = "0 0 80 80"
        body = (
            '<rect x="5" y="73" width="70" height="5" fill="#C8C4BE" stroke="#2C2C2C" stroke-width="0.8"/>'
            '<rect x="5" y="17" width="70" height="56" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="2" y="2" width="76" height="15" rx="1" fill="#D8D4CC" stroke="#2C2C2C" stroke-width="1.2"/>'
            '<rect x="8" y="5" width="64" height="9" rx="1.5" fill="#1E1E1C" stroke="#2C2C2C" stroke-width="1"/>'
            '<circle cx="20" cy="9.5" r="2.8" fill="none" stroke="#6E6E6A" stroke-width="1"/>'
            '<circle cx="32" cy="9.5" r="2.8" fill="none" stroke="#6E6E6A" stroke-width="1"/>'
            '<circle cx="48" cy="9.5" r="2.8" fill="none" stroke="#6E6E6A" stroke-width="1"/>'
            '<circle cx="60" cy="9.5" r="2.8" fill="none" stroke="#6E6E6A" stroke-width="1"/>'
            '<rect x="5" y="17" width="70" height="11" fill="#8A8880" stroke="#2C2C2C" stroke-width="1"/>'
            '<circle cx="16" cy="22.5" r="3.2" fill="#6A6860" stroke="#444" stroke-width="0.8"/>'
            '<rect x="28" y="19.5" width="24" height="6" rx="1" fill="#111" stroke="#444" stroke-width="0.6"/>'
            '<text x="40" y="24.3" font-size="4.2" fill="#FF3030" text-anchor="middle" font-family="monospace" font-weight="bold">12:10</text>'
            '<circle cx="64" cy="22.5" r="3.2" fill="#6A6860" stroke="#444" stroke-width="0.8"/>'
            '<rect x="5" y="28" width="70" height="36" rx="1" fill="#F0F0EE" stroke="#444" stroke-width="1"/>'
            '<rect x="11" y="31" width="58" height="2.5" rx="1.2" fill="#C8C8C6" stroke="#888" stroke-width="0.6"/>'
            '<rect x="9" y="36" width="62" height="24" rx="1" fill="#2A2A28" stroke="#555" stroke-width="1"/>'
            '<rect x="12" y="39" width="56" height="18" rx="1" fill="#161614" stroke="#444" stroke-width="0.5"/>'
            '<rect x="5" y="64" width="70" height="9" rx="1" fill="#EEECE8" stroke="#555" stroke-width="1"/>'
            '<rect x="20" y="67.5" width="40" height="2.5" rx="1.2" fill="#C8C8C6" stroke="#888" stroke-width="0.7"/>'
            '<line x1="5" y1="64" x2="75" y2="64" stroke="#CFCBC5" stroke-width="0.8"/>'
        )

    elif "DISHWASHER_FREESTANDING" in t:
        vb = "0 0 80 65"
        body = (
            '<rect x="1" y="3" width="3" height="61" rx="1" fill="#E0DDD8" stroke="#AAA" stroke-width="0.7"/>'
            '<rect x="76" y="3" width="3" height="61" rx="1" fill="#E0DDD8" stroke="#AAA" stroke-width="0.7"/>'
            '<rect x="8" y="59" width="8" height="4" fill="#C0BCB8" stroke="#888" stroke-width="0.8"/>'
            '<rect x="64" y="59" width="8" height="4" fill="#C0BCB8" stroke="#888" stroke-width="0.8"/>'
            '<rect x="4" y="2" width="72" height="57" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="4" y="2" width="72" height="9" fill="#3A3A38" stroke="#2C2C2C" stroke-width="1"/>'
            '<circle cx="30" cy="6.5" r="2" fill="none" stroke="#AAA" stroke-width="0.8"/>'
            '<circle cx="40" cy="6.5" r="2" fill="none" stroke="#AAA" stroke-width="0.8"/>'
            '<circle cx="50" cy="6.5" r="2" fill="none" stroke="#AAA" stroke-width="0.8"/>'
            '<circle cx="40" cy="35" r="20" fill="none" stroke="#444" stroke-width="1.2"/>'
            '<circle cx="40" cy="35" r="15" fill="#E8ECF0" stroke="#5588AA" stroke-width="1"/>'
            '<circle cx="40" cy="35" r="8" fill="#C8D8E4" stroke="#5588AA" stroke-width="0.8"/>'
            '<rect x="26" y="12" width="28" height="2" rx="1" fill="#1A1A1A"/>'
        )

    elif "FREESTANDING" in t:
        vb = "0 0 80 65"
        body = (
            '<rect x="1" y="2" width="4" height="62" fill="#D8D4CF" stroke="#AAA" stroke-width="0.7"/>'
            '<rect x="75" y="2" width="4" height="62" fill="#D8D4CF" stroke="#AAA" stroke-width="0.7"/>'
            '<rect x="5" y="59" width="70" height="4" fill="#C0BCB8" stroke="#888" stroke-width="0.8"/>'
            '<rect x="5" y="2" width="70" height="5" fill="#1A1A1A" stroke="#2C2C2C" stroke-width="1"/>'
            '<rect x="5" y="7" width="70" height="10" fill="#2C2C2A" stroke="#2C2C2C" stroke-width="1"/>'
            '<circle cx="18" cy="12" r="3.5" fill="#3A3A38" stroke="#888" stroke-width="1"/>'
            '<circle cx="18" cy="12" r="1.5" fill="#555"/>'
            '<circle cx="31" cy="12" r="3.5" fill="#3A3A38" stroke="#888" stroke-width="1"/>'
            '<circle cx="31" cy="12" r="1.5" fill="#555"/>'
            '<circle cx="49" cy="12" r="3.5" fill="#3A3A38" stroke="#888" stroke-width="1"/>'
            '<circle cx="49" cy="12" r="1.5" fill="#555"/>'
            '<circle cx="62" cy="12" r="3.5" fill="#3A3A38" stroke="#888" stroke-width="1"/>'
            '<circle cx="62" cy="12" r="1.5" fill="#555"/>'
            '<rect x="5" y="18" width="70" height="38" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.2"/>'
            '<rect x="12" y="19" width="56" height="3" rx="1.5" fill="#C0C0BE" stroke="#888" stroke-width="0.8"/>'
            '<rect x="12" y="25" width="56" height="27" rx="1" fill="#2A2A28" stroke="#555" stroke-width="1"/>'
            '<rect x="14" y="27" width="52" height="23" rx="1" fill="#1A1A18" stroke="#444" stroke-width="0.5"/>'
        )

    elif "DISHWASHER" in t:
        vb = "0 0 80 65"
        body = (
            '<rect x="2" y="57" width="76" height="6" fill="#D8D4CF"/>'
            '<rect x="2" y="2" width="76" height="55" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="2" y="2" width="76" height="7" fill="#2C2C2C" stroke="#2C2C2C" stroke-width="1"/>'
            '<rect x="15" y="10" width="50" height="3" rx="1.5" fill="#1A1A1A"/>'
            '<rect x="5" y="14" width="70" height="39" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<line x1="2" y1="57" x2="78" y2="57" stroke="#2C2C2C" stroke-width="1"/>'
        )

    elif "SINK" in t:
        vb = "0 0 80 65"
        body = (
            '<rect x="2" y="57" width="76" height="6" fill="#D8D4CF"/>'
            '<rect x="2" y="2" width="76" height="55" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="2" y="2" width="76" height="9" fill="#D8D4CC" stroke="#2C2C2C" stroke-width="1"/>'
            '<rect x="14" y="3.5" width="40" height="6" rx="1" fill="#8AAABB" stroke="#4A7A9A" stroke-width="1"/>'
            '<rect x="16" y="4.5" width="36" height="4" rx="0.5" fill="#6A90A0" stroke="#4A7A9A" stroke-width="0.5"/>'
            '<rect x="57" y="2.5" width="1.5" height="5" fill="#AAA" rx="0.7"/>'
            '<path d="M 54 4 Q 54 2 57.5 2.5" stroke="#AAA" stroke-width="1.2" fill="none"/>'
            '<rect x="5" y="12" width="34" height="41" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="33" y="26" width="2" height="18" rx="1" fill="#1A1A1A"/>'
            '<rect x="41" y="12" width="34" height="41" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="45" y="26" width="2" height="18" rx="1" fill="#1A1A1A"/>'
            '<line x1="2" y1="57" x2="78" y2="57" stroke="#2C2C2C" stroke-width="1"/>'
        )

    elif "TRASH" in t:
        vb = "0 0 80 65"
        body = (
            '<rect x="2" y="57" width="76" height="6" fill="#D8D4CF"/>'
            '<rect x="2" y="2" width="76" height="55" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="2" y="2" width="76" height="4" fill="#E0DDD8" stroke="#2C2C2C" stroke-width="1"/>'
            '<rect x="5" y="9" width="70" height="44" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="14" y="15" width="20" height="28" rx="2" fill="none" stroke="#888" stroke-width="1"/>'
            '<rect x="46" y="15" width="20" height="28" rx="2" fill="none" stroke="#888" stroke-width="1"/>'
            '<line x1="14" y1="21" x2="34" y2="21" stroke="#888" stroke-width="1"/>'
            '<line x1="46" y1="21" x2="66" y2="21" stroke="#888" stroke-width="1"/>'
            '<rect x="26" y="48" width="28" height="2" rx="1" fill="#1A1A1A"/>'
            '<line x1="2" y1="57" x2="78" y2="57" stroke="#2C2C2C" stroke-width="1"/>'
        )

    elif "DOOR_DRAWER" in t:
        vb = "0 0 80 65"
        body = (
            '<rect x="2" y="57" width="76" height="6" fill="#D8D4CF"/>'
            '<rect x="2" y="2" width="76" height="55" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="2" y="2" width="76" height="4" fill="#E0DDD8" stroke="#2C2C2C" stroke-width="1"/>'
            '<rect x="5" y="8" width="70" height="16" rx="1" fill="#EEECE8" stroke="#555" stroke-width="1.2"/>'
            '<rect x="28" y="14" width="24" height="2.5" rx="1.2" fill="#1A1A1A"/>'
            '<rect x="5" y="26" width="33" height="27" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="32" y="34" width="2" height="12" rx="1" fill="#1A1A1A"/>'
            '<rect x="40" y="26" width="35" height="27" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="46" y="34" width="2" height="12" rx="1" fill="#1A1A1A"/>'
            '<line x1="2" y1="57" x2="78" y2="57" stroke="#2C2C2C" stroke-width="1"/>'
        )

    elif "DRAWERS" in t:
        vb = "0 0 80 65"
        body = (
            '<rect x="2" y="57" width="76" height="6" fill="#D8D4CF"/>'
            '<rect x="2" y="2" width="76" height="55" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="2" y="2" width="76" height="4" fill="#E0DDD8" stroke="#2C2C2C" stroke-width="1"/>'
            '<rect x="5" y="9" width="70" height="14" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="5" y="25" width="70" height="14" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="5" y="41" width="70" height="12" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="26" y="14" width="28" height="2" rx="1" fill="#1A1A1A"/>'
            '<rect x="26" y="30" width="28" height="2" rx="1" fill="#1A1A1A"/>'
            '<rect x="26" y="45" width="28" height="2" rx="1" fill="#1A1A1A"/>'
            '<line x1="2" y1="57" x2="78" y2="57" stroke="#2C2C2C" stroke-width="1"/>'
        )

    elif "NARROW" in t:
        vb = "0 0 45 65"
        body = (
            '<rect x="2" y="57" width="41" height="6" fill="#D8D4CF"/>'
            '<rect x="2" y="2" width="41" height="55" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="2" y="2" width="41" height="4" fill="#E0DDD8" stroke="#2C2C2C" stroke-width="1"/>'
            '<rect x="6" y="9" width="33" height="44" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="35" y="23" width="2" height="18" rx="1" fill="#1A1A1A"/>'
            '<line x1="2" y1="57" x2="43" y2="57" stroke="#2C2C2C" stroke-width="1"/>'
        )

    elif "OPEN" in t:
        vb = "0 0 80 65"
        body = (
            '<rect x="2" y="57" width="76" height="6" fill="#D8D4CF"/>'
            '<rect x="2" y="2" width="76" height="55" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="2" y="2" width="76" height="4" fill="#E0DDD8" stroke="#2C2C2C" stroke-width="1"/>'
            '<line x1="5" y1="26" x2="75" y2="26" stroke="#444" stroke-width="1"/>'
            '<line x1="5" y1="44" x2="75" y2="44" stroke="#444" stroke-width="1"/>'
            '<line x1="2" y1="57" x2="78" y2="57" stroke="#2C2C2C" stroke-width="1"/>'
        )

    elif "2DOOR" in t:
        vb = "0 0 80 65"
        body = (
            '<rect x="2" y="57" width="76" height="6" fill="#D8D4CF"/>'
            '<rect x="2" y="2" width="76" height="55" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="2" y="2" width="76" height="4" fill="#E0DDD8" stroke="#2C2C2C" stroke-width="1"/>'
            '<rect x="5" y="9" width="34" height="44" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="41" y="9" width="34" height="44" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="33" y="23" width="2" height="18" rx="1" fill="#1A1A1A"/>'
            '<rect x="45" y="23" width="2" height="18" rx="1" fill="#1A1A1A"/>'
            '<line x1="2" y1="57" x2="78" y2="57" stroke="#2C2C2C" stroke-width="1"/>'
        )

    elif "END_PANEL" in t:
        vb = "0 0 80 65"
        body = (
            '<rect x="2" y="2" width="76" height="61" fill="#F0EDE8" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<line x1="5" y1="12" x2="75" y2="12" stroke="#D8D4CF" stroke-width="0.8"/>'
            '<line x1="5" y1="20" x2="75" y2="20" stroke="#D8D4CF" stroke-width="0.8"/>'
            '<line x1="5" y1="28" x2="72" y2="28" stroke="#D8D4CF" stroke-width="0.8"/>'
            '<line x1="5" y1="36" x2="75" y2="36" stroke="#D8D4CF" stroke-width="0.8"/>'
            '<line x1="5" y1="44" x2="70" y2="44" stroke="#D8D4CF" stroke-width="0.8"/>'
            '<line x1="5" y1="52" x2="73" y2="52" stroke="#D8D4CF" stroke-width="0.8"/>'
            '<line x1="5" y1="60" x2="75" y2="60" stroke="#D8D4CF" stroke-width="0.8"/>'
        )

    elif "FILLER_PANEL" in t or "FILLER" in t:
        vb = "0 0 24 65"
        body = (
            '<rect x="2" y="2" width="20" height="61" fill="#F0EDE8" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<line x1="7" y1="4" x2="7" y2="61" stroke="#D8D4CF" stroke-width="1"/>'
            '<line x1="12" y1="4" x2="12" y2="61" stroke="#D8D4CF" stroke-width="1"/>'
            '<line x1="17" y1="4" x2="17" y2="61" stroke="#D8D4CF" stroke-width="1"/>'
        )

    else:
        # BASE_1DOOR — default
        vb = "0 0 80 65"
        body = (
            '<rect x="2" y="57" width="76" height="6" fill="#D8D4CF"/>'
            '<rect x="2" y="2" width="76" height="55" fill="#F8F8F6" stroke="#2C2C2C" stroke-width="1.5"/>'
            '<rect x="2" y="2" width="76" height="4" fill="#E0DDD8" stroke="#2C2C2C" stroke-width="1"/>'
            '<rect x="6" y="9" width="68" height="44" rx="1" fill="#F8F8F6" stroke="#444" stroke-width="1"/>'
            '<rect x="62" y="23" width="2" height="18" rx="1" fill="#1A1A1A"/>'
            '<line x1="2" y1="57" x2="78" y2="57" stroke="#2C2C2C" stroke-width="1"/>'
        )

    # SVG bez fiksnih dimenzija — kontejner u katalogu kontroliše veličinu
    return (f'<svg viewBox="{vb}" '
            f'style="display:block;max-width:100%;max-height:100%;width:auto;height:auto;" fill="none" xmlns="http://www.w3.org/2000/svg">'
            f'{body}</svg>')
