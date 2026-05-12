# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Callable, Iterable


def render_sidebar_content_layout(
    *,
    ui: Any,
    is_edit_mode: bool,
    on_close_edit: Callable[[], None],
    edit_body: Callable[[], None],
    tabs: Iterable[dict],
    active_key: str,
    has_items_for_tab: Callable[[str], bool],
    on_select_tab: Callable[[str], None],
    add_body: Callable[[], None],
    footer_label: str,
    on_footer_click: Callable[[], None],
    tr_fn: Callable[[str], str],
    show_footer: bool = True,
) -> None:
    """Render left sidebar shell (ADD/EDIT modes) with external callbacks."""
    with ui.element('div').classes(
        'px-3 py-2 bg-gray-50 border-b border-gray-200 shrink-0'
    ):
        with ui.row().classes('w-full items-center justify-between'):
            ui.label(
                tr_fn("elements.params_title") if is_edit_mode else tr_fn("elements.add_element")
            ).classes('text-xs font-bold text-gray-600 uppercase tracking-wider')
            if is_edit_mode:
                ui.button(
                    icon='close',
                    on_click=on_close_edit,
                ).props('flat round dense').classes('text-gray-600')

    if is_edit_mode:
        with ui.scroll_area().classes('left-panel-body flex-1 min-h-0 w-full').props('id=sidebar-edit-scroll'):
            with ui.column().classes('w-full gap-1 px-1 pb-1'):
                edit_body()
        return

    # Tab strip (Donji / Gornji / Visoki) se prikazuje samo u katalogu,
    # a skriva se kada je prikazana kartica selektovanog elementa (show_footer=True).
    if not show_footer:
        with ui.row().classes('left-tabs-row w-full flex-wrap gap-1 shrink-0 px-2 py-1 bg-gray-50 border-b border-gray-200'):
            for _tab in tabs:
                _k = _tab["key"]
                _has_items = has_items_for_tab(_k)
                _is_disabled = not _has_items
                if _is_disabled:
                    _state_cls = 'left-tab-disabled'
                elif active_key == _k:
                    _state_cls = 'left-tab-active'
                else:
                    _state_cls = 'left-tab-inactive'
                _props = 'no-caps outline color=dark'
                if _is_disabled:
                    _props += ' disable'
                ui.button(
                    _tab["label"],
                    on_click=lambda k=_k: on_select_tab(k)
                ).classes(f'left-tab-btn flex-1 {_state_cls}').props(_props)

    with ui.scroll_area().classes('left-panel-body flex-1 min-h-0 w-full').props('id=sidebar-add-scroll'):
        with ui.column().classes('w-full gap-1 px-1 pb-1'):
            add_body()

    if show_footer:
        with ui.element('div').classes(
            'sidebar-sticky-footer w-full bg-white border-t border-gray-300 p-2 shrink-0'
        ).style('position:sticky;bottom:0;z-index:5;'):
            ui.button(footer_label, on_click=on_footer_click).classes(
                'w-full text-xs font-semibold'
            )
