# -*- coding: utf-8 -*-
from __future__ import annotations

import re


def set_sidebar_primary_action(
    *,
    ui,
    logger,
    impl,
    label: str,
    handler=None,
) -> None:
    impl(
        ui=ui,
        logger=logger,
        label=label,
        handler=handler,
    )


def run_sidebar_primary_action(
    *,
    ui,
    impl,
    label_fallback: str,
    notify_empty: str,
) -> None:
    impl(
        ui=ui,
        label_fallback=label_fallback,
        notify_empty=notify_empty,
    )


def _translate_runtime_error(msg: str, lang: str) -> str:
    if str(lang or "sr").lower().strip() != "en":
        return str(msg or "")

    translated = str(msg or "")
    replacements = [
        ("Blokirano:", "Blocked:"),
        ("Greška:", "Error:"),
        ("Greska:", "Error:"),
        ("Element nije pronađen.", "Element not found."),
        ("Element nije pronađen", "Element not found"),
        ("Nema elemenata na zidu.", "There are no elements on the wall."),
        ("Element obrisan", "Element deleted"),
        ("Modul na Zidu", "Module on Wall"),
        ("ulazi u ugaoni prostor", "enters the corner zone"),
        ("leva ugaona zona", "left corner zone"),
        ("desna ugaona zona", "right corner zone"),
        ("dubine Zida A", "of Wall A depth"),
        ("granica=", "limit="),
        ("Pomeri desno za min", "Move right by at least"),
        ("Pomeri levo ili dodaj ugaoni modul.", "Move left or add a corner unit."),
        ("Jednokrilna vrata uz levi zid nemaju dovoljno mesta za otvaranje na strani sarke.", "Single-door unit next to the left wall does not have enough clearance to open on the hinge side."),
        ("Jednokrilna vrata uz desni zid nemaju dovoljno mesta za otvaranje na strani sarke.", "Single-door unit next to the right wall does not have enough clearance to open on the hinge side."),
        ("Promeni stranu rucke ili dodaj filer najmanje 30-50mm.", "Change the handle side or add a filler of at least 30-50 mm."),
        ("Drugi red gornjih elemenata mora biti oslonjen na element ispod po celoj svojoj sirini.", "The second row of wall units must be fully supported by the unit below across its entire width."),
        ("Popuna iznad visokog mora biti oslonjena na visoki element ispod po celoj svojoj sirini.", "The top infill above a tall unit must be fully supported by the tall unit below across its entire width."),
        ("Donji element dubine", "Base unit with depth"),
        ("je preplitak za kuhinjski standard.", "is too shallow for the kitchen standard."),
        ("Postavi najmanje 500mm, preporuceno 560mm.", "Set at least 500 mm; 560 mm is recommended."),
        ("Visoki element dubine", "Tall unit with depth"),
        ("je preplitak za stabilan kuhinjski korpus.", "is too shallow for a stable tall kitchen cabinet."),
        ("Gornji element dubine", "Wall unit with depth"),
        ("je predubok za bezbednu i ergonomicnu montazu.", "is too deep for safe and ergonomic installation."),
        ("Drzi se opsega 300-400mm.", "Keep it within the 300-400 mm range."),
        ("je premalen za standardni korpus i okove.", "is too small for a standard cabinet and hardware."),
        ("Postavi najmanje 250mm.", "Set at least 250 mm."),
        ("Ugradna masina za sudove trazi sirinu nise od najmanje 600mm.", "A built-in dishwasher requires a niche width of at least 600 mm."),
        ("Rerna/sporet sa plocom trazi najmanje 600mm sirine.", "An oven/cooker with a hob requires at least 600 mm of width."),
        ("Ugaoni element ima smisla samo u L ili U rasporedu kuhinje.", "A corner unit only makes sense in an L-shaped or U-shaped kitchen layout."),
        ("Na zidu", "On wall"),
        ("vec postoji ugaoni modul u zoni", "there is already a corner unit in zone"),
        ("Ugaoni modul na zidu", "The corner unit on wall"),
        ("mora biti naslonjen na unutrasnji ugao, kao poslednji element desno.", "must be aligned to the inner corner as the last unit on the right."),
        ("mora biti poslednji element na tom kraku.", "must be the last unit on that run."),
        ("mora biti naslonjen na unutrasnji ugao, kao prvi element levo.", "must be aligned to the inner corner as the first unit on the left."),
        ("mora biti prvi element na tom kraku.", "must be the first unit on that run."),
        ("Visoka appliance kolona za rernu/mikrotalasnu trazi najmanje 600mm sirine.", "A tall appliance column for an oven/microwave requires at least 600 mm of width."),
        ("Frizider modul trazi najmanje 600mm sirine.", "A fridge unit requires at least 600 mm of width."),
        ("Sudoperski element manji od 600mm nije preporucen za laicki workflow.", "A sink base unit smaller than 600 mm is not recommended for the standard workflow."),
        ("Ugaoni element sirine manje od", "A corner unit narrower than"),
        ("je previse rizican za stabilan ugaoni raspored.", "is too risky for a stable corner layout."),
        ("Modul za napu ili mikrotalasnu trazi najmanje 600mm sirine.", "A hood or microwave unit requires at least 600 mm of width."),
        ("Modul za napu ili mikrotalasnu trazi najmanje 300mm dubine.", "A hood or microwave unit requires at least 300 mm of depth."),
        ("Samostojeci uredjaj u donjoj zoni trazi najmanje 580mm dubine.", "A freestanding appliance in the base zone requires at least 580 mm of depth."),
        ("Samostojeci frizider trazi najmanje 600mm dubine.", "A freestanding fridge requires at least 600 mm of depth."),
        ("Integrisana visoka appliance kolona trazi najmanje 560mm dubine.", "An integrated tall appliance column requires at least 560 mm of depth."),
        ("Lift-up sirine", "A lift-up unit with width"),
        ("je previse rizican za ovu aplikaciju.", "is too risky for this application."),
        ("Razdvoji na dva elementa ili smanji sirinu na najvise 1200mm.", "Split it into two units or reduce the width to 1200 mm maximum."),
        ("Fiokar dubine", "A drawer unit with depth"),
        ("je preplitak za stabilan izbor klizaca.", "is too shallow for a stable slide selection."),
        ("Postavi najmanje 450mm.", "Set at least 450 mm."),
        ("Front fioke manji od 80mm nije dozvoljen za stabilan laicki workflow.", "A drawer front smaller than 80 mm is not allowed for a stable standard workflow."),
        ("Zbir visina fioka", "The total height of the drawers"),
        ("je prevelik za visinu modula", "is too large for the unit height"),
        ("Ostavi barem 10mm rezerve za fuge i frontove.", "Leave at least 10 mm of clearance for gaps and fronts."),
        ("Vrata kod kombinacije vrata + fioka moraju imati najmanje 180mm visine.", "In a doors + drawer combination, the doors must be at least 180 mm high."),
        ("Vrata kod kombinacije vrata + fioka su previsoka; ostavi najmanje 120mm za fioku i fuge.", "In a doors + drawer combination, the doors are too tall; leave at least 120 mm for the drawer and gaps."),
        ("Jednokrilni element sirine", "A single-door unit with width"),
        ("je previse sirok za stabilno kucno sklapanje.", "is too wide for stable home assembly."),
        ("Koristi 2 vrata ili podeli element.", "Use 2 doors or split the unit."),
        ("Jednokrilni sused uz ugaoni modul ne sme da otvara vrata ka uglu.", "A single-door unit next to a corner unit must not open toward the corner."),
        ("Promeni stranu rucke ili koristi drugi tip susednog elementa.", "Change the handle side or use a different adjacent unit type."),
        ("Jednokrilni sused uz ugaoni modul je preširok", "A single-door unit next to a corner unit is too wide"),
        ("za sigurno otvaranje u L uglu.", "for safe opening in an L-shaped corner."),
        ("Koristi max", "Use a maximum of"),
        ("dvokrilni element, fiokar ili ostavi filer.", "a double-door unit, a drawer unit, or leave a filler."),
        ("Visoki element", "Tall unit"),
        ("je previsok za standardno kucno rukovanje i montazu.", "is too tall for standard home handling and installation."),
        ("Smanji visinu ili koristi tall + tall_top podelu.", "Reduce the height or use a tall + top-extension split."),
        ("Element iznad visokog moze da se doda tek kada postoji visoki element ispod njega.", "A unit above a tall unit can only be added when there is a tall unit below it."),
        ("Drugi red gornjih elemenata moze da se doda tek kada postoji gornji element ispod njega.", "A second row of wall units can only be added when there is a wall unit below it."),
        ("Nema slobodnog mesta u zoni", "There is no free space in zone"),
        ("Slobodno:", "Free:"),
        ("Visina elementa", "Unit height"),
        ("prelazi dozvoljenu visinu za zonu", "exceeds the allowed height for zone"),
        ("Smanji visinu!", "Reduce the height."),
        ("Nema prostora za izmenu širine: fali", "There is not enough space to change the width: missing"),
        ("do zida.", "to the wall."),
        ("Nema prostora za izmenu širine: preklapanje donjih elemenata.", "There is not enough space to change the width: base units would overlap."),
    ]
    for src, dst in replacements:
        translated = translated.replace(src, dst)
    translated = re.sub(r"\bZid ([ABC])\b", r"Wall \1", translated)
    return translated


def format_user_error(err: Exception | str, lang: str = "sr") -> str:
    msg = str(err or "").strip()
    if not msg:
        return "Error." if str(lang or "sr").lower().strip() == "en" else "Greška."
    msg = _translate_runtime_error(msg, lang)
    _lower = msg.lower()
    if _lower.startswith("blocked:") or _lower.startswith("blokirano:"):
        return msg
    if _lower.startswith("error:") or _lower.startswith("greška:") or _lower.startswith("greska:"):
        return msg
    return f"{'Error' if str(lang or 'sr').lower().strip() == 'en' else 'Greška'}: {msg}"


def render_color_picker_wrapper(
    *,
    ui,
    render_color_picker_fn,
    presets,
    color_ref: dict,
    title: str,
    columns: int,
    swatch_h: int,
    lang: str = "sr",
) -> None:
    render_color_picker_fn(
        ui=ui,
        presets=presets,
        color_ref=color_ref,
        title=title,
        columns=columns,
        swatch_h=swatch_h,
        lang=lang,
    )
