# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
import re
from typing import Any, Callable
from i18n import (
    CUTLIST_BTN_EXCEL,
    CUTLIST_BTN_PDF,
    CUTLIST_BY_ELEMENT,
    CUTLIST_EMPTY,
    CUTLIST_ERR_EXCEL,
    CUTLIST_ERR_PDF,
    CUTLIST_KITCHEN_OVERVIEW,
    CUTLIST_IMG_UNAVAILABLE_FMT,
    CUTLIST_NOTIFY_EXCEL_OK,
    CUTLIST_NOTIFY_PDF_OK,
    CUTLIST_SECTION_ASSEMBLY,
    CUTLIST_SECTION_CUTS,
    CUTLIST_SUMMARY,
    CUTLIST_TITLE,
    CUTLIST_TOOLTIP_EXCEL,
    CUTLIST_TOOLTIP_PDF,
    CUTLIST_ERR_GENERIC_FMT,
    CUTLIST_PREVIEW_2D,
    CUTLIST_PREVIEW_3D,
    CUTLIST_BEGINNER_CHECK_TITLE,
    CUTLIST_BEGINNER_CHECK_ITEMS,
)

_LOG = logging.getLogger(__name__)


def _friendly_part_name(value: Any) -> str:
    txt = str(value or "").strip()
    txt = re.sub(r"^[A-Z]\d+\s*[—-]\s*", "", txt)
    mapping = {
        "Leva strana": "Leva stranica korpusa",
        "Desna strana": "Desna stranica korpusa",
        "Dno": "Donja ploča korpusa",
        "Plafon": "Gornja ploča korpusa",
        "Vrata": "Front vrata",
        "Front fioke": "Front fioke",
        "Front fioke (unif.)": "Front fioke",
        "Front fioke (kuhinjska jedinica)": "Front fioke ispod rerne",
        "Front fioke (ispod rerne)": "Front fioke ispod rerne",
        "Vrata (ispod ploče za kuvanje)": "Front vrata ispod ploče",
        "Vrata (ispod sudopere)": "Front vrata ispod sudopere",
        "Vrata rerne": "Front za rernu",
        "Front integrisanog frižidera": "Front ugradnog frižidera",
        "Gornji front frižidera": "Gornji front frižidera",
        "Donji front zamrzivača": "Donji front zamrzivača",
        "Završna bočna ploča": "Završna bočna ploča",
        "Bočna ploča": "Bočna ploča",
        "Prednja strana sanduka": "Prednja strana sanduka fioke",
        "Zadnja strana sanduka": "Zadnja strana sanduka fioke",
        "Dno sanduka": "Dno sanduka fioke",
        "Bočna ploča": "Bočna stranica sanduka fioke",
        "Leđa": "Leđna ploča",
        "Ledja": "Leđna ploča",
        "Ledja / prolaz": "Leđna ploča / prolaz",
    }
    return mapping.get(txt, txt)


def _friendly_position_name(value: Any) -> str:
    txt = str(value or "").strip()
    mapping = {
        "LEVO": "Levo",
        "DESNO": "Desno",
        "GORE": "Gore",
        "DOLE": "Dole",
        "CENTAR": "Sredina",
        "NAPRED": "Napred",
        "POZADI": "Pozadi",
    }
    return mapping.get(txt.upper(), txt)


def render_cutlist_tab(
    *,
    ui: Any,
    state: Any,
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
    from cutlist import build_service_packet

    with ui.row().classes('w-full items-center justify-between mb-2'):
        ui.label(CUTLIST_TITLE).classes('text-2xl font-bold')

        with ui.row().classes('gap-2 items-center'):
            def _download_pdf():
                try:
                    _kb = build_pdf_bytes(state.kitchen)
                    import datetime as _dt
                    _fname = f'krojna_lista_{_dt.date.today().strftime("%Y%m%d")}.pdf'
                    ui.download(_kb, filename=_fname, media_type='application/pdf')
                    ui.notify(CUTLIST_NOTIFY_PDF_OK, type='positive')
                except Exception as _pe:
                    _LOG.exception("PDF export failed: %s", _pe)
                    ui.notify(CUTLIST_ERR_PDF.format(err=_pe), type='negative')

            ui.button(CUTLIST_BTN_PDF, on_click=_download_pdf).classes(
                'font-semibold px-4 py-2 rounded shadow'
            ).props('icon=picture_as_pdf').tooltip(CUTLIST_TOOLTIP_PDF)

            def _download_excel():
                try:
                    import datetime as _dt
                    _xe = generate_cutlist_excel(state.kitchen)
                    _fname = f'krojna_lista_{_dt.date.today().strftime("%Y%m%d")}.xlsx'
                    ui.download(
                        _xe,
                        filename=_fname,
                        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    )
                    ui.notify(CUTLIST_NOTIFY_EXCEL_OK, type='positive')
                except Exception as _xe_err:
                    ui.notify(CUTLIST_ERR_EXCEL.format(err=_xe_err), type='negative')

            ui.button(CUTLIST_BTN_EXCEL, on_click=_download_excel).classes(
                'font-semibold px-4 py-2 rounded shadow'
            ).props('icon=table_chart').tooltip(CUTLIST_TOOLTIP_EXCEL)

            def _download_wardrobe_csv():
                try:
                    from cutlist import generate_wardrobe_sections_csv
                    import datetime as _dt
                    _csv = generate_wardrobe_sections_csv(state.kitchen)
                    _fname = f'krojna_lista_ormar_{_dt.date.today().strftime("%Y%m%d")}.csv'
                    ui.download(_csv, filename=_fname, media_type='text/csv; charset=utf-8')
                    ui.notify('CSV krojna lista (americki ormar) preuzimanje pokrenuto.', type='positive')
                except Exception as _csv_err:
                    ui.notify(f'Greska pri generisanju CSV: {_csv_err}', type='negative')

            ui.button('CSV', on_click=_download_wardrobe_csv).classes(
                'font-semibold px-4 py-2 rounded shadow'
            ).props('icon=description').tooltip('Preuzmi CSV za sekcije americkog ormara')

    try:
        sections = build_cutlist_sections(state.kitchen)
        service_packet = build_service_packet(state.kitchen, sections)
        mods = state.kitchen.get('modules', []) or []
        all_dfs = [df for df in sections.values() if df is not None and not df.empty]
        _hw_df = sections.get('hardware')
        _warnings_df = None
        if _hw_df is not None and not _hw_df.empty and 'Kategorija' in _hw_df.columns:
            _warnings_df = _hw_df[_hw_df['Kategorija'].astype(str).str.lower() == 'warning']

        if not mods:
            ui.label(CUTLIST_EMPTY).classes('text-gray-400 mt-4')
            return

        with ui.card().classes('w-full mb-4 p-3 bg-gray-50'):
            ui.label(CUTLIST_BEGINNER_CHECK_TITLE).classes('font-bold text-base mb-2')
            ui.markdown(CUTLIST_BEGINNER_CHECK_ITEMS)

        if _warnings_df is not None and not _warnings_df.empty:
            with ui.card().classes('w-full mb-4 p-3 border border-yellow-500 bg-yellow-50'):
                ui.label(f'Manufacturing upozorenja: {len(_warnings_df)}').classes('font-bold text-base mb-2')
                for _, _wr in _warnings_df.head(10).iterrows():
                    _wline = f"{_wr.get('Modul', '')}: {_wr.get('Napomena', '')}"
                    ui.label(_wline).classes('text-xs text-yellow-900 leading-snug')

        with ui.card().classes('w-full mb-4 p-3'):
            ui.label(CUTLIST_KITCHEN_OVERVIEW).classes('font-bold text-base mb-2')
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

        if all_dfs:
            with ui.card().classes('w-full mb-4 p-3'):
                ui.label(CUTLIST_SUMMARY).classes('font-bold text-base mb-2')
                _combined = pd.concat(all_dfs, ignore_index=True)
                _summary = (
                    _combined.groupby(
                        ['Materijal', 'Deb.', 'CUT_W [mm]', 'CUT_H [mm]', 'Kant'], as_index=False
                    )
                    .agg({'Kol.': 'sum'})
                    .sort_values(['Materijal', 'CUT_W [mm]', 'CUT_H [mm]'])
                )
                _sum_cols = [
                    {'name': 'mat', 'label': 'Materijal', 'field': 'Materijal'},
                    {'name': 'deb', 'label': 'Deb.', 'field': 'Deb.'},
                    {'name': 'cw', 'label': 'Dužina [mm]', 'field': 'CUT_W [mm]'},
                    {'name': 'ch', 'label': 'Širina [mm]', 'field': 'CUT_H [mm]'},
                    {'name': 'kant', 'label': 'Kant', 'field': 'Kant'},
                    {'name': 'kol', 'label': 'Kol.', 'field': 'Kol.'},
                ]
                ui.table(columns=_sum_cols, rows=_summary.to_dict('records')).classes('w-full')

        _hdr_df = service_packet.get('project_header')
        if _hdr_df is not None and not _hdr_df.empty:
            with ui.card().classes('w-full mb-4 p-3'):
                ui.label('Podaci o projektu').classes('font-bold text-base mb-2')
                ui.table(
                    columns=[
                        {'name': 'polje', 'label': 'Polje', 'field': 'Polje'},
                        {'name': 'vrednost', 'label': 'Vrednost', 'field': 'Vrednost'},
                    ],
                    rows=_hdr_df.to_dict('records'),
                ).classes('w-full')

        _guide_df = service_packet.get('user_guide')
        if _guide_df is not None and not _guide_df.empty:
            with ui.card().classes('w-full mb-4 p-3 bg-blue-50'):
                ui.label('Kako ides redom').classes('font-bold text-base mb-2')
                ui.table(
                    columns=[
                        {'name': 'korak', 'label': 'Korak', 'field': 'Korak'},
                        {'name': 'sta', 'label': 'Sta radis', 'field': 'Sta radis'},
                        {'name': 'nap', 'label': 'Napomena', 'field': 'Napomena'},
                    ],
                    rows=_guide_df.to_dict('records'),
                ).classes('w-full')

        _svc_instr = service_packet.get('service_instructions')
        if _svc_instr is not None and not _svc_instr.empty:
            with ui.card().classes('w-full mb-4 p-3 bg-amber-50'):
                ui.label('Instrukcije za servis').classes('font-bold text-base mb-2')
                ui.table(
                    columns=[
                        {'name': 'rb', 'label': 'RB', 'field': 'RB'},
                        {'name': 'stavka', 'label': 'Stavka', 'field': 'Stavka'},
                        {'name': 'instr', 'label': 'Instrukcija', 'field': 'Instrukcija'},
                    ],
                    rows=_svc_instr.to_dict('records'),
                ).classes('w-full text-sm')

        with ui.row().classes('w-full gap-4 items-start mb-4'):
            _svc_cuts = service_packet.get('service_cuts')
            if _svc_cuts is not None and not _svc_cuts.empty:
                with ui.card().classes('flex-1 p-3'):
                    ui.label('Sta nosis u servis: secenje').classes('font-bold text-base mb-2')
                    ui.table(
                        columns=[
                            {'name': 'rb', 'label': 'RB', 'field': 'RB'},
                            {'name': 'zid', 'label': 'Zid', 'field': 'Zid'},
                            {'name': 'mat', 'label': 'Materijal', 'field': 'Materijal'},
                            {'name': 'deb', 'label': 'Deb.', 'field': 'Deb.'},
                            {'name': 'cw', 'label': 'CUT Duzina', 'field': 'CUT_W [mm]'},
                            {'name': 'ch', 'label': 'CUT Sirina', 'field': 'CUT_H [mm]'},
                            {'name': 'kant', 'label': 'Kant', 'field': 'Kant'},
                            {'name': 'kol', 'label': 'Kol.', 'field': 'Kol.'},
                        ],
                        rows=_svc_cuts.to_dict('records'),
                    ).classes('w-full text-sm')
            _shop_df = service_packet.get('shopping_list')
            if _shop_df is not None and not _shop_df.empty:
                with ui.card().classes('flex-1 p-3'):
                    ui.label('Sta kupujes posebno').classes('font-bold text-base mb-2')
                    ui.table(
                        columns=[
                            {'name': 'grupa', 'label': 'Grupa', 'field': 'Grupa'},
                            {'name': 'naziv', 'label': 'Naziv', 'field': 'Naziv'},
                            {'name': 'sifra', 'label': 'Tip / Šifra', 'field': 'Tip / Šifra'},
                            {'name': 'kol', 'label': 'Kol.', 'field': 'Kol.'},
                            {'name': 'nap', 'label': 'Napomena', 'field': 'Napomena'},
                        ],
                        rows=_shop_df.to_dict('records'),
                    ).classes('w-full text-sm')

        _ready_df = service_packet.get('ready_made_items')
        if _ready_df is not None and not _ready_df.empty:
            with ui.expansion('Gotovi proizvodi - ne ulaze u secenje', icon='shopping_bag').classes('w-full mb-2 border rounded'):
                ui.table(
                    columns=[
                        {'name': 'grupa', 'label': 'Grupa', 'field': 'Grupa'},
                        {'name': 'naziv', 'label': 'Naziv', 'field': 'Naziv'},
                        {'name': 'sifra', 'label': 'Tip / Šifra', 'field': 'Tip / Šifra'},
                        {'name': 'kol', 'label': 'Kol.', 'field': 'Kol.'},
                        {'name': 'nap', 'label': 'Napomena', 'field': 'Napomena'},
                    ],
                    rows=_ready_df.to_dict('records'),
                ).classes('w-full text-sm')

        _svc_edge = service_packet.get('service_edge')
        if _svc_edge is not None and not _svc_edge.empty:
            with ui.expansion('Sta nosis u servis: kantovanje', icon='content_cut').classes('w-full mb-2 border rounded'):
                ui.table(
                    columns=[
                        {'name': 'part', 'label': 'PartCode', 'field': 'PartCode'},
                        {'name': 'zid', 'label': 'Zid', 'field': 'Zid'},
                        {'name': 'modul', 'label': 'Modul', 'field': 'Modul'},
                        {'name': 'deo', 'label': 'Deo', 'field': 'Deo'},
                        {'name': 'kol', 'label': 'Kol.', 'field': 'Kol.'},
                        {'name': 'kant', 'label': 'Kant', 'field': 'Kant'},
                        {'name': 'nap', 'label': 'Napomena', 'field': 'Napomena'},
                    ],
                    rows=_svc_edge.to_dict('records'),
                ).classes('w-full text-sm')

        _svc_proc = service_packet.get('service_processing')
        if _svc_proc is not None and not _svc_proc.empty:
            with ui.expansion('Sta nosis u servis: obrada', icon='build').classes('w-full mb-2 border rounded'):
                ui.table(
                    columns=[
                        {'name': 'part', 'label': 'PartCode', 'field': 'PartCode'},
                        {'name': 'zid', 'label': 'Zid', 'field': 'Zid'},
                        {'name': 'modul', 'label': 'Modul', 'field': 'Modul'},
                        {'name': 'deo', 'label': 'Deo', 'field': 'Deo'},
                        {'name': 'tip', 'label': 'Tip obrade', 'field': 'Tip obrade'},
                        {'name': 'izvodi', 'label': 'Izvodi', 'field': 'Izvodi'},
                        {'name': 'osnov', 'label': 'Osnov izvođenja', 'field': 'Osnov izvođenja'},
                        {'name': 'kol', 'label': 'Kol.', 'field': 'Kol.'},
                        {'name': 'obr', 'label': 'Obrada / napomena', 'field': 'Obrada / napomena'},
                    ],
                    rows=_svc_proc.to_dict('records'),
                ).classes('w-full text-sm')

        with ui.row().classes('w-full gap-4 items-start mb-4'):
            _wcl = service_packet.get('workshop_checklist')
            if _wcl is not None and not _wcl.empty:
                with ui.card().classes('flex-1 p-3'):
                    ui.label('Checklist pre servisa').classes('font-bold text-base mb-2')
                    ui.table(
                        columns=[
                            {'name': 'rb', 'label': 'RB', 'field': 'RB'},
                            {'name': 'stavka', 'label': 'Stavka', 'field': 'Stavka'},
                            {'name': 'status', 'label': 'Status', 'field': 'Status'},
                        ],
                        rows=_wcl.to_dict('records'),
                    ).classes('w-full text-sm')
            _hcl = service_packet.get('home_checklist')
            if _hcl is not None and not _hcl.empty:
                with ui.card().classes('flex-1 p-3'):
                    ui.label('Checklist pre sklapanja').classes('font-bold text-base mb-2')
                    ui.table(
                        columns=[
                            {'name': 'rb', 'label': 'RB', 'field': 'RB'},
                            {'name': 'stavka', 'label': 'Stavka', 'field': 'Stavka'},
                            {'name': 'status', 'label': 'Status', 'field': 'Status'},
                        ],
                        rows=_hcl.to_dict('records'),
                    ).classes('w-full text-sm')

        _titles = {
            'carcass': 'Korpus (stranice, dno, plafon)',
            'backs': 'Leđne ploče',
            'fronts': 'Frontovi',
            'drawer_boxes': 'Sanduk fioke (iverica)',
            'worktop': 'Radna ploča i nosači',
            'plinth': 'Sokla / lajsna',
            'hardware': '🔩 Okovi (šarke, klizači, mehanizmi)',
        }
        _sec_cols = [
            {'name': 'part', 'label': 'PartCode', 'field': 'PartCode'},
            {'name': 'zid', 'label': 'Zid', 'field': 'Zid'},
            {'name': 'modul', 'label': 'Modul', 'field': 'Modul'},
            {'name': 'deo', 'label': 'Deo', 'field': 'Deo'},
            {'name': 'poz', 'label': 'Pozicija', 'field': 'Pozicija'},
            {'name': 'korak', 'label': 'Korak', 'field': 'SklopKorak'},
            {'name': 'cw', 'label': 'Dužina [mm]', 'field': 'CUT_W [mm]'},
            {'name': 'ch', 'label': 'Širina [mm]', 'field': 'CUT_H [mm]'},
            {'name': 'deb', 'label': 'Deb.', 'field': 'Deb.'},
            {'name': 'kol', 'label': 'Kol.', 'field': 'Kol.'},
            {'name': 'kant', 'label': 'Kant', 'field': 'Kant'},
            {'name': 'nap', 'label': 'Napomena', 'field': 'Napomena'},
        ]
        _hw_cols = [
            {'name': 'part', 'label': 'PartCode', 'field': 'PartCode'},
            {'name': 'zid', 'label': 'Zid', 'field': 'Zid'},
            {'name': 'modul', 'label': 'Modul', 'field': 'Modul'},
            {'name': 'kat', 'label': 'Kategorija', 'field': 'Kategorija'},
            {'name': 'naziv', 'label': 'Naziv', 'field': 'Naziv'},
            {'name': 'sifra', 'label': 'Tip / Šifra', 'field': 'Tip / Šifra'},
            {'name': 'korak', 'label': 'Korak', 'field': 'SklopKorak'},
            {'name': 'kol', 'label': 'Kol.', 'field': 'Kol.'},
            {'name': 'nap', 'label': 'Napomena', 'field': 'Napomena'},
        ]
        for _sk, _df in sections.items():
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
        ui.label(CUTLIST_BY_ELEMENT).classes('text-xl font-bold mb-3')
        _elem_cols = [
            {'name': 'part', 'label': 'PartCode', 'field': 'PartCode'},
            {'name': 'deo', 'label': 'Deo', 'field': 'Deo'},
            {'name': 'poz', 'label': 'Pozicija', 'field': 'Pozicija'},
            {'name': 'korak', 'label': 'Korak', 'field': 'SklopKorak'},
            {'name': 'cw', 'label': 'Dužina [mm]', 'field': 'CUT_W [mm]'},
            {'name': 'ch', 'label': 'Širina [mm]', 'field': 'CUT_H [mm]'},
            {'name': 'deb', 'label': 'Deb.', 'field': 'Deb.'},
            {'name': 'kol', 'label': 'Kol.', 'field': 'Kol.'},
            {'name': 'kant', 'label': 'Kant', 'field': 'Kant'},
        ]
        _combined_e = pd.concat(all_dfs, ignore_index=True) if all_dfs else None

        for _m in mods:
            _mid = int(_m.get('id', 0))
            _mlbl = str(_m.get('label', ''))
            _mzone = str(_m.get('zone', 'base')).lower()
            _mw = int(_m.get('w_mm', 0))
            _mh = int(_m.get('h_mm', 0))
            _md = int(_m.get('d_mm', 0))
            _mtid = str(_m.get('template_id', ''))

            _hdr = f'#{_mid} - {_mlbl}  ({_mw}x{_mh}x{_md} mm)'
            with ui.expansion(_hdr, icon='view_in_ar').classes('w-full mb-3 border border-gray-200 rounded'):
                _mparts = None
                if _combined_e is not None:
                    _mparts = _combined_e[_combined_e['ID'] == _mid]
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
                                    ui.label(CUTLIST_PREVIEW_2D).classes('text-[10px] text-gray-400 font-semibold')
                                    ui.image(_uri_2d).style(
                                        'width:110px; height:auto; border:1px solid #ddd; border-radius:4px;'
                                    )
                                    ui.label('Oznake na slici koriste skraćeni deo stvarnog PartCode-a, npr. M01-F02 -> F02.').classes('text-[10px] text-amber-700')
                                with ui.column().classes('items-center gap-0.5'):
                                    ui.label(CUTLIST_PREVIEW_3D).classes('text-[10px] text-gray-400 font-semibold')
                                    ui.image(_uri_3d).style(
                                        'width:140px; height:auto; border:1px solid #ddd; border-radius:4px;'
                                    )
                        except Exception as ex:
                            _LOG.debug('Cutlist tab: fallback to SVG preview for template %s: %s', _mtid, ex)
                            ui.html(svg_for_tid(_mtid)).classes('w-32 h-32')

                    with ui.column().classes('flex-1 gap-2'):
                        if _mparts is not None and not _mparts.empty:
                            _map_df = _mparts[['PartCode', 'Deo', 'Pozicija', 'SklopKorak', 'Kol.']].copy()
                            _map_df['Deo'] = _map_df['Deo'].map(_friendly_part_name)
                            _map_df['Pozicija'] = _map_df['Pozicija'].map(_friendly_position_name)
                            _map_df = _map_df.sort_values(['SklopKorak', 'PartCode']).reset_index(drop=True)
                            ui.label('Mapa delova za sklapanje').classes('text-sm font-semibold text-gray-700')
                            ui.table(
                                columns=[
                                    {'name': 'part', 'label': 'PartCode', 'field': 'PartCode'},
                                    {'name': 'deo', 'label': 'Deo', 'field': 'Deo'},
                                    {'name': 'poz', 'label': 'Gde ide', 'field': 'Pozicija'},
                                    {'name': 'korak', 'label': 'Korak', 'field': 'SklopKorak'},
                                    {'name': 'kol', 'label': 'Kom.', 'field': 'Kol.'},
                                ],
                                rows=_map_df.to_dict('records'),
                            ).classes('w-full text-xs')
                            ui.label('Napomena: oznake na slici su skraćene iz stvarnog PartCode-a, pa se direktno poklapaju sa tabelom i koracima sklapanja.').classes('text-[11px] text-gray-600')
                            ui.label(CUTLIST_SECTION_CUTS).classes('text-sm font-semibold text-gray-700')
                            _cuts_df = _mparts.copy()
                            _cuts_df['Deo'] = _cuts_df['Deo'].map(_friendly_part_name)
                            _cuts_df['Pozicija'] = _cuts_df['Pozicija'].map(_friendly_position_name)
                            ui.table(columns=_elem_cols, rows=_cuts_df.to_dict('records')).classes('w-full text-xs')

                        ui.label(CUTLIST_SECTION_ASSEMBLY).classes('text-sm font-semibold text-gray-700 mt-2')
                        if _mparts is not None and not _mparts.empty:
                            _needed_cols = {'PartCode', 'Deo', 'Pozicija', 'Kol.', 'SklopKorak'}
                            if _needed_cols.issubset(set(_mparts.columns)):
                                _asm = _mparts.copy()
                                _asm['_korak_sort'] = pd.to_numeric(_asm['SklopKorak'], errors='coerce').fillna(99).astype(int)
                                _asm = _asm.sort_values(['_korak_sort', 'PartCode']).reset_index(drop=True)
                                with ui.column().classes('gap-0.5 mb-1'):
                                    for _, _r in _asm.iterrows():
                                        _line = (
                                            f"Korak {_r.get('SklopKorak', '-')}: "
                                            f"{_r.get('PartCode', '')} | {_friendly_part_name(_r.get('Deo', ''))} | "
                                            f"{_friendly_position_name(_r.get('Pozicija', '-'))} | kom {_r.get('Kol.', 1)}"
                                        )
                                        ui.label(_line).classes('text-xs text-gray-700 leading-snug')

                        _steps = assembly_instructions(_mtid, _mzone, m=_m, kitchen=state.kitchen)
                        with ui.column().classes('gap-0.5'):
                            for _step in _steps:
                                ui.label(_step).classes('text-xs text-gray-600 leading-snug')
    except Exception as e:
        ui.label(CUTLIST_ERR_GENERIC_FMT.format(err=e)).classes('text-red-500')
