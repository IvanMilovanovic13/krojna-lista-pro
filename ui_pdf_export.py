# -*- coding: utf-8 -*-
from __future__ import annotations

from io import BytesIO
import base64
import re
from pathlib import Path
import math
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def _friendly_part_name(value, lang: str = "sr") -> str:
    txt = str(value or "").strip()
    txt = (
        txt.replace("LeÄ‘a", "Ledja")
        .replace("LeÃ„â€˜a", "Ledja")
        .replace("BoÄna ploÄa", "Bocna ploca")
        .replace("BoÃ„Âna ploÃ„Âa", "Bocna ploca")
        .replace("ploÄa", "ploca")
        .replace("ploÃ„Âa", "ploca")
    )
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
        "Ledja / prolaz": "Leđna ploča / prolaz",
    })
    mapping["Dno"] = "Donja ploča korpusa"
    mapping["LeÄ‘a"] = "Leđna ploča"
    mapping["Plafon"] = "Gornja ploča korpusa"
    mapping["LeÄ‘a"] = "Leđna ploča"
    mapping["Ledja"] = "Leđna ploča"
    mapping["BoÄna ploÄa"] = "Bočna stranica sanduka fioke"
    mapping["BoÄna ploÄa"] = "Bočna stranica sanduka fioke"
    if str(lang or "sr").lower().strip() == "en":
        mapping_en = {
            "Leva strana": "Left carcass side",
            "Desna strana": "Right carcass side",
            "Dno": "Bottom carcass panel",
            "LeÄ‘a": "Back panel",
            "Plafon": "Top carcass panel",
            "Vrata": "Door front",
            "Front fioke": "Drawer front",
            "LeÄ‘a": "Back panel",
            "Ledja": "Back panel",
            "Front fioke (unif.)": "Drawer front",
            "Front fioke (kuhinjska jedinica)": "Drawer front below oven",
            "Front fioke (ispod rerne)": "Drawer front below oven",
            "Vrata (ispod sudopere)": "Door front below sink",
            "Vrata rerne": "Oven front",
            "Prednja strana sanduka": "Drawer box front",
            "Zadnja strana sanduka": "Drawer box back",
            "Dno sanduka": "Drawer box bottom",
            "BoÄna ploÄa": "Drawer box side",
            "BoÄna ploÄa": "Drawer box side",
            "Ledja / prolaz": "Back panel / opening",
        }
        mapping_en["Leva stranica korpusa"] = "Left carcass side"
        mapping_en["Desna stranica korpusa"] = "Right carcass side"
        mapping_en["Donja ploča korpusa"] = "Bottom carcass panel"
        mapping_en["Gornja ploča korpusa"] = "Top carcass panel"
        mapping_en["Front vrata"] = "Door front"
        mapping_en["Front vrata ispod sudopere"] = "Door front below sink"
        mapping_en["Front za rernu"] = "Oven front"
        mapping_en["Prednja strana sanduka fioke"] = "Drawer box front"
        mapping_en["Zadnja strana sanduka fioke"] = "Drawer box back"
        mapping_en["Dno sanduka fioke"] = "Drawer box bottom"
        mapping_en["Bočna stranica sanduka fioke"] = "Drawer box side"
        mapping_en["Leđna ploča"] = "Back panel"
        mapping_en["Leđna ploča / prolaz"] = "Back panel / opening"
        return mapping_en.get(txt, txt)
    mapping.update({
        "Left carcass side": "Leva stranica korpusa",
        "Right carcass side": "Desna stranica korpusa",
        "Bottom carcass panel": "Donja ploča korpusa",
        "Top carcass panel": "Gornja ploča korpusa",
        "Door front": "Front vrata",
        "Drawer front": "Front fioke",
        "Back panel": "Leđna ploča",
        "Door front below sink": "Front vrata ispod sudopere",
        "Oven front": "Front za rernu",
        "Drawer box front": "Prednja strana sanduka fioke",
        "Drawer box back": "Zadnja strana sanduka fioke",
        "Drawer box bottom": "Dno sanduka fioke",
        "Drawer box side": "Bočna stranica sanduka fioke",
        "Back panel / opening": "Leđna ploča / prolaz",
    })
    return mapping.get(txt, txt)


def _friendly_position_name(value, lang: str = "sr") -> str:
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
    if str(lang or "sr").lower().strip() == "en":
        mapping_en = {
            "LEVO": "Left",
            "DESNO": "Right",
            "GORE": "Top",
            "DOLE": "Bottom",
            "CENTAR": "Center",
            "NAPRED": "Front",
            "POZADI": "Back",
        }
        return mapping_en.get(txt.upper(), txt)
    mapping.update({
        "Left": "Levo",
        "Right": "Desno",
        "Top": "Gore",
        "Bottom": "Dole",
        "Center": "Sredina",
        "Front": "Napred",
        "Back": "Pozadi",
    })
    return mapping.get(txt.upper(), txt)


def _short_part_code(value: str) -> str:
    txt = str(value or "").strip()
    m = re.search(r'([A-Z]\d{2})$', txt)
    return m.group(1) if m else txt


_LABEL_NORMALIZATION = {
    # Ispravni oblici — ostaju nepromenjeni
    "Le\u0111a": "Le\u0111a",
    "Le\u0111na plo\u010da": "Le\u0111na plo\u010da",
    "Le\u0111na plo\u010da / prolaz": "Le\u0111na plo\u010da / prolaz",
    "Bo\u010dna plo\u010da": "Bo\u010dna plo\u010da",
    "Bo\u010dna stranica sanduka fioke": "Bo\u010dna stranica sanduka fioke",
    "Zavr\u0161na bo\u010dna plo\u010da": "Zavr\u0161na bo\u010dna plo\u010da",
    "plo\u010da": "plo\u010da",
    # Mojibake varijante → ispravni srpski
    "Le\u00c4\u2018a": "Le\u0111a",
    "Le\u00c3\u201e\u20ac\u02dca": "Le\u0111a",
    "Le\u00c3\u0192\u00e2\u20ac\u017e\u00c3\u00a2\u00e2\u201a\u00ac\u00cb\u0153a": "Le\u0111a",
    "Bo\u00c4\u008dna plo\u00c4\u008da": "Bo\u010dna plo\u010da",
    "Bo\u00c3\u201e\u00c2\u008dna plo\u00c3\u201e\u00c2\u008da": "Bo\u010dna plo\u010da",
    "Bo\u00c3\u0192\u00e2\u20ac\u017e\u00c3\u201a\u00c2\u008dna plo\u00c3\u0192\u00e2\u20ac\u017e\u00c3\u201a\u00c2\u008da": "Bo\u010dna plo\u010da",
    "plo\u00c4\u008da": "plo\u010da",
    "plo\u00c3\u201e\u00c2\u008da": "plo\u010da",
    "plo\u00c3\u0192\u00e2\u20ac\u017e\u00c3\u201a\u00c2\u008da": "plo\u010da",
}


def _normalize_label_text(value) -> str:
    txt = str(value or "").strip()
    for src, dst in _LABEL_NORMALIZATION.items():
        txt = txt.replace(src, dst)
    return re.sub(r"\s+", " ", txt).strip()


def _friendly_part_name(value, lang: str = "sr") -> str:
    txt = _normalize_label_text(value)
    txt = re.sub(r"^[A-Z]\d+\s*[\u2014-]\s*", "", txt)
    mapping_sr = {
        "Leva strana": "Leva stranica korpusa",
        "Desna strana": "Desna stranica korpusa",
        "Dno": "Donja plo\u010da korpusa",
        "Plafon": "Gornja plo\u010da korpusa",
        "Vrata": "Front vrata",
        "Front fioke": "Front fioke",
        "Front fioke (unif.)": "Front fioke",
        "Front fioke (kuhinjska jedinica)": "Front fioke ispod rerne",
        "Front fioke (ispod rerne)": "Front fioke ispod rerne",
        "Vrata (ispod sudopere)": "Front vrata ispod sudopere",
        "Vrata rerne": "Front za rernu",
        "Prednja strana sanduka": "Prednja strana sanduka fioke",
        "Zadnja strana sanduka": "Zadnja strana sanduka fioke",
        "Dno sanduka": "Dno sanduka fioke",
        "Bo\u010dna plo\u010da": "Bo\u010dna stranica sanduka fioke",
        "Bocna ploca": "Bo\u010dna stranica sanduka fioke",
        "Le\u0111a": "Le\u0111na plo\u010da",
        "Ledja": "Le\u0111na plo\u010da",
        "Le\u0111a / prolaz": "Le\u0111na plo\u010da / prolaz",
        "Ledja / prolaz": "Le\u0111na plo\u010da / prolaz",
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
        "Vrata (ispod sudopere)": "Door front below sink",
        "Vrata rerne": "Oven front",
        "Prednja strana sanduka": "Drawer box front",
        "Zadnja strana sanduka": "Drawer box back",
        "Dno sanduka": "Drawer box bottom",
        "Bo\u010dna plo\u010da": "Drawer box side",
        "Bocna ploca": "Drawer box side",
        "Le\u0111a": "Back panel",
        "Ledja": "Back panel",
        "Le\u0111a / prolaz": "Back panel / opening",
        "Ledja / prolaz": "Back panel / opening",
    }
    mapping_sr.update({str(v): str(k) for k, v in mapping_en.items()})
    mapping = mapping_en if str(lang or "sr").lower().strip() == "en" else mapping_sr
    return mapping.get(txt, txt)


def _kant_legend(lang: str = "sr") -> str:
    if str(lang or "sr").lower().strip() == "en":
        return "Edge legend: T = top edge, B = bottom edge, L = left edge, R = right edge, F = front edge."
    return "Legenda kanta: T = gornja ivica, B = donja ivica, L = leva ivica, R = desna ivica, F = prednja ivica."


def _format_material_role_pdf(material: str, role: str, lang: str = "sr") -> str:
    mat = str(material or "").strip()
    if not mat:
        return ""
    if str(lang or "sr").lower().strip() == "en":
        role_map = {
            "carcass": "Carcass",
            "front": "Front",
            "back": "Back",
            "drawer_box": "Drawer box",
            "worktop": "Worktop",
            "plinth": "Plinth",
        }
    else:
        role_map = {
            "carcass": "Korpus",
            "front": "Front",
            "back": "Leđa",
            "drawer_box": "Sanduk fioke",
            "worktop": "Radna ploča",
            "plinth": "Sokla",
        }
    role_label = role_map.get(str(role or "").strip().lower(), "")
    return f"{mat} {role_label}".strip() if role_label else mat


def _summary_material_label(section_key: str, material: str, lang: str = "sr") -> str:
    skey = str(section_key or "").strip().lower()
    role = {
        "carcass": "carcass",
        "fronts": "front",
        "backs": "back",
        "drawer_boxes": "drawer_box",
        "worktop": "worktop",
        "plinth": "plinth",
    }.get(skey, "carcass")
    return _format_material_role_pdf(material, role, lang=lang)


def _part_role_note(part_name: str, material: str, thickness: str, lang: str = "sr") -> str:
    part = str(part_name or "").lower()
    mat = str(material or "").upper()
    thk = str(thickness or "").strip()
    if "leđ" in part or "ledj" in part or "back panel" in part:
        if mat.startswith("MDF"):
            return "Tanja zadnja ploča elementa." if lang == "sr" else "Thin back panel of the unit."
        if mat.startswith("HDF") or "LESONIT" in mat:
            return "Zadnja ploča elementa." if lang == "sr" else "Back panel of the unit."
    if "front" in part or "vrata" in part:
        if mat.startswith("MDF"):
            return f"MDF front {thk} mm." if lang == "sr" else f"MDF front {thk} mm."
    return ""


def _format_material_role_pdf(material: str, role: str, lang: str = "sr") -> str:
    mat = str(material or "").strip()
    if not mat:
        return ""
    if str(lang or "sr").lower().strip() == "en":
        role_map = {
            "carcass": "Carcass",
            "front": "Front",
            "back": "Back",
            "drawer_box": "Drawer box",
            "worktop": "Worktop",
            "plinth": "Plinth",
        }
    else:
        role_map = {
            "carcass": "Korpus",
            "front": "Front",
            "back": "Le\u0111a",
            "drawer_box": "Sanduk fioke",
            "worktop": "Radna plo\u010da",
            "plinth": "Sokla",
        }
    role_label = role_map.get(str(role or "").strip().lower(), "")
    return f"{mat} {role_label}".strip() if role_label else mat


def _part_role_note(part_name: str, material: str, thickness: str, lang: str = "sr") -> str:
    part = _normalize_label_text(part_name).lower()
    mat = str(material or "").upper()
    thk = str(thickness or "").strip()
    if "le\u0111" in part or "ledj" in part or "back panel" in part:
        if mat.startswith("MDF"):
            return "Tanja zadnja plo\u010da elementa." if lang == "sr" else "Thin back panel of the unit."
        if mat.startswith("HDF") or "LESONIT" in mat:
            return "Zadnja plo\u010da elementa." if lang == "sr" else "Back panel of the unit."
    if "front" in part or "vrata" in part:
        if mat.startswith("MDF"):
            return f"MDF front {thk} mm." if lang == "sr" else f"MDF front {thk} mm."
    return ""


def _module_tool_hardware_lines(tid: str, zone: str, lang: str = "sr") -> list[str]:
    _lang = str(lang or "sr").lower().strip()
    FONT_REGULAR, FONT_BOLD = _register_pdf_fonts()
    def _t(sr: str, en: str) -> str:
        return en if _lang == "en" else sr
    tid_u = str(tid or "").upper()
    lines = [
        _t("Aku-odvijač ili šrafciger", "Drill-driver or screwdriver"),
        _t("Metar", "Tape measure"),
        _t("Libela", "Spirit level"),
    ]
    if zone == "wall":
        lines.append(_t("Nosači za zid / kačenje", "Wall brackets / hanging hardware"))
    if "DOOR" in tid_u or "2DOOR" in tid_u or "1DOOR" in tid_u or "SINK" in tid_u:
        lines.append(_t("Šarke za vrata", "Door hinges"))
    if "DRAWER" in tid_u or "COOKING_UNIT" in tid_u or "TRASH" in tid_u:
        lines.append(_t("Klizači za fioku", "Drawer runners"))
    if "LIFTUP" in tid_u:
        lines.append(_t("Lift-up mehanizam", "Lift-up mechanism"))
    if "GLASS" in tid_u:
        lines.append(_t("Šarke za staklena vrata", "Glass-door hinges"))
    if tid_u == "BASE_DISHWASHER":
        lines.append(_t("Montažni set za front MZS", "Dishwasher front mounting kit"))
    if "WALL" in tid_u:
        lines.append(_t("Tipli / vijci za zid prema podlozi", "Wall plugs / screws according to wall type"))
    return lines


def _module_preassembly_lines(tid: str, zone: str, lang: str = "sr") -> list[str]:
    _lang = str(lang or "sr").lower().strip()
    def _t(sr: str, en: str) -> str:
        return en if _lang == "en" else sr
    tid_u = str(tid or "").upper()
    lines = [
        _t("Proveri da li broj delova odgovara tabeli.", "Check that the number of parts matches the table."),
        _t("Odvoji korpus, frontove, leđa i okov pre početka sklapanja.", "Separate carcass parts, fronts, backs and hardware before assembly."),
        _t("Pregledaj kantovane ivice da prednja strana elementa bude pravilno okrenuta.", "Check the edged sides so the front of the unit is oriented correctly."),
    ]
    if zone in ("wall", "wall_upper"):
        lines.append(_t("Pre bušenja proveri zid i odaberi odgovarajuće tiple i vijke.", "Before drilling, check the wall type and choose suitable plugs and screws."))
    if "DISHWASHER" in tid_u or "SINK" in tid_u or "HOB" in tid_u or "OVEN" in tid_u:
        lines.append(_t("Pre sklapanja proveri položaj instalacija i otvora za uređaj.", "Before assembly, verify the service positions and appliance opening."))
    if "TALL" in tid_u:
        lines.append(_t("Visoki element obavezno planiraj za pričvršćenje u zid.", "A tall unit must always be planned for wall fixing."))
    return lines

def _find_font_file(filename: str) -> str | None:
    here = Path(__file__).resolve().parent
    cwd = Path.cwd()
    for p in (here / "fonts" / filename, here / filename, cwd / "fonts" / filename, cwd / filename):
        if p.exists():
            return str(p)
    return None


def _register_pdf_fonts() -> tuple[str, str]:
    try:
        pdfmetrics.getFont("DejaVuSans")
        pdfmetrics.getFont("DejaVuSans-Bold")
        return "DejaVuSans", "DejaVuSans-Bold"
    except Exception:
        pass
    reg_file = _find_font_file("DejaVuSans.ttf")
    bold_file = _find_font_file("DejaVuSans-Bold.ttf")
    try:
        if reg_file:
            pdfmetrics.registerFont(TTFont("DejaVuSans", reg_file))
        if bold_file:
            pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", bold_file))
        if reg_file and bold_file:
            return "DejaVuSans", "DejaVuSans-Bold"
    except Exception:
        pass
    return "Helvetica", "Helvetica-Bold"


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
    lang: str = "sr",
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
    _lang = str(lang or "sr").lower().strip()

    def _t(sr: str, en: str) -> str:
        return en if _lang == "en" else sr

    # ── Helpers ────────────────────────────────────────────────────────────────
    import struct as _struct

    def _safe(text: str) -> str:
        """Ukloni Unicode znakove van Latin-1 opsega (emoji, ①-⑧ → cifre)."""
        _MAP = {'①':'1.','②':'2.','③':'3.','④':'4.',
                '⑤':'5.','⑥':'6.','⑦':'7.','⑧':'8.'}
        for k, v in _MAP.items():
            text = text.replace(k, v)
        return re.sub(r'[^\x00-\xFF]', '', text)

    def _normalize_pdf_text(text: str) -> str:
        txt = str(text or "")
        replacements = {
            "KORAK 1 - BOCNE PLOCE": "KORAK 1 - BOČNE PLOČE",
            "KORAK 2 - DNO I GORNJA PLOCA": "KORAK 2 - DNO I GORNJA PLOČA",
            "KORAK 2 - LEDJA I OTVORI": "KORAK 2 - LEĐA I OTVORI",
            "KORAK 3 - MONTAZA NA ZID": "KORAK 3 - MONTAŽA NA ZID",
            "KORAK 4 - RADNA PLOCA I SUDOPERA": "KORAK 4 - RADNA PLOČA I SUDOPERA",
            "KORAK 5 - ZAVRSNA PROVERA": "KORAK 5 - ZAVRŠNA PROVERA",
            "Ledjna ploča": "Leđna ploča",
            "Ledjna ploca": "Leđna ploča",
            "Sta radis": "Šta radiš",
            "bocne stranice": "bočne stranice",
            "bocnu stranicu": "bočnu stranicu",
            "gornju plocu": "gornju ploču",
            "izmedju bocnih": "između bočnih",
            "izmedju": "između",
            "Pre sledeceg koraka": "Pre sledećeg koraka",
            "busenjima": "bušenjima",
            "okaci vrata": "okači vrata",
            "Obelezi tacnu visinu": "Obeležite tačnu visinu",
            "nosac ili sinu": "nosač ili šinu",
            "Pre zavrsnog stezanja": "Pre završnog stezanja",
            "cvrsto vezan": "čvrsto vezan",
            "sledeci zidni": "sledeći zidni",
            "sledeci element": "sledeći element",
            "sledeci modul": "sledeći modul",
            "Sastavi bocne": "Sastavite bočne",
            "duzina": "dužina",
            "Zastita": "Zaštita",
            "iskljucivo": "isključivo",
            "pricvrscenje": "pričvršćenje",
            "nosace i": "nosače i",
            "nosace": "nosače",
            "nosaca": "nosača",
            "klizaca": "klizača",
            "busenje:": "bušenje:",
            "O35mm dubina": "Ø35mm dubina",
            "Zavrsno": "Završno",
            "ukljuceni": "uključeni",
            "montazna ploca": "montažna ploča",
            "radne ploce": "radne ploče",
            "ploce na nosace": "ploče na nosače",
            "vijak za rucku": "vijak za ručku",
            "po rucki": "po ručki",
            "sinu ili": "šinu ili",
            "za pricvrscenje": "za pričvršćenje",
            "Nosac radne ploce": "Nosač radne ploče",
        }
        for src, dst in replacements.items():
            txt = txt.replace(src, dst)
        return txt

    def _safe(text: str) -> str:
        return re.sub(r"[\x00-\x08\x0B-\x1F\x7F]", '', _normalize_pdf_text(text))

    def _safe_val(v: object, default: str = "-") -> str:
        if v is None:
            return default
        if isinstance(v, float) and math.isnan(v):
            return default
        txt = str(v).strip()
        if txt.lower() in {'', 'nan', 'none', 'null'}:
            return default
        return _safe(txt)

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

    ST  = ParagraphStyle('KL_T',  parent=SS['Title'],   fontSize=20, spaceAfter=3*mm, fontName=FONT_BOLD)
    H1  = ParagraphStyle('KL_H1', parent=SS['Heading1'],fontSize=13, spaceBefore=6*mm, spaceAfter=2*mm, textColor=C_BLUE, fontName=FONT_BOLD)
    H2  = ParagraphStyle('KL_H2', parent=SS['Heading2'],fontSize=10, spaceBefore=4*mm, spaceAfter=1*mm, textColor=C_GREEN, fontName=FONT_BOLD)
    NRM = ParagraphStyle('KL_N',  parent=SS['Normal'],  fontSize=8, fontName=FONT_REGULAR)
    SB  = ParagraphStyle('KL_SB', parent=SS['Normal'],  fontSize=8,  fontName=FONT_BOLD)
    STP = ParagraphStyle('KL_ST', parent=SS['Normal'],  fontSize=7,  leading=10, fontName=FONT_REGULAR)
    STEP = ParagraphStyle('KL_STEP', parent=SS['Normal'], fontSize=7, leading=10, fontName=FONT_BOLD, textColor=C_BLUE, spaceBefore=1.5*mm)

    def _tbl_style():
        return TableStyle([
            ('BACKGROUND',    (0, 0), (-1,  0), C_HDR),
            ('TEXTCOLOR',     (0, 0), (-1,  0), colors.white),
            ('FONTNAME',      (0, 0), (-1,  0), FONT_BOLD),
            ('FONTSIZE',      (0, 0), (-1,  0), 7),
            ('FONTNAME',      (0, 1), (-1, -1), FONT_REGULAR),
            ('FONTSIZE',      (0, 1), (-1, -1), 7),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.white, C_ODD]),
            ('GRID',          (0, 0), (-1, -1), 0.3, colors.grey),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING',    (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING',   (0, 0), (-1, -1), 3),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 3),
        ])

    def _tbl_style_compact():
        return TableStyle([
            ('BACKGROUND',    (0, 0), (-1,  0), C_HDR),
            ('TEXTCOLOR',     (0, 0), (-1,  0), colors.white),
            ('FONTNAME',      (0, 0), (-1,  0), FONT_BOLD),
            ('FONTSIZE',      (0, 0), (-1,  0), 6.5),
            ('FONTNAME',      (0, 1), (-1, -1), FONT_REGULAR),
            ('FONTSIZE',      (0, 1), (-1, -1), 6.5),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.white, C_ODD]),
            ('GRID',          (0, 0), (-1, -1), 0.3, colors.grey),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING',    (0, 0), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
            ('LEFTPADDING',   (0, 0), (-1, -1), 1.5),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 1.5),
        ])

    story = []

    # ── 1. Naslov ──────────────────────────────────────────────────────────────
    story.append(Paragraph(_t('Krojna Lista', 'Cut List'), ST))
    wl_k  = kitchen.get('wall', {}).get('length_mm', 0)
    wh_k  = kitchen.get('wall', {}).get('height_mm', 0)
    today = datetime.date.today().strftime('%d.%m.%Y')
    story.append(Paragraph(_safe(_t(f'Datum: {today}  |  Zid: {wl_k} x {wh_k} mm', f'Date: {today}  |  Wall: {wl_k} x {wh_k} mm')), NRM))
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
    service_packet = build_service_packet(kitchen, sections, lang=_lang)
    mods     = kitchen.get('modules', []) or []
    _summary_frames = []
    for _sec_key, _sec_df in (sections or {}).items():
        if _sec_df is None or _sec_df.empty:
            continue
        _tmp = _sec_df.copy()
        _tmp['__summary_material'] = _tmp['Materijal'].apply(
            lambda _m: _summary_material_label(_sec_key, _m, _lang)
        )
        _summary_frames.append(_tmp)

    if _summary_frames:
        story.append(Paragraph(_t('Sumarni pregled — svi rezovi', 'Summary - all cut parts'), H1))
        _comb = pd.concat(_summary_frames, ignore_index=True)
        _summ = (
            _comb
            .groupby(['__summary_material', 'Deb.', 'CUT_W [mm]', 'CUT_H [mm]', 'Kant'], as_index=False)
            .agg({'Kol.': 'sum'})
            .sort_values(['__summary_material', 'CUT_W [mm]', 'CUT_H [mm]'])
        )
        _sh = [[_t('Materijal', 'Material'), _t('Deb.', 'Thk.'), _t('Dužina [mm]', 'Length [mm]'), _t('Širina [mm]', 'Width [mm]'), _t('Kant', 'Edge'), _t('Kol.', 'Qty')]]
        _sr = [
            [_safe(str(r['__summary_material'])), str(r['Deb.']),
             _safe_val(r.get('CUT_W [mm]')), _safe_val(r.get('CUT_H [mm]')),
             _safe_val(r.get('Kant')), str(int(r['Kol.']))]
            for _, r in _summ.iterrows()
        ]
        _st = Table(_sh + _sr,
                    colWidths=[PW*0.25, PW*0.07, PW*0.14, PW*0.14, PW*0.32, PW*0.08],
                    repeatRows=1)
        _st.setStyle(_tbl_style_compact())
        story.append(_st)
        story.append(Spacer(1, 4*mm))

    _hdr_df = service_packet.get("project_header", pd.DataFrame())
    if _hdr_df is not None and not _hdr_df.empty:
        story.append(Paragraph(_t('Podaci o projektu', 'Project data'), H1))
        _hd = [[_t('Polje', 'Field'), _t('Vrednost', 'Value')]]
        _hd += [[_safe(str(r.get('Polje', ''))), _safe(str(r.get('Vrednost', '')))] for r in _hdr_df.to_dict('records')]
        _ht = Table(_hd, colWidths=[PW * 0.22, PW * 0.78], repeatRows=1)
        _ht.setStyle(_tbl_style())
        story.append(_ht)
        story.append(Spacer(1, 4*mm))

    _svc_cuts = service_packet.get("service_cuts", pd.DataFrame())
    if _svc_cuts is not None and not _svc_cuts.empty:
        story.append(Paragraph(_t('Šta nosiš u servis - sečenje', 'What you take to the workshop - cutting'), H1))
        _sh = [['RB', _t('Zid', 'Wall'), _t('Materijal', 'Material'), _t('Deb.', 'Thk.'), _t('CUT Duž.', 'Cut length'), _t('CUT Šir.', 'Cut width'), _t('Kant', 'Edge'), _t('Kol.', 'Qty')]]
        _sr = [[
            str(r.get('RB', '')),
            _safe_val(r.get('Zid', ''), '-'),
            _safe(str(r.get('Materijal', ''))),
            str(r.get('Deb.', '')),
            _safe_val(r.get('CUT_W [mm]', '')),
            _safe_val(r.get('CUT_H [mm]', '')),
            _safe_val(r.get('Kant', ''), '-'),
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
        story.append(Paragraph(_t('Šta nosiš u servis - kantovanje', 'What you take to the workshop - edging'), H1))
        _eh = [['PartCode', _t('Zid', 'Wall'), _t('Modul', 'Module'), _t('Deo', 'Part'), _t('Kol.', 'Qty'), _t('Kant', 'Edge'), _t('Napomena', 'Note')]]
        _er = [[
            _safe(str(r.get('PartCode', ''))),
            _safe_val(r.get('Zid', ''), '-'),
            _safe(str(r.get('Modul', ''))),
            _safe(_friendly_part_name(r.get('Deo', ''), _lang)),
            str(r.get('Kol.', '')),
            _safe_val(r.get('Kant', ''), '-'),
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
        story.append(Paragraph(_t('Šta nosiš u servis - obrada', 'What you take to the workshop - processing'), H1))
        _ph = [['PartCode', _t('Modul', 'Module'), _t('Deo', 'Part'), _t('Tip obrade', 'Processing type'), _t('Izvodi', 'Operations'), _t('Osnov izvođenja', 'Execution basis'), _t('Kol.', 'Qty'), _t('Obrada / napomena', 'Processing / note')]]
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
        story.append(Paragraph(_t('Instrukcije za servis', 'Workshop instructions'), H1))
        _ih = [['RB', _t('Stavka', 'Item'), _t('Instrukcija', 'Instruction')]]
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
        'carcass': _t('Korpus (stranice, dno, plafon)', 'Carcass (sides, bottom, top)'),
        'backs': _t('Leđne ploče', 'Back panels'),
        'fronts': _t('Frontovi', 'Fronts'),
        'worktop': _t('Radna ploča i nosači', 'Worktop and supports'),
        'plinth': _t('Sokla / Lajsna', 'Plinth / toe kick'),
    }
    for _sk, _df in sections.items():
        if _df is None or _df.empty:
            continue
        story.append(Paragraph(_SEC_TITLES.get(_sk, _sk.capitalize()), H1))
        if _sk == 'worktop':
            _sdh = [[
                _t('Modul', 'Module'),
                _t('Duž. zida', 'Wall L'),
                _t('Potrebno', 'Required'),
                _t('Nabavno', 'Purchase'),
                _t('Dub.', 'Depth'),
                _t('Field cut', 'Field cut'),
                _t('Spoj', 'Joint'),
                _t('Izrezi', 'Cut-outs'),
                _t('Napomena', 'Note'),
            ]]
            _sdr = [[
                _safe(str(r.get('Modul', ''))[:24]),
                str(int(float(r.get('Wall length [mm]', 0) or 0))) if str(r.get('Wall length [mm]', '')).strip() else '',
                str(int(float(r.get('Required length [mm]', 0) or 0))) if str(r.get('Required length [mm]', '')).strip() else '',
                str(int(float(r.get('Purchase length [mm]', 0) or 0))) if str(r.get('Purchase length [mm]', '')).strip() else '',
                str(int(float(r.get('Širina [mm]', 0) or 0))) if str(r.get('Širina [mm]', '')).strip() else '',
                _safe(str(r.get('Field cut', ''))),
                _safe(str(r.get('Joint type', ''))),
                _safe(str(r.get('Cutouts', ''))),
                _safe(str(r.get('Napomena', ''))),
            ] for r in _df.to_dict('records')]
            _sdt = Table(
                _sdh + _sdr,
                colWidths=[PW*0.15, PW*0.07, PW*0.08, PW*0.08, PW*0.06, PW*0.08, PW*0.07, PW*0.16, PW*0.25],
                repeatRows=1,
            )
        else:
            _rows = []
            for r in _df.to_dict('records'):
                _len_v = r.get('Dužina [mm]', '')
                if str(_len_v).strip() == '':
                    _len_v = r.get('CUT_W [mm]', '')
                _wid_v = r.get('Širina [mm]', '')
                if str(_wid_v).strip() == '':
                    _wid_v = r.get('CUT_H [mm]', '')
                _rows.append([
                    _safe(str(r.get('Modul', ''))[:22]),
                    _safe(_friendly_part_name(r.get('Deo', ''), _lang)),
                    _safe_val(_len_v), _safe_val(_wid_v),
                    str(r.get('Deb.', '')), str(int(r.get('Kol.', 0))),
                    _safe_val(r.get('Kant', ''), '-'), _safe(str(r.get('Napomena', '')))
                ])
            _sdh = [[_t('Modul', 'Module'), _t('Deo', 'Part'), _t('Duž.', 'Length'), _t('Šir.', 'Width'), _t('Deb.', 'Thk.'), _t('Kol.', 'Qty'), _t('Kant', 'Edge'), _t('Napomena', 'Note')]]
            _sdr = _rows
            _sdt = Table(_sdh + _sdr,
                         colWidths=[PW*0.20, PW*0.13, PW*0.08, PW*0.08,
                                    PW*0.06, PW*0.05, PW*0.20, PW*0.20],
                         repeatRows=1)
        _sdt.setStyle(_tbl_style())
        story.append(_sdt)
        story.append(Spacer(1, 3*mm))

    # ── 5. Po elementima ───────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph(_t('Po elementima - detalji i montaža', 'By unit - details and assembly'), H1))

    _comb_e  = pd.concat(all_dfs, ignore_index=True) if all_dfs else None
    _comb_has_id = (
        _comb_e is not None
        and not _comb_e.empty
        and "ID" in _comb_e.columns
    )
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
        _wall  = _safe(str(_m.get('wall_key', '') or ''))
        _mparts = _comb_e[_comb_e['ID'] == _mid_e] if _comb_has_id else pd.DataFrame()
        story.append(Paragraph(_t(f"#{_mid_e} – {_mlbl}", f"#{_mid_e} - {_mlbl}"), H2))
        story.append(Paragraph(
            _t(
                f"Tip: {_mtid}  |  Dimenzije: {_mw} × {_mh} × {_md} mm" + (f"  |  Zid: {_wall}" if _wall else ""),
                f"Type: {_mtid}  |  Dimensions: {_mw} × {_mh} × {_md} mm" + (f"  |  Wall: {_wall}" if _wall else ""),
            ),
            NRM,
        ))
        story.append(Spacer(1, 1.5*mm))

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
                _map_parts["Oznaka"] = _map_parts["PartCode"].map(_short_part_code)
                _map_parts["Deo"] = _map_parts["Deo"].map(lambda v: _friendly_part_name(v, _lang))
                _map_parts["Pozicija"] = _map_parts["Pozicija"].map(lambda v: _friendly_position_name(v, _lang))
                _map_parts = _map_parts.sort_values(["SklopKorak", "PartCode"]).reset_index(drop=True)
                _mhdr = [[_t('Oznaka', 'Label'), _t('Deo', 'Part'), _t('Gde ide', 'Where it goes'), _t('Korak', 'Step'), _t('Kom.', 'Qty')]]
                _mrows = [[
                    _safe(str(r.get('Oznaka', ''))),
                    _safe(_friendly_part_name(r.get('Deo', ''), _lang)),
                    _safe(str(r.get('Pozicija', ''))),
                    str(r.get('SklopKorak', '')),
                    str(r.get('Kol.', '')),
                ] for r in _map_parts.to_dict('records')]
                _mtbl = Table(
                    _mhdr + _mrows,
                    colWidths=[TBL_W*0.14, TBL_W*0.30, TBL_W*0.24, TBL_W*0.10, TBL_W*0.10],
                    repeatRows=1,
                )
                _mtbl.setStyle(_tbl_style())
                _ph = [[_t('Oznaka', 'Label'), _t('Deo', 'Part'), _t('Duž.', 'Length'), _t('Šir.', 'Width'), _t('Deb.', 'Thk.'), _t('Kol.', 'Qty'), _t('Kant', 'Edge')]]
                _pr = [
                    [_safe(_short_part_code(r.get('PartCode', ''))),
                     _safe(_friendly_part_name(r.get('Deo', ''), _lang)),
                     _safe_val((r.get('Dužina [mm]', '') if str(r.get('Dužina [mm]', '')).strip().lower() not in {'', 'nan', 'none', 'null'} else r.get('CUT_W [mm]', ''))),
                     _safe_val((r.get('Širina [mm]', '') if str(r.get('Širina [mm]', '')).strip().lower() not in {'', 'nan', 'none', 'null'} else r.get('CUT_H [mm]', ''))),
                     str(r.get('Deb.', '')), str(int(r.get('Kol.', 0))),
                     _safe_val(r.get('Kant', ''), '-')]
                    for r in _mparts.to_dict('records')
                ]
                _ptbl = Table(
                    _ph + _pr,
                    colWidths=[TBL_W*0.12, TBL_W*0.26, TBL_W*0.11, TBL_W*0.11,
                               TBL_W*0.08, TBL_W*0.08, TBL_W*0.24],
                    repeatRows=1,
                )
                _ptbl.setStyle(_tbl_style())

        # ── Uputstvo za montažu ────────────────────────────────────────────────
        _steps = assembly_instructions(_mtid, _mz, m=_m, kitchen=kitchen, lang=lang)
        _step_paras = []
        for s in _steps:
            _txt = _safe(s)
            if str(_txt).strip().startswith("--"):
                _step_paras.append(Paragraph(_txt.replace("--", "").strip(), STEP))
            elif str(_txt).strip():
                _step_paras.append(Paragraph(_txt, STP))
            else:
                _step_paras.append(Spacer(1, 1*mm))

        _tool_lines = _module_tool_hardware_lines(_mtid, _mz, _lang)
        _tool_paras = [Paragraph(_safe(f"• {x}"), STP) for x in _tool_lines]
        _preassembly_lines = _module_preassembly_lines(_mtid, _mz, _lang)
        _preassembly_paras = [Paragraph(_safe(f"• {x}"), STP) for x in _preassembly_lines]
        _role_notes: list[str] = []
        if _mparts is not None and not _mparts.empty:
            for _, _pr in _mparts.iterrows():
                _note = _part_role_note(
                    _friendly_part_name(_pr.get('Deo', ''), _lang),
                    _pr.get('Materijal', ''),
                    _pr.get('Deb.', ''),
                    _lang,
                )
                if _note and _note not in _role_notes:
                    _role_notes.append(_note)
        _role_note_paras = [Paragraph(_safe(f"• {x}"), STP) for x in _role_notes]

        # ── Desna kolona: rezovi + uputstvo ────────────────────────────────────
        _right: list = []
        _right.append(Paragraph(_t('Napomena za početnika', 'Note for beginners'), SB))
        _right.append(Paragraph(
            _t(
                'Oznaka dela na slici, u tabeli i u tekstu je ista. Prvo razvrstaj delove po oznaci, pa tek onda kreni na sklapanje.',
                'The part label is the same in the image, table and text. Sort the parts by label first, then start assembly.',
            ),
            STP,
        ))
        _right.append(Spacer(1, 2*mm))
        if _role_note_paras:
            _right.append(Paragraph(_t('Važne napomene o delovima', 'Important part notes'), SB))
            _right.extend(_role_note_paras)
            _right.append(Spacer(1, 2*mm))
        _right.append(Paragraph(_t('Proveri pre sklapanja', 'Check before assembly'), SB))
        _right.extend(_preassembly_paras)
        _right.append(Spacer(1, 2*mm))
        if _mtbl:
            _right.append(Paragraph(_t('Mapa delova za sklapanje', 'Assembly parts map'), SB))
            _right.append(_mtbl)
            _right.append(Paragraph(_t('Oznake na 2D slici koriste istu kratku oznaku kao i tabela i koraci sklapanja.', 'The labels in the 2D view use the same short label as the table and assembly steps.'), STP))
            _right.append(Spacer(1, 2*mm))
        if _ptbl:
            _right.append(Paragraph(_t('Rezovi', 'Cut parts'), SB))
            _right.append(_ptbl)
            _right.append(Paragraph(_safe(_kant_legend(_lang)), STP))
            _right.append(Spacer(1, 2*mm))
        _right.append(Paragraph(_t('Potreban alat i okov', 'Required tools and hardware'), SB))
        _right.extend(_tool_paras)
        _right.append(Spacer(1, 2*mm))
        _right.append(Paragraph(_t('Uputstvo za montažu', 'Assembly instructions'), SB))
        _right.extend(_step_paras)

        # ── Leva kolona: 2D iznad, 3D ispod — nested Table ────────────────────
        # ReportLab ne podrzava listu flowable-a direktno u celiji Table-a;
        # koristimo nested Table (1 kolona, vise redova) da slazemo slike.
        _img_nested_rows = []
        if _eimg_2d:
            _img_nested_rows.append([Paragraph('2D', STP)])
            _img_nested_rows.append([_eimg_2d])
            _img_nested_rows.append([Paragraph(_t('Oznake na slici prate tabelu dela: C = korpus, B = leđa, F = front, D = fioka.', 'Image labels match the parts table: C = carcass, B = back, F = front, D = drawer.'), STP)])
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
        story.append(Paragraph(_t('Šta kupuješ posebno', 'What you buy separately'), H1))
        _hh = [[_t('Grupa', 'Group'), _t('Naziv', 'Name'), _t('Tip / Sifra', 'Type / Code'), _t('Kol.', 'Qty'), _t('Napomena', 'Note')]]
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
        story.append(Paragraph(_t('Gotovi proizvodi - ne ulaze u sečenje', 'Ready-made products - not included in cutting'), H1))
        _rh = [[_t('Grupa', 'Group'), _t('Naziv', 'Name'), _t('Tip / Sifra', 'Type / Code'), _t('Kol.', 'Qty'), _t('Napomena', 'Note')]]
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
        story.append(Paragraph(_t('Kako ideš redom', 'Workflow order'), H1))
        _gh = [[_t('Korak', 'Step'), _t('Šta radiš', 'What you do'), _t('Napomena', 'Note')]]
        _gr = [[
            str(r.get('Korak', '')),
            _safe(str(r.get('Šta radiš', r.get('Sta radis', '')))),
            _safe(str(r.get('Napomena', ''))),
        ] for r in _guide_df.to_dict('records')]
        _gt = Table(_gh + _gr,
                    colWidths=[PW*0.08, PW*0.30, PW*0.62],
                    repeatRows=1)
        _gt.setStyle(_tbl_style())
        story.append(_gt)
        story.append(Spacer(1, 4*mm))

    for _title, _key in (
        (_t('Checklist pre servisa', 'Checklist before workshop'), 'workshop_checklist'),
        (_t('Checklist pre kucnog sklapanja', 'Checklist before home assembly'), 'home_checklist'),
    ):
        _cdf = service_packet.get(_key, pd.DataFrame())
        if _cdf is None or _cdf.empty:
            continue
        story.append(Paragraph(_title, H1))
        _ch = [['RB', _t('Stavka', 'Item'), _t('Status', 'Status')]]
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
