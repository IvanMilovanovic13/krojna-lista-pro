# -*- coding: utf-8 -*-
from __future__ import annotations

from io import BytesIO
import base64
import re


def _friendly_part_name(value) -> str:
    txt = str(value or "").strip()
    txt = re.sub(r"^[A-Z]\d+\s*[—-]\s*", "", txt)
    mapping = {
        "Leva strana": "Leva stranica korpusa",
        "Desna strana": "Desna stranica korpusa",
        "Dno": "Donja ploča korpusa",
        "Plafon": "Gornja ploča korpusa",
        "Vrata": "Front vrata",
        "Front fioke": "Front fioke",
        "Leđa": "Leđna ploča",
        "Ledja": "Leđna ploča",
    }
    mapping.update({
        "Front fioke (unif.)": "Front fioke",
        "Front fioke (kuhinjska jedinica)": "Front fioke ispod rerne",
        "Front fioke (ispod rerne)": "Front fioke ispod rerne",
        "Vrata (ispod sudopere)": "Front vrata ispod sudopere",
        "Vrata rerne": "Front za rernu",
        "Prednja strana sanduka": "Prednja strana sanduka fioke",
        "Zadnja strana sanduka": "Zadnja strana sanduka fioke",
        "Dno sanduka": "Dno sanduka fioke",
        "Bočna ploča": "Bočna stranica sanduka fioke",
        "Ledja / prolaz": "Ledjna ploca / prolaz",
    })
    return mapping.get(txt, txt)


def _friendly_position_name(value) -> str:
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

def build_pdf_bytes(
    kitchen: dict,
    *,
    build_cutlist_sections,
    wall_len_h,
    render_fn,
    pd,
    plt,
    render_element_preview,
    assembly_instructions,
    logger,
) -> bytes:
    from cutlist import build_service_packet
    """Generiše kompletan PDF krojna liste i vraća ga kao bytes."""
    import re, datetime
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
        Image as RLImage, PageBreak, HRFlowable, KeepTogether,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    # ── Helpers ────────────────────────────────────────────────────────────────
    import struct as _struct

    def _safe(text: str) -> str:
        """Ukloni Unicode znakove van Latin-1 opsega (emoji, ①-⑧ → cifre)."""
        _MAP = {'①':'1.','②':'2.','③':'3.','④':'4.',
                '⑤':'5.','⑥':'6.','⑦':'7.','⑧':'8.'}
        for k, v in _MAP.items():
            text = text.replace(k, v)
        return re.sub(r'[^\x00-\xFF]', '', text)

    def _rl_image(uri: str, width: float) -> RLImage:
        """Kreira RLImage iz base64 data URI sa tačnim odnosom visine i širine.

        ReportLab nekad ne skalira visinu automatski (samo siri na zadanu sirinu),
        pa visinu računamo sami iz pixel dimenzija PNG zaglavlja.
        """
        raw  = base64.b64decode(uri.split(',', 1)[1])
        pw   = _struct.unpack('>I', raw[16:20])[0]  # pixel width
        ph   = _struct.unpack('>I', raw[20:24])[0]  # pixel height
        h    = width * ph / max(pw, 1)
        return RLImage(BytesIO(raw), width=width, height=h)

    # ── Page geometry ──────────────────────────────────────────────────────────
    PDF_BUF = BytesIO()
    PW  = A4[0] - 30 * mm           # usable width  ≈ 165 mm
    DOC = SimpleDocTemplate(
        PDF_BUF, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm,
    )

    # ── Stilovi ────────────────────────────────────────────────────────────────
    SS  = getSampleStyleSheet()
    C_BLUE  = colors.HexColor('#1E3A5F')
    C_GREEN = colors.HexColor('#2D6A4F')
    C_HDR   = colors.HexColor('#1E3A5F')
    C_ODD   = colors.HexColor('#F0F4F8')

    ST  = ParagraphStyle('KL_T',  parent=SS['Title'],   fontSize=20, spaceAfter=3*mm)
    H1  = ParagraphStyle('KL_H1', parent=SS['Heading1'],fontSize=13, spaceBefore=6*mm, spaceAfter=2*mm, textColor=C_BLUE)
    H2  = ParagraphStyle('KL_H2', parent=SS['Heading2'],fontSize=10, spaceBefore=4*mm, spaceAfter=1*mm, textColor=C_GREEN)
    NRM = ParagraphStyle('KL_N',  parent=SS['Normal'],  fontSize=8)
    SB  = ParagraphStyle('KL_SB', parent=SS['Normal'],  fontSize=8,  fontName='Helvetica-Bold')
    STP = ParagraphStyle('KL_ST', parent=SS['Normal'],  fontSize=7,  leading=10)

    def _tbl_style():
        return TableStyle([
            ('BACKGROUND',    (0, 0), (-1,  0), C_HDR),
            ('TEXTCOLOR',     (0, 0), (-1,  0), colors.white),
            ('FONTNAME',      (0, 0), (-1,  0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1,  0), 7),
            ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE',      (0, 1), (-1, -1), 7),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.white, C_ODD]),
            ('GRID',          (0, 0), (-1, -1), 0.3, colors.grey),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING',    (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING',   (0, 0), (-1, -1), 3),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 3),
        ])

    story = []

    # ── 1. Naslov ──────────────────────────────────────────────────────────────
    story.append(Paragraph('Krojna Lista', ST))
    wl_k  = kitchen.get('wall', {}).get('length_mm', 0)
    wh_k  = kitchen.get('wall', {}).get('height_mm', 0)
    today = datetime.date.today().strftime('%d.%m.%Y')
    story.append(Paragraph(_safe(f'Datum: {today}  |  Zid: {wl_k} x {wh_k} mm'), NRM))
    story.append(Spacer(1, 4*mm))

    # ── 2. Slika kuhinje ───────────────────────────────────────────────────────
    try:
        _wl_v, _wh_v = wall_len_h(kitchen)
        _sc_v  = 5.0 / max(_wh_v + 280, 1)
        _fw_v  = max((_wl_v + 260) * _sc_v, 5.0 * 1.65)
        _fig_k = plt.figure(figsize=(_fw_v, 5.0))
        _ax_k  = _fig_k.add_subplot(111)
        render_fn(ax=_ax_k, kitchen=kitchen, view_mode='Tehnicki',
                show_grid=False, grid_mm=10, show_bounds=True,
                kickboard=True, ceiling_filler=False)
        _fig_k.tight_layout(pad=0.3)
        _kbuf  = BytesIO()
        _fig_k.savefig(_kbuf, format='png', dpi=150)
        plt.close(_fig_k)
        _kbuf.seek(0)
        _ratio = 5.0 / _fw_v
        story.append(RLImage(_kbuf, width=PW, height=PW * _ratio))
    except Exception as _ek:
        story.append(Paragraph(_safe(f'Slika nije dostupna: {_ek}'), NRM))
    story.append(Spacer(1, 5*mm))

    # ── 3. Sumarni pregled ─────────────────────────────────────────────────────
    sections = build_cutlist_sections(kitchen)
    service_packet = build_service_packet(kitchen, sections)
    mods     = kitchen.get('modules', []) or []
    all_dfs  = [df for df in sections.values() if df is not None and not df.empty]

    if all_dfs:
        story.append(Paragraph('Sumarni pregled — svi rezovi', H1))
        _comb = pd.concat(all_dfs, ignore_index=True)
        _summ = (
            _comb
            .groupby(['Materijal', 'Deb.', 'CUT_W [mm]', 'CUT_H [mm]', 'Kant'], as_index=False)
            .agg({'Kol.': 'sum'})
            .sort_values(['Materijal', 'CUT_W [mm]', 'CUT_H [mm]'])
        )
        _sh = [['Materijal', 'Deb.', 'Dužina [mm]', 'Širina [mm]', 'Kant', 'Kol.']]
        _sr = [
            [_safe(str(r['Materijal'])), str(r['Deb.']),
             str(r['CUT_W [mm]']), str(r['CUT_H [mm]']),
             _safe(str(r['Kant'])), str(int(r['Kol.']))]
            for _, r in _summ.iterrows()
        ]
        _st = Table(_sh + _sr,
                    colWidths=[PW*0.28, PW*0.08, PW*0.14, PW*0.14, PW*0.26, PW*0.10],
                    repeatRows=1)
        _st.setStyle(_tbl_style())
        story.append(_st)
        story.append(Spacer(1, 4*mm))

    _hdr_df = service_packet.get("project_header", pd.DataFrame())
    if _hdr_df is not None and not _hdr_df.empty:
        story.append(Paragraph('Podaci o projektu', H1))
        _hd = [['Polje', 'Vrednost']]
        _hd += [[_safe(str(r.get('Polje', ''))), _safe(str(r.get('Vrednost', '')))] for r in _hdr_df.to_dict('records')]
        _ht = Table(_hd, colWidths=[PW * 0.22, PW * 0.78], repeatRows=1)
        _ht.setStyle(_tbl_style())
        story.append(_ht)
        story.append(Spacer(1, 4*mm))

    _svc_cuts = service_packet.get("service_cuts", pd.DataFrame())
    if _svc_cuts is not None and not _svc_cuts.empty:
        story.append(Paragraph('Sta nosis u servis - secenje', H1))
        _sh = [['RB', 'Zid', 'Materijal', 'Deb.', 'CUT Duz.', 'CUT Sir.', 'Kant', 'Kol.']]
        _sr = [[
            str(r.get('RB', '')),
            _safe(str(r.get('Zid', ''))),
            _safe(str(r.get('Materijal', ''))),
            str(r.get('Deb.', '')),
            str(r.get('CUT_W [mm]', '')),
            str(r.get('CUT_H [mm]', '')),
            _safe(str(r.get('Kant', ''))),
            str(r.get('Kol.', '')),
        ] for r in _svc_cuts.to_dict('records')]
        _st = Table(_sh + _sr,
                    colWidths=[PW*0.05, PW*0.09, PW*0.17, PW*0.07, PW*0.11, PW*0.11, PW*0.24, PW*0.08],
                    repeatRows=1)
        _st.setStyle(_tbl_style())
        story.append(_st)
        story.append(Spacer(1, 3*mm))

    _svc_edge = service_packet.get("service_edge", pd.DataFrame())
    if _svc_edge is not None and not _svc_edge.empty:
        story.append(Paragraph('Sta nosis u servis - kantovanje', H1))
        _eh = [['PartCode', 'Zid', 'Modul', 'Deo', 'Kol.', 'Kant', 'Napomena']]
        _er = [[
            _safe(str(r.get('PartCode', ''))),
            _safe(str(r.get('Zid', ''))),
            _safe(str(r.get('Modul', ''))),
            _safe(str(r.get('Deo', ''))),
            str(r.get('Kol.', '')),
            _safe(str(r.get('Kant', ''))),
            _safe(str(r.get('Napomena', ''))),
        ] for r in _svc_edge.to_dict('records')]
        _et = Table(_eh + _er,
                    colWidths=[PW*0.10, PW*0.08, PW*0.16, PW*0.15, PW*0.06, PW*0.18, PW*0.27],
                    repeatRows=1)
        _et.setStyle(_tbl_style())
        story.append(_et)
        story.append(Spacer(1, 3*mm))

    _svc_proc = service_packet.get("service_processing", pd.DataFrame())
    if _svc_proc is not None and not _svc_proc.empty:
        story.append(Paragraph('Sta nosis u servis - obrada', H1))
        _ph = [['PartCode', 'Modul', 'Deo', 'Tip obrade', 'Izvodi', 'Osnov izvođenja', 'Kol.', 'Obrada / napomena']]
        _pr = [[
            _safe(str(r.get('PartCode', ''))),
            _safe(str(r.get('Modul', ''))),
            _safe(str(r.get('Deo', ''))),
            _safe(str(r.get('Tip obrade', ''))),
            _safe(str(r.get('Izvodi', ''))),
            _safe(str(r.get('Osnov izvođenja', ''))),
            str(r.get('Kol.', '')),
            _safe(str(r.get('Obrada / napomena', ''))),
        ] for r in _svc_proc.to_dict('records')]
        _pt = Table(_ph + _pr,
                    colWidths=[PW*0.07, PW*0.11, PW*0.10, PW*0.12, PW*0.10, PW*0.16, PW*0.05, PW*0.29],
                    repeatRows=1)
        _pt.setStyle(_tbl_style())
        story.append(_pt)
        story.append(Spacer(1, 4*mm))

    _svc_instr = service_packet.get("service_instructions", pd.DataFrame())
    if _svc_instr is not None and not _svc_instr.empty:
        story.append(Paragraph('Instrukcije za servis', H1))
        _ih = [['RB', 'Stavka', 'Instrukcija']]
        _ir = [[
            str(r.get('RB', '')),
            _safe(str(r.get('Stavka', ''))),
            _safe(str(r.get('Instrukcija', ''))),
        ] for r in _svc_instr.to_dict('records')]
        _it = Table(_ih + _ir,
                    colWidths=[PW*0.06, PW*0.20, PW*0.74],
                    repeatRows=1)
        _it.setStyle(_tbl_style())
        story.append(_it)
        story.append(Spacer(1, 4*mm))

    # ── 4. Detalji po sekcijama ────────────────────────────────────────────────
    _SEC_TITLES = {
        'carcass': 'Korpus (stranice, dno, plafon)',
        'backs':   'Leđe ploče',
        'fronts':  'Frontovi',
        'worktop': 'Radna ploča i nosači',
        'plinth':  'Sokla / Lajsna',
    }
    for _sk, _df in sections.items():
        if _df is None or _df.empty:
            continue
        story.append(Paragraph(_SEC_TITLES.get(_sk, _sk.capitalize()), H1))
        _sdh = [['Modul', 'Deo', 'Duz.', 'Sir.', 'Deb.', 'Kol.', 'Kant', 'Napomena']]
        _sdr = [
            [_safe(str(r.get('Modul', ''))[:22]),
             _safe(str(r.get('Deo', ''))),
             str(r.get('CUT_W [mm]', '')), str(r.get('CUT_H [mm]', '')),
             str(r.get('Deb.', '')), str(int(r.get('Kol.', 0))),
             _safe(str(r.get('Kant', ''))), _safe(str(r.get('Napomena', '')))]
            for r in _df.to_dict('records')
        ]
        _sdt = Table(_sdh + _sdr,
                     colWidths=[PW*0.20, PW*0.13, PW*0.08, PW*0.08,
                                PW*0.06, PW*0.05, PW*0.20, PW*0.20],
                     repeatRows=1)
        _sdt.setStyle(_tbl_style())
        story.append(_sdt)
        story.append(Spacer(1, 3*mm))

    # ── 5. Po elementima ───────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph('Po elementima - detalji i montaža', H1))

    _comb_e  = pd.concat(all_dfs, ignore_index=True) if all_dfs else None
    # Column widths: left = images (2D stacked above 3D), right = cuts + instructions
    IMG_COL  = 50 * mm
    TBL_W    = PW - IMG_COL - 4 * mm   # ≈ 111 mm
    IMG_2D_W = 47 * mm                  # 2D portrait image width in PDF
    IMG_3D_W = 47 * mm                  # 3D landscape image width in PDF

    for _m in mods:
        _mid_e = int(_m.get('id', 0))
        _mlbl  = _safe(str(_m.get('label', '')))
        _mz    = str(_m.get('zone', 'base')).lower()
        _mw    = int(_m.get('w_mm', 0))
        _mh    = int(_m.get('h_mm', 0))
        _md    = int(_m.get('d_mm', 0))
        _mtid  = str(_m.get('template_id', ''))
        _mparts = _comb_e[_comb_e['ID'] == _mid_e] if _comb_e is not None else pd.DataFrame()

        # ── Generate 2D and 3D preview images for PDF ─────────────────────────
        _eimg_2d = None
        _eimg_3d = None
        try:
            _uri_2d, _uri_3d = render_element_preview(
                _m,
                kitchen,
                label_mode="part_codes",
                part_rows=_mparts.to_dict('records') if _mparts is not None and not _mparts.empty else None,
            )
            # _rl_image() reads pixel dims from PNG header to compute correct height
            _eimg_2d = _rl_image(_uri_2d, IMG_2D_W)
            _eimg_3d = _rl_image(_uri_3d, IMG_3D_W)
        except Exception as ex:
            logger.debug("Element preview render failed for id=%s: %s", _mid_e, ex)

        # ── Tabela rezova ──────────────────────────────────────────────────────
        _ptbl = None
        _mtbl = None
        if _mparts is not None and not _mparts.empty:
                _map_parts = _mparts[["PartCode", "Deo", "Pozicija", "SklopKorak", "Kol."]].copy()
                _map_parts["Deo"] = _map_parts["Deo"].map(_friendly_part_name)
                _map_parts["Pozicija"] = _map_parts["Pozicija"].map(_friendly_position_name)
                _map_parts = _map_parts.sort_values(["SklopKorak", "PartCode"]).reset_index(drop=True)
                _mhdr = [['PartCode', 'Deo', 'Gde ide', 'Korak', 'Kom.']]
                _mrows = [[
                    _safe(str(r.get('PartCode', ''))),
                    _safe(str(r.get('Deo', ''))),
                    _safe(str(r.get('Pozicija', ''))),
                    str(r.get('SklopKorak', '')),
                    str(r.get('Kol.', '')),
                ] for r in _map_parts.to_dict('records')]
                _mtbl = Table(
                    _mhdr + _mrows,
                    colWidths=[TBL_W*0.16, TBL_W*0.28, TBL_W*0.24, TBL_W*0.10, TBL_W*0.10],
                    repeatRows=1,
                )
                _mtbl.setStyle(_tbl_style())
                _ph = [['Deo', 'Duz.', 'Sir.', 'Deb.', 'Kol.', 'Kant']]
                _pr = [
                    [_safe(_friendly_part_name(r.get('Deo', ''))),
                     str(r.get('CUT_W [mm]', '')), str(r.get('CUT_H [mm]', '')),
                     str(r.get('Deb.', '')), str(int(r.get('Kol.', 0))),
                     _safe(str(r.get('Kant', '')))]
                    for r in _mparts.to_dict('records')
                ]
                _ptbl = Table(
                    _ph + _pr,
                    colWidths=[TBL_W*0.28, TBL_W*0.13, TBL_W*0.13,
                               TBL_W*0.10, TBL_W*0.08, TBL_W*0.28],
                    repeatRows=1,
                )
                _ptbl.setStyle(_tbl_style())

        # ── Uputstvo za montažu ────────────────────────────────────────────────
        _steps = assembly_instructions(_mtid, _mz, m=_m, kitchen=kitchen)
        _step_paras = [Paragraph(_safe(s), STP) for s in _steps]

        # ── Desna kolona: rezovi + uputstvo ────────────────────────────────────
        _right: list = []
        if _mtbl:
            _right.append(Paragraph('Mapa delova za sklapanje', SB))
            _right.append(_mtbl)
            _right.append(Paragraph('Oznake na 2D slici koriste skraćeni deo stvarnog PartCode-a, pa se direktno poklapaju sa tabelom i koracima sklapanja.', STP))
            _right.append(Spacer(1, 2*mm))
        if _ptbl:
            _right.append(Paragraph('Rezovi', SB))
            _right.append(_ptbl)
            _right.append(Spacer(1, 2*mm))
        _right.append(Paragraph('Uputstvo za montažu', SB))
        _right.extend(_step_paras)

        # ── Leva kolona: 2D iznad, 3D ispod — nested Table ────────────────────
        # ReportLab ne podrzava listu flowable-a direktno u celiji Table-a;
        # koristimo nested Table (1 kolona, vise redova) da slazemo slike.
        _img_nested_rows = []
        if _eimg_2d:
            _img_nested_rows.append([Paragraph('2D', STP)])
            _img_nested_rows.append([_eimg_2d])
            _img_nested_rows.append([Paragraph('Oznake: F = front, P = panel', STP)])
            _img_nested_rows.append([Spacer(1, 2 * mm)])
        if _eimg_3d:
            _img_nested_rows.append([Paragraph('3D', STP)])
            _img_nested_rows.append([_eimg_3d])

        _img_cell = None
        if _img_nested_rows:
            _inner_tbl = Table(
                _img_nested_rows,
                colWidths=[IMG_COL - 2 * mm],
            )
            _inner_tbl.setStyle(TableStyle([
                ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING',    (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                ('LEFTPADDING',   (0, 0), (-1, -1), 0),
                ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
            ]))
            _img_cell = _inner_tbl

        # ── Složeni red: [slike | desna kolona] ───────────────────────────────
        _hdr_para = Paragraph(f'#{_mid_e}  {_mlbl}  •  {_mw}x{_mh}x{_md} mm', H2)
        _hr_line  = HRFlowable(width='100%', thickness=0.5, color=C_GREEN)

        if _img_cell is not None:
            _layout = Table(
                [[_img_cell, _right]],
                colWidths=[IMG_COL, TBL_W],
            )
            _layout.setStyle(TableStyle([
                ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING',   (0, 0), (-1, -1), 2),
                ('RIGHTPADDING',  (0, 0), (-1, -1), 2),
                ('TOPPADDING',    (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            _block = [_hdr_para, _hr_line, Spacer(1, 2*mm), _layout, Spacer(1, 4*mm)]
        else:
            _block = [_hdr_para, _hr_line, Spacer(1, 2*mm)] + _right + [Spacer(1, 4*mm)]

        try:
            story.append(KeepTogether(_block))
        except Exception as ex:
            logger.debug("PDF KeepTogether fallback triggered for module id=%s: %s", _mid_e, ex)
            story.extend(_block)

    _shop_df = service_packet.get("shopping_list", pd.DataFrame())
    if _shop_df is not None and not _shop_df.empty:
        story.append(PageBreak())
        story.append(Paragraph('Sta kupujes posebno', H1))
        _hh = [['Grupa', 'Naziv', 'Tip / Sifra', 'Kol.', 'Napomena']]
        _rr = [[
            _safe(str(r.get('Grupa', ''))),
            _safe(str(r.get('Naziv', ''))),
            _safe(str(r.get('Tip / Šifra', ''))),
            str(r.get('Kol.', '')),
            _safe(str(r.get('Napomena', ''))),
        ] for r in _shop_df.to_dict('records')]
        _tt = Table(_hh + _rr,
                    colWidths=[PW*0.18, PW*0.22, PW*0.20, PW*0.07, PW*0.33],
                    repeatRows=1)
        _tt.setStyle(_tbl_style())
        story.append(_tt)
        story.append(Spacer(1, 4*mm))

    _ready_df = service_packet.get("ready_made_items", pd.DataFrame())
    if _ready_df is not None and not _ready_df.empty:
        story.append(Paragraph('Gotovi proizvodi - ne ulaze u secenje', H1))
        _rh = [['Grupa', 'Naziv', 'Tip / Sifra', 'Kol.', 'Napomena']]
        _rr2 = [[
            _safe(str(r.get('Grupa', ''))),
            _safe(str(r.get('Naziv', ''))),
            _safe(str(r.get('Tip / Šifra', ''))),
            str(r.get('Kol.', '')),
            _safe(str(r.get('Napomena', ''))),
        ] for r in _ready_df.to_dict('records')]
        _rt = Table(_rh + _rr2,
                    colWidths=[PW*0.18, PW*0.22, PW*0.20, PW*0.07, PW*0.33],
                    repeatRows=1)
        _rt.setStyle(_tbl_style())
        story.append(_rt)
        story.append(Spacer(1, 4*mm))

    _guide_df = service_packet.get("user_guide", pd.DataFrame())
    if _guide_df is not None and not _guide_df.empty:
        story.append(Paragraph('Kako ides redom', H1))
        _gh = [['Korak', 'Sta radis', 'Napomena']]
        _gr = [[
            str(r.get('Korak', '')),
            _safe(str(r.get('Sta radis', ''))),
            _safe(str(r.get('Napomena', ''))),
        ] for r in _guide_df.to_dict('records')]
        _gt = Table(_gh + _gr,
                    colWidths=[PW*0.08, PW*0.30, PW*0.62],
                    repeatRows=1)
        _gt.setStyle(_tbl_style())
        story.append(_gt)
        story.append(Spacer(1, 4*mm))

    for _title, _key in (
        ('Checklist pre servisa', 'workshop_checklist'),
        ('Checklist pre kucnog sklapanja', 'home_checklist'),
    ):
        _cdf = service_packet.get(_key, pd.DataFrame())
        if _cdf is None or _cdf.empty:
            continue
        story.append(Paragraph(_title, H1))
        _ch = [['RB', 'Stavka', 'Status']]
        _cr = [[str(r.get('RB', '')), _safe(str(r.get('Stavka', ''))), _safe(str(r.get('Status', '')))] for r in _cdf.to_dict('records')]
        _ct = Table(_ch + _cr,
                    colWidths=[PW*0.06, PW*0.78, PW*0.16],
                    repeatRows=1)
        _ct.setStyle(_tbl_style())
        story.append(_ct)
        story.append(Spacer(1, 3*mm))

    # ── Build ──────────────────────────────────────────────────────────────────
    DOC.build(story)
    PDF_BUF.seek(0)
    return PDF_BUF.read()

