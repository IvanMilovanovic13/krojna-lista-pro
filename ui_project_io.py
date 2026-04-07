# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Callable


def make_toolbar_actions(
    *,
    ui: Any,
    state: Any,
    logger: Any,
    tr_fn: Callable[[str], str],
    save_project_json: Callable[[], bytes],
    load_project_json: Callable[[bytes], tuple[bool, str]],
    main_content_refresh: Callable[[], None],
):
    """Vrati save/load handlere za toolbar, bez promene business logike."""

    def _toolbar_save() -> None:
        from datetime import datetime as _dt

        filename = f"kuhinja_{_dt.now().strftime('%Y%m%d_%H%M%S')}.json"
        data = save_project_json()
        ui.download(data, filename, "application/json")
        ui.notify(tr_fn('project_io.save_ok', filename=filename), type='positive', timeout=3000)

    def _toolbar_load() -> None:
        with ui.dialog() as _dlg:
            _dlg.open()
            with ui.card().classes('p-6 min-w-96 gap-3'):
                ui.label(tr_fn('project_io.load_title')).classes('text-lg font-bold')
                ui.label(tr_fn('project_io.load_desc')).classes('text-sm text-gray-500')

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
                        _status.set_text(tr_fn('project_io.content_missing'))
                        _status.classes('text-red-600', remove='text-gray-700')
                        ui.notify(tr_fn('project_io.load_empty_fail'), type='negative')
                        return
                    _pending_raw[0] = _raw
                    _status.set_text(tr_fn('project_io.file_selected'))
                    _status.classes('text-gray-700', remove='text-red-600')

                def _do_load_selected() -> None:
                    _raw = _pending_raw[0]
                    if not _raw:
                        _status.set_text(tr_fn('project_io.content_missing'))
                        _status.classes('text-red-600', remove='text-gray-700')
                        ui.notify(tr_fn('project_io.load_empty_fail'), type='negative')
                        return
                    ok, err = load_project_json(_raw)
                    if ok:
                        _status.set_text(tr_fn('project_io.load_ok'))
                        _status.classes('text-gray-700 font-semibold', remove='text-red-600')
                        ui.notify(tr_fn('project_io.project_loaded_ok'), type='positive')
                        state.room_setup_done = True
                        _dlg.close()
                        main_content_refresh()
                    else:
                        _status.set_text(tr_fn('project_io.load_error', err=err))
                        _status.classes('text-red-600', remove='text-gray-700')
                        ui.notify(tr_fn('project_io.load_error', err=err), type='negative', timeout=5000)

                ui.upload(
                    on_upload=_handle_upload,
                    auto_upload=True,
                ).props(f'accept=".json" label="{tr_fn("project_io.upload_label")}"').classes('w-full')
                ui.button(tr_fn('project_io.load_selected'), on_click=_do_load_selected).classes(
                    'w-full bg-white text-[#111] border border-[#111]'
                )
                ui.button(tr_fn('project_io.cancel'), on_click=_dlg.close).classes('w-full')

    return _toolbar_save, _toolbar_load
