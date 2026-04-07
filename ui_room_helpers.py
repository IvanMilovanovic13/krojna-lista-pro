# -*- coding: utf-8 -*-
from __future__ import annotations

from i18n import tr


ROOM_OPENING_TYPES = {
    "prozor": ("window", "Prozor", "#60A5FA"),
    "vrata": ("door_front", "Vrata", "#86EFAC"),
}

ROOM_FIXTURE_TYPES = {
    "voda": ("water_drop", "Voda/odvod", "#67E8F9"),
    "struja": ("bolt", "Struja", "#FCD34D"),
    "gas": ("local_fire_department", "Gas", "#FCA5A5"),
}


def get_room_opening_types(lang: str = "sr") -> dict:
    _lang = str(lang or "sr").lower().strip()
    return {
        "prozor": (ROOM_OPENING_TYPES["prozor"][0], tr("room.tool_window", _lang), ROOM_OPENING_TYPES["prozor"][2]),
        "vrata": (ROOM_OPENING_TYPES["vrata"][0], tr("room.tool_door", _lang), ROOM_OPENING_TYPES["vrata"][2]),
    }


def get_room_fixture_types(lang: str = "sr") -> dict:
    _lang = str(lang or "sr").lower().strip()
    return {
        "voda": (ROOM_FIXTURE_TYPES["voda"][0], tr("room.tool_water", _lang), ROOM_FIXTURE_TYPES["voda"][2]),
        "struja": (ROOM_FIXTURE_TYPES["struja"][0], tr("room.tool_socket", _lang), ROOM_FIXTURE_TYPES["struja"][2]),
        "gas": (ROOM_FIXTURE_TYPES["gas"][0], tr("room.tool_gas", _lang), ROOM_FIXTURE_TYPES["gas"][2]),
    }


def ensure_room_walls(room: dict) -> list:
    """Ensure room has per-wall structure; keep legacy fields in sync."""
    if not room:
        return []
    walls = room.get("walls") or []
    if not walls:
        wl = int(room.get("wall_length_mm", 3000))
        wh = int(room.get("wall_height_mm", 2600))
        rd = int(room.get("room_depth_mm", 3000))
        walls = [
            {"key": "A", "label": "Wall A", "length_mm": wl, "height_mm": wh, "openings": [], "fixtures": []},
            {"key": "B", "label": "Wall B", "length_mm": rd, "height_mm": wh, "openings": [], "fixtures": []},
            {"key": "C", "label": "Wall C", "length_mm": rd, "height_mm": wh, "openings": [], "fixtures": []},
        ]
        room["walls"] = walls
    if "active_wall" not in room:
        room["active_wall"] = "A"
    wall_a = next((w for w in walls if w.get("key") == "A"), walls[0])
    room["wall_length_mm"] = int(wall_a.get("length_mm", room.get("wall_length_mm", 3000)))
    room["wall_height_mm"] = int(wall_a.get("height_mm", room.get("wall_height_mm", 2600)))
    room.setdefault("openings", wall_a.get("openings", []))
    if room.get("openings") is not wall_a.get("openings"):
        wall_a["openings"] = room["openings"]
    return walls


def get_room_wall(room: dict, key: str) -> dict:
    walls = ensure_room_walls(room)
    key = str(key or "A").upper()
    return next((w for w in walls if str(w.get("key", "")).upper() == key), walls[0] if walls else {})
