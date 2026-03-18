# -*- coding: utf-8 -*-
from __future__ import annotations

import copy

# Tabovi palete - svaki template tacno u jednom tabu (bez duplikata)
PALETTE_TABS = [
    {
        "key": "donji",
        "label": "Donji",
        "subgroups": [
            {"label": "1 / 2 vrata", "tids": ["BASE_NARROW", "BASE_1DOOR", "BASE_2DOOR", "BASE_OPEN"]},
            {"label": "Fioke", "tids": ["BASE_DRAWERS_3", "BASE_DOOR_DRAWER"]},
            {"label": "Funkcionalni", "tids": ["SINK_BASE", "BASE_TRASH"]},
            {"label": "Paneli", "tids": ["FILLER_PANEL", "END_PANEL"]},
        ],
    },
    {
        "key": "gornji",
        "label": "Gornji",
        "subgroups": [
            {"label": "1 / 2 vrata", "tids": ["WALL_NARROW", "WALL_1DOOR", "WALL_2DOOR", "WALL_GLASS", "WALL_LIFTUP"]},
            {"label": "Otvoreni", "tids": ["WALL_OPEN"]},
            {"label": "Iznad visokih", "tids": ["WALL_UPPER_1DOOR", "WALL_UPPER_2DOOR", "WALL_UPPER_OPEN"]},
        ],
    },
    {
        "key": "visoki",
        "label": "Visoki",
        "subgroups": [
            {"label": "Standardni", "tids": ["TALL_PANTRY", "TALL_GLASS", "TALL_DOORS", "TALL_OPEN"]},
            {"label": "Frizider ugradni", "tids": ["TALL_FRIDGE", "TALL_FRIDGE_FREEZER"]},
            {"label": "Frizider samostojeci", "tids": ["TALL_FRIDGE_FREESTANDING"]},
            {"label": "Gornja dopuna", "tids": ["TALL_TOP_DOORS", "TALL_TOP_OPEN"]},
        ],
    },
    {
        "key": "ormari",
        "label": "Ugradni",
        "subgroups": [
            {"label": "Kuvanje", "tids": ["BASE_COOKING_UNIT", "TALL_OVEN", "TALL_OVEN_MICRO"]},
            {"label": "Kuhinjski", "tids": ["BASE_DISHWASHER", "WALL_MICRO", "WALL_HOOD"]},
            {"label": "Samostojeci uredjaji", "tids": ["BASE_OVEN_HOB_FREESTANDING", "BASE_DISHWASHER_FREESTANDING"]},
        ],
    },
    {
        "key": "garderoba",
        "label": "Ormari",
        "subgroups": [
            {"label": "Krilna i klizna", "tids": ["TALL_WARDROBE_2DOOR", "TALL_WARDROBE_DRAWERS", "TALL_WARDROBE_2DOOR_SLIDING"]},
            {"label": "Američki plakar", "tids": ["TALL_WARDROBE_AMERICAN"]},
            {"label": "Unutrašnje sekcije", "tids": ["TALL_WARDROBE_INT_SHELVES", "TALL_WARDROBE_INT_DRAWERS", "TALL_WARDROBE_INT_HANG"]},
            {"label": "Ugaoni ormari", "tids": ["TALL_WARDROBE_CORNER", "TALL_WARDROBE_CORNER_SLIDING"]},
        ],
    },
]

_FRONT_COLOR_PRESETS = [
    {"hex": "#FDFDFB", "name": "Beli dekor", "swatch": "linear-gradient(145deg,#ffffff,#f0f1ee)"},
    {"hex": "#E7D9BF", "name": "Svetli drvni dekor", "swatch": "linear-gradient(145deg,#f3ead7,#d8c49e)"},
    {"hex": "#CFAE84", "name": "Bukva", "swatch": "linear-gradient(145deg,#e7c89d,#bb8f63)"},
    {"hex": "#B8A079", "name": "Jela", "swatch": "linear-gradient(145deg,#d6c4a2,#9f865f)"},
    {"hex": "#B98A55", "name": "Hrast", "swatch": "linear-gradient(145deg,#d6ab76,#996a3f)"},
    {"hex": "#D3B17F", "name": "Bor", "swatch": "linear-gradient(145deg,#e4c89b,#b88d59)"},
    {"hex": "#C49368", "name": "Aris", "swatch": "linear-gradient(145deg,#ddb58a,#a47347)"},
    {"hex": "#7D3F2D", "name": "Mahagoni", "swatch": "linear-gradient(145deg,#9a5842,#5d2c1f)"},
    {"hex": "#A85A42", "name": "Tresnja", "swatch": "linear-gradient(145deg,#bf7257,#8f4633)"},
    {"hex": "#8C5C3C", "name": "Kesten", "swatch": "linear-gradient(145deg,#a9744e,#6d452f)"},
    {"hex": "#B97A44", "name": "Tik", "swatch": "linear-gradient(145deg,#cf9760,#9d6232)"},
    {"hex": "#5D3E35", "name": "Palisander", "swatch": "linear-gradient(145deg,#7a554a,#452d27)"},
    {"hex": "#6F4B33", "name": "Orah", "swatch": "linear-gradient(145deg,#8d6648,#543825)"},
    {"hex": "#6C7A4E", "name": "Maslina", "swatch": "linear-gradient(145deg,#889865,#55603d)"},
    {"hex": "#2D5A3D", "name": "Zelena", "swatch": "linear-gradient(145deg,#3f7a54,#20442d)"},
    {"hex": "#A67F45", "name": "Bagrem", "swatch": "linear-gradient(145deg,#c49c60,#8b6736)"},
    {"hex": "#1E1B1A", "name": "Ebanovina", "swatch": "linear-gradient(145deg,#3a3532,#121010)"},
]


_TV_ZONE_TABS = [
    {
        "key": "donji",
        "label": "TV Komode",
        "subgroups": [
            {"label": "TV moduli", "tids": ["BASE_TV_2DOOR", "BASE_TV_DRAWERS", "BASE_TV_OPEN"]},
            {"label": "Komode", "tids": ["BASE_1DOOR", "BASE_2DOOR", "BASE_DRAWERS_3", "BASE_DOOR_DRAWER", "BASE_OPEN"]},
            {"label": "Paneli", "tids": ["FILLER_PANEL", "END_PANEL"]},
        ],
    },
    {
        "key": "gornji",
        "label": "Police",
        "subgroups": [
            {"label": "TV zid", "tids": ["WALL_TV_OPEN"]},
            {"label": "Zidni elementi", "tids": ["WALL_OPEN", "WALL_GLASS", "WALL_1DOOR", "WALL_2DOOR", "WALL_LIFTUP"]},
            {"label": "Gornja dopuna", "tids": ["WALL_UPPER_1DOOR", "WALL_UPPER_2DOOR", "WALL_UPPER_OPEN"]},
        ],
    },
]

# Ugaoni tab — vidljiv samo za L/U kuhinje
UGAONI_TAB = {
    "key": "ugaoni",
    "label": "Ugaoni",
    "subgroups": [
        {"label": "Donji ugaoni", "tids": ["BASE_CORNER", "BASE_CORNER_DIAGONAL"]},
        {"label": "Gornji ugaoni", "tids": ["WALL_CORNER", "WALL_CORNER_DIAGONAL"]},
    ],
}

# Layouts koji aktiviraju ugaoni tab
_CORNER_LAYOUTS = {"l_oblik", "u_oblik"}


def get_palette_tabs(
    project_type: str,
    wardrobe_profile: str = "standard",
    kitchen_layout: str = "",
) -> list[dict]:
    _ = str(project_type or "kitchen").lower().strip()
    # Scope odluka 12.03.2026:
    # `krojna_lista_pro` je kitchen-only aplikacija.
    # TV / wardrobe / hallway / bathroom / office scenariji ostaju van aktivnog kataloga.
    base_tabs = copy.deepcopy(PALETTE_TABS[:4])
    if str(kitchen_layout or "").lower().strip() in _CORNER_LAYOUTS:
        base_tabs.append(copy.deepcopy(UGAONI_TAB))
    return base_tabs


