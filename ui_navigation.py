# -*- coding: utf-8 -*-
from __future__ import annotations


def safe_refresh(refresh_fn, logger) -> None:
    """Refresh guard: ignorisi stale-client pozive posle re-kreiranja UI klijenta."""
    if not callable(refresh_fn):
        return
    try:
        refresh_fn()
    except Exception as err:
        if "client this element belongs to has been deleted" in str(err).lower():
            logger.debug("Ignored stale-client refresh call: %s", err)
            return
        raise


def switch_tab(
    *,
    ui,
    state,
    key: str,
    msg_podesi_prostoriju_prvo: str,
    main_content_refresh,
    render_toolbar_refresh,
    logger,
) -> None:
    if key == "krojna":
        from state_logic import get_cutlist_access_state

        cutlist_access = get_cutlist_access_state()
        if str(cutlist_access.get("allowed", "")).lower() != "true":
            state.active_tab = "nalog"
            ui.notify(str(cutlist_access.get("reason", "") or "Krojna lista nije dostupna."), type="warning")
            safe_refresh(main_content_refresh, logger)
            ui.timer(0.05, lambda: ui.run_javascript('window.scrollTo({top: 0, behavior: "auto"})'), once=True)
            ui.timer(0.05, lambda: safe_refresh(render_toolbar_refresh, logger), once=True)
            return
    if key in ("elementi", "krojna") and not getattr(state, "room_setup_done", False):
        state.active_tab = "wizard"
        state.wizard_step = 4
        ui.notify(msg_podesi_prostoriju_prvo, type="warning")
    else:
        state.active_tab = key
    safe_refresh(main_content_refresh, logger)
    # Delay toolbar refresh by 1 tick so the toolbar button DOM isn't destroyed
    # during its own click handler.
    ui.timer(0.05, lambda: safe_refresh(render_toolbar_refresh, logger), once=True)

