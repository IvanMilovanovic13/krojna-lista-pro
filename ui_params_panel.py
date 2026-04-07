# -*- coding: utf-8 -*-
from __future__ import annotations

from i18n import tr
from i18n import (
    BTN_OTKAZI,
    GRAIN_HORZ,
    GRAIN_NONE,
    GRAIN_VERT,
    PARAMS_ADD_OK_FMT,
    PARAMS_DEPTH_DIALOG_TITLE_FMT,
    PARAMS_DEPTH_INDEPENDENT_FMT,
    PARAMS_DEPTH_ONLY_THIS_FMT,
    PARAMS_DEPTH_SET_OK_FMT,
    PARAMS_DEPTH_SET_STD_FMT,
    PARAMS_DEPTH_STANDARD_FMT,
    PARAMS_DOOR_H_LABEL,
    PARAMS_DOOR_DRAWER,
    PARAMS_DRAWERS_TITLE,
    PARAMS_DRAWERS_COUNT,
    PARAMS_DRAWER_H_FMT,
    PARAMS_DRAWER_LABEL_FMT,
    PARAMS_DRAWER_MIN_WARN_FMT,
    PARAMS_DRAWER_OK_FMT,
    PARAMS_DRAWER_REMAINING_FMT,
    PARAMS_DRAWER_TOO_SMALL_FMT,
    PARAMS_ERR_FMT,
    PARAMS_INNER_H_FMT,
    PARAMS_MAX_H_FMT,
    PARAMS_OVEN_DRAWER_TITLE,
    PARAMS_OVEN_STD_H_FMT,
    PARAMS_RECALC,
    PARAMS_RECALC_BTN,
    PARAMS_SHELVES,
    PARAMS_SHELVES_COUNT,
    PARAMS_SHELVES_SPACING_FMT,
    PARAMS_SHELVES_SUGGEST_FMT,
    PARAMS_WHAT_TO_DO,
)
from ui_panels_helpers import format_user_error
from ui_catalog_config import translate_template_label
from module_rules import (
    default_shelf_count,
    dishwasher_installation_metrics,
    module_supports_adjustable_shelves,
)
from drawer_logic import rebalance_drawers_proportional, redistribute_drawers_proportional

_FREESTANDING_TIDS = {
    "BASE_DISHWASHER_FREESTANDING",
    "BASE_OVEN_HOB_FREESTANDING",
    "TALL_FRIDGE_FREESTANDING",
}

def render_params_panel(
    *,
    ui,
    state,
    templates,
    logger,
    is_independent_depth,
    get_zone_depth_standard,
    max_allowed_h_for_zone,
    set_zone_depth_standard,
    suggest_corner_neighbor_guidance,
    find_first_free_x,
    add_module_instance_local,
    nacrt_refresh,
    sidebar_refresh,
    set_sidebar_primary_action,
    params_panel_refresh,
    l_odaberi_element,
    l_sirina_mm,
    l_visina_mm,
    l_dubina_mm,
    l_smer_goda,
    l_naziv,
    l_strana_rucke,
    l_iznad_kog_gornjeg,
    m_nema_gornjih_1_red,
    b_dodaj_na_zid,
) -> None:
    _lang = str(getattr(state, 'language', 'sr') or 'sr').lower().strip()
    def _t(key: str, **fmt: object) -> str:
        return tr(key, _lang, **fmt)

    if not state.selected_tid:
        set_sidebar_primary_action(None)
        with ui.column().classes('w-full items-center py-6 gap-2'):
            ui.icon('touch_app').classes('text-3xl text-gray-200')
            ui.label(l_odaberi_element).classes(
                'text-xs text-gray-400 text-center'
            )
        return

    tmpl = templates.get(state.selected_tid, {})
    # get_templates() vraća flatten strukturu — w_mm/h_mm/d_mm su top-level ključevi,
    # a ne unutar "defaults" pod-dikt-a. Rekonstruišemo defaults za uniforman pristup.
    defaults = {
        'w_mm': int(tmpl.get('w_mm', 600)),
        'h_mm': int(tmpl.get('h_mm', 720)),
        'd_mm': int(tmpl.get('d_mm', 560)),
    }
    label = translate_template_label(
        tmpl.get("label", state.selected_tid),
        _lang,
        tmpl.get("label_i18n"),
    )
    zone = str(tmpl.get("zone", "base"))
    tid = str(state.selected_tid or "").upper()
    _active_wall = str((getattr(state, 'room', {}) or {}).get('active_wall', 'A') or 'A').upper()
    _corner_guidance = suggest_corner_neighbor_guidance(zone, _active_wall, tid)

    # ── Separator + "Dodaj" section header ───────────────────────────────────
    ui.separator().classes('my-1')
    with ui.element('div').classes('px-2 pt-2 pb-0.5'):
        ui.label(label).classes('text-[11px] font-bold text-gray-700')

    with ui.element('div').classes('px-2 pb-2'):

        # ── Depth standard logika ─────────────────────────────────────────────
        _is_indep = is_independent_depth(state.selected_tid)
        _zone_std_d = get_zone_depth_standard(zone)

        _zd = state.zone_defaults.get(zone, {})
        _use_template_defaults = tid in _FREESTANDING_TIDS
        if zone not in ('tall', 'tall_top'):
            _h_val = defaults.get('h_mm', 720) if _use_template_defaults else _zd.get('h_mm', defaults.get('h_mm', 720))
        else:
            _h_val = defaults.get('h_mm', 2100)
        if _is_indep:
            _d_val = defaults.get('d_mm', 560)
        elif zone not in ('tall', 'tall_top'):
            _d_val = _zone_std_d
        else:
            _d_val = defaults.get('d_mm', 560)

        _max_h = max_allowed_h_for_zone(zone, tid)

        # ── Mutable tracker za dimenzije (zaštita od NiceGUI async desync) ────
        # Problem: korisnik unese vrednost u browser, klikne dugme, ali Python-side
        # .value još uvek ima staru vrednost (WebSocket kasnjenje ili stale closure).
        # Rešenje: eksplicitno pratimo vrednost kroz on_change i čuvamo u _dim dict-u.
        _dim = {
            'w': int(defaults.get('w_mm', 600)),
            'h': int(min(_h_val, _max_h)),
            'd': int(_d_val),
        }

        def _on_w_change(e):
            try:
                _dim['w'] = max(100, min(3000, int(float(e.value))))
            except Exception:
                pass

        def _on_h_change(e):
            try:
                _dim['h'] = max(100, min(_max_h, int(float(e.value))))
            except Exception:
                pass

        def _on_d_change(e):
            try:
                _dim['d'] = max(100, min(2000, int(float(e.value))))
            except Exception:
                pass

        # ── Dimension inputs (pregledno, bez sečenja labela) ──────────────────
        with ui.column().classes('w-full gap-1 mt-1'):
            with ui.row().classes('w-full gap-1'):
                w = ui.number(
                    label=l_sirina_mm, value=defaults.get('w_mm', 600),
                    min=100, max=3000, step=10,
                    on_change=_on_w_change,
                ).props('dense outlined').classes('flex-1 min-w-0')
                w.on('update:model-value', _on_w_change)
                h = ui.number(
                    label=l_visina_mm, value=min(_h_val, _max_h),
                    min=100, max=_max_h, step=10,
                    on_change=_on_h_change,
                ).props('dense outlined').classes('flex-1 min-w-0')
                h.on('update:model-value', _on_h_change)
            d = ui.number(
                label=l_dubina_mm, value=_d_val,
                min=100, max=2000, step=10,
                on_change=_on_d_change,
            ).props('dense outlined').classes('w-full')
            d.on('update:model-value', _on_d_change)
            ui.label(_t("params.max_height_fmt", h=_max_h)).classes(
                'text-[10px] text-gray-500'
            )

        # ── Depth status badge ────────────────────────────────────────────────
        if _is_indep:
            _depth_badge_txt = _t("params.depth_independent_fmt", d=_d_val)
            _depth_badge_cls = 'text-[10px] text-gray-700 bg-gray-50 border border-gray-300 px-2 py-0.5 rounded mt-1'
        else:
            _depth_badge_txt = _t("params.depth_standard_fmt", d=_zone_std_d)
            _depth_badge_cls = 'text-[10px] text-gray-700 bg-gray-50 border border-gray-300 px-2 py-0.5 rounded mt-1'
        _depth_status_lbl = ui.label(_depth_badge_txt).classes(_depth_badge_cls)
        if _corner_guidance.get('active'):
            ui.label(str(_corner_guidance.get('message', ''))).classes(
                'text-[10px] text-amber-800 bg-amber-50 border border-amber-200 px-2 py-1 rounded mt-1'
            )

        # ── Smer goda ─────────────────────────────────────────────────────────
        with ui.row().classes('w-full items-center gap-2 mt-1'):
            ui.label(l_smer_goda).classes('text-[10px] text-gray-500 shrink-0')
            grain_sel_add = ui.select(
                {
                    'V': _t("params.grain_vertical"),
                    'H': _t("params.grain_horizontal"),
                    'N': _t("params.grain_none"),
                },
                value='V'
            ).classes('flex-1').props('dense outlined')

        # ── Fioke / Police panel ──────────────────────────────────────────
        features = tmpl.get("features", {})
        has_drawers = features.get("drawers", False)
        has_shelves = module_supports_adjustable_shelves(tid, features=features) and not has_drawers
        has_oven = features.get("oven", False)
        has_door_and_drawer = features.get("doors", False) and features.get("drawers", False)
        has_wardrobe = bool(features.get("wardrobe", False))

        # Konstante
        carcass_thk = float(state.kitchen.get("materials", {}).get("carcass_thk", 18))
        edge_thk = float(state.kitchen.get("materials", {}).get("edge_abs_thk", 2))
        OVEN_H = 595  # standardna visina rerne
        OVEN_D = 550  # standardna dubina rerne
        MIN_DRAWER_H = 80  # minimalna visina fioke
        def _inner_h(corp_h: float) -> float:
            """Unutrašnja visina korpusa (oduzmi dno i plafon)."""
            return corp_h - 2 * carcass_thk

        def _distribute(total: float, n: int, locked: dict) -> list:
            """
            Ravnomerno rasporedi visinu na n fioka.
            locked = {index: visina} — zaključane fioke
            Slobodan prostor ide na nezaključane.
            """
            locked_sum = sum(locked.values())
            free = total - locked_sum
            unlocked = [i for i in range(n) if i not in locked]
            if not unlocked:
                return [locked.get(i, free/n) for i in range(n)]
            per = free / len(unlocked)
            return [locked.get(i, per) for i in range(n)]

        # state holders for dodaj()
        drawer_heights_state = None
        door_h_inp = None
        drawer_h_inp = None
        n_shelves = None
        fioka_h = None
        sink_cutout_x = None
        sink_cutout_w = None
        sink_cutout_d = None
        hob_cutout_x = None
        hob_cutout_w = None
        hob_cutout_d = None
        dishwasher_slot_info = None
        tall_appliance_info = None
        wardrobe_front_style = None
        wardrobe_door_mode = None
        wardrobe_n_shelves = None
        wardrobe_n_shelves_slider = None
        wardrobe_n_drawers = None
        wardrobe_n_drawers_slider = None
        wardrobe_hanger_sections = None
        wardrobe_hanger_sections_slider = None
        wardrobe_to_ceiling = None

        if has_oven and not has_door_and_drawer:
            # Rerna + fioka: rerna je fiksna, ostatak je fioka
            corp_h = float(_dim['h'])
            inner = _inner_h(corp_h)
            fioka_h = max(MIN_DRAWER_H, inner - OVEN_H)
            with ui.card().classes('w-full p-2 bg-gray-50 border border-gray-300 mt-1'):
                ui.label(_t('elements.oven_drawer_title')).classes('font-bold text-xs mb-0')
                ui.label(_t('elements.oven_std_h', h=OVEN_H)).classes('text-xs text-gray-500')
                ui.label(_t('elements.drawer_remaining', h=fioka_h)).classes('text-xs text-gray-700 font-bold')
                _drawer_info = (
                    f'Visina fioke: {fioka_h:.0f} mm'
                    if _lang == 'sr' else
                    f'Drawer height: {fioka_h:.0f} mm'
                )
                _oven_handle_note = (
                    'Ručka rerne je fiksno horizontalna pri vrhu vrata.'
                    if _lang == 'sr' else
                    'The oven handle is fixed horizontally at the top of the door.'
                )
                ui.label(_drawer_info).classes('text-xs text-gray-700')
                ui.label(_oven_handle_note).classes('text-[10px] text-gray-500')
                if fioka_h < MIN_DRAWER_H:
                    ui.label(_t('elements.drawer_min_warn', h=MIN_DRAWER_H)).classes('text-xs text-red-500')

        if tid == "SINK_BASE":
            _default_cut_w = max(400, min(int(_dim['w']) - 80, 500))
            _default_cut_d = max(400, min(int(_dim['d']) - 40, 480))
            _default_cut_x = max(0, int((int(_dim['w']) - _default_cut_w) / 2))
            _sink_title = 'Sudopera - izrez u radnoj ploči' if _lang == 'sr' else 'Sink - worktop cut-out'
            _sink_x_lbl = 'X pozicija izreza [mm]' if _lang == 'sr' else 'Cut-out X position [mm]'
            _sink_w_lbl = 'Širina izreza [mm]' if _lang == 'sr' else 'Cut-out width [mm]'
            _sink_d_lbl = 'Dubina izreza [mm]' if _lang == 'sr' else 'Cut-out depth [mm]'
            _sink_note = (
                'Izrez se radi na licu mesta po šablonu proizvođača sudopere.'
                if _lang == 'sr' else
                "Cut-out is made on site according to the sink manufacturer's template."
            )
            with ui.card().classes('w-full p-2 bg-gray-50 border border-gray-300 mt-1'):
                ui.label(_sink_title).classes('font-bold text-xs mb-1')
                sink_cutout_x = ui.number(label=_sink_x_lbl, value=_default_cut_x, min=0, max=max(0, int(_dim['w']) - 200), step=5).props('dense outlined').classes('w-full')
                sink_cutout_w = ui.number(label=_sink_w_lbl, value=_default_cut_w, min=300, max=max(300, int(_dim['w']) - 40), step=5).props('dense outlined').classes('w-full')
                sink_cutout_d = ui.number(label=_sink_d_lbl, value=_default_cut_d, min=300, max=max(300, int(_dim['d']) - 20), step=5).props('dense outlined').classes('w-full')
                ui.label(_sink_note).classes('text-[10px] text-gray-500')

        if tid in {"BASE_COOKING_UNIT", "BASE_HOB"}:
            _default_hob_w = max(450, min(int(_dim['w']) - 60, 560))
            _default_hob_d = max(400, min(int(_dim['d']) - 40, 490))
            _default_hob_x = max(0, int((int(_dim['w']) - _default_hob_w) / 2))
            _hob_title = 'Ploča za kuvanje - izrez u radnoj ploči' if _lang == 'sr' else 'Hob - worktop cut-out'
            _hob_x_lbl = 'X pozicija izreza [mm]' if _lang == 'sr' else 'Cut-out X position [mm]'
            _hob_w_lbl = 'Širina izreza [mm]' if _lang == 'sr' else 'Cut-out width [mm]'
            _hob_d_lbl = 'Dubina izreza [mm]' if _lang == 'sr' else 'Cut-out depth [mm]'
            _hob_note = (
                'Izrez se radi na licu mesta po šablonu proizvođača ploče za kuvanje.'
                if _lang == 'sr' else
                "Cut-out is made on site according to the hob manufacturer's template."
            )
            with ui.card().classes('w-full p-2 bg-gray-50 border border-gray-300 mt-1'):
                ui.label(_hob_title).classes('font-bold text-xs mb-1')
                hob_cutout_x = ui.number(label=_hob_x_lbl, value=_default_hob_x, min=0, max=max(0, int(_dim['w']) - 200), step=5).props('dense outlined').classes('w-full')
                hob_cutout_w = ui.number(label=_hob_w_lbl, value=_default_hob_w, min=350, max=max(350, int(_dim['w']) - 40), step=5).props('dense outlined').classes('w-full')
                hob_cutout_d = ui.number(label=_hob_d_lbl, value=_default_hob_d, min=300, max=max(300, int(_dim['d']) - 20), step=5).props('dense outlined').classes('w-full')
                ui.label(_hob_note).classes('text-[10px] text-gray-500')

        if tid == "BASE_DISHWASHER":
            _dish = dishwasher_installation_metrics(
                {
                    **state.kitchen,
                    "worktop": state.kitchen.get("worktop", {}) or {},
                },
                {"h_mm": int(_dim['h']), "template_id": tid},
            )
            _dish_title = 'Ugradna mašina za sudove' if _lang == 'sr' else 'Built-in dishwasher'
            _dish_l1 = (
                'Ovo je otvor za ugradni uređaj sa integrisanim frontom, ne puni korpus.'
                if _lang == 'sr' else
                'This is an appliance slot with an integrated front, not a full cabinet carcass.'
            )
            _dish_l2 = (
                'Krojna lista daje veznu letvu i front za MZS.'
                if _lang == 'sr' else
                'The cut list includes the cross rail and the integrated dishwasher front.'
            )
            _dish_l3 = (
                'Proveri prolaz creva i kabla prema instalacijama.'
                if _lang == 'sr' else
                'Check hose and cable routing against the service points.'
            )
            with ui.card().classes('w-full p-2 bg-gray-50 border border-gray-300 mt-1'):
                ui.label(_dish_title).classes('font-bold text-xs mb-1')
                ui.label(_dish_l1).classes('text-[10px] text-gray-600')
                ui.label(_dish_l2).classes('text-[10px] text-gray-600')
                ui.label(_dish_l3).classes('text-[10px] text-gray-500')
                ui.label(
                    (
                        f"Dostupno ispod ploče: {_dish['dishwasher_available_height_under_worktop']} mm"
                        if _lang == 'sr' else
                        f"Available under worktop: {_dish['dishwasher_available_height_under_worktop']} mm"
                    )
                ).classes('text-[10px] text-gray-600')
                ui.label(
                    (
                        f"Standardni front MZS: {_dish['dishwasher_front_height']} mm"
                        if _lang == 'sr' else
                        f"Standard dishwasher front: {_dish['dishwasher_front_height']} mm"
                    )
                ).classes('text-[10px] text-gray-600')
                if _dish["dishwasher_raised_mode"]:
                    ui.label(
                        (
                            f"Raised mode: postolje {_dish['dishwasher_platform_height']} mm + donja maska {_dish['dishwasher_lower_filler_height']} mm"
                            if _lang == 'sr' else
                            f"Raised mode: platform {_dish['dishwasher_platform_height']} mm + lower filler {_dish['dishwasher_lower_filler_height']} mm"
                        )
                    ).classes('text-[10px] font-semibold text-gray-700')

        if tid == "BASE_TRASH":
            _trash_title = 'Sortirnik / kante za otpad' if _lang == 'sr' else 'Waste sorting / bins'
            _trash_l1 = (
                'Ovo je funkcionalni modul sa gotovim izvlaÄnim mehanizmom.'
                if _lang == 'sr' else
                'This is a functional unit with a ready-made pull-out mechanism.'
            )
            _trash_l2 = (
                'Krojna lista daje korpus i front; sortirnik se kupuje kao gotov set.'
                if _lang == 'sr' else
                'The cut list includes the carcass and front; the waste sorter is purchased as a ready-made set.'
            )
            _trash_l3 = (
                'Proveri potreban svetli otvor i kompatibilnost mehanizma sa Å¡irinom korpusa.'
                if _lang == 'sr' else
                'Check the required clear opening and mechanism compatibility with the cabinet width.'
            )
            with ui.card().classes('w-full p-2 bg-gray-50 border border-gray-300 mt-1'):
                ui.label(_trash_title).classes('font-bold text-xs mb-1')
                ui.label(_trash_l1).classes('text-[10px] text-gray-600')
                ui.label(_trash_l2).classes('text-[10px] text-gray-600')
                ui.label(_trash_l3).classes('text-[10px] text-gray-500')

        if tid == "BASE_CORNER":
            _corner_title = 'Ugaoni donji element' if _lang == 'sr' else 'Base corner unit'
            _corner_l1 = (
                'Ovo je ugaoni modul; proveri smer otvaranja fronta prema susednom elementu.'
                if _lang == 'sr' else
                'This is a corner unit; verify the front opening direction against the adjacent unit.'
            )
            _corner_l2 = (
                'Po potrebi dodaj filer ili tehnički razmak za ručku, front i montažu.'
                if _lang == 'sr' else
                'Add a filler or technical gap if needed for the handle, front clearance, and installation.'
            )
            _corner_l3 = (
                'Krojna lista daje ugaoni korpus; ugaona funkcija i pristup zavise od rasporeda zida.'
                if _lang == 'sr' else
                'The cut list includes the corner carcass; corner usability and access depend on the wall layout.'
            )
            with ui.card().classes('w-full p-2 bg-gray-50 border border-gray-300 mt-1'):
                ui.label(_corner_title).classes('font-bold text-xs mb-1')
                ui.label(_corner_l1).classes('text-[10px] text-gray-600')
                ui.label(_corner_l2).classes('text-[10px] text-gray-600')
                ui.label(_corner_l3).classes('text-[10px] text-gray-500')

        if tid == "END_PANEL":
            _end_title = 'Završna bočna ploča' if _lang == 'sr' else 'End side panel'
            _end_l1 = (
                'Ovo je vidljiva završna dekorativna bočna ploča, ne standardna stranica korpusa.'
                if _lang == 'sr' else
                'This is a visible decorative end side panel, not a standard carcass side.'
            )
            _end_l2 = (
                'Dimenzija prati visinu elementa i dubinu završne strane koju zatvara.'
                if _lang == 'sr' else
                'Its size follows the unit height and the finished side depth it closes.'
            )
            _end_l3 = (
                'Proveri smer goda, vidljive ivice i eventualni prepust prema podu ili radnoj ploči.'
                if _lang == 'sr' else
                'Check grain direction, visible edges, and any reveal toward the floor or worktop.'
            )
            with ui.card().classes('w-full p-2 bg-gray-50 border border-gray-300 mt-1'):
                ui.label(_end_title).classes('font-bold text-xs mb-1')
                ui.label(_end_l1).classes('text-[10px] text-gray-600')
                ui.label(_end_l2).classes('text-[10px] text-gray-600')
                ui.label(_end_l3).classes('text-[10px] text-gray-500')

        if tid == "FILLER_PANEL":
            _filler_title = 'Filer panel' if _lang == 'sr' else 'Filler panel'
            _filler_l1 = (
                'Ovo je uska panel-popuna prostora, ne puni korpus.'
                if _lang == 'sr' else
                'This is a narrow space-filling panel, not a full cabinet carcass.'
            )
            _filler_l2 = (
                'Koristi se za završetak reda, nivelaciju zazora i odvajanje fronta od zida.'
                if _lang == 'sr' else
                'Use it to finish a run, tune installation gaps, and separate fronts from the wall.'
            )
            _filler_l3 = (
                'Ako je preširok, razmotri završnu bočnu ploču ili poseban uski modul.'
                if _lang == 'sr' else
                'If it becomes too wide, consider an end side panel or a dedicated narrow unit.'
            )
            with ui.card().classes('w-full p-2 bg-gray-50 border border-gray-300 mt-1'):
                ui.label(_filler_title).classes('font-bold text-xs mb-1')
                ui.label(_filler_l1).classes('text-[10px] text-gray-600')
                ui.label(_filler_l2).classes('text-[10px] text-gray-600')
                ui.label(_filler_l3).classes('text-[10px] text-gray-500')

        if tid in {"TALL_FRIDGE", "TALL_FRIDGE_FREEZER", "TALL_FRIDGE_FREESTANDING"}:
            _fridge_title = 'Visoka kolona za frižider' if _lang == 'sr' else 'Tall fridge column'
            _fridge_l1 = (
                'Ovo je kolona za ugradni frižider; otvor uređaja ne ide kao puni korpus.'
                if _lang == 'sr' else
                'This is a built-in fridge column; the appliance opening is not treated as a full carcass bay.'
            )
            _fridge_l2 = (
                'Krojna lista daje noseće stranice, bazu, plafon i servisne frontove prema tipu modula.'
                if _lang == 'sr' else
                'The cut list includes the supporting sides, base, top panel, and service fronts depending on the module type.'
            )
            _fridge_l3 = (
                'Proveri ventilacione razmake i ugradne mere proizvođača frižidera.'
                if _lang == 'sr' else
                "Check ventilation clearances and the fridge manufacturer's built-in dimensions."
            )
            with ui.card().classes('w-full p-2 bg-gray-50 border border-gray-300 mt-1'):
                ui.label(_fridge_title).classes('font-bold text-xs mb-1')
                ui.label(_fridge_l1).classes('text-[10px] text-gray-600')
                ui.label(_fridge_l2).classes('text-[10px] text-gray-600')
                ui.label(_fridge_l3).classes('text-[10px] text-gray-500')

        if tid in {"TALL_OVEN", "TALL_OVEN_MICRO"}:
            _is_combo = tid == "TALL_OVEN_MICRO"
            _title = 'Visoka kolona za uređaje' if _lang == 'sr' else 'Tall appliance column'
            _l1 = (
                'Donji servisni front ulazi u krojnu listu.'
                if _lang == 'sr' else
                'The lower service front is included in the cut list.'
            )
            _l2 = (
                'Zona rerne i mikrotalasne zatvara se gotovim uređajima.'
                if _is_combo and _lang == 'sr' else
                'The oven and microwave zones are closed by the finished appliances.'
                if _is_combo else
                'Zona rerne zatvara se gotovim uređajem.'
                if _lang == 'sr' else
                'The oven zone is closed by the finished appliance.'
            )
            _l3 = (
                'Proveri ventilaciju i ugradne mere proizvođača.'
                if _lang == 'sr' else
                "Check ventilation clearances and the manufacturer's built-in dimensions."
            )
            with ui.card().classes('w-full p-2 bg-gray-50 border border-gray-300 mt-1'):
                ui.label(_title).classes('font-bold text-xs mb-1')
                ui.label(_l1).classes('text-[10px] text-gray-600')
                ui.label(_l2).classes('text-[10px] text-gray-600')
                ui.label(_l3).classes('text-[10px] text-gray-500')

        elif has_drawers and not has_door_and_drawer:
            # Čiste fioke — nova logika bez locked/distribute
            n_drawers_default = features.get("n_drawers", 3)

            with ui.card().classes('w-full p-2 bg-gray-50 border border-gray-300 mt-1'):
                ui.label(_t('elements.drawers')).classes('font-bold text-xs mb-0')

                # State: samo lista visina i inputi — bez locked
                drawer_heights_state = {'n': n_drawers_default, 'heights': [], 'inputs': {}}
                fioka_container = ui.column().classes('w-full gap-1')
                _p_valid_lbl  = [None]
                _p_prop_html  = [None]   # ref na ui.html za proportion bars
                _P_COLORS = ['#111111', '#2f2f2f', '#4b4b4b',
                             '#676767', '#838383', '#9f9f9f']

                def _p_get_total():
                    return _inner_h(float(_dim['h']))

                def _p_distribute_equal_int(total_mm, count):
                    total_i = int(round(total_mm))
                    count_i = max(1, int(count))
                    base = total_i // count_i
                    rem = total_i - (base * count_i)
                    vals = [base] * count_i
                    vals[0] += rem
                    return vals

                def _p_refresh_valid():
                    total = int(round(_p_get_total()))
                    zbir = sum(drawer_heights_state['heights'])
                    diff = abs(zbir - total)
                    if _p_valid_lbl[0] is not None:
                        if diff < 1:
                            _p_valid_lbl[0].set_text(f'✅ {zbir:.0f} = {total:.0f}mm')
                            _p_valid_lbl[0].classes(remove='text-red-500', add='text-gray-700')
                        else:
                            _warn_hint = 'klikni ↺' if _lang == 'sr' else 'click ↺'
                            _p_valid_lbl[0].set_text(f'⚠️ {zbir:.0f} ≠ {total:.0f}mm — {_warn_hint}')
                            _p_valid_lbl[0].classes(remove='text-gray-700', add='text-red-500')

                def _p_update_prop_bars():
                    """Instant CSS proportion preview u panelu za dodavanje."""
                    if _p_prop_html[0] is None:
                        return
                    heights = drawer_heights_state['heights']
                    if not heights:
                        return
                    total_h = max(1.0, sum(heights))
                    parts = [
                        '<div style="display:flex;flex-direction:column;gap:2px;'
                        'width:100%;height:72px;border-radius:4px;overflow:hidden;">'
                    ]
                    for i, hv in enumerate(heights):
                        grow = max(1, int(hv / total_h * 1000))
                        col  = _P_COLORS[i % len(_P_COLORS)]
                        parts.append(
                            f'<div style="flex-grow:{grow};background:{col};'
                            f'display:flex;align-items:center;padding:0 5px;'
                            f'color:#fff;font-size:9px;font-weight:600;'
                            f'overflow:hidden;white-space:nowrap;">'
                            f'F{i+1}&nbsp;{int(hv)}mm</div>'
                        )
                    parts.append('</div>')
                    _p_prop_html[0].set_content(''.join(parts))

                def _p_auto_redistribute(idx, new_val, heights, total, n):
                    """Set heights[idx]=new_val, redistribute remaining proportionally."""
                    redistributed = redistribute_drawers_proportional(
                        heights,
                        changed_idx=idx,
                        requested_height=new_val,
                        total_target=total,
                        min_h=MIN_DRAWER_H,
                        step=1,
                    )
                    for pos in range(min(n, len(redistributed))):
                        heights[pos] = int(redistributed[pos])
                    return heights

                def _p_build(n, init_list=None):
                    fioka_container.clear()
                    drawer_heights_state['inputs'].clear()
                    total = int(round(_p_get_total()))
                    if init_list and len(init_list) == n:
                        heights = [int(round(float(x))) for x in init_list]
                    else:
                        heights = _p_distribute_equal_int(total, n)
                    drawer_heights_state['heights'] = heights
                    drawer_heights_state['original_heights'] = list(heights)
                    drawer_heights_state['n'] = n
                    with fioka_container:
                        # F1 = top drawer (index 0) shown at top; F(n) = bottom
                        for i in range(n):
                            with ui.row().classes('w-full items-center gap-2 p-1'):
                                ui.label(_t('elements.drawer_label', i=i+1)).classes('text-[10px] text-gray-500 w-10 shrink-0')
                                def _on_change(e, idx=i):
                                    try:
                                        h_state = list(drawer_heights_state['heights'])
                                        _n = drawer_heights_state['n']
                                        _total = _p_get_total()
                                        _p_auto_redistribute(idx, float(e.value), h_state, _total, _n)
                                        drawer_heights_state['heights'] = h_state
                                        for j, inp in drawer_heights_state['inputs'].items():
                                            if j != idx:
                                                try:
                                                    inp.set_value(int(h_state[j]))
                                                except Exception as ex:
                                                    logger.debug("Add drawer input sync failed: %s", ex)
                                        _p_refresh_valid()
                                        _p_update_prop_bars()  # ← instant vizuelni feedback
                                    except Exception as ex:
                                        logger.debug("Add drawer redistribute failed: %s", ex)
                                inp = ui.number(
                                    value=int(heights[i]),
                                    min=MIN_DRAWER_H, max=int(total),
                                    step=1, on_change=_on_change
                                ).props('outlined dense').classes('w-32 max-w-full')
                                drawer_heights_state['inputs'][i] = inp
                    _p_refresh_valid()
                    _p_update_prop_bars()

                def _p_recalc():
                    n = drawer_heights_state['n']
                    total = int(round(_p_get_total()))
                    current = list(drawer_heights_state['heights'])
                    original = drawer_heights_state.get('original_heights', [])
                    THRESHOLD = 1.0
                    if original and len(original) == n:
                        modified = {i for i in range(n) if abs(current[i] - original[i]) > THRESHOLD}
                    else:
                        orig_per = total / n
                        modified = {i for i in range(n) if abs(current[i] - orig_per) > THRESHOLD}
                    # Ako su sve izmenjene — zadrži sve osim prve, preračunaj prvu
                    if len(modified) == n:
                        modified = set(range(1, n))
                    free_indices = [i for i in range(n) if i not in modified]
                    heights = rebalance_drawers_proportional(
                        current,
                        fixed_indices=modified,
                        total_target=total,
                        min_h=MIN_DRAWER_H,
                        step=1,
                        basis_heights=original if original and len(original) == n else current,
                    )
                    drawer_heights_state['heights'] = heights
                    if 'original_heights' not in drawer_heights_state:
                        drawer_heights_state['original_heights'] = list(heights)
                    else:
                        for i in free_indices:
                            drawer_heights_state['original_heights'][i] = heights[i]
                    for idx, inp in drawer_heights_state['inputs'].items():
                        try:
                            inp.set_value(int(heights[idx]))
                        except Exception as ex:
                            logger.debug("Add drawer recalc input update failed: %s", ex)
                    _p_refresh_valid()
                    _p_update_prop_bars()

                def _on_n_change_p(e):
                    _p_build(int(float(e.value)))
                    _p_update_prop_bars()

                ui.number(_t('elements.drawer_count'), value=n_drawers_default, min=1, max=6, step=1,
                          on_change=_on_n_change_p).props('dense').classes('w-full mt-1')

                with ui.row().classes('w-full items-center gap-2 mt-1'):
                    _p_valid_lbl[0] = ui.label('').classes('text-xs text-gray-700 flex-1')
                    ui.button(
                        _t('elements.recalc_drawers', label=_t('elements.recalc')),
                        on_click=_p_recalc,
                    ).props('flat dense').classes('text-xs text-gray-700 border border-gray-300')

                # ── Proportion bars — instant CSS preview ─────────────────────
                _p_prop_html[0] = ui.html('').classes('w-full mt-1')

                ui.timer(0.05, lambda: (_p_build(n_drawers_default), _p_update_prop_bars()), once=True)


        elif has_door_and_drawer:
            # Vrata + fioka kombinovano
            corp_h = float(_dim['h'])
            template_params = dict(tmpl.get("params") or {})
            template_drawers = list(template_params.get("drawer_heights") or [])
            default_drawer_h = float(template_drawers[0]) if template_drawers else 170.0
            default_door_h = float(template_params.get("door_height", corp_h - default_drawer_h) or (corp_h - default_drawer_h))
            default_drawer_h = max(float(MIN_DRAWER_H), min(default_drawer_h, corp_h - 180.0))
            default_door_h = max(180.0, min(default_door_h, corp_h - float(MIN_DRAWER_H)))

            with ui.card().classes('w-full p-2 bg-gray-50 border border-gray-300 mt-1'):
                ui.label(_t('elements.door_drawer')).classes('font-bold text-xs mb-0')
                ui.label(_t('elements.door_drawer_total_h', h=corp_h)).classes('text-xs text-gray-500')

                with ui.row().classes('w-full gap-1'):
                    door_h_inp = ui.number(
                        label=_t('elements.door_h_label'),
                        value=round(default_door_h, 1),
                        min=180, max=int(corp_h - MIN_DRAWER_H), step=1
                    ).props('dense').classes('flex-1 min-w-0')
                    drawer_h_inp = ui.number(
                        label=_t('elements.drawer_h_label'),
                        value=round(default_drawer_h, 1),
                        min=MIN_DRAWER_H, max=int(corp_h - 180), step=1
                    ).props('dense').classes('flex-1 min-w-0')

                drawer_h_lbl = ui.label('').classes('text-xs text-gray-700 font-bold mt-1')
                _door_drawer_syncing = {'value': False}

                def _update_door_drawer_hint():
                    try:
                        door_val = float(door_h_inp.value or 0)
                        drawer_val = float(drawer_h_inp.value or 0)
                        remaining = corp_h - door_val - drawer_val
                        if drawer_val < MIN_DRAWER_H:
                            drawer_h_lbl.set_text(_t('elements.drawer_too_small', h=drawer_val, min_h=MIN_DRAWER_H))
                        elif remaining < 0:
                            drawer_h_lbl.set_text(_t('elements.door_drawer_sum_too_high', total=door_val + drawer_val, h=corp_h))
                        else:
                            drawer_h_lbl.set_text(_t('elements.door_drawer_sum_ok', total=door_val + drawer_val, reserve=remaining))
                    except Exception:
                        pass

                def _on_door_change(e=None):
                    if _door_drawer_syncing['value']:
                        return
                    try:
                        _door_drawer_syncing['value'] = True
                        door_val = max(180.0, min(float(door_h_inp.value or 0), corp_h - float(MIN_DRAWER_H)))
                        drawer_h_inp.set_value(max(float(MIN_DRAWER_H), corp_h - door_val))
                    finally:
                        _door_drawer_syncing['value'] = False
                    _update_door_drawer_hint()

                def _on_drawer_change(e=None):
                    if _door_drawer_syncing['value']:
                        return
                    try:
                        _door_drawer_syncing['value'] = True
                        drawer_val = max(float(MIN_DRAWER_H), min(float(drawer_h_inp.value or 0), corp_h - 180.0))
                        door_h_inp.set_value(max(180.0, corp_h - drawer_val))
                    finally:
                        _door_drawer_syncing['value'] = False
                    _update_door_drawer_hint()

                door_h_inp.on('change', _on_door_change)
                drawer_h_inp.on('change', _on_drawer_change)
                _update_door_drawer_hint()

        elif has_shelves:
            # Police
            corp_h = float(_dim['h'])
            inner = _inner_h(corp_h)
            default_n_shelves = default_shelf_count(
                tid,
                zone=zone,
                h_mm=corp_h,
                params={},
                features=features,
            )

            with ui.card().classes('w-full p-2 bg-gray-50 border border-gray-300 mt-1'):
                ui.label(_t('elements.shelves')).classes('font-bold text-xs mb-0')
                ui.label(_t('elements.shelves_suggest', n=default_n_shelves)).classes('text-xs text-gray-500')
                n_shelves = ui.number(_t('elements.shelf_count'), value=default_n_shelves, min=0, max=10, step=1).props('dense').classes('w-full')
                _initial_spacing = (inner / (default_n_shelves + 1)) if default_n_shelves > 0 else inner
                shelf_h_lbl = ui.label(_t('elements.shelves_spacing', h=_initial_spacing)).classes('text-xs text-gray-700')

                def _on_shelves_change(e):
                    n = max(0, int(e.value or 0))
                    spacing = inner / (n + 1) if n > 0 else inner
                    shelf_h_lbl.set_text(_t('elements.shelves_spacing', h=spacing))

                n_shelves.on('change', _on_shelves_change)


        if has_wardrobe:
            _s_min, _s_max = (0, 12)
            _d_min, _d_max = (0, 8)
            _h_min, _h_max = (0, 3)
            with ui.card().classes('w-full p-2 bg-gray-50 border border-gray-300 mt-1'):
                ui.label(_t('elements.wardrobe_interior')).classes('font-bold text-xs mb-0')
                _front_default = 'inside' if bool(features.get('interior_only', False)) else 'both'
                wardrobe_front_style = ui.select(
                    {
                        'doors': _t('elements.front_outside'),
                        'inside': _t('elements.front_inside'),
                        'both': _t('elements.front_both'),
                    },
                    value=_front_default,
                    label=_t('elements.front_view_choice'),
                ).props('dense outlined').classes('w-full')
                _default_door_mode = 'sliding' if bool(features.get('sliding', False)) else str(getattr(state, 'wardrobe_door_mode', 'hinged') or 'hinged')
                wardrobe_door_mode = ui.select(
                    {'hinged': _t('elements.doors_hinged'), 'sliding': _t('elements.doors_sliding')},
                    value=_default_door_mode if _default_door_mode in ('hinged', 'sliding') else 'hinged',
                    label=_t('elements.door_type'),
                ).props('dense outlined').classes('w-full')
                _ws = int(features.get('n_shelves', 4))
                _wd = int(features.get('n_drawers', 2))
                _wh = int(features.get('hanger_sections', 1))
                wardrobe_n_shelves = ui.number(_t('elements.shelf_count'), value=_ws, min=_s_min, max=_s_max, step=1).props('dense outlined').classes('w-full')
                wardrobe_n_shelves_slider = ui.slider(min=_s_min, max=_s_max, value=_ws, step=1).props('label-always').classes('w-full -mt-1')
                wardrobe_n_drawers = ui.number(_t('elements.drawer_count'), value=_wd, min=_d_min, max=_d_max, step=1).props('dense outlined').classes('w-full')
                wardrobe_n_drawers_slider = ui.slider(min=_d_min, max=_d_max, value=_wd, step=1).props('label-always').classes('w-full -mt-1')
                wardrobe_hanger_sections = ui.number(_t('elements.hanging_zones'), value=_wh, min=_h_min, max=_h_max, step=1).props('dense outlined').classes('w-full')
                wardrobe_hanger_sections_slider = ui.slider(min=_h_min, max=_h_max, value=_wh, step=1).props('label-always').classes('w-full -mt-1')
                wardrobe_to_ceiling = ui.switch(_t('elements.to_ceiling'), value=bool(getattr(state, 'wardrobe_to_ceiling', True))).classes('mt-1')

                def _sync_num_to_slider(num_el, slider_el):
                    def _h(e):
                        try:
                            slider_el.set_value(int(float(e.value)))
                        except Exception:
                            pass
                    return _h

                def _sync_slider_to_num(slider_el, num_el):
                    def _h(e):
                        try:
                            num_el.set_value(int(float(e.value)))
                        except Exception:
                            pass
                    return _h

                wardrobe_n_shelves.on('change', _sync_num_to_slider(wardrobe_n_shelves, wardrobe_n_shelves_slider))
                wardrobe_n_shelves_slider.on('change', _sync_slider_to_num(wardrobe_n_shelves_slider, wardrobe_n_shelves))
                wardrobe_n_drawers.on('change', _sync_num_to_slider(wardrobe_n_drawers, wardrobe_n_drawers_slider))
                wardrobe_n_drawers_slider.on('change', _sync_slider_to_num(wardrobe_n_drawers_slider, wardrobe_n_drawers))
                wardrobe_hanger_sections.on('change', _sync_num_to_slider(wardrobe_hanger_sections, wardrobe_hanger_sections_slider))
                wardrobe_hanger_sections_slider.on('change', _sync_slider_to_num(wardrobe_hanger_sections_slider, wardrobe_hanger_sections))


        name = ui.input(l_naziv, value=label).props('dense').classes('w-full mt-1')
        handle_side_sel = None
        if "1DOOR" in tid and zone in ("base", "wall", "tall"):
            _default_handle_side = str(_corner_guidance.get('recommended_handle_side') or "right")
            handle_side_sel = ui.select(["left", "right"], value=_default_handle_side, label=l_strana_rucke).props('dense').classes('w-full')

        wall_upper_x = None
        if zone == "wall_upper":
            _active_wk = str(
                (getattr(state, "room", {}) or {}).get("active_wall",
                    (getattr(state, "room", {}) or {}).get("kitchen_wall", "A")) or "A"
            ).upper()
            wall_mods = [m for m in (state.kitchen.get("modules", []) or [])
                         if str(m.get("zone", "")).lower() == "wall"
                         and str(m.get("wall_key", "A")).upper() == _active_wk]
            options = [(f"#{m.get('id')} {m.get('label','')}", int(m.get("x_mm", 0))) for m in wall_mods]
            if options:
                def _wu_change(e):
                    try:
                        state.wall_upper_target_x = int(e.value[1])
                    except Exception as ex:
                        logger.debug("Wall-upper target change parse failed: %s", ex)
                        state.wall_upper_target_x = -1

                sel = ui.select(options, value=options[0], label=l_iznad_kog_gornjeg, on_change=_wu_change).props('dense').classes('w-full')
                wall_upper_x = sel
                try:
                    state.wall_upper_target_x = int(sel.value[1])
                except Exception as ex:
                    logger.debug("Wall-upper initial target parse failed: %s", ex)
                    state.wall_upper_target_x = -1
            else:
                ui.label(m_nema_gornjih_1_red).classes('text-xs text-gray-500')
                state.wall_upper_target_x = -1

        def _do_dodaj(use_d_mm: int, override_as_new_standard: bool = False) -> None:
            """Interni helper — stvarno dodaje element."""
            try:
                _h_for_add = int(_dim['h'])
                if has_wardrobe and wardrobe_to_ceiling is not None and bool(wardrobe_to_ceiling.value):
                    _h_for_add = int(_max_h)

                # Ažuriraj zone_defaults (samo za base/wall/wall_upper)
                if zone not in ('tall', 'tall_top') and not _use_template_defaults:
                    state.zone_defaults[zone]['h_mm'] = _h_for_add
                    if not _is_indep:
                        state.zone_defaults[zone]['d_mm'] = int(use_d_mm)

                # Ako korisnik bira da postavi novu zone dubinu kao standard
                if override_as_new_standard and not _is_indep:
                    set_zone_depth_standard(zone, use_d_mm, update_existing=False)

                # Skupi params za fioke/police
                _extra_params = {}
                try:
                    if has_drawers and not has_door_and_drawer and drawer_heights_state:
                        n_cur = int(drawer_heights_state.get('n', 3))
                        heights = drawer_heights_state.get('heights', [])
                        if not heights or len(heights) != n_cur:
                            total = int(round(_inner_h(float(_dim['h']))))
                            heights = _p_distribute_equal_int(total, n_cur)
                        _extra_params['drawer_heights'] = [int(round(x)) for x in heights]
                        _extra_params['n_drawers'] = n_cur
                    if has_door_and_drawer and door_h_inp is not None:
                        _door_h = float(door_h_inp.value)
                        _drawer_h = float(drawer_h_inp.value) if drawer_h_inp is not None else float(_dim['h']) - _door_h
                        if _door_h + _drawer_h > float(_dim['h']):
                            raise ValueError(
                                _t('elements.door_drawer_sum_too_high', total=_door_h + _drawer_h, h=float(_dim['h']))
                            )
                        _extra_params['door_height'] = _door_h
                        _extra_params['drawer_heights'] = [_drawer_h]
                        _extra_params['n_drawers'] = 1
                    if has_shelves and n_shelves is not None:
                        _extra_params['n_shelves'] = int(n_shelves.value)
                    if has_oven and fioka_h is not None:
                        _extra_params['drawer_heights'] = [fioka_h]
                        _extra_params['n_drawers'] = 1
                        _extra_params['oven_h'] = OVEN_H
                    if tid == "SINK_BASE":
                        if sink_cutout_x is not None:
                            _extra_params['sink_cutout_x_mm'] = int(float(sink_cutout_x.value or 0))
                        if sink_cutout_w is not None:
                            _extra_params['sink_cutout_width_mm'] = int(float(sink_cutout_w.value or 0))
                        if sink_cutout_d is not None:
                            _extra_params['sink_cutout_depth_mm'] = int(float(sink_cutout_d.value or 0))
                    if tid in {"BASE_COOKING_UNIT", "BASE_HOB"}:
                        if hob_cutout_x is not None:
                            _extra_params['hob_cutout_x_mm'] = int(float(hob_cutout_x.value or 0))
                        if hob_cutout_w is not None:
                            _extra_params['hob_cutout_width_mm'] = int(float(hob_cutout_w.value or 0))
                        if hob_cutout_d is not None:
                            _extra_params['hob_cutout_depth_mm'] = int(float(hob_cutout_d.value or 0))
                    if has_wardrobe:
                        _extra_params['wardrobe'] = True
                        if wardrobe_front_style is not None:
                            _extra_params['front_style'] = str(wardrobe_front_style.value or 'both')
                        if wardrobe_door_mode is not None:
                            _extra_params['door_mode'] = str(wardrobe_door_mode.value or 'hinged')
                        if wardrobe_n_shelves is not None:
                            _extra_params['n_shelves'] = int(wardrobe_n_shelves.value)
                        if wardrobe_n_drawers is not None:
                            _extra_params['n_drawers'] = int(wardrobe_n_drawers.value)
                        if wardrobe_hanger_sections is not None:
                            _extra_params['hanger_sections'] = int(wardrobe_hanger_sections.value)
                        if wardrobe_to_ceiling is not None:
                            _extra_params['to_ceiling'] = bool(wardrobe_to_ceiling.value)
                        if 'AMERICAN' in tid:
                            _extra_params['american_sections'] = {
                                'left_pct': 33,
                                'center_pct': 34,
                                'right_pct': 33,
                                'top_h_mm': 420,
                                'left': {
                                    'shelves': int(_extra_params.get('n_shelves', 4)),
                                    'drawers': max(0, int(_extra_params.get('n_drawers', 2)) // 2),
                                    'hangers': 0,
                                },
                                'center': {
                                    'shelves': 1,
                                    'drawers': 0,
                                    'hangers': max(1, int(_extra_params.get('hanger_sections', 1))),
                                },
                                'right': {
                                    'shelves': max(1, int(_extra_params.get('n_shelves', 4)) // 2),
                                    'drawers': max(0, int(_extra_params.get('n_drawers', 2))),
                                    'hangers': max(0, int(_extra_params.get('hanger_sections', 1)) - 1),
                                },
                                'top': {
                                    'shelves': 2,
                                    'drawers': 0,
                                    'hangers': 0,
                                },
                                'locked': False,
                            }
                except Exception as ex:
                    logger.debug("Add element extra params collection failed: %s", ex)

                _room_for_add = getattr(state, 'room', None)
                _kwall_key    = str(
                    (_room_for_add or {}).get('active_wall',
                        (_room_for_add or {}).get('kitchen_wall', 'A')) or 'A'
                ).upper()
                x_use = int(find_first_free_x(state.kitchen, zone, _dim['w'], wall_key=_kwall_key))
                if zone == "wall_upper" and wall_upper_x is not None:
                    x_use = int(wall_upper_x.value[1])
                if handle_side_sel is not None:
                    _extra_params["handle_side"] = str(handle_side_sel.value)

                # ── Smer goda ─────────────────────────────────────────────────
                _extra_params["grain_dir"] = str(grain_sel_add.value or "V")

                new_mod = add_module_instance_local(
                    template_id=state.selected_tid,
                    zone=zone,
                    x_mm=int(x_use),
                    w_mm=_dim['w'],
                    h_mm=_h_for_add,
                    d_mm=int(use_d_mm),
                    gap_after_mm=0,
                    label=name.value,
                    params=_extra_params,
                    room=_room_for_add,
                    wall_key=_kwall_key,
                )
                # Ako je CUSTOM (korisnik uneo drugačiju d od standarda), označi
                if not _is_indep and int(use_d_mm) != get_zone_depth_standard(zone):
                    new_mod["depth_mode"] = "CUSTOM"
                ui.notify(_t('elements.added', label=label), type='positive')
                nacrt_refresh()
                sidebar_refresh()
            except Exception as e:
                ui.notify(_t('elements.error', err=format_user_error(e, getattr(state, 'language', 'sr'))), type='negative')

        def dodaj() -> None:
            entered_d = _dim['d']
            zone_std = get_zone_depth_standard(zone)

            # Aparat — direktno dodaj, bez pitanja
            if _is_indep:
                _do_dodaj(entered_d)
                return

            # Korisnik uneo d_mm različit od zone standarda → pitaj
            if entered_d != zone_std:
                zone_label = zone.upper()
                with ui.dialog() as _dlg_override:
                    with ui.card().classes('p-4 gap-2 min-w-72'):
                        ui.label(
                            _t('elements.depth_dialog_title', entered=entered_d, zone=zone_label, std=zone_std)
                        ).classes('font-bold text-sm')
                        ui.label(_t('elements.what_to_do')).classes('text-sm text-gray-600')
                        with ui.column().classes('w-full gap-2 mt-2'):
                            def _set_as_std():
                                _dlg_override.close()
                                _do_dodaj(entered_d, override_as_new_standard=True)
                                ui.notify(_t('elements.depth_set_ok', zone=zone_label, d=entered_d), type='info')
                                params_panel_refresh()
                            def _keep_custom():
                                _dlg_override.close()
                                _do_dodaj(entered_d, override_as_new_standard=False)
                            def _cancel():
                                _dlg_override.close()

                            ui.button(
                                _t('elements.depth_set_std', d=entered_d, zone=zone_label),
                                on_click=_set_as_std
                            ).classes('w-full bg-white text-[#111] border border-[#111] text-xs')
                            ui.button(
                                _t('elements.depth_only_this', std=zone_std),
                                on_click=_keep_custom
                            ).classes('w-full bg-gray-100 text-xs')
                            ui.button(_t('common.cancel'), on_click=_cancel).classes('w-full text-xs')
                _dlg_override.open()
            else:
                _do_dodaj(entered_d)

        set_sidebar_primary_action(dodaj, b_dodaj_na_zid)

