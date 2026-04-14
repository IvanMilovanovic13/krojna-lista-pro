# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import logging
import re
from typing import Any, Callable
from i18n import (
    CUTLIST_IMG_UNAVAILABLE_FMT,
)
from ui_catalog_config import translate_template_label

_LOG = logging.getLogger(__name__)


_LABEL_NORMALIZATION = {
    "Le\u0111a": "Ledja",
    "Le\u0111na plo\u010da": "Ledjna ploca",
    "Le\u0111na plo\u010da / prolaz": "Ledjna ploca / prolaz",
    "Bo\u010dna plo\u010da": "Bocna ploca",
    "Bo\u010dna stranica sanduka fioke": "Bocna stranica sanduka fioke",
    "Zavr\u0161na bo\u010dna plo\u010da": "Zavrsna bocna ploca",
    "plo\u010da": "ploca",
    "Le\u00c4\u2018a": "Ledja",
    "Le\u00c3\u201e\u20ac\u02dca": "Ledja",
    "Le\u00c3\u0192\u00e2\u20ac\u017e\u00c3\u00a2\u00e2\u201a\u00ac\u00cb\u0153a": "Ledja",
    "Bo\u00c4\u008dna plo\u00c4\u008da": "Bocna ploca",
    "Bo\u00c3\u201e\u00c2\u008dna plo\u00c3\u201e\u00c2\u008da": "Bocna ploca",
    "Bo\u00c3\u0192\u00e2\u20ac\u017e\u00c3\u201a\u00c2\u008dna plo\u00c3\u0192\u00e2\u20ac\u017e\u00c3\u201a\u00c2\u008da": "Bocna ploca",
    "plo\u00c4\u008da": "ploca",
    "plo\u00c3\u201e\u00c2\u008da": "ploca",
    "plo\u00c3\u0192\u00e2\u20ac\u017e\u00c3\u201a\u00c2\u008da": "ploca",
}


def _normalize_label_text(value: Any) -> str:
    txt = str(value or "").strip()
    for src, dst in _LABEL_NORMALIZATION.items():
        txt = txt.replace(src, dst)
    return re.sub(r"\s+", " ", txt).strip()


def _friendly_part_name(value: Any, lang: str = "sr") -> str:
    txt = _normalize_label_text(value)
    txt = re.sub(r"^[A-Z]\d+\s*[—-]\s*", "", txt)
    mapping_sr = {
        "Leva strana": "Leva stranica korpusa",
        "Desna strana": "Desna stranica korpusa",
        "Dno": "Donja ploča korpusa",
        "Plafon": "Gornja ploča korpusa",
        "Vrata": "Front vrata",
        "Front fioke": "Front fioke",
        "Front fioke (unif.)": "Front fioke",
        "Front fioke (kuhinjska jedinica)": "Front fioke ispod rerne",
        "Front fioke (ispod rerne)": "Front fioke ispod rerne",
        "Vrata (ispod ploce za kuvanje)": "Front vrata ispod ploče",
        "Vrata (ispod sudopere)": "Front vrata ispod sudopere",
        "Vrata rerne": "Front za rernu",
        "Front integrisanog frizidera": "Front ugradnog frizidera",
        "Gornji front frizidera": "Gornji front frizidera",
        "Donji front zamrzivaca": "Donji front zamrzivaca",
        "Zavrsna bocna ploca": "Završna bočna ploča",
        "Bocna ploca": "Bočna stranica sanduka fioke",
        "Prednja strana sanduka": "Prednja strana sanduka fioke",
        "Zadnja strana sanduka": "Zadnja strana sanduka fioke",
        "Dno sanduka": "Dno sanduka fioke",
        "Ledja": "Leđna ploča",
        "Ledja / prolaz": "Leđna ploča / prolaz",
    }
    mapping_en = {
        "Leva strana": "Left carcass side",
        "Desna strana": "Right carcass side",
        "Dno": "Bottom carcass panel",
        "Plafon": "Top carcass panel",
        "Vrata": "Door front",
        "Front fioke": "Drawer front",
        "Front fioke (unif.)": "Drawer front",
        "Front fioke (kuhinjska jedinica)": "Drawer front below oven",
        "Front fioke (ispod rerne)": "Drawer front below oven",
        "Vrata (ispod ploce za kuvanje)": "Door front below hob",
        "Vrata (ispod sudopere)": "Door front below sink",
        "Vrata rerne": "Oven front",
        "Front integrisanog frizidera": "Integrated fridge front",
        "Gornji front frizidera": "Upper fridge front",
        "Donji front zamrzivaca": "Lower freezer front",
        "Zavrsna bocna ploca": "End side panel",
        "Bocna ploca": "Drawer box side",
        "Prednja strana sanduka": "Drawer box front",
        "Zadnja strana sanduka": "Drawer box back",
        "Dno sanduka": "Drawer box bottom",
        "Ledja": "Back panel",
        "Ledja / prolaz": "Back panel / opening",
    }
    mapping_sr.update({str(v): str(k) for k, v in mapping_en.items()})
    mapping = mapping_en if str(lang or "sr").lower().strip() == "en" else mapping_sr
    return mapping.get(txt, txt)


def _friendly_position_name(value: Any, lang: str = "sr") -> str:
    txt = str(value or "").strip()
    mapping_sr = {
        "LEVO": "Levo",
        "DESNO": "Desno",
        "GORE": "Gore",
        "DOLE": "Dole",
        "CENTAR": "Sredina",
        "NAPRED": "Napred",
        "POZADI": "Pozadi",
    }
    mapping_en = {
        "LEVO": "Left",
        "DESNO": "Right",
        "GORE": "Top",
        "DOLE": "Bottom",
        "CENTAR": "Center",
        "NAPRED": "Front",
        "POZADI": "Back",
    }
    mapping_sr.update({str(v): str(k) for k, v in mapping_en.items()})
    mapping = mapping_en if str(lang or "sr").lower().strip() == "en" else mapping_sr
    return mapping.get(txt.upper(), txt)


def _summary_material_label(part_name: Any, material: Any, thickness: Any, lang: str = "sr") -> str:
    part = _normalize_label_text(part_name).lower()
    mat = str(material or "").strip()
    thk = str(thickness or "").strip()
    if "ledj" in part or "ledn" in part or "back" in part:
        role = "Back" if str(lang or "sr").lower().strip() == "en" else "Ledja"
    elif "front" in part or "vrata" in part:
        role = "Front"
    elif "radna ploca" in part or "worktop" in part:
        role = "Worktop" if str(lang or "sr").lower().strip() == "en" else "Radna ploča"
    elif "sokla" in part or "plinth" in part:
        role = "Plinth" if str(lang or "sr").lower().strip() == "en" else "Sokla"
    elif "sanduka" in part or "drawer box" in part or re.match(r"f\d+\s+[—-]", str(part_name or "").lower()):
        role = "Drawer box" if str(lang or "sr").lower().strip() == "en" else "Sanduk fioke"
    else:
        role = "Carcass" if str(lang or "sr").lower().strip() == "en" else "Korpus"
    if not mat:
        return ""
    return f"{mat} {role} / {thk} mm" if thk else f"{mat} {role}"


def render_cutlist_tab(
    *,
    ui: Any,
    state: Any,
    tr_fn: Callable[[str], str],
    pd: Any,
    plt: Any,
    build_cutlist_sections: Callable[[dict], dict],
    generate_cutlist_excel: Callable[[dict], bytes],
    build_pdf_bytes: Callable[[dict], bytes],
    wall_len_h: Callable[[dict], tuple[int, int]],
    render_fn: Callable[..., None],
    fig_to_data_uri_exact: Callable[[Any], str],
    render_element_preview: Callable[[dict, dict], tuple[str, str]],
    svg_for_tid: Callable[[str], str],
    assembly_instructions: Callable[..., list[str]],
) -> None:
    from cutlist import get_final_cutlist_dataset, _translate_export_df
    from export_jobs import enqueue_export_job
    from project_store import (
        ensure_local_user,
        get_export_job,
        get_user_by_email,
        list_export_jobs_for_user,
    )
    from state_logic import build_checkout_start_message, get_cutlist_access_state
    _lang = str(getattr(state, 'language', 'sr') or 'sr').lower().strip()

    def _start_paid_checkout(plan_code: str = 'pro_monthly') -> None:
        ok, msg = build_checkout_start_message(plan_code)
        if ok and str(msg or '').startswith(('http://', 'https://')):
            ui.navigate.to(str(msg), new_tab=True)
            ui.notify(tr_fn('gate.checkout_redirect'), type='positive', timeout=4000)
        else:
            ui.notify(msg or tr_fn('gate.checkout_btn'), type='info' if ok else 'negative', timeout=5000)

    _access = get_cutlist_access_state()
    if str(_access.get('allowed', '')).lower() != 'true':
        with ui.column().classes('w-full max-w-2xl mx-auto py-10 gap-4'):
            with ui.card().classes('w-full p-8 border border-amber-200 bg-white'):
                ui.label(tr_fn('cutlist.locked_title')).classes('text-2xl font-bold text-gray-900')
                ui.label(str(_access.get('reason', '') or tr_fn('cutlist.locked_desc'))).classes(
                    'text-sm text-gray-700'
                )
                ui.button(tr_fn('gate.checkout_btn'), on_click=lambda: _start_paid_checkout('pro_monthly')).classes(
                    'mt-4 bg-[#111] text-white'
                )
                ui.label(tr_fn('cutlist.locked_features_title')).classes('text-xs font-semibold uppercase tracking-[0.18em] text-gray-400 mt-4')
                with ui.column().classes('gap-1'):
                    ui.label(tr_fn('cutlist.locked_feature_1')).classes('text-sm text-gray-600')
                    ui.label(tr_fn('cutlist.locked_feature_2')).classes('text-sm text-gray-600')
                    ui.label(tr_fn('cutlist.locked_feature_3')).classes('text-sm text-gray-600')
                    ui.label(tr_fn('cutlist.locked_feature_4')).classes('text-sm text-gray-600')
                    ui.label(tr_fn('cutlist.locked_feature_5')).classes('text-sm text-gray-600')
        return

    def _active_user():
        _email = str(getattr(state, 'current_user_email', '') or '').strip()
        if _email:
            _user = get_user_by_email(_email)
            if _user is not None:
                return _user
        return ensure_local_user()

    def _queue_export_job(job_type: str):
        try:
            _user = _active_user()
            return enqueue_export_job(
                user_id=int(_user.id),
                project_id=int(getattr(state, 'current_project_id', 0) or 0),
                kitchen=dict(state.kitchen),
                job_type=job_type,
                lang=_lang,
                project_title='Krojna lista PRO' if _lang == 'sr' else 'CabinetCut PRO',
            )
        except Exception as _job_ex:
            _LOG.debug("Export job queue failed: %s", _job_ex)
            raise

    def _build_download_url(result_ref: str) -> str:
        _session_token = str(getattr(state, 'current_session_token', '') or '').strip()
        _download_url = str(result_ref or '')
        if _download_url and _session_token:
            _sep = '&' if '?' in _download_url else '?'
            _download_url = f'{_download_url}{_sep}token={_session_token}'
        return _download_url

    def _watch_export_and_download(job_id: int, job_type: str, attempt: int = 0) -> None:
        try:
            _user = _active_user()
            _job = get_export_job(int(job_id), user_id=int(_user.id))
            if _job is None:
                ui.notify(tr_fn('cutlist.export_job_missing'), type='negative', timeout=5000)
                return

            _status = str(_job.status or '').strip().lower()
            if _status == 'done' and str(_job.result_ref or '').strip():
                _download_url = _build_download_url(str(_job.result_ref or ''))
                ui.navigate.to(_download_url, new_tab=True)
                ui.notify(
                    tr_fn('cutlist.export_download_started', job_type=str(job_type or '').upper()),
                    type='positive',
                    timeout=4000,
                )
                return
            if _status == 'failed':
                ui.notify(
                    tr_fn('cutlist.export_jobs_error', error=str(_job.error_message or 'export_failed')),
                    type='negative',
                    timeout=5000,
                )
                return
            if _status == 'canceled':
                ui.notify(tr_fn('cutlist.export_job_canceled'), type='warning', timeout=4000)
                return
            if attempt >= 120:
                ui.notify(tr_fn('cutlist.export_job_still_processing'), type='warning', timeout=5000)
                return
            ui.timer(0.5, lambda: _watch_export_and_download(int(job_id), job_type, attempt + 1), once=True)
        except Exception as _watch_ex:
            _LOG.debug("Export auto-download watch failed: %s", _watch_ex)
            ui.notify(tr_fn('cutlist.export_watch_error', err=_watch_ex), type='negative', timeout=5000)

    with ui.row().classes('w-full items-center justify-between mb-2'):
        ui.label(tr_fn('cutlist.title')).classes('text-2xl font-bold')

        with ui.row().classes('gap-2 items-center'):
            def _download_pdf():
                try:
                    _job_id = _queue_export_job('pdf')
                    ui.notify(tr_fn('cutlist.export_job_queued', job_type='PDF', job_id=_job_id), type='positive')
                    _watch_export_and_download(int(_job_id), 'PDF')
                except Exception as _pe:
                    _LOG.exception("PDF export queue failed: %s", _pe)
                    ui.notify(tr_fn('cutlist.err_pdf', err=_pe), type='negative')

            ui.button(tr_fn('cutlist.btn_pdf'), on_click=_download_pdf).classes(
                'font-semibold px-4 py-2 rounded shadow'
            ).props('icon=picture_as_pdf').tooltip(tr_fn('cutlist.tooltip_pdf'))

            def _download_excel():
                try:
                    _job_id = _queue_export_job('excel')
                    ui.notify(tr_fn('cutlist.export_job_queued', job_type='Excel', job_id=_job_id), type='positive')
                    _watch_export_and_download(int(_job_id), 'Excel')
                except Exception as _xe_err:
                    ui.notify(tr_fn('cutlist.err_excel', err=_xe_err), type='negative')

            ui.button(tr_fn('cutlist.btn_excel'), on_click=_download_excel).classes(
                'font-semibold px-4 py-2 rounded shadow'
            ).props('icon=table_chart').tooltip(tr_fn('cutlist.tooltip_excel'))

            def _download_wardrobe_csv():
                try:
                    _job_id = _queue_export_job('csv')
                    ui.notify(tr_fn('cutlist.export_job_queued', job_type='CSV', job_id=_job_id), type='positive')
                    _watch_export_and_download(int(_job_id), 'CSV')
                except Exception as _csv_err:
                    ui.notify(tr_fn('cutlist.csv_error', err=_csv_err), type='negative')

            ui.button(tr_fn('cutlist.btn_csv'), on_click=_download_wardrobe_csv).classes(
                'font-semibold px-4 py-2 rounded shadow'
            ).props('icon=description').tooltip(tr_fn('cutlist.csv_tooltip'))

    try:
        final_ds = get_final_cutlist_dataset(state.kitchen, lang=_lang)
        sections = final_ds["sections"]
        service_packet = final_ds["service_packet"]
        summary_packet = final_ds["summary"]
        display_sections = {
            key: _translate_export_df(df, _lang)
            for key, df in sections.items()
        }
        display_service_packet = {
            key: _translate_export_df(df, _lang)
            for key, df in service_packet.items()
        }
        mods = state.kitchen.get('modules', []) or []
        all_dfs = [df for df in display_sections.values() if df is not None and not df.empty]
        _hw_df = display_sections.get('hardware')
        _warnings_df = None
        if _hw_df is not None and not _hw_df.empty and 'Kategorija' in _hw_df.columns:
            _warnings_df = _hw_df[_hw_df['Kategorija'].astype(str).str.lower() == 'warning']

        if not mods:
            ui.label(tr_fn('cutlist.empty')).classes('text-gray-400 mt-4')
            return

        try:
            _job_rows = []
            _user = _active_user()
            for _job in list_export_jobs_for_user(int(_user.id), limit=6):
                _result_ref = str(_job.result_ref or '')
                _download_url = _build_download_url(_result_ref)
                _job_rows.append({
                    'type': tr_fn(f'cutlist.export_job_type_{str(_job.job_type).lower()}') if str(_job.job_type).lower() in {'pdf', 'excel', 'csv'} else str(_job.job_type).upper(),
                    'status': tr_fn(f'cutlist.export_job_status_{str(_job.status).lower()}') if str(_job.status).lower() in {'queued', 'running', 'done', 'failed', 'canceled'} else str(_job.status),
                    'created_at': str(_job.created_at or ''),
                    'result_ref': _result_ref,
                    'download_url': _download_url,
                    'error_message': str(_job.error_message or ''),
                })
            with ui.card().classes('w-full mb-4 p-3 bg-[#f8fafc] border border-[#dbe3ec]'):
                ui.label(tr_fn('cutlist.export_jobs_title')).classes('font-bold text-base mb-2')
                if not _job_rows:
                    ui.label(tr_fn('cutlist.export_jobs_empty')).classes('text-xs text-gray-500')
                else:
                    for _row in _job_rows:
                        with ui.card().classes('w-full p-3 mb-2 bg-white border border-gray-200'):
                            ui.label(
                                tr_fn(
                                    'cutlist.export_jobs_meta',
                                    job_type=str(_row['type']),
                                    status=str(_row['status']),
                                    created_at=str(_row['created_at']),
                                )
                            ).classes('text-xs text-gray-700 font-semibold')
                            if _row['result_ref']:
                                with ui.row().classes('items-center gap-2'):
                                    ui.label(
                                        tr_fn('cutlist.export_jobs_result', result_ref=str(_row['result_ref']))
                                    ).classes('text-xs text-gray-500')
                                    ui.link(
                                        tr_fn('cutlist.export_jobs_download'),
                                        target=str(_row.get('download_url', '') or _row['result_ref']),
                                        new_tab=True,
                                    ).classes('text-xs text-blue-700')
                            if _row['error_message']:
                                ui.label(
                                    tr_fn('cutlist.export_jobs_error', error=str(_row['error_message']))
                                ).classes('text-xs text-red-600')
        except Exception as _jobs_ex:
            _LOG.debug("Export jobs panel failed: %s", _jobs_ex)

        with ui.card().classes('w-full mb-4 p-3 bg-gray-50'):
            ui.label(tr_fn('cutlist.beginner_title')).classes('font-bold text-base mb-2')
            ui.markdown(tr_fn('cutlist.beginner_items'))

        if _warnings_df is not None and not _warnings_df.empty:
            with ui.card().classes('w-full mb-4 p-3 border border-yellow-500 bg-yellow-50'):
                ui.label(tr_fn('cutlist.mfg_warnings', count=len(_warnings_df))).classes('font-bold text-base mb-2')
                for _, _wr in _warnings_df.head(10).iterrows():
                    _wline = f"{_wr.get('Modul', '')}: {_wr.get('Napomena', '')}"
                    ui.label(_wline).classes('text-xs text-yellow-900 leading-snug')

        _worktop_df = display_sections.get('worktop')
        if _worktop_df is not None and not _worktop_df.empty:
            with ui.card().classes('w-full mb-4 p-3 bg-[#f8fafc] border border-[#dbe3ec]'):
                ui.label(tr_fn('cutlist.worktop_spec_title')).classes('font-bold text-base mb-1')
                ui.label(tr_fn('cutlist.worktop_spec_desc')).classes('text-xs text-gray-600 mb-2')
                _worktop_cols = [
                    {'name': 'zid', 'label': tr_fn('cutlist.col_wall'), 'field': 'Zid'},
                    {'name': 'modul', 'label': tr_fn('cutlist.col_module'), 'field': 'Modul'},
                    {'name': 'req', 'label': tr_fn('cutlist.worktop_required_len'), 'field': 'Required length [mm]'},
                    {'name': 'buy', 'label': tr_fn('cutlist.worktop_purchase_len'), 'field': 'Purchase length [mm]'},
                    {'name': 'depth', 'label': tr_fn('cutlist.worktop_depth'), 'field': 'Širina [mm]'},
                    {'name': 'field', 'label': tr_fn('cutlist.worktop_field_cut'), 'field': 'Field cut'},
                    {'name': 'joint', 'label': tr_fn('cutlist.worktop_joint'), 'field': 'Joint type'},
                    {'name': 'protect', 'label': tr_fn('cutlist.worktop_protection'), 'field': 'Edge protection type'},
                    {'name': 'cutouts', 'label': tr_fn('cutlist.worktop_cutouts'), 'field': 'Cutouts'},
                    {'name': 'note', 'label': tr_fn('cutlist.col_note'), 'field': 'Napomena'},
                ]
                ui.table(
                    columns=_worktop_cols,
                    rows=_worktop_df.to_dict('records'),
                ).classes('w-full text-sm')

        with ui.card().classes('w-full mb-4 p-3'):
            ui.label(tr_fn('cutlist.kitchen_overview')).classes('font-bold text-base mb-2')
            try:
                _wl, _wh = wall_len_h(state.kitchen)
                _sc = 5.0 / max(_wh + 280, 1)
                _fw = max((_wl + 260) * _sc, 5.0 * 1.65)
                _fig_k = plt.figure(figsize=(_fw, 5.0))
                _fig_k.patch.set_facecolor('#BFBDBA')
                _ax_k = _fig_k.add_subplot(111)
                render_fn(
                    ax=_ax_k,
                    kitchen=state.kitchen,
                    view_mode='Katalog',
                    show_grid=False,
                    grid_mm=10,
                    show_bounds=False,
                    kickboard=True,
                    ceiling_filler=state.ceiling_filler,
                )
                _fig_k.tight_layout(pad=0.3)
                _uri_k = fig_to_data_uri_exact(_fig_k)
                plt.close(_fig_k)
                ui.image(_uri_k).style('width:100%; height:auto;')
            except Exception as _ek:
                ui.label(CUTLIST_IMG_UNAVAILABLE_FMT.format(err=_ek)).classes('text-xs text-red-400')

        _summary_df = summary_packet.get('summary_all')
        if _summary_df is not None and not _summary_df.empty:
            with ui.card().classes('w-full mb-4 p-3'):
                ui.label(tr_fn('cutlist.summary')).classes('font-bold text-base mb-2')
                with ui.column().classes('w-full gap-1 mb-2'):
                    ui.label(
                        'Legenda za početnika' if _lang != 'en' else 'Beginner legend'
                    ).classes('text-sm font-semibold text-gray-700')
                    _legend_lines = (
                        [
                            'Deo = naziv ploče ili dela elementa',
                            'Kom = koliko komada tog dela treba',
                            'Deb. = debljina ploče u milimetrima',
                            'Dužina / Širina = gotove mere dela',
                            'Materijal = od čega se deo izrađuje',
                            'Orijentacija = smer ploče ili dezena',
                            'Kant = koje ivice se kantuju',
                            'L1/L2 = duže ivice, K1/K2 = kraće ivice',
                            '1 = kantuje se, 0 = ne kantuje se',
                        ]
                        if _lang != 'en'
                        else [
                            'Part = the name of the panel or unit part',
                            'Qty = how many pieces are needed',
                            'Thk. = panel thickness in millimeters',
                            'Length / Width = finished part dimensions',
                            'Material = what the part is made of',
                            'Orientation = board or grain direction',
                            'Edge = which edges get edge banding',
                            'L1/L2 = long edges, K1/K2 = short edges',
                            '1 = edged, 0 = not edged',
                        ]
                    )
                    for _line in _legend_lines:
                        ui.label(_line).classes('text-xs text-gray-600 leading-snug')
                _summary_rows = _summary_df.copy()
                if {'Deo', 'Materijal', 'Deb.'}.issubset(_summary_rows.columns):
                    _summary_rows['Materijal'] = _summary_rows.apply(
                        lambda _r: _summary_material_label(
                            _r.get('Deo', ''),
                            _r.get('Materijal', ''),
                            _r.get('Deb.', ''),
                            _lang,
                        ),
                        axis=1,
                    )
                if 'Kol.' in _summary_rows.columns and 'Kom' not in _summary_rows.columns:
                    _summary_rows['Kom'] = _summary_rows['Kol.']
                _sum_cols = [
                    {'name': 'rb', 'label': 'RB', 'field': 'RB', 'style': 'width: 38px; text-align:right;'},
                    {'name': 'deo', 'label': tr_fn('cutlist.col_part'), 'field': 'Deo', 'style': 'width: 150px; white-space: normal;'},
                    {'name': 'kom', 'label': 'Kom', 'field': 'Kom', 'style': 'width: 48px; text-align:right;'},
                    {'name': 'cw', 'label': tr_fn('cutlist.col_length_mm'), 'field': 'Dužina [mm]', 'style': 'width: 82px; text-align:right;'},
                    {'name': 'ch', 'label': tr_fn('cutlist.col_width_mm'), 'field': 'Širina [mm]', 'style': 'width: 82px; text-align:right;'},
                    {'name': 'deb', 'label': tr_fn('cutlist.col_thickness'), 'field': 'Deb.', 'style': 'width: 54px; text-align:right;'},
                    {'name': 'mat', 'label': tr_fn('cutlist.col_material'), 'field': 'Materijal', 'style': 'width: 170px; white-space: normal;'},
                    {'name': 'ori', 'label': ('Orientation' if _lang == 'en' else 'Orijentacija'), 'field': 'Orijentacija', 'style': 'width: 92px; white-space: normal;'},
                    {'name': 'l1', 'label': 'L1', 'field': 'L1', 'style': 'width: 34px; text-align:center;'},
                    {'name': 'l2', 'label': 'L2', 'field': 'L2', 'style': 'width: 34px; text-align:center;'},
                    {'name': 'k1', 'label': 'K1', 'field': 'K1', 'style': 'width: 34px; text-align:center;'},
                    {'name': 'k2', 'label': 'K2', 'field': 'K2', 'style': 'width: 34px; text-align:center;'},
                ]
                ui.table(columns=_sum_cols, rows=_summary_rows.to_dict('records')).classes('w-full text-xs').props('dense wrap-cells flat square separator=cell')

        _hdr_df = display_service_packet.get('project_header')
        if _hdr_df is not None and not _hdr_df.empty:
            with ui.card().classes('w-full mb-4 p-3'):
                ui.label(tr_fn('cutlist.project_data')).classes('font-bold text-base mb-2')
                ui.table(
                    columns=[
                        {'name': 'polje', 'label': tr_fn('cutlist.col_field'), 'field': 'Polje'},
                        {'name': 'vrednost', 'label': tr_fn('cutlist.col_value'), 'field': 'Vrednost'},
                    ],
                    rows=_hdr_df.to_dict('records'),
                ).classes('w-full')

        _guide_df = display_service_packet.get('user_guide')
        if _guide_df is not None and not _guide_df.empty:
            with ui.card().classes('w-full mb-4 p-3 bg-blue-50'):
                ui.label(tr_fn('cutlist.workflow')).classes('font-bold text-base mb-2')
                ui.table(
                    columns=[
                        {'name': 'korak', 'label': tr_fn('cutlist.col_step'), 'field': 'Korak'},
                        {'name': 'sta', 'label': tr_fn('cutlist.col_what'), 'field': 'Sta radis'},
                        {'name': 'nap', 'label': tr_fn('cutlist.col_note'), 'field': 'Napomena'},
                    ],
                    rows=_guide_df.to_dict('records'),
                ).classes('w-full')

        _svc_instr = display_service_packet.get('service_instructions')
        if _svc_instr is not None and not _svc_instr.empty:
            with ui.card().classes('w-full mb-4 p-3 bg-amber-50'):
                ui.label(tr_fn('cutlist.service_instructions')).classes('font-bold text-base mb-2')
                ui.table(
                    columns=[
                        {'name': 'rb', 'label': 'RB', 'field': 'RB'},
                        {'name': 'stavka', 'label': tr_fn('cutlist.col_item'), 'field': 'Stavka'},
                        {'name': 'instr', 'label': tr_fn('cutlist.col_instruction'), 'field': 'Instrukcija'},
                    ],
                    rows=_svc_instr.to_dict('records'),
                ).classes('w-full text-sm')

        with ui.row().classes('w-full gap-4 items-start mb-4'):
            _svc_cuts = display_service_packet.get('service_cuts')
            if _svc_cuts is not None and not _svc_cuts.empty:
                with ui.card().classes('flex-1 p-3'):
                    ui.label(tr_fn('cutlist.service_cutting')).classes('font-bold text-base mb-2')
                    ui.table(
                        columns=[
                            {'name': 'rb', 'label': 'RB', 'field': 'RB'},
                            {'name': 'zid', 'label': tr_fn('cutlist.col_wall'), 'field': 'Zid'},
                            {'name': 'mat', 'label': tr_fn('cutlist.col_material'), 'field': 'Materijal'},
                            {'name': 'deb', 'label': tr_fn('cutlist.col_thickness'), 'field': 'Deb.'},
                            {'name': 'cw', 'label': tr_fn('cutlist.col_cut_length'), 'field': 'CUT_W [mm]'},
                            {'name': 'ch', 'label': tr_fn('cutlist.col_cut_width'), 'field': 'CUT_H [mm]'},
                            {'name': 'kant', 'label': tr_fn('cutlist.col_edge'), 'field': 'Kant'},
                            {'name': 'kol', 'label': tr_fn('cutlist.col_qty'), 'field': 'Kol.'},
                        ],
                        rows=_svc_cuts.to_dict('records'),
                    ).classes('w-full text-sm')
            _shop_df = display_service_packet.get('shopping_list')
            if _shop_df is not None and not _shop_df.empty:
                with ui.card().classes('flex-1 p-3'):
                    ui.label(tr_fn('cutlist.shopping_extra')).classes('font-bold text-base mb-2')
                    ui.table(
                        columns=[
                            {'name': 'grupa', 'label': tr_fn('cutlist.col_group'), 'field': 'Grupa'},
                            {'name': 'naziv', 'label': tr_fn('cutlist.col_name'), 'field': 'Naziv'},
                            {'name': 'sifra', 'label': tr_fn('cutlist.col_type_code'), 'field': 'Tip / Šifra'},
                            {'name': 'kol', 'label': tr_fn('cutlist.col_qty'), 'field': 'Kol.'},
                            {'name': 'nap', 'label': tr_fn('cutlist.col_note'), 'field': 'Napomena'},
                        ],
                        rows=_shop_df.to_dict('records'),
                    ).classes('w-full text-sm')

        _ready_df = display_service_packet.get('ready_made_items')
        if _ready_df is not None and not _ready_df.empty:
            with ui.expansion(tr_fn('cutlist.ready_made'), icon='shopping_bag').classes('w-full mb-2 border rounded'):
                ui.table(
                    columns=[
                        {'name': 'grupa', 'label': tr_fn('cutlist.col_group'), 'field': 'Grupa'},
                        {'name': 'naziv', 'label': tr_fn('cutlist.col_name'), 'field': 'Naziv'},
                        {'name': 'sifra', 'label': tr_fn('cutlist.col_type_code'), 'field': 'Tip / Šifra'},
                        {'name': 'kol', 'label': tr_fn('cutlist.col_qty'), 'field': 'Kol.'},
                        {'name': 'nap', 'label': tr_fn('cutlist.col_note'), 'field': 'Napomena'},
                    ],
                    rows=_ready_df.to_dict('records'),
                ).classes('w-full text-sm')

        _svc_edge = display_service_packet.get('service_edge')
        if _svc_edge is not None and not _svc_edge.empty:
            with ui.expansion(tr_fn('cutlist.service_edging'), icon='content_cut').classes('w-full mb-2 border rounded'):
                ui.table(
                    columns=[
                        {'name': 'part', 'label': 'PartCode', 'field': 'PartCode'},
                        {'name': 'zid', 'label': tr_fn('cutlist.col_wall'), 'field': 'Zid'},
                        {'name': 'modul', 'label': tr_fn('cutlist.col_module'), 'field': 'Modul'},
                        {'name': 'deo', 'label': tr_fn('cutlist.col_part'), 'field': 'Deo'},
                        {'name': 'kol', 'label': tr_fn('cutlist.col_qty'), 'field': 'Kol.'},
                        {'name': 'kant', 'label': tr_fn('cutlist.col_edge'), 'field': 'Kant'},
                        {'name': 'nap', 'label': tr_fn('cutlist.col_note'), 'field': 'Napomena'},
                    ],
                    rows=_svc_edge.to_dict('records'),
                ).classes('w-full text-sm')

        _svc_proc = display_service_packet.get('service_processing')
        if _svc_proc is not None and not _svc_proc.empty:
            with ui.expansion(tr_fn('cutlist.service_processing'), icon='build').classes('w-full mb-2 border rounded'):
                ui.table(
                    columns=[
                        {'name': 'part', 'label': 'PartCode', 'field': 'PartCode'},
                        {'name': 'zid', 'label': tr_fn('cutlist.col_wall'), 'field': 'Zid'},
                        {'name': 'modul', 'label': tr_fn('cutlist.col_module'), 'field': 'Modul'},
                        {'name': 'deo', 'label': tr_fn('cutlist.col_part'), 'field': 'Deo'},
                        {'name': 'tip', 'label': tr_fn('cutlist.col_processing_type'), 'field': 'Tip obrade'},
                        {'name': 'izvodi', 'label': tr_fn('cutlist.col_ops'), 'field': 'Izvodi'},
                        {'name': 'osnov', 'label': tr_fn('cutlist.col_basis'), 'field': 'Osnov izvođenja'},
                        {'name': 'kol', 'label': tr_fn('cutlist.col_qty'), 'field': 'Kol.'},
                        {'name': 'obr', 'label': tr_fn('cutlist.col_processing_note'), 'field': 'Obrada / napomena'},
                    ],
                    rows=_svc_proc.to_dict('records'),
                ).classes('w-full text-sm')

        with ui.row().classes('w-full gap-4 items-start mb-4'):
            _wcl = display_service_packet.get('workshop_checklist')
            if _wcl is not None and not _wcl.empty:
                with ui.card().classes('flex-1 p-3'):
                    ui.label(tr_fn('cutlist.checklist_service')).classes('font-bold text-base mb-2')
                    ui.table(
                        columns=[
                            {'name': 'rb', 'label': 'RB', 'field': 'RB'},
                            {'name': 'stavka', 'label': tr_fn('cutlist.col_item'), 'field': 'Stavka'},
                            {'name': 'status', 'label': tr_fn('cutlist.col_status'), 'field': 'Status'},
                        ],
                        rows=_wcl.to_dict('records'),
                    ).classes('w-full text-sm')
            _hcl = display_service_packet.get('home_checklist')
            if _hcl is not None and not _hcl.empty:
                with ui.card().classes('flex-1 p-3'):
                    ui.label(tr_fn('cutlist.checklist_assembly')).classes('font-bold text-base mb-2')
                    ui.table(
                        columns=[
                            {'name': 'rb', 'label': 'RB', 'field': 'RB'},
                            {'name': 'stavka', 'label': tr_fn('cutlist.col_item'), 'field': 'Stavka'},
                            {'name': 'status', 'label': tr_fn('cutlist.col_status'), 'field': 'Status'},
                        ],
                        rows=_hcl.to_dict('records'),
                    ).classes('w-full text-sm')

        _titles = {
            'carcass': tr_fn('cutlist.section_carcass'),
            'backs': tr_fn('cutlist.section_backs'),
            'fronts': tr_fn('cutlist.section_fronts'),
            'drawer_boxes': tr_fn('cutlist.section_drawers'),
            'worktop': tr_fn('cutlist.section_worktop'),
            'plinth': tr_fn('cutlist.section_plinth'),
            'hardware': tr_fn('cutlist.section_hardware'),
        }
        _sec_cols = [
            {'name': 'part', 'label': 'PartCode', 'field': 'PartCode'},
            {'name': 'zid', 'label': tr_fn('cutlist.col_wall'), 'field': 'Zid'},
            {'name': 'modul', 'label': tr_fn('cutlist.col_module'), 'field': 'Modul'},
            {'name': 'deo', 'label': tr_fn('cutlist.col_part'), 'field': 'Deo'},
            {'name': 'poz', 'label': tr_fn('cutlist.col_position'), 'field': 'Pozicija'},
            {'name': 'korak', 'label': tr_fn('cutlist.col_step'), 'field': 'SklopKorak'},
            {'name': 'cw', 'label': tr_fn('cutlist.col_length_mm'), 'field': 'CUT_W [mm]'},
            {'name': 'ch', 'label': tr_fn('cutlist.col_width_mm'), 'field': 'CUT_H [mm]'},
            {'name': 'deb', 'label': tr_fn('cutlist.col_thickness'), 'field': 'Deb.'},
            {'name': 'kol', 'label': tr_fn('cutlist.col_qty'), 'field': 'Kol.'},
            {'name': 'kant', 'label': tr_fn('cutlist.col_edge'), 'field': 'Kant'},
            {'name': 'nap', 'label': tr_fn('cutlist.col_note'), 'field': 'Napomena'},
        ]
        _hw_cols = [
            {'name': 'part', 'label': 'PartCode', 'field': 'PartCode'},
            {'name': 'zid', 'label': tr_fn('cutlist.col_wall'), 'field': 'Zid'},
            {'name': 'modul', 'label': tr_fn('cutlist.col_module'), 'field': 'Modul'},
            {'name': 'kat', 'label': tr_fn('cutlist.col_category'), 'field': 'Kategorija'},
            {'name': 'naziv', 'label': tr_fn('cutlist.col_name'), 'field': 'Naziv'},
            {'name': 'sifra', 'label': tr_fn('cutlist.col_type_code'), 'field': 'Tip / Šifra'},
            {'name': 'korak', 'label': tr_fn('cutlist.col_step'), 'field': 'SklopKorak'},
            {'name': 'kol', 'label': tr_fn('cutlist.col_qty'), 'field': 'Kol.'},
            {'name': 'nap', 'label': tr_fn('cutlist.col_note'), 'field': 'Napomena'},
        ]
        for _sk, _df in display_sections.items():
            if _df is None or _df.empty:
                continue
            with ui.expansion(_titles.get(_sk, _sk.capitalize()), icon='table_rows').classes(
                'w-full mb-2 border rounded'
            ):
                ui.table(
                    columns=_hw_cols if _sk == 'hardware' else _sec_cols,
                    rows=_df.to_dict('records')
                ).classes('w-full text-sm')

        ui.separator().classes('my-4')
        ui.label(tr_fn('cutlist.by_element')).classes('text-xl font-bold mb-3')
        with ui.card().classes('w-full mb-3 p-3 bg-gray-50'):
            ui.label(
                'Legenda za detalje po elementu' if _lang != 'en' else 'Legend for unit details'
            ).classes('text-sm font-semibold text-gray-700 mb-1')
            _by_unit_legend = (
                [
                    'PartCode = interna oznaka dela',
                    'Pozicija = gde deo ide na elementu',
                    'SklopKorak = kojim redom se sklapa',
                    'Kant = kantovanje ivica',
                    'Materijal = materijal i namena dela',
                ]
                if _lang != 'en'
                else [
                    'PartCode = internal part label',
                    'Position = where the part goes on the unit',
                    'Step = assembly order',
                    'Edge = edge banding',
                    'Material = material and part purpose',
                ]
            )
            for _line in _by_unit_legend:
                ui.label(_line).classes('text-xs text-gray-600 leading-snug')
        _elem_cols = [
            {'name': 'part', 'label': 'PartCode', 'field': 'PartCode'},
            {'name': 'deo', 'label': tr_fn('cutlist.col_part'), 'field': 'Deo'},
            {'name': 'poz', 'label': tr_fn('cutlist.col_position'), 'field': 'Pozicija'},
            {'name': 'korak', 'label': tr_fn('cutlist.col_step'), 'field': 'SklopKorak'},
            {'name': 'cw', 'label': tr_fn('cutlist.col_length_mm'), 'field': 'CUT_W [mm]'},
            {'name': 'ch', 'label': tr_fn('cutlist.col_width_mm'), 'field': 'CUT_H [mm]'},
            {'name': 'deb', 'label': tr_fn('cutlist.col_thickness'), 'field': 'Deb.'},
            {'name': 'kol', 'label': tr_fn('cutlist.col_qty'), 'field': 'Kol.'},
            {'name': 'kant', 'label': tr_fn('cutlist.col_edge'), 'field': 'Kant'},
        ]
        _combined_e = summary_packet.get('summary_detaljna')
        _combined_has_id = (
            _combined_e is not None
            and not _combined_e.empty
            and 'ID' in _combined_e.columns
        )

        for _m in mods:
            _mid = int(_m.get('id', 0))
            _mlbl_raw = str(_m.get('label', ''))
            _mzone = str(_m.get('zone', 'base')).lower()
            _mw = int(_m.get('w_mm', 0))
            _mh = int(_m.get('h_mm', 0))
            _md = int(_m.get('d_mm', 0))
            _mtid = str(_m.get('template_id', ''))
            _mlbl = translate_template_label(_mlbl_raw, _lang)

            _hdr = f'#{_mid} - {_mlbl}  ({_mw}x{_mh}x{_md} mm)'
            with ui.expansion(_hdr, icon='view_in_ar').classes('w-full mb-3 border border-gray-200 rounded'):
                _mparts = None
                if _combined_has_id:
                    _mparts = _combined_e[_combined_e['ID'] == _mid]
                    if _mparts is not None and not _mparts.empty and {'Deo', 'Materijal', 'Deb.'}.issubset(_mparts.columns):
                        _mparts = _mparts.copy()
                        _mparts['Materijal'] = _mparts.apply(
                            lambda _r: _summary_material_label(
                                _r.get('Deo', ''),
                                _r.get('Materijal', ''),
                                _r.get('Deb.', ''),
                                _lang,
                            ),
                            axis=1,
                        )
                with ui.row().classes('w-full gap-4 items-start p-2'):
                    with ui.column().classes('shrink-0 gap-2'):
                        try:
                            _part_rows = _mparts.to_dict('records') if _mparts is not None and not _mparts.empty else None
                            _uri_2d, _uri_3d = render_element_preview(
                                _m,
                                state.kitchen,
                                label_mode='part_codes',
                                part_rows=_part_rows,
                            )
                            with ui.row().classes('gap-2 items-start'):
                                with ui.column().classes('items-center gap-0.5'):
                                    ui.label(tr_fn('cutlist.preview_2d')).classes('text-[10px] text-gray-400 font-semibold')
                                    ui.image(_uri_2d).style(
                                        'width:110px; height:auto; border:1px solid #ddd; border-radius:4px;'
                                    )
                                    ui.label(tr_fn('cutlist.preview_note_short')).classes('text-[10px] text-amber-700')
                                with ui.column().classes('items-center gap-0.5'):
                                    ui.label(tr_fn('cutlist.preview_3d')).classes('text-[10px] text-gray-400 font-semibold')
                                    ui.image(_uri_3d).style(
                                        'width:140px; height:auto; border:1px solid #ddd; border-radius:4px;'
                                    )
                        except Exception as ex:
                            _LOG.debug('Cutlist tab: fallback to SVG preview for template %s: %s', _mtid, ex)
                            ui.html(svg_for_tid(_mtid)).classes('w-32 h-32')

                    with ui.column().classes('flex-1 gap-2'):
                        if _mparts is not None and not _mparts.empty:
                            _map_df = _mparts[['PartCode', 'Deo', 'Pozicija', 'SklopKorak', 'Kol.']].copy()
                            _map_df['Deo'] = _map_df['Deo'].map(lambda v: _friendly_part_name(v, _lang))
                            _map_df['Pozicija'] = _map_df['Pozicija'].map(lambda v: _friendly_position_name(v, _lang))
                            _map_df = _map_df.sort_values(['SklopKorak', 'PartCode']).reset_index(drop=True)
                            ui.label(tr_fn('cutlist.parts_map')).classes('text-sm font-semibold text-gray-700')
                            ui.table(
                                columns=[
                                    {'name': 'part', 'label': 'PartCode', 'field': 'PartCode'},
                                    {'name': 'deo', 'label': tr_fn('cutlist.col_part'), 'field': 'Deo'},
                                    {'name': 'poz', 'label': tr_fn('cutlist.where_goes'), 'field': 'Pozicija'},
                                    {'name': 'korak', 'label': tr_fn('cutlist.col_step'), 'field': 'SklopKorak'},
                                    {'name': 'kol', 'label': tr_fn('cutlist.pieces'), 'field': 'Kol.'},
                                ],
                                rows=_map_df.to_dict('records'),
                            ).classes('w-full text-xs')
                            ui.label(tr_fn('cutlist.preview_note_full')).classes('text-[11px] text-gray-600')
                            ui.label(tr_fn('cutlist.section_cuts')).classes('text-sm font-semibold text-gray-700')
                            _cuts_df = _mparts.copy()
                            _cuts_df['Deo'] = _cuts_df['Deo'].map(lambda v: _friendly_part_name(v, _lang))
                            _cuts_df['Pozicija'] = _cuts_df['Pozicija'].map(lambda v: _friendly_position_name(v, _lang))
                            ui.table(columns=_elem_cols, rows=_cuts_df.to_dict('records')).classes('w-full text-xs')

                        ui.label(tr_fn('cutlist.section_assembly')).classes('text-sm font-semibold text-gray-700 mt-2')
                        if _mparts is not None and not _mparts.empty:
                            _needed_cols = {'PartCode', 'Deo', 'Pozicija', 'Kol.', 'SklopKorak'}
                            if _needed_cols.issubset(set(_mparts.columns)):
                                _asm = _mparts.copy()
                                _asm['_korak_sort'] = pd.to_numeric(_asm['SklopKorak'], errors='coerce').fillna(99).astype(int)
                                _asm = _asm.sort_values(['_korak_sort', 'PartCode']).reset_index(drop=True)
                                with ui.column().classes('gap-0.5 mb-1'):
                                    for _, _r in _asm.iterrows():
                                        _line = (
                                            tr_fn(
                                                'cutlist.asm_step_line',
                                                step=_r.get('SklopKorak', '-'),
                                                part=_r.get('PartCode', ''),
                                                piece=_friendly_part_name(_r.get('Deo', ''), _lang),
                                                position=_friendly_position_name(_r.get('Pozicija', '-'), _lang),
                                                qty=_r.get('Kol.', 1),
                                            )
                                        )
                                        ui.label(_line).classes('text-xs text-gray-700 leading-snug')

                        _steps = assembly_instructions(_mtid, _mzone, m=_m, kitchen=state.kitchen, lang=_lang)
                        with ui.column().classes('gap-0.5'):
                            for _step in _steps:
                                ui.label(_step).classes('text-xs text-gray-600 leading-snug')
    except Exception as e:
        ui.label(tr_fn('cutlist.err_generic', err=e)).classes('text-red-500')
