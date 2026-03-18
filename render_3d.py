# -*- coding: utf-8 -*-
from __future__ import annotations

import math
import logging
from typing import Any, Callable
from visualization import _y_for_wall_upper, _y_for_tall_top
from layout_engine import _l_corner_offsets_mm

_LOG = logging.getLogger(__name__)

TEMPLATE_OPEN = {
    'BASE_OPEN', 'WALL_OPEN', 'TALL_OPEN', 'TALL_TOP_OPEN', 'WALL_UPPER_OPEN',
}
TEMPLATE_GLASS = {'WALL_GLASS'}
TEMPLATE_DRAWERS = {'BASE_DRAWERS', 'BASE_DRAWERS_3'}
TEMPLATE_DOOR_DRAWER = {'BASE_DOOR_DRAWER'}
TEMPLATE_SINK = {'SINK_BASE'}
TEMPLATE_FRIDGE = {'TALL_FRIDGE', 'TALL_FRIDGE_FREEZER', 'TALL_FRIDGE_FREESTANDING'}
TEMPLATE_APPLIANCE = {
    'BASE_OVEN', 'BASE_DISHWASHER', 'BASE_DISHWASHER_FREESTANDING',
    'BASE_COOKING_UNIT', 'BASE_OVEN_HOB_FREESTANDING',
    'WALL_HOOD', 'WALL_MICRO', 'TALL_OVEN_MICRO', 'TALL_OVEN',
}
TEMPLATE_CORNER = {'BASE_CORNER', 'WALL_CORNER', 'BASE_CORNER_DIAGONAL', 'WALL_CORNER_DIAGONAL'}
TEMPLATE_DOOR2 = {
    'BASE_2DOOR', 'BASE_DOORS', 'WALL_2DOOR', 'WALL_DOORS',
    'TALL_DOORS', 'TALL_TOP_DOORS', 'WALL_UPPER_2DOOR',
}
TEMPLATE_DOOR1 = {
    'BASE_1DOOR', 'BASE_NARROW', 'WALL_1DOOR', 'WALL_NARROW',
    'WALL_UPPER_1DOOR',
}
TEMPLATE_LIFTUP = {'WALL_LIFTUP'}


def _hex_to_rgb(c: str) -> tuple[int, int, int]:
    c = str(c or "").strip().lstrip("#")
    if len(c) != 6:
        return (170, 184, 198)
    try:
        return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))
    except Exception as ex:
        _LOG.debug("Invalid hex color '%s': %s", c, ex)
        return (170, 184, 198)


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    r = max(0, min(255, int(rgb[0])))
    g = max(0, min(255, int(rgb[1])))
    b = max(0, min(255, int(rgb[2])))
    return f"#{r:02x}{g:02x}{b:02x}"


def _shade(c: str, factor: float) -> str:
    r, g, b = _hex_to_rgb(c)
    return _rgb_to_hex((r * factor, g * factor, b * factor))


def to_scene_coords(
    x_mm: float,
    y_mm: float,
    d_mm: float,
    w_mm: float,
    h_mm: float,
    on_left_wall: bool,
    s: float,
) -> tuple[float, float, float, float, float, float]:
    """Pretvara mm koordinate jednog modula u scene koordinate.

    Jedinstven koordinatni sistem za sve zidove — nema duplirane transformacione logike.

    on_left_wall=False  →  Zid A (zadnji zid):
        scene_x = (x_mm + w_mm/2) * s   — pozicija duž zadnjeg zida
        scene_y = y_mm * s               — vertikala (ista za oba zida)
        scene_z = (d_mm / 2) * s         — dubina od zadnjeg zida prema kameri
        box     = (w_mm*s, h_mm*s, d_mm*s)

    on_left_wall=True   →  Zid B (levi zid, x↔z zamena):
        scene_x = (d_mm / 2) * s         — dubina od levog zida prema desno
        scene_y = y_mm * s               — vertikala
        scene_z = (x_mm + w_mm/2) * s   — pozicija duž levog zida (u Z pravcu)
        box     = (d_mm*s, h_mm*s, w_mm*s)

    Vraća (cx, cy, cz, box_w, box_h, box_d) — sve u scene jedinicama.
    """
    cy = float(y_mm) * s
    if not on_left_wall:
        cx  = (float(x_mm) + float(w_mm) / 2.0) * s
        cz  = float(d_mm) / 2.0 * s
        bw  = float(w_mm) * s
        bh  = float(h_mm) * s
        bd  = float(d_mm) * s
    else:
        # x↔z zamena: x_mm ide duž Z ose, d_mm ide duž X ose
        cx  = float(d_mm) / 2.0 * s
        cz  = (float(x_mm) + float(w_mm) / 2.0) * s
        bw  = float(d_mm) * s
        bh  = float(h_mm) * s
        bd  = float(w_mm) * s
    return cx, cy, cz, bw, bh, bd


def _lock_scene_to_horizontal_orbit(
    ui: Any,
    scene: Any,
    *,
    cam_x: float,
    cam_y: float,
    cam_z: float,
    target_x: float,
    target_y: float,
    target_z: float,
    polar_angle: float = 1.40,
    delay_s: float = 0.25,
) -> None:
    """Postavi kameru i zaključaj OrbitControls na horizontalnu rotaciju.

    JavaScript atomski:
    1. Nađe OrbitControls
    2. Postavi ctrl.target (centar orbitanja = kuhinjski zid)
    3. Postavi camera.position na našu Python-izračunatu poziciju
    4. Sinhronizuje OrbitControls internu sfernu reprezentaciju (ctrl.update)
    5. Zaključa polar kut na izračunati opseg
    6. Onemogući pan
    """
    try:
        _dom_id = f"c{int(getattr(scene, 'id', 0))}"
    except Exception:
        _dom_id = ""
    if not _dom_id:
        return
    _cx  = round(float(cam_x), 5)
    _cy  = round(float(cam_y), 5)
    _cz  = round(float(cam_z), 5)
    _tx  = round(float(target_x), 5)
    _ty  = round(float(target_y), 5)
    _tz  = round(float(target_z), 5)
    _pa  = round(float(polar_angle), 5)
    _js = rf"""(function(){{
        const root = document.getElementById('{_dom_id}');
        if (!root) return;
        function applyLock(tries) {{
            let ctrl = null, el = root;
            for (let i = 0; i < 28 && el; i++) {{
                const vc = el._vueParentComponent;
                if (vc && vc.setupState) {{
                    ctrl = vc.setupState.controls;
                    if (ctrl && ctrl.value !== undefined) ctrl = ctrl.value;
                    if (ctrl && typeof ctrl.getPolarAngle === 'function') break;
                    ctrl = null;
                }}
                el = el.parentElement;
            }}
            if (!ctrl) {{
                if (tries > 0) setTimeout(() => applyLock(tries - 1), 250);
                return;
            }}
            // 1) Postavi target (centar orbitanja = kuhinjski zid)
            ctrl.target.set({_tx}, {_ty}, {_tz});
            // 2) Direktno postavi poziciju kamere (zaobilazi NiceGUI async problem)
            const cam = ctrl.object;
            cam.position.set({_cx}, {_cy}, {_cz});
            cam.up.set(0, 1, 0);
            cam.lookAt({_tx}, {_ty}, {_tz});
            // 3) Sinhronizuj OrbitControls interne sferne koordinate sa novom pozicijom
            ctrl.update();
            // 4) Zaključaj vertikalni kut — dozvoli ±18° oko željenog polar kuta
            const margin = 0.30;
            ctrl.minPolarAngle = Math.max(0.05, {_pa} - margin);
            ctrl.maxPolarAngle = Math.min(Math.PI - 0.05, {_pa} + margin);
            ctrl.enablePan = false;
            ctrl.screenSpacePanning = false;
            ctrl.enableZoom = true;
            // 5) Još jedan update da primijeni nova ograničenja
            ctrl.update();
        }}
        applyLock(22);
    }})();"""
    ui.timer(delay_s, lambda: ui.run_javascript(_js), once=True)


def _move_camera_y_up(
    scene: Any,
    *,
    x: float,
    y: float,
    z: float,
    look_at_x: float,
    look_at_y: float,
    look_at_z: float,
) -> None:
    """Move camera with world-up aligned to positive Y (standard room orientation)."""
    scene.move_camera(
        x=x,
        y=y,
        z=z,
        look_at_x=look_at_x,
        look_at_y=look_at_y,
        look_at_z=look_at_z,
        up_x=0.0,
        up_y=1.0,
        up_z=0.0,
    )


def _enhance_scene_lighting(
    ui: Any,
    scene: Any,
    w: float,
    h: float,
    d: float,
    delay_s: float = 0.55,
) -> None:
    """Dodaje Three.js svjetla u scenu: ambient + hemisferno + 2x direktno.

    Zamjenjuje NiceGUI default osvjetljenje boljim, toplim setom koji daje
    realističniji izgled kuhinjskim elementima.
    """
    try:
        _dom_id = f"c{int(getattr(scene, 'id', 0))}"
    except Exception:
        _dom_id = ""
    if not _dom_id:
        return
    _wx = round(float(w), 4)
    _hx = round(float(h), 4)
    _dx = round(float(d), 4)
    _js = rf"""(function(){{
        const root = document.getElementById('{_dom_id}');
        if (!root) return;
        const W={_wx}, H={_hx}, D={_dx};
        function applyLights(tries) {{
            // Pronađi Three.js scenu kroz Vue komponentu
            let sc3 = null, vcf = null, el = root;
            for (let i = 0; i < 25 && el; i++) {{
                const vc = el._vueParentComponent;
                if (vc && vc.setupState) {{
                    let s = vc.setupState.scene || vc.setupState.threeScene;
                    if (s && s.value !== undefined) s = s.value;
                    if (s && s.isScene) {{ sc3 = s; vcf = vc; break; }}
                }}
                el = el.parentElement;
            }}
            if (!sc3) {{
                if (tries > 0) setTimeout(() => applyLights(tries - 1), 200);
                return;
            }}
            // Pronađi THREE global
            const T = window.THREE
                || (vcf && vcf.setupState && vcf.setupState.THREE)
                || (vcf && vcf.appContext && vcf.appContext.config
                    && vcf.appContext.config.globalProperties
                    && vcf.appContext.config.globalProperties.THREE);
            if (!T) {{
                if (tries > 0) setTimeout(() => applyLights(tries - 1), 300);
                return;
            }}
            // Ukloni stara svjetla
            const old = [];
            sc3.traverse(o => {{ if (o.isLight) old.push(o); }});
            old.forEach(l => sc3.remove(l));
            // 1) Ambijentalno — puni sjene (mekano, neutralno bijelo)
            sc3.add(new T.AmbientLight(0xffffff, 0.42));
            // 2) Hemisferno — toplo tlo + hladniji plafon
            sc3.add(new T.HemisphereLight(0xEEF2FF, 0xE4CDA6, 0.50));
            // 3) Glavno direktno — lijevo-gore ispred (toplo, imitira prozor)
            const sun = new T.DirectionalLight(0xFFF8F0, 1.05);
            sun.position.set(W * 0.25, H * 1.70, D * 0.90);
            sc3.add(sun);
            // 4) Fill — desna strana, blaže (neutralizuje tvrde sjene)
            const fill = new T.DirectionalLight(0xF2F5FF, 0.30);
            fill.position.set(W * 0.90, H * 0.70, D * 0.60);
            sc3.add(fill);
        }}
        applyLights(28);
    }})();"""
    ui.timer(delay_s, lambda: ui.run_javascript(_js), once=True)


def render_kitchen_elements_scene_3d(
    *,
    ui: Any,
    state: Any,
    main_content_refresh: Callable[[], None],
    wall_len_h: Callable[[dict], tuple[int, int]],
    zone_baseline_and_height: Callable[[dict, str], tuple[int, int]],
    get_zone_depth_standard: Callable[[str], int],
) -> None:
    """Render 3D scene for kitchen elements tab."""
    def _fnum(val: Any, default: float = 0.0) -> float:
        try:
            return float(val)
        except Exception:
            return float(default)

    _active_wall = str(
        (getattr(state, 'room', {}) or {}).get('active_wall',
            (getattr(state, 'room', {}) or {}).get('kitchen_wall', 'A')) or 'A'
    ).upper()
    try:
        _walls = list((getattr(state, 'room', {}) or {}).get('walls', []) or [])
        _wall = next((ww for ww in _walls if str(ww.get('key', '')).upper() == _active_wall), None)
        if _wall is not None:
            state.kitchen.setdefault('wall', {})
            state.kitchen['active_wall_key'] = _active_wall
            state.kitchen.setdefault('wall_lengths_mm', {})[_active_wall] = int(_wall.get('length_mm', state.kitchen.get('wall', {}).get('length_mm', 3000)) or 3000)
            state.kitchen.setdefault('wall_heights_mm', {})[_active_wall] = int(_wall.get('height_mm', state.kitchen.get('wall', {}).get('height_mm', 2600)) or 2600)
            state.kitchen['wall']['length_mm'] = int(_wall.get('length_mm', state.kitchen.get('wall', {}).get('length_mm', 3000)) or 3000)
            state.kitchen['wall']['height_mm'] = int(_wall.get('height_mm', state.kitchen.get('wall', {}).get('height_mm', 2600)) or 2600)
    except Exception:
        pass

    # U 3D prikazu koristimo jedinstven "room preview" stil kao u referenci.
    _is_technical = False
    _wl, _wh = wall_len_h(state.kitchen)
    _depth = int(state.room.get('room_depth_mm', 3000) if getattr(state, 'room', None) else 3000)
    s = 0.01
    w = float(_wl) * s
    h = float(_wh) * s
    d = float(_depth) * s
    with ui.scene(width=1200, height=760, grid=False).classes('w-full h-full') as sc:
        _bg = '#ECECEC'
        _floor_col = '#E4CDA6'
        _wall_a = '#DCDCDC'
        _wall_b = '#D7D7D7'
        _wall_c = '#D7D7D7'
        _floor_t = 0.10
        _wall_t = 0.10
        sc.background_color = _bg
        sc.box(w, _floor_t, d).move(w / 2, -_floor_t / 2, d / 2).material(_floor_col)
        # Suptilne drvene trake poda za realniji izgled
        _planks = max(18, int(d / 0.22))
        _pz = d / _planks
        for _i in range(_planks):
            _tone = '#D8BE94' if (_i % 2 == 0) else '#EAD5B3'
            sc.box(w * 0.996, 0.0035, max(0.02, _pz * 0.90)).move(
                w / 2, -0.001, (_i + 0.5) * _pz
            ).material(_tone, opacity=0.65)
        # Zadnji + bočni zidovi sa realnijom debljinom
        sc.box(w, h, _wall_t).move(w / 2, h / 2, _wall_t / 2).material(_wall_a, opacity=0.97)
        sc.box(_wall_t, h, d).move(-_wall_t / 2, h / 2, d / 2).material(_wall_b, opacity=0.94)
        sc.box(_wall_t, h, d).move(w + _wall_t / 2, h / 2, d / 2).material(_wall_c, opacity=0.92)
        # Sokla uz zidove
        _sk_h = 0.06
        _sk_t = 0.016
        sc.box(w, _sk_h, _sk_t).move(w / 2, _sk_h / 2, _wall_t + _sk_t / 2).material('#C5C5C5', opacity=0.95)
        sc.box(_sk_t, _sk_h, d).move(_wall_t + _sk_t / 2, _sk_h / 2, d / 2).material('#C2C2C2', opacity=0.92)
        sc.box(_sk_t, _sk_h, d).move(w - _sk_t / 2, _sk_h / 2, d / 2).material('#C2C2C2', opacity=0.92)
        # Bez tehničkih natpisa i pomoćnih linija u ovom režimu.

        # Za L-kuhinju Zid B/C: ne koristimo glavni render (koji uvek crta na zadnji zid).
        # Zid B elementi se crtaju u L-kontekst sekciji sa ispravnom x↔z zamenom,
        # tako da se pojavljuju na levom zidu scene, a ne na zadnjem.
        _is_l_main = (
            str(getattr(state, 'kitchen_layout', state.kitchen.get('layout', '')) or '')
            .lower().strip() == 'l_oblik'
        )
        if _is_l_main and _active_wall != 'A':
            _mods_all = []  # Zid B se crta u L-kontekst sekciji ispod
        else:
            _mods_all = [
                m for m in (state.kitchen.get('modules', []) or [])
                if str(m.get('wall_key', 'A')).upper() == _active_wall
            ]
        _mods = [m for m in _mods_all if str(m.get('zone', '')).lower().strip() not in ('tall_top', 'wall_upper')]
        _mods += [m for m in _mods_all if str(m.get('zone', '')).lower().strip() == 'tall_top']
        _mods += [m for m in _mods_all if str(m.get('zone', '')).lower().strip() == 'wall_upper']
        _worktop_segments: list[tuple[float, float, float, float]] = []
        for _m in _mods:
            _x = _fnum(_m.get('x_mm', 0), 0.0)
            _w = _fnum(_m.get('w_mm', 0), 0.0)
            _h = _fnum(_m.get('h_mm', 0), 0.0)
            _z = str(_m.get('zone', 'base')).lower()
            _tid = str(_m.get('template_id', '') or _m.get('id_template', '') or '').upper()
            _lbl = str(_m.get('label', '')).upper()
            _d_mm = _fnum(_m.get('d_mm', 0) or 0, 0.0)
            if _d_mm <= 0:
                _d_mm = _fnum(get_zone_depth_standard(_z) or 560, 560.0)
            try:
                if _z == 'wall_upper':
                    _y0 = int(_y_for_wall_upper(state.kitchen, _m, _mods_all))
                elif _z == 'tall_top':
                    _y0 = int(_y_for_tall_top(state.kitchen, _m, _mods_all))
                else:
                    _y0, _ = zone_baseline_and_height(state.kitchen, _z)
            except Exception as ex:
                _LOG.debug("3D baseline resolve failed (zone=%s, id=%s): %s", _z, _m.get('id', -1), ex)
                _y0 = 0
            # Sudopera ima vlastitu inox ploču — isključi je iz globalnog radnog stola
            _is_sink_chk = ('SINK' in _tid) or ('SUDOPER' in _lbl)
            if _z == 'base' and not _is_sink_chk:
                _worktop_segments.append((_x, _w, float(_y0), _h))

            _bx = (_x + _w / 2.0) * s
            _by = (float(_y0) + _h / 2.0) * s
            _bz = (_d_mm / 2.0) * s
            _front_z = (_d_mm * s) - 0.002

            # Boja fronta: 1) per-modul params, 2) globalni front_color, 3) default bijela
            _global_front = str(
                state.kitchen.get('front_color', getattr(state, 'front_color', '#F5F4F1')) or '#F5F4F1'
            )
            _m_front_raw = str((_m.get('params') or {}).get('front_color') or '').strip()
            _front_c = _m_front_raw if _m_front_raw.startswith('#') else _global_front
            if not _front_c.startswith('#'):
                _front_c = '#F5F4F1'
            # Korpus je uvijek neutralno bijel/krem — kontrast prema frontu
            _carcass_c = '#ECEAE6'
            _side_c = _shade(_carcass_c, 0.88)   # bočna sjena
            _top_c = _shade(_carcass_c, 0.92)     # gornja ploča
            # Ručke: tamnosivi inox profil — čitljiv na bilo kojoj boji fronta
            _handle_c = '#404850'
            _handle_hi = '#D0D8DF'
            _shadow_c = '#5F6772'
            _edge_c = '#707780'
            _inox_light = '#cfd5db'
            _inox_mid = '#aeb6bf'
            _inox_dark = '#7e8791'

            _is_open = (_tid in TEMPLATE_OPEN) or ('OPEN' in _tid) or ('OTVOR' in _lbl)
            _is_glass = (_tid in TEMPLATE_GLASS) or ('GLASS' in _tid) or ('STAK' in _lbl)
            _is_door_drawer = (_tid in TEMPLATE_DOOR_DRAWER)
            _is_drawer = (not _is_door_drawer) and (
                (_tid in TEMPLATE_DRAWERS) or ('DRAWER' in _tid) or ('FIOK' in _lbl)
            )
            _is_sink = (_tid in TEMPLATE_SINK) or ('SINK' in _tid) or ('SUDOPER' in _lbl)
            _is_cooking_unit = ('COOKING_UNIT' in _tid)
            _is_oven = ('OVEN' in _tid) or ('RERN' in _lbl)
            _is_hob = ('HOB' in _tid) or ('PLOCA' in _lbl) or ('PLOČA' in _lbl)
            _is_fridge = (_tid in TEMPLATE_FRIDGE) or (
                ('FRIDGE' in _tid) or ('FREEZER' in _tid) or ('FRIZ' in _lbl) or
                ('FRIŽ' in _lbl) or ('ZAMRZ' in _lbl)
            )
            _is_dish = ('DISHWASHER' in _tid) or ('SUDOV' in _lbl) or ('MASIN' in _lbl) or ('MAŠIN' in _lbl)
            # NOTE:
            # `independent_depth` nije pouzdan indikator "aparata" za bojenje fronta.
            # Ako se koristi ovde, neki klasicni ormari mogu pogresno postati inox-sivi.
            # Appliance status odredjujemo samo po tipu/template-u.
            _is_appliance = bool((_tid in TEMPLATE_APPLIANCE) or _is_fridge or _is_oven or _is_hob or _is_dish)
            _is_corner = (_tid in TEMPLATE_CORNER) or ('CORNER' in _tid) or ('COSK' in _lbl) or ('ĆOŠ' in _lbl)
            _is_tall = _z == 'tall'
            _is_wall = _z in ('wall', 'wall_upper')
            _is_liftup = (_tid in TEMPLATE_LIFTUP)

            # Otvoreni elementi: boja vidljivih ploča = front_c per-elementa.
            # Ako korisnik nije postavio zasebnu boju (ostala default bijela), padamo na toplu drvo nijansu.
            if _is_open and not _is_technical:
                _white_defaults = {'#F5F4F1', '#FFFFFF', '#ffffff', '#f5f4f1', '#F5F5F5', '#f5f5f5'}
                _open_base = _front_c if _front_c not in _white_defaults else '#D5C8B4'
                _carcass_c = _open_base
                _side_c = _shade(_carcass_c, 0.82)
                _top_c = _shade(_carcass_c, 0.90)

            # Base shadow
            sc.box((_w + 24) * s, 0.012, (_d_mm + 20) * s).move(
                _bx,
                (float(_y0) * s) - 0.004,
                (_d_mm * 0.5 * s) + 0.02,
            ).material(_shadow_c, opacity=0.08 if _is_technical else 0.22)

            if _is_open:
                # ── OTVORENI ORMAR: 5 odvojenih panela bez prednjeg — vidljiva unutrašnjost ──
                _pt = 18.0 * s                                       # debljina ploče (scene jedinice)
                _bc = '#AEAAA4' if not _is_technical else '#c4cad1'  # leđna ploča — siva
                _side_sh = _shade(_carcass_c, 0.84)
                _top_sh  = _shade(_carcass_c, 0.93)
                _bot_sh  = _shade(_carcass_c, 0.77)
                # Desna bočna ploča
                _carcass = sc.box(_pt, _h * s, _d_mm * s).move(
                    (_bx + (_w * s / 2)) - _pt / 2, _by, _bz
                ).material(_side_sh, opacity=1.0)
                # Leva bočna ploča
                sc.box(_pt, _h * s, _d_mm * s).move(
                    (_bx - (_w * s / 2)) + _pt / 2, _by, _bz
                ).material(_side_sh, opacity=1.0)
                # Gornja ploča
                sc.box(_w * s, _pt, _d_mm * s).move(
                    _bx, (_by + (_h * s / 2)) - _pt / 2, _bz
                ).material(_top_sh, opacity=1.0)
                # Donja ploča
                sc.box(_w * s, _pt, _d_mm * s).move(
                    _bx, (_by - (_h * s / 2)) + _pt / 2, _bz
                ).material(_bot_sh, opacity=1.0)
                # Leđna ploča (siva — kontrast i vizuelna dubina)
                sc.box(_w * s, _h * s, 8.0 * s).move(
                    _bx, _by, 4.0 * s
                ).material(_bc, opacity=1.0)
            else:
                # ── ZATVORENI ORMAR: solidan korpus boks ──
                _carcass = sc.box(_w * s, _h * s, _d_mm * s).move(_bx, _by, _bz).material(_carcass_c, opacity=1.0)
                # Gornja ploča korporusa (suptilna)
                sc.box((_w - 6) * s, 0.005, (_d_mm - 8) * s).move(
                    _bx,
                    (_by + (_h * s / 2)) - 0.002,
                    _bz,
                ).material(_top_c, opacity=0.50)
                # Bočna sjena desno — 3D dubina
                sc.box(0.014, (_h - 4) * s, (_d_mm - 4) * s).move(
                    (_bx + (_w * s / 2)) - 0.007,
                    _by,
                    _bz,
                ).material(_shade(_carcass_c, 0.65), opacity=0.90)
                # Tamna vertikalna linija na lijevoj ivici — razdvaja susjedne elemente
                sc.box(0.010, (_h - 2) * s, 0.020).move(
                    (_bx - (_w * s / 2)) + 0.005,
                    _by,
                    _front_z + 0.002,
                ).material('#2E3440', opacity=0.55)
                # Tamna horizontalna linija pri dnu fronta
                sc.box((_w - 4) * s, 0.008, 0.014).move(
                    _bx,
                    (_by - (_h * s / 2)) + 0.005,
                    _front_z + 0.010,
                ).material('#2E3440', opacity=0.45)

            # Toe kick (plintha) ispod donjih elemenata — prostire se od poda do dna korpusa
            if _z == 'base' and float(_y0) > 0:
                sc.box((_w - 10) * s, float(_y0) * s, 0.035).move(
                    _bx,
                    (float(_y0) / 2.0) * s,
                    (_d_mm * s) - 0.012,
                ).material('#7a7a7a' if not _is_technical else '#c8cdd3', opacity=0.96)

            # Front composition
            if _is_open:
                # Police unutar otvorenog ormara (paneli i leđna ploča su nacrtani gore)
                _thk = 18.0
                _back_thk = 8.0
                _inner_w = max(40.0, _w - 2.0 * _thk)
                _shelf_c = _carcass_c
                _shelf_edge_c = _shade(_carcass_c, 0.72)            # tamnija prednja ivica police
                _shelves = int(((_m.get('params') or {}).get('n_shelves', 0) or 0))
                if _shelves <= 0:
                    _shelves = (2 if _is_wall else 3)
                _shelves = max(1, min(12, _shelves))
                _shelf_depth = max(40.0, _d_mm - _back_thk - _thk - 2.0)
                _shelf_z_c = (_back_thk + _shelf_depth / 2.0 + 1.0) * s
                for _i in range(_shelves):
                    _yy = (float(_y0) + (_h * ((_i + 1) / (_shelves + 1)))) * s
                    # Tijelo police — vidljivo sa strane (puna dubina, 18mm)
                    sc.box((_inner_w - 2.0) * s, _thk * s, _shelf_depth * s).move(
                        _bx, _yy, _shelf_z_c,
                    ).material(_shelf_c if not _is_technical else '#dde2e7', opacity=1.0)
                    # Prednja ivica police — tamniji rub koji daje "vidim policu" efekat
                    sc.box((_inner_w - 2.0) * s, _thk * s, 0.010).move(
                        _bx, _yy, _front_z - 0.002,
                    ).material(_shelf_edge_c, opacity=1.0)
            elif _is_drawer:
                _n = 3
                if _tid == 'BASE_DRAWERS':
                    _n = 2
                if _tid == 'BASE_DRAWERS_3':
                    _n = 3
                if '2' in _tid:
                    _n = 2
                if '4' in _tid:
                    _n = 4
                try:
                    _n = int((_m.get('params') or {}).get('n_drawers', _n))
                except Exception as ex:
                    _LOG.debug("3D drawer count parse failed for module %s: %s", _m.get('id', -1), ex)
                _gap = 8.0
                _usable_h = max(120.0, _h - (_gap * (_n + 1)))
                _dh = _usable_h / _n
                for _i in range(_n):
                    _y1 = float(_y0) + _gap + _i * (_dh + _gap)
                    _cy = (_y1 + (_dh / 2.0)) * s
                    _face = sc.box((_w - 14) * s, _dh * s, 0.012).move(_bx, _cy, _front_z).material(_front_c, opacity=1.0)
                    # handle (jači kontrast i debljina)
                    _hl = min(220.0, _w * 0.50) * s
                    sc.box(_hl, 0.013, 0.018).move(
                        _bx,
                        _cy,
                        _front_z + 0.010,
                    ).material(_handle_c, opacity=1.0)
                    sc.box(_hl * 0.92, 0.006, 0.009).move(
                        _bx,
                        _cy + 0.001,
                        _front_z + 0.013,
                    ).material(_handle_hi, opacity=0.95)
                    try:
                        _face.on_click(lambda e, mid=int(_m.get('id', -1)): (
                            setattr(state, 'selected_edit_id', mid),
                            setattr(state, 'mode', 'edit'),
                            main_content_refresh(),
                        ))
                    except Exception as ex:
                        _LOG.debug("3D click-bind failed (drawer front, id=%s): %s", _m.get('id', -1), ex)
            elif _is_door_drawer:
                # Kombi: gornja fioka + donja dvokrilna vrata
                _gap = 6.0
                _drawer_h = max(90.0, min(180.0, _h * 0.26))
                _drawer_cy = (float(_y0) + _h - _gap - (_drawer_h / 2.0)) * s
                _face = sc.box((_w - 14) * s, _drawer_h * s, 0.012).move(_bx, _drawer_cy, _front_z).material(_front_c, opacity=1.0)
                _hl = min(220.0, _w * 0.50) * s
                sc.box(_hl, 0.013, 0.018).move(_bx, _drawer_cy, _front_z + 0.010).material(_handle_c, opacity=1.0)
                sc.box(_hl * 0.92, 0.006, 0.009).move(_bx, _drawer_cy + 0.001, _front_z + 0.013).material(_handle_hi, opacity=0.95)
                _door_h = _h - _drawer_h - (_gap * 3)
                _dw = (_w - (_gap * 3)) / 2
                _door_cy = (float(_y0) + _gap + (_door_h / 2.0)) * s
                for _i in range(2):
                    _cx = (_x + _gap + (_dw / 2) + (_i * (_dw + _gap))) * s
                    _dface = sc.box(_dw * s, _door_h * s, 0.012).move(_cx, _door_cy, _front_z).material(_front_c, opacity=1.0)
                    _hx = _cx + ((_dw * s) * (0.33 if _i == 0 else -0.33))
                    _vh = min(220.0, _door_h * 0.34) * s
                    sc.box(0.013, _vh, 0.018).move(_hx, _door_cy, _front_z + 0.010).material(_handle_c, opacity=1.0)
                    sc.box(0.006, _vh * 0.9, 0.009).move(_hx + 0.002, _door_cy + 0.001, _front_z + 0.013).material(_handle_hi, opacity=0.95)
                    try:
                        _dface.on_click(lambda e, mid=int(_m.get('id', -1)): (
                            setattr(state, 'selected_edit_id', mid),
                            setattr(state, 'mode', 'edit'),
                            main_content_refresh(),
                        ))
                    except Exception as ex:
                        _LOG.debug("3D click-bind failed (door+drawer door, id=%s): %s", _m.get('id', -1), ex)
                try:
                    _face.on_click(lambda e, mid=int(_m.get('id', -1)): (
                        setattr(state, 'selected_edit_id', mid),
                        setattr(state, 'mode', 'edit'),
                        main_content_refresh(),
                    ))
                except Exception as ex:
                    _LOG.debug("3D click-bind failed (door+drawer face, id=%s): %s", _m.get('id', -1), ex)
            elif _is_fridge:
                _is_integrated_fridge = _tid in {'TALL_FRIDGE', 'TALL_FRIDGE_FREEZER'}
                if _is_integrated_fridge:
                    # Integrisani frižider mora pratiti boju fronta, ne inox izgled.
                    sc.box((_w - 8) * s, (_h - 8) * s, 0.014).move(
                        _bx, _by, _front_z + 0.002
                    ).material(_front_c, opacity=1.0)
                    # Blaga vertikalna refleksija da panel ne bude potpuno ravan.
                    sc.box((_w * 0.16) * s, (_h - 14) * s, 0.010).move(
                        _bx - (_w * 0.20) * s,
                        _by,
                        _front_z + 0.010,
                    ).material(_shade(_front_c, 1.08), opacity=0.32)
                    # Podela frižider / zamrzivač.
                    sc.box((_w - 12) * s, 0.010, 0.014).move(
                        _bx,
                        _by - (_h * s * 0.22),
                        _front_z + 0.014,
                    ).material(_handle_c, opacity=0.85)
                    # Ručke ostaju metalne.
                    _upper_handle_h = min(260.0, _h * 0.30) * s
                    _lower_handle_h = min(220.0, _h * 0.24) * s
                    sc.box(0.018, _upper_handle_h, 0.026).move(
                        _bx + (_w * s * 0.36),
                        _by + (_h * s * 0.16),
                        _front_z + 0.018,
                    ).material(_handle_c, opacity=1.0)
                    sc.box(0.018, _lower_handle_h, 0.026).move(
                        _bx + (_w * s * 0.36),
                        _by - (_h * s * 0.26),
                        _front_z + 0.018,
                    ).material(_handle_c, opacity=1.0)
                else:
                    # Samostojeći frižider ostaje uređaj sa inox izgledom.
                    sc.box((_w - 4) * s, (_h - 4) * s, 0.018).move(
                        _bx, _by, _front_z + 0.002
                    ).material(_inox_mid, opacity=1.0)
                    sc.box((_w * 0.22) * s, (_h - 8) * s, 0.012).move(
                        _bx - (_w * 0.18) * s,
                        _by,
                        _front_z + 0.014,
                    ).material(_inox_light, opacity=0.72)
                    sc.box((_w - 8) * s, 0.010, 0.014).move(
                        _bx,
                        _by - (_h * s * 0.22),
                        _front_z + 0.014,
                    ).material(_inox_dark, opacity=1.0)
                    sc.box(0.020, min(480.0, _h * 0.68) * s, 0.032).move(
                        _bx + (_w * s * 0.36),
                        _by,
                        _front_z + 0.020,
                    ).material(_inox_dark, opacity=1.0)
                    sc.box(0.009, min(460.0, _h * 0.64) * s, 0.014).move(
                        _bx + (_w * s * 0.36) + 0.002,
                        _by + 0.002,
                        _front_z + 0.026,
                    ).material(_inox_light, opacity=0.90)
            elif _is_dish:
                # Ugradna mašina za sudove sa front panelom u boji kuhinje
                _dish_face = sc.box((_w - 14) * s, (_h - 12) * s, 0.012).move(
                    _bx, _by, _front_z
                ).material(_front_c, opacity=1.0)
                # Gornja tehnička traka + komandna zona (diskretno inox/crno)
                _panel_h = max(46.0, min(70.0, _h * 0.10))
                _panel_y = (_by + (_h * s / 2)) - ((_panel_h * s) / 2) - 0.004
                sc.box((_w - 18) * s, _panel_h * s, 0.014).move(
                    _bx, _panel_y, _front_z + 0.004
                ).material('#b9bfc7', opacity=0.95)
                sc.box((_w * 0.18) * s, (_panel_h * 0.55) * s, 0.015).move(
                    _bx, _panel_y, _front_z + 0.010
                ).material('#2f3b4a', opacity=0.95)
                # Ručka kao kod ostalih frontova
                _hl = min(220.0, _w * 0.50) * s
                sc.box(_hl, 0.013, 0.018).move(
                    _bx,
                    _by - ((_h * s) * 0.36),
                    _front_z + 0.010,
                ).material(_handle_c, opacity=1.0)
                sc.box(_hl * 0.92, 0.006, 0.009).move(
                    _bx,
                    _by - ((_h * s) * 0.36) + 0.002,
                    _front_z + 0.013,
                ).material(_handle_hi, opacity=0.95)
                try:
                    _dish_face.on_click(lambda e, mid=int(_m.get('id', -1)): (
                        setattr(state, 'selected_edit_id', mid),
                        setattr(state, 'mode', 'edit'),
                        main_content_refresh(),
                    ))
                except Exception as ex:
                    _LOG.debug("3D click-bind failed (dishwasher, id=%s): %s", _m.get('id', -1), ex)
            elif _is_cooking_unit:
                # Base cooking unit: hob top + oven door + bottom drawer.
                _ctrl_h = max(42.0, _h * 0.10)
                _drawer_h = max(105.0, _h * 0.18)
                _oven_h = max(240.0, _h - _ctrl_h - _drawer_h - 22.0)

                _y_top = float(_y0) + _h
                _y_ctrl_c = _y_top - (_ctrl_h / 2.0) - 6.0
                _y_oven_c = _y_ctrl_c - (_ctrl_h / 2.0) - (_oven_h / 2.0) - 4.0
                _y_drawer_c = float(_y0) + (_drawer_h / 2.0) + 6.0

                # Inox front strips
                sc.box((_w - 12) * s, _ctrl_h * s, 0.012).move(_bx, _y_ctrl_c * s, _front_z).material(_inox_light, opacity=1.0)
                sc.box((_w - 12) * s, _oven_h * s, 0.012).move(_bx, _y_oven_c * s, _front_z).material(_inox_mid, opacity=1.0)
                sc.box((_w - 12) * s, _drawer_h * s, 0.012).move(_bx, _y_drawer_c * s, _front_z).material(_front_c, opacity=1.0)

                # Oven glass
                sc.box((_w - 28) * s, (_oven_h - 24) * s, 0.014).move(
                    _bx, _y_oven_c * s, _front_z + 0.004
                ).material('#111827', opacity=0.92)

                # Oven horizontal handle
                _oh = min(230.0, _w * 0.52) * s
                sc.box(_oh, 0.010, 0.013).move(
                    _bx, (_y_oven_c - (_oven_h * 0.26)) * s, _front_z + 0.010
                ).material(_handle_c, opacity=1.0)
                sc.box(_oh * 0.92, 0.006, 0.010).move(
                    _bx, (_y_oven_c - (_oven_h * 0.26) + 2.0) * s, _front_z + 0.013
                ).material(_handle_hi, opacity=0.95)

                # Bottom drawer handle
                _dh = min(210.0, _w * 0.45) * s
                sc.box(_dh, 0.011, 0.014).move(
                    _bx, _y_drawer_c * s, _front_z + 0.010
                ).material(_handle_c, opacity=1.0)

                # Knobs + display on control strip
                _knob_r = 0.010
                sc.sphere(_knob_r).move((_bx - (_w * 0.22) * s), _y_ctrl_c * s, _front_z + 0.010).material('#e5e7eb', opacity=1.0)
                sc.sphere(_knob_r).move((_bx + (_w * 0.22) * s), _y_ctrl_c * s, _front_z + 0.010).material('#e5e7eb', opacity=1.0)
                sc.box((_w * 0.16) * s, 0.016, 0.012).move(_bx, _y_ctrl_c * s, _front_z + 0.010).material('#111827', opacity=0.95)

                # Hob on top
                sc.box((_w - 8) * s, 0.012, (_d_mm - 8) * s).move(
                    _bx, (_by + (_h * s / 2)) + 0.006, _bz
                ).material('#111827', opacity=0.97)
                # 4 burners
                _hy = (_by + (_h * s / 2)) + 0.013
                _hz = [(_d_mm * 0.27) * s, (_d_mm * 0.60) * s]
                _hx = [(_bx - (_w * 0.22) * s), (_bx + (_w * 0.22) * s)]
                for _cx in _hx:
                    for _cz in _hz:
                        sc.sphere(0.012).move(_cx, _hy, _cz).material('#6b7280', opacity=0.9)

            elif _is_oven or _is_hob or _is_appliance:
                # Appliance front (inox + glass)
                sc.box((_w - 12) * s, (_h - 12) * s, 0.012).move(_bx, _by, _front_z).material(_inox_mid, opacity=1.0)
                sc.box((_w * 0.22) * s, (_h - 16) * s, 0.012).move(
                    _bx + (_w * 0.18) * s,
                    _by,
                    _front_z + 0.004,
                ).material(_inox_light, opacity=0.9)
                _glass_h = min((_h - 70) * s, 0.42 * (_h * s))
                sc.box((_w - 30) * s, _glass_h, 0.014).move(
                    _bx,
                    (_by + 0.02),
                    _front_z + 0.004,
                ).material('#111827', opacity=0.92)
                _ap_hl = min(240.0, _w * 0.54) * s
                sc.box(_ap_hl, 0.009, 0.012).move(
                    _bx,
                    (_by - _glass_h * 0.25),
                    _front_z + 0.010,
                ).material(_handle_c, opacity=1.0)
                sc.box(_ap_hl * 0.92, 0.006, 0.010).move(
                    _bx,
                    (_by - _glass_h * 0.25) + 0.002,
                    _front_z + 0.013,
                ).material(_handle_hi, opacity=0.95)
                if _is_hob or _is_oven:
                    sc.box((_w - 8) * s, 0.012, (_d_mm - 8) * s).move(
                        _bx,
                        (_by + (_h * s / 2)) + 0.006,
                        _bz,
                    ).material('#1f2937', opacity=0.95)
            elif _is_sink:
                # Sink base: front mora pratiti istu boju kao ostali frontovi
                _door_gap = 6.0
                _dw = (_w - (_door_gap * 3)) / 2 if _w >= 520 else (_w - 14)
                if _w >= 520:
                    for _i in range(2):
                        _cx = (_x + _door_gap + (_dw / 2) + (_i * (_dw + _door_gap))) * s
                        _face = sc.box(_dw * s, (_h - 12) * s, 0.012).move(_cx, _by, _front_z).material(_front_c, opacity=1.0)
                        _hx = _cx + ((_dw * s) * (0.33 if _i == 0 else -0.33))
                        _vh = min(220.0, _h * 0.34) * s
                        sc.box(0.013, _vh, 0.018).move(
                            _hx,
                            _by,
                            _front_z + 0.010,
                        ).material(_handle_c, opacity=1.0)
                        sc.box(0.006, _vh * 0.9, 0.009).move(
                            _hx + 0.002,
                            _by + 0.002,
                            _front_z + 0.013,
                        ).material(_handle_hi, opacity=0.95)
                        try:
                            _face.on_click(lambda e, mid=int(_m.get('id', -1)): (
                                setattr(state, 'selected_edit_id', mid),
                                setattr(state, 'mode', 'edit'),
                                main_content_refresh(),
                            ))
                        except Exception as ex:
                            _LOG.debug("3D click-bind failed (sink door, id=%s): %s", _m.get('id', -1), ex)
                else:
                    _face = sc.box((_w - 14) * s, (_h - 12) * s, 0.012).move(_bx, _by, _front_z).material(_front_c, opacity=1.0)
                    _hl = min(220.0, _w * 0.50) * s
                    sc.box(_hl, 0.013, 0.018).move(
                        _bx,
                        _by - ((_h * s) * 0.33),
                        _front_z + 0.010,
                    ).material(_handle_c, opacity=1.0)
                    sc.box(_hl * 0.92, 0.006, 0.009).move(
                        _bx,
                        _by - ((_h * s) * 0.33) + 0.002,
                        _front_z + 0.013,
                    ).material(_handle_hi, opacity=0.95)
                # Sudopera: inox radna površina, korito i slavina
                _sink_top_c = '#C8CDD3'   # inox radna površina
                _sink_bowl_c = '#9EA8B2'  # tamnije korito (udubljeno)
                _sink_rim_c  = '#B2BAC2'  # rub korita
                _faucet_c    = '#BEC6CE'  # tijelo slavine (brushed chrome)
                _faucet_hi   = '#DDE4EA'  # odsjaj slavine
                # Debljina inox radne ploče = ista kao globalni radni sto
                _wt_k = (state.kitchen.get('worktop', {}) or {})
                _wt_thk_s = max(20.0, float(_wt_k.get('thickness', 4.0)) * 10.0)
                _cab_top = _by + (_h * s / 2.0)               # vrh korpusa u 3D
                _inox_center_y = _cab_top + (_wt_thk_s * s / 2.0)
                _inox_top_y    = _cab_top + (_wt_thk_s * s)   # gornja površina inox ploče
                # Inox radna ploča (iste dimenzije kao globalni radni sto)
                sc.box((_w - 10) * s, _wt_thk_s * s, (_d_mm - 10) * s).move(
                    _bx, _inox_center_y, _bz,
                ).material(_sink_top_c, opacity=1.0)
                # Korito — usjek u inox ploči (isti centar Y, malo dublji od ploče)
                _bowl_w = max((_w * 0.42) * s, 0.30)
                _bowl_d = (_d_mm * 0.48) * s
                sc.box(_bowl_w, _wt_thk_s * s + 0.025, _bowl_d).move(
                    _bx - (_w * 0.05 * s),
                    _inox_center_y,
                    (_d_mm * 0.52) * s,
                ).material(_sink_bowl_c, opacity=1.0)
                # Rub korita (highlight na gornjoj ivici korita)
                sc.box(_bowl_w + 0.008, 0.006, _bowl_d + 0.008).move(
                    _bx - (_w * 0.05 * s),
                    _inox_top_y + 0.001,
                    (_d_mm * 0.52) * s,
                ).material(_sink_rim_c, opacity=0.80)
                # Slavina — vertikalni vrat (stoji IZNAD inox ploče)
                _faucet_x = _bx - (_w * 0.05 * s)
                _faucet_base_y = _inox_top_y
                sc.box(0.022, 0.095, 0.022).move(
                    _faucet_x,
                    _faucet_base_y + 0.048,
                    (_d_mm * 0.28) * s,
                ).material(_faucet_c, opacity=1.0)
                # Slavina — horizontalna ruka (luk prema koritu)
                sc.box(0.016, 0.016, (_d_mm * 0.22) * s).move(
                    _faucet_x,
                    _faucet_base_y + 0.092,
                    (_d_mm * 0.38) * s,
                ).material(_faucet_c, opacity=1.0)
                # Highlight odsjaj na slavini
                sc.box(0.008, 0.085, 0.010).move(
                    _faucet_x + 0.004,
                    _faucet_base_y + 0.048,
                    (_d_mm * 0.28) * s - 0.006,
                ).material(_faucet_hi, opacity=0.75)
                # klik fallback na korpus je vec dole
            elif _is_glass:
                # Frame + glass
                _frame_c = _shade(_front_c, 0.84)
                sc.box((_w - 12) * s, (_h - 12) * s, 0.012).move(_bx, _by, _front_z).material(_frame_c, opacity=1.0)
                sc.box((_w - 28) * s, (_h - 28) * s, 0.010).move(_bx, _by, _front_z + 0.003).material('#c7e5ff', opacity=0.42)
            else:
                # Standard doors
                _doors = 1
                if _tid in TEMPLATE_DOOR2:
                    _doors = 2
                if _tid in TEMPLATE_DOOR1:
                    _doors = 1
                if ('2DOOR' in _tid) or ('2 VRATA' in _lbl) or (' 2 ' in _lbl):
                    _doors = 2
                if _is_tall and _w >= 700:
                    _doors = 2
                _door_gap = 6.0
                if _doors == 2:
                    _dw = (_w - (_door_gap * 3)) / 2
                    for _i in range(2):
                        _cx = (_x + _door_gap + (_dw / 2) + (_i * (_dw + _door_gap))) * s
                        _face = sc.box(_dw * s, (_h - 12) * s, 0.012).move(_cx, _by, _front_z).material(_front_c, opacity=1.0)
                        _hx = _cx + ((_dw * s) * (0.33 if _i == 0 else -0.33))
                        _vh = min(240.0, _h * 0.36) * s
                        sc.box(0.013, _vh, 0.018).move(
                            _hx,
                            _by,
                            _front_z + 0.010,
                        ).material(_handle_c, opacity=1.0)
                        sc.box(0.006, _vh * 0.9, 0.009).move(
                            _hx + 0.002,
                            _by + 0.002,
                            _front_z + 0.013,
                        ).material(_handle_hi, opacity=0.95)
                        try:
                            _face.on_click(lambda e, mid=int(_m.get('id', -1)): (
                                setattr(state, 'selected_edit_id', mid),
                                setattr(state, 'mode', 'edit'),
                                main_content_refresh(),
                            ))
                        except Exception as ex:
                            _LOG.debug("3D click-bind failed (double door, id=%s): %s", _m.get('id', -1), ex)
                else:
                    _face = sc.box((_w - 14) * s, (_h - 12) * s, 0.012).move(_bx, _by, _front_z).material(_front_c, opacity=1.0)
                    # Strana ručke čita se iz params (default 'right')
                    _h_side = str((_m.get('params') or {}).get('handle_side', 'right')).lower()
                    _vh_len = min(240.0, _h * 0.40) * s
                    if _h_side in ('left', 'right'):
                        _hx = _bx + (_w * s * (0.36 if _h_side == 'right' else -0.36))
                        _hy_off = (_h * s * 0.12) if _is_wall else 0.0
                        sc.box(0.013, _vh_len, 0.018).move(
                            _hx, _by - _hy_off, _front_z + 0.010
                        ).material(_handle_c, opacity=1.0)
                        sc.box(0.004, _vh_len * 0.90, 0.007).move(
                            _hx + 0.002, _by - _hy_off + 0.001, _front_z + 0.013
                        ).material(_handle_hi, opacity=0.95)
                    else:
                        # center = horizontalna ručka
                        _hl = min(220.0, _w * 0.52) * s
                        sc.box(_hl, 0.013, 0.018).move(
                            _bx,
                            _by - ((_h * s) * 0.34 if _is_wall else (_h * s) * 0.36),
                            _front_z + 0.010,
                        ).material(_handle_c, opacity=1.0)
                        sc.box(_hl * 0.92, 0.006, 0.009).move(
                            _bx,
                            _by - ((_h * s) * 0.34 if _is_wall else (_h * s) * 0.36) + 0.002,
                            _front_z + 0.013,
                        ).material(_handle_hi, opacity=0.95)
                    try:
                        _face.on_click(lambda e, mid=int(_m.get('id', -1)): (
                            setattr(state, 'selected_edit_id', mid),
                            setattr(state, 'mode', 'edit'),
                            main_content_refresh(),
                        ))
                    except Exception as ex:
                        _LOG.debug("3D click-bind failed (single door, id=%s): %s", _m.get('id', -1), ex)
                # Lift-up: dodatna horizontalna podela i jedna centralna ručka
                if _is_liftup:
                    _split_y = _by + (_h * s * 0.07)
                    sc.box((_w - 14) * s, 0.006, 0.010).move(_bx, _split_y, _front_z + 0.008).material('#4b5563', opacity=0.75)
                    sc.box(min(200.0, _w * 0.48) * s, 0.012, 0.018).move(_bx, _by - (_h * s * 0.35), _front_z + 0.018).material(_handle_c, opacity=1.0)

            # Corner (L-oblik) – pravo 3D L-krilo prema posmatraču
            if _is_corner:
                _is_left_c = _x < (_wl / 2)
                _is_diag_corner = 'DIAGONAL' in _tid
                _is_wall_corner = _z in ('wall', 'wall_upper')

                # Krilo se proteže prema posmatraču iza/iznad dubine glavnog elementa.
                # wing_extra = koliko mm dalje od _d_mm ide krilo u Z pravcu (prema kameri)
                _wing_extra = max(220.0 if _is_wall_corner else 280.0, _w * (0.32 if _is_wall_corner else 0.40))
                # Širina krila u X pravcu = dubina elementa (standardno za L-ćošak)
                _wing_face_x = min(_d_mm, _w * 0.65) * s

                # Centar krila u X (prislonjeno uz bočni zid)
                if _is_left_c:
                    _wing_cx = (_bx - _w * s / 2) + _wing_face_x / 2
                else:
                    _wing_cx = (_bx + _w * s / 2) - _wing_face_x / 2

                # Centar krila u Z (počinje od kraja dubine glavnog, proteže se dalje)
                _wing_cz = (_d_mm + _wing_extra / 2) * s
                # Prednja Z-koordinata krila (bliže kameri nego glavni front)
                _wing_front_z = (_d_mm + _wing_extra) * s - 0.002

                # ── Korpus krila ──
                sc.box(_wing_face_x, _h * s, _wing_extra * s).move(
                    _wing_cx, _by, _wing_cz
                ).material(_carcass_c, opacity=1.0)

                # ── Top highlight krila ──
                sc.box(max(0.010, _wing_face_x - 0.008), 0.005,
                       max(0.010, (_wing_extra - 10) * s)).move(
                    _wing_cx,
                    (_by + _h * s / 2) - 0.003,
                    _wing_cz,
                ).material(_top_c, opacity=0.55)

                # ── Front ploča krila (prema posmatraču) ──
                sc.box(_wing_face_x, (_h - 4) * s, 0.022).move(
                    _wing_cx, _by, _wing_front_z - 0.010
                ).material(_front_c, opacity=1.0)
                if _is_wall_corner:
                    sc.box(_wing_face_x, 0.010, max(0.10, (_wing_extra - 10) * s)).move(
                        _wing_cx,
                        (_by - (_h * s / 2)) + 0.005,
                        _wing_cz,
                    ).material(_shade(_carcass_c, 0.72), opacity=0.95)
                    sc.box(max(0.08, _wing_face_x - 0.010), 0.006, 0.012).move(
                        _wing_cx,
                        (_by + (_h * s / 2)) - 0.004,
                        _wing_front_z - 0.004,
                    ).material(_shade(_carcass_c, 0.82), opacity=0.88)

                # ── Bočna sjena krila (vidljiva od kamere) ──
                _sh_x = ((_wing_cx + _wing_face_x / 2) - 0.006) if _is_left_c \
                    else ((_wing_cx - _wing_face_x / 2) + 0.006)
                sc.box(0.012, (_h - 6) * s, max(0.010, (_wing_extra - 6) * s)).move(
                    _sh_x, _by, _wing_cz
                ).material(_shade(_carcass_c, 0.70), opacity=0.82)

                # ── Donja bordura fronta krila ──
                sc.box(_wing_face_x, 0.006, 0.010).move(
                    _wing_cx,
                    (_by - _h * s / 2) + 0.004,
                    _wing_front_z - 0.004,
                ).material(_shade(_carcass_c, 0.58), opacity=0.88)

                if _is_diag_corner:
                    _diag_len = max(0.18, ((_wing_face_x / s) + (_wing_extra * 0.72)) * s)
                    _diag_x = _wing_cx + ((_wing_face_x * 0.16) if _is_left_c else -(_wing_face_x * 0.16))
                    _diag_z = ((_d_mm + (_wing_extra * 0.48)) * s)
                    sc.box(max(0.016, _diag_len), (_h - 10) * s, 0.018).move(
                        _diag_x, _by, _diag_z
                    ).rotate(0, -0.78 if _is_left_c else 0.78, 0).material(_front_c, opacity=1.0)
                    sc.box(max(0.12, _diag_len * 0.42), 0.012, 0.020).move(
                        _diag_x, _by, _diag_z + 0.010
                    ).rotate(0, -0.78 if _is_left_c else 0.78, 0).material(_handle_c, opacity=0.95)
                    if _is_wall_corner:
                        sc.box(0.014, max(0.08, (_h - 40) * s), max(0.10, _diag_len * 0.30)).move(
                            _diag_x + (0.010 if _is_left_c else -0.010),
                            _by - (_h * s * 0.08),
                            _diag_z,
                        ).rotate(0, -0.78 if _is_left_c else 0.78, 0).material(_handle_c, opacity=0.92)
                elif _z == 'base':
                    sc.box(max(0.08, _wing_face_x * 0.36), 0.012, 0.018).move(
                        _wing_cx,
                        _by - (_h * s * 0.18),
                        _wing_front_z + 0.004,
                    ).material(_handle_c, opacity=0.95)
                    _wt = (state.kitchen.get('worktop', {}) or {})
                    _wt_thk_mm = max(20.0, float(_wt.get('thickness', 4.0)) * 10.0)
                    _wt_depth_mm = max(300.0, _fnum(_wt.get('width', 600.0), 600.0))
                    _wt_y = (float(_y0) + _h) * s + (_wt_thk_mm * s / 2.0)
                    sc.box(_wing_face_x, _wt_thk_mm * s, _wing_extra * s).move(
                        _wing_cx, _wt_y, _wing_cz
                    ).material('#B0A898', opacity=0.98)
                    sc.box(max(0.08, _wing_face_x - 0.008), (_wt_thk_mm * 0.78) * s, 0.012).move(
                        _wing_cx, _wt_y, _wing_front_z - 0.004
                    ).material('#7A726A', opacity=1.0)
                elif _is_wall_corner:
                    sc.box(0.014, max(0.08, (_h - 34) * s), 0.020).move(
                        _wing_cx + ((_wing_face_x * 0.28) if _is_left_c else -(_wing_face_x * 0.28)),
                        _by - (_h * s * 0.06),
                        _wing_front_z + 0.006,
                    ).material(_handle_c, opacity=0.92)

            # Base click area fallback
            try:
                _carcass.on_click(lambda e, mid=int(_m.get('id', -1)): (
                    setattr(state, 'selected_edit_id', mid),
                    setattr(state, 'mode', 'edit'),
                    main_content_refresh(),
                ))
            except Exception as ex:
                _LOG.debug("3D click-bind failed (carcass fallback, id=%s): %s", _m.get('id', -1), ex)

            if int(_m.get('id', -1)) == int(getattr(state, 'selected_edit_id', -1)):
                sc.box((_w + 8) * s, (_h + 8) * s, (_d_mm + 8) * s).move(_bx, _by, _bz).material('#111111', opacity=0.22)

        # Radna ploča iznad donjih elemenata (vidljiva u 3D)
        _wt = (state.kitchen.get('worktop', {}) or {})
        _wt_thk_mm = max(20.0, float(_wt.get('thickness', 4.0)) * 10.0)   # thickness je u cm
        _wt_w_mm = max(300.0, float(_wt.get('width', 600.0)))
        _wt_col_top = '#d1d1d1' if _is_technical else '#B0A898'
        _wt_col_side = '#4f4f4f' if _is_technical else '#7A726A'
        for _x, _w, _y0, _hm in _worktop_segments:
            _cx = (_x + _w / 2.0) * s
            _top = (_y0 + _hm) * s
            _cy = _top + (_wt_thk_mm * s / 2.0)
            _cz = (_wt_w_mm * s / 2.0)
            # Top plate
            sc.box(_w * s, _wt_thk_mm * s, _wt_w_mm * s).move(
                _cx, _cy, _cz
            ).material(_wt_col_top, opacity=0.98)
            # Front edge (tamna traka) za bolju vidljivost
            sc.box((_w - 6) * s, (_wt_thk_mm * 0.78) * s, 0.012).move(
                _cx, _cy, (_wt_w_mm * s) - 0.005
            ).material(_wt_col_side, opacity=1.0)

        # Backsplash – tamne keramičke pločice između baze i gornjaka (samo Katalog)
        if not _is_technical:
            _k = state.kitchen or {}
            _bs_foot = float(_k.get('foot_height_mm', 150))
            _bs_korp = float(_k.get('base_korpus_h_mm', 720))
            _bs_gap = float(_k.get('vertical_gap_mm', 460))
            _wt_thk = max(20.0, float((_k.get('worktop') or {}).get('thickness', 4.0)) * 10.0)
            _bs_y_bot = (_bs_foot + _bs_korp + _wt_thk) * s
            _bs_y_top = _bs_y_bot + (_bs_gap - 20.0) * s
            if _bs_y_top > _bs_y_bot + 0.06:
                _bs_h = _bs_y_top - _bs_y_bot
                sc.box(w - 0.01, _bs_h, 0.007).move(
                    w / 2, _bs_y_bot + _bs_h / 2, 0.015
                ).material('#3B3835', opacity=0.82)
                # Horizontalne fuge (grout linije za realistični izgled pločica)
                _n_grout = max(2, int(_bs_h / 0.25))
                for _gi in range(1, _n_grout):
                    _gy = _bs_y_bot + (_bs_h * _gi / _n_grout)
                    sc.box(w - 0.015, 0.004, 0.008).move(
                        w / 2, _gy, 0.017
                    ).material('#22201E', opacity=0.60)

        # Napomena:
        # ranije je ovde postojao poseban, uprošćeni L-render za zid B.
        # Taj dodatni put je crtao elemente i kada aktivni zid nije B, pa su
        # se moduli pojavljivali i na zidu C, a specijalni elementi (npr.
        # sudopera) nisu pratili puni renderer aktivnog zida.
        #
        # Dok ne postoji jedinstven multi-wall renderer za A/B/C, 3D mora da
        # prikaže TAČNO aktivni zid kroz glavni renderer iznad, bez dodatnog
        # "polovičnog" crtanja drugog kraka.

        # L-kuhinja prikaz: oba zida istovremeno u sceni.
        #
        # Pravilo renderovanja:
        #   Zid A elementi → zadnji zid (x_mm→scX, d_mm→scZ) — normalne koordinate
        #   Zid B elementi → levi zid  (x_mm→scZ, d_mm→scX) — zamena koordinata (x↔z)
        #
        # Aktivni zid: pun render (opacity 1.0 za korpus/front).
        # Neaktivni zid: kontekst render, utišan (opacity 0.52).
        #
        # Zid C: nema posebne L-logike, ne prikazuje kontekst drugog zida.
        _is_l_ctx = (
            str(getattr(state, 'kitchen_layout', state.kitchen.get('layout', '')) or '')
            .lower().strip() == 'l_oblik'
            and _active_wall in ('A', 'B')
        )
        if _is_l_ctx:
            try:
                _gwt_ctx_s = max(0.020, float(
                    (state.kitchen.get('worktop') or {}).get('thickness', 3.8)
                ) * 10.0 * s)
                _cf_s = float(state.kitchen.get('foot_height_mm', 100)) * s
                _nz   = 0.036

                # Boje aktivnog zida (pun render)
                _act_korp  = '#ECEAE6'
                _act_front_col = str(state.kitchen.get('front_color', '#F5F4F1') or '#F5F4F1')
                _act_wt    = '#B0A898' if not _is_technical else '#d1d1d1'
                _act_noz   = '#404850'
                # Boje kontekst zida (utišan)
                _ctx_korp  = '#C8C5C0'
                _ctx_front = '#DEDAD6'
                _ctx_wt    = '#B8B0A8'
                _ctx_noz   = '#808080'
                _wall_b_len_mm = float(
                    (state.kitchen.get('wall_lengths_mm', {}) or {}).get('B')
                    or next(
                        (
                            int(wall.get('length_mm', 2400) or 2400)
                            for wall in ((getattr(state, 'room', {}) or {}).get('walls', []) or [])
                            if str(wall.get('key', '')).upper() == 'B'
                        ),
                        2400,
                    )
                )
                _corner_left_mm, _corner_right_mm = _l_corner_offsets_mm(state.kitchen, 'B')

                def _draw_left_wall_corner_zone() -> None:
                    """Prikaži rezervisani L-ugao na Zidu B kao ghost volumen.

                    2D već prikazuje sivi `Ugao Zid A (560mm)` span. Ovdje crtamo
                    isti koncept u 3D, bez lažnog dodavanja modula na pogrešan zid.
                    """
                    _corner_span_mm = float(_corner_left_mm or _corner_right_mm or 0.0)
                    if _corner_span_mm <= 0:
                        return
                    _span_start_mm = 0.0 if _corner_left_mm > 0 else max(0.0, _wall_b_len_mm - _corner_span_mm)
                    _ghost_depth_mm = max(
                        float(
                            max(
                                (
                                    int(m.get('d_mm', 0) or 0)
                                    for m in (state.kitchen.get('modules', []) or [])
                                    if str(m.get('wall_key', 'A')).upper() == 'A'
                                    and str(m.get('zone', '')).lower().strip() == 'base'
                                ),
                                default=0,
                            )
                        ),
                        float(get_zone_depth_standard('base') or 560),
                    )
                    _base_y0, _base_h = zone_baseline_and_height(state.kitchen, 'base')
                    _cx, _cy, _cz, _bw, _bh, _bd = to_scene_coords(
                        x_mm=_span_start_mm,
                        y_mm=float(_base_y0) + float(_base_h) / 2.0,
                        d_mm=_ghost_depth_mm,
                        w_mm=_corner_span_mm,
                        h_mm=float(_base_h),
                        on_left_wall=True,
                        s=s,
                    )
                    sc.box(_bw, _bh, _bd).move(_cx, _cy, _cz).material('#B5B1AB', opacity=0.18)
                    sc.box(0.012, _bh - 0.010, max(0.012, _bd - 0.010)).move(
                        _bw + 0.006, _cy, _cz
                    ).material('#8B8781', opacity=0.22)
                    sc.box(_bw + 0.014, _gwt_ctx_s, _bd + 0.014).move(
                        _cx, (float(_base_y0 + _base_h) * s) + (_gwt_ctx_s / 2.0), _cz
                    ).material('#B8B0A8', opacity=0.20)

                def _render_wall_mod(
                    cm: dict,
                    on_left_wall: bool,
                    is_active: bool,
                ) -> None:
                    """Renderuje jedan modul na zadnjem (on_left_wall=False) ili levom zidu.

                    Koristi to_scene_coords() za jedinstvenu koordinatnu transformaciju —
                    nema duplirane inline logike za Zid A / Zid B.

                    Ugaoni klip (Wall B):
                        x_mm Wall B elementa = distanca od ugla duž levog zida.
                        Mora biti ≥ max d_mm svih Wall A base modula da nema 3D preklapanja.
                        Ako element ulazi u ugaonu zonu, klipujemo ga ili preskačemo.
                    """
                    _m_x  = float(cm.get('x_mm', 0) or 0)
                    _m_w  = float(cm.get('w_mm', 0) or 0)
                    _m_h  = float(cm.get('h_mm', 0) or 0)
                    _m_zn = str(cm.get('zone', 'base')).lower().strip()
                    _m_d  = float(cm.get('d_mm', 0) or 0)
                    if _m_d <= 0:
                        _m_d = float(get_zone_depth_standard(_m_zn) or 560)

                    # ── Ugaoni klip za Wall B ──────────────────────────────────────
                    # Wall B modul na x_mm ≥ 0 fizički počinje od ugla (x=0 = dodir
                    # sa Zidom A). Da bi se izbjeglo 3D preklapanje sa Wall A baza
                    # modulima (koji sežu dubinom d_A u Z pravcu = "ugaona zona"),
                    # efektivni početak Wall B modula ne smije biti manji od
                    # max(d_mm) svih Wall A baza modula.
                    if on_left_wall:
                        _wa_base = [
                            m for m in (state.kitchen.get('modules', []) or [])
                            if str(m.get('wall_key', 'A')).upper() == 'A'
                            and str(m.get('zone', '')).lower().strip() == 'base'
                        ]
                        _corner_clear = max(
                            (float(m.get('d_mm', 0) or 0) for m in _wa_base),
                            default=float(get_zone_depth_standard('base') or 560),
                        )
                        _m_end = _m_x + _m_w
                        if _m_end <= _corner_clear:
                            # Modul je potpuno u ugaonoj zoni — ne prikazuj ništa
                            return
                        if _m_x < _corner_clear:
                            # Modul dijelimično ulazi u ugaonu zonu — klipuj početak
                            _m_w = _m_end - _corner_clear
                            _m_x = _corner_clear
                    try:
                        _m_y0, _ = zone_baseline_and_height(state.kitchen, _m_zn)
                    except Exception:
                        _m_y0 = int(state.kitchen.get('foot_height_mm', 100))
                    _m_y0   = float(_m_y0)
                    _m_h_s  = _m_h * s
                    _m_y0_s = _m_y0 * s

                    _op_k  = 0.96 if is_active else 0.52
                    _op_f  = 0.92 if is_active else 0.48
                    _op_wt = 0.96 if is_active else 0.52
                    _op_nz = 0.80 if is_active else 0.38
                    _korp  = _act_korp       if is_active else _ctx_korp
                    _fc    = _act_front_col  if is_active else _ctx_front
                    _wtc   = _act_wt         if is_active else _ctx_wt
                    _nzc   = _act_noz        if is_active else _ctx_noz

                    # Centralne scene koordinate i dimenzije kutije — jedinstven poziv
                    _bcx, _byc, _bcz, _bw, _bh, _bd = to_scene_coords(
                        x_mm=_m_x, y_mm=_m_y0 + _m_h / 2.0,
                        d_mm=_m_d, w_mm=_m_w, h_mm=_m_h,
                        on_left_wall=on_left_wall, s=s,
                    )

                    # Korpus
                    sc.box(_bw, _bh, _bd).move(_bcx, _byc, _bcz).material(_korp, opacity=_op_k)

                    if not on_left_wall:
                        # Zid A — front pri prednjem rubu (+Z, prema kameri)
                        sc.box(_bw - 0.006, _bh - 0.008, 0.018).move(
                            _bcx, _byc, _bd + 0.009
                        ).material(_fc, opacity=_op_f)
                        if _m_zn == 'base':
                            sc.box(_bw + 0.018, _gwt_ctx_s, _bd + 0.018).move(
                                _bcx, _m_y0_s + _m_h_s + _gwt_ctx_s / 2.0, _bcz
                            ).material(_wtc, opacity=_op_wt)
                            for _nx in (_bcx - _bw / 2.0 + 0.05, _bcx + _bw / 2.0 - 0.05):
                                sc.box(_nz, _cf_s, _nz).move(_nx, _cf_s / 2.0, _bd * 0.14).material(_nzc, opacity=_op_nz)
                                sc.box(_nz, _cf_s, _nz).move(_nx, _cf_s / 2.0, _bd * 0.86).material(_nzc, opacity=_op_nz)
                    else:
                        # Zid B — front pri prednjem rubu (+X, gleda prema unutra)
                        sc.box(0.018, _bh - 0.008, _bd - 0.006).move(
                            _bw + 0.009, _byc, _bcz
                        ).material(_fc, opacity=_op_f)
                        if _m_zn == 'base':
                            sc.box(_bw + 0.018, _gwt_ctx_s, _bd + 0.018).move(
                                _bcx, _m_y0_s + _m_h_s + _gwt_ctx_s / 2.0, _bcz
                            ).material(_wtc, opacity=_op_wt)
                            for _nz_pos in (_bcz - _bd / 2.0 + 0.05, _bcz + _bd / 2.0 - 0.05):
                                sc.box(_nz, _cf_s, _nz).move(_bw * 0.14, _cf_s / 2.0, _nz_pos).material(_nzc, opacity=_op_nz)
                                sc.box(_nz, _cf_s, _nz).move(_bw * 0.86, _cf_s / 2.0, _nz_pos).material(_nzc, opacity=_op_nz)

                _mods_A = [
                    m for m in (state.kitchen.get('modules', []) or [])
                    if str(m.get('wall_key', 'A')).upper() == 'A'
                    and str(m.get('zone', '')).lower().strip() not in ('tall_top', 'wall_upper')
                ]
                _mods_B = [
                    m for m in (state.kitchen.get('modules', []) or [])
                    if str(m.get('wall_key', 'A')).upper() == 'B'
                    and str(m.get('zone', '')).lower().strip() not in ('tall_top', 'wall_upper')
                ]

                if _active_wall == 'A':
                    # Zid A je vec odraden u glavnoj petlji (pun render sa vratima/ruckama).
                    # Ovde samo dodajemo Zid B kao utisani kontekst na levom zidu.
                    _draw_left_wall_corner_zone()
                    for _cm in _mods_B:
                        _render_wall_mod(_cm, on_left_wall=True, is_active=False)
                else:
                    # Zid B aktivan: glavna petlja je prazna (_mods_all=[]).
                    # Crtamo oba zida ovde u pravilnim koordinatama.
                    # Zid A → zadnji zid (kontekst, utisan)
                    for _cm in _mods_A:
                        _render_wall_mod(_cm, on_left_wall=False, is_active=False)
                    # Zid B → levi zid (aktivan, pun opacity)
                    _draw_left_wall_corner_zone()
                    for _cm in _mods_B:
                        _render_wall_mod(_cm, on_left_wall=True, is_active=True)

            except Exception as _ex:
                _LOG.debug('L-kontekst render greška: %s', _ex)

        # Kamera IZVAN prostorije (z > d), centrirana, gleda ka kuhinjskom zidu (z≈0).
        # d = dubina sobe u scene jedinicama (30 = 3000mm).
        # Kamera stoji na 1.8× dubine iza ulaza = uvijek van prostorije.
        _is_l_layout = str(getattr(state, 'kitchen_layout', state.kitchen.get('layout', '')) or '').lower().strip() == 'l_oblik'
        if _is_l_layout and _active_wall == 'A':
            # Zid A aktivan — kamera desno-napred, gleda ka centru zadnjeg zida.
            # Levi zid (Zid B kontekst) vidljiv na levoj strani slike.
            _look_x = w * 0.40    # centar Zid A (blago desno od sredine)
            _look_y = h * 0.32
            _look_z = d * 0.10    # blizu zadnjeg zida
            _cam_x  = w * 0.90
            _cam_y  = h * 0.55
            _cam_z  = d * 1.60
        elif _is_l_layout and _active_wall == 'B':
            # Zid B aktivan — kamera desno-napred, gleda direktno na levi zid (x≈0).
            # Zadnji zid (Zid A kontekst) vidljiv u dubini scene.
            _look_x = 0.15        # levi zid (Zid B je pri x=0)
            _look_y = h * 0.32
            _look_z = d * 0.40    # sredina Zid B (dubinom)
            _cam_x  = w * 0.85
            _cam_y  = h * 0.55
            _cam_z  = d * 0.75
        else:
            # Normalan prikaz (jedan zid ili Zid C) — centrirana kamera ispred zida
            _look_x = w / 2
            _look_y = h * 0.35
            _look_z = 0.0
            _cam_x  = w / 2
            _cam_y  = h * 0.60
            _cam_z  = d * 1.80
        _move_camera_y_up(
            sc,
            x=_cam_x,
            y=_cam_y,
            z=_cam_z,
            look_at_x=_look_x,
            look_at_y=_look_y,
            look_at_z=_look_z,
        )
        _dx = _cam_x - _look_x
        _dy = _cam_y - _look_y
        _dz = _cam_z - _look_z
        _radius = max(1e-6, math.sqrt((_dx * _dx) + (_dy * _dy) + (_dz * _dz)))
        _cos_polar = max(-1.0, min(1.0, _dy / _radius))
        _polar = math.acos(_cos_polar)

    # Postavi kameru i zaključaj orbit — JavaScript direktno, bez async race-a.
    _lock_scene_to_horizontal_orbit(
        ui,
        sc,
        cam_x=_cam_x,
        cam_y=_cam_y,
        cam_z=_cam_z,
        target_x=_look_x,
        target_y=_look_y,
        target_z=_look_z,
        polar_angle=_polar,
        delay_s=0.35,
    )
    # Poboljšano Three.js osvjetljenje — topliji, realističniji izgled.
    _enhance_scene_lighting(ui, sc, w, h, d, delay_s=0.65)


def render_room_setup_scene_3d(
    *,
    ui: Any,
    state: Any,
    room: dict,
    ensure_room_walls: Callable[[dict], Any],
    get_room_wall: Callable[[dict, str], dict],
    camera_view: dict,
    diag_yaw: dict,
    refs: dict,
    openings_list_refresh: Callable[[], None],
    opening_selected_info_refresh: Callable[[], None],
    wall_headline_refresh: Callable[[], None],
    wall_compass_refresh: Callable[[], None],
    wall_preview_refresh: Callable[[], None],
    scene_refresh: Callable[[], None],
) -> None:
    """Render 3D room scene for room setup wizard."""
    ensure_room_walls(room)
    wall_a = get_room_wall(room, "A")
    wall_b = get_room_wall(room, "B")
    wall_c = get_room_wall(room, "C")
    _active = str(room.get("active_wall", "A")).upper()
    _kitchen_wall = str(room.get("kitchen_wall", "A")).upper()
    wl = int(wall_a.get('length_mm', room.get('wall_length_mm', 3000)))
    wh = int(wall_a.get('height_mm', room.get('wall_height_mm', 2600)))
    rd = int(room.get('room_depth_mm', 3000))
    depth_mm = max(rd, int(wall_b.get('length_mm', rd)), int(wall_c.get('length_mm', rd)))
    s = 0.01
    w = wl * s
    h = wh * s
    d = depth_mm * s
    hb = int(wall_b.get('height_mm', wh)) * s
    hc = int(wall_c.get('height_mm', wh)) * s

    with ui.scene(width=1200, height=700).classes('w-full h-full') as scene:
        scene.background_color = '#ECECEC'
        _show_guides = False
        _floor_t = 0.10
        _ceil_t = 0.04
        _wall_t = 0.10
        scene.box(w, _floor_t, d).move(w / 2, -_floor_t / 2, d / 2).material('#DEC6A0')
        _planks = max(16, int(d / 0.24))
        _pz = d / _planks
        for _i in range(_planks):
            _tone = '#D8BE94' if (_i % 2 == 0) else '#E8D0AC'
            scene.box(w * 0.996, 0.0035, max(0.02, _pz * 0.90)).move(
                w / 2, -0.001, (_i + 0.5) * _pz
            ).material(_tone, opacity=0.62)
        _wcol = {"A": "#E4E4E4", "B": "#DFDFDF", "C": "#DFDFDF"}
        _abox = scene.box(w, h, _wall_t).move(w / 2, h / 2, _wall_t / 2).material(
            _wcol["A"], opacity=0.98 if _active == "A" else 0.82
        )
        # B je LEVI zid (x < 0), C je DESNI zid (x > w)
        _bbox = scene.box(_wall_t, hb, d).move(-_wall_t / 2, hb / 2, d / 2).material(
            _wcol["B"], opacity=0.98 if _active == "B" else 0.78
        )
        _cbox = scene.box(_wall_t, hc, d).move(w + _wall_t / 2, hc / 2, d / 2).material(
            _wcol["C"], opacity=0.98 if _active == "C" else 0.78
        )
        scene.box(w, _ceil_t, d).move(w / 2, h + _ceil_t / 2, d / 2).material('#FFFFFF', opacity=0.10)
        # Sokla uz zidove
        _sk_h = 0.06
        _sk_t = 0.016
        scene.box(w, _sk_h, _sk_t).move(w / 2, _sk_h / 2, _wall_t + _sk_t / 2).material('#C5C5C5', opacity=0.95)
        scene.box(_sk_t, _sk_h, d).move(_wall_t + _sk_t / 2, _sk_h / 2, d / 2).material('#C2C2C2', opacity=0.92)
        scene.box(_sk_t, _sk_h, d).move(w - _sk_t / 2, _sk_h / 2, d / 2).material('#C2C2C2', opacity=0.92)

        if _show_guides:
            try:
                scene.text('POD').move(w * 0.08, h + _floor_t + 0.03, d * 0.08).scale(0.24)
                scene.text('PLAFON').move(w * 0.08, _ceil_t + 0.03, d * 0.08).scale(0.24)
                _ft = 0.01
                _fy = h + _floor_t + (_ft / 2)
                scene.box(w + _ft, _ft, _ft).move(w / 2, _fy, -_ft / 2).material('#111111', opacity=0.75)
                scene.box(w + _ft, _ft, _ft).move(w / 2, _fy, d + _ft / 2).material('#111111', opacity=0.75)
                scene.box(_ft, _ft, d + _ft).move(-_ft / 2, _fy, d / 2).material('#111111', opacity=0.75)
                scene.box(_ft, _ft, d + _ft).move(w + _ft / 2, _fy, d / 2).material('#111111', opacity=0.75)
                _et = 0.01
                _ey = _ceil_t + (_et / 2)
                scene.box(w + _et, _et, _et).move(w / 2, _ey, -_et / 2).material('#111111', opacity=0.85)
                scene.box(w + _et, _et, _et).move(w / 2, _ey, d + _et / 2).material('#111111', opacity=0.85)
                scene.box(_et, _et, d + _et).move(-_et / 2, _ey, d / 2).material('#111111', opacity=0.85)
                scene.box(_et, _et, d + _et).move(w + _et / 2, _ey, d / 2).material('#111111', opacity=0.85)
            except Exception as ex:
                _LOG.debug("3D room helper labels/edges failed: %s", ex)

        def _dim_line_x(x1: float, x2: float, y: float, z: float, color: str, txt: str | None = None):
            if not _show_guides:
                return
            ln = max(0.02, abs(x2 - x1))
            scene.box(ln, 0.008, 0.008).move((x1 + x2) / 2, y, z).material(color, opacity=0.95)
            scene.box(0.008, 0.028, 0.008).move(x1, y, z).material(color, opacity=0.95)
            scene.box(0.008, 0.028, 0.008).move(x2, y, z).material(color, opacity=0.95)
            if txt:
                try:
                    scene.text(txt).move((x1 + x2) / 2, y + 0.03, z).scale(0.12)
                except Exception as ex:
                    _LOG.debug("3D dimension label X failed: %s", ex)

        def _dim_line_y(y1: float, y2: float, x: float, z: float, color: str, txt: str | None = None):
            if not _show_guides:
                return
            ln = max(0.02, abs(y2 - y1))
            scene.box(0.008, ln, 0.008).move(x, (y1 + y2) / 2, z).material(color, opacity=0.95)
            scene.box(0.028, 0.008, 0.008).move(x, y1, z).material(color, opacity=0.95)
            scene.box(0.028, 0.008, 0.008).move(x, y2, z).material(color, opacity=0.95)
            if txt:
                try:
                    scene.text(txt).move(x + 0.02, (y1 + y2) / 2, z).scale(0.12)
                except Exception as ex:
                    _LOG.debug("3D dimension label Y failed: %s", ex)

        def _dim_line_z(z1: float, z2: float, y: float, x: float, color: str, txt: str | None = None):
            if not _show_guides:
                return
            ln = max(0.02, abs(z2 - z1))
            scene.box(0.008, 0.008, ln).move(x, y, (z1 + z2) / 2).material(color, opacity=0.95)
            scene.box(0.008, 0.028, 0.008).move(x, y, z1).material(color, opacity=0.95)
            scene.box(0.008, 0.028, 0.008).move(x, y, z2).material(color, opacity=0.95)
            if txt:
                try:
                    scene.text(txt).move(x, y + 0.03, (z1 + z2) / 2).scale(0.12)
                except Exception as ex:
                    _LOG.debug("3D dimension label Z failed: %s", ex)

        if _show_guides:
            try:
                scene.text('ZID A / ZADNJI').move(w * 0.50, h * 0.90, 0.07).scale(0.35)
                scene.text('ZID B / LEVI').move(0.08, hb * 0.90, d * 0.50).rotate(0, 1.57, 0).scale(0.30)
                scene.text('ZID C / DESNI').move(w - 0.08, hc * 0.90, d * 0.50).rotate(0, -1.57, 0).scale(0.30)
                if _kitchen_wall == "A":
                    scene.text('ZID KUHINJE').move(w * 0.50, h * 0.78, 0.07).scale(0.34)
                elif _kitchen_wall == "B":
                    scene.text('ZID KUHINJE').move(0.08, hb * 0.78, d * 0.50).rotate(0, 1.57, 0).scale(0.30)
                else:
                    scene.text('ZID KUHINJE').move(w - 0.08, hc * 0.78, d * 0.50).rotate(0, -1.57, 0).scale(0.30)
            except Exception as ex:
                _LOG.debug("3D wall text labels failed: %s", ex)

        _dim_col_wall = '#1F2937'
        _dim_col_open = '#8B5E3C'
        _dim_line_x(0.0, w, 0.08, -0.06, _dim_col_wall, f'{wl} mm')
        _dim_line_y(0.0, h, w + 0.08, -0.03, _dim_col_wall, f'H {wh} mm')
        _dim_line_z(0.0, d, 0.10, w + 0.05, _dim_col_wall, f'D {depth_mm} mm')
        _dim_line_y(0.0, h, -0.10, d + 0.02, '#374151', 'Visina plafona')

        if str(getattr(state, "measurement_mode", "standard")).lower() == "pro":
            _pm = room.get("pro_measurements", {}) or {}
            _wm = _pm.get(_active) or _pm.get(_kitchen_wall) or {}
            _off_colors = {'0': '#111827', '300': '#7C3AED', '600': '#B45309'}
            for _off_i, _off in enumerate(("0", "300", "600")):
                _row = (_wm.get(_off) or _wm.get(str(_off)) or {})
                for _h in ("0", "1000", "2000", "2500"):
                    _v = _row.get(_h)
                    if not isinstance(_v, (int, float)) or _v <= 0:
                        continue
                    _yy = min(h - 0.03, max(0.03, int(_h) * s + 0.03 + _off_i * 0.03))
                    _len = max(0.02, min(float(_v) * s, w))
                    _col = _off_colors.get(_off, '#374151')
                    _txt = f'{int(_v)} ({int(int(_off)/10)}cm)'
                    if _kitchen_wall == "A":
                        _dim_line_x(0.0, _len, _yy, 0.10 + _off_i * 0.02, _col, _txt)
                    elif _kitchen_wall == "B":
                        _dim_line_z(0.0, min(_len, d), _yy, w - 0.10 - _off_i * 0.02, _col, _txt)
                    else:
                        _dim_line_z(0.0, min(_len, d), _yy, 0.10 + _off_i * 0.02, _col, _txt)

        def _select_wall(k: str, event=None):
            room["active_wall"] = k
            # Sačuvaj poslednju kliknutu 3D poziciju po zidu (u mm) za precizno dodavanje.
            try:
                if event is not None and getattr(event, "hits", None):
                    _hit = event.hits[0]
                    if k == "A":
                        _x_mm = int(max(0, min(wl, round(float(_hit.x) / s))))
                    elif k == "B":
                        _x_mm = int(max(0, min(depth_mm, round(float(_hit.z) / s))))
                    else:
                        _x_mm = int(max(0, min(depth_mm, round(float(_hit.z) / s))))
                    refs["scene_pick"] = {"wall": str(k), "x_mm": _x_mm}
            except Exception as ex:
                _LOG.debug("3D scene pick parse failed: %s", ex)
            wall_headline_refresh()
            wall_compass_refresh()
            openings_list_refresh()
            opening_selected_info_refresh()
            wall_preview_refresh()
            scene_refresh()

        try:
            _abox.on_click(lambda e: _select_wall("A", e))
            _bbox.on_click(lambda e: _select_wall("B", e))
            _cbox.on_click(lambda e: _select_wall("C", e))
        except Exception as ex:
            _LOG.debug("3D wall click-bind failed: %s", ex)

        _fx3d = {'voda': '#67E8F9', 'struja': '#FCD34D', 'gas': '#FCA5A5'}

        def _select_opening_3d(wkey: str, idx: int):
            room["active_wall"] = str(wkey or "A").upper()
            refs['selected_open_idx'][0] = int(idx)
            openings_list_refresh()
            opening_selected_info_refresh()
            wall_headline_refresh()
            wall_compass_refresh()
            wall_preview_refresh()
            scene_refresh()

        def _draw_back_wall_items(wall: dict):
            for _idx, op in enumerate(wall.get('openings', [])):
                _ot = str(op.get('type', 'prozor'))
                ox1 = op['x_mm'] * s
                ox2 = (op['x_mm'] + op['width_mm']) * s
                _fw = op['width_mm'] * s
                _fh = op['height_mm'] * s
                _y_mm = 0 if _ot == 'vrata' else int(op.get('y_mm', 0) or 0)
                oy1 = max(0.0, min(h - _fh, (_y_mm * s)))
                oy2 = oy1 + _fh
                _cx = ox1 + _fw / 2
                _cy = oy1 + _fh / 2
                if _ot == 'vrata':
                    _door_shape = scene.box(_fw, _fh, 0.065).move(_cx, _cy, 0.035).material('#D6B58A', opacity=0.95)
                    _dt = 0.014
                    _d1 = scene.box(_fw + _dt, _dt, 0.014).move(_cx, oy1 + _fh + _dt / 2, 0.067).material('#111111', opacity=0.98)
                    scene.box(_dt, _fh + _dt, 0.014).move(ox1 - _dt / 2, _cy, 0.067).material('#111111', opacity=0.98)
                    scene.box(_dt, _fh + _dt, 0.014).move(ox1 + _fw + _dt / 2, _cy, 0.067).material('#111111', opacity=0.98)
                    scene.box(0.012, 0.032, 0.02).move(ox1 + _fw - 0.045, oy1 + _fh * 0.5, 0.075).material('#2D3748', opacity=1.0)
                    try:
                        _door_shape.on_click(lambda e, idx=_idx: _select_opening_3d('A', idx))
                        _d1.on_click(lambda e, idx=_idx: _select_opening_3d('A', idx))
                    except Exception as ex:
                        _LOG.debug("3D opening click-bind failed (back door idx=%s): %s", _idx, ex)
                else:
                    _win_shape = scene.box(_fw, _fh, 0.05).move(_cx, _cy, 0.03).material('#93C5FD', opacity=0.55)
                    _wt = 0.018
                    _z = 0.058
                    _w1 = scene.box(_fw + _wt, _wt, 0.016).move(_cx, oy1 + _fh + _wt / 2, _z).material('#111111', opacity=0.98)
                    scene.box(_fw + _wt, _wt, 0.016).move(_cx, oy1 - _wt / 2, _z).material('#111111', opacity=0.98)
                    scene.box(_wt, _fh + _wt, 0.016).move(ox1 - _wt / 2, _cy, _z).material('#111111', opacity=0.98)
                    scene.box(_wt, _fh + _wt, 0.016).move(ox1 + _fw + _wt / 2, _cy, _z).material('#111111', opacity=0.98)
                    try:
                        _win_shape.on_click(lambda e, idx=_idx: _select_opening_3d('A', idx))
                        _w1.on_click(lambda e, idx=_idx: _select_opening_3d('A', idx))
                    except Exception as ex:
                        _LOG.debug("3D opening click-bind failed (back window idx=%s): %s", _idx, ex)
                _dim_line_x(ox1, ox2, oy2 + 0.05, 0.07, _dim_col_open, f'{int(op["width_mm"])}')
                _dim_line_y(oy1, oy2, ox2 + 0.04, 0.07, _dim_col_open, f'{int(op["height_mm"])}')
            for fx in wall.get('fixtures', []):
                fc = _fx3d.get(fx['type'], '#DDD')
                scene.box(0.08, 0.08, 0.08).move(fx['x_mm'] * s, fx['y_mm'] * s, 0.05).material(fc, opacity=0.9)

        def _draw_left_wall_items(wall: dict):
            for _idx, op in enumerate(wall.get('openings', [])):
                _ot = str(op.get('type', 'prozor'))
                oz1 = op['x_mm'] * s
                oz2 = (op['x_mm'] + op['width_mm']) * s
                _fw = op['width_mm'] * s
                _fh = op['height_mm'] * s
                _y_mm = 0 if _ot == 'vrata' else int(op.get('y_mm', 0) or 0)
                oy1 = max(0.0, min(hb - _fh, (_y_mm * s)))
                oy2 = oy1 + _fh
                _cz = oz1 + _fw / 2
                _cy = oy1 + _fh / 2
                if _ot == 'vrata':
                    _door_shape = scene.box(0.065, _fh, _fw).move(0.035, _cy, _cz).material('#D6B58A', opacity=0.95)
                    _dt = 0.014
                    _d1 = scene.box(0.014, _dt, _fw + _dt).move(0.067, oy1 + _fh + _dt / 2, _cz).material('#111111', opacity=0.98)
                    scene.box(0.014, _fh + _dt, _dt).move(0.067, _cy, oz1 - _dt / 2).material('#111111', opacity=0.98)
                    scene.box(0.014, _fh + _dt, _dt).move(0.067, _cy, oz1 + _fw + _dt / 2).material('#111111', opacity=0.98)
                    scene.box(0.02, 0.032, 0.012).move(0.075, oy1 + _fh * 0.5, oz1 + _fw - 0.045).material('#2D3748', opacity=1.0)
                    try:
                        _door_shape.on_click(lambda e, idx=_idx: _select_opening_3d('B', idx))
                        _d1.on_click(lambda e, idx=_idx: _select_opening_3d('B', idx))
                    except Exception as ex:
                        _LOG.debug("3D opening click-bind failed (left door idx=%s): %s", _idx, ex)
                else:
                    _win_shape = scene.box(0.05, _fh, _fw).move(0.03, _cy, _cz).material('#93C5FD', opacity=0.55)
                    _wt = 0.018
                    _x = 0.058
                    _w1 = scene.box(0.016, _wt, _fw + _wt).move(_x, oy1 + _fh + _wt / 2, _cz).material('#111111', opacity=0.98)
                    scene.box(0.016, _wt, _fw + _wt).move(_x, oy1 - _wt / 2, _cz).material('#111111', opacity=0.98)
                    scene.box(0.016, _fh + _wt, _wt).move(_x, _cy, oz1 - _wt / 2).material('#111111', opacity=0.98)
                    scene.box(0.016, _fh + _wt, _wt).move(_x, _cy, oz1 + _fw + _wt / 2).material('#111111', opacity=0.98)
                    try:
                        _win_shape.on_click(lambda e, idx=_idx: _select_opening_3d('B', idx))
                        _w1.on_click(lambda e, idx=_idx: _select_opening_3d('B', idx))
                    except Exception as ex:
                        _LOG.debug("3D opening click-bind failed (left window idx=%s): %s", _idx, ex)
                scene.box(0.008, 0.008, max(0.02, abs(oz2 - oz1))).move(0.10, oy2 + 0.05, (oz1 + oz2) / 2).material(_dim_col_open, opacity=0.95)
                _dim_line_y(oy1, oy2, 0.12, (oz1 + oz2) / 2, _dim_col_open, f'{int(op["height_mm"])}')
            for fx in wall.get('fixtures', []):
                fc = _fx3d.get(fx['type'], '#DDD')
                scene.box(0.08, 0.08, 0.08).move(0.05, fx['y_mm'] * s, fx['x_mm'] * s).material(fc, opacity=0.9)

        def _draw_right_wall_items(wall: dict):
            for _idx, op in enumerate(wall.get('openings', [])):
                _ot = str(op.get('type', 'prozor'))
                oz1 = op['x_mm'] * s
                oz2 = (op['x_mm'] + op['width_mm']) * s
                _fw = op['width_mm'] * s
                _fh = op['height_mm'] * s
                _y_mm = 0 if _ot == 'vrata' else int(op.get('y_mm', 0) or 0)
                oy1 = max(0.0, min(hc - _fh, (_y_mm * s)))
                oy2 = oy1 + _fh
                _cz = oz1 + _fw / 2
                _cy = oy1 + _fh / 2
                if _ot == 'vrata':
                    _door_shape = scene.box(0.065, _fh, _fw).move(w - 0.035, _cy, _cz).material('#D6B58A', opacity=0.95)
                    _dt = 0.014
                    _d1 = scene.box(0.014, _dt, _fw + _dt).move(w - 0.067, oy1 + _fh + _dt / 2, _cz).material('#111111', opacity=0.98)
                    scene.box(0.014, _fh + _dt, _dt).move(w - 0.067, _cy, oz1 - _dt / 2).material('#111111', opacity=0.98)
                    scene.box(0.014, _fh + _dt, _dt).move(w - 0.067, _cy, oz1 + _fw + _dt / 2).material('#111111', opacity=0.98)
                    scene.box(0.02, 0.032, 0.012).move(w - 0.075, oy1 + _fh * 0.5, oz1 + _fw - 0.045).material('#2D3748', opacity=1.0)
                    try:
                        _door_shape.on_click(lambda e, idx=_idx: _select_opening_3d('C', idx))
                        _d1.on_click(lambda e, idx=_idx: _select_opening_3d('C', idx))
                    except Exception as ex:
                        _LOG.debug("3D opening click-bind failed (right door idx=%s): %s", _idx, ex)
                else:
                    _win_shape = scene.box(0.05, _fh, _fw).move(w - 0.03, _cy, _cz).material('#93C5FD', opacity=0.55)
                    _wt = 0.018
                    _x = w - 0.058
                    _w1 = scene.box(0.016, _wt, _fw + _wt).move(_x, oy1 + _fh + _wt / 2, _cz).material('#111111', opacity=0.98)
                    scene.box(0.016, _wt, _fw + _wt).move(_x, oy1 - _wt / 2, _cz).material('#111111', opacity=0.98)
                    scene.box(0.016, _fh + _wt, _wt).move(_x, _cy, oz1 - _wt / 2).material('#111111', opacity=0.98)
                    scene.box(0.016, _fh + _wt, _wt).move(_x, _cy, oz1 + _fw + _wt / 2).material('#111111', opacity=0.98)
                    try:
                        _win_shape.on_click(lambda e, idx=_idx: _select_opening_3d('C', idx))
                        _w1.on_click(lambda e, idx=_idx: _select_opening_3d('C', idx))
                    except Exception as ex:
                        _LOG.debug("3D opening click-bind failed (right window idx=%s): %s", _idx, ex)
                scene.box(0.008, 0.008, max(0.02, abs(oz2 - oz1))).move(w - 0.10, oy2 + 0.05, (oz1 + oz2) / 2).material(_dim_col_open, opacity=0.95)
                _dim_line_y(oy1, oy2, w - 0.12, (oz1 + oz2) / 2, _dim_col_open, f'{int(op["height_mm"])}')
            for fx in wall.get('fixtures', []):
                fc = _fx3d.get(fx['type'], '#DDD')
                scene.box(0.08, 0.08, 0.08).move(w - 0.05, fx['y_mm'] * s, fx['x_mm'] * s).material(fc, opacity=0.9)

        _draw_back_wall_items(wall_a)
        _draw_left_wall_items(wall_b)
        _draw_right_wall_items(wall_c)

        cam_dist = max(w, d) * 1.10
        eye_y = h * 0.62
        tgt_y = h * 0.45
        _view = str(camera_view.get('value', 'front'))
        # ── P1-4: frontalni ugao — blagi 20° nagib ka desno, pokazuje dubinu ormarića ──
        _FRONT_YAW = math.radians(20)
        # Finalne koordinate kamere i mete (menjaju se po granama ispod)
        _fcam_x, _fcam_y, _fcam_z = w * 0.5, eye_y, cam_dist
        _ftgt_x, _ftgt_y, _ftgt_z = w * 0.5, tgt_y, 0.0
        if _view == "top":
            # Čist frontalni pogled (referentni, bez ugla)
            _move_camera_y_up(scene, x=_fcam_x, y=_fcam_y, z=_fcam_z, look_at_x=_ftgt_x, look_at_y=_ftgt_y, look_at_z=_ftgt_z)
        elif _view == "front":
            # Blagi 3/4 ugao: kamera ~20° desno od fronte — vidi se bok i dubina korpusa
            _fcam_x = w * 0.5 + cam_dist * math.sin(_FRONT_YAW)
            _fcam_z = cam_dist * math.cos(_FRONT_YAW)
            _move_camera_y_up(scene, x=_fcam_x, y=_fcam_y, z=_fcam_z, look_at_x=_ftgt_x, look_at_y=_ftgt_y, look_at_z=_ftgt_z)
        elif _view in ("B",):
            _fcam_x, _fcam_z = -cam_dist, d * 0.5
            _ftgt_x, _ftgt_z = 0.0, d * 0.5
            _move_camera_y_up(scene, x=_fcam_x, y=_fcam_y, z=_fcam_z, look_at_x=_ftgt_x, look_at_y=_ftgt_y, look_at_z=_ftgt_z)
        elif _view in ("C",):
            _fcam_x, _fcam_z = w + cam_dist, d * 0.5
            _ftgt_x, _ftgt_z = w, d * 0.5
            _move_camera_y_up(scene, x=_fcam_x, y=_fcam_y, z=_fcam_z, look_at_x=_ftgt_x, look_at_y=_ftgt_y, look_at_z=_ftgt_z)
        elif _view == "diag":
            _rad = math.radians(float(diag_yaw.get('value', 45)))
            _cx, _cz = w * 0.5, d * 0.5
            _fcam_x = _cx + math.cos(_rad) * cam_dist
            _fcam_z = _cz + math.sin(_rad) * cam_dist
            _ftgt_x, _ftgt_z = _cx, _cz
            _move_camera_y_up(
                scene,
                x=_fcam_x,
                y=_fcam_y,
                z=_fcam_z,
                look_at_x=_ftgt_x,
                look_at_y=_ftgt_y,
                look_at_z=_ftgt_z,
            )
        elif _view in ("A",):
            # Zid A čisti front (bez ugla — eksplicitni "A" view)
            _move_camera_y_up(scene, x=_fcam_x, y=_fcam_y, z=_fcam_z, look_at_x=_ftgt_x, look_at_y=_ftgt_y, look_at_z=_ftgt_z)
        else:
            _move_camera_y_up(scene, x=_fcam_x, y=_fcam_y, z=_fcam_z, look_at_x=_ftgt_x, look_at_y=_ftgt_y, look_at_z=_ftgt_z)
        # Polar angle iz vektora kamera→meta (za OrbitControls zaključavanje)
        _dp_lock = max(1e-6, ((_fcam_x - _ftgt_x) ** 2 + (_fcam_y - _ftgt_y) ** 2 + (_fcam_z - _ftgt_z) ** 2) ** 0.5)
        _polar_lock = math.acos(max(-1.0, min(1.0, (_fcam_y - _ftgt_y) / _dp_lock)))
        _lock_scene_to_horizontal_orbit(
            ui,
            scene,
            cam_x=_fcam_x,
            cam_y=_fcam_y,
            cam_z=_fcam_z,
            target_x=_ftgt_x,
            target_y=_ftgt_y,
            target_z=_ftgt_z,
            polar_angle=_polar_lock,
            delay_s=0.35,
        )
