# -*- coding: utf-8 -*-
from __future__ import annotations

# Pomoćne konstante/funkcije za podešavanje prostorije (zidovi / otvori / instalacije)
ROOM_OPENING_TYPES = {
    "prozor": ("🪟", "Prozor", "#60A5FA"),
    "vrata": ("🚪", "Vrata", "#86EFAC"),
}
ROOM_FIXTURE_TYPES = {
    "voda": ("💧", "Voda/odvod", "#67E8F9"),
    "struja": ("⚡", "Struja", "#FCD34D"),
    "gas": ("🔥", "Gas", "#FCA5A5"),
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
            {"key": "A", "label": "Zid A", "length_mm": wl, "height_mm": wh, "openings": [], "fixtures": []},
            {"key": "B", "label": "Zid B", "length_mm": rd, "height_mm": wh, "openings": [], "fixtures": []},
            {"key": "C", "label": "Zid C", "length_mm": rd, "height_mm": wh, "openings": [], "fixtures": []},
        ]
        room["walls"] = walls
    if "active_wall" not in room:
        room["active_wall"] = "A"
    # Legacy sync (wall A mirrors room-level fields)
    wall_a = next((w for w in walls if w.get("key") == "A"), walls[0])
    room["wall_length_mm"] = int(wall_a.get("length_mm", room.get("wall_length_mm", 3000)))
    room["wall_height_mm"] = int(wall_a.get("height_mm", room.get("wall_height_mm", 2600)))
    room.setdefault("openings", wall_a.get("openings", []))
    if room.get("openings") is not wall_a.get("openings"):
        # keep same list reference for compatibility
        wall_a["openings"] = room["openings"]
    return walls


def get_room_wall(room: dict, key: str) -> dict:
    walls = ensure_room_walls(room)
    key = str(key or "A").upper()
    return next((w for w in walls if str(w.get("key", "")).upper() == key), walls[0] if walls else {})

