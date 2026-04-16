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
    save_to_account: Callable[[str], tuple[bool, str]] | None = None,
    list_account_projects: Callable[[], list[dict]] | None = None,
    load_from_account: Callable[[int], tuple[bool, str]] | None = None,
):
    """Vrati save/load handlere za toolbar, bez promene business logike."""

    def _toolbar_save() -> None:
        from datetime import datetime as _dt

        is_authenticated = int(getattr(state, 'current_user_id', 0) or 0) > 0

        if is_authenticated and save_to_account is not None:
            current_name = str(getattr(state, 'current_project_name', '') or '').strip()
            if current_name:
                # Projekat vec ima naziv — odmah sacuvaj bez dijaloga
                ok, result = save_to_account(current_name)
                if ok:
                    ui.notify(tr_fn('project_io.account_save_ok', name=result), type='positive', timeout=3000)
                else:
                    ui.notify(tr_fn('project_io.account_save_fail', err=result), type='negative', timeout=5000)
            else:
                # Novi projekat — pitaj za naziv
                with ui.dialog() as _dlg:
                    _dlg.open()
                    with ui.card().classes('p-6 min-w-80 gap-3'):
                        ui.label(tr_fn('project_io.save_name_title')).classes('text-lg font-bold')
                        _name_input = ui.input(
                            label=tr_fn('project_io.save_name_label'),
                            value=f"Kuhinja_{_dt.now().strftime('%d%m%Y')}",
                        ).props('id=toolbar-save-name-input').classes('w-full')

                        def _do_save() -> None:
                            name_val = str(_name_input.value or '').strip() or f"Kuhinja_{_dt.now().strftime('%d%m%Y')}"
                            ok, result = save_to_account(name_val)
                            _dlg.close()
                            if ok:
                                ui.notify(tr_fn('project_io.account_save_ok', name=result), type='positive', timeout=3000)
                            else:
                                ui.notify(tr_fn('project_io.account_save_fail', err=result), type='negative', timeout=5000)

                        with ui.row().classes('w-full gap-3 mt-2'):
                            ui.button(tr_fn('project_io.save_confirm'), on_click=_do_save).classes(
                                'flex-1 bg-[#111] text-white'
                            )
                            ui.button(tr_fn('project_io.cancel'), on_click=_dlg.close).classes(
                                'flex-1 bg-white text-[#111] border border-[#111]'
                            )
            return

        # Anoniman korisnik — download .json
        filename = f"kuhinja_{_dt.now().strftime('%Y%m%d_%H%M%S')}.json"
        data = save_project_json()
        ui.download(data, filename, "application/json")
        ui.notify(tr_fn('project_io.save_ok', filename=filename), type='positive', timeout=3000)

    def _toolbar_load() -> None:
        is_authenticated = int(getattr(state, 'current_user_id', 0) or 0) > 0

        if is_authenticated and list_account_projects is not None and load_from_account is not None:
            with ui.dialog().props('full-width') as _dlg:
                _dlg.open()
                with ui.card().classes('p-6 gap-4').style('width: 600px; max-width: 96vw;'):
                    ui.label(tr_fn('project_io.account_load_title')).classes('text-xl font-bold text-gray-900')
                    projects = list_account_projects()
                    if not projects:
                        ui.label(tr_fn('project_io.account_load_empty')).classes('text-sm text-gray-500')
                    else:
                        with ui.scroll_area().style('width: 100%; max-height: 400px;'):
                            for item in projects:
                                pid = int(item.get('project_id', 0) or 0)
                                name = str(item.get('name', '') or tr_fn('project_io.account_load_unknown'))
                                updated = str(item.get('updated_at', '') or item.get('last_opened_at', '') or '')
                                updated_short = updated[:16] if updated else ''

                                def _do_load(project_id=pid) -> None:
                                    ok, err = load_from_account(project_id)
                                    _dlg.close()
                                    if ok:
                                        state.room_setup_done = True
                                        main_content_refresh()
                                        ui.notify(tr_fn('project_io.account_load_ok'), type='positive')
                                    else:
                                        ui.notify(tr_fn('project_io.account_load_fail', err=err), type='negative', timeout=5000)

                                with ui.card().classes('w-full p-4 mb-2 border border-gray-200 bg-white shadow-sm'):
                                    with ui.row().classes('w-full items-center justify-between gap-4'):
                                        with ui.column().classes('gap-1 flex-1'):
                                            ui.label(name).classes('text-base font-bold text-gray-900')
                                            if updated_short:
                                                ui.label(updated_short).classes('text-sm text-gray-500')
                                        ui.button(
                                            tr_fn('project_io.account_load_open'),
                                            on_click=_do_load,
                                        ).classes('bg-[#111] text-white px-5 py-2 text-sm font-medium')
                    ui.button(tr_fn('project_io.cancel'), on_click=_dlg.close).classes(
                        'w-full bg-white text-[#111] border border-[#111] mt-2'
                    )
            return

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
