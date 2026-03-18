# -*- coding: utf-8 -*-
from __future__ import annotations


def render_sidebar_content_panel(
    *,
    ui,
    state,
    templates,
    palette_tabs,
    palette_tab_map,
    sidebar_primary_action,
    btn_dodaj_na_zid,
    render_sidebar_content_layout,
    render_palette,
    params_panel,
    edit_panel,
    select_palette_tab,
    run_sidebar_primary_action,
    nacrt_refresh,
    sidebar_refresh,
    set_sidebar_footer_refresh,
) -> None:
    """Levi sidebar ADD/EDIT render bez menjanja logike aplikacije."""
    _is_edit_mode = (state.mode == "edit" and state.selected_edit_id > 0)
    _active_key = state.active_group if state.active_group in palette_tab_map else "donji"
    _label = str(sidebar_primary_action.get("label") or btn_dodaj_na_zid)

    def _close_edit() -> None:
        setattr(state, "selected_edit_id", 0)
        setattr(state, "mode", "add")
        nacrt_refresh()
        sidebar_refresh()

    def _has_items_for_tab(_k: str) -> bool:
        _tab = palette_tab_map.get(_k, {})
        return any(
            templates.get(_tid)
            for _sg in _tab.get("subgroups", [])
            for _tid in _sg.get("tids", [])
        )

    def _render_add_body() -> None:
        render_palette()
        params_panel()

    render_sidebar_content_layout(
        ui=ui,
        is_edit_mode=_is_edit_mode,
        on_close_edit=_close_edit,
        edit_body=edit_panel,
        tabs=palette_tabs,
        active_key=_active_key,
        has_items_for_tab=_has_items_for_tab,
        on_select_tab=select_palette_tab,
        add_body=_render_add_body,
        footer_label=_label,
        on_footer_click=run_sidebar_primary_action,
    )

    set_sidebar_footer_refresh(None)

