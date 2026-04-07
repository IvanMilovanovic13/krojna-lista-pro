# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Callable


def render_help_tab(ui: Any, tr_fn: Callable[[str], str]) -> None:
    with ui.card().classes('max-w-2xl mx-auto mt-10 p-6'):
        ui.label(tr_fn('help.title')).classes('text-2xl font-bold mb-4')
        ui.markdown(tr_fn('help.md'))
