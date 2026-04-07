# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from typing import List


def _line(title: str) -> str:
    return f"-- {title} --"


def _translate_instruction_line(line: str, lang: str = "sr") -> str:
    if str(lang or "sr").lower().strip() != "en":
        return line

    txt = str(line or "")
    exact = {
        "-- PANEL ELEMENT --": "-- PANEL ELEMENT --",
        "-- SUDOPERSKI ELEMENT --": "-- SINK BASE UNIT --",
        "-- SASTAVNICA KORPUSA --": "-- CABINET COMPONENTS --",
        "-- SASTAVNICA GORNJEG ELEMENTA --": "-- WALL CABINET COMPONENTS --",
        "-- SASTAVNICA GORNJE POPUNE --": "-- TOP FILLER UNIT COMPONENTS --",
        "-- SAMOSTOJECA MASINA ZA SUDOVE --": "-- FREESTANDING DISHWASHER --",
        "-- SAMOSTOJECI SPORET --": "-- FREESTANDING RANGE --",
        "-- SAMOSTOJECI FRIZIDER --": "-- FREESTANDING REFRIGERATOR --",
        "-- SASTAVNICA MZS SLOTA --": "-- DISHWASHER OPENING SET --",
        "-- KORAK 1 - PROVERA MERE --": "-- STEP 1 - VERIFY DIMENSIONS --",
        "-- KORAK 2 - POZICIONIRANJE --": "-- STEP 2 - POSITIONING --",
        "-- KORAK 3 - FIKSIRANJE --": "-- STEP 3 - FIXING --",
        "-- KORAK 4 - ZAVRSNA PROVERA --": "-- STEP 4 - FINAL CHECK --",
        "-- KORAK 1 - PRIPREMA OTVORA --": "-- STEP 1 - PREPARE THE OPENING --",
        "-- KORAK 2 - PRIKLJUCCI --": "-- STEP 2 - CONNECTIONS --",
        "-- KORAK 3 - UBACIVANJE MASINE --": "-- STEP 3 - INSTALL THE MACHINE --",
        "-- KORAK 4 - FRONT MZS --": "-- STEP 4 - DISHWASHER FRONT --",
        "-- KORAK 1 - KORPUS --": "-- STEP 1 - CARCASS --",
        "-- KORAK 2 - LEDJA I OTVORI --": "-- STEP 2 - BACK PANEL AND CUT-OUTS --",
        "-- KORAK 3 - VRATA --": "-- STEP 3 - DOORS --",
        "-- KORAK 4 - RADNA PLOCA I SUDOPERA --": "-- STEP 4 - WORKTOP AND SINK --",
        "-- KORAK 1 - BOCNE PLOCE --": "-- STEP 1 - SIDE PANELS --",
        "-- KORAK 2 - DNO I GORNJA PLOCA --": "-- STEP 2 - BOTTOM AND TOP PANEL --",
        "-- KORAK 3 - LEDJNA PLOCA --": "-- STEP 3 - BACK PANEL --",
        "-- KORAK 4 - FIOKE --": "-- STEP 4 - DRAWERS --",
        "-- KORAK 4 - VRATA + FIOKA --": "-- STEP 4 - DOORS + DRAWER --",
        "-- KORAK 4 - SORTIRNIK --": "-- STEP 4 - WASTE SORTER --",
        "-- KORAK 4 - USKI IZVLACNI MODUL --": "-- STEP 4 - NARROW PULL-OUT UNIT --",
        "-- KORAK 4 - KUHINJSKA JEDINICA --": "-- STEP 4 - COOKING UNIT --",
        "-- KORAK 4 - POLICE --": "-- STEP 4 - SHELVES --",
        "-- KORAK 4 - PLOCA ZA KUVANJE --": "-- STEP 4 - HOB --",
        "-- KORAK 4 - UGRADNA RERNA --": "-- STEP 4 - BUILT-IN OVEN --",
        "-- KORAK 5 - NOGE I POZICIONIRANJE --": "-- STEP 5 - LEGS AND POSITIONING --",
        "-- KORAK 2 - VRATA / MEHANIZAM --": "-- STEP 2 - DOORS / MECHANISM --",
        "-- KORAK 3 - MONTAZA NA ZID --": "-- STEP 3 - WALL INSTALLATION --",
        "-- KORAK 1 - SKLOP POPUNE --": "-- STEP 1 - ASSEMBLE THE TOP UNIT --",
        "-- KORAK 2 - VEZA SA VISOKIM ELEMENTOM --": "-- STEP 2 - CONNECT TO THE TALL UNIT --",
        "-- KORAK 3 - POLICA --": "-- STEP 3 - SHELF --",
        "-- KORAK 2 - LEDJA --": "-- STEP 2 - BACK PANEL --",
        "-- KORAK 3 - FRIŽIDER + ZAMRZIVAC --": "-- STEP 3 - FRIDGE + FREEZER --",
        "-- KORAK 3 - UGRADNI FRIZIDER --": "-- STEP 3 - BUILT-IN REFRIGERATOR --",
        "-- KORAK 3 - RERNA + MIKROTALASNA --": "-- STEP 3 - OVEN + MICROWAVE --",
        "-- KORAK 3 - KOLONA ZA RERNU --": "-- STEP 3 - OVEN TOWER --",
        "-- KORAK 3 - STAKLENA VRATA --": "-- STEP 3 - GLASS DOORS --",
        "-- KORAK 4 - POSTAVLJANJE --": "-- STEP 4 - POSITIONING --",
    }
    if txt in exact:
        return exact[txt]
    if txt == "-- KORAK 3 - LEDJNA PLOCA --":
        return "-- KORAK 3 - LE\u0110NA PLO\u010cA --"

    replacements = [
        ("Filer panel", "Filler panel"),
        ("Zavrsna bocna ploca", "End side panel"),
        ("Leva bocna ploca", "Left side panel"),
        ("Desna bocna ploca", "Right side panel"),
        ("Ledjna ploca", "Back panel"),
        ("Gornja ploca", "Top panel"),
        ("Donji servisni front", "Lower service front"),
        ("Gornji front uredjaja", "Upper appliance front"),
        ("Donji front uredjaja", "Lower appliance front"),
        ("Front uredjaja", "Appliance front"),
        ("Front fioke", "Drawer front"),
        ("Frontovi fioka", "Drawer fronts"),
        ("Front uskog modula", "Narrow-unit front"),
        ("Vrata ispod sudopere", "Sink-base doors"),
        ("Vrata (ispod sudopere)", "Doors below sink"),
        ("Vrata (ispod ploče za kuvanje)", "Doors below hob"),
        ("Vrata rerne", "Oven front"),
        ("Vrata", "Doors"),
        ("Staklena vrata", "Glass doors"),
        ("Sarniri", "Hinges"),
        ("Sarke za staklo", "Glass-door hinges"),
        ("Klizaci za fioke", "Drawer runners"),
        ("Klizaci za fioku", "Drawer runners"),
        ("klizace", "runners"),
        ("klizac", "runner"),
        ("Sanduk fioke", "Drawer box"),
        ("Ugradna rerna", "Built-in oven"),
        ("Ugradna mikrotalasna", "Built-in microwave"),
        ("Ploca za kuvanje", "Hob"),
        ("Ugradna masina", "Built-in dishwasher"),
        ("Montazni set fronta", "Front mounting kit"),
        ("Vezna letva", "Cross rail"),
        ("Nosac radne ploce", "Worktop support rail"),
        ("Noge", "Legs"),
        ("Dno", "Bottom panel"),
        ("Medjupolica", "Intermediate shelf"),
        ("Podesive police", "Adjustable shelves"),
        ("Podesiva polica", "Adjustable shelf"),
        ("Nosaci polica", "Shelf supports"),
        ("Nosaci police", "Shelf supports"),
        ("Uski izvlacni mehanizam", "Narrow pull-out mechanism"),
        ("Korpe / nosaci", "Baskets / supports"),
        ("Lift-up mehanizam", "Lift-up mechanism"),
        ("Set za vezu fronta", "Front connection kit"),
        ("Set za vezu frontova", "Front connection kits"),
        ("Ventilacioni set / distancer", "Ventilation spacer kit"),
        ("kom", "pcs"),
    ]
    for src, dst in replacements:
        txt = txt.replace(src, dst)

    sentences = {
        "  Ovaj uredjaj nema korpus ni front u krojnoj listi.": "  This appliance has no carcass or front in the cut list.",
        "  Povezi vodu, odvod i struju prema uputstvu proizvodjaca.": "  Connect water, drain and power according to the manufacturer's instructions.",
        "  Nakon nivelacije proveri otvaranje vrata i pristup instalacijama.": "  After levelling, check door clearance and access to services.",
        "  Posle nivelacije proveri da vrata rerne i ploca imaju slobodan prostor.": "  After levelling, make sure the oven door and hob area have adequate clearance.",
        "  Ne zatvaraj gornji i zadnji vazdusni prostor maskama bez ventilacije.": "  Do not close the top or rear air gap with unventilated trim panels.",
        "  Nakon postavljanja proveri otvaranje vrata i pristup uticnici.": "  After installation, check door opening and socket access.",
        "  Ovaj modul nema sopstveni korpus; bocne strane daju susedni elementi.": "  This module has no dedicated carcass; the adjacent cabinets form its sides.",
        "  Creva i kabl ne smeju biti prignjeceni iza uredjaja.": "  Hoses and the power cable must not be pinched behind the appliance.",
        "  Uvuci masinu u nisu bez sile i iznivelisi je preko fabrickih nozica.": "  Slide the machine into the opening without force and level it using the factory feet.",
        "  Front pricvrsti na vrata masine pomocu fabrickog sablona i montaznog seta.": "  Fix the front to the dishwasher door using the factory template and mounting kit.",
        "  Ostaviti jednake fuge 2-3 mm prema susednim frontovima.": "  Leave even 2-3 mm reveals relative to adjacent fronts.",
        "  Probaj otvaranje vrata i rad masine pre zatvaranja sokle.": "  Test door movement and machine operation before fitting the plinth.",
        "  Sastavi bocne stranice i dno kao standardni bazni korpus.": "  Assemble the side panels and bottom as a standard base carcass.",
        "  Gornja puna ploca se ne ugradjuje preko celog otvora zbog sudopere i instalacija.": "  Do not fit a full top panel across the entire opening because of the sink and services.",
        "  Otvor pravi tek kada proveris stvarnu poziciju instalacija na zidu.": "  Cut the opening only after checking the actual service positions on site.",
        "  Montiraj vrata i podesi fuge 2-3 mm da se nesmetano otvaraju ispod sudopere.": "  Fit the doors and set 2-3 mm reveals so they open freely below the sink.",
        "  Na radnoj ploci iscrtaj otvor prema sablonu sudopere.": "  Mark the cut-out in the worktop using the sink template.",
        "  Isprskanu ivicu otvora zastiti od vlage pre montaze sudopere.": "  Seal the exposed cut edge against moisture before installing the sink.",
        "  Pusti vodu i proveri da li sifon, slavina i spojevi cure.": "  Run water and check the trap, tap and all connections for leaks.",
        "  Izbusiti rupe za konfirmate i zleb za ledjnu plocu.": "  Drill the confirmat holes and cut the groove for the back panel.",
        "  Spoji dno i gornju plocu izmedju bocnih stranica.": "  Connect the bottom and top panel between the side panels.",
        "  Umetni ledjnu plocu i proveri dijagonale.": "  Insert the back panel and verify the diagonals.",
        "  Montiraj klizace, sastavi sanduke fioka i podesi frontove.": "  Fit the runners, assemble the drawer boxes and align the fronts.",
        "  Montiraj vrata, zatim klizac i front fioke.": "  Fit the doors first, then the runner and drawer front.",
        "  Montiraj izvlacni mehanizam i pricvrsti front sortirnika.": "  Install the pull-out mechanism and attach the sorter front.",
        "  Montiraj cargo mehanizam i pricvrsti front na nosac mehanizma.": "  Install the cargo mechanism and fix the front to the mechanism carrier.",
        "  Uvuci rernu u korpus i isezi otvor u radnoj ploci prema sablonu ploce.": "  Slide the oven into the carcass and cut the hob opening in the worktop using the manufacturer's template.",
        "  Lazni front montiraj tek nakon probe zazora oko rerne.": "  Fit the dummy front only after checking the clearance around the oven.",
        "  Ugradi nosace polica i postavi police na zeljene visine.": "  Fit the shelf supports and place the shelves at the required heights.",
        "  Proveri da su sve police u libeli pre opterecenja.": "  Make sure all shelves are level before loading them.",
        "  Iseci otvor u radnoj ploci prema sablonu ploce i montiraj vrata ispod.": "  Cut the hob opening in the worktop using the template and fit the doors below.",
        "  Ostaviti otvor za kabl i pricvrstiti rernu prema uputstvu proizvodjaca.": "  Leave a cable opening and secure the oven according to the manufacturer's instructions.",
        "  Montiraj sarnire, okaci vrata i podesi fuge 2 mm.": "  Fit the hinges, hang the doors and set 2 mm reveals.",
        "  Montiraj noge, nivelisi element i tek onda montiraj radnu plocu.": "  Fit the legs, level the cabinet, and only then install the worktop.",
        "  Sastavi okvir i umetni ledjnu plocu u zlebove.": "  Assemble the carcass and insert the back panel into the grooves.",
        "  Element je kuciste za napu - bez vrata i bez polica.": "  This is a hood housing unit, without doors or shelves.",
        "  Ostaviti otvor za odvod prema sablonu proizvodjaca.": "  Leave the duct opening according to the manufacturer's template.",
        "  Element je otvorena nisa za mikrotalasnu - bez vrata.": "  This is an open microwave niche, without doors.",
        "  Ostaviti otvor za kabl i ventilacioni razmak.": "  Leave a cable opening and the required ventilation gap.",
        "  Ugaoni zidni element zahteva proveru stvarnog ugla zida pre busenja.": "  A corner wall unit requires the actual wall angle to be checked before drilling.",
        "  Montiraj sarke za staklena vrata prema sablonu proizvodjaca.": "  Fit the glass-door hinges using the manufacturer's template.",
        "  Montiraj lift-up mehanizam i podesi snagu opruge prema masi fronta.": "  Install the lift-up mechanism and set the spring force to match the front weight.",
        "  Otvoreni element - ugradi police na zeljene visine.": "  Open unit: fit the shelves at the desired heights.",
        "  Montiraj sarnire i podesi vrata sa fugom 2 mm.": "  Install the hinges and set the doors with a 2 mm reveal.",
        "  Montiraj zidni nosac ili sinju i nivelisi element pre zavrsnog stezanja.": "  Install the wall brackets or hanging rail and level the cabinet before final tightening.",
        "  Sastavi mali korpus i proveri dijagonale pre zatvaranja ledjima.": "  Assemble the small carcass and check the diagonals before fitting the back panel.",
        "  Popunu poravnaj sa visokom kolonom ispod i spoji spojnim vijcima kroz bocne stranice.": "  Align the top filler with the tall unit below and connect them with cabinet connector screws through the side panels.",
        "  Ugradi policu na zeljenu visinu i proveri ravninu sa okolnim elementima.": "  Install the shelf at the required height and check alignment with adjacent units.",
        "  Montiraj vrata i podesi male fuge prema frontovima visoke kolone ispod.": "  Fit the doors and set consistent small reveals relative to the tall unit fronts below.",
        "  Sastavi dno, gornju plocu, bocne stranice i medjupolice.": "  Assemble the bottom, top, side panels and intermediate shelves.",
        "  Umetni ledjnu plocu i proveri dijagonale pre konacnog stezanja.": "  Insert the back panel and verify the diagonals before final tightening.",
        "  Uvuci uredjaj u gotov korpus i proveri ventilacione zazore.": "  Slide the appliance into the finished carcass and verify all ventilation clearances.",
        "  Montiraj gornji i donji front na vrata uredjaja pomocu fabrickog seta za vezu.": "  Mount the upper and lower fronts to the appliance doors using the factory connection kit.",
        "  Front uredjaja montiraj tek nakon nivelacije korpusa i probe otvaranja vrata.": "  Fit the appliance front only after levelling the carcass and testing the door opening.",
        "  Proveri dve appliance zone i ventilaciju pre unosenja uredjaja.": "  Check both appliance zones and ventilation paths before inserting the appliances.",
        "  Prvo ugradi mikrotalasnu, zatim rernu u donju zonu.": "  Install the microwave first, then the oven in the lower zone.",
        "  Donji servisni front montiraj tek nakon probe otvaranja i zazora uredjaja.": "  Fit the lower service front only after checking door opening and appliance clearances.",
        "  Proveri visinu appliance zone i pricvrsti rernu prema fabrickom uputstvu.": "  Verify the appliance opening height and secure the oven according to the factory instructions.",
        "  Donji servisni front montiraj nakon nivelacije kolone i probe ventilacije.": "  Fit the lower service front after levelling the tower and checking ventilation.",
        "  Montiraj staklena vrata prema sablonu proizvodjaca vitrine.": "  Fit the glass doors using the display-unit manufacturer's template.",
        "  Ugradi police i podesi razmake prema nameni elementa.": "  Install the shelves and set the spacing to suit the intended use.",
        "  Za ostavu proveri da teret na policama bude ravnomerno rasporedjen.": "  For pantry units, make sure the load is distributed evenly across the shelves.",
        "  Montiraj sarnire i podesi vrata posle nivelacije korpusa.": "  Fit the hinges and adjust the doors after levelling the carcass.",
        "  Nivelisi kolonu i obavezno pricvrsti anti-tip set za zid.": "  Level the tall unit and always secure the anti-tip kit to the wall.",
        "1. Sastavi bocne ploce, dno i gornju plocu.": "1. Assemble the side panels, bottom and top panel.",
        "2. Proveri kvadraturu i umetni ledjnu plocu.": "2. Check squareness and insert the back panel.",
        "3. Montiraj vrata ili okove prema tipu elementa.": "3. Install the doors or hardware according to the unit type.",
        "  Proveri stvarnu sirinu otvora ili zavrsne stranice pre busenja.": "  Check the actual opening width or end panel width before drilling.",
        "  Ostaviti 2-3 mm rezerve ako panel ide uz neravan zid.": "  Leave a 2-3 mm allowance if the panel meets an uneven wall.",
        "  Privremeno namesti panel stegama uz susedni korpus ili zidnu letvu.": "  Temporarily clamp the panel against the adjacent cabinet or wall batten.",
        "  Prednja ivica mora biti u ravni sa frontovima kuhinje.": "  The front edge must align with the kitchen fronts.",
        "  Pricvrsti panel vijcima 4x30 mm sa unutrasnje strane susednog elementa.": "  Fix the panel with 4x30 mm screws from inside the adjacent cabinet.",
        "  Ako ide uz zid, po potrebi koristi pomocnu letvu ili ugaonik.": "  If it finishes against a wall, use a helper batten or angle bracket if needed.",
        "  Proveri da panel ne viri ispred fronta i da nema uvijanja.": "  Make sure the panel does not project beyond the fronts and is not twisted.",
        "  Na ledjnoj ploci obelezi i izrezi otvor za dovod, odvod i eventualnu uticnicu.": "  Mark and cut the back panel for water supply, drain and any required socket.",
        "  Povezi struju ili gas prema pravilima proizvodjaca i lokalnim propisima.": "  Connect electricity or gas according to the manufacturer's instructions and local regulations.",
        "  Proveri cistu sirinu nise i dubinu pre unosenja uredjaja.": "  Check the clear niche width and depth before inserting the appliance.",
        "  Veznu letvu montiraj ispod radne ploce izmedju susednih korpusa.": "  Install the cross rail below the worktop between the adjacent cabinets.",
        "  Dovedi struju, vodu i odvod prema uputstvu proizvodjaca.": "  Bring in power, water and drain connections according to the manufacturer's instructions.",
        "  Gornja puna ploca se ne ugradjuje preko celog otvora, da ostane prostor za sudoperu i instalacije.": "  Do not fit a full top panel across the entire opening so there is room for the sink and services.",
        "  Na ledjnoj ploci obelezi otvore za dovod vode, odvod i eventualnu uticnicu.": "  Mark the back panel for the water supply, drain and any required socket.",
        "  Otvore iseci tek kada proveris stvarnu poziciju instalacija na zidu, ne samo po proceni.": "  Cut the openings only after verifying the actual service positions on the wall, not just by estimate.",
        "  Proveri da sifon i cevi ne udaraju u vrata pri zatvaranju.": "  Check that the trap and pipes do not hit the doors when closing.",
        "  Na radnoj ploci iscrtaj otvor prema sablonu sudopere i proveri poziciju pre secenja.": "  Mark the sink cut-out in the worktop using the template and verify the position before cutting.",
        "  Isecenu ivicu otvora zastiti od vlage pre montaze sudopere.": "  Protect the cut edge of the opening from moisture before mounting the sink.",
        "  Pusti vodu i proveri da li sifon, slavina i svi spojevi cure.": "  Run water and check whether the trap, tap and all connections leak.",
        "  Tek kada je sve suvo i bez curenja zatvori element i nastavi na sledeci modul.": "  Only when everything is dry and leak-free should you close the unit and continue to the next module.",
    }
    if txt in sentences:
        return sentences[txt]

    txt = re.sub(r"^\s*Debljina panela:", "  Panel thickness:", txt)
    txt = re.sub(r"^\s*Kantovanje:", "  Edgebanding:", txt)
    txt = re.sub(r"^\s*Obezbedi ravnu nisu sirine", "  Provide a level opening, width", txt)
    txt = re.sub(r"^\s*Obezbedi ravnu poziciju sirine", "  Provide a level opening, width", txt)
    txt = re.sub(r"^\s*Obezbedi poziciju sirine", "  Provide an opening, width", txt)
    txt = txt.replace("ledjima", "the back panel")
    return txt


def _polish_instruction_line_sr(line: str) -> str:
    txt = str(line or "")
    exact = {
        "-- SASTAVNICA KORPUSA --": "-- SPISAK DELOVA KORPUSA --",
        "-- SASTAVNICA GORNJEG ELEMENTA --": "-- SPISAK DELOVA GORNJEG ELEMENTA --",
        "-- SASTAVNICA GORNJE POPUNE --": "-- SPISAK DELOVA GORNJE POPUNE --",
        "-- SASTAVNICA MZS SLOTA --": "-- SPISAK DELOVA ZA MZS NIŠU --",
        "-- PANEL ELEMENT --": "-- PANEL ELEMENT --",
        "-- SUDOPERSKI ELEMENT --": "-- SUDOPERSKI ELEMENT --",
        "-- KORAK 1 - BOCNE PLOCE --": "-- KORAK 1 - BOČNE PLOČE --",
        "-- KORAK 2 - DNO I GORNJA PLOCA --": "-- KORAK 2 - DNO I GORNJA PLOČA --",
        "-- KORAK 2 - LEDJA I OTVORI --": "-- KORAK 2 - LEĐA I OTVORI --",
        "-- KORAK 3 - MONTAZA NA ZID --": "-- KORAK 3 - MONTAŽA NA ZID --",
        "-- KORAK 4 - RADNA PLOCA I SUDOPERA --": "-- KORAK 4 - RADNA PLOČA I SUDOPERA --",
        "-- KORAK 4 - ZAVRSNA PROVERA --": "-- KORAK 4 - ZAVRŠNA PROVERA --",
        "-- KORAK 5 - ZAVRSNA PROVERA --": "-- KORAK 5 - ZAVRŠNA PROVERA --",
    }
    if txt in exact:
        return exact[txt]

    replacements = [
        ("  Izbusiti ", "  Izbušite "),
        ("  Spoji ", "  Spojite "),
        ("  Umetni ", "  Umetnite "),
        ("  Montiraj ", "  Montirajte "),
        ("  Proveri ", "  Proverite "),
        ("  Ostaviti ", "  Ostavite "),
        ("  Uvuci ", "  Uvucite "),
        ("  Povezi ", "  Povežite "),
        ("  Dovedi ", "  Dovedite "),
        ("  Sastavi ", "  Sastavite "),
        ("  Ugradi ", "  Ugradite "),
        ("  Popunu poravnaj ", "  Popunu poravnajte "),
        ("  Front pricvrsti ", "  Front pričvrstite "),
        ("  Front uredjaja montiraj ", "  Front uređaja montirajte "),
        ("  Dno", "  Donja ploča"),
        ("  Gornja ploca", "  Gornja ploča"),
        ("  Ledjna ploca", "  Leđna ploča"),
        ("  Leva bocna ploca", "  Leva bočna ploča"),
        ("  Desna bocna ploca", "  Desna bočna ploča"),
        ("  Nosac radne ploce", "  Nosač radne ploče"),
        ("  Sarniri", "  Šarke"),
        ("  Klizaci", "  Klizači"),
        ("  Ugradna masina", "  Ugradna mašina"),
        ("  Montazni set", "  Montažni set"),
        ("  Na radnoj ploci iscrtaj otvor prema sablonu sudopere.", "  Na radnoj ploči obeležite otvor prema šablonu sudopere."),
        ("  Isprskanu ivicu otvora zastiti od vlage pre montaze sudopere.", "  Zaštitite isečenu ivicu otvora od vlage pre montaže sudopere."),
        ("  Pusti vodu i proveri da li sifon, slavina i spojevi cure.", "  Pustite vodu i proverite da li sifon, slavina i spojevi cure."),
        ("  Ovaj modul nema sopstveni korpus; bocne strane daju susedni elementi.", "  Ovaj modul nema sopstveni korpus; bočne strane formiraju susedni elementi."),
        ("  Proveri cistu sirinu nise i dubinu pre unosenja uredjaja.", "  Proverite čistu širinu niše i dubinu pre unošenja uređaja."),
        ("  Veznu letvu montiraj ispod radne ploce izmedju susednih korpusa.", "  Veznu letvu montirajte ispod radne ploče između susednih korpusa."),
        ("  Dovedi struju, vodu i odvod prema uputstvu proizvodjaca.", "  Dovedite struju, vodu i odvod prema uputstvu proizvođača."),
        ("  Creva i kabl ne smeju biti prignjeceni iza uredjaja.", "  Creva i kabl ne smeju biti prignječeni iza uređaja."),
        ("  Uvuci masinu u nisu bez sile i iznivelisi je preko fabrickih nozica.", "  Uvucite mašinu u nišu bez sile i iznivelisite je preko fabričkih nožica."),
        ("  Ostaviti jednake fuge 2-3 mm prema susednim frontovima.", "  Ostavite jednake fuge od 2-3 mm prema susednim frontovima."),
        ("  Probaj otvaranje vrata i rad masine pre zatvaranja sokle.", "  Proverite otvaranje vrata i rad mašine pre zatvaranja sokle."),
    ]
    for src, dst in replacements:
        txt = txt.replace(src, dst)
    extra_sr_replacements = [
        ("  Sastavi bocne stranice i dno kao standardni bazni korpus.", "  Sastavite bo\u010dne stranice i dno kao standardni bazni korpus."),
        ("  Gornja puna ploca se ne ugradjuje preko celog otvora, da ostane prostor za sudoperu i instalacije.", "  Gornja puna plo\u010da se ne ugra\u0111uje preko celog otvora, da ostane prostor za sudoperu i instalacije."),
        ("  Na ledjnoj ploci obelezi otvore za dovod vode, odvod i eventualnu uticnicu.", "  Na le\u0111noj plo\u010di obele\u017eite otvore za dovod vode, odvod i eventualnu uti\u010dnicu."),
        ("  Otvore iseci tek kada proveris stvarnu poziciju instalacija na zidu, ne samo po proceni.", "  Otvore isecite tek kada proverite stvarnu poziciju instalacija na zidu, ne samo po proceni."),
        ("  Montiraj vrata i podesi fuge 2-3 mm da se nesmetano otvaraju ispod sudopere.", "  Montirajte vrata i podesite fuge od 2-3 mm da se nesmetano otvaraju ispod sudopere."),
        ("  Proveri da sifon i cevi ne udaraju u vrata pri zatvaranju.", "  Proverite da sifon i cevi ne udaraju u vrata pri zatvaranju."),
        ("  Na radnoj ploci iscrtaj otvor prema sablonu sudopere i proveri poziciju pre secenja.", "  Na radnoj plo\u010di obele\u017eite otvor prema \u0161ablonu sudopere i proverite poziciju pre se\u010denja."),
        ("  Isecenu ivicu otvora zastiti od vlage pre montaze sudopere.", "  Ise\u010denu ivicu otvora za\u0161titite od vlage pre monta\u017ee sudopere."),
        ("  Pusti vodu i proveri da li sifon, slavina i svi spojevi cure.", "  Pustite vodu i proverite da li sifon, slavina i svi spojevi cure."),
        ("  Tek kada je sve suvo i bez curenja zatvori element i nastavi na sledeci modul.", "  Tek kada je sve suvo i bez curenja zatvorite element i nastavite na slede\u0107i modul."),
        ("  Uzmi levu i desnu bocnu plocu i postavi ih uspravno tako da kantovane prednje ivice gledaju napred.", "  Uzmite levu i desnu bo\u010dnu plo\u010du i postavite ih uspravno tako da kantovane prednje ivice gledaju napred."),
        ("  Umetni dno izmedju bocnih stranica i spoji ga prema busenjima.", "  Umetnite dno izme\u0111u bo\u010dnih stranica i spojite ga prema bu\u0161enjima."),
        ("  Zatim postavi gornju plocu i proveri da korpus ostane ravan.", "  Zatim postavite gornju plo\u010du i proverite da korpus ostane ravan."),
        ("  Umetni ledjnu plocu na zadnju stranu elementa.", "  Umetnite le\u0111nu plo\u010du na zadnju stranu elementa."),
        ("  Pre konacnog stezanja proveri dijagonale da element bude pod pravim uglom.", "  Pre kona\u010dnog stezanja proverite dijagonale da element bude pod pravim uglom."),
        ("  Prvo proveri da li rerna slobodno ulazi u otvor korpusa i da li ima prostora za ventilaciju.", "  Prvo proverite da li rerna slobodno ulazi u otvor korpusa i da li ima prostora za ventilaciju."),
        ("  Zatim isezi otvor u radnoj ploci prema sablonu ploce za kuvanje.", "  Zatim isecite otvor u radnoj plo\u010di prema \u0161ablonu plo\u010de za kuvanje."),
        ("  Lazni front ili front fioke montiraj tek nakon probe zazora oko rerne i vrata rerne.", "  La\u017eni front ili front fioke montirajte tek nakon probe zazora oko rerne i vrata rerne."),
        ("  Montiraj noge ili stopice, zatim nivelisi element na mestu ugradnje.", "  Montirajte noge ili stopice, zatim niveli\u0161ite element na mestu ugradnje."),
        ("  Tek kada je korpus ravan i stabilan montiraj radnu plocu ili nastavi na sledeci element.", "  Tek kada je korpus ravan i stabilan montirajte radnu plo\u010du ili nastavite na slede\u0107i element."),
        ("  Montirajte vrata i podesi fuge 2-3 mm da se nesmetano otvaraju ispod sudopere.", "  Montirajte vrata i podesite fuge od 2-3 mm da se nesmetano otvaraju ispod sudopere."),
        ("  Izbu\u0161ite rupe za konfirmate i zleb za ledjnu plocu.", "  Izbu\u0161ite rupe za konfirmate i \u017eleb za le\u0111nu plo\u010du."),
        ("  Umetnite dno izmedju bocnih stranica i spoji ga prema busenjima.", "  Umetnite dno izme\u0111u bo\u010dnih stranica i spojite ga prema bu\u0161enjima."),
        ("  Umetnite ledjnu plocu na zadnju stranu elementa.", "  Umetnite le\u0111nu plo\u010du na zadnju stranu elementa."),
        ("  Montirajte noge ili stopice, zatim nivelisi element na mestu ugradnje.", "  Montirajte noge ili stopice, zatim niveli\u0161ite element na mestu ugradnje."),
    ]
    for src, dst in extra_sr_replacements:
        txt = txt.replace(src, dst)
    txt = txt.replace("-- KORAK 3 - LEDJNA PLOCA --", "-- KORAK 3 - LE\u0110NA PLO\u010cA --")
    txt = txt.replace("  Montirajte sarnire, okaci vrata i podesi fuge 2 mm.", "  Montirajte \u0161arke, oka\u010dite vrata i podesite fuge od 2 mm.")
    txt = txt.replace("bocne stranice", "bočne stranice")
    txt = txt.replace("bocnu stranicu", "bočnu stranicu")
    txt = txt.replace("bocne ploce", "bočne ploče")
    txt = txt.replace("gornju plocu", "gornju ploču")
    txt = txt.replace("Gornja ploca", "Gornja ploča")
    txt = txt.replace("izmedju", "između")
    txt = txt.replace("Pre sledeceg koraka", "Pre sledećeg koraka")
    txt = txt.replace("busenjima", "bušenjima")
    txt = txt.replace("okaci vrata", "okači vrata")
    txt = txt.replace("Obelezi tacnu visinu", "Obeležite tačnu visinu")
    txt = txt.replace("nosac ili sinu", "nosač ili šinu")
    txt = txt.replace("Pre zavrsnog stezanja", "Pre završnog stezanja")
    txt = txt.replace("cvrsto vezan", "čvrsto vezan")
    txt = txt.replace("sledeci zidni", "sledeći zidni")
    txt = txt.replace("sledeci element", "sledeći element")
    txt = txt.replace("sledeci modul", "sledeći modul")
    txt = txt.replace("Sastavi bocne", "Sastavite bočne")
    txt = txt.replace("Nosac radne ploce", "Nosač radne ploče")
    txt = txt.replace("radne ploce", "radne ploče")
    txt = txt.replace("ledjnu plocu", "leđnu ploču")
    txt = txt.replace("ledjnoj ploci", "leđnoj ploči")
    txt = txt.replace("ledjna ploca", "leđna ploča")
    txt = txt.replace("Ledjna ploca", "Leđna ploča")
    return txt


def _polish_instruction_line_en(line: str) -> str:
    txt = str(line or "")
    exact = {
        "-- CABINET COMPONENTS --": "-- BASE UNIT PARTS LIST --",
        "-- WALL CABINET COMPONENTS --": "-- WALL UNIT PARTS LIST --",
        "-- TOP FILLER UNIT COMPONENTS --": "-- TOP FILLER PARTS LIST --",
        "-- DISHWASHER OPENING SET --": "-- DISHWASHER OPENING PARTS LIST --",
    }
    if txt in exact:
        return exact[txt]

    replacements = [
        ("  Bottom panel", "  Bottom panel"),
        ("  Top panel", "  Top panel"),
        ("  Back panel", "  Back panel"),
        ("  Fix the front", "  Attach the front"),
        ("  Test door movement and machine operation", "  Check door movement and machine operation"),
        ("  Mark the cut-out", "  Mark the cut-out"),
        ("  Seal the exposed cut edge", "  Protect the exposed cut edge"),
        ("  This module has no dedicated carcass; the adjacent cabinets form its sides.", "  This module has no dedicated carcass; the adjacent cabinets form its side support."),
    ]
    for src, dst in replacements:
        txt = txt.replace(src, dst)
    return txt


def _render_instruction_line(line: str, lang: str = "sr") -> str:
    _lang = str(lang or "sr").lower().strip()
    if _lang == "en":
        return _polish_instruction_line_en(_translate_instruction_line(line, "en"))
    return _polish_instruction_line_sr(line)


def assembly_instructions(
    tid: str,
    zone: str,
    m: dict | None = None,
    kitchen: dict | None = None,
    lang: str = "sr",
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
        return [_render_instruction_line(line, lang) for line in [
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
        ]]

    if tid == "BASE_DISHWASHER_FREESTANDING":
        return [_render_instruction_line(line, lang) for line in [
            _line("SAMOSTOJECA MASINA ZA SUDOVE"),
            "  Ovaj uredjaj nema korpus ni front u krojnoj listi.",
            f"  Obezbedi ravnu nisu sirine {w} mm i dubine najmanje {d} mm.",
            "  Povezi vodu, odvod i struju prema uputstvu proizvodjaca.",
            "  Nakon nivelacije proveri otvaranje vrata i pristup instalacijama.",
        ]]

    if tid == "BASE_OVEN_HOB_FREESTANDING":
        return [_render_instruction_line(line, lang) for line in [
            _line("SAMOSTOJECI SPORET"),
            "  Ovaj uredjaj nema korpus ni front u krojnoj listi.",
            f"  Obezbedi ravnu poziciju sirine {w} mm i dubine najmanje {d} mm.",
            "  Povezi struju ili gas prema pravilima proizvodjaca i lokalnim propisima.",
            "  Posle nivelacije proveri da vrata rerne i ploca imaju slobodan prostor.",
        ]]

    if tid == "TALL_FRIDGE_FREESTANDING":
        return [_render_instruction_line(line, lang) for line in [
            _line("SAMOSTOJECI FRIZIDER"),
            "  Ovaj uredjaj nema korpus ni front u krojnoj listi.",
            f"  Obezbedi poziciju sirine {w} mm, dubine najmanje {d} mm i ventilacioni razmak po uputstvu proizvodjaca.",
            "  Ne zatvaraj gornji i zadnji vazdusni prostor maskama bez ventilacije.",
            "  Nakon postavljanja proveri otvaranje vrata i pristup uticnici.",
        ]]

    if zone == "base":
        if tid == "BASE_DISHWASHER":
            return [_render_instruction_line(line, lang) for line in [
                _line("SASTAVNICA MZS SLOTA"),
                f"  Vezna letva: 1 kom  {w} x 100 mm",
                f"  Front MZS: 1 kom  {door_w} x {door_h} mm",
                "  Ugradna masina: 1 kom",
                "  Montazni set fronta: 1 set",
                "",
                _line("KORAK 1 - PRIPREMA OTVORA"),
                "  Ovaj modul nema sopstveni korpus; bocne strane daju susedni elementi.",
                "  Prvo proveri cistu sirinu i dubinu nise, bez merenja preko frontova ili rucki.",
                "  Veznu letvu montiraj ispod radne ploce izmedju susednih korpusa, tako da ne smeta telu masine.",
                "",
                _line("KORAK 2 - PRIKLJUCCI"),
                "  Pre ubacivanja masine pripremi struju, vodu i odvod prema uputstvu proizvodjaca.",
                "  Proveri da creva i kabl mogu da prodju bez savijanja i prignjecenja iza uredjaja.",
                "",
                _line("KORAK 3 - UBACIVANJE MASINE"),
                "  Uvuci masinu u nisu bez sile i zaustavi je tako da prednja ivica bude u ravni sa susednim frontovima.",
                "  Iznivelisi masinu preko fabrickih nozica pre bilo kakvog pricvrscivanja fronta.",
                "",
                _line("KORAK 4 - FRONT MZS"),
                "  Front pricvrsti na vrata masine pomocu fabrickog sablona i montaznog seta iz uredjaja.",
                "  Podesi da gornja ivica fronta bude u ravni sa susednim frontovima i ostavi jednake fuge 2-3 mm.",
                "",
                _line("KORAK 5 - ZAVRSNA PROVERA"),
                "  Probaj otvaranje vrata do kraja i proveri da front nigde ne kaci.",
                "  Ukljuci probni rad masine pre zatvaranja sokle.",
            ]]

        if "SINK" in tid:
            return [_render_instruction_line(line, lang) for line in [
                _line("SUDOPERSKI ELEMENT"),
                f"  Leva bocna ploca: 1 kom  {side_d} x {side_h} mm",
                f"  Desna bocna ploca: 1 kom  {side_d} x {side_h} mm",
                f"  Dno: 1 kom  {inner_w} x {inner_d} mm",
                f"  Ledjna ploca: 1 kom  {back_w} x {back_h} mm",
                f"  Vrata ispod sudopere: {n_doors} kom  {door_w} x {door_h} mm",
                "",
                _line("KORAK 1 - KORPUS"),
                "  Sastavi bocne stranice i dno kao standardni bazni korpus.",
                "  Gornja puna ploca se ne ugradjuje preko celog otvora, da ostane prostor za sudoperu i instalacije.",
                "",
                _line("KORAK 2 - LEDJA I OTVORI"),
                "  Na ledjnoj ploci obelezi otvore za dovod vode, odvod i eventualnu uticnicu.",
                "  Otvore iseci tek kada proveris stvarnu poziciju instalacija na zidu, ne samo po proceni.",
                "",
                _line("KORAK 3 - VRATA"),
                "  Montiraj vrata i podesi fuge 2-3 mm da se nesmetano otvaraju ispod sudopere.",
                "  Proveri da sifon i cevi ne udaraju u vrata pri zatvaranju.",
                "",
                _line("KORAK 4 - RADNA PLOCA I SUDOPERA"),
                "  Na radnoj ploci iscrtaj otvor prema sablonu sudopere i proveri poziciju pre secenja.",
                "  Isecenu ivicu otvora zastiti od vlage pre montaze sudopere.",
                "",
                _line("KORAK 5 - ZAVRSNA PROVERA"),
                "  Pusti vodu i proveri da li sifon, slavina i svi spojevi cure.",
                "  Tek kada je sve suvo i bez curenja zatvori element i nastavi na sledeci modul.",
            ]]

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
            "  Uzmi levu i desnu bocnu plocu i postavi ih uspravno tako da kantovane prednje ivice gledaju napred.",
            "  Izbusiti rupe za konfirmate i zleb za ledjnu plocu.",
            "",
            _line("KORAK 2 - DNO I GORNJA PLOCA"),
            "  Umetni dno izmedju bocnih stranica i spoji ga prema busenjima.",
            "  Zatim postavi gornju plocu i proveri da korpus ostane ravan.",
            "",
            _line("KORAK 3 - LEDJNA PLOCA"),
            "  Umetni ledjnu plocu na zadnju stranu elementa.",
            "  Pre konacnog stezanja proveri dijagonale da element bude pod pravim uglom.",
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
                "  Prvo proveri da li rerna slobodno ulazi u otvor korpusa i da li ima prostora za ventilaciju.",
                "  Zatim isezi otvor u radnoj ploci prema sablonu ploce za kuvanje.",
                "  Lazni front ili front fioke montiraj tek nakon probe zazora oko rerne i vrata rerne.",
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
            "  Montiraj noge ili stopice, zatim nivelisi element na mestu ugradnje.",
            "  Tek kada je korpus ravan i stabilan montiraj radnu plocu ili nastavi na sledeci element.",
        ]
        return [_render_instruction_line(line, lang) for line in steps]

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
            "  Uzmi levu i desnu bocnu stranicu i postavi ih uspravno tako da prednje ivice gledaju ka napred.",
            "  Umetni dno i gornju plocu izmedju bocnih stranica i spoji ih prema busenjima.",
            "  Pre sledeceg koraka proveri da korpus stoji ravno i da nigde nije uvijen.",
            "",
            _line("KORAK 2 - VRATA / MEHANIZAM"),
        ]
        if "HOOD" in tid:
            steps += [
                "  Ovo je kuciste za napu, zato nema vrata ni police.",
                "  Pre montaze ostavi otvor za odvod prema sablonu proizvodjaca nape.",
            ]
        elif "MICRO" in tid:
            steps += [
                "  Ovo je otvorena nisa za mikrotalasnu, zato nema vrata.",
                "  Ostaviti otvor za kabl i obavezan ventilacioni razmak oko uredjaja.",
            ]
        elif "CORNER" in tid:
            steps += [
                "  Pre busenja proveri stvarni ugao zida, jer ugaoni elementi tesko prastaju odstupanja.",
            ]
        elif "GLASS" in tid:
            steps += [
                "  Montiraj sarke za staklena vrata prema sablonu proizvodjaca i proveri da staklo ne dodiruje korpus.",
            ]
        elif "LIFTUP" in tid:
            steps += [
                "  Montiraj lift-up mehanizam i podesi snagu opruge prema tezini fronta.",
                "  Front mora da se otvara glatko i da ne pada sam od sebe.",
            ]
        elif "OPEN" in tid:
            steps += [
                "  Ovo je otvoreni element, pa sada ugradi police na zeljene visine.",
            ]
        else:
            steps += [
                "  Montiraj šarke, okači vrata i podesi male razmake tako da se vrata lako otvaraju i ne zapinju.",
            ]
        steps += [
            "",
            _line("KORAK 3 - MONTAŽA NA ZID"),
            "  Obeleži tačnu visinu na zidu, montiraj zidni nosač ili šinu i tek onda okači element.",
            "  Pre završnog stezanja proveri libelom da je element potpuno ravan levo-desno i napred-nazad.",
            "  Tek kada je element ravan i čvrsto vezan, nastavi na sledeći zidni element ili front.",
        ]
        return [_render_instruction_line(line, lang) for line in steps]

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
            "  Sastavi mali korpus od bocnih stranica, dna i gornje ploce.",
            "  Proveri dijagonale pre nego sto zatvoris element ledjima.",
            "",
            _line("KORAK 2 - VEZA SA VISOKIM ELEMENTOM"),
            "  Popunu poravnaj sa visokom kolonom ispod.",
            "  Kada je prednja ivica u ravni, spoji elemente spojnim vijcima kroz bocne stranice.",
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
        return [_render_instruction_line(line, lang) for line in steps]

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
            "  Sastavi bocne stranice, dno i gornju plocu dok je element jos polozen i stabilan.",
            "  Zatim dodaj medjupolice i proveri da su prednje ivice svih delova u istoj ravni.",
            "",
            _line("KORAK 2 - LEDJA"),
            "  Postavi ledjnu plocu na zadnju stranu elementa i ucvrsti je prema predvidjenom spoju.",
            "  Pre konacnog stezanja proveri dijagonale da visoki element bude pod pravim uglom.",
            "  Ako dijagonale nisu jednake, prvo ispravi korpus pa tek onda nastavi dalje.",
        ]
        if "FRIDGE" in tid:
            if "FREEZER" in tid:
                steps += [
                    "",
                    _line("KORAK 3 - FRIŽIDER + ZAMRZIVAC"),
                    "  Uvuci uredjaj u gotov korpus tek kada je kolona potpuno ravna i stabilna.",
                    "  Proveri obavezne ventilacione zazore pre konacnog pricvrscivanja uredjaja.",
                    "  Gornji i donji front montiraj pomocu fabrickog seta za vezu vrata.",
                ]
            else:
                steps += [
                    "",
                    _line("KORAK 3 - UGRADNI FRIZIDER"),
                    "  Uvuci uredjaj u gotov korpus tek nakon nivelacije kolone.",
                    "  Proveri ventilacione zazore i probu otvaranja vrata pre montaze fronta.",
                    "  Front uredjaja montiraj tek kada si siguran da vrata uredjaja rade bez zapinjanja.",
                ]
        elif "OVEN_MICRO" in tid:
            steps += [
                "",
                _line("KORAK 3 - RERNA + MIKROTALASNA"),
                "  Pre unosenja uredjaja proveri obe zone i obaveznu ventilaciju.",
                "  Prvo ugradi mikrotalasnu, zatim rernu u donju zonu.",
                "  Donji servisni front montiraj tek nakon probe otvaranja i provere zazora oko oba uredjaja.",
            ]
        elif "OVEN" in tid:
            steps += [
                "",
                _line("KORAK 3 - KOLONA ZA RERNU"),
                "  Proveri visinu appliance zone i ventilaciju pre unosenja rerne.",
                "  Pricvrsti rernu prema fabrickom uputstvu proizvodjaca.",
                "  Donji servisni front montiraj tek nakon probe otvaranja vrata rerne.",
            ]
        elif "GLASS" in tid:
            steps += [
                "",
                _line("KORAK 3 - STAKLENA VRATA"),
                "  Montiraj staklena vrata prema sablonu proizvodjaca vitrine i proveri da nigde ne dodiruju korpus.",
            ]
        elif "OPEN" in tid or "PANTRY" in tid:
            steps += [
                "",
                _line("KORAK 3 - POLICE"),
                "  Ugradi police i podesi razmake prema nameni elementa.",
                "  Za ostavu proveri da teret na policama bude ravnomerno rasporedjen i da najtezi predmeti idu nize.",
            ]
        else:
            steps += [
                "",
                _line("KORAK 3 - VRATA"),
                "  Montiraj sarnire i podesi vrata tek kada je kolona nivelisana.",
                "  Vrata moraju da se zatvaraju ravno i bez trljanja o susedni front.",
            ]
        steps += [
            "",
            _line("KORAK 4 - POSTAVLJANJE"),
            "  Podigni kolonu na mesto pazljivo i po mogucstvu u paru, jer je element visok i tezak.",
            "  Nivelisi je, proveri da se ne ljulja i da prednja ivica stoji ravno sa susednim elementima.",
            "  Obavezno pricvrsti anti-tip set za zid pre koriscenja elementa.",
        ]
        return [_render_instruction_line(line, lang) for line in steps]

    return [_render_instruction_line(line, lang) for line in [
        "1. Sastavi bocne ploce, dno i gornju plocu.",
        "2. Proveri kvadraturu i umetni ledjnu plocu.",
        "3. Montiraj vrata ili okove prema tipu elementa.",
    ]]
