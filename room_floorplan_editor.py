# -*- coding: utf-8 -*-
from __future__ import annotations

import base64
import io
import math
from typing import Any, Callable

import matplotlib as _mpl

_mpl.use("Agg")
import matplotlib.pyplot as _plt
import matplotlib.patches as _mpatches


def render_room_floorplan_editor(
    *,
    ui: Any,
    room: dict,
    state: Any,
    ensure_room_walls: Callable[[dict], list],
    get_room_wall: Callable[[dict, str], dict],
    refs: dict,
    opening_types: dict,
    fixture_types: dict,
    wall_headline_refresh: Callable[[], None],
    wall_compass_refresh: Callable[[], None],
    wall_preview_refresh: Callable[[], None],
    scene_refresh: Callable[[], None],
    openings_list_refresh: Callable[[], None],
    fixtures_list_refresh: Callable[[], None],
    opening_selected_info_refresh: Callable[[], None],
    on_show_3d: Callable[[], None] | None = None,
) -> None:
    """Simple room editor: one place to add by click and move by drag & drop."""
    ensure_room_walls(room)

    if "simple_tool" not in refs:
        refs["simple_tool"] = "prozor"
    if "plan_drag" not in refs:
        refs["plan_drag"] = {"kind": None, "wall": None, "idx": None, "active": False}
    if "plan_add_drag" not in refs:
        refs["plan_add_drag"] = {"active": False, "start_x": 0.0, "start_y": 0.0, "moved": False}
    if "plan_skip_click" not in refs:
        refs["plan_skip_click"] = False

    wall_a = get_room_wall(room, "A")
    wall_b = get_room_wall(room, "B")
    wall_c = get_room_wall(room, "C")
    wl = int(wall_a.get("length_mm", room.get("wall_length_mm", 3000)))
    rd = int(room.get("room_depth_mm", 3000))
    rd = max(rd, int(wall_b.get("length_mm", rd)), int(wall_c.get("length_mm", rd)))

    with ui.card().props("id=room-floorplan-card").classes("w-full p-3 border border-gray-200"):
        ui.label("Dodavanje i pomeranje na jednom mestu").classes("text-sm font-bold text-gray-800")
        ui.label("Izaberi alat, klikni na zid za dodavanje, pa prevuci element ako treba pomeranje.").classes(
            "text-xs text-gray-600"
        )
        if callable(on_show_3d):
            ui.button("3D prikaz", on_click=on_show_3d).props("dense outlined").classes("text-xs mt-1")

        with ui.row().classes("w-full gap-2 flex-wrap mt-1"):
            def _set_tool(t: str) -> None:
                refs["simple_tool"] = t
                floorplan.refresh()

            tools = [
                ("prozor", "Prozor"),
                ("vrata", "Vrata"),
                ("struja", "Uticnica"),
                ("voda", "Voda"),
                ("gas", "Gas"),
            ]
            for key, label in tools:
                active = refs.get("simple_tool") == key
                cls = "bg-white text-gray-900 border-2 border-gray-900" if active else "bg-white text-gray-700 border border-gray-300"
                ui.button(label, on_click=lambda k=key: _set_tool(k)).props("dense").classes(f"text-xs {cls}")

        with ui.row().classes("w-full gap-2 mt-2"):
            refs["simple_w"] = ui.number(value=900, min=100, max=4000, step=10, label="Sirina [mm]").props(
                "dense outlined"
            ).classes("flex-1")
            refs["simple_h"] = ui.number(value=1200, min=100, max=3000, step=10, label="Visina [mm]").props(
                "dense outlined"
            ).classes("flex-1")
            refs["simple_y"] = ui.number(value=0, min=0, max=3000, step=10, label="Y od poda [mm]").props(
                "dense outlined"
            ).classes("flex-1")

        @ui.refreshable
        def floorplan() -> None:
            ensure_room_walls(room)
            wall_a_l = get_room_wall(room, "A")
            wall_b_l = get_room_wall(room, "B")
            wall_c_l = get_room_wall(room, "C")
            _wl = int(wall_a_l.get("length_mm", room.get("wall_length_mm", 3000)))
            _rd = int(room.get("room_depth_mm", 3000))
            _rd = max(_rd, int(wall_b_l.get("length_mm", _rd)), int(wall_c_l.get("length_mm", _rd)))

            mrg = max(250, int(min(_wl, _rd) * 0.08))
            _data_w = float(_wl + 2 * mrg)
            _data_h = float(_rd + 2 * mrg)
            # Adaptivna figura — proporcionalna prostoriji, uvijek vidljivi svi zidovi
            _max_w_px = 900.0
            _max_h_px = 520.0
            _ratio = _data_w / max(_data_h, 1.0)
            if _ratio >= (_max_w_px / _max_h_px):
                _img_w = int(round(_max_w_px))
                _img_h = int(round(max(320.0, _max_w_px / max(_ratio, 1e-6))))
            else:
                _img_h = int(round(_max_h_px))
                _img_w = int(round(max(520.0, _max_h_px * _ratio)))
            _fig_w = _img_w / 100.0
            _fig_h = _img_h / 100.0

            fig = _plt.figure(figsize=(_fig_w, _fig_h), dpi=100)
            ax = fig.add_subplot(111)
            fig.patch.set_facecolor("#f4f5f7")
            ax.set_facecolor("#ffffff")

            ax.set_xlim(-mrg, _wl + mrg)
            ax.set_ylim(_rd + mrg, -mrg)
            ax.set_aspect("equal", adjustable="box")
            # Bez set_aspect("equal") — figura je vec proporcionalna prostoriji

            ax.add_patch(_mpatches.Rectangle((0, 0), _wl, _rd, facecolor="#f8efe1", edgecolor="#111827", linewidth=2.0, zorder=1))
            ax.plot([0, _wl], [_rd, _rd], color="#6b7280", linewidth=1.4, linestyle="--", zorder=2)
            ax.text(_wl * 0.5, -40, "Zid A", ha="center", va="top", fontsize=9, color="#1f2937", fontweight="bold")
            ax.text(-30, _rd * 0.5, "Zid B", ha="right", va="center", fontsize=9, color="#1f2937", rotation=90)
            ax.text(_wl + 30, _rd * 0.5, "Zid C", ha="left", va="center", fontsize=9, color="#1f2937", rotation=-90)

            _oc = {"prozor": "#93C5FD", "vrata": "#86EFAC"}
            for wk in ("A", "B", "C"):
                wobj = get_room_wall(room, wk)
                for i, op in enumerate(wobj.get("openings", [])):
                    x0 = float(op.get("x_mm", 0))
                    ww = float(op.get("width_mm", 800))
                    col = _oc.get(str(op.get("type", "prozor")), "#cbd5e1")
                    if wk == "A":
                        ax.add_patch(_mpatches.Rectangle((x0, -18), ww, 18, facecolor=col, edgecolor="#1f2937", linewidth=1.1, zorder=6))
                    elif wk == "B":
                        ax.add_patch(_mpatches.Rectangle((-18, x0), 18, ww, facecolor=col, edgecolor="#1f2937", linewidth=1.1, zorder=6))
                    else:
                        ax.add_patch(_mpatches.Rectangle((_wl, x0), 18, ww, facecolor=col, edgecolor="#1f2937", linewidth=1.1, zorder=6))
                    if refs.get("plan_drag", {}).get("active") and refs.get("plan_drag", {}).get("idx") == i and refs.get("plan_drag", {}).get("wall") == wk:
                        ax.text(_wl * 0.5, _rd * 0.5, "Pomeranje...", ha="center", va="center", fontsize=10, color="#111827")

            _fc = {"voda": "#67E8F9", "struja": "#FCD34D", "gas": "#FCA5A5"}
            for wk in ("A", "B", "C"):
                wobj = get_room_wall(room, wk)
                for fx in wobj.get("fixtures", []):
                    x0 = float(fx.get("x_mm", 0))
                    col = _fc.get(str(fx.get("type", "struja")), "#d1d5db")
                    if wk == "A":
                        cx, cy = x0, 24
                    elif wk == "B":
                        cx, cy = 24, x0
                    else:
                        cx, cy = _wl - 24, x0
                    ax.add_patch(_mpatches.Circle((cx, cy), radius=11, facecolor=col, edgecolor="#111827", linewidth=1.1, zorder=7))

            ax.set_xticks([])
            ax.set_yticks([])
            fig.tight_layout(pad=0.3)
            fig.canvas.draw()

            pos = ax.get_position()
            refs["plan_t"] = {
                "ax_x0": pos.x0,
                "ax_y0": pos.y0,
                "ax_w": pos.width,
                "ax_h": pos.height,
                "xlim": ax.get_xlim(),
                "ylim": ax.get_ylim(),
                "img_w": float(_img_w),
                "img_h": float(_img_h),
            }

            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=100)
            _plt.close(fig)
            buf.seek(0)
            data_uri = "data:image/png;base64," + base64.b64encode(buf.read()).decode()

            def _event_to_space(ev):
                t = refs.get("plan_t")
                if not t:
                    return None, None
                ix = float(getattr(ev, "image_x", 0))
                iy = float(getattr(ev, "image_y", 0))
                fx = ix / t["img_w"]
                fy = 1.0 - iy / t["img_h"]
                nx = (fx - t["ax_x0"]) / max(t["ax_w"], 1e-6)
                ny = (fy - t["ax_y0"]) / max(t["ax_h"], 1e-6)
                xl = t["xlim"]
                yl = t["ylim"]
                return float(xl[0] + nx * (xl[1] - xl[0])), float(yl[0] + ny * (yl[1] - yl[0]))

            def _nearest_wall(x: float, y: float) -> str:
                da = abs(y - 0)
                db = abs(x - 0)
                dc = abs(x - _wl)
                return "A" if da <= db and da <= dc else ("B" if db <= dc else "C")

            def _wall_coord(wk: str, x: float, y: float) -> int:
                return int(max(0, min(_wl if wk == "A" else _rd, round(x if wk == "A" else y))))

            def _hit_opening(x: float, y: float):
                for wk in ("A", "B", "C"):
                    wobj = get_room_wall(room, wk)
                    for i, op in enumerate(wobj.get("openings", [])):
                        ox = float(op.get("x_mm", 0))
                        ow = float(op.get("width_mm", 800))
                        if wk == "A" and (ox <= x <= ox + ow) and (-22 <= y <= 6):
                            return ("opening", wk, i)
                        if wk == "B" and (-22 <= x <= 6) and (ox <= y <= ox + ow):
                            return ("opening", wk, i)
                        if wk == "C" and (_wl - 6 <= x <= _wl + 22) and (ox <= y <= ox + ow):
                            return ("opening", wk, i)
                return None

            def _hit_fixture(x: float, y: float):
                for wk in ("A", "B", "C"):
                    wobj = get_room_wall(room, wk)
                    for i, fx in enumerate(wobj.get("fixtures", [])):
                        fx_x = float(fx.get("x_mm", 0))
                        if wk == "A":
                            cx, cy = fx_x, 24.0
                        elif wk == "B":
                            cx, cy = 24.0, fx_x
                        else:
                            cx, cy = _wl - 24.0, fx_x
                        if math.hypot(x - cx, y - cy) <= 16:
                            return ("fixture", wk, i)
                return None

            def _on_mouse(ev):
                def _add_item_at(xp: float, yp: float) -> None:
                    wk = _nearest_wall(xp, yp)
                    room["active_wall"] = wk
                    wall_headline_refresh()
                    wall_compass_refresh()
                    pos = _wall_coord(wk, xp, yp)
                    tool = str(refs.get("simple_tool", "prozor"))
                    if tool in ("prozor", "vrata"):
                        ww = int((refs.get("simple_w").value if refs.get("simple_w") is not None else 900) or 900)
                        hh = int((refs.get("simple_h").value if refs.get("simple_h") is not None else 1200) or 1200)
                        yy = int((refs.get("simple_y").value if refs.get("simple_y") is not None else 0) or 0)
                        if tool == "vrata":
                            yy = 0
                        lim = _wl if wk == "A" else _rd
                        pos_clamped = int(max(0, min(max(0, lim - ww), pos)))
                        get_room_wall(room, wk).setdefault("openings", []).append(
                            {"type": tool, "wall": wk, "x_mm": pos_clamped, "width_mm": ww, "height_mm": hh, "y_mm": yy}
                        )
                    else:
                        yy = int((refs.get("simple_y").value if refs.get("simple_y") is not None else 300) or 300)
                        lim = _wl if wk == "A" else _rd
                        pos_clamped = int(max(0, min(lim, pos)))
                        get_room_wall(room, wk).setdefault("fixtures", []).append(
                            {"type": tool, "wall": wk, "x_mm": pos_clamped, "y_mm": yy}
                        )
                    openings_list_refresh()
                    fixtures_list_refresh()
                    opening_selected_info_refresh()
                    wall_preview_refresh()
                    scene_refresh()
                    floorplan.refresh()

                etype = str(getattr(ev, "type", "") or "").lower()
                x, y = _event_to_space(ev)
                if x is None:
                    return
                drag = refs.get("plan_drag", {})
                add_drag = refs.get("plan_add_drag", {})

                if etype == "mousedown":
                    hit = _hit_opening(x, y) or _hit_fixture(x, y)
                    if hit:
                        drag["kind"], drag["wall"], drag["idx"] = hit
                        drag["active"] = True
                        refs["plan_drag"] = drag
                        room["active_wall"] = str(drag["wall"]).upper()
                        wall_headline_refresh()
                        wall_compass_refresh()
                        return
                    add_drag["active"] = True
                    add_drag["start_x"] = float(x)
                    add_drag["start_y"] = float(y)
                    add_drag["moved"] = False
                    refs["plan_add_drag"] = add_drag
                    return

                if etype == "mousemove" and drag.get("active"):
                    wk = str(drag.get("wall", "A"))
                    idx = int(drag.get("idx", -1))
                    if idx < 0:
                        return
                    room["active_wall"] = wk
                    wall_headline_refresh()
                    wall_compass_refresh()
                    if drag.get("kind") == "opening":
                        arr = get_room_wall(room, wk).get("openings", [])
                        if 0 <= idx < len(arr):
                            op = arr[idx]
                            ow = int(op.get("width_mm", 800))
                            v = _wall_coord(wk, x, y)
                            mx = (_wl if wk == "A" else _rd) - ow
                            op["x_mm"] = int(max(0, min(mx, v)))
                    else:
                        arr = get_room_wall(room, wk).get("fixtures", [])
                        if 0 <= idx < len(arr):
                            fx = arr[idx]
                            v = _wall_coord(wk, x, y)
                            mx = _wl if wk == "A" else _rd
                            fx["x_mm"] = int(max(0, min(mx, v)))
                    floorplan.refresh()
                    wall_preview_refresh()
                    scene_refresh()
                    openings_list_refresh()
                    fixtures_list_refresh()
                    opening_selected_info_refresh()
                    return

                if etype == "mousemove" and add_drag.get("active"):
                    if math.hypot(float(x) - float(add_drag.get("start_x", x)), float(y) - float(add_drag.get("start_y", y))) >= 8:
                        add_drag["moved"] = True
                        refs["plan_add_drag"] = add_drag
                    return

                if etype == "mouseup":
                    if drag.get("active"):
                        drag["active"] = False
                        refs["plan_drag"] = drag
                        refs["plan_skip_click"] = True
                        return
                    if add_drag.get("active"):
                        if add_drag.get("moved"):
                            _add_item_at(x, y)
                            refs["plan_skip_click"] = True
                        add_drag["active"] = False
                        add_drag["moved"] = False
                        refs["plan_add_drag"] = add_drag
                    return

                if etype == "click":
                    if bool(refs.get("plan_skip_click")):
                        refs["plan_skip_click"] = False
                        return
                    if _hit_opening(x, y) or _hit_fixture(x, y):
                        return
                    _add_item_at(x, y)

            ui.interactive_image(
                data_uri,
                on_mouse=_on_mouse,
                events=["mousedown", "mousemove", "mouseup", "click"],
            ).classes("w-full").style(
                "width:100%;max-width:900px;height:56vh;min-height:320px;max-height:560px;object-fit:contain;display:block;cursor:crosshair;margin:0 auto;"
            )

        floorplan()
