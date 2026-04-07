# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from typing import Any, Callable

from i18n import tr

_LOG = logging.getLogger(__name__)


def render_settings_tab(
    *,
    ui: Any,
    state: Any,
    tr_fn: Callable[[str], str],
    get_zone_depth_standard: Callable[[str], int],
    set_zone_depth_standard: Callable[[str, int], int],
    nacrt_refresh: Callable[[], None],
    main_content_refresh: Callable[[], None],
    set_front_color: Callable[[str], None],
    set_material: Callable[[str, Any], None],
    set_wall_length: Callable[[int], None],
    set_wall_height: Callable[[int], None],
    set_foot_height: Callable[[int], None],
    set_worktop_thickness: Callable[[float], None],
    set_base_height: Callable[[int], None],
    set_worktop_width: Callable[[float], None],
    set_worktop_reserve_mm: Callable[[int], None],
    set_worktop_front_overhang_mm: Callable[[int], None],
    set_worktop_field_cut: Callable[[bool], None],
    set_worktop_edge_protection: Callable[[bool], None],
    set_worktop_edge_protection_type: Callable[[str], None],
    set_worktop_joint_type: Callable[[str], None],
    set_vertical_gap: Callable[[int], None],
    set_max_element_height: Callable[[int], None],
    render_color_picker: Callable[..., None],
) -> None:
    _lang = str(getattr(state, "language", "sr") or "sr").lower().strip()

    def _t(key: str, **fmt: object) -> str:
        return tr(key, _lang, **fmt)

    def _refresh_after_dimension_change() -> None:
        try:
            nacrt_refresh()
        except Exception as ex:
            _LOG.debug("Settings tab: nacrt refresh failed after dimension change: %s", ex)
        main_content_refresh()

    def _on_foot_change(v: Any) -> None:
        set_foot_height(int(v))
        _refresh_after_dimension_change()

    def _on_worktop_thk_change(v: Any) -> None:
        set_worktop_thickness(float(v))
        _refresh_after_dimension_change()

    def _on_base_h_change(v: Any) -> None:
        set_base_height(int(v))
        _refresh_after_dimension_change()

    def _bind_number_commit(
        inp: Any,
        *,
        caster: Callable[[Any], Any],
        apply_fn: Callable[[Any], None],
    ) -> None:
        def _commit(_: Any = None) -> None:
            try:
                apply_fn(caster(inp.value))
            except Exception as ex:
                _LOG.debug("Settings tab: number commit failed: %s", ex)
        inp.on("blur", _commit)
        inp.on("keydown.enter", _commit)

    def _field_row(label_text: str, min_label_rem: float = 8.5):
        return ui.row().classes("w-full items-center gap-2").style(
            f"min-height: 2.75rem; --settings-label-width: {min_label_rem}rem;"
        )

    def _render_zone_depth_card() -> None:
        with ui.card().classes("w-full p-4 border border-gray-300 bg-white"):
            ui.label(_t("settings.depth_std_title")).classes("font-bold text-base mb-1 text-gray-800")
            ui.label(_t("settings.depth_std_desc")).classes("text-xs text-gray-500 mb-3")

            _depth_zone_keys = [
                ("base", _t("settings.zone_base")),
                ("wall", _t("settings.zone_wall")),
                ("wall_upper", _t("settings.zone_wall_upper")),
                ("tall", _t("settings.zone_tall")),
            ]

            for _dz_key, _dz_label in _depth_zone_keys:
                _cur_std = get_zone_depth_standard(_dz_key)
                with ui.row().classes("w-full items-center justify-between gap-2 mb-2"):
                    ui.label(_dz_label).classes("text-sm font-medium w-28 whitespace-normal")
                    _dz_inp = ui.number(
                        value=_cur_std,
                        min=100,
                        max=2000,
                        step=10,
                    ).props("dense outlined").classes("w-28")

                    def _apply_zone_std(zone_k=_dz_key, zone_lbl=_dz_label, inp=_dz_inp):
                        new_val = int(inp.value)
                        cur_std = get_zone_depth_standard(zone_k)
                        if new_val == cur_std:
                            ui.notify(_t("settings.depth_already_fmt", zone=zone_lbl, val=new_val), type="info")
                            return
                        with ui.dialog() as _dlg_std:
                            with ui.card().classes("p-4 gap-2 min-w-80"):
                                ui.label(
                                    _t("settings.depth_dialog_title_fmt", zone=zone_lbl, old=cur_std, new=new_val)
                                ).classes("font-bold text-sm")
                                ui.label(_t("settings.depth_dialog_ask")).classes(
                                    "text-sm text-gray-600 mt-1 whitespace-normal"
                                )
                                ui.label(_t("settings.depth_dialog_note")).classes(
                                    "text-xs text-gray-400 whitespace-normal"
                                )
                                with ui.row().classes("w-full mt-3 gap-2"):
                                    def _yes(zk=zone_k, nv=new_val, lbl=zone_lbl, dlg=_dlg_std):
                                        n = set_zone_depth_standard(zk, nv, update_existing=True)
                                        dlg.close()
                                        ui.notify(
                                            _t("settings.notify_updated_fmt", zone=lbl, val=nv, count=n),
                                            type="positive",
                                        )
                                        nacrt_refresh()
                                        main_content_refresh()

                                    def _no(zk=zone_k, nv=new_val, lbl=zone_lbl, dlg=_dlg_std):
                                        set_zone_depth_standard(zk, nv, update_existing=False)
                                        dlg.close()
                                        ui.notify(
                                            _t("settings.notify_future_fmt", zone=lbl, val=nv),
                                            type="info",
                                        )
                                        main_content_refresh()

                                    ui.button(_t("settings.btn_yes_update"), on_click=_yes).classes("flex-1 text-xs")
                                    ui.button(_t("settings.btn_only_future"), on_click=_no).classes(
                                        "flex-1 bg-gray-100 text-xs"
                                    )
                                    ui.button(_t("project_io.cancel"), on_click=_dlg_std.close).classes("text-xs")
                        _dlg_std.open()

            ui.button(_t("edit.apply"), on_click=_apply_zone_std).props("dense").classes("text-xs px-3 btn-wrap")

    def _render_front_color_card() -> None:
        with ui.card().classes("w-full p-4"):
            ui.label(_t("settings.global_front_title")).classes("font-bold text-base mb-2")
            ui.label(_t("settings.global_front_desc")).classes("text-xs text-gray-500 mb-2")

            _global_color_ref = {
                "value": str(state.front_color or state.kitchen.get("front_color", "#FDFDFB"))
            }

            def _on_global_front_change() -> None:
                set_front_color(str(_global_color_ref.get("value", "#FDFDFB")))
                try:
                    nacrt_refresh()
                except Exception as ex:
                    _LOG.debug("Settings tab: nacrt refresh failed after front color change: %s", ex)
                main_content_refresh()

            _global_color_ref["_on_change"] = _on_global_front_change
            render_color_picker(
                _global_color_ref,
                title=_t("settings.front_decor_title"),
                columns=5,
                swatch_h=38,
                lang=_lang,
            )

    ui.label(_t("settings.title")).classes("text-2xl font-bold mb-4")

    with ui.row().classes("w-full gap-4 flex-wrap items-start"):
        with ui.column().classes("gap-4").style("flex: 0 0 20rem; width: 20rem; min-width: 20rem;"):
            _render_zone_depth_card()
            _render_front_color_card()

        with ui.row().classes("gap-4 flex-wrap items-start").style("flex: 1 1 0; min-width: 52rem;"):
            with ui.card().classes("p-4").style("flex: 1 1 26rem; min-width: 24rem; max-width: 28rem;"):
                ui.label(_t("settings.materials_title")).classes("font-bold text-base mb-3")
                mats = state.kitchen.get("materials", {})
                _carcass_options = {
                    "Iverica": _t("settings.material_chipboard_carcass"),
                    "MDF": _t("settings.material_mdf_carcass"),
                    "Ã…Â per ploÃ„Âa": _t("settings.material_plywood_carcass"),
                    "Puno drvo": _t("settings.material_solid_wood_carcass"),
                }
                _front_options = {
                    "MDF": _t("settings.material_mdf_front"),
                    "Iverica": _t("settings.material_chipboard_front"),
                    "Akril": _t("settings.material_acrylic_front"),
                    "Furnir": _t("settings.material_veneer_front"),
                    "Lakobel": _t("settings.material_lacobel_front"),
                }

                with ui.column().classes("w-full gap-2"):
                    with _field_row(tr_fn("settings.carcass_material"), 9.8):
                        ui.label(tr_fn("settings.carcass_material")).classes(
                            "text-sm text-gray-700 shrink-0"
                        ).style("width: var(--settings-label-width);")
                        ui.select(
                            _carcass_options,
                            value=mats.get("carcass_material", "Iverica"),
                            on_change=lambda e: set_material("carcass_material", e.value),
                        ).props("dense borderless").classes("flex-1")
                    with _field_row(tr_fn("settings.front_material"), 9.8):
                        ui.label(tr_fn("settings.front_material")).classes(
                            "text-sm text-gray-700 shrink-0"
                        ).style("width: var(--settings-label-width);")
                        ui.select(
                            _front_options,
                            value=mats.get("front_material", "MDF"),
                            on_change=lambda e: set_material("front_material", e.value),
                        ).props("dense borderless").classes("flex-1")
                    with _field_row(tr_fn("settings.carcass_thk"), 9.8):
                        ui.label(tr_fn("settings.carcass_thk").replace(" [mm]", "")).classes(
                            "text-sm text-gray-700 shrink-0"
                        ).style("width: var(--settings-label-width);")
                        ui.select(
                            [16, 18, 22, 25],
                            value=mats.get("carcass_thk", 18),
                            on_change=lambda e: set_material("carcass_thk", e.value),
                        ).props("dense borderless").classes("flex-1")
                        ui.label("mm").classes("text-sm text-gray-500 shrink-0")
                    with _field_row(tr_fn("settings.front_thk"), 9.8):
                        ui.label(tr_fn("settings.front_thk").replace(" [mm]", "")).classes(
                            "text-sm text-gray-700 shrink-0"
                        ).style("width: var(--settings-label-width);")
                        ui.select(
                            [16, 18, 22, 25],
                            value=mats.get("front_thk", 18),
                            on_change=lambda e: set_material("front_thk", e.value),
                        ).props("dense borderless").classes("flex-1")
                        ui.label("mm").classes("text-sm text-gray-500 shrink-0")
                    with _field_row(tr_fn("settings.back_thk"), 9.8):
                        ui.label(tr_fn("settings.back_thk").replace(" [mm]", "")).classes(
                            "text-sm text-gray-700 shrink-0"
                        ).style("width: var(--settings-label-width);")
                        ui.select(
                            [3, 4, 6, 8],
                            value=mats.get("back_thk", 8),
                            on_change=lambda e: set_material("back_thk", e.value),
                        ).props("dense borderless").classes("flex-1")
                        ui.label("mm").classes("text-sm text-gray-500 shrink-0")
                    with _field_row(tr_fn("settings.abs_thk"), 9.8):
                        ui.label(tr_fn("settings.abs_thk").replace(" [mm]", "")).classes(
                            "text-sm text-gray-700 shrink-0"
                        ).style("width: var(--settings-label-width);")
                        ui.select(
                            [0.4, 1, 2, 3],
                            value=mats.get("edge_abs_thk", 2),
                            on_change=lambda e: set_material("edge_abs_thk", e.value),
                        ).props("dense borderless").classes("flex-1")
                        ui.label("mm").classes("text-sm text-gray-500 shrink-0")

            with ui.card().classes("p-4").style("flex: 1 1 19rem; min-width: 18rem; max-width: 21rem;"):
                ui.label(_t("settings.room_dim_title")).classes("font-bold text-base mb-3")
                with ui.column().classes("w-full gap-2"):
                    with _field_row(tr_fn("settings.wall_width"), 8.8):
                        ui.label(tr_fn("settings.wall_width").replace(" [mm]", "")).classes("text-sm text-gray-700 shrink-0").style(
                            "width: var(--settings-label-width);"
                        )
                        _wall_len_inp = ui.number(
                            value=state.kitchen.get("wall", {}).get("length_mm", 3000),
                            min=500,
                            max=10000,
                            step=10,
                        ).props("dense borderless").classes("flex-1")
                        _bind_number_commit(
                            _wall_len_inp,
                            caster=int,
                            apply_fn=lambda v: (set_wall_length(v), _refresh_after_dimension_change()),
                        )
                        ui.label("mm").classes("text-sm text-gray-500 shrink-0")
                    with _field_row(tr_fn("settings.wall_height"), 8.8):
                        ui.label(tr_fn("settings.wall_height").replace(" [mm]", "")).classes("text-sm text-gray-700 shrink-0").style(
                            "width: var(--settings-label-width);"
                        )
                        _wall_h_inp = ui.number(
                            value=state.kitchen.get("wall", {}).get("height_mm", 2600),
                            min=2000,
                            max=3500,
                            step=10,
                        ).props("dense borderless").classes("flex-1")
                        _bind_number_commit(
                            _wall_h_inp,
                            caster=int,
                            apply_fn=lambda v: (set_wall_height(v), _refresh_after_dimension_change()),
                        )
                        ui.label("mm").classes("text-sm text-gray-500 shrink-0")

            with ui.card().classes("p-4").style("flex: 1 1 19rem; min-width: 18rem; max-width: 21rem;"):
                ui.label(_t("settings.base_params_title")).classes("font-bold text-base mb-3")
                _wt_cfg = dict(state.kitchen.get("worktop", {}) or {})
                with ui.column().classes("w-full gap-2"):
                    with _field_row(tr_fn("settings.foot_height"), 9.2):
                        ui.label(tr_fn("settings.foot_height").replace(" [mm]", "")).classes("text-sm text-gray-700 shrink-0").style(
                            "width: var(--settings-label-width);"
                        )
                        _foot_inp = ui.number(
                            value=state.kitchen.get("foot_height_mm", 100),
                            min=0,
                            max=200,
                            step=10,
                        ).props("dense borderless").classes("flex-1")
                        _bind_number_commit(_foot_inp, caster=int, apply_fn=_on_foot_change)
                        ui.label("mm").classes("text-sm text-gray-500 shrink-0")
                    with _field_row(tr_fn("settings.worktop_thk_cm"), 9.2):
                        ui.label(tr_fn("settings.worktop_thk_cm")).classes("text-sm text-gray-700 shrink-0").style(
                            "width: var(--settings-label-width);"
                        )
                        ui.select(
                            [2.5, 3.0, 3.5, 3.8, 4.0, 4.5, 5.0],
                            value=state.kitchen.get("worktop", {}).get("thickness", 3.8),
                            on_change=lambda e: _on_worktop_thk_change(e.value),
                        ).props("dense borderless").classes("flex-1")
                    with _field_row(tr_fn("settings.base_height"), 9.2):
                        ui.label(tr_fn("settings.base_height").replace(" [mm]", "")).classes("text-sm text-gray-700 shrink-0").style(
                            "width: var(--settings-label-width);"
                        )
                        _base_h_inp = ui.number(
                            value=state.kitchen.get("base_korpus_h_mm", 720),
                            min=500,
                            max=1000,
                            step=10,
                        ).props("dense borderless").classes("flex-1")
                        _bind_number_commit(_base_h_inp, caster=int, apply_fn=_on_base_h_change)
                        ui.label("mm").classes("text-sm text-gray-500 shrink-0")
                    with _field_row(tr_fn("settings.worktop_width"), 9.2):
                        ui.label(tr_fn("settings.worktop_width").replace(" [mm]", "")).classes("text-sm text-gray-700 shrink-0").style(
                            "width: var(--settings-label-width);"
                        )
                        _wt_w_inp = ui.number(
                            value=state.kitchen.get("worktop", {}).get("width", 600),
                            min=400,
                            max=900,
                            step=10,
                        ).props("dense borderless").classes("flex-1")
                        _bind_number_commit(
                            _wt_w_inp,
                            caster=int,
                            apply_fn=lambda v: (set_worktop_width(v), nacrt_refresh()),
                        )
                        ui.label("mm").classes("text-sm text-gray-500 shrink-0")
                    with _field_row(tr_fn("settings.worktop_reserve"), 9.2):
                        ui.label(tr_fn("settings.worktop_reserve").replace(" [mm]", "")).classes("text-sm text-gray-700 shrink-0").style(
                            "width: var(--settings-label-width);"
                        )
                        _wt_res_inp = ui.number(
                            value=_wt_cfg.get("mounting_reserve_mm", 20),
                            min=0,
                            max=50,
                            step=1,
                        ).props("dense borderless").classes("flex-1")
                        _bind_number_commit(
                            _wt_res_inp,
                            caster=int,
                            apply_fn=lambda v: (set_worktop_reserve_mm(v), nacrt_refresh()),
                        )
                        ui.label("mm").classes("text-sm text-gray-500 shrink-0")
                    with _field_row(tr_fn("settings.worktop_overhang"), 9.2):
                        ui.label(tr_fn("settings.worktop_overhang").replace(" [mm]", "")).classes("text-sm text-gray-700 shrink-0").style(
                            "width: var(--settings-label-width);"
                        )
                        _wt_ov_inp = ui.number(
                            value=_wt_cfg.get("front_overhang_mm", 20),
                            min=0,
                            max=50,
                            step=1,
                        ).props("dense borderless").classes("flex-1")
                        _bind_number_commit(
                            _wt_ov_inp,
                            caster=int,
                            apply_fn=lambda v: (set_worktop_front_overhang_mm(v), nacrt_refresh()),
                        )
                        ui.label("mm").classes("text-sm text-gray-500 shrink-0")
                    with _field_row(tr_fn("settings.worktop_joint_type"), 9.2):
                        ui.label(tr_fn("settings.worktop_joint_type")).classes("text-sm text-gray-700 shrink-0").style(
                            "width: var(--settings-label-width);"
                        )
                        ui.select(
                            {
                                "STRAIGHT": tr_fn("settings.worktop_joint_straight"),
                                "MITER_45": tr_fn("settings.worktop_joint_miter"),
                            },
                            value=_wt_cfg.get("joint_type", "STRAIGHT"),
                            on_change=lambda e: set_worktop_joint_type(e.value),
                        ).props("dense borderless").classes("flex-1")
                    with _field_row(tr_fn("settings.worktop_field_cut"), 9.2):
                        ui.label(tr_fn("settings.worktop_field_cut")).classes("text-sm text-gray-700 shrink-0").style(
                            "width: var(--settings-label-width);"
                        )
                        ui.select(
                            {True: tr_fn("settings.worktop_field_cut_yes"), False: tr_fn("settings.worktop_field_cut_no")},
                            value=bool(_wt_cfg.get("field_cut", True)),
                            on_change=lambda e: set_worktop_field_cut(bool(e.value)),
                        ).props("dense borderless").classes("flex-1")
                    with _field_row(tr_fn("settings.worktop_edge_protection"), 9.2):
                        ui.label(tr_fn("settings.worktop_edge_protection")).classes("text-sm text-gray-700 shrink-0").style(
                            "width: var(--settings-label-width);"
                        )
                        ui.select(
                            {True: tr_fn("settings.worktop_edge_protection_yes"), False: tr_fn("settings.worktop_edge_protection_no")},
                            value=bool(_wt_cfg.get("edge_protection", True)),
                            on_change=lambda e: set_worktop_edge_protection(bool(e.value)),
                        ).props("dense borderless").classes("flex-1")
                    with _field_row(tr_fn("settings.worktop_edge_protection_type"), 9.2):
                        ui.label(tr_fn("settings.worktop_edge_protection_type")).classes("text-sm text-gray-700 shrink-0").style(
                            "width: var(--settings-label-width);"
                        )
                        ui.input(
                            value=str(_wt_cfg.get("edge_protection_type", "silikon / vodootporni premaz")),
                            on_change=lambda e: set_worktop_edge_protection_type(str(e.value or "")),
                        ).props("dense borderless").classes("flex-1")
                _cutout_modules = []
                for _m in state.kitchen.get("modules", []) or []:
                    _tid = str(_m.get("template_id", "") or "").upper()
                    if _tid == "SINK_BASE":
                        _cutout_modules.append("Sudopera" if _lang != "en" else "Sink")
                    elif _tid in {"BASE_COOKING_UNIT", "BASE_HOB"}:
                        _cutout_modules.append("Ploča za kuvanje" if _lang != "en" else "Hob")
                _cutout_modules = list(dict.fromkeys(_cutout_modules))
                foot = state.kitchen.get("foot_height_mm", 100)
                base = state.kitchen.get("base_korpus_h_mm", 720)
                wt = int(round(float(state.kitchen.get("worktop", {}).get("thickness", 3.8)) * 10))
                ui.label(
                    _t("settings.worktop_top_edge_fmt", total=foot + base + wt, foot=foot, base=base, wt=wt)
                ).classes("text-xs text-gray-700 mt-2 whitespace-normal break-words")
                with ui.card().classes("w-full mt-3 p-3 bg-gray-50 border border-gray-200"):
                    ui.label(tr_fn("settings.worktop_rules_title")).classes("text-sm font-bold text-gray-800 mb-1")
                    ui.label(tr_fn("settings.worktop_rules_global")).classes("text-xs text-gray-700 whitespace-normal")
                    ui.label(tr_fn("settings.worktop_rules_cutouts")).classes("text-xs text-gray-700 whitespace-normal")
                    if _cutout_modules:
                        ui.label(
                            tr_fn("settings.worktop_rules_cutout_modules", modules=", ".join(_cutout_modules))
                        ).classes("text-xs text-gray-700 whitespace-normal")
                    else:
                        ui.label(tr_fn("settings.worktop_rules_cutout_none")).classes("text-xs text-gray-500 whitespace-normal")

            with ui.card().classes("p-4").style("flex: 1 1 19rem; min-width: 18rem; max-width: 21rem;"):
                ui.label(_t("settings.wall_params_title")).classes("font-bold text-base mb-3")
                with ui.column().classes("w-full gap-2"):
                    with _field_row(tr_fn("settings.wall_gap"), 9.2):
                        ui.label(tr_fn("settings.wall_gap").replace(" [mm]", "")).classes("text-sm text-gray-700 shrink-0").style(
                            "width: var(--settings-label-width);"
                        )
                        _gap_inp = ui.number(
                            value=state.kitchen.get("vertical_gap_mm", 600),
                            min=400,
                            max=1000,
                            step=10,
                        ).props("dense borderless").classes("flex-1")
                        _bind_number_commit(
                            _gap_inp,
                            caster=int,
                            apply_fn=lambda v: (set_vertical_gap(v), _refresh_after_dimension_change()),
                        )
                        ui.label("mm").classes("text-sm text-gray-500 shrink-0")
                    with _field_row(tr_fn("settings.max_height"), 9.2):
                        ui.label(tr_fn("settings.max_height").replace(" [mm]", "")).classes("text-sm text-gray-700 shrink-0").style(
                            "width: var(--settings-label-width);"
                        )
                        _max_h_inp = ui.number(
                            value=state.kitchen.get(
                                "max_element_height",
                                state.kitchen.get("wall", {}).get("height_mm", 2600) - 50,
                            ),
                            min=1000,
                            max=3000,
                            step=10,
                        ).props("dense borderless").classes("flex-1")
                        _bind_number_commit(
                            _max_h_inp,
                            caster=int,
                            apply_fn=lambda v: (set_max_element_height(v), _refresh_after_dimension_change()),
                        )
                        ui.label("mm").classes("text-sm text-gray-500 shrink-0")
                foot = state.kitchen.get("foot_height_mm", 100)
                base = state.kitchen.get("base_korpus_h_mm", 720)
                wt = int(round(float(state.kitchen.get("worktop", {}).get("thickness", 3.8)) * 10))
                gap = state.kitchen.get("vertical_gap_mm", 600)
                wall_bottom = foot + base + wt + gap
                wall_h = state.kitchen.get("wall", {}).get("height_mm", 2600)
                max_h = state.kitchen.get("max_element_height", wall_h - 50)
                ui.label(_t("settings.upper_bottom_fmt", val=wall_bottom)).classes(
                    "text-xs text-gray-700 mt-1 whitespace-normal break-words"
                )
                ui.label(
                    _t("settings.upper_height_fmt", h=max_h - wall_bottom, bottom=wall_bottom, max_h=max_h)
                ).classes("text-xs text-gray-700 whitespace-normal break-words")
