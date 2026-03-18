# -*- coding: utf-8 -*-
from __future__ import annotations

from i18n import HELP_MD, HELP_TITLE


def render_help_tab(ui) -> None:
    with ui.card().classes('max-w-2xl mx-auto mt-10 p-6'):
        ui.label(HELP_TITLE).classes('text-2xl font-bold mb-4')
        ui.markdown(HELP_MD)
