# -*- coding: utf-8 -*-
"""
test_i18n.py — Kompletna provera i18n za sve jezike.
Pokreni: python test_i18n.py
Ocekivani rezultat: sve provere PASS, na kraju "SVE PROVERE PROSLE"
"""
import sys
import py_compile
sys.stdout.reconfigure(encoding="utf-8")

PASS = 0
FAIL = 0
WARN = 0

def ok(msg):
    global PASS
    PASS += 1
    print(f"  [PASS] {msg}")

def fail(msg):
    global FAIL
    FAIL += 1
    print(f"  [FAIL] {msg}")

def warn(msg):
    global WARN
    WARN += 1
    print(f"  [WARN] {msg}")

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ─────────────────────────────────────────────────────────────
section("1. SINTAKSA FAJLOVA")
# ─────────────────────────────────────────────────────────────
for fname in ["i18n.py", "ui_pdf_export.py"]:
    try:
        py_compile.compile(fname, doraise=True)
        ok(f"{fname} — sintaksa OK")
    except py_compile.PyCompileError as e:
        fail(f"{fname} — SINTAKSNA GRESKA: {e}")

# ─────────────────────────────────────────────────────────────
section("2. IMPORT I OSNOVNE FUNKCIJE")
# ─────────────────────────────────────────────────────────────
try:
    from i18n import tr, _TRANSLATIONS, normalize_language_code, LANGUAGE_OPTIONS, LANGUAGE_FALLBACKS
    ok("import i18n OK")
except Exception as e:
    fail(f"import i18n GRESKA: {e}")
    sys.exit(1)

try:
    from ui_pdf_export import _friendly_part_name, _normalize_label_text, _format_material_role_pdf
    ok("import ui_pdf_export OK")
except Exception as e:
    fail(f"import ui_pdf_export GRESKA: {e}")

# ─────────────────────────────────────────────────────────────
section("3. LANGUAGE OPTIONS I FALLBACK LANAC")
# ─────────────────────────────────────────────────────────────
expected_langs = ["sr", "en", "es", "pt-br", "ru", "zh-cn", "hi"]
for lang in expected_langs:
    if lang in LANGUAGE_OPTIONS:
        ok(f"LANGUAGE_OPTIONS ima '{lang}'")
    else:
        fail(f"LANGUAGE_OPTIONS NEMA '{lang}'")

# normalize_language_code
norm_tests = [
    ("pt-BR", "pt-br"), ("pt-br", "pt-br"), ("PT-BR", "pt-br"),
    ("zh-CN", "zh-cn"), ("zh-cn", "zh-cn"), ("ZH-CN", "zh-cn"),
    ("ru", "ru"), ("RU", "ru"),
    ("hi", "hi"), ("HI", "hi"),
    ("es", "es"), ("ES", "es"),
    ("sr", "sr"), ("en", "en"),
]
for inp, expected in norm_tests:
    result = normalize_language_code(inp)
    if result == expected:
        ok(f"normalize('{inp}') = '{result}'")
    else:
        fail(f"normalize('{inp}') = '{result}', ocekivano '{expected}'")

# ─────────────────────────────────────────────────────────────
section("4. SRPSKI — REFERENCE JEZIK")
# ─────────────────────────────────────────────────────────────
sr_keys = [
    "tab.wizard", "tab.elements", "tab.cutlist", "tab.settings",
    "toolbar.save", "toolbar.load", "toolbar.reset",
    "wizard.back", "wizard.mode_standard",
    "settings.title", "settings.carcass_material",
    "room.start_design", "room.wall_name_back",
    "elements.add_element", "params.width_mm",
    "edit.apply", "common.cancel",
    "cutlist.title", "cutlist.section_carcass",
]
sr = _TRANSLATIONS.get("sr", {})
for key in sr_keys:
    val = tr(key, "sr")
    if val == key:
        fail(f"sr '{key}' -> KEY_MISSING (vracen kljuc)")
    else:
        ok(f"sr '{key}' -> '{val}'")

# ─────────────────────────────────────────────────────────────
section("5. ENGLESKI — REFERENTNI FALLBACK")
# ─────────────────────────────────────────────────────────────
en = _TRANSLATIONS.get("en", {})
en_mandatory = [
    "tab.wizard", "tab.elements", "tab.cutlist", "tab.settings",
    "toolbar.save", "toolbar.load", "toolbar.reset",
    "wizard.back", "wizard.mode_standard", "wizard.step_mode",
    "settings.title", "settings.carcass_material",
    "room.start_design", "room.wall_name_back",
    "elements.add_element", "params.width_mm",
    "edit.apply", "common.cancel",
    "cutlist.title", "cutlist.section_carcass",
    "cutlist.section_fronts", "cutlist.section_hardware",
    "cutlist.workflow", "cutlist.checklist_assembly",
    "project_io.load_title", "project_io.save_ok",
    "help.title", "nova.title", "nova.created_ok",
    "gate.title", "gate.checkout_btn",
]
for key in en_mandatory:
    val = tr(key, "en")
    if val == key:
        fail(f"en '{key}' -> KEY_MISSING")
    else:
        ok(f"en '{key}' -> '{val}'")

# ─────────────────────────────────────────────────────────────
section("6. PROVJERA ???? PLACEHOLDER VRIJEDNOSTI")
# ─────────────────────────────────────────────────────────────
all_langs = ["sr", "en", "es", "pt-br", "ru", "zh-cn", "hi"]
for lang in all_langs:
    block = _TRANSLATIONS.get(lang, {})
    import re as _re
    # Placeholder: ? unutar reci (nije legitimni upitnik na kraju recenice/reci)
    # Legitimni upitnici: "password?", "lozinka?", "zone?" — na kraju reci/recenice
    # Problematicni: "Padr?o" — unutar reci, "?????" — vise uzastopnih
    q_keys = []
    for k, v in block.items():
        if "?" not in v:
            continue
        if any(ord(c) > 127 for c in v):
            continue  # ima unicode, nije placeholder problem
        # Vise uzastopnih upitnika = sigurno placeholder
        if _re.search(r'\?{2,}', v):
            q_keys.append(k)
            continue
        # Upitnik unutar reci (nije na kraju reci/recenice) = problem
        if _re.search(r'\?[a-zA-Z]', v):
            q_keys.append(k)
    if q_keys:
        fail(f"{lang}: {len(q_keys)} kljuceva sa sumnjivim '?' (unutar reci): {q_keys[:3]}")
    else:
        ok(f"{lang}: nema sumnjivnih '?' placeholder vrijednosti")

# ─────────────────────────────────────────────────────────────
section("7. KLJUCNI UI EKRANI — SVA PREVODI (ne smiju biti engleski)")
# ─────────────────────────────────────────────────────────────
# Kljucevi koji MORAJU biti prevedeni (ne smiju padati na engleski)
must_translate = [
    "tab.wizard", "tab.elements", "tab.cutlist", "tab.settings",
    "toolbar.save", "toolbar.load", "toolbar.reset",
    "wizard.back", "settings.title", "settings.carcass_material",
    "room.start_design", "elements.add_element",
    "params.width_mm", "edit.apply", "common.cancel",
    "cutlist.title", "cutlist.section_carcass",
]
# Legitimno ostaje engleski (brand nazivi, kratice)
LEGIT_EN = {
    "toolbar.app_sub", "tab.ops", "nova.plan_free_title",
    "cutlist.btn_pdf", "cutlist.btn_excel", "cutlist.btn_csv",
    "cutlist.preview_2d", "cutlist.preview_3d",
    "settings.material_mdf", "settings.material_lacobel",
    "settings.worktop_joint_miter",
}
non_sr_langs = ["es", "pt-br", "ru", "zh-cn", "hi"]
for key in must_translate:
    en_val = en.get(key, "")
    for lang in non_sr_langs:
        val = tr(key, lang)
        if val == key:
            fail(f"[{lang}] '{key}' -> KEY MISSING (vracen kljuc)")
        elif val == en_val and key not in LEGIT_EN:
            warn(f"[{lang}] '{key}' -> jos engleski: '{val}'")
        else:
            ok(f"[{lang}] '{key}' -> '{val}'")

# ─────────────────────────────────────────────────────────────
section("8. FALLBACK LANAC — NEDOSTAJUCI KLJUC IDE NA ENGLESKI, NE NA KEY")
# ─────────────────────────────────────────────────────────────
# Kljuc koji sigurno ne postoji ni u jednom bloku
fake_key = "this.key.does.not.exist.xyz_12345"
for lang in non_sr_langs:
    val = tr(fake_key, lang)
    if val == fake_key:
        ok(f"[{lang}] nepostojeci kljuc vraca sam kljuc (fallback se iscrpio) — OK za nepostojece")
    else:
        warn(f"[{lang}] nepostojeci kljuc vraca '{val}' — neocekivano")

# Kljuc koji postoji u EN ali ne u ostalim jezicima — mora se vratiti EN verzija
en_only_key = "ops.denied_title"  # admin-only, ne prevodi se
en_only_val = en.get(en_only_key, "")
if en_only_val:
    for lang in non_sr_langs:
        val = tr(en_only_key, lang)
        if val == en_only_val:
            ok(f"[{lang}] '{en_only_key}' ispravno pada na EN fallback")
        elif val == en_only_key:
            fail(f"[{lang}] '{en_only_key}' vracen kao kljuc — fallback ne radi!")
        else:
            ok(f"[{lang}] '{en_only_key}' -> prevedeno: '{val[:40]}'")

# ─────────────────────────────────────────────────────────────
section("9. PDF DIJAKRITIKE — _friendly_part_name")
# ─────────────────────────────────────────────────────────────
pdf_tests = [
    ("Ledja",           "sr", "Leđna ploča"),
    ("Bocna ploca",     "sr", "Bočna stranica sanduka fioke"),
    ("Ledja / prolaz",  "sr", "Leđna ploča / prolaz"),
    ("Leđa",            "sr", "Leđna ploča"),
    ("Bočna ploča",     "sr", "Bočna stranica sanduka fioke"),
    ("Dno",             "sr", "Donja ploča korpusa"),
    ("Plafon",          "sr", "Gornja ploča korpusa"),
    ("Leva strana",     "sr", "Leva stranica korpusa"),
    ("Desna strana",    "sr", "Desna stranica korpusa"),
    ("Ledja",           "en", "Back panel"),
    ("Bocna ploca",     "en", "Drawer box side"),
    ("Leva strana",     "en", "Left carcass side"),
    ("Dno",             "en", "Bottom carcass panel"),
]
for inp, lang, expected in pdf_tests:
    result = _friendly_part_name(inp, lang=lang)
    if result == expected:
        ok(f"_friendly_part_name('{inp}', '{lang}') = '{result}'")
    else:
        fail(f"_friendly_part_name('{inp}', '{lang}') = '{result}', ocekivano '{expected}'")

# Provjera da nema losih stringova u izlazu
bad_substrings = ["ploca", "ledja", "bocna ploca", "bocni", "radna ploca",
                  "gornja ploca", "donja ploca", "bocna stranica sanduka fioke".replace("č","c")]
all_inputs = ["Ledja", "Bocna ploca", "Leđa", "Bočna ploča", "Dno", "Plafon",
              "Leva strana", "Desna strana", "Vrata", "Front fioke"]
for inp in all_inputs:
    result = _friendly_part_name(inp, lang="sr")
    for bad in bad_substrings:
        if bad.lower() in result.lower():
            fail(f"_friendly_part_name('{inp}') -> '{result}' SADRZI LOS STRING '{bad}'")
            break

# _format_material_role_pdf
pdf_role_tests = [
    ("back",    "sr", "Leđa"),
    ("worktop", "sr", "Radna ploča"),
    ("back",    "en", "Back"),
    ("worktop", "en", "Worktop"),
]
for role, lang, expected_contains in pdf_role_tests:
    result = _format_material_role_pdf("Iverica 18mm", role, lang=lang)
    if expected_contains in result:
        ok(f"_format_material_role_pdf(role='{role}', lang='{lang}') = '{result}'")
    else:
        fail(f"_format_material_role_pdf(role='{role}', lang='{lang}') = '{result}', ocekivano da sadrzi '{expected_contains}'")

# ─────────────────────────────────────────────────────────────
section("10. FORMAT STRINGOVI SA PLACEHOLDERIMA")
# ─────────────────────────────────────────────────────────────
fmt_tests = [
    ("settings.notify_updated_fmt", "sr",   {"zone": "Baza", "val": "560", "count": "3"}),
    ("settings.notify_updated_fmt", "en",   {"zone": "Base", "val": "560", "count": "3"}),
    ("settings.notify_updated_fmt", "ru",   {"zone": "База", "val": "560", "count": "3"}),
    ("cutlist.export_job_queued",   "en",   {"job_type": "PDF", "job_id": "42"}),
    ("cutlist.export_job_queued",   "es",   {"job_type": "PDF", "job_id": "42"}),
    ("nova.billing_status_fmt",     "en",   {"plan": "PRO", "billing_status": "active", "access_tier": "pro"}),
    ("canvas.notify_added",         "sr",   {"label": "Ormarić 600"}),
    ("canvas.notify_added",         "en",   {"label": "Cabinet 600"}),
]
for key, lang, kwargs in fmt_tests:
    result = tr(key, lang, **kwargs)
    if result == key:
        fail(f"[{lang}] '{key}' -> KEY_MISSING")
    elif "{" in result and "}" in result:
        fail(f"[{lang}] '{key}' -> neformatirano: '{result}'")
    else:
        ok(f"[{lang}] '{key}' -> '{result}'")

# ─────────────────────────────────────────────────────────────
section("REZULTAT")
# ─────────────────────────────────────────────────────────────
total = PASS + FAIL + WARN
print(f"\n  PASS: {PASS}")
print(f"  FAIL: {FAIL}")
print(f"  WARN: {WARN} (upozorenja — ne blokiraju)")
print(f"  UKUPNO: {total}")
print()
if FAIL == 0:
    print("  ✓ SVE PROVERE PROSLE — i18n i PDF dijakritike su ispravni.")
else:
    print(f"  ✗ IMA {FAIL} NEUSPJELIH PROVJERA — pogledaj FAIL redove gore.")
    sys.exit(1)
