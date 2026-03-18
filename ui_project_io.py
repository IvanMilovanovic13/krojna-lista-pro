# -*- coding: utf-8 -*-
from __future__ import annotations

from i18n import (
    BTN_OTKAZI,
    BTN_UCITAJ_IZABRANI,
    DLG_UCITAJ_PROJEKAT_DESC,
    DLG_UCITAJ_PROJEKAT_TITLE,
    ERR_LOAD_PREFIX,
    LBL_UPLOAD_JSON,
    MSG_SAVE_OK,
    STATUS_LOAD_CONTENT_MISSING,
    STATUS_LOAD_EMPTY_FAIL,
    STATUS_LOAD_OK_DETAIL,
    STATUS_PROJECT_LOADED_OK,
)


def make_toolbar_actions(
    *,
    ui,
    state,
    logger,
    save_project_json,
    load_project_json,
    main_content_refresh,
):
    """Vrati save/load handlere za toolbar, bez promene business logike."""

    def _toolbar_save() -> None:
        from datetime import datetime as _dt

        filename = f"kuhinja_{_dt.now().strftime('%Y%m%d_%H%M%S')}.json"
        data = save_project_json()
        ui.download(data, filename, "application/json")
        ui.notify(MSG_SAVE_OK.format(filename=filename), type='positive', timeout=3000)

    def _toolbar_load() -> None:
        with ui.dialog() as _dlg:
            _dlg.open()
            with ui.card().classes('p-6 min-w-96 gap-3'):
                ui.label(DLG_UCITAJ_PROJEKAT_TITLE).classes('text-lg font-bold')
                ui.label(DLG_UCITAJ_PROJEKAT_DESC).classes('text-sm text-gray-500')

                _status = ui.label('').classes('text-sm')
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
                        logger.debug("Load upload read failed: %s", ex)
                        _raw = b''
                    return _raw

                async def _handle_upload(e) -> None:
                    _raw = await _extract_raw_upload(e)
                    if not _raw:
                        _status.set_text(STATUS_LOAD_CONTENT_MISSING)
                        _status.classes('text-red-600', remove='text-gray-700')
                        ui.notify(STATUS_LOAD_EMPTY_FAIL, type='negative')
                        return
                    _pending_raw[0] = _raw
                    _status.set_text("Fajl je izabran. Klikni 'Učitaj izabrani fajl'.")
                    _status.classes('text-gray-700', remove='text-red-600')

                def _do_load_selected() -> None:
                    _raw = _pending_raw[0]
                    if not _raw:
                        _status.set_text(STATUS_LOAD_CONTENT_MISSING)
                        _status.classes('text-red-600', remove='text-gray-700')
                        ui.notify(STATUS_LOAD_EMPTY_FAIL, type='negative')
                        return
                    ok, err = load_project_json(_raw)
                    if ok:
                        _status.set_text(STATUS_LOAD_OK_DETAIL)
                        _status.classes('text-gray-700 font-semibold', remove='text-red-600')
                        ui.notify(STATUS_PROJECT_LOADED_OK, type='positive')
                        state.room_setup_done = True
                        _dlg.close()
                        main_content_refresh()
                    else:
                        _status.set_text(ERR_LOAD_PREFIX.format(err=err))
                        _status.classes('text-red-600', remove='text-gray-700')
                        ui.notify(ERR_LOAD_PREFIX.format(err=err), type='negative', timeout=5000)

                _uploader = ui.upload(
                    on_upload=_handle_upload,
                    auto_upload=True,
                ).props(f'accept=".json" label="{LBL_UPLOAD_JSON}"').classes('w-full')
                ui.button(BTN_UCITAJ_IZABRANI, on_click=_do_load_selected).classes(
                    'w-full bg-white text-[#111] border border-[#111]'
                )

                ui.button(BTN_OTKAZI, on_click=_dlg.close).classes('w-full')

    return _toolbar_save, _toolbar_load
