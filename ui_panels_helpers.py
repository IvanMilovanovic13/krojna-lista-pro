# -*- coding: utf-8 -*-
from __future__ import annotations


def set_sidebar_primary_action(
    *,
    ui,
    logger,
    impl,
    label: str,
    handler=None,
) -> None:
    impl(
        ui=ui,
        logger=logger,
        label=label,
        handler=handler,
    )


def run_sidebar_primary_action(
    *,
    ui,
    impl,
    label_fallback: str,
    notify_empty: str,
) -> None:
    impl(
        ui=ui,
        label_fallback=label_fallback,
        notify_empty=notify_empty,
    )


def format_user_error(err: Exception | str) -> str:
    msg = str(err or "").strip()
    if not msg:
        return "Greška."
    if msg.lower().startswith("blokirano:"):
        return msg
    return f"Greška: {msg}"


def render_color_picker_wrapper(
    *,
    ui,
    render_color_picker_fn,
    presets,
    color_ref: dict,
    title: str,
    columns: int,
    swatch_h: int,
) -> None:
    render_color_picker_fn(
        ui=ui,
        presets=presets,
        color_ref=color_ref,
        title=title,
        columns=columns,
        swatch_h=swatch_h,
    )
