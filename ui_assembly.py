# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List


def _line(title: str) -> str:
    return f"-- {title} --"


def assembly_instructions(
    tid: str,
    zone: str,
    m: dict | None = None,
    kitchen: dict | None = None,
) -> List[str]:
    """Vraca prakticna montazna uputstva po tipu elementa."""
    tid = str(tid or "").upper()
    zone = str(zone or "base").lower()
    m = m or {}
    kitchen = kitchen or {}

    w = int(m.get("w_mm", 600))
    h = int(m.get("h_mm", 720))
    d = int(m.get("d_mm", 560))
    params = m.get("params") or {}
    thk = int(float((kitchen.get("materials") or {}).get("carcass_thk", 18) or 18))
    edge = int(float((kitchen.get("materials") or {}).get("edge_abs_thk", 2) or 2))
    foot = int(kitchen.get("foot_height_mm", 100) or 100)

    side_h = h - edge
    side_d = d - edge
    inner_w = w - 2 * thk
    inner_d = d - edge
    back_w = w - 2 * thk - 2
    back_h = h - 2 * thk
    rail_w = w - 2 * thk
    rail_h = 96

    n_doors = 2 if ("2DOOR" in tid or "DOORS" in tid or "HOB" in tid) else 1
    door_w = max(1, (w - 2) // n_doors)
    door_h = h - edge
    drawer_heights = params.get("drawer_heights") or []
    n_drawers = len(drawer_heights) if drawer_heights else int(params.get("n_drawers", 3 if h > 600 else 2))

    if tid in {"FILLER_PANEL", "END_PANEL"}:
        panel_name = "Filer panel" if tid == "FILLER_PANEL" else "Zavrsna bocna ploca"
        panel_w = w if tid == "FILLER_PANEL" else d
        return [
            _line("PANEL ELEMENT"),
            f"  {panel_name}: 1 kom  {panel_w} x {h} mm",
            f"  Debljina panela: {thk} mm",
            "  Kantovanje: prednja + gornja + donja ivica",
            "",
            _line("KORAK 1 - PROVERA MERE"),
            "  Proveri stvarnu sirinu otvora ili zavrsne stranice pre busenja.",
            "  Ostaviti 2-3 mm rezerve ako panel ide uz neravan zid.",
            "",
            _line("KORAK 2 - POZICIONIRANJE"),
            "  Privremeno namesti panel stegama uz susedni korpus ili zidnu letvu.",
            "  Prednja ivica mora biti u ravni sa frontovima kuhinje.",
            "",
            _line("KORAK 3 - FIKSIRANJE"),
            "  Pricvrsti panel vijcima 4x30 mm sa unutrasnje strane susednog elementa.",
            "  Ako ide uz zid, po potrebi koristi pomocnu letvu ili ugaonik.",
            "",
            _line("KORAK 4 - ZAVRSNA PROVERA"),
            "  Proveri da panel ne viri ispred fronta i da nema uvijanja.",
        ]

    if tid == "BASE_DISHWASHER_FREESTANDING":
        return [
            _line("SAMOSTOJECA MASINA ZA SUDOVE"),
            "  Ovaj uredjaj nema korpus ni front u krojnoj listi.",
            f"  Obezbedi ravnu nisu sirine {w} mm i dubine najmanje {d} mm.",
            "  Povezi vodu, odvod i struju prema uputstvu proizvodjaca.",
            "  Nakon nivelacije proveri otvaranje vrata i pristup instalacijama.",
        ]

    if tid == "BASE_OVEN_HOB_FREESTANDING":
        return [
            _line("SAMOSTOJECI SPORET"),
            "  Ovaj uredjaj nema korpus ni front u krojnoj listi.",
            f"  Obezbedi ravnu poziciju sirine {w} mm i dubine najmanje {d} mm.",
            "  Povezi struju ili gas prema pravilima proizvodjaca i lokalnim propisima.",
            "  Posle nivelacije proveri da vrata rerne i ploca imaju slobodan prostor.",
        ]

    if tid == "TALL_FRIDGE_FREESTANDING":
        return [
            _line("SAMOSTOJECI FRIZIDER"),
            "  Ovaj uredjaj nema korpus ni front u krojnoj listi.",
            f"  Obezbedi poziciju sirine {w} mm, dubine najmanje {d} mm i ventilacioni razmak po uputstvu proizvodjaca.",
            "  Ne zatvaraj gornji i zadnji vazdusni prostor maskama bez ventilacije.",
            "  Nakon postavljanja proveri otvaranje vrata i pristup uticnici.",
        ]

    if zone == "base":
        if tid == "BASE_DISHWASHER":
            return [
                _line("SASTAVNICA MZS SLOTA"),
                f"  Vezna letva: 1 kom  {w} x 100 mm",
                f"  Front MZS: 1 kom  {door_w} x {door_h} mm",
                "  Ugradna masina: 1 kom",
                "  Montazni set fronta: 1 set",
                "",
                _line("KORAK 1 - PRIPREMA OTVORA"),
                "  Ovaj modul nema sopstveni korpus; bocne strane daju susedni elementi.",
                "  Proveri cistu sirinu nise i dubinu pre unosenja uredjaja.",
                "  Veznu letvu montiraj ispod radne ploce izmedju susednih korpusa.",
                "",
                _line("KORAK 2 - PRIKLJUCCI"),
                "  Dovedi struju, vodu i odvod prema uputstvu proizvodjaca.",
                "  Creva i kabl ne smeju biti prignjeceni iza uredjaja.",
                "",
                _line("KORAK 3 - UBACIVANJE MASINE"),
                "  Uvuci masinu u nisu bez sile i iznivelisi je preko fabrickih nozica.",
                "",
                _line("KORAK 4 - FRONT MZS"),
                "  Front pricvrsti na vrata masine pomocu fabrickog sablona i montaznog seta.",
                "  Ostaviti jednake fuge 2-3 mm prema susednim frontovima.",
                "",
                _line("KORAK 5 - ZAVRSNA PROVERA"),
                "  Probaj otvaranje vrata i rad masine pre zatvaranja sokle.",
            ]

        if "SINK" in tid:
            return [
                _line("SUDOPERSKI ELEMENT"),
                f"  Leva bocna ploca: 1 kom  {side_d} x {side_h} mm",
                f"  Desna bocna ploca: 1 kom  {side_d} x {side_h} mm",
                f"  Dno: 1 kom  {inner_w} x {inner_d} mm",
                f"  Ledjna ploca: 1 kom  {back_w} x {back_h} mm",
                f"  Vrata ispod sudopere: {n_doors} kom  {door_w} x {door_h} mm",
                "",
                _line("KORAK 1 - KORPUS"),
                "  Sastavi bocne stranice i dno kao standardni bazni korpus.",
                "  Gornja puna ploca se ne ugradjuje preko celog otvora zbog sudopere i instalacija.",
                "",
                _line("KORAK 2 - LEDJA I OTVORI"),
                "  Na ledjnoj ploci obelezi i izrezi otvor za dovod, odvod i eventualnu uticnicu.",
                "  Otvor pravi tek kada proveris stvarnu poziciju instalacija na zidu.",
                "",
                _line("KORAK 3 - VRATA"),
                "  Montiraj vrata i podesi fuge 2-3 mm da se nesmetano otvaraju ispod sudopere.",
                "",
                _line("KORAK 4 - RADNA PLOCA I SUDOPERA"),
                "  Na radnoj ploci iscrtaj otvor prema sablonu sudopere.",
                "  Isprskanu ivicu otvora zastiti od vlage pre montaze sudopere.",
                "",
                _line("KORAK 5 - ZAVRSNA PROVERA"),
                "  Pusti vodu i proveri da li sifon, slavina i spojevi cure.",
            ]

        steps: List[str] = [
            _line("SASTAVNICA KORPUSA"),
            f"  Leva bocna ploca: 1 kom  {side_d} x {side_h} mm",
            f"  Desna bocna ploca: 1 kom  {side_d} x {side_h} mm",
            f"  Dno: 1 kom  {inner_w} x {inner_d} mm",
            f"  Gornja ploca: 1 kom  {inner_w} x {inner_d} mm",
            f"  Ledjna ploca: 1 kom  {back_w} x {back_h} mm",
            f"  Nosac radne ploce: 1 kom  {rail_w} x {rail_h} mm",
            f"  Noge: 4 kom  h = {foot} mm",
        ]
        if "COOKING" in tid or tid == "OVEN_HOB":
            steps += [
                f"  Front fioke: 1 kom  {door_w} x 126 mm",
                "  Sanduk fioke: 1 kom",
                "  Klizaci za fioku: 1 par",
                "  Ugradna rerna: 1 kom",
                "  Ploca za kuvanje: 1 kom",
            ]
        elif "DRAWER" in tid and "DOOR" not in tid:
            steps += [
                f"  Frontovi fioka: {n_drawers} kom",
                f"  Klizaci za fioke: {n_drawers} para",
            ]
        elif "DOOR_DRAWER" in tid:
            steps += [
                f"  Vrata: {n_doors} kom  {door_w} x {door_h} mm",
                "  Front fioke: 1 kom",
                "  Klizaci za fioku: 1 par",
            ]
        elif tid == "BASE_NARROW":
            steps += [
                f"  Front uskog modula: 1 kom  {door_w} x {door_h} mm",
                "  Uski izvlacni mehanizam: 1 set",
                "  Korpe / nosaci: 1 set",
            ]
        elif "OPEN" in tid:
            steps += [
                "  Podesive police: prema krojnoj listi",
                "  Nosaci polica: 4 kom po polici",
            ]
        elif "DRAWER" not in tid and "OVEN" not in tid and "COOKING" not in tid and "HOB" not in tid:
            steps += [
                f"  Vrata: {n_doors} kom  {door_w} x {door_h} mm",
                f"  Sarniri: {n_doors * 2} kom",
            ]

        steps += [
            "",
            _line("KORAK 1 - BOCNE PLOCE"),
            "  Izbusiti rupe za konfirmate i zleb za ledjnu plocu.",
            "",
            _line("KORAK 2 - DNO I GORNJA PLOCA"),
            "  Spoji dno i gornju plocu izmedju bocnih stranica.",
            "",
            _line("KORAK 3 - LEDJNA PLOCA"),
            "  Umetni ledjnu plocu i proveri dijagonale.",
        ]

        if "DRAWER" in tid and "DOOR" not in tid:
            steps += [
                "",
                _line("KORAK 4 - FIOKE"),
                "  Montiraj klizace, sastavi sanduke fioka i podesi frontove.",
            ]
        elif "DOOR_DRAWER" in tid or ("DOOR" in tid and "DRAWER" in tid):
            steps += [
                "",
                _line("KORAK 4 - VRATA + FIOKA"),
                "  Montiraj vrata, zatim klizac i front fioke.",
            ]
        elif "TRASH" in tid:
            steps += [
                "",
                _line("KORAK 4 - SORTIRNIK"),
                "  Montiraj izvlacni mehanizam i pricvrsti front sortirnika.",
            ]
        elif tid == "BASE_NARROW":
            steps += [
                "",
                _line("KORAK 4 - USKI IZVLACNI MODUL"),
                "  Montiraj cargo mehanizam i pricvrsti front na nosac mehanizma.",
            ]
        elif "COOKING" in tid or tid == "OVEN_HOB":
            steps += [
                "",
                _line("KORAK 4 - KUHINJSKA JEDINICA"),
                "  Uvuci rernu u korpus i isezi otvor u radnoj ploci prema sablonu ploce.",
                "  Lazni front montiraj tek nakon probe zazora oko rerne.",
            ]
        elif "OPEN" in tid:
            steps += [
                "",
                _line("KORAK 4 - POLICE"),
                "  Ugradi nosace polica i postavi police na zeljene visine.",
                "  Proveri da su sve police u libeli pre opterecenja.",
            ]
        elif "HOB" in tid:
            steps += [
                "",
                _line("KORAK 4 - PLOCA ZA KUVANJE"),
                "  Iseci otvor u radnoj ploci prema sablonu ploce i montiraj vrata ispod.",
            ]
        elif "OVEN" in tid:
            steps += [
                "",
                _line("KORAK 4 - UGRADNA RERNA"),
                "  Ostaviti otvor za kabl i pricvrstiti rernu prema uputstvu proizvodjaca.",
            ]
        else:
            steps += [
                "",
                _line("KORAK 4 - VRATA"),
                "  Montiraj sarnire, okaci vrata i podesi fuge 2 mm.",
            ]

        steps += [
            "",
            _line("KORAK 5 - NOGE I POZICIONIRANJE"),
            "  Montiraj noge, nivelisi element i tek onda montiraj radnu plocu.",
        ]
        return steps

    if zone in ("wall", "wall_upper"):
        n_wall_doors = 2 if ("2DOOR" in tid or "DOORS" in tid) else 1
        wall_title = "SASTAVNICA GORNJEG ELEMENTA" if zone == "wall_upper" else "SASTAVNICA KORPUSA"
        steps = [
            _line(wall_title),
            f"  Leva bocna ploca: 1 kom  {side_d} x {side_h} mm",
            f"  Desna bocna ploca: 1 kom  {side_d} x {side_h} mm",
            f"  Dno: 1 kom  {inner_w} x {inner_d} mm",
            f"  Gornja ploca: 1 kom  {inner_w} x {inner_d} mm",
            f"  Ledjna ploca: 1 kom  {back_w} x {back_h} mm",
        ]
        if "OPEN" in tid:
            steps += [
                "  Podesive police: prema krojnoj listi",
                "  Nosaci polica: 4 kom po polici",
            ]
        if "LIFTUP" in tid:
            steps += [
                f"  Front klapne: 1 kom  {door_w} x {door_h} mm",
                "  Lift-up mehanizam: 1 set",
            ]
        elif "GLASS" in tid:
            steps += [
                f"  Staklena vrata: {n_wall_doors} kom  {door_w} x {door_h} mm",
                f"  Sarke za staklo: {n_wall_doors * 2} kom",
            ]
        elif "OPEN" not in tid and "HOOD" not in tid and "MICRO" not in tid:
            steps += [
                f"  Vrata: {n_wall_doors} kom  {door_w} x {door_h} mm",
                f"  Sarniri: {n_wall_doors * 2} kom",
            ]
        steps += [
            "",
            _line("KORAK 1 - KORPUS"),
            "  Sastavi okvir i umetni ledjnu plocu u zlebove.",
            "",
            _line("KORAK 2 - VRATA / MEHANIZAM"),
        ]
        if "HOOD" in tid:
            steps += [
                "  Element je kuciste za napu - bez vrata i bez polica.",
                "  Ostaviti otvor za odvod prema sablonu proizvodjaca.",
            ]
        elif "MICRO" in tid:
            steps += [
                "  Element je otvorena nisa za mikrotalasnu - bez vrata.",
                "  Ostaviti otvor za kabl i ventilacioni razmak.",
            ]
        elif "CORNER" in tid:
            steps += [
                "  Ugaoni zidni element zahteva proveru stvarnog ugla zida pre busenja.",
            ]
        elif "GLASS" in tid:
            steps += [
                "  Montiraj sarke za staklena vrata prema sablonu proizvodjaca.",
            ]
        elif "LIFTUP" in tid:
            steps += [
                "  Montiraj lift-up mehanizam i podesi snagu opruge prema masi fronta.",
            ]
        elif "OPEN" in tid:
            steps += [
                "  Otvoreni element - ugradi police na zeljene visine.",
            ]
        else:
            steps += [
                "  Montiraj sarnire i podesi vrata sa fugom 2 mm.",
            ]
        steps += [
            "",
            _line("KORAK 3 - MONTAZA NA ZID"),
            "  Montiraj zidni nosac ili sinju i nivelisi element pre zavrsnog stezanja.",
        ]
        return steps

    if zone == "tall_top":
        n_top_doors = 2 if ("2DOOR" in tid or "DOORS" in tid) else 1
        steps = [
            _line("SASTAVNICA GORNJE POPUNE"),
            f"  Leva bocna ploca: 1 kom  {side_d} x {side_h} mm",
            f"  Desna bocna ploca: 1 kom  {side_d} x {side_h} mm",
            f"  Dno: 1 kom  {inner_w} x {inner_d} mm",
            f"  Gornja ploca: 1 kom  {inner_w} x {inner_d} mm",
            f"  Ledjna ploca: 1 kom  {back_w} x {back_h} mm",
        ]
        if "OPEN" in tid:
            steps += [
                "  Podesiva polica: prema krojnoj listi",
                "  Nosaci police: 4 kom",
            ]
        else:
            steps += [
                f"  Vrata: {n_top_doors} kom  {door_w} x {door_h} mm",
                f"  Sarniri: {n_top_doors * 2} kom",
            ]
        steps += [
            "",
            _line("KORAK 1 - SKLOP POPUNE"),
            "  Sastavi mali korpus i proveri dijagonale pre zatvaranja ledjima.",
            "",
            _line("KORAK 2 - VEZA SA VISOKIM ELEMENTOM"),
            "  Popunu poravnaj sa visokom kolonom ispod i spoji spojnim vijcima kroz bocne stranice.",
        ]
        if "OPEN" in tid:
            steps += [
                "",
                _line("KORAK 3 - POLICA"),
                "  Ugradi policu na zeljenu visinu i proveri ravninu sa okolnim elementima.",
            ]
        else:
            steps += [
                "",
                _line("KORAK 3 - VRATA"),
                "  Montiraj vrata i podesi male fuge prema frontovima visoke kolone ispod.",
            ]
        return steps

    if zone == "tall":
        steps = [
            _line("SASTAVNICA KORPUSA"),
            f"  Leva bocna ploca: 1 kom  {side_d} x {side_h} mm",
            f"  Desna bocna ploca: 1 kom  {side_d} x {side_h} mm",
            f"  Dno: 1 kom  {inner_w} x {inner_d} mm",
            f"  Gornja ploca: 1 kom  {inner_w} x {inner_d} mm",
            f"  Ledjna ploca: 1 kom  {back_w} x {back_h} mm",
            f"  Medjupolica: 2 kom  {inner_w} x {inner_d} mm",
            f"  Noge: 4 kom  h = {foot} mm",
        ]
        if "FRIDGE" in tid:
            if "FREEZER" in tid:
                steps += [
                    f"  Gornji front uredjaja: 1 kom  {door_w} x {int(h * 0.60) - edge} mm",
                    f"  Donji front uredjaja: 1 kom  {door_w} x {int(h * 0.40) - edge} mm",
                    "  Set za vezu frontova: 2 seta",
                ]
            else:
                steps += [
                    f"  Front uredjaja: 1 kom  {door_w} x {door_h} mm",
                    "  Set za vezu fronta: 1 set",
                ]
        elif tid == "TALL_OVEN_MICRO":
            service_front_h = max(120, min(320, int(h * 0.16) - edge))
            steps += [
                f"  Donji servisni front: 1 kom  {door_w} x {service_front_h} mm",
                "  Ugradna mikrotalasna: 1 kom",
                "  Ugradna rerna: 1 kom",
                "  Ventilacioni set / distancer: 1 set",
            ]
        elif tid == "TALL_OVEN":
            service_front_h = max(120, min(360, int(h * 0.18) - edge))
            steps += [
                f"  Donji servisni front: 1 kom  {door_w} x {service_front_h} mm",
                "  Ugradna rerna: 1 kom",
                "  Ventilacioni set / distancer: 1 set",
            ]
        else:
            n_tall_doors = 2 if ("2DOOR" in tid or "DOORS" in tid) else 1
            if "GLASS" in tid:
                steps += [
                    f"  Staklena vrata: {n_tall_doors} kom  {door_w} x {door_h} mm",
                    f"  Sarke za staklo: {n_tall_doors * 2} kom",
                ]
            else:
                steps += [
                    f"  Vrata: {n_tall_doors} kom  {door_w} x {door_h} mm",
                    f"  Sarniri: {n_tall_doors * 2} kom",
                ]
        steps += [
            "",
            _line("KORAK 1 - KORPUS"),
            "  Sastavi dno, gornju plocu, bocne stranice i medjupolice.",
            "",
            _line("KORAK 2 - LEDJA"),
            "  Umetni ledjnu plocu i proveri dijagonale pre konacnog stezanja.",
        ]
        if "FRIDGE" in tid:
            if "FREEZER" in tid:
                steps += [
                    "",
                    _line("KORAK 3 - FRIŽIDER + ZAMRZIVAC"),
                    "  Uvuci uredjaj u gotov korpus i proveri ventilacione zazore.",
                    "  Montiraj gornji i donji front na vrata uredjaja pomocu fabrickog seta za vezu.",
                ]
            else:
                steps += [
                    "",
                    _line("KORAK 3 - UGRADNI FRIZIDER"),
                    "  Uvuci uredjaj u gotov korpus i proveri ventilacione zazore.",
                    "  Front uredjaja montiraj tek nakon nivelacije korpusa i probe otvaranja vrata.",
                ]
        elif "OVEN_MICRO" in tid:
            steps += [
                "",
                _line("KORAK 3 - RERNA + MIKROTALASNA"),
                "  Proveri dve appliance zone i ventilaciju pre unosenja uredjaja.",
                "  Prvo ugradi mikrotalasnu, zatim rernu u donju zonu.",
                "  Donji servisni front montiraj tek nakon probe otvaranja i zazora uredjaja.",
            ]
        elif "OVEN" in tid:
            steps += [
                "",
                _line("KORAK 3 - KOLONA ZA RERNU"),
                "  Proveri visinu appliance zone i pricvrsti rernu prema fabrickom uputstvu.",
                "  Donji servisni front montiraj nakon nivelacije kolone i probe ventilacije.",
            ]
        elif "GLASS" in tid:
            steps += [
                "",
                _line("KORAK 3 - STAKLENA VRATA"),
                "  Montiraj staklena vrata prema sablonu proizvodjaca vitrine.",
            ]
        elif "OPEN" in tid or "PANTRY" in tid:
            steps += [
                "",
                _line("KORAK 3 - POLICE"),
                "  Ugradi police i podesi razmake prema nameni elementa.",
                "  Za ostavu proveri da teret na policama bude ravnomerno rasporedjen.",
            ]
        else:
            steps += [
                "",
                _line("KORAK 3 - VRATA"),
                "  Montiraj sarnire i podesi vrata posle nivelacije korpusa.",
            ]
        steps += [
            "",
            _line("KORAK 4 - POSTAVLJANJE"),
            "  Nivelisi kolonu i obavezno pricvrsti anti-tip set za zid.",
        ]
        return steps

    return [
        "1. Sastavi bocne ploce, dno i gornju plocu.",
        "2. Proveri kvadraturu i umetni ledjnu plocu.",
        "3. Montiraj vrata ili okove prema tipu elementa.",
    ]
