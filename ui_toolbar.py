# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Callable, Iterable, Tuple, Any
from i18n import (
    BTN_RESET_PROJEKTA,
    BTN_SACUVAJ,
    BTN_UCITAJ,
    TOOLBAR_RESET_TOOLTIP,
    TOOLBAR_APP_NAME,
    TOOLBAR_APP_SUB,
    TOOLBAR_LOAD_TOOLTIP,
    TOOLBAR_SAVE_TOOLTIP,
)


def render_toolbar_layout(
    *,
    ui: Any,
    tabs: Iterable[Tuple[str, str, str]],
    active_tab: str,
    on_tab_click: Callable[[str], None],
    on_save_click: Callable[[], None],
    on_load_click: Callable[[], None],
    on_reset_click: Callable[[], None] | None = None,
) -> None:
    """Render only toolbar layout; behavior is provided via callbacks."""
    with ui.row().classes(
        'w-full bg-white px-2 py-0 gap-0 border-b border-gray-200 items-stretch'
    ).style('min-height:48px;'):
        with ui.element('div').classes('flex items-center px-3 border-r border-gray-200 shrink-0'):
            ui.label(TOOLBAR_APP_NAME).classes('text-sm font-bold text-gray-700')
            ui.label(TOOLBAR_APP_SUB).classes('text-[9px] font-bold text-gray-700 ml-1 mt-0.5')

        for key, label, icon in tabs:
            is_active = active_tab == key
            if is_active:
                btn_cls = (
                    'flex flex-col items-center px-4 py-1 rounded-none '
                    'border-b-2 border-gray-900 text-gray-900 bg-white'
                )
                lbl_cls = 'text-[10px] font-bold text-gray-900'
                icn_cls = 'text-xl text-gray-900'
            else:
                btn_cls = (
                    'flex flex-col items-center px-4 py-1 rounded-none '
                    'border-b-2 border-transparent text-gray-500 '
                    'hover:bg-gray-50 hover:text-gray-700'
                )
                lbl_cls = 'text-[10px] font-medium text-gray-500'
                icn_cls = 'text-xl text-gray-500'
            with ui.button(on_click=lambda k=key: on_tab_click(k)).classes(btn_cls).props('flat no-caps'):
                ui.icon(icon).classes(icn_cls)
                ui.label(label).classes(lbl_cls)

        ui.element('div').classes('flex-1')

        with ui.button(on_click=on_save_click).classes(
            'flex flex-col items-center px-3 py-1 rounded-none hover:bg-gray-50'
        ).props('flat dense').tooltip(TOOLBAR_SAVE_TOOLTIP):
            ui.icon('save').classes('text-xl text-gray-900')
            ui.label(BTN_SACUVAJ).classes('text-[10px] text-gray-900 font-medium')

        with ui.button(on_click=on_load_click).classes(
            'flex flex-col items-center px-3 py-1 rounded-none hover:bg-gray-50'
        ).props('flat dense').tooltip(TOOLBAR_LOAD_TOOLTIP):
            ui.icon('folder_open').classes('text-xl text-gray-900')
            ui.label(BTN_UCITAJ).classes('text-[10px] text-gray-900 font-medium')

        if callable(on_reset_click):
            with ui.button(on_click=on_reset_click).classes(
                'flex flex-col items-center px-3 py-1 rounded-none hover:bg-gray-50'
            ).props('flat dense').tooltip(TOOLBAR_RESET_TOOLTIP):
                ui.icon('restart_alt').classes('text-xl text-gray-900')
                ui.label(BTN_RESET_PROJEKTA).classes('text-[10px] text-gray-900 font-medium')
