# -*- coding: utf-8 -*-
from __future__ import annotations


_SIDEBAR_PRIMARY_ACTION = {"label": "Dodaj na zid", "handler": None}
_SIDEBAR_FOOTER_REFRESH = None


def get_sidebar_primary_action() -> dict:
    return _SIDEBAR_PRIMARY_ACTION


def get_sidebar_footer_refresh(*, ui, logger):
    try:
        _client = ui.context.client
        return getattr(_client, "_sidebar_footer_refresh", None)
    except Exception as ex:
        logger.debug("Sidebar footer refresh getter fallback to global: %s", ex)
        return _SIDEBAR_FOOTER_REFRESH


def set_sidebar_footer_refresh(*, ui, logger, refresh_fn) -> None:
    global _SIDEBAR_FOOTER_REFRESH
    _SIDEBAR_FOOTER_REFRESH = refresh_fn
    try:
        _client = ui.context.client
        setattr(_client, "_sidebar_footer_refresh", refresh_fn)
    except Exception as ex:
        logger.debug("Sidebar footer refresh setter fallback to global: %s", ex)


def set_sidebar_primary_action(
    *,
    ui,
    logger,
    label: str,
    handler=None,
) -> None:
    _SIDEBAR_PRIMARY_ACTION["handler"] = handler
    _SIDEBAR_PRIMARY_ACTION["label"] = label
    _footer_refresh = get_sidebar_footer_refresh(ui=ui, logger=logger)
    if callable(_footer_refresh):
        try:
            _footer_refresh()
        except Exception as err:
            if "client this element belongs to has been deleted" in str(err).lower():
                logger.debug("Ignored stale sidebar footer refresh: %s", err)
                set_sidebar_footer_refresh(ui=ui, logger=logger, refresh_fn=None)
            else:
                raise


def run_sidebar_primary_action(*, ui, label_fallback: str, notify_empty: str) -> None:
    _handler = _SIDEBAR_PRIMARY_ACTION.get("handler")
    if callable(_handler):
        _handler()
    else:
        ui.notify(notify_empty, type="warning")
        _SIDEBAR_PRIMARY_ACTION["label"] = label_fallback

