# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass, field
import copy
import json
import logging
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

from i18n import normalize_language_code
from layout_engine import find_first_free_x, available_space_in_zone, solve_layout, _profile_clearance_mm, _l_corner_offsets_mm
from module_templates import resolve_template

_LOG = logging.getLogger(__name__)
_EMAIL_RE = re.compile(r"^[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9-]+(?:\.[A-Z0-9-]+)+$", re.IGNORECASE)


def normalize_email_address(email: str) -> str:
    return str(email or "").strip().lower()


def normalize_username(username: str) -> str:
    import re

    raw = str(username or "").strip().lower()
    if not raw:
        return ""
    cleaned = re.sub(r"[^a-z0-9._+-]+", "-", raw)
    cleaned = cleaned.strip("._+-")
    cleaned = re.sub(r"[-]{2,}", "-", cleaned)
    return cleaned[:40]


def _username_validation_error(username: str) -> str:
    clean_username = normalize_username(username)
    if not clean_username:
        return "Unesi korisnicko ime."
    if len(clean_username) < 3:
        return "Korisnicko ime mora imati najmanje 3 karaktera."
    return ""


def is_valid_email_address(email: str) -> bool:
    clean_email = normalize_email_address(email)
    if not clean_email or len(clean_email) > 254 or ".." in clean_email:
        return False
    return bool(_EMAIL_RE.match(clean_email))


def _email_validation_error(email: str) -> str:
    return "" if is_valid_email_address(email) else "Unesi ispravan email."


def _build_email_verification_url(token: str) -> str:
    try:
        from app_config import get_public_runtime_config

        base_url = str((get_public_runtime_config() or {}).get("base_url", "") or "").rstrip("/")
    except Exception:
        base_url = ""
    if not base_url:
        base_url = "http://localhost:8080"
    return f"{base_url}/verify-email?token={quote(str(token or '').strip(), safe='')}"


def _build_password_reset_url(token: str) -> str:
    try:
        from app_config import get_public_runtime_config

        base_url = str((get_public_runtime_config() or {}).get("base_url", "") or "").rstrip("/")
    except Exception:
        base_url = ""
    if not base_url:
        base_url = "http://localhost:8080"
    return f"{base_url}/reset-password?token={quote(str(token or '').strip(), safe='')}"


def _allow_auth_dev_link_fallback() -> bool:
    try:
        from app_config import get_app_config

        return str(get_app_config().app_env or "").strip().lower() in {"development", "test"}
    except Exception:
        return True


def _normalize_project_type(value: Any) -> str:
    raw = str(value or "").strip().lower()
    mapping = {
        "kitchen": "kitchen",
        "kuhinja": "kitchen",
        "tv_zone": "tv_zone",
        "tv_zona": "tv_zone",
        "hallway": "hallway",
        "hodnik": "hallway",
        "bathroom": "bathroom",
        "kupatilo": "bathroom",
        "office": "office",
        "kancelarija": "office",
        "wardrobe": "wardrobe",
        "orman": "wardrobe",
    }
    return mapping.get(raw, "kitchen")


def _compute_zones(k: dict) -> dict:
    wall = k.get("wall", {}) or {}
    wall_h = int(wall.get("height_mm", 2600))

    foot_mm = int(k.get("foot_height_mm", 100))
    base_h = int(k.get("base_korpus_h_mm", 720))

    wt = k.get("worktop", {}) or {}
    worktop_thk_mm = int(round(float(wt.get("thickness", 3.8)) * 10.0))

    vertical_gap_mm = int(k.get("vertical_gap_mm", 600))

    wall_gap = foot_mm + base_h + worktop_thk_mm + vertical_gap_mm
    wall_h_elem = max(300, wall_h - wall_gap - 50)
    tall_h_elem = max(1800, wall_h - foot_mm - 50)

    return {
        "base": {"height_mm": base_h},
        "wall": {"height_mm": wall_h_elem, "gap_from_base_mm": wall_gap},
        "tall": {"height_mm": tall_h_elem},
    }


_FREESTANDING_BASE_TIDS = {
    "BASE_DISHWASHER_FREESTANDING",
    "BASE_OVEN_HOB_FREESTANDING",
}


def _is_freestanding_template(template_id: str | None) -> bool:
    return "FREESTANDING" in str(template_id or "").upper().strip()


def _max_allowed_h_for_zone(zone: str, template_id: str | None = None) -> int:
    """
    Računa maksimalnu dozvoljenu visinu elementa u datoj zoni
    na osnovu kitchen parametara i max_element_height granice.
    """
    k = state.kitchen
    wall_h = int(k.get('wall', {}).get('height_mm', 2600))
    max_h_global = int(k.get('max_element_height', wall_h - 50))
    z = (zone or 'base').lower().strip()

    if z == 'base':
        _tid = str(template_id or "").upper().strip()
        if _is_freestanding_template(_tid):
            return max_h_global
        return int(k.get('base_korpus_h_mm', 720))

    elif z == 'wall':
        # Wall element počinje na wall_gap, ne sme preći max_h_global
        zones = k.get('zones', {}) or {}
        wall_gap = int((zones.get('wall', {}) or {}).get('gap_from_base_mm', 0))
        if wall_gap == 0:
            foot = int(k.get('foot_height_mm', 100))
            base_h = int(k.get('base_korpus_h_mm', 720))
            wt = int(round(float((k.get('worktop', {}) or {}).get('thickness', 3.8)) * 10.0))
            vgap = int(k.get('vertical_gap_mm', 600))
            wall_gap = foot + base_h + wt + vgap
        return max(100, max_h_global - wall_gap)

    elif z == 'wall_upper':
        # wall_upper počinje iznad wall elementa — koristi stvarnu visinu ako postoji
        zones = k.get('zones', {}) or {}
        wall_gap = int((zones.get('wall', {}) or {}).get('gap_from_base_mm', 0))
        if wall_gap == 0:
            foot = int(k.get('foot_height_mm', 100))
            base_h = int(k.get('base_korpus_h_mm', 720))
            wt = int(round(float((k.get('worktop', {}) or {}).get('thickness', 3.8)) * 10.0))
            vgap = int(k.get('vertical_gap_mm', 600))
            wall_gap = foot + base_h + wt + vgap
        # Nađi visinu wall elementa ispod — traži po target_x, fallback na najmanji wall
        target_x = int(getattr(state, "wall_upper_target_x", -1))
        _active_wk = str(
            (getattr(state, "room", {}) or {}).get("kitchen_wall",
                (getattr(state, "room", {}) or {}).get("active_wall", "A")) or "A"
        ).upper()
        wall_mods = [mm for mm in (k.get("modules", []) or [])
                     if str(mm.get("zone", "")).lower() == "wall"
                     and str(mm.get("wall_key", "A")).upper() == _active_wk]
        wall_h_ref = 0
        if target_x >= 0:
            # Traži wall element na istoj X poziciji
            ref = next((mm for mm in wall_mods
                        if int(mm.get("x_mm", -9999)) == target_x), None)
            if ref:
                wall_h_ref = int(ref.get("h_mm", 0))
        if wall_h_ref == 0 and wall_mods:
            # Fallback: uzmi najmanji wall element (konzervativna granica)
            wall_h_ref = min(int(mm.get("h_mm", 720)) for mm in wall_mods)
        if wall_h_ref == 0:
            wall_h_ref = 720  # poslednji fallback
        wu_y_start = wall_gap + wall_h_ref
        return max(100, max_h_global - wu_y_start)

    elif z == 'tall':
        foot = int(k.get('foot_height_mm', 100))
        return max(100, max_h_global - foot)

    elif z == 'tall_top':
        return max(100, wall_h - 50)

    return max_h_global


def _default_kitchen() -> Dict[str, Any]:
    k = {
        "project_type": "kitchen",
        "standard": "Srbija (SRB)",
        "wall": {"length_mm": 3000, "height_mm": 2600},
        "foot_height_mm": 100,
        "base_korpus_h_mm": 720,
        "vertical_gap_mm": 600,
        "worktop": {
            "thickness": 3.8,
            "width": 600.0,
            "mounting_reserve_mm": 20,
            "front_overhang_mm": 20,
            "field_cut": True,
            "edge_protection": True,
            "edge_protection_type": "silikon / vodootporni premaz",
            "joint_type": "STRAIGHT",
            "standard_lengths_mm": [2000, 3000, 4000],
        },
        "manufacturing": {"profile": "EU_SRB"},
        "materials": {
            "carcass_material": "Iverica",
            "carcass_thk": 18,
            "front_material": "Iverica",
            "front_thk": 18,
            "back_thk": 8,
            "edge_abs_thk": 2,
        },
        "front_color": "#FDFDFB",
        "modules": [],
        "layout": "jedan_zid",
    }
    k["zones"] = _compute_zones(k)
    k["max_element_height"] = int(k["wall"]["height_mm"]) - 50
    return k


def _default_room() -> Dict[str, Any]:
    base = {
        "wall_length_mm": 3000,
        "wall_height_mm": 2600,
        "room_depth_mm":  3000,   # dubina prostorije za 3D prikaz
        "openings": [],           # legacy: lista otvora za jedan zid
    }
    base["walls"] = [
        {
            "key": "A",
            "label": "Zid A",
            "length_mm": base["wall_length_mm"],
            "height_mm": base["wall_height_mm"],
            "openings": [],
            "fixtures": [],
        },
        {
            "key": "B",
            "label": "Zid B",
            "length_mm": base["room_depth_mm"],
            "height_mm": base["wall_height_mm"],
            "openings": [],
            "fixtures": [],
        },
        {
            "key": "C",
            "label": "Zid C",
            "length_mm": base["room_depth_mm"],
            "height_mm": base["wall_height_mm"],
            "openings": [],
            "fixtures": [],
        },
    ]
    base["active_wall"] = "A"
    return base


@dataclass
class AppState:
    active_tab: str = "wizard"
    active_group: str = "donji"
    selected_tid: str = ""
    kitchen: Dict[str, Any] = field(default_factory=_default_kitchen)
    next_id: int = 1
    view_mode: str = "Tehnički"
    show_grid: bool = False
    grid_mm: int = 10
    show_bounds: bool = True
    ceiling_filler: bool = False
    wall_upper_target_x: int = -1
    front_color: str = "#FDFDFB"
    selected_edit_id: int = 0
    language: str = "sr"
    mode: str = "add"            # "add" | "edit"
    sidebar_tab: str = 'dodaj'   # legacy UI tab state
    # ── Wizard ────────────────────────────────────────────────────────────────
    wizard_step: int = 1          # 1=tip nameštaja, 2=režim merenja, 3=raspored kuhinje, 4=prostorija
    project_type: str = "kitchen" # "kitchen" | "tv_zone" | "hallway" | "bathroom" | "office" | "wardrobe"
    furniture_type: str = ""      # "kuhinja" | "orman" | ...
    measurement_mode: str = ""    # "standard" | "pro"
    kitchen_layout: str = "jedan_zid"  # "jedan_zid" | "l_oblik" | "u_oblik" | "galija"
    l_corner_side: str = "right"  # "right" | "left"
    wardrobe_profile: str = "standard"   # "standard" | "american" | "corner"
    wardrobe_to_ceiling: bool = True
    wardrobe_door_mode: str = "hinged"   # "hinged" | "sliding"
    wardrobe_target_wall: str = "A"      # "A" | "B" | "C"
    current_user_id: int = 0
    current_user_email: str = ""
    current_user_display: str = ""
    current_session_token: str = ""
    current_session_expires_at: str = ""
    current_auth_mode: str = ""
    current_access_tier: str = ""
    current_subscription_status: str = ""
    current_gate_reason: str = ""
    current_can_access_app: bool = True
    account_upgrade_focus: bool = False
    current_project_id: int = 0
    current_project_name: str = ""
    current_project_source: str = ""
    room: Dict[str, Any] = field(default_factory=_default_room)
    room_setup_done: bool = False
    # Pamti poslednje koriscene dimenzije po zoni
    zone_defaults: Dict[str, Dict[str, int]] = field(default_factory=lambda: {
        "base":        {"h_mm": 720,  "d_mm": 560},
        "wall":        {"h_mm": 720,  "d_mm": 350},
        "wall_upper":  {"h_mm": 400,  "d_mm": 350},
        "tall":        {},  # tall ne deli defaults
        "tall_top":    {},
    })
    # ── Zone Depth Standards ───────────────────────────────────────────────────
    # Standardna dubina po zoni — korisnik može menjati u UI
    zone_depth_standards: Dict[str, int] = field(default_factory=lambda: {
        "base":       560,
        "wall":       320,
        "wall_upper": 300,
        "tall":       560,
        "tall_top":   560,
    })


_STATE_REGISTRY: Dict[str, AppState] = {"default": AppState()}


def _get_current_client_key() -> str:
    """
    Vraca per-klijent kljuc za _STATE_REGISTRY.
    Iskljucivo koristi context.client.id — nikad zajednicki storage.
    """
    try:
        from nicegui import context
        client = getattr(context, "client", None)
        client_id = getattr(client, "id", None)
        if client_id is not None:
            return str(client_id)
    except Exception:
        pass
    return "_no_client_context_"


def get_runtime_state() -> AppState:
    key = _get_current_client_key()
    _LOG.info("[SESSION_DEBUG] get_runtime_state key=%s email=%s",
              key,
              _STATE_REGISTRY.get(key, AppState()).current_user_email or "(prazno)")
    current = _STATE_REGISTRY.get(key)
    if current is None:
        current = AppState()
        _STATE_REGISTRY[key] = current
    return current


class StateProxy:
    def _target(self) -> AppState:
        return get_runtime_state()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._target(), name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self._target(), name, value)

    def __dir__(self) -> List[str]:
        return sorted(set(dir(type(self)) + dir(self._target())))

    def __repr__(self) -> str:
        return repr(self._target())


state = StateProxy()


def _sync_kitchen_wall_from_room(*, room: Optional[Dict[str, Any]] = None, wall_key: str | None = None) -> None:
    room_obj = room or getattr(state, "room", None) or {}
    walls = list(room_obj.get("walls", []) or [])
    if not walls:
        return
    wk = str(wall_key or room_obj.get("active_wall", "A") or "A").upper()
    wall = next((w for w in walls if str(w.get("key", "")).upper() == wk), None)
    if wall is None:
        return
    state.kitchen.setdefault("wall", {})
    state.kitchen["active_wall_key"] = wk
    state.kitchen["wall"]["length_mm"] = int(wall.get("length_mm", state.kitchen["wall"].get("length_mm", 3000)) or 3000)
    state.kitchen["wall"]["height_mm"] = int(wall.get("height_mm", state.kitchen["wall"].get("height_mm", 2600)) or 2600)
    state.kitchen["zones"] = _compute_zones(state.kitchen)
    state.kitchen.setdefault("wall_lengths_mm", {})
    state.kitchen.setdefault("wall_heights_mm", {})
    for _w in walls:
        _key = str(_w.get("key", "") or "").upper()
        if not _key:
            continue
        state.kitchen["wall_lengths_mm"][_key] = int(_w.get("length_mm", 3000) or 3000)
        state.kitchen["wall_heights_mm"][_key] = int(_w.get("height_mm", 2600) or 2600)


def reset_state() -> None:
    """Resetuje state na podrazumevane vrednosti — poziva se na svakom novom page loadu."""
    state.active_tab        = "wizard"
    state.wizard_step       = 1
    state.project_type      = "kitchen"
    state.furniture_type    = ""
    state.measurement_mode  = ""
    state.kitchen_layout    = "jedan_zid"
    state.l_corner_side     = "right"
    state.wardrobe_profile  = "standard"
    state.wardrobe_to_ceiling = True
    state.wardrobe_door_mode = "hinged"
    state.wardrobe_target_wall = "A"
    state.current_user_id   = 0
    state.current_user_email = ""
    state.current_user_display = ""
    state.current_session_token = ""
    state.current_session_expires_at = ""
    state.current_auth_mode = ""
    state.current_access_tier = ""
    state.current_subscription_status = ""
    state.current_gate_reason = ""
    state.current_can_access_app = True
    state.account_upgrade_focus = False
    state.current_project_id = 0
    state.current_project_name = ""
    state.current_project_source = ""
    state.room              = _default_room()
    state.room_setup_done   = False
    state.active_group      = "donji"
    state.selected_tid      = ""
    state.kitchen           = _default_kitchen()
    state.next_id           = 1
    state.view_mode         = "Tehnički"
    state.show_grid         = False
    state.grid_mm           = 10
    state.show_bounds       = True
    state.ceiling_filler    = False
    state.wall_upper_target_x = -1
    state.front_color       = "#FDFDFB"
    state.selected_edit_id  = 0
    state.language          = "sr"
    state.mode              = "add"
    state.sidebar_tab       = 'dodaj'
    state.zone_defaults     = {
        "base":       {"h_mm": 720, "d_mm": 560},
        "wall":       {"h_mm": 720, "d_mm": 350},
        "wall_upper": {"h_mm": 400, "d_mm": 350},
        "tall":       {},
        "tall_top":   {},
    }
    state.zone_depth_standards = {
        "base":       560,
        "wall":       320,
        "wall_upper": 300,
        "tall":       560,
        "tall_top":   560,
    }
    _sync_kitchen_wall_from_room(room=state.room, wall_key="A")


def reset_workspace_for_active_session() -> None:
    """
    Resetuje samo radni prostor projekta, ali zadržava aktivnog korisnika,
    sesiju i izabrani jezik. Ovo je važno kada se korisnik promeni u istom tabu,
    kako novi nalog ne bi nasledio prethodnu kuhinju iz memorije.
    """
    preserved_language = str(getattr(state, "language", "sr") or "sr")

    state.active_tab = "wizard"
    state.wizard_step = 1
    state.project_type = "kitchen"
    state.furniture_type = ""
    state.measurement_mode = ""
    state.kitchen_layout = "jedan_zid"
    state.l_corner_side = "right"
    state.wardrobe_profile = "standard"
    state.wardrobe_to_ceiling = True
    state.wardrobe_door_mode = "hinged"
    state.wardrobe_target_wall = "A"
    state.account_upgrade_focus = False
    state.current_project_id = 0
    state.current_project_name = ""
    state.current_project_source = ""
    state.room = _default_room()
    state.room_setup_done = False
    state.active_group = "donji"
    state.selected_tid = ""
    state.kitchen = _default_kitchen()
    state.next_id = 1
    state.view_mode = "Tehnički"
    state.show_grid = False
    state.grid_mm = 10
    state.show_bounds = True
    state.ceiling_filler = False
    state.wall_upper_target_x = -1
    state.front_color = "#FDFDFB"
    state.selected_edit_id = 0
    state.mode = "add"
    state.sidebar_tab = 'dodaj'
    state.zone_defaults = {
        "base": {"h_mm": 720, "d_mm": 560},
        "wall": {"h_mm": 720, "d_mm": 350},
        "wall_upper": {"h_mm": 400, "d_mm": 350},
        "tall": {},
        "tall_top": {},
    }
    state.zone_depth_standards = {
        "base": 560,
        "wall": 320,
        "wall_upper": 300,
        "tall": 560,
        "tall_top": 560,
    }
    state.language = preserved_language if preserved_language in ("sr", "en", "de") else "sr"
    _sync_kitchen_wall_from_room(room=state.room, wall_key="A")


# ── Lokalni add/delete (bez utils.py) ─────────────────────────────────────────

def _next_id() -> int:
    nid = int(state.next_id)
    state.next_id = nid + 1
    return nid


def _zone_norm(zone: str) -> str:
    z = str(zone or "base").lower().strip()
    return z if z in ("base", "wall", "wall_upper", "tall", "tall_top") else "base"


def _validate_blocking_design_rules(
    *,
    kitchen: Dict[str, Any],
    template_id: str,
    zone: str,
    x_mm: int = 0,
    w_mm: int,
    h_mm: int,
    d_mm: int,
    params: Optional[Dict[str, Any]] = None,
    wall_key: str = "A",
) -> None:
    """Blocking production/home-assembly checks before module is accepted."""
    tid = str(template_id or "").upper()
    z = _zone_norm(zone)
    p = params or {}
    wk = str(wall_key or "A").upper()

    # Corner offset safety net: regularni moduli na Wall B/C ne smiju biti u ugaonoj zoni Wall A
    if "CORNER" not in tid and wk != "A" and x_mm > 0:
        _lo, _ro = _l_corner_offsets_mm(kitchen, wk)
        if _lo > 0 and x_mm < _lo:
            raise ValueError(
                f"Blokirano: Modul na Zidu {wk} x={x_mm}mm ulazi u ugaoni prostor "
                f"(leva ugaona zona {_lo}mm dubine Zida A). "
                f"Pomeri desno za min {_lo - x_mm}mm ili dodaj ugaoni modul."
            )
        if _ro > 0:
            _wl_b = int(
                (kitchen.get("wall_lengths_mm", {}) or {}).get(
                    wk, (kitchen.get("wall", {}) or {}).get("length_mm", 3000)
                ) or 3000
            )
            if (x_mm + w_mm) > (_wl_b - _ro):
                raise ValueError(
                    f"Blokirano: Modul na Zidu {wk} kraj={x_mm + w_mm}mm ulazi u ugaoni prostor "
                    f"(desna ugaona zona {_ro}mm dubine Zida A, granica={_wl_b - _ro}mm). "
                    f"Pomeri levo ili dodaj ugaoni modul."
                )

    def _fail(msg: str) -> None:
        raise ValueError(f"Blokirano: {msg}")

    def _touching_corner_neighbor(_mods: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        _candidate_span = (int(x_mm), int(x_mm) + int(w_mm))
        for _m in _mods:
            _tid2 = str(_m.get("template_id", "")).upper()
            if "CORNER" not in _tid2:
                continue
            _mx = int(_m.get("x_mm", 0))
            _mw = int(_m.get("w_mm", 0))
            _mspan = (_mx, _mx + _mw)
            if abs(_candidate_span[1] - _mspan[0]) <= 2 or abs(_mspan[1] - _candidate_span[0]) <= 2:
                return _m
        return None

    _single_door_tids = {"BASE_1DOOR", "WALL_1DOOR", "WALL_UPPER_1DOOR", "WALL_NARROW", "BASE_NARROW"}
    _is_single_door = ("1DOOR" in tid) or (tid in _single_door_tids)
    if _is_single_door:
        left_clear, right_clear = _profile_clearance_mm(kitchen)
        wall_len = int((kitchen.get("wall", {}) or {}).get("length_mm", 3000) or 3000)
        handle_side_raw = p.get("handle_side", None)
        handle_side = str(handle_side_raw or "").lower()
        side_margin = 30
        if handle_side in ("left", "right") and int(x_mm) <= int(left_clear) + side_margin and handle_side == "right":
            _fail(
                "Jednokrilna vrata uz levi zid nemaju dovoljno mesta za otvaranje na strani sarke. "
                "Promeni stranu rucke ili dodaj filer najmanje 30-50mm."
            )
        if handle_side in ("left", "right") and (int(x_mm) + int(w_mm)) >= (int(wall_len) - int(right_clear) - side_margin) and handle_side == "left":
            _fail(
                "Jednokrilna vrata uz desni zid nemaju dovoljno mesta za otvaranje na strani sarke. "
                "Promeni stranu rucke ili dodaj filer najmanje 30-50mm."
            )

    if z == "wall_upper":
        support_found = any(
            str(m.get("zone", "")).lower() == "wall"
            and str(m.get("wall_key", "A")).upper() == wk
            and int(m.get("x_mm", 0)) <= int(x_mm)
            and (int(m.get("x_mm", 0)) + int(m.get("w_mm", 0))) >= (int(x_mm) + int(w_mm))
            for m in (kitchen.get("modules", []) or [])
        )
        if not support_found and any(
            str(m.get("zone", "")).lower() == "wall" and str(m.get("wall_key", "A")).upper() == wk
            for m in (kitchen.get("modules", []) or [])
        ):
            _fail("Drugi red gornjih elemenata mora biti oslonjen na element ispod po celoj svojoj sirini.")

    if z == "tall_top":
        support_found = any(
            str(m.get("zone", "")).lower() == "tall"
            and str(m.get("wall_key", "A")).upper() == wk
            and int(m.get("x_mm", 0)) <= int(x_mm)
            and (int(m.get("x_mm", 0)) + int(m.get("w_mm", 0))) >= (int(x_mm) + int(w_mm))
            for m in (kitchen.get("modules", []) or [])
        )
        if not support_found and any(
            str(m.get("zone", "")).lower() == "tall" and str(m.get("wall_key", "A")).upper() == wk
            for m in (kitchen.get("modules", []) or [])
        ):
            _fail("Popuna iznad visokog mora biti oslonjena na visoki element ispod po celoj svojoj sirini.")

    if z == "base" and "FREESTANDING" not in tid and "DISHWASHER" not in tid and d_mm < 500:
        _fail(
            f"Donji element dubine {d_mm}mm je preplitak za kuhinjski standard. "
            f"Postavi najmanje 500mm, preporuceno 560mm."
        )

    if z == "tall" and "FREESTANDING" not in tid and d_mm < 500:
        _fail(
            f"Visoki element dubine {d_mm}mm je preplitak za stabilan kuhinjski korpus. "
            f"Postavi najmanje 500mm, preporuceno 560mm."
        )

    if z == "wall" and d_mm > 400:
        _fail(
            f"Gornji element dubine {d_mm}mm je predubok za bezbednu i ergonomicnu montazu. "
            f"Drzi se opsega 300-400mm."
        )

    if z == "wall_upper" and d_mm > 700:
        _fail(
            f"Gornji element drugog reda dubine {d_mm}mm je predubok za sigurno kacenje. "
            f"Postavi najvise 700mm."
        )

    if z in ("wall", "wall_upper") and d_mm < 250 and "OPEN" not in tid:
        _fail(
            f"Gornji element dubine {d_mm}mm je premalen za standardni korpus i okove. "
            f"Postavi najmanje 250mm."
        )

    if "BASE_DISHWASHER" in tid and "FREESTANDING" not in tid and w_mm < 600:
        _fail("Ugradna masina za sudove trazi sirinu niše od najmanje 600mm.")

    if tid in {"BASE_COOKING_UNIT", "OVEN_HOB", "BASE_OVEN_HOB_FREESTANDING"} and w_mm < 600:
        _fail("Rerna/sporet sa plocom trazi najmanje 600mm sirine.")

    if "CORNER" in tid:
        _layout = str(getattr(state, "kitchen_layout", kitchen.get("layout", "")) or "").lower().strip()
        if _layout not in ("l_oblik", "u_oblik"):
            _fail("Ugaoni element ima smisla samo u L ili U rasporedu kuhinje.")
        wall_len = int((kitchen.get("wall_lengths_mm", {}) or {}).get(wk, (kitchen.get("wall", {}) or {}).get("length_mm", 3000)) or 3000)
        left_clear, right_clear = _profile_clearance_mm(kitchen)
        expected_anchor = get_l_corner_anchor_side(wk, kitchen)
        if z == "base":
            siblings = [
                m for m in (kitchen.get("modules", []) or [])
                if str(m.get("zone", "")).lower() == "base" and str(m.get("wall_key", "A")).upper() == wk
            ]
        elif z == "wall":
            siblings = [
                m for m in (kitchen.get("modules", []) or [])
                if str(m.get("zone", "")).lower() == "wall" and str(m.get("wall_key", "A")).upper() == wk
            ]
        else:
            siblings = []
        if any("CORNER" in str(m.get("template_id", "")).upper() for m in siblings):
            _fail(f"Na zidu {wk} vec postoji ugaoni modul u zoni {z.upper()}.")
        if expected_anchor == "right":
            if abs((int(x_mm) + int(w_mm)) - (wall_len - int(right_clear))) > 5:
                _fail(f"Ugaoni modul na zidu {wk} mora biti naslonjen na unutrasnji ugao, kao poslednji element desno.")
            if any(int(m.get("x_mm", 0)) > int(x_mm) for m in siblings):
                _fail(f"Ugaoni modul na zidu {wk} mora biti poslednji element na tom kraku.")
        else:
            if abs(int(x_mm) - int(left_clear)) > 5:
                _fail(f"Ugaoni modul na zidu {wk} mora biti naslonjen na unutrasnji ugao, kao prvi element levo.")
            if any((int(m.get("x_mm", 0)) + int(m.get("w_mm", 0))) < (int(x_mm) + int(w_mm)) for m in siblings):
                _fail(f"Ugaoni modul na zidu {wk} mora biti prvi element na tom kraku.")

    if tid in {"TALL_OVEN", "TALL_OVEN_MICRO"} and w_mm < 600:
        _fail("Visoka appliance kolona za rernu/mikrotalasnu trazi najmanje 600mm sirine.")

    if tid in {"TALL_FRIDGE", "TALL_FRIDGE_FREEZER", "TALL_FRIDGE_FREESTANDING"} and w_mm < 600:
        _fail("Frizider modul trazi najmanje 600mm sirine.")

    if "SINK" in tid and w_mm < 600:
        _fail("Sudoperski element manji od 600mm nije preporucen za laicki workflow.")

    if "CORNER" in tid:
        # Donji ugaoni (BASE) treba min 800mm za lazy-Susan mehanizam.
        # Gornji ugaoni (WALL) je manji element — min 450mm je dovoljan.
        _corner_min_w = 450 if "WALL" in tid else 800
        if w_mm < _corner_min_w:
            _fail(f"Ugaoni element sirine manje od {_corner_min_w}mm je previse rizican za stabilan ugaoni raspored.")

    if tid in {"WALL_HOOD", "WALL_MICRO"} and w_mm < 600:
        _fail("Modul za napu ili mikrotalasnu trazi najmanje 600mm sirine.")

    if tid in {"WALL_HOOD", "WALL_MICRO"} and d_mm < 300:
        _fail("Modul za napu ili mikrotalasnu trazi najmanje 300mm dubine.")

    if tid in {"BASE_DISHWASHER_FREESTANDING", "BASE_OVEN_HOB_FREESTANDING"} and d_mm < 580:
        _fail("Samostojeci uredjaj u donjoj zoni trazi najmanje 580mm dubine.")

    if tid == "TALL_FRIDGE_FREESTANDING" and d_mm < 600:
        _fail("Samostojeci frizider trazi najmanje 600mm dubine.")

    if tid in {"TALL_FRIDGE", "TALL_FRIDGE_FREEZER", "TALL_OVEN", "TALL_OVEN_MICRO"} and d_mm < 560:
        _fail("Integrisana visoka appliance kolona trazi najmanje 560mm dubine.")

    if "LIFTUP" in tid and w_mm > 1200:
        _fail(
            f"Lift-up sirine {w_mm}mm je previse rizican za ovu aplikaciju. "
            f"Razdvoji na dva elementa ili smanji sirinu na najvise 1200mm."
        )

    if "DRAWER" in tid and d_mm < 450:
        _fail(
            f"Fiokar dubine {d_mm}mm je preplitak za stabilan izbor klizaca. "
            f"Postavi najmanje 450mm."
        )

    drawer_heights = p.get("drawer_heights") or []
    if drawer_heights:
        if any(float(x) < 80 for x in drawer_heights):
            _fail("Front fioke manji od 80mm nije dozvoljen za stabilan laicki workflow.")
        total = sum(float(x) for x in drawer_heights)
        if total > (h_mm - 10):
            _fail(
                f"Zbir visina fioka ({total:.0f}mm) je prevelik za visinu modula {h_mm}mm. "
                f"Ostavi barem 10mm rezerve za fuge i frontove."
            )

    if "DOOR_DRAWER" in tid:
        _default_door_h = min(550.0, max(180.0, h_mm - 170.0))
        door_h = float(p.get("door_height", _default_door_h) or _default_door_h)
        if door_h < 180:
            _fail("Vrata kod kombinacije vrata + fioka moraju imati najmanje 180mm visine.")
        if door_h > (h_mm - 120):
            _fail("Vrata kod kombinacije vrata + fioka su previsoka; ostavi najmanje 120mm za fioku i fuge.")
        drawer_sum = sum(float(x) for x in (p.get("drawer_heights") or []))
        if drawer_sum > 0 and (door_h + drawer_sum) > h_mm:
            _fail(
                f"Zbir vrata i fioke ({door_h + drawer_sum:.0f}mm) je veci od visine modula {h_mm}mm."
            )

    if ("1DOOR" in tid or tid in {"BASE_1DOOR", "WALL_1DOOR", "WALL_NARROW", "BASE_NARROW"}) and w_mm > 600:
        _fail(
            f"Jednokrilni element sirine {w_mm}mm je previse sirok za stabilno kucno sklapanje. "
            f"Koristi 2 vrata ili podeli element."
        )

    if ("CORNER" not in tid) and ("1DOOR" in tid or tid in {"BASE_1DOOR", "WALL_1DOOR", "WALL_UPPER_1DOOR", "WALL_NARROW", "BASE_NARROW"}):
        if z in ("base", "wall"):
            _siblings = [
                m for m in (kitchen.get("modules", []) or [])
                if str(m.get("zone", "")).lower() == z and str(m.get("wall_key", "A")).upper() == wk
            ]
            _corner_neighbor = _touching_corner_neighbor(_siblings)
            if _corner_neighbor is not None:
                _handle_side = str(p.get("handle_side", "") or "").lower()
                _corner_x = int(_corner_neighbor.get("x_mm", 0))
                _opens_into_corner = False
                if int(x_mm) < _corner_x:
                    _opens_into_corner = _handle_side == "left"
                else:
                    _opens_into_corner = _handle_side == "right"
                if _opens_into_corner:
                    _fail(
                        "Jednokrilni sused uz ugaoni modul ne sme da otvara vrata ka uglu. "
                        "Promeni stranu rucke ili koristi drugi tip susednog elementa."
                    )
                _max_corner_neighbor_w = 500 if z == "base" else 450
                if int(w_mm) > _max_corner_neighbor_w:
                    _fail(
                        f"Jednokrilni sused uz ugaoni modul je preširok ({w_mm}mm) za sigurno otvaranje u L uglu. "
                        f"Koristi max {_max_corner_neighbor_w}mm, dvokrilni element, fiokar ili ostavi filer."
                    )

    if z == "tall" and h_mm > 2350 and "TOP" not in tid:
        _fail(
            f"Visoki element {h_mm}mm je previsok za standardno kucno rukovanje i montazu. "
            f"Smanji visinu ili koristi tall + tall_top podelu."
        )


def add_module_instance_local(
    *,
    template_id: str,
    zone: str,
    x_mm: int,
    w_mm: int,
    h_mm: int,
    d_mm: int,
    gap_after_mm: int = 0,
    label: str = "",
    params: Optional[Dict[str, Any]] = None,
    room: Optional[Dict[str, Any]] = None,
    wall_key: str = "A",
) -> Dict[str, Any]:
    k = state.kitchen
    z = _zone_norm(zone)
    _wk = str(wall_key or (room or {}).get("active_wall", "A") or "A").upper()
    if room:
        _sync_kitchen_wall_from_room(room=room, wall_key=_wk)

    _x_for_validation = int(x_mm)
    if "CORNER" in str(template_id or "").upper() and z in ("base", "wall"):
        _wall_len = int((k.get("wall_lengths_mm", {}) or {}).get(_wk, (k.get("wall", {}) or {}).get("length_mm", 3000)) or 3000)
        _left_clear, _right_clear = _profile_clearance_mm(k)
        _anchor = get_l_corner_anchor_side(_wk, k)
        if _anchor == "right":
            _x_for_validation = int(_wall_len) - int(_right_clear) - int(w_mm)
        else:
            _x_for_validation = int(_left_clear)

    tpl = resolve_template(template_id)
    nid = _next_id()

    # ── Depth standard logika ─────────────────────────────────────────────────
    # Ako je aparat (independent_depth), koristi prosleđeni d_mm bez promene standarda.
    # Za standardne korpuse:
    # - d_mm == zone standard  -> STANDARD
    # - d_mm != zone standard  -> CUSTOM (zadrzi unesenu dubinu)
    is_independent = bool(tpl.get("independent_depth", False))
    _req_d = int(d_mm)
    if is_independent:
        _depth_mode = "INDEPENDENT"
    else:
        _zone_std = get_zone_depth_standard(z)
        if _req_d > 0 and _req_d != _zone_std:
            _depth_mode = "CUSTOM"
            d_mm = _req_d
        else:
            _depth_mode = "STANDARD"
            d_mm = _zone_std

    if z == "tall_top":
        _tall_candidates = [
            m for m in (k.get("modules", []) or [])
            if str(m.get("zone", "")).lower() == "tall" and str(m.get("wall_key", "A")).upper() == _wk
        ]
        if not _tall_candidates:
            raise ValueError("Element iznad visokog moze da se doda tek kada postoji visoki element ispod njega.")

    if z == "wall_upper":
        _wall_candidates = [
            m for m in (k.get("modules", []) or [])
            if str(m.get("zone", "")).lower() == "wall" and str(m.get("wall_key", "A")).upper() == _wk
        ]
        if not _wall_candidates:
            raise ValueError("Drugi red gornjih elemenata moze da se doda tek kada postoji gornji element ispod njega.")

    _params_for_validation = dict(tpl.get("params") or {})
    if params:
        _params_for_validation.update(dict(params or {}))

    _validate_blocking_design_rules(
        kitchen=k,
        template_id=template_id,
        zone=z,
        x_mm=int(_x_for_validation),
        w_mm=int(w_mm),
        h_mm=int(h_mm),
        d_mm=int(d_mm),
        params=_params_for_validation,
        wall_key=_wk,
    )

    # ── Room constraints (otvori, instalacije) ────────────────────────────────
    _room_constraints: list = []
    _forbidden_spans: list = []
    if room:
        try:
            from room_constraints import (
                get_wall_constraints,
                get_hard_blocked_spans,
            )
            _room_constraints = get_wall_constraints(room, _wk, k)
            _forbidden_spans  = get_hard_blocked_spans(_room_constraints, z)
        except Exception as _rc_err:
            _LOG.debug("room_constraints greška: %s", _rc_err)

    # Pokušaj naći slobodan prostor od x_mm (hint korisnika / klik na canvas).
    # Ako nema slobodnog mesta od te pozicije, vrati se na klasično skeniranje od levog ruba.
    if "CORNER" in str(template_id or "").upper() and z in ("base", "wall"):
        free_x = int(_x_for_validation)
    else:
        _hint = int(x_mm) if int(x_mm) > 0 else None
        free_x = find_first_free_x(
            kitchen=k, zone=z, w_mm=int(w_mm), forbidden_spans=_forbidden_spans, start_x=_hint, wall_key=_wk
        )
        if free_x < 0 and _hint is not None:
            free_x = find_first_free_x(kitchen=k, zone=z, w_mm=int(w_mm), forbidden_spans=_forbidden_spans, wall_key=_wk)

    if z == "tall_top":
        if free_x < 0:
            free = available_space_in_zone(k, z, wall_key=_wk)
            raise ValueError(
                f"Nema slobodnog mesta u zoni '{z.upper()}' za element širine {w_mm}mm. "
                f"Slobodno: {free}mm."
            )
        use_x = int(free_x)
        tall_below = next(
            (m for m in (k.get("modules", []) or [])
             if str(m.get("zone", "")).lower() == "tall" and int(m.get("x_mm", 0)) == use_x),
            None
        )
        if tall_below:
            w_mm = int(tall_below.get("w_mm", w_mm))
    elif z == "wall_upper":
        wall_mods = [
            m for m in (k.get("modules", []) or [])
            if str(m.get("zone", "")).lower() == "wall" and str(m.get("wall_key", "A")).upper() == _wk
        ]
        if not wall_mods:
            use_x = 0
        else:
            if free_x < 0:
                free = available_space_in_zone(k, z, wall_key=_wk)
                raise ValueError(
                    f"Nema slobodnog mesta u zoni '{z.upper()}' za element širine {w_mm}mm. "
                    f"Slobodno: {free}mm."
                )
            wall_at_passed_x = next(
                (m for m in wall_mods if int(m.get("x_mm", 0)) == int(x_mm)),
                None
            )
            if wall_at_passed_x is not None:
                use_x = int(x_mm)
                w_mm = int(wall_at_passed_x.get("w_mm", w_mm))
            else:
                use_x = int(free_x)
    else:
        if free_x < 0:
            free = available_space_in_zone(k, z, wall_key=_wk)
            raise ValueError(
                f"Nema slobodnog mesta u zoni '{z.upper()}' za element širine {w_mm}mm. "
                f"Slobodno: {free}mm."
            )
        use_x = int(free_x)

    # ── Provjera prostornih constraint-a (prozori, vrata) ─────────────────────
    if _room_constraints:
        try:
            from room_constraints import check_module_against_constraints, get_installation_warnings
            _ok, _err = check_module_against_constraints(_room_constraints, z, use_x, int(w_mm))
            if not _ok:
                raise ValueError(_err)
            # Loguj upozorenja za instalacije (ne blokira, samo info)
            _warns = get_installation_warnings(_room_constraints, use_x, int(w_mm))
            for _w in _warns:
                _LOG.info("Instalacija upozorenje: %s", _w)
            if _warns:
                _params = dict(params or {})
                _params["installation_warnings"] = list(_warns)
                params = _params
        except ValueError:
            raise
        except Exception as _rc_err:
            _LOG.debug("room_constraints check greška: %s", _rc_err)

    _params_final = dict(tpl.get("params") or {})
    if params:
        _params_final.update(dict(params or {}))

    mod = {
        "id": nid,
        "template_id": template_id,
        "label": label or tpl.get("label", template_id),
        "zone": z,
        "x_mm": int(use_x),
        "w_mm": int(w_mm),
        "h_mm": int(h_mm),
        "d_mm": int(d_mm),
        "gap_after_mm": int(gap_after_mm),
        "params": _params_final,
        "depth_mode": _depth_mode,
        "wall_key": _wk,
    }
    # Validacija visine po zoni — uzima u obzir Y poziciju elementa
    _zone_max_h = _max_allowed_h_for_zone(z, template_id)
    if int(h_mm) > _zone_max_h:
        raise ValueError(
            f"Visina elementa {h_mm}mm prelazi dozvoljenu visinu za zonu '{z.upper()}' "
            f"({_zone_max_h}mm). Smanji visinu!"
        )

    k.setdefault("modules", []).append(mod)

    # Proveri preklapanje pre pack-a
    mods_in_zone = [
        m for m in k.get("modules", [])
        if str(m.get("zone","")).lower() == z and str(m.get("wall_key", "A")).upper() == _wk
    ]
    has_overlap = False
    for i in range(len(mods_in_zone)):
        for j in range(i+1, len(mods_in_zone)):
            a = (int(mods_in_zone[i].get("x_mm",0)), int(mods_in_zone[i].get("x_mm",0)) + int(mods_in_zone[i].get("w_mm",0)))
            b = (int(mods_in_zone[j].get("x_mm",0)), int(mods_in_zone[j].get("x_mm",0)) + int(mods_in_zone[j].get("w_mm",0)))
            if a[0] < b[1] and b[0] < a[1]:
                has_overlap = True
                break

    if has_overlap:
        # Presloži samo ako ima preklapanja
        solve_layout(k, zone=z, mode="pack", wall_key=_wk)
    else:
        # Samo clamp, ne pomeri postojeće
        from layout_engine import _clamp_to_wall
        _clamp_to_wall(k, mod)

    write_autosave_snapshot(reason="add_module")
    return mod


def delete_module_local(module_id: int) -> None:
    k = state.kitchen
    mods = k.get("modules", []) or []
    k["modules"] = [m for m in mods if int(m.get("id", -1)) != int(module_id)]
    write_autosave_snapshot(reason="delete_module")


def update_module_local(
    module_id: int,
    *,
    x_mm: int,
    w_mm: int,
    h_mm: int,
    d_mm: int,
    gap_after_mm: int,
    label: str,
    template_id: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    manual_x: Optional[bool] = None,
) -> None:
    k = state.kitchen
    # snapshot pre-change (for safe rollback)
    _before = copy.deepcopy(k.get("modules", []) or [])
    mods = k.get("modules", []) or []
    m = next((m for m in mods if int(m.get("id", -1)) == int(module_id)), None)
    if not m:
        raise ValueError("Element nije pronađen.")
    _sync_kitchen_wall_from_room(room=getattr(state, "room", None), wall_key=str(m.get("wall_key", "A") or "A").upper())
    _new_template_id = str(template_id or m.get("template_id", ""))
    _new_zone = str(resolve_template(_new_template_id).get("zone", m.get("zone", "base"))) if template_id else str(m.get("zone", "base"))
    _validate_blocking_design_rules(
        kitchen=k,
        template_id=_new_template_id,
        zone=_new_zone,
        x_mm=int(x_mm),
        w_mm=int(w_mm),
        h_mm=int(h_mm),
        d_mm=int(d_mm),
        params=params if params is not None else (m.get("params", {}) or {}),
        wall_key=str(m.get("wall_key", "A") or "A").upper(),
    )
    m["x_mm"] = int(x_mm)
    m["w_mm"] = int(w_mm)
    m["h_mm"] = int(h_mm)
    m["d_mm"] = int(d_mm)
    m["gap_after_mm"] = int(gap_after_mm)
    m["label"] = str(label)
    if manual_x is not None:
        m["manual_x"] = bool(manual_x)
    if template_id:
        m["template_id"] = str(template_id)
        # zona se automatski vezuje za template
        tpl = resolve_template(str(template_id))
        m["zone"] = str(tpl.get("zone", m.get("zone", "base")))
    if params is not None:
        m["params"] = params
    _wk = str(m.get("wall_key", "A") or "A").upper()
    z = str(m.get("zone", "base")).lower().strip()

    _room_constraints: list = []
    try:
        from room_constraints import get_wall_constraints, check_module_against_constraints, get_installation_warnings
        _room = getattr(state, "room", None) or {}
        if _room:
            _room_constraints = get_wall_constraints(_room, _wk, k)
            _ok, _err = check_module_against_constraints(_room_constraints, z, int(x_mm), int(w_mm))
            if not _ok:
                k["modules"] = _before
                raise ValueError(_err)
            _warns = get_installation_warnings(_room_constraints, int(x_mm), int(w_mm))
            if _warns:
                _p = dict(m.get("params", {}) or {})
                _p["installation_warnings"] = list(_warns)
                m["params"] = _p
            else:
                _p = dict(m.get("params", {}) or {})
                _p.pop("installation_warnings", None)
                m["params"] = _p
    except ValueError:
        raise
    except Exception as _rc_err:
        _LOG.debug("room_constraints update check greška: %s", _rc_err)

    # Base zone: reflow neighbors, but abort if no space
    if z == "base":
        solve_layout(k, zone="base", mode="pack", wall_key=_wk)
        # Proveri samo BASE overlap (ne diraj WALL/WALL_UPPER)
        base_mods = [
            mm for mm in (k.get("modules", []) or [])
            if str(mm.get("zone","")).lower() == "base" and str(mm.get("wall_key", "A")).upper() == _wk
        ]
        base_spans = [(int(mm.get("x_mm",0)), int(mm.get("x_mm",0)) + int(mm.get("w_mm",0))) for mm in base_mods]
        base_spans.sort(key=lambda s: s[0])
        has_overlap = any(base_spans[i][1] > base_spans[i+1][0] for i in range(len(base_spans)-1))
        if has_overlap:
            # Izračunaj koliko mm fali do zida
            wall_len = int(k.get("wall", {}).get("length_mm", 0))
            left, right = _profile_clearance_mm(k)
            usable = max(0, wall_len - int(left) - int(right))
            base_used = sum(int(mm.get("w_mm", 0)) + int(mm.get("gap_after_mm", 0)) for mm in base_mods)
            tall_used = sum(
                int(mm.get("w_mm", 0))
                for mm in (k.get("modules", []) or [])
                if str(mm.get("zone","")).lower() == "tall" and str(mm.get("wall_key", "A")).upper() == _wk
            )
            missing = max(0, base_used + tall_used - usable)
            k["modules"] = _before
            if missing > 0:
                raise ValueError(f"Nema prostora za izmenu širine: fali {missing}mm do zida.")
            raise ValueError("Nema prostora za izmenu širine: preklapanje donjih elemenata.")
    else:
        solve_layout(k, zone=z, mode="insert", wall_key=_wk)
    write_autosave_snapshot(reason="update_module")


def clear_all_local() -> None:
    state.kitchen["modules"] = []
    state.next_id = 1
    write_autosave_snapshot(reason="clear_project")


# ── SVG ikone za paletu ───────────────────────────────────────────────────────



# UI setters

def _set_view_mode(val: str) -> None:
    state.view_mode = str(val)


def _set_show_grid(val: bool) -> None:
    state.show_grid = bool(val)


def _set_grid_mm(val: int) -> None:
    state.grid_mm = int(val)


def _set_show_bounds(val: bool) -> None:
    state.show_bounds = bool(val)


def _set_ceiling_filler(val: bool) -> None:
    state.ceiling_filler = bool(val)


def _set_wall_length(val: int) -> None:
    _v = int(val)
    _wk = str((getattr(state, "room", {}) or {}).get("active_wall", "A") or "A").upper()
    _walls = list((getattr(state, "room", {}) or {}).get("walls", []) or [])
    _wall = next((w for w in _walls if str(w.get("key", "")).upper() == _wk), None)
    if _wall is not None:
        _wall["length_mm"] = _v
    state.kitchen.setdefault("wall_lengths_mm", {})[_wk] = _v
    state.kitchen["wall"]["length_mm"] = _v
    state.kitchen["zones"] = _compute_zones(state.kitchen)
    state.kitchen["l_corner_side"] = "right"
    write_autosave_snapshot(reason="set_wall_length")


def _set_wall_height(val: int) -> None:
    _v = int(val)
    _wk = str((getattr(state, "room", {}) or {}).get("active_wall", "A") or "A").upper()
    _walls = list((getattr(state, "room", {}) or {}).get("walls", []) or [])
    _wall = next((w for w in _walls if str(w.get("key", "")).upper() == _wk), None)
    if _wall is not None:
        _wall["height_mm"] = _v
    state.kitchen.setdefault("wall_heights_mm", {})[_wk] = _v
    state.kitchen["wall"]["height_mm"] = _v
    state.kitchen["zones"] = _compute_zones(state.kitchen)
    if "max_element_height" not in state.kitchen:
        state.kitchen["max_element_height"] = _v - 50
    write_autosave_snapshot(reason="set_wall_height")


def _set_foot_height(val: int) -> None:
    state.kitchen["foot_height_mm"] = int(val)
    state.kitchen["zones"] = _compute_zones(state.kitchen)
    write_autosave_snapshot(reason="set_foot_height")


def _recalc_base_module_heights(new_base_h: int) -> None:
    """Propagates base corpus height to existing BASE modules and recalculates drawer heights."""
    k = state.kitchen
    mats = k.get("materials", {}) or {}
    carcass_thk = float(mats.get("carcass_thk", 18))
    new_inner = max(0.0, float(new_base_h) - 2.0 * carcass_thk)
    drawer_step = 1

    def _floor_step(val: float) -> int:
        return int(float(val) // drawer_step) * drawer_step

    def _snap_step(val: float) -> int:
        return int(drawer_step * round(float(val) / drawer_step))

    def _normalize_drawers(values: list[float], total_target: float) -> list[int]:
        snapped = [max(80, _snap_step(v)) for v in values]
        diff = int(total_target - sum(snapped))
        while diff != 0:
            changed = False
            if diff > 0:
                for idx in reversed(range(len(snapped))):
                    snapped[idx] += drawer_step
                    diff -= drawer_step
                    changed = True
                    if diff <= 0:
                        break
            else:
                for idx in reversed(range(len(snapped))):
                    if snapped[idx] - drawer_step >= 80:
                        snapped[idx] -= drawer_step
                        diff += drawer_step
                        changed = True
                        if diff >= 0:
                            break
            if not changed:
                break
        return snapped

    for m in k.get("modules", []) or []:
        if str(m.get("zone", "")).lower() != "base":
            continue
        tid = str(m.get("template_id", "")).upper()
        if "DISHWASHER" in tid or "FREESTANDING" in tid:
            # Ugradna MZS ima svoje standarde i često ne prati visinu korpusa.
            continue

        m["h_mm"] = int(new_base_h)
        p = m.get("params", {}) or {}
        dh = p.get("drawer_heights")
        if not isinstance(dh, list) or not dh:
            m["params"] = p
            continue

        # Oven+hob+fioka: fioka = unutrašnja visina - visina rerne
        if ("OVEN" in tid or "COOKING_UNIT" in tid or "HOB" in tid) and int(p.get("n_drawers", 0) or 0) == 1:
            oven_h = float(p.get("oven_h", 595) or 595)
            p["drawer_heights"] = [round(max(80.0, new_inner - oven_h), 1)]
            p["n_drawers"] = 1
            m["params"] = p
            continue

        # Ostale fioke: skaliraj proporcionalno na novu unutrašnju visinu.
        old = [float(x) for x in dh if float(x) > 0]
        if not old:
            m["params"] = p
            continue
        old_sum = sum(old)
        if old_sum <= 0:
            m["params"] = p
            continue

        scaled = [round((x / old_sum) * new_inner, 1) for x in old]
        if scaled:
            scaled[-1] = round(new_inner - sum(scaled[:-1]), 1)
        p["drawer_heights"] = scaled
        p["n_drawers"] = len(scaled)
        m["params"] = p


def _set_base_height(val: int) -> None:
    _new_h = int(val)
    state.kitchen["base_korpus_h_mm"] = _new_h
    state.zone_defaults.setdefault("base", {})["h_mm"] = _new_h
    _recalc_base_module_heights(_new_h)
    state.kitchen["zones"] = _compute_zones(state.kitchen)
    write_autosave_snapshot(reason="set_base_height")


def _set_vertical_gap(val: int) -> None:
    state.kitchen["vertical_gap_mm"] = int(val)
    state.kitchen["zones"] = _compute_zones(state.kitchen)
    write_autosave_snapshot(reason="set_vertical_gap")


def _set_material(key: str, val) -> None:
    state.kitchen.setdefault('materials', {})[key] = val
    write_autosave_snapshot(reason="set_material")


def _set_front_color(val: str) -> None:
    s = str(val or "").strip()
    if not (s.startswith("#") and len(s) in (4, 7, 9)):
        return
    state.front_color = s
    state.kitchen["front_color"] = s
    write_autosave_snapshot(reason="set_front_color")


def _set_worktop_thickness(val: float) -> None:
    state.kitchen.setdefault('worktop', {})['thickness'] = float(val)
    state.kitchen['zones'] = _compute_zones(state.kitchen)
    write_autosave_snapshot(reason="set_worktop_thickness")


def _set_worktop_width(val: float) -> None:
    state.kitchen.setdefault('worktop', {})['width'] = float(val)
    write_autosave_snapshot(reason="set_worktop_width")


def _set_worktop_reserve_mm(val: int) -> None:
    state.kitchen.setdefault('worktop', {})['mounting_reserve_mm'] = int(val)
    write_autosave_snapshot(reason="set_worktop_reserve")


def _set_worktop_front_overhang_mm(val: int) -> None:
    state.kitchen.setdefault('worktop', {})['front_overhang_mm'] = int(val)
    write_autosave_snapshot(reason="set_worktop_front_overhang")


def _set_worktop_field_cut(val: bool) -> None:
    state.kitchen.setdefault('worktop', {})['field_cut'] = bool(val)
    write_autosave_snapshot(reason="set_worktop_field_cut")


def _set_worktop_edge_protection(val: bool) -> None:
    state.kitchen.setdefault('worktop', {})['edge_protection'] = bool(val)
    write_autosave_snapshot(reason="set_worktop_edge_protection")


def _set_worktop_edge_protection_type(val: str) -> None:
    state.kitchen.setdefault('worktop', {})['edge_protection_type'] = str(val or "").strip()
    write_autosave_snapshot(reason="set_worktop_edge_protection_type")


def _set_worktop_joint_type(val: str) -> None:
    state.kitchen.setdefault('worktop', {})['joint_type'] = str(val or "STRAIGHT").strip().upper()
    write_autosave_snapshot(reason="set_worktop_joint_type")


def _set_max_element_height(val: int) -> None:
    state.kitchen['max_element_height'] = int(val)
    write_autosave_snapshot(reason="set_max_element_height")


# ── Zone Depth Standards — helper funkcije ────────────────────────────────────

def _is_independent_depth(template_id: str) -> bool:
    """
    Vraća True ako template ima independent_depth: true u JSON-u.
    Ovi elementi (frižideri, aparati) ne učestvuju u zone standard logici.
    """
    from module_templates import resolve_template
    try:
        tpl = resolve_template(template_id)
        return bool(tpl.get("independent_depth", False))
    except Exception as ex:
        _LOG.debug("resolve_template failed for '%s': %s", template_id, ex)
        return False


def _get_depth_mode(mod: Dict[str, Any]) -> str:
    """
    Vraća depth_mode modula.
    Backward-compatible: ako ne postoji, default je:
      - INDEPENDENT za aparate
      - STANDARD za sve ostale
    """
    existing = mod.get("depth_mode")
    if existing in ("STANDARD", "CUSTOM", "INDEPENDENT"):
        return existing
    # Backward-compatible default
    tid = str(mod.get("template_id", ""))
    if _is_independent_depth(tid):
        return "INDEPENDENT"
    return "STANDARD"


def _set_depth_mode(mod: Dict[str, Any], mode: str) -> None:
    """Postavi depth_mode na modul (in-place)."""
    assert mode in ("STANDARD", "CUSTOM", "INDEPENDENT")
    mod["depth_mode"] = mode


def get_zone_depth_standard(zone: str) -> int:
    """Vraća trenutni depth standard za zonu."""
    z = str(zone or "base").lower().strip()
    standards = getattr(state, "zone_depth_standards", {})
    defaults = {"base": 560, "wall": 320, "wall_upper": 300, "tall": 560, "tall_top": 560}
    return int(standards.get(z, defaults.get(z, 560)))


def set_zone_depth_standard(zone: str, new_depth: int, *, update_existing: bool) -> int:
    """
    Postavi novi zone depth standard.
    Ako update_existing=True, ažurira sve STANDARD module u toj zoni.
    Vraća broj ažuriranih modula.
    """
    z = str(zone or "base").lower().strip()
    if not hasattr(state, "zone_depth_standards"):
        state.zone_depth_standards = {"base": 560, "wall": 320, "wall_upper": 300, "tall": 560, "tall_top": 560}
    state.zone_depth_standards[z] = int(new_depth)
    # Ažuriraj i zone_defaults.d_mm da params_panel prikazuje novi default
    if z in state.zone_defaults:
        state.zone_defaults[z]["d_mm"] = int(new_depth)

    updated = 0
    if update_existing:
        mods = state.kitchen.get("modules", []) or []
        for m in mods:
            if str(m.get("zone", "")).lower().strip() != z:
                continue
            if _get_depth_mode(m) == "STANDARD":
                m["d_mm"] = int(new_depth)
                updated += 1
    return updated


def suggest_corner_neighbor_guidance(zone: str, wall_key: str, template_id: str) -> Dict[str, Any]:
    z = str(zone or "base").lower().strip()
    wk = str(wall_key or "A").upper()
    tid = str(template_id or "").upper()
    mods = state.kitchen.get("modules", []) or []
    corner = next(
        (
            m for m in mods
            if str(m.get("zone", "")).lower() == z
            and str(m.get("wall_key", "A")).upper() == wk
            and "CORNER" in str(m.get("template_id", "")).upper()
        ),
        None,
    )
    if corner is None:
        return {"active": False}

    if z == "base":
        recommended = ["BASE_NARROW", "BASE_2DOOR", "BASE_DRAWERS", "BASE_DRAWERS_3"]
        avoid = ["BASE_1DOOR > 500mm", "otvaranje vrata ka uglu"]
        max_single = 500
    elif z == "wall":
        recommended = ["WALL_NARROW", "WALL_2DOOR", "WALL_GLASS", "WALL_LIFTUP"]
        avoid = ["WALL_1DOOR > 450mm", "otvaranje vrata ka uglu"]
        max_single = 450
    else:
        return {"active": False}

    recommended_handle_side = None
    if ("1DOOR" in tid) or (tid in {"BASE_1DOOR", "WALL_1DOOR", "WALL_UPPER_1DOOR", "WALL_NARROW", "BASE_NARROW"}):
        _anchor = get_l_corner_anchor_side(wk, state.kitchen)
        recommended_handle_side = "right" if _anchor == "right" else "left"

    return {
        "active": True,
        "wall_key": wk,
        "zone": z,
        "recommended_templates": recommended,
        "avoid": avoid,
        "max_single_width_mm": max_single,
        "recommended_handle_side": recommended_handle_side,
        "message": (
            f"L ugao aktivan na zidu {wk}: uz ugao koristi "
            f"{', '.join(recommended[:3])}; jednokrilni sused drzi do {max_single}mm."
        ),
    }


def get_l_corner_anchor_side(wall_key: str, kitchen: Optional[Dict[str, Any]] = None) -> str:
    wk = str(wall_key or "A").upper()
    k = kitchen or state.kitchen
    side = str((k or {}).get("l_corner_side", getattr(state, "l_corner_side", "right")) or "right").lower()
    if side not in ("left", "right"):
        side = "right"
    if wk == "A":
        return side
    if wk in ("B", "C"):
        return "left" if side == "right" else "right"
    return side


# ── Save / Load projekta (JSON) ───────────────────────────────────────────────

_SAVE_VERSION = "1.0"
_SAVE_APP     = "KrojnaListaPRO"
_LOCAL_DATA_DIR = Path(__file__).resolve().parent / "data"
_RECENT_DIR = _LOCAL_DATA_DIR / "recent_projects"
_RECENT_LIMIT = 8


def _current_user_storage_key() -> str:
    raw = str(getattr(state, "current_user_email", "") or "").strip().lower()
    if not raw:
        uid = int(getattr(state, "current_user_id", 0) or 0)
        raw = f"user_{uid}" if uid > 0 else "local"
    safe = "".join(ch if ch.isalnum() or ch in ("-", "_", ".") else "_" for ch in raw)
    return safe or "local"


def _recent_index_path() -> Path:
    return _LOCAL_DATA_DIR / f"recent_projects_index_{_current_user_storage_key()}.json"


def _autosave_path() -> Path:
    return _LOCAL_DATA_DIR / f"autosave_project_{_current_user_storage_key()}.json"


def _autosave_meta_path() -> Path:
    return _LOCAL_DATA_DIR / f"autosave_meta_{_current_user_storage_key()}.json"


def _get_active_user_record():
    try:
        from project_store import ensure_local_user, get_user_by_email
        email = str(getattr(state, "current_user_email", "") or "").strip()
        if email:
            user = get_user_by_email(email)
            if user is not None:
                return user
        return ensure_local_user()
    except Exception:
        return None


def build_demo_project_json() -> bytes:
    """Vraća gotov demo projekat kao JSON bytes u istom formatu kao Save/Load."""
    demo_path = Path(__file__).resolve().parent / "data" / "demo_kitchen.json"
    return demo_path.read_bytes()


def _ensure_recent_storage() -> None:
    _RECENT_DIR.mkdir(parents=True, exist_ok=True)


def _read_recent_index() -> List[Dict[str, Any]]:
    _ensure_recent_storage()
    _index_path = _recent_index_path()
    if not _index_path.exists():
        return []
    try:
        payload = json.loads(_index_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(payload, list):
        return []
    items: List[Dict[str, Any]] = []
    for entry in payload:
        if not isinstance(entry, dict):
            continue
        path = str(entry.get("path", "") or "").strip()
        if not path:
            continue
        items.append(
            {
                "label": str(entry.get("label", "") or "Projekat"),
                "path": path,
                "saved_at": str(entry.get("saved_at", "") or ""),
            }
        )
    return items


def _write_recent_index(items: List[Dict[str, Any]]) -> None:
    _ensure_recent_storage()
    _recent_index_path().write_text(
        json.dumps(items[:_RECENT_LIMIT], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def list_recent_projects() -> List[Dict[str, Any]]:
    try:
        from project_store import list_projects_for_user_by_source
        _user = _get_active_user_record()
        if _user is not None:
            _projects = list_projects_for_user_by_source(
                _user.id,
                source="local_recent",
                include_autosave=False,
                limit=_RECENT_LIMIT,
            )
            if _projects:
                return [
                    {
                        "label": str(_project.name or "Projekat"),
                        "path": f"store://{int(_project.id)}",
                        "saved_at": str(_project.updated_at or _project.last_opened_at or ""),
                        "store_project_id": int(_project.id),
                    }
                    for _project in _projects
                ]
    except Exception as ex:
        _LOG.debug("list_recent_projects store read failed: %s", ex)

    items = _read_recent_index()
    result: List[Dict[str, Any]] = []
    for entry in items:
        path = Path(str(entry.get("path", "") or ""))
        if not path.exists():
            continue
        result.append(
            {
                "label": str(entry.get("label", "") or "Projekat"),
                "path": str(path),
                "saved_at": str(entry.get("saved_at", "") or ""),
                "store_project_id": int(entry.get("store_project_id", 0) or 0),
            }
        )
    return result[:_RECENT_LIMIT]


def save_local_recent_project(*, label: str) -> str:
    payload_bytes = save_project_json()
    _store_project_id = None
    try:
        from project_store import save_payload_from_bytes
        _user = _get_active_user_record()
        if _user is None:
            raise RuntimeError("Aktivni korisnik nije dostupan.")
        _record = save_payload_from_bytes(
            user_id=_user.id,
            name=str(label or "Projekat"),
            payload_bytes=payload_bytes,
            source="local_recent",
            is_demo=False,
            is_autosave=False,
        )
        _store_project_id = int(_record.id)
        state.current_user_id = int(_user.id)
        state.current_project_id = int(_record.id)
        state.current_project_name = str(_record.name)
        state.current_project_source = str(_record.source)
        return f"store://{_store_project_id}"
    except Exception as ex:
        _LOG.debug("save_local_recent_project store sync failed, fallback to file: %s", ex)

    _ensure_recent_storage()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_label = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in str(label or "projekat"))[:40]
    if not safe_label:
        safe_label = "projekat"
    path = _RECENT_DIR / f"{timestamp}_{safe_label}.json"
    path.write_bytes(payload_bytes)
    items = [item for item in _read_recent_index() if str(item.get("path", "")) != str(path)]
    items.insert(
        0,
        {
            "label": str(label or "Projekat"),
            "path": str(path),
            "saved_at": datetime.now().isoformat(timespec="seconds"),
            "store_project_id": _store_project_id,
        },
    )
    _write_recent_index(items)
    return str(path)


def account_save_current_project(name: str | None = None) -> tuple[bool, str]:
    """
    Snima ili azurira projekat u bazi za aktivnog korisnika.
    Ako projekat vec postoji (current_project_id > 0), azurira ga.
    Ako je novi, kreira novi zapis.
    Vraca (True, naziv) ili (False, poruka_greske).
    """
    try:
        from project_store import get_project_record, save_payload_from_bytes, update_payload_from_bytes
        _user = _get_active_user_record()
        if _user is None:
            return False, "Korisnik nije prijavljen."
        payload_bytes = save_project_json()
        project_name = str(name or getattr(state, "current_project_name", "") or "Moj projekat").strip()
        if not project_name:
            project_name = "Moj projekat"
        current_project_id = int(getattr(state, "current_project_id", 0) or 0)
        current_project_source = str(getattr(state, "current_project_source", "") or "").strip().lower()
        can_update_existing = current_project_id > 0 and current_project_source == "account_saved"
        if can_update_existing:
            _existing = get_project_record(current_project_id, user_id=_user.id)
            if _existing is not None and str(_existing.source or "").strip().lower() == "account_saved":
                _record = update_payload_from_bytes(
                    project_id=current_project_id,
                    user_id=_user.id,
                    name=project_name,
                    payload_bytes=payload_bytes,
                    source="account_saved",
                )
                if _record is None:
                    _record = save_payload_from_bytes(
                        user_id=_user.id,
                        name=project_name,
                        payload_bytes=payload_bytes,
                        source="account_saved",
                    )
            else:
                _record = save_payload_from_bytes(
                    user_id=_user.id,
                    name=project_name,
                    payload_bytes=payload_bytes,
                    source="account_saved",
                )
        else:
            _record = save_payload_from_bytes(
                user_id=_user.id,
                name=project_name,
                payload_bytes=payload_bytes,
                source="account_saved",
            )
        state.current_project_id = int(_record.id)
        state.current_project_name = str(_record.name)
        state.current_project_source = str(_record.source)
        return True, str(_record.name)
    except Exception as ex:
        _LOG.warning("account_save_current_project failed: %s", ex)
        return False, str(ex)


def load_recent_project(path: str) -> Tuple[bool, str]:
    try:
        data = Path(path).read_bytes()
    except Exception as exc:
        return False, f"Ne mogu da otvorim lokalni projekat: {exc}"
    ok, err = load_project_json(data)
    if ok:
        try:
            _items = _read_recent_index()
            _matched = next((item for item in _items if str(item.get("path", "")) == str(path)), None)
            if _matched and _matched.get("store_project_id"):
                from project_store import get_project_record, touch_project_opened
                _user = _get_active_user_record()
                _user_id = int(getattr(_user, "id", 0) or 0)
                _pid = int(_matched["store_project_id"])
                if _user_id <= 0:
                    return ok, err
                touch_project_opened(_pid, user_id=_user_id)
                _project = get_project_record(_pid, user_id=_user_id)
                if _project is not None:
                    state.current_project_id = int(_project.id)
                    state.current_user_id = _user_id
                    state.current_project_name = str(_project.name)
                    state.current_project_source = str(_project.source)
        except Exception as ex:
            _LOG.debug("load_recent_project store touch failed: %s", ex)
    return ok, err


def write_autosave_snapshot(*, reason: str = "") -> str:
    payload_bytes = save_project_json()
    try:
        from project_store import save_payload_from_bytes
        _user = _get_active_user_record()
        if _user is None:
            raise RuntimeError("Aktivni korisnik nije dostupan.")
        _record = save_payload_from_bytes(
            user_id=_user.id,
            name="Auto-save",
            payload_bytes=payload_bytes,
            source="db_autosave",
            is_demo=False,
            is_autosave=True,
        )
        state.current_user_id = int(_user.id)
        return f"store://{int(_record.id)}"
    except Exception as ex:
        _LOG.debug("write_autosave_snapshot store sync failed, fallback to file: %s", ex)

    _ensure_recent_storage()
    _path = _autosave_path()
    _meta_path = _autosave_meta_path()
    _path.write_bytes(payload_bytes)
    _meta_path.write_text(
        json.dumps(
            {
                "saved_at": datetime.now().isoformat(timespec="seconds"),
                "reason": str(reason or ""),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return str(_path)


def get_autosave_info() -> Optional[Dict[str, str]]:
    try:
        from project_store import get_user_autosave_project
        _user = _get_active_user_record()
        if _user is not None:
            _autosave = get_user_autosave_project(_user.id)
            if _autosave is not None:
                return {
                    "path": f"store://{int(_autosave.id)}",
                    "saved_at": str(_autosave.updated_at or _autosave.last_opened_at or ""),
                    "reason": "",
                }
    except Exception as ex:
        _LOG.debug("get_autosave_info store read failed: %s", ex)

    _path = _autosave_path()
    _meta_path = _autosave_meta_path()
    if not _path.exists():
        return None
    saved_at = ""
    reason = ""
    if _meta_path.exists():
        try:
            payload = json.loads(_meta_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                saved_at = str(payload.get("saved_at", "") or "")
                reason = str(payload.get("reason", "") or "")
        except Exception:
            pass
    return {
        "path": str(_path),
        "saved_at": saved_at,
        "reason": reason,
    }


def load_autosave_project() -> Tuple[bool, str]:
    try:
        from project_store import get_project_payload, get_user_autosave_project, touch_project_opened
        _user = _get_active_user_record()
        if _user is not None:
            _autosave = get_user_autosave_project(_user.id)
            if _autosave is not None:
                _payload = get_project_payload(int(_autosave.id), user_id=int(_user.id))
                if _payload:
                    ok, err = load_project_json(_payload.encode("utf-8"))
                    if ok:
                        touch_project_opened(int(_autosave.id), user_id=int(_user.id))
                        state.current_user_id = int(_user.id)
                        state.current_project_id = int(_autosave.id)
                        state.current_project_name = str(_autosave.name)
                        state.current_project_source = str(_autosave.source)
                    return ok, err
    except Exception as ex:
        _LOG.debug("load_autosave_project store load failed: %s", ex)

    _path = _autosave_path()
    if not _path.exists():
        return False, "Auto-save projekat ne postoji."
    try:
        data = _path.read_bytes()
    except Exception as exc:
        return False, f"Ne mogu da otvorim auto-save projekat: {exc}"
    return load_project_json(data)


def seed_demo_project_store() -> None:
    try:
        from project_store import ensure_local_user, save_payload_from_bytes
        _user = ensure_local_user()
        _record = save_payload_from_bytes(
            user_id=_user.id,
            name="Demo primer",
            payload_bytes=build_demo_project_json(),
            source="builtin_demo",
            is_demo=True,
            is_autosave=False,
            replace_source=True,
        )
        state.current_user_id = int(_user.id)
        if not int(getattr(state, "current_project_id", 0) or 0):
            state.current_project_id = int(_record.id)
            state.current_project_name = str(_record.name)
            state.current_project_source = str(_record.source)
    except Exception as ex:
        _LOG.debug("seed_demo_project_store failed: %s", ex)


def load_project_from_store(project_id: int) -> Tuple[bool, str]:
    try:
        from project_store import get_project_payload, get_project_record, touch_project_opened
        _user = _get_active_user_record()
        _user_id = int(getattr(_user, "id", 0) or 0)
        if _user_id <= 0:
            return False, "Aktivni korisnik nije dostupan."
        _payload = get_project_payload(int(project_id), user_id=_user_id)
        if not _payload:
            return False, "Projekat nije pronađen ili ne pripada aktivnom korisniku."
        ok, err = load_project_json(_payload.encode("utf-8"))
        if not ok:
            return ok, err
        touch_project_opened(int(project_id), user_id=_user_id)
        _record = get_project_record(int(project_id), user_id=_user_id)
        if _record is not None:
            state.current_user_id = _user_id
            state.current_project_id = int(_record.id)
            state.current_project_name = str(_record.name)
            state.current_project_source = str(_record.source)
        return True, ""
    except Exception as ex:
        return False, f"Ne mogu da otvorim projekat iz storage baze: {ex}"


def list_user_store_projects() -> List[Dict[str, Any]]:
    try:
        from project_store import list_projects_for_user_by_source
        _user = _get_active_user_record()
        if _user is None:
            return []
        _projects = list_projects_for_user_by_source(
            _user.id,
            source="account_saved",
            include_autosave=False,
            limit=100,
        )
        result: List[Dict[str, Any]] = []
        for _project in _projects:
            result.append(
                {
                    "project_id": int(_project.id),
                    "name": str(_project.name),
                    "source": str(_project.source),
                    "language": str(_project.language),
                    "project_type": str(_project.project_type),
                    "is_demo": bool(_project.is_demo),
                    "updated_at": str(_project.updated_at),
                    "last_opened_at": str(_project.last_opened_at),
                }
            )
        return result
    except Exception as ex:
        _LOG.debug("list_user_store_projects failed: %s", ex)
        return []


def init_local_session_state() -> None:
    try:
        from auth_models import ensure_local_session
        session = ensure_local_session()
        _apply_session_state(session)
        state.current_session_token = ""
        state.current_session_expires_at = ""
        state.current_project_id = 0
        state.current_project_name = ""
        state.current_project_source = ""
    except Exception as ex:
        _LOG.debug("init_local_session_state failed: %s", ex)


def _get_user_storage() -> Any | None:
    # Koristimo app.storage.client umesto app.storage.user.
    # app.storage.user je na Render-u deljiv između browser sesija jer NiceGUI
    # pada na zajednički in-memory dict kada filesystem nije dostupan za pisanje.
    # app.storage.client je striktno per-WebSocket-konekcija i nikad nije deljiv.
    # Tradeoff: token se gubi na refresh stranice (korisnik se ponovo loguje),
    # ali nema cross-browser curenja sesije.
    try:
        from nicegui import app as nicegui_app
        return nicegui_app.storage.client
    except Exception:
        return None


def _persist_session_token(session_token: str, *, expires_at: str = "") -> None:
    storage = _get_user_storage()
    if storage is None:
        return
    clean_token = str(session_token or "").strip()
    if clean_token:
        storage["auth_session_token"] = clean_token
        storage["auth_session_expires_at"] = str(expires_at or "")
    else:
        storage.pop("auth_session_token", None)
        storage.pop("auth_session_expires_at", None)


def _load_persisted_session_token() -> str:
    storage = _get_user_storage()
    if storage is None:
        return ""
    return str(storage.get("auth_session_token", "") or "").strip()


def ensure_runtime_state_initialized(*, allow_local_fallback: bool = True) -> None:
    try:
        current = get_runtime_state()
        if str(getattr(current, "current_user_email", "") or "").strip():
            return
        persisted_token = _load_persisted_session_token()
        if persisted_token:
            from auth_models import restore_session_from_token
            from project_store import get_effective_auth_session, touch_auth_session
            auth_session = get_effective_auth_session(persisted_token)
            if auth_session is not None and str(auth_session.status).lower() == "active":
                auth_session = touch_auth_session(persisted_token)
            restored = restore_session_from_token(persisted_token)
            if restored is not None and auth_session is not None and str(auth_session.status).lower() == "active":
                _apply_session_state(restored)
                state.current_session_token = str(auth_session.session_token)
                state.current_session_expires_at = str(auth_session.expires_at)
                return
            _persist_session_token("")
        if allow_local_fallback:
            init_local_session_state()
    except Exception as ex:
        _LOG.debug("ensure_runtime_state_initialized failed: %s", ex)
        if allow_local_fallback:
            try:
                init_local_session_state()
            except Exception as fallback_ex:
                _LOG.debug("ensure_runtime_state_initialized local fallback failed: %s", fallback_ex)


def refresh_current_session_access() -> None:
    try:
        current_email = str(getattr(state, "current_user_email", "") or "").strip().lower()
        if not current_email:
            return
        from auth_models import build_session_from_user
        from project_store import get_user_by_email

        user = get_user_by_email(current_email)
        if user is None:
            init_local_session_state()
            return
        _apply_session_state(build_session_from_user(user))
    except Exception as ex:
        _LOG.debug("refresh_current_session_access failed: %s", ex)
        try:
            init_local_session_state()
        except Exception as fallback_ex:
            _LOG.debug("refresh_current_session_access local fallback failed: %s", fallback_ex)


def _clear_current_project_binding() -> None:
    state.current_project_id = 0
    state.current_project_name = ""
    state.current_project_source = ""


def _apply_session_state(session: Any) -> None:
    try:
        previous_user_id = int(getattr(state, "current_user_id", 0) or 0)
        previous_email = str(getattr(state, "current_user_email", "") or "").strip().lower()
        next_user_id = int(session.user.user_id)
        next_email = str(session.user.email)
        _LOG.info("[SESSION_DEBUG] _apply_session_state key=%s prev=%s next=%s",
                  _get_current_client_key(), previous_email or "(prazno)", next_email)
        user_changed = previous_user_id not in (0, next_user_id) or (
            previous_email and previous_email != str(next_email).strip().lower()
        )
        if user_changed:
            reset_workspace_for_active_session()
        state.current_user_id = int(session.user.user_id)
        state.current_user_email = str(session.user.email)
        state.current_user_display = str(session.user.display_name)
        state.current_auth_mode = str(session.user.auth_mode)
        state.current_access_tier = str(session.user.access_tier)
        state.current_subscription_status = str(session.user.subscription_status)
        state.current_gate_reason = str(session.gate_reason or "")
        state.current_can_access_app = bool(session.can_access_app)
        # Normalizuj UI/session state prema billing istini kako bi toolbar i tabovi
        # koristili isti efektivni pristup kao access gate logika.
        effective_access = get_effective_access_context()
        state.current_access_tier = str(effective_access.get("access_tier", state.current_access_tier) or "")
        state.current_subscription_status = str(
            effective_access.get("subscription_status", state.current_subscription_status) or ""
        )
        state.current_gate_reason = str(effective_access.get("gate_reason", state.current_gate_reason) or "")
        state.current_can_access_app = bool(
            effective_access.get("can_access_app", state.current_can_access_app)
        )
        if user_changed:
            _clear_current_project_binding()
        if str(getattr(state, "active_tab", "") or "").strip() in ("wizard", "nalog", ""):
            state.active_tab = "nova"
    except Exception as ex:
        _LOG.debug("_apply_session_state failed: %s", ex)


def login_user_session(identifier: str, password: str) -> Tuple[bool, str]:
    try:
        from auth_models import build_session_from_user
        from project_store import (
            append_audit_log,
            authenticate_user,
            clear_failed_login_attempts,
            create_email_verification_token,
            create_auth_session,
            get_login_rate_limit_status,
            get_user_by_login_identifier,
            record_login_attempt,
        )
        raw_identifier = str(identifier or "").strip()
        if not raw_identifier:
            return False, "Unesi email ili korisnicko ime."
        using_email = "@" in raw_identifier
        clean_identifier = normalize_email_address(raw_identifier) if using_email else normalize_username(raw_identifier)
        if using_email:
            email_err = _email_validation_error(clean_identifier)
            if email_err:
                return False, email_err
        else:
            username_err = _username_validation_error(clean_identifier)
            if username_err:
                return False, username_err
        if not str(password or "").strip():
            return False, "Unesi lozinku."
        rate_limit = get_login_rate_limit_status(clean_identifier)
        if bool(rate_limit.get("is_locked", False)):
            append_audit_log(
                event_type="auth.login_locked",
                status="warning",
                detail=f"login={clean_identifier} retry_after={int(rate_limit.get('retry_after_minutes', 0) or 0)}",
            )
            retry_after = int(rate_limit.get("retry_after_minutes", 0) or 0)
            return False, f"Previse neuspesnih prijava. Pokusaj ponovo za oko {retry_after} min."
        user = authenticate_user(clean_identifier, str(password))
        if user is None:
            record_login_attempt(email=clean_identifier, success=False)
            append_audit_log(
                event_type="auth.login_failed",
                status="warning",
                detail=f"login={clean_identifier}",
            )
            return False, "Pogresan email, korisnicko ime ili lozinka."
        effective_email = normalize_email_address(str(user.email or ""))
        if not bool(getattr(user, "email_verified", False)) or str(user.status or "").strip().lower() == "pending_verification":
            verification = create_email_verification_token(email=effective_email, reuse_existing_active=True)
            try:
                append_audit_log(
                    event_type="auth.login_blocked_unverified_email",
                    status="warning",
                    detail=f"email={effective_email}",
                    user_id=int(user.id),
                )
            except Exception as audit_ex:
                _LOG.debug("login_user_session unverified audit failed: %s", audit_ex)
            verification_url = _build_email_verification_url(str(verification.verification_token)) if verification else ""
            if verification_url:
                from email_service import send_verification_email

                sent, detail = send_verification_email(
                    to_email=effective_email,
                    verification_url=verification_url,
                    display_name=str(getattr(user, "display_name", "") or ""),
                )
                try:
                    append_audit_log(
                        event_type="auth.verification_email_resent" if sent else "auth.verification_email_resend_failed",
                        status="success" if sent else "warning",
                        detail=f"email={effective_email} | detail={detail}",
                        user_id=int(user.id),
                    )
                except Exception as audit_ex:
                    _LOG.debug("login_user_session verification resend audit failed: %s", audit_ex)
                if sent:
                    return False, "Email jos nije potvrdjen. Poslali smo novi verifikacioni email."
                if _allow_auth_dev_link_fallback():
                    return False, f"Email jos nije potvrdjen. Otvori verifikacioni link: {verification_url}"
                return False, "Email jos nije potvrdjen. Slanje verifikacionog emaila trenutno nije dostupno."
            return False, "Email jos nije potvrdjen. Zatrazi novi verifikacioni link."
        record_login_attempt(email=effective_email, success=True)
        clear_failed_login_attempts(effective_email)
        auth_session = create_auth_session(
            user_id=int(user.id),
            session_kind="browser",
            auth_provider="password",
            expires_in_days=14,
        )
        try:
            _persist_session_token(
                str(auth_session.session_token),
                expires_at=str(auth_session.expires_at),
            )
        except Exception:
            try:
                from project_store import revoke_auth_session
                revoke_auth_session(str(auth_session.session_token))
            except Exception as revoke_ex:
                _LOG.debug("login_user_session rollback revoke failed: %s", revoke_ex)
            raise
        session = build_session_from_user(user)
        _apply_session_state(session)
        state.current_session_token = str(auth_session.session_token)
        state.current_session_expires_at = str(auth_session.expires_at)
        try:
            append_audit_log(
                event_type="auth.login_success",
                status="success",
                detail=f"email={effective_email}",
                user_id=int(user.id),
            )
        except Exception as audit_ex:
            _LOG.debug("login_user_session audit failed: %s", audit_ex)
        state.active_tab = "nova"
        return True, ""
    except Exception as ex:
        return False, f"Ne mogu da pokrenem prijavu: {ex}"


def register_trial_user_session(email: str, display_name: str = "", password: str = "", username: str = "") -> Tuple[bool, str]:
    try:
        from project_store import (
            append_audit_log,
            create_email_verification_token,
            create_user_record,
            get_user_by_username,
            hash_password,
        )
        clean_email = normalize_email_address(email)
        email_err = _email_validation_error(clean_email)
        if email_err:
            return False, email_err
        clean_username = normalize_username(username) if str(username or "").strip() else normalize_username(clean_email.split("@", 1)[0])
        username_err = _username_validation_error(clean_username)
        if username_err:
            return False, username_err
        existing_username = get_user_by_username(clean_username)
        if existing_username is not None and normalize_email_address(existing_username.email) != clean_email:
            return False, "Korisnicko ime je zauzeto."
        clean_password = str(password or "")
        if len(clean_password) < 6:
            return False, "Lozinka mora imati najmanje 6 karaktera."
        user = create_user_record(
            email=clean_email,
            username=clean_username,
            display_name=str(display_name).strip(),
            password_hash=hash_password(clean_password),
            auth_mode="password",
            access_tier="trial",
            status="pending_verification",
            email_verified=False,
        )
        verification = create_email_verification_token(email=clean_email)
        verification_url = _build_email_verification_url(str(verification.verification_token)) if verification else ""
        try:
            append_audit_log(
                event_type="auth.register_trial_pending_verification",
                status="success",
                detail=f"email={clean_email}",
                user_id=int(user.id),
            )
        except Exception as audit_ex:
            _LOG.debug("register_trial_user_session audit failed: %s", audit_ex)
        state.active_tab = "nalog"
        if verification_url:
            from email_service import send_verification_email

            sent, detail = send_verification_email(
                to_email=clean_email,
                verification_url=verification_url,
                display_name=str(user.display_name or ""),
            )
            try:
                append_audit_log(
                    event_type="auth.verification_email_sent" if sent else "auth.verification_email_send_failed",
                    status="success" if sent else "warning",
                    detail=f"email={clean_email} | detail={detail}",
                    user_id=int(user.id),
                )
            except Exception as audit_ex:
                _LOG.debug("register verification email audit failed: %s", audit_ex)
            if sent:
                return True, "Nalog je napravljen. Proveri email i potvrdi adresu preko poslatog linka."
            if _allow_auth_dev_link_fallback():
                return True, f"Nalog je napravljen. Potvrdi email preko linka: {verification_url}"
            return True, "Nalog je napravljen, ali slanje verifikacionog emaila trenutno nije dostupno."
        return True, "Nalog je napravljen. Potvrdi email preko verifikacionog linka."
    except Exception as ex:
        return False, f"Ne mogu da napravim probni nalog: {ex}"


def verify_email_with_token(token: str) -> Tuple[bool, str]:
    clean_token = str(token or "").strip()
    if not clean_token:
        return False, "Verifikacioni token nedostaje."
    try:
        from project_store import append_audit_log, get_effective_email_verification_token, use_email_verification_token

        token_record = get_effective_email_verification_token(clean_token)
        if token_record is None:
            return False, "Verifikacioni token nije pronadjen."
        if str(token_record.status or "").strip().lower() != "active":
            return False, "Verifikacioni token vise nije aktivan."
        user = use_email_verification_token(verification_token=clean_token)
        if user is None:
            return False, "Email nije moguce potvrditi."
        try:
            append_audit_log(
                event_type="auth.email_verified",
                status="success",
                detail=f"email={user.email}",
                user_id=int(user.id),
            )
        except Exception as audit_ex:
            _LOG.debug("verify_email_with_token audit failed: %s", audit_ex)
        return True, f"Email je potvrdjen za {user.email}. Sada mozes da se prijavis."
    except Exception as ex:
        return False, f"Ne mogu da potvrdim email: {ex}"


def restore_local_session_state() -> Tuple[bool, str]:
    try:
        _persist_session_token("")
        init_local_session_state()
        return True, ""
    except Exception as ex:
        return False, f"Ne mogu da vratim lokalnu sesiju: {ex}"


def logout_current_session() -> Tuple[bool, str]:
    try:
        user_id = int(getattr(state, "current_user_id", 0) or 0)
        user_email = str(getattr(state, "current_user_email", "") or "").strip().lower()
        if str(getattr(state, "current_session_token", "") or "").strip():
            try:
                from project_store import append_audit_log, revoke_auth_session
                revoke_auth_session(str(state.current_session_token))
                append_audit_log(
                    event_type="auth.logout",
                    status="success",
                    detail=f"email={user_email}",
                    user_id=user_id,
                )
            except Exception as ex:
                _LOG.debug("logout_current_session revoke/audit failed: %s", ex)
        _persist_session_token("")
        init_local_session_state()
        return True, ""
    except Exception as ex:
        return False, f"Ne mogu da odjavim aktivnu sesiju: {ex}"


def build_forgot_password_message(email: str) -> Tuple[bool, str]:
    clean_email = normalize_email_address(email)
    if not clean_email:
        return False, "Unesi email adresu."
    email_err = _email_validation_error(clean_email)
    if email_err:
        return False, email_err
    try:
        from project_store import append_audit_log, create_password_reset_token, get_user_by_email
        reset_token = create_password_reset_token(email=clean_email, expires_in_minutes=30)
        if reset_token is None:
            append_audit_log(
                event_type="auth.password_reset_requested_missing_user",
                status="warning",
                detail=f"email={clean_email}",
            )
            return False, "Ne postoji nalog za taj email."
        append_audit_log(
            event_type="auth.password_reset_requested",
            status="success",
            detail=f"email={clean_email}",
            user_id=int(reset_token.user_id),
        )
        user = get_user_by_email(clean_email)
        reset_url = _build_password_reset_url(str(reset_token.reset_token))
        from email_service import send_password_reset_email

        sent, detail = send_password_reset_email(
            to_email=clean_email,
            reset_url=reset_url,
            display_name=str(getattr(user, "display_name", "") or ""),
        )
        append_audit_log(
            event_type="auth.password_reset_email_sent" if sent else "auth.password_reset_email_failed",
            status="success" if sent else "warning",
            detail=f"email={clean_email} | detail={detail}",
            user_id=int(reset_token.user_id),
        )
        if sent:
            return True, "Poslali smo email sa linkom za reset lozinke."
        if _allow_auth_dev_link_fallback():
            return (
                True,
                "Reset token je napravljen. Email servis jos nije povezan, "
                f"pa za sada razvojni token glasi: {reset_token.reset_token} "
                f"(vazi do {reset_token.expires_at})."
            )
        return False, "Reset lozinke trenutno nije dostupan. Pokusaj ponovo malo kasnije."
    except Exception as ex:
        return False, f"Ne mogu da pripremim reset lozinke: {ex}"


def reset_password_with_token(reset_token: str, new_password: str) -> Tuple[bool, str]:
    clean_token = str(reset_token or "").strip()
    clean_password = str(new_password or "")
    if not clean_token:
        return False, "Unesi reset token."
    if len(clean_password) < 6:
        return False, "Nova lozinka mora imati najmanje 6 karaktera."
    try:
        from project_store import append_audit_log, hash_password, use_password_reset_token
        user = use_password_reset_token(
            reset_token=clean_token,
            new_password_hash=hash_password(clean_password),
        )
        if user is None:
            append_audit_log(
                event_type="auth.password_reset_failed",
                status="warning",
                detail="invalid_or_expired_token",
            )
            return False, "Reset token nije vazeci ili je istekao."
        append_audit_log(
            event_type="auth.password_reset_completed",
            status="success",
            detail=f"email={user.email}",
            user_id=int(user.id),
        )
        return True, f"Lozinka je promenjena za {user.email}."
    except Exception as ex:
        return False, f"Ne mogu da zavrsim promenu lozinke: {ex}"


def get_current_billing_summary() -> Dict[str, Any] | None:
    try:
        from billing_models import get_billing_summary_for_email
        email = str(getattr(state, "current_user_email", "") or "").strip()
        auth_mode = str(getattr(state, "current_auth_mode", "") or "").strip().lower()
        if not email:
            return None
        if auth_mode == "local":
            return None
        summary = get_billing_summary_for_email(email)
        if summary is None:
            return None
        return {
            "email": str(summary.email),
            "access_tier": str(summary.access_tier),
            "account_status": str(summary.account_status),
            "billing_status": str(summary.billing_status),
            "plan_code": str(summary.plan_code),
            "provider": str(summary.provider),
            "current_period_end": str(summary.current_period_end),
            "trial_started_at": str(summary.trial_started_at),
            "has_checkout": bool(summary.has_checkout),
            "has_portal": bool(summary.has_portal),
            "stripe_ready": bool(summary.billing_ready),
            "billing_ready": bool(summary.billing_ready),
        }
    except Exception as ex:
        _LOG.debug("get_current_billing_summary failed: %s", ex)
        return None


def get_effective_access_context() -> Dict[str, Any]:
    from i18n import tr

    lang = str(getattr(state, "language", "sr") or "sr")
    source = str(getattr(state, "current_project_source", "") or "").strip().lower()
    tier = str(getattr(state, "current_access_tier", "") or "").strip().lower()
    status = str(getattr(state, "current_subscription_status", "") or "").strip().lower()
    gate_reason = str(getattr(state, "current_gate_reason", "") or "")
    can_access_app = bool(getattr(state, "current_can_access_app", True))
    auth_mode = str(getattr(state, "current_auth_mode", "") or "").strip().lower()

    context: Dict[str, Any] = {
        "source": source,
        "access_tier": tier,
        "subscription_status": status,
        "gate_reason": gate_reason,
        "can_access_app": can_access_app,
        "auth_mode": auth_mode,
    }

    if "demo" in source:
        context.update(
            {
                "access_tier": "demo",
                "subscription_status": "demo_active",
                "gate_reason": "",
                "can_access_app": True,
                "mode": "demo",
            }
        )
        return context

    billing = get_current_billing_summary()
    if billing:
        billing_status = str(billing.get("billing_status", "") or "").strip().lower()
        plan_code = str(billing.get("plan_code", "") or "").strip().lower()
        billing_access_tier = str(billing.get("access_tier", "") or "").strip().lower()
        is_paid_billing = billing_status in {"active", "paid"} and plan_code not in {"", "trial"}
        is_trial_billing = billing_status in {"trial", "trialing", "on_trial"} or (
            billing_status in {"active", "paid"} and plan_code == "trial"
        )
        is_unactivated = billing_status == "unactivated"

        if is_unactivated:
            context.update(
                {
                    "access_tier": "unactivated",
                    "subscription_status": "unactivated",
                    "gate_reason": "Izaberi plan ili aktiviraj besplatni probni pristup.",
                    "can_access_app": False,
                    "mode": "unactivated",
                }
            )
            return context

        if is_paid_billing:
            context.update(
                {
                    "access_tier": "paid",
                    "subscription_status": "paid_active",
                    "gate_reason": "",
                    "can_access_app": True,
                    "mode": "paid",
                }
            )
            return context

        if billing_access_tier == "admin":
            context.update(
                {
                    "access_tier": "admin",
                    "subscription_status": "admin_active",
                    "gate_reason": "",
                    "can_access_app": True,
                    "mode": "admin",
                }
            )
            return context

        if is_trial_billing:
            context.update(
                {
                    "access_tier": "trial",
                    "subscription_status": "trial_active",
                    "gate_reason": tr("access.cutlist_reason_free", lang),
                    "can_access_app": True,
                    "mode": "trial",
                }
            )
            return context

    if tier in {"admin", "paid", "pro"}:
        context["mode"] = tier or "paid"
        return context
    if tier == "trial":
        context.setdefault("gate_reason", tr("access.cutlist_reason_free", lang))
        context["mode"] = "trial"
        return context
    if tier in {"local", "local_beta", ""}:
        context.setdefault("gate_reason", tr("access.cutlist_reason_local", lang))
        context["mode"] = "free"
        return context
    if status in {"inactive", "canceled", "past_due"}:
        context.setdefault("gate_reason", tr("access.cutlist_reason_inactive", lang))
        context["mode"] = "blocked"
        return context
    context.setdefault("gate_reason", tr("access.cutlist_reason_locked", lang))
    context["mode"] = "blocked"
    return context


def get_cutlist_access_state() -> Dict[str, str]:
    context = get_effective_access_context()
    source = str(context.get("source", "") or "").strip().lower()
    tier = str(context.get("access_tier", "") or "").strip().lower()
    status = str(context.get("subscription_status", "") or "").strip().lower()
    gate_reason = str(context.get("gate_reason", "") or "")

    if "demo" in source:
        return {"allowed": "true", "reason": "", "mode": "demo"}
    if tier in {"admin", "paid", "pro"}:
        return {"allowed": "true", "reason": "", "mode": tier or "paid"}
    if tier == "trial":
        return {
            "allowed": "false",
            "reason": gate_reason,
            "mode": "free",
        }
    if tier in {"local", "local_beta", ""}:
        return {
            "allowed": "false",
            "reason": gate_reason,
            "mode": "free",
        }
    if status in {"inactive", "canceled", "past_due"}:
        return {
            "allowed": "false",
            "reason": gate_reason,
            "mode": "blocked",
        }
    return {
        "allowed": "false",
        "reason": gate_reason,
        "mode": "blocked",
    }


def get_user_onboarding_state() -> str:
    """
    Vraca stanje onboardinga korisnika:
    - 'unactivated'   : novi korisnik, nije izabrao nista
    - 'trial_active'  : aktivan free trial (jos nije istekao)
    - 'trial_expired' : trial je istekao
    - 'paid'          : platio
    - 'admin'         : admin
    - 'local'         : lokalni mod
    """
    try:
        from billing_models import get_trial_days_remaining_for_email
        email = str(getattr(state, "current_user_email", "") or "").strip()
        if not email:
            return "local"
        billing = get_current_billing_summary()
        if billing is None:
            return "local"
        billing_status = str(billing.get("billing_status", "") or "").strip().lower()
        plan_code = str(billing.get("plan_code", "") or "").strip().lower()
        access_tier = str(billing.get("access_tier", "") or "").strip().lower()
        if access_tier == "admin":
            return "admin"
        if billing_status in {"active", "paid"} and plan_code not in {"", "trial"}:
            return "paid"
        if billing_status == "unactivated":
            return "unactivated"
        if billing_status in {"trial", "trialing", "on_trial"}:
            days = get_trial_days_remaining_for_email(email)
            if days == 0:
                return "trial_expired"
            return "trial_active"
        return "unactivated"
    except Exception:
        return "local"


def activate_free_trial() -> tuple[bool, str]:
    """Aktivira free trial za trenutno ulogovanog korisnika."""
    try:
        from billing_models import activate_free_trial_for_email
        email = str(getattr(state, "current_user_email", "") or "").strip()
        if not email:
            return False, "Nema aktivnog korisnika."
        ok = activate_free_trial_for_email(email)
        if ok:
            return True, "Besplatni probni pristup je aktiviran."
        return False, "Greska pri aktivaciji probnog pristupa."
    except Exception as ex:
        return False, f"Greska: {ex}"


def build_checkout_start_message(plan_code: str = "pro_monthly") -> Tuple[bool, str]:
    try:
        from billing_models import build_checkout_placeholder
        from lemon_squeezy_service import get_billing_runtime_status
        email = str(getattr(state, "current_user_email", "") or "").strip()
        auth_mode = str(getattr(state, "current_auth_mode", "") or "").strip().lower()
        if not email:
            return False, "Nema aktivnog korisnika za billing."
        if auth_mode == "local":
            return False, "Billing nije dostupan za lokalnu fallback sesiju."
        billing = get_billing_runtime_status()
        has_api_key = str(billing.get("has_api_key", "") or "").strip().lower() == "true"
        has_variant = (
            str(billing.get("has_variant_id_weekly", "") or "").strip().lower() == "true"
            or str(billing.get("has_variant_id_monthly", "") or "").strip().lower() == "true"
        )
        if not has_api_key or not has_variant:
            return False, "Lemon Squeezy checkout jos nije konfigurisan za ovo okruzenje."
        return True, build_checkout_placeholder(email, plan_code=str(plan_code or "pro_monthly"))
    except Exception as ex:
        return False, f"Ne mogu da pripremim checkout: {ex}"


def build_customer_portal_message() -> Tuple[bool, str]:
    try:
        from billing_models import build_customer_portal_placeholder
        from lemon_squeezy_service import get_billing_runtime_status
        email = str(getattr(state, "current_user_email", "") or "").strip()
        auth_mode = str(getattr(state, "current_auth_mode", "") or "").strip().lower()
        if not email:
            return False, "Nema aktivnog korisnika za billing portal."
        if auth_mode == "local":
            return False, "Billing portal nije dostupan za lokalnu fallback sesiju."
        billing = get_billing_runtime_status()
        has_api_key = str(billing.get("has_api_key", "") or "").strip().lower() == "true"
        has_store_subdomain = str(billing.get("has_store_subdomain", "") or "").strip().lower() == "true"
        if not has_api_key and not has_store_subdomain:
            return False, "Lemon Squeezy billing portal jos nije konfigurisan za ovo okruzenje."
        return True, build_customer_portal_placeholder(email)
    except Exception as ex:
        return False, f"Ne mogu da pripremim billing portal: {ex}"


def get_release_readiness_summary(target: str = "production") -> Dict[str, Any]:
    try:
        tier = str(getattr(state, "current_access_tier", "") or "").strip().lower()
        if tier != "admin":
            return {
                "target": str(target or "production"),
                "ready": False,
                "error": "admin_only",
                "summary": {"total_checks": 0, "passed": 0, "blockers": 1, "warnings": 0},
                "blockers": [{"label": "admin_only", "detail": "Release readiness summary je dostupan samo administratoru."}],
                "warnings": [],
            }
        from release_readiness import get_release_readiness_report
        return get_release_readiness_report(target=str(target or "production"))
    except Exception as ex:
        return {
            "target": str(target or "production"),
            "ready": False,
            "summary": {"total_checks": 0, "passed": 0, "blockers": 1, "warnings": 0},
            "blockers": [{"label": "readiness_error", "detail": str(ex)}],
            "warnings": [],
        }


def get_ops_runtime_summary() -> Dict[str, Any]:
    try:
        tier = str(getattr(state, "current_access_tier", "") or "").strip().lower()
        if tier != "admin":
            return {
                "error": "admin_only",
                "runtime_health": {
                    "ready": False,
                    "blockers": ["Ops runtime summary je dostupan samo administratoru."],
                    "warnings": [],
                },
            }
        from app_config import get_public_runtime_config
        from export_jobs import get_export_runtime_summary
        from project_store import (
            get_auth_runtime_summary,
            get_billing_event_summary,
            get_export_job_summary,
            get_project_store_runtime_info,
        )
        from lemon_squeezy_service import get_billing_runtime_status
        app_config = get_public_runtime_config()
        project_store = get_project_store_runtime_info()
        export_jobs = get_export_runtime_summary()
        export_job_counts = get_export_job_summary()
        auth_runtime = get_auth_runtime_summary()
        stripe = get_billing_runtime_status()
        blockers: list[str] = []
        warnings: list[str] = []

        if str(project_store.get("production_ready", "")).lower() != "true":
            blockers.append("Storage nije production-ready. SQLite nije finalni backend za vise korisnika.")
        if str(app_config.get("web_workers", "0") or "0").strip() in ("", "0"):
            warnings.append("WEB_WORKERS je 0, pa app i dalje radi u development-style single worker modu.")
        if str(export_jobs.get("mode", "")).lower() == "dedicated_process" and str(export_jobs.get("worker_alive", "")).lower() != "true":
            blockers.append("Dedicated export worker je podesen, ali heartbeat nije aktivan.")
        elif str(export_jobs.get("production_ready", "")).lower() != "true":
            warnings.append("Export i dalje radi u app procesu; za ozbiljniji scale treba izdvojen worker servis.")
        if str(stripe.get("has_api_key", "")).lower() != "true":
            warnings.append("Lemon Squeezy API key nije povezan.")
        if str(stripe.get("has_webhook_secret", "")).lower() != "true":
            warnings.append("Lemon Squeezy webhook secret nije povezan.")
        if int(auth_runtime.get("active_reset_tokens", 0)) > 20:
            warnings.append("Ima previse aktivnih reset tokena; proveri auth cleanup tok.")
        if int(auth_runtime.get("failed_login_attempts", 0)) > 50:
            warnings.append("Ima mnogo failed login attempt zapisa; proveri rate limit i auth cleanup.")
        return {
            "app_config": app_config,
            "project_store": project_store,
            "auth_runtime": auth_runtime,
            "export_jobs": export_jobs,
            "export_job_counts": export_job_counts,
            "stripe": stripe,
            "billing_events": get_billing_event_summary(),
            "runtime_health": {
                "ready": not blockers,
                "blockers": blockers,
                "warnings": warnings,
            },
        }
    except Exception as ex:
        return {"error": str(ex)}


def get_visible_audit_logs(limit: int = 20) -> List[Dict[str, Any]]:
    try:
        from project_store import list_recent_audit_logs
        tier = str(getattr(state, "current_access_tier", "") or "").strip().lower()
        user_id = int(getattr(state, "current_user_id", 0) or 0)
        if tier == "admin":
            rows = list_recent_audit_logs(limit=limit)
        elif user_id > 0:
            rows = list_recent_audit_logs(user_id=user_id, limit=limit)
        else:
            rows = []
        return [
            {
                "created_at": str(row.created_at),
                "event_type": str(row.event_type),
                "status": str(row.status),
                "detail": str(row.detail),
            }
            for row in rows
        ]
    except Exception as ex:
        return [{"created_at": "-", "event_type": "ops.error", "status": "warning", "detail": str(ex)}]


def get_visible_users(limit: int = 200) -> List[Dict[str, Any]]:
    try:
        from project_store import list_users

        tier = str(getattr(state, "current_access_tier", "") or "").strip().lower()
        if tier != "admin":
            return []
        rows = list_users(limit=limit)
        return [
            {
                "email": str(row.email),
                "username": str(getattr(row, "username", "") or ""),
                "display_name": str(row.display_name),
                "auth_mode": str(row.auth_mode),
                "access_tier": str(row.access_tier),
                "status": str(row.status),
                "email_verified": "yes" if bool(row.email_verified) else "no",
                "created_at": str(row.created_at),
                "updated_at": str(row.updated_at),
            }
            for row in rows
        ]
    except Exception as ex:
        return [{
            "email": "-",
            "username": "-",
            "display_name": "ops.error",
            "auth_mode": "-",
            "access_tier": "-",
            "status": str(ex),
            "email_verified": "-",
            "created_at": "-",
            "updated_at": "-",
        }]


def save_project_json() -> bytes:
    """
    Serijalizuje trenutni projekat u JSON bytes.
    Format:
      {
        "_version":             "1.0",
        "_app":                 "KrojnaListaPRO",
        "_saved_at":            "2026-03-02T14:35:00",
        "kitchen":              { ... },
        "zone_depth_standards": { ... },
        "next_id":              42
      }
    """
    payload: Dict[str, Any] = {
        "_version":             _SAVE_VERSION,
        "_app":                 _SAVE_APP,
        "_saved_at":            datetime.now().isoformat(timespec="seconds"),
        "project_type":         str(getattr(state, "project_type", "kitchen")),
        "kitchen_layout":       str(getattr(state, "kitchen_layout", "jedan_zid")),
        "l_corner_side":        str(getattr(state, "l_corner_side", "right")),
        "room_setup_done":      bool(getattr(state, "room_setup_done", False)),
        "language":             str(getattr(state, "language", "sr") or "sr"),
        "room":                 copy.deepcopy(getattr(state, "room", {})),
        "wardrobe_profile":     str(getattr(state, "wardrobe_profile", "standard")),
        "wardrobe_to_ceiling":  bool(getattr(state, "wardrobe_to_ceiling", True)),
        "wardrobe_door_mode":   str(getattr(state, "wardrobe_door_mode", "hinged")),
        "wardrobe_target_wall": str(getattr(state, "wardrobe_target_wall", "A")).upper(),
        "kitchen":              copy.deepcopy(state.kitchen),
        "zone_depth_standards": dict(state.zone_depth_standards),
        "next_id":              int(state.next_id),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def load_project_json(data: bytes) -> Tuple[bool, str]:
    """
    Učitava projekat iz JSON bytes.
    Vraća (True, "") ako uspešno, ili (False, poruka_greške) ako ne.
    State se mijenja SAMO ako je sve OK.
    """
    # ── 1. Parse ──────────────────────────────────────────────────────────────
    try:
        payload = json.loads(data.decode("utf-8"))
    except Exception as exc:
        return False, f"Nije validan JSON fajl: {exc}"

    if not isinstance(payload, dict):
        return False, "Fajl nema ispravan format (očekivan JSON objekat)."

    # Legacy fallback:
    # 1) fajl je direktan "kitchen" objekat (bez wrapper-a)
    # 2) fajl ima "kitchen", ali nema _app potpis starije verzije
    if "_app" not in payload:
        if isinstance(payload.get("modules"), list):
            payload = {
                "_version": _SAVE_VERSION,
                "_app": _SAVE_APP,
                "project_type": payload.get("project_type", "kitchen"),
                "kitchen": payload,
                "zone_depth_standards": getattr(state, "zone_depth_standards", {
                    "base": 560, "wall": 320, "wall_upper": 300, "tall": 560, "tall_top": 560,
                }),
                "next_id": payload.get("next_id", 1),
            }
        elif isinstance(payload.get("kitchen"), dict):
            payload["_app"] = _SAVE_APP
            payload.setdefault("_version", _SAVE_VERSION)

    # ── 2. Validacija identiteta ───────────────────────────────────────────────
    if payload.get("_app") != _SAVE_APP:
        found = payload.get("_app", "nepoznato")
        return False, f"Fajl nije KrojnaListaPRO projekat (pronađeno: '{found}')."

    version = str(payload.get("_version", ""))
    if not version:
        return False, "Fajl ne sadrži version informaciju."

    # ── 3. Validacija kitchen objekta ─────────────────────────────────────────
    kitchen = payload.get("kitchen")
    if not isinstance(kitchen, dict):
        return False, "Fajl ne sadrži validan 'kitchen' objekat."

    # modules mora biti lista (može biti prazna)
    if not isinstance(kitchen.get("modules", []), list):
        return False, "Fajl sadrži neispravan 'modules' format."

    # ── 4. project_type (backward compat) ────────────────────────────────────
    project_type = _normalize_project_type(payload.get("project_type", ""))
    if project_type == "kitchen":
        project_type = _normalize_project_type(kitchen.get("project_type", ""))

    # ── 5. zone_depth_standards (backward compat — default ako nedostaje) ─────
    _zds_defaults: Dict[str, int] = {
        "base": 560, "wall": 320, "wall_upper": 300, "tall": 560, "tall_top": 560,
    }
    zds = payload.get("zone_depth_standards", _zds_defaults)
    if not isinstance(zds, dict):
        zds = _zds_defaults

    # ── 6. next_id ────────────────────────────────────────────────────────────
    next_id = payload.get("next_id", None)
    if not isinstance(next_id, int) or next_id < 1:
        # Izračunaj iz maksimalnog id-a u modulima + 1
        mods_ids = [int(m.get("id", 0)) for m in (kitchen.get("modules", []) or [])]
        next_id = (max(mods_ids) if mods_ids else 0) + 1

    # ── 6b. wardrobe setup (backward compat) ─────────────────────────────────
    _wardrobe_profile = str(payload.get("wardrobe_profile", "standard") or "standard").lower()
    if _wardrobe_profile not in ("standard", "american", "corner"):
        _wardrobe_profile = "standard"
    _wardrobe_to_ceiling = bool(payload.get("wardrobe_to_ceiling", True))
    _wardrobe_door_mode = str(payload.get("wardrobe_door_mode", "hinged") or "hinged").lower()
    if _wardrobe_door_mode not in ("hinged", "sliding"):
        _wardrobe_door_mode = "hinged"
    _wardrobe_target_wall = str(payload.get("wardrobe_target_wall", "A") or "A").upper()
    if _wardrobe_target_wall not in ("A", "B", "C"):
        _wardrobe_target_wall = "A"

    # ── 7. Sve OK — ažuriraj state ────────────────────────────────────────────
    state.kitchen              = copy.deepcopy(kitchen)
    for _m in (state.kitchen.get("modules", []) or []):
        _wk = str(_m.get("wall_key", "A") or "A").upper()
        if _wk not in ("A", "B", "C", "D", "E", "F"):
            _wk = "A"
        _m["wall_key"] = _wk
    state.project_type         = project_type
    state.kitchen["project_type"] = state.project_type
    _saved_language = str(payload.get("language", "sr") or "sr").lower().strip()
    state.language = _saved_language if _saved_language in ("sr", "en") else "sr"

    # kitchen_layout + l_corner_side (backward compat: čitaj iz kitchen ako nedostaje)
    _saved_layout = str(payload.get("kitchen_layout", "") or "").lower().strip()
    if not _saved_layout:
        _saved_layout = str(state.kitchen.get("layout", "jedan_zid") or "jedan_zid").lower().strip()
    if _saved_layout not in ("jedan_zid", "l_oblik", "u_oblik", "galija"):
        _saved_layout = "jedan_zid"
    state.kitchen_layout        = _saved_layout
    state.kitchen["layout"]     = _saved_layout

    _saved_corner = str(payload.get("l_corner_side", state.kitchen.get("l_corner_side", "right")) or "right").lower()
    if _saved_corner not in ("right", "left"):
        _saved_corner = "right"
    state.l_corner_side         = _saved_corner
    state.kitchen["l_corner_side"] = _saved_corner

    # room (otvori, instalacije, zidne dimenzije) — backward compat
    _saved_room = payload.get("room", None)
    if isinstance(_saved_room, dict) and _saved_room.get("walls"):
        state.room = copy.deepcopy(_saved_room)
    else:
        # Stari fajl bez room: inicijalizuj iz kitchen.wall dimenzija
        _wall_len = int((state.kitchen.get("wall", {}) or {}).get("length_mm", 3000))
        _wall_h   = int((state.kitchen.get("wall", {}) or {}).get("height_mm", 2600))
        state.room = _default_room()
        state.room["wall_length_mm"] = _wall_len
        state.room["wall_height_mm"] = _wall_h
        for _w in state.room.get("walls", []):
            _w["length_mm"] = _wall_len if _w.get("key") == "A" else 3000
            _w["height_mm"] = _wall_h

    state.room_setup_done       = bool(payload.get("room_setup_done", True))

    state.wardrobe_profile     = _wardrobe_profile
    state.wardrobe_to_ceiling  = _wardrobe_to_ceiling
    state.wardrobe_door_mode   = _wardrobe_door_mode
    state.wardrobe_target_wall = _wardrobe_target_wall
    if not isinstance(state.kitchen.get("front_color"), str) or not str(state.kitchen.get("front_color")).strip():
        state.kitchen["front_color"] = "#FDFDFB"
    state.front_color          = str(state.kitchen.get("front_color", "#FDFDFB"))
    state.zone_depth_standards = {**_zds_defaults, **{str(k): int(v) for k, v in zds.items()}}
    state.next_id              = int(next_id)

    # Recompute zones (visine, gap-ovi) za slučaj starih fajlova
    state.kitchen["zones"] = _compute_zones(state.kitchen)

    # Resetuj UI state (selekcija, edit panel, itd.)
    state.selected_tid       = ""
    state.measurement_mode   = "standard"
    state.selected_edit_id   = 0
    state.mode               = "add"
    state.sidebar_tab        = "dodaj"
    state.active_tab         = "elementi"
    write_autosave_snapshot(reason="load_project")

    return True, ""


def _set_language(lang: str) -> None:
    state.language = normalize_language_code(lang)
