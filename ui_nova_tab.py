# -*- coding: utf-8 -*-
from __future__ import annotations

import logging

from i18n import (
    BTN_NOVA_CONFIRM,
    BTN_OTKAZI,
    BTN_SACUVAJ_JSON,
    BTN_UCITAJ_IZABRANI,
    ERR_LOAD_PREFIX,
    LBL_UCITAJ_IZ_FAJLA,
    LBL_UPLOAD_JSON,
    MSG_SAVE_OK,
    NOVA_CREATED_OK,
    NOVA_SAVE_LOAD_TITLE,
    STATUS_LOAD_EMPTY_FAIL,
    STATUS_NO_FILE_CONTENT,
    STATUS_LOAD_OK_DETAIL,
    TAB_NOVA_TITLE,
    TAB_NOVA_WARN_CLEAR,
)

_LOG = logging.getLogger(__name__)


def render_nova_tab(
    ui,
    state,
    main_content_refresh,
    switch_tab,
    clear_all_local,
    save_project_json,
    load_project_json,
) -> None:
    with ui.column().classes('w-full max-w-2xl mx-auto gap-6 py-8'):
        with ui.card().classes('w-full p-8 text-center'):
            ui.label(TAB_NOVA_TITLE).classes('text-2xl font-bold mb-2')
            ui.label(TAB_NOVA_WARN_CLEAR).classes('text-gray-500 mb-6')

            def _potvrdi():
                clear_all_local()
                state.active_tab = "elementi"
                main_content_refresh()
                ui.notify(NOVA_CREATED_OK, type='positive')

            ui.button(BTN_NOVA_CONFIRM, on_click=_potvrdi).classes(
                'bg-white text-[#111] border border-[#111] w-full'
            )
            ui.button(BTN_OTKAZI, on_click=lambda: switch_tab('elementi')).classes('w-full mt-2')

        with ui.card().classes('w-full p-6'):
            ui.label(NOVA_SAVE_LOAD_TITLE).classes('text-lg font-bold mb-4')

            def _nova_save():
                from datetime import datetime as _dt
                filename = f"kuhinja_{_dt.now().strftime('%Y%m%d_%H%M%S')}.json"
                data = save_project_json()
                ui.download(data, filename, "application/json")
                ui.notify(MSG_SAVE_OK.format(filename=filename), type='positive', timeout=3000)

            ui.button(BTN_SACUVAJ_JSON, on_click=_nova_save).classes(
                'w-full bg-white text-[#111] border border-[#111] mb-4'
            )

            ui.label(LBL_UCITAJ_IZ_FAJLA).classes('text-sm text-gray-600 mb-2')
            _nova_status = ui.label('').classes('text-sm mb-2')
            _pending_raw = [b'']

            async def _extract_raw_upload(e) -> bytes:
                _raw = b''
                try:
                    _file = getattr(e, 'file', None)
                    if _file is not None and hasattr(_file, 'read'):
                        _raw = await _file.read()
                        if _raw:
                            return _raw
                    _content = getattr(e, 'content', None)
                    if hasattr(_content, 'read'):
                        _raw = _content.read()
                        if not _raw and hasattr(_content, 'seek'):
                            _content.seek(0)
                            _raw = _content.read()
                    elif isinstance(_content, (bytes, bytearray)):
                        _raw = bytes(_content)
                    elif isinstance(getattr(e, 'content', None), str):
                        _raw = str(e.content).encode('utf-8')
                    if not _raw:
                        _data = getattr(e, 'data', None)
                        if isinstance(_data, (bytes, bytearray)):
                            _raw = bytes(_data)
                except Exception as ex:
                    _LOG.debug("Nova upload read failed: %s", ex)
                    _raw = b''
                return _raw

            async def _nova_upload(e) -> None:
                _raw = await _extract_raw_upload(e)
                if not _raw:
                    _nova_status.set_text(STATUS_NO_FILE_CONTENT)
                    _nova_status.classes('text-red-600', remove='text-gray-800')
                    ui.notify(STATUS_LOAD_EMPTY_FAIL, type='negative')
                    return
                _pending_raw[0] = _raw
                _nova_status.set_text("Fajl je izabran. Klikni 'Učitaj izabrani fajl'.")
                _nova_status.classes('text-gray-800', remove='text-red-600')

            def _nova_load_selected() -> None:
                _raw = _pending_raw[0]
                if not _raw:
                    _nova_status.set_text(STATUS_NO_FILE_CONTENT)
                    _nova_status.classes('text-red-600', remove='text-gray-800')
                    ui.notify(STATUS_LOAD_EMPTY_FAIL, type='negative')
                    return
                ok, err = load_project_json(_raw)
                if ok:
                    _nova_status.set_text(STATUS_LOAD_OK_DETAIL)
                    _nova_status.classes('text-gray-800 font-semibold', remove='text-red-600')
                    ui.notify(STATUS_LOAD_OK_DETAIL, type='positive')
                    state.room_setup_done = True
                    main_content_refresh()
                else:
                    _nova_status.set_text(ERR_LOAD_PREFIX.format(err=err))
                    _nova_status.classes('text-red-600', remove='text-gray-800')
                    ui.notify(ERR_LOAD_PREFIX.format(err=err), type='negative', timeout=5000)

            _nova_uploader = ui.upload(
                on_upload=_nova_upload,
                auto_upload=True,
            ).props(f'accept=".json" label="{LBL_UPLOAD_JSON}"').classes('w-full')
            ui.button(BTN_UCITAJ_IZABRANI, on_click=_nova_load_selected).classes(
                'w-full bg-white text-[#111] border border-[#111] mt-2'
            )
