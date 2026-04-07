# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Callable, Iterable, Tuple, Any


def render_toolbar_layout(
    *,
    ui: Any,
    tabs: Iterable[Tuple[str, str, str]],
    active_tab: str,
    on_tab_click: Callable[[str], None],
    on_save_click: Callable[[], None],
    on_load_click: Callable[[], None],
    on_reset_click: Callable[[], None] | None = None,
    language_label: str = "",
    language_options: dict[str, str] | None = None,
    current_language: str = "sr",
    on_language_change: Callable[[str], None] | None = None,
    toolbar_app_name: str = "",
    toolbar_app_sub: str = "",
    toolbar_save_label: str = "",
    toolbar_load_label: str = "",
    toolbar_reset_label: str = "",
    toolbar_save_tooltip: str = "",
    toolbar_load_tooltip: str = "",
    toolbar_reset_tooltip: str = "",
    session_label: str = "",
    account_label: str = "",
    logout_label: str = "",
    on_account_click: Callable[[], None] | None = None,
    on_logout_click: Callable[[], None] | None = None,
) -> None:
    """Kompaktni flat toolbar — sve uniformno, bez bordera."""
    with ui.row().classes(
        'w-full bg-white px-0 py-0 gap-0 border-b border-gray-200 items-stretch'
    ).style('min-height:42px; height:42px;'):

        # Naziv aplikacije
        with ui.element('div').classes(
            'flex items-center gap-1 px-3 border-r border-gray-200 shrink-0'
        ):
            ui.label(toolbar_app_name).classes(
                'text-[13px] font-bold text-gray-800 whitespace-nowrap'
            )
            if toolbar_app_sub:
                ui.label(toolbar_app_sub).classes(
                    'text-[8px] font-semibold text-gray-400 whitespace-nowrap'
                )

        # Tab dugmad
        for key, label, icon in tabs:
            is_active = active_tab == key
            extra = 'toolbar-btn--active' if is_active else ''
            with ui.button(
                on_click=lambda k=key: on_tab_click(k)
            ).classes(f'toolbar-btn {extra}').props('flat no-caps'):
                ui.icon(icon).classes('text-[15px]')
                ui.label(label).classes('text-[12px] font-medium whitespace-nowrap')

        # Spacer
        ui.element('div').classes('flex-1')

        # Akcijska dugmad desno
        with ui.button(on_click=on_save_click).classes(
            'toolbar-btn toolbar-btn--action'
        ).props('flat no-caps dense').tooltip(toolbar_save_tooltip):
            ui.icon('save').classes('text-[15px]')
            ui.label(toolbar_save_label).classes('text-[12px] font-medium whitespace-nowrap')

        with ui.button(on_click=on_load_click).classes(
            'toolbar-btn toolbar-btn--action'
        ).props('flat no-caps dense').tooltip(toolbar_load_tooltip):
            ui.icon('folder_open').classes('text-[15px]')
            ui.label(toolbar_load_label).classes('text-[12px] font-medium whitespace-nowrap')

        if callable(on_reset_click):
            with ui.button(on_click=on_reset_click).classes(
                'toolbar-btn toolbar-btn--action'
            ).props('flat no-caps dense').tooltip(toolbar_reset_tooltip):
                ui.icon('restart_alt').classes('text-[15px]')
                ui.label(toolbar_reset_label).classes('text-[12px] font-medium whitespace-nowrap')

        if session_label:
            with ui.element('div').classes(
                'flex items-center px-3 border-l border-gray-200 shrink-0'
            ).style('height:42px;'):
                ui.label(session_label).classes('text-[11px] text-gray-600 whitespace-nowrap')

        if callable(on_account_click):
            with ui.button(on_click=on_account_click).classes(
                'toolbar-btn toolbar-btn--action'
            ).props('flat no-caps dense'):
                ui.icon('person').classes('text-[15px]')
                ui.label(account_label).classes('text-[12px] font-medium whitespace-nowrap')

        if callable(on_logout_click):
            with ui.button(on_click=on_logout_click).classes(
                'toolbar-btn toolbar-btn--action'
            ).props('flat no-caps dense'):
                ui.icon('logout').classes('text-[15px]')
                ui.label(logout_label).classes('text-[12px] font-medium whitespace-nowrap')

        # Jezik — isti izgled kao ostala toolbar dugmad
        if language_options and callable(on_language_change):
            visible_language = current_language if current_language in language_options else "sr"
            with ui.element('div').classes(
                'flex items-center border-l border-gray-200 shrink-0'
            ).style('height:42px;'):
                ui.select(
                    options=language_options,
                    value=visible_language,
                    on_change=lambda e: on_language_change(str(e.value or 'sr')),
                ).props('dense borderless').classes('toolbar-lang text-[11px] font-medium').style(
                    'min-width:78px; max-width:96px; height:42px;'
                )
