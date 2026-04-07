# -*- coding: utf-8 -*-
from __future__ import annotations

import time

from layout_engine import solve_layout
from i18n import CANVAS_ERR_FMT
from ui_image_utils import fig_to_data_uri_exact
from ui_panels_helpers import format_user_error




def render_nacrt(*, ui, state, tr_fn, plt, render_fn, wall_len_h, zone_baseline_and_height, ensure_room_walls, get_room_wall, nacrt_refresh, sidebar_refresh, logger, add_module_fn=None, templates=None) -> None:
    try:
        _design_wall_key = str(
            (state.room or {}).get('active_wall', (state.room or {}).get('kitchen_wall', 'A')) or 'A'
        ).upper()
        try:
            ensure_room_walls(state.room)
            _design_wall = get_room_wall(state.room, _design_wall_key)
            state.kitchen.setdefault('wall', {})
            state.kitchen['language'] = str(getattr(state, 'language', 'sr') or 'sr').lower().strip()
            state.kitchen['active_wall_key'] = _design_wall_key
            state.kitchen.setdefault('wall_lengths_mm', {})[_design_wall_key] = int(_design_wall.get('length_mm', state.kitchen.get('wall', {}).get('length_mm', 3000)) or 3000)
            state.kitchen.setdefault('wall_heights_mm', {})[_design_wall_key] = int(_design_wall.get('height_mm', state.kitchen.get('wall', {}).get('height_mm', 2600)) or 2600)
            state.kitchen['wall']['length_mm'] = int(_design_wall.get('length_mm', state.kitchen.get('wall', {}).get('length_mm', 3000)) or 3000)
            state.kitchen['wall']['height_mm'] = int(_design_wall.get('height_mm', state.kitchen.get('wall', {}).get('height_mm', 2600)) or 2600)
        except Exception as ex:
            logger.debug("Design wall sync failed: %s", ex)
        _wl, _wh = wall_len_h(state.kitchen)
        # Dodatni padding da natpisi/kote ne budu odsečeni pri gustoj mreži (npr. 5 mm)
        _margin_x = 380
        _margin_y = 380
        # ── Adaptivne dimenzije figure — visina ograničena na ~5in (600px) ────
        # Skala se računa prema visini, tako da se cela kuhinja vidi bez skrola
        _TARGET_H = 5.0          # inches (= 600px @ 120dpi) — dobar fit za FullHD
        _scale = _TARGET_H / max(_wh + _margin_y, 1)
        # Širina po sadržaju; ali uvek pravimo "landscape" format (aspect ≥ 1.6)
        # da bi slika sa width:100% imala odgovarajuću visinu na ekranu
        _content_w = (_wl + _margin_x) * _scale
        _fig_h = max(3.0, _TARGET_H)
        _fig_w = max(_content_w, _fig_h * 2.25)   # širi canvas da desna ivica/kote uvek stanu
        fig = plt.figure(figsize=(_fig_w, _fig_h))
        ax = fig.add_subplot(111)
        _is_catalog = str(state.view_mode).lower().strip() != "tehnički"
        fig.patch.set_facecolor("#BFBDBA" if _is_catalog else "white")
        _kitchen_wall_key = _design_wall_key
        render_fn(
            ax=ax,
            kitchen=state.kitchen,
            view_mode=state.view_mode,
            show_grid=bool(state.show_grid),
            grid_mm=int(state.grid_mm),
            show_bounds=bool(state.show_bounds),
            kickboard=True,
            ceiling_filler=bool(state.ceiling_filler),
            room=getattr(state, 'room', None),
            wall_key=_kitchen_wall_key,
        )

        # ── Preklop otvora i instalacija prostorije (zid A) ───────────────────
        try:
            ensure_room_walls(state.room)
            _wall_cur = get_room_wall(state.room, _kitchen_wall_key)
            _ops = _wall_cur.get('openings', [])
            _fxs = _wall_cur.get('fixtures', [])
            _op_colors = {'prozor': '#93C5FD', 'vrata': '#86EFAC'}
            _fx_colors = {'voda': '#67E8F9', 'struja': '#FCD34D', 'gas': '#FCA5A5'}
            for op in _ops:
                oc = _op_colors.get(op.get('type'), '#DDD')
                ax.add_patch(plt.Rectangle(
                    (op.get('x_mm', 0), op.get('y_mm', 0)),
                    op.get('width_mm', 0), op.get('height_mm', 0),
                    facecolor=oc, edgecolor='#1F2937',
                    linewidth=1.2, alpha=0.30, zorder=5,
                ))
            for fx in _fxs:
                fc = _fx_colors.get(fx.get('type'), '#DDD')
                ax.add_patch(plt.Circle(
                    (fx.get('x_mm', 0), fx.get('y_mm', 0)),
                    radius=20,
                    facecolor=fc, edgecolor='#111827',
                    linewidth=1.0, alpha=0.6, zorder=6,
                ))
        except Exception as ex:
            logger.debug("2D openings/fixtures overlay render failed: %s", ex)

        # ── Tamni overlay na editovanom elementu ──────────────────────────────
        if state.selected_edit_id > 0:
            _sel_mods = [
                m for m in (state.kitchen.get('modules', []) or [])
                if str(m.get('wall_key', 'A')).upper() == _kitchen_wall_key
            ]
            _sel_m = next((m for m in _sel_mods
                           if int(m.get('id', -1)) == state.selected_edit_id), None)
            if _sel_m:
                _sx    = int(_sel_m.get('x_mm', 0))
                _sw    = int(_sel_m.get('w_mm', 0))
                _sh    = int(_sel_m.get('h_mm', 0))
                _szone = str(_sel_m.get('zone', 'base')).lower()

                # Izračunaj Y poziciju — posebna logika za wall_upper
                if _szone == 'wall_upper':
                    _zones   = state.kitchen.get('zones', {}) or {}
                    _wgap    = int((_zones.get('wall', {}) or {}).get('gap_from_base_mm', 0))
                    if _wgap == 0:
                        _wgap = (int(state.kitchen.get('foot_height_mm', 100))
                                 + int(state.kitchen.get('base_korpus_h_mm', 720))
                                 + int(round(float((state.kitchen.get('worktop', {}) or {}).get('thickness', 4.0)) * 10.0))
                                 + int(state.kitchen.get('vertical_gap_mm', 600)))
                    _wbelow  = next((mm for mm in _sel_mods
                                     if str(mm.get('zone', '')).lower() == 'wall'
                                     and int(mm.get('x_mm', -1)) == _sx), None)
                    _sy0 = _wgap + (int(_wbelow.get('h_mm', 0)) if _wbelow else 0)
                elif _szone == 'tall_top':
                    _foot = int(state.kitchen.get('foot_height_mm', 100))
                    _tbelow = next(
                        (
                            mm for mm in _sel_mods
                            if str(mm.get('zone', '')).lower() == 'tall'
                            and int(mm.get('x_mm', 0)) < (_sx + _sw)
                            and (int(mm.get('x_mm', 0)) + int(mm.get('w_mm', 0))) > _sx
                        ),
                        None
                    )
                    if _tbelow:
                        _tid_b = str(_tbelow.get('template_id', '')).upper()
                        if 'FRIDGE' in _tid_b:
                            _sy0 = int(_tbelow.get('h_mm', 2100))
                        else:
                            _sy0 = _foot + int(_tbelow.get('h_mm', 2100))
                    else:
                        _wall_h = int(state.kitchen.get('wall', {}).get('height_mm', 2600))
                        _sy0 = _wall_h - _sh - 50
                else:
                    try:
                        _sy0, _ = zone_baseline_and_height(state.kitchen, _szone)
                    except Exception as ex:
                        logger.debug("Selected module baseline resolve failed: %s", ex)
                        _sy0 = 0

                # ── Selected state: CAD tamni okvir (bez plave popune) ───────
                _sel_border = 2
                ax.add_patch(plt.Rectangle(
                    (_sx - _sel_border, _sy0 - _sel_border),
                    _sw + 2 * _sel_border, _sh + 2 * _sel_border,
                    fill=False, facecolor='none',
                    edgecolor='#1F2937', linewidth=2.0, zorder=27,
                ))

        # ── Stabilan raspored ose (bez "skakanja" pri promeni mreže) ────────
        fig.subplots_adjust(left=0.02, right=0.99, bottom=0.02, top=0.995)
        fig.canvas.draw()
        _ax_pos = ax.get_position()
        _xlim   = ax.get_xlim()
        _ylim   = ax.get_ylim()
        _img_w  = _fig_w * 120.0
        _img_h  = _fig_h * 120.0

        state._nacrt_t = {
            'ax_x0': _ax_pos.x0, 'ax_y0': _ax_pos.y0,
            'ax_w':  _ax_pos.width, 'ax_h': _ax_pos.height,
            'xlim': _xlim, 'ylim': _ylim,
            'img_w': _img_w, 'img_h': _img_h,
        }

        # Bounding-box svakog modula u mm (za hit-test)
        _all_mods = [
            m for m in (state.kitchen.get('modules', []) or [])
            if str(m.get('wall_key', 'A')).upper() == _kitchen_wall_key
        ]
        _bboxes = []
        for _m in _all_mods:
            _mid  = int(_m.get('id', 0))
            _mx   = float(_m.get('x_mm', 0))
            _mw   = float(_m.get('w_mm', 0))
            _mh   = float(_m.get('h_mm', 0))
            _mz   = str(_m.get('zone', 'base')).lower()
            if _mz == 'wall_upper':
                _zones_bb = state.kitchen.get('zones', {}) or {}
                _wgap_bb  = int((_zones_bb.get('wall', {}) or {}).get('gap_from_base_mm', 0))
                if _wgap_bb == 0:
                    _wgap_bb = (int(state.kitchen.get('foot_height_mm', 100))
                                + int(state.kitchen.get('base_korpus_h_mm', 720))
                                + int(round(float((state.kitchen.get('worktop', {}) or {}).get('thickness', 4.0)) * 10.0))
                                + int(state.kitchen.get('vertical_gap_mm', 600)))
                _wb = next((mm for mm in _all_mods
                             if str(mm.get('zone', '')).lower() == 'wall'
                             and int(mm.get('x_mm', -1)) == int(_mx)), None)
                _my0 = _wgap_bb + (int(_wb.get('h_mm', 0)) if _wb else 0)
            elif _mz == 'tall_top':
                _foot_bb = int(state.kitchen.get('foot_height_mm', 100))
                _tb = next(
                    (
                        mm for mm in _all_mods
                        if str(mm.get('zone', '')).lower() == 'tall'
                        and int(mm.get('x_mm', 0)) < (_mx + _mw)
                        and (int(mm.get('x_mm', 0)) + int(mm.get('w_mm', 0))) > _mx
                    ),
                    None
                )
                if _tb:
                    _tid_tb = str(_tb.get('template_id', '')).upper()
                    if 'FRIDGE' in _tid_tb:
                        _my0 = int(_tb.get('h_mm', 2100))
                    else:
                        _my0 = _foot_bb + int(_tb.get('h_mm', 2100))
                else:
                    _wall_h_bb = int(state.kitchen.get('wall', {}).get('height_mm', 2600))
                    _my0 = _wall_h_bb - int(_mh) - 50
            else:
                try:
                    _my0, _ = zone_baseline_and_height(state.kitchen, _mz)
                except Exception as ex:
                    logger.debug("BBox baseline resolve failed for module id=%s: %s", _mid, ex)
                    _my0 = 0
            _bboxes.append({'id': _mid, 'x': _mx, 'y': _my0, 'w': _mw, 'h': _mh})
        state._nacrt_mods = _bboxes

        data_uri = fig_to_data_uri_exact(fig)
        plt.close(fig)

        # ── Drag state ────────────────────────────────────────────────────────
        if not hasattr(state, "_nacrt_drag"):
            state._nacrt_drag = {
                "active": False,
                "module_id": None,
                "start_mm_x": 0.0,
                "offset_x": 0.0,
                "orig_x": 0,
                "last_refresh": 0.0,
                "did_move": False,
                "zone_orig_x": {},  # originalne x_mm pozicije svih elemenata u zoni na drag start
                "_just_finished": False,  # blokira spurious click koji browser salje odmah nakon mouseup+drag
            }

        def _event_to_mm(e):
            _t = getattr(state, '_nacrt_t', None)
            if not _t:
                return None, None
            _ix = float(getattr(e, 'image_x', 0))
            _iy = float(getattr(e, 'image_y', 0))

            # Pikseli slike → frakcija figure (y obrnuto)
            _fx = _ix / _t['img_w']
            _fy = 1.0 - _iy / _t['img_h']

            # Frakcija figure → normalizovano unutar axes
            _nx = (_fx - _t['ax_x0']) / max(_t['ax_w'], 1e-6)
            _ny = (_fy - _t['ax_y0']) / max(_t['ax_h'], 1e-6)

            # Normalizovano → mm
            _xl = _t['xlim']; _yl = _t['ylim']
            _mm_x = _xl[0] + _nx * (_xl[1] - _xl[0])
            _mm_y = _yl[0] + _ny * (_yl[1] - _yl[0])
            return _mm_x, _mm_y

        def _hit_module_id(mm_x: float, mm_y: float) -> int:
            _ml = getattr(state, '_nacrt_mods', [])
            # Od vrha ka dnu (zadnji nacrtani ima prioritet)
            for _mb in reversed(_ml):
                if (_mb['x'] <= mm_x <= _mb['x'] + _mb['w'] and
                        _mb['y'] <= mm_y <= _mb['y'] + _mb['h']):
                    return int(_mb['id'])
            return -1

        def _on_nacrt_mouse(e):
            _etype = str(getattr(e, 'type', '') or '').lower()
            _drag = state._nacrt_drag
            _mods = [
                m for m in (state.kitchen.get('modules', []) or [])
                if str(m.get('wall_key', 'A')).upper() == _kitchen_wall_key
            ]

            def _clearance():
                try:
                    _mfg = state.kitchen.get("manufacturing", {}) or {}
                    return (
                        int(_mfg.get("mounting_tolerance_left_mm", 5)),
                        int(_mfg.get("mounting_tolerance_right_mm", 5)),
                    )
                except Exception:
                    return 5, 5

            def _finalize_drag(set_just_finished=False):
                _cid_f = int(_drag.get("module_id") or 0)
                _mod_f = next((m for m in _mods if int(m.get('id', -1)) == _cid_f), None)
                _did_f = bool(_drag.get("did_move", False))
                _drag["active"] = False
                _drag["module_id"] = None
                _drag["_just_finished"] = bool(set_just_finished)
                if _mod_f and _did_f:
                    _zone_f = str(_mod_f.get('zone', 'base')).lower().strip()
                    solve_layout(state.kitchen, zone=_zone_f, mode='pack', wall_key=_kitchen_wall_key)
                    nacrt_refresh()
                    sidebar_refresh()
                else:
                    for _om in _mods:
                        _oid = int(_om.get('id', 0))
                        if _oid in _drag.get("zone_orig_x", {}):
                            _om['x_mm'] = _drag["zone_orig_x"][_oid]
                    nacrt_refresh()

            if _etype == 'mousedown':
                _drag["_just_finished"] = False
                if int(getattr(e, 'button', 0)) != 0:
                    return
                _mm_x, _mm_y = _event_to_mm(e)
                if _mm_x is None:
                    return
                _cid = _hit_module_id(_mm_x, _mm_y)
                if _cid <= 0:
                    if _drag.get("active"):
                        _finalize_drag()
                    return
                _mod = next((m for m in _mods if int(m.get('id', -1)) == _cid), None)
                if not _mod:
                    return
                _zone = str(_mod.get('zone', 'base')).lower().strip()
                if _zone in ('wall_upper', 'tall_top'):
                    ui.notify(tr_fn('canvas.notify_overlap_drag'), type='warning')
                    return
                _drag.update({
                    "active": True,
                    "module_id": _cid,
                    "start_mm_x": float(_mm_x),
                    "offset_x": float(_mm_x) - float(_mod.get('x_mm', 0)),
                    "orig_x": int(_mod.get('x_mm', 0)),
                    "did_move": False,
                    "last_refresh": 0.0,
                    "zone_orig_x": {
                        int(m.get('id', 0)): int(m.get('x_mm', 0))
                        for m in _mods
                        if str(m.get('zone', '')).lower().strip() == _zone
                    },
                })
                state.selected_edit_id = _cid
                state.mode = "edit"
                nacrt_refresh()
                sidebar_refresh()
                return

            if _etype == 'mousemove' and _drag.get("active") and _drag.get("module_id"):
                _raw_buttons = getattr(e, 'buttons', None)
                if _raw_buttons is not None and int(_raw_buttons) == 0:
                    _finalize_drag(set_just_finished=False)
                    return

                _mm_x, _mm_y = _event_to_mm(e)
                if _mm_x is None:
                    return

                _cid = int(_drag["module_id"])
                _mod = next((m for m in _mods if int(m.get('id', -1)) == _cid), None)
                if not _mod:
                    _drag["active"] = False
                    return
                _zone = str(_mod.get('zone', 'base')).lower().strip()
                _wall_len = int(state.kitchen.get('wall', {}).get('length_mm', 3000))
                _m_w = int(_mod.get('w_mm', 0))
                _left, _right = _clearance()
                _max_x = max(_left, _wall_len - _right - _m_w)

                _snap = max(5, int(state.grid_mm) if bool(state.show_grid) and int(state.grid_mm) > 0 else 10)
                _new_x = int(round((float(_mm_x) - float(_drag["offset_x"])) / _snap) * _snap)
                _new_x = max(_left, min(_new_x, _max_x))

                _orig = _drag.get("zone_orig_x", {})
                _best_snap = None
                _best_dist = 81
                for _om in _mods:
                    _oid = int(_om.get('id', 0))
                    if str(_om.get('zone', '')).lower().strip() != _zone or _oid == _cid:
                        continue
                    _ox = int(_orig.get(_oid, int(_om.get('x_mm', 0))))
                    _ow = int(_om.get('w_mm', 0))
                    d1 = abs(_new_x - (_ox + _ow))
                    if d1 < _best_dist:
                        _best_dist = d1
                        _best_snap = _ox + _ow
                    d2 = abs((_new_x + _m_w) - _ox)
                    if d2 < _best_dist:
                        _best_dist = d2
                        _best_snap = _ox - _m_w
                if _best_snap is not None:
                    _new_x = max(_left, min(int(_best_snap), _max_x))

                if int(_mod.get('x_mm', 0)) != _new_x:
                    _drag["did_move"] = True
                    for _om in _mods:
                        _oid = int(_om.get('id', 0))
                        if _oid != _cid and _oid in _orig:
                            _om['x_mm'] = _orig[_oid]
                    _mod['x_mm'] = int(_new_x)
                    _now = time.monotonic()
                    if _now - float(_drag.get("last_refresh", 0.0)) >= 0.06:
                        _drag["last_refresh"] = _now
                        nacrt_refresh()
                return

            if _etype == 'mouseleave':
                if _drag.get("active"):
                    _finalize_drag(set_just_finished=False)
                return

            if _etype == 'mouseup':
                if _drag.get("active"):
                    _was_drag = _drag.get("did_move", False)
                    _finalize_drag(set_just_finished=_was_drag)
                return

            if _etype == 'click':
                if _drag.get("_just_finished"):
                    _drag["_just_finished"] = False
                    return
                _mm_x, _mm_y = _event_to_mm(e)
                if _mm_x is None:
                    return
                _cid = _hit_module_id(_mm_x, _mm_y)
                if _cid > 0:
                    if state.selected_edit_id == _cid:
                        state.selected_edit_id = 0
                        state.mode = "add"
                    else:
                        state.selected_edit_id = _cid
                        state.mode = "edit"
                elif (state.mode == "add"
                      and str(getattr(state, 'selected_tid', '') or '').strip()
                      and callable(add_module_fn)
                      and templates is not None):
                    _tid = str(state.selected_tid)
                    _tmpl = (templates or {}).get(_tid, {}) or {}
                    _defs = _tmpl.get('defaults', {}) or {}
                    _tmpl_zone = str(_tmpl.get('zone', 'base'))
                    _zd = (state.zone_defaults or {}).get(_tmpl_zone, {}) or {}
                    _snap_c = max(5, int(state.grid_mm) if bool(state.show_grid) and int(state.grid_mm) > 0 else 10)
                    try:
                        add_module_fn(
                            template_id=_tid,
                            zone=_tmpl_zone,
                            x_mm=int(round(float(_mm_x) / _snap_c) * _snap_c),
                            w_mm=int(_defs.get('w_mm') or 600),
                            h_mm=int(_zd.get('h_mm') or _defs.get('h_mm') or 720),
                            d_mm=int(_zd.get('d_mm') or _defs.get('d_mm') or 560),
                            label=str(_tmpl.get('label', _tid)),
                        )
                        ui.notify(tr_fn('canvas.notify_added', label=_tmpl.get("label", _tid)), type='positive')
                    except Exception as _add_ex:
                        logger.debug("Canvas klik-dodaj greška: %s", _add_ex)
                        ui.notify(format_user_error(_add_ex, getattr(state, 'language', 'sr')), type='negative')
                nacrt_refresh()
                sidebar_refresh()

        ui.interactive_image(
            data_uri,
            on_mouse=_on_nacrt_mouse,
            events=['mousedown', 'mousemove', 'mouseup', 'mouseleave', 'click'],
        ).classes('nacrt-fit-image cursor-pointer').style(
            'width:100%;height:auto;max-width:100%;max-height:100%;object-fit:contain;display:block;'
        )

    except Exception as e:
        ui.label(tr_fn('canvas.err_draw', err=e)).classes('text-red-500')
