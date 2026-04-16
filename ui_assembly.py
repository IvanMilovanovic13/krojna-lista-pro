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
        "-- KORAK 3 - FRIŽIDER + ZAMRZIVAČ --": "-- STEP 3 - FRIDGE + FREEZER --",
        "-- KORAK 3 - UGRADNI FRIZIDER --": "-- STEP 3 - BUILT-IN REFRIGERATOR --",
        "-- KORAK 3 - UGRADNI FRIŽIDER --": "-- STEP 3 - BUILT-IN REFRIGERATOR --",
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
    txt = txt.replace("KORAK ", "STEP ")
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

    sr_replacements = [
        ("Umetni dno izmedju bocnih stranica i spoji ga prema busenjima.", "Insira o painel inferior entre as laterais e una conforme as furações."),
        ("Umetni dno i gornju plocu izmedju bocnih stranica i spoji ih prema busenjima.", "Insira o painel inferior e o superior entre as laterais e una conforme as furações."),
        ("Zatim postavi gornju plocu i proveri da korpus ostane ravan.", "Depois coloque o painel superior e confira se o corpo permanece alinhado."),
        ("Uzmi levu i desnu bocnu stranicu i postavi ih uspravno tako da prednje ivice gledaju ka napred.", "Pegue a lateral esquerda e a direita e coloque-as em pé, com as bordas frontais voltadas para a frente."),
        ("Pre sledeceg koraka proveri da korpus stoji ravno i da nigde nije uvijen.", "Antes do próximo passo, confira se o corpo está reto e sem torção."),
        ("Montiraj šarke, okači vrata i podesi male razmake tako da se vrata lako otvaraju i ne zapinju.", "Monte as dobradiças, pendure as portas e ajuste as folgas para que abram sem raspar."),
        ("Obeleži tačnu visinu na zidu, montiraj zidni nosač ili šinu i tek onda okači element.", "Marque a altura exata na parede, monte o suporte ou trilho de parede e só então pendure o módulo."),
        ("Pre završnog stezanja proveri libelom da je element potpuno ravan levo-desno i napred-nazad.", "Antes do aperto final, confira com nível se o módulo está alinhado à esquerda, à direita, à frente e atrás."),
        ("Tek kada je element ravan i čvrsto vezan, nastavi na sledeći zidni element ili frente.", "Só continue para o próximo módulo superior ou frente quando o módulo estiver nivelado e bem fixado."),
        ("Umetni ledjnu plocu na zadnju stranu elementa.", "Insira o painel traseiro na parte de trás do módulo."),
        ("Pre konacnog stezanja proveri dijagonale da element bude pod pravim uglom.", "Antes do aperto final, confira as diagonais para deixar o módulo no esquadro."),
        ("Prvo proveri da li rerna slobodno ulazi u otvor korpusa i da li ima prostora za ventilaciju.", "Primeiro confira se o forno entra livremente no vão do corpo e se há espaço para ventilação."),
        ("Zatim isezi otvor u radnoj ploci prema šablonu ploce za kuvanje.", "Depois recorte a abertura na bancada conforme o gabarito do cooktop."),
        ("Zatim isezi otvor u radnoj ploci prema sablonu ploce za kuvanje.", "Depois recorte a abertura na bancada conforme o gabarito do cooktop."),
        ("Lazni front ili front fioke montiraj tek nakon probe zazora oko rerne i vrata rerne.", "Monte a frente falsa ou a frente da gaveta somente depois de conferir as folgas ao redor do forno e da porta do forno."),
        ("Montiraj noge ili stopice, zatim nivelisi element na mestu ugradnje.", "Monte os pés, depois nivele o módulo no local de instalação."),
        ("Tek kada je korpus ravan i stabilan montiraj radnu plocu ili nastavi na sledeci element.", "Somente quando o corpo estiver nivelado e estável, monte a bancada ou continue para o próximo módulo."),
        ("Izbusiti rupe za konfirmate i zleb za ledjnu plocu.", "Fure para os parafusos confirmat e faça o canal do painel traseiro."),
        ("Ugradna rerna", "Forno de embutir"),
        ("Ploca za kuvanje", "Cooktop"),
        ("Fioka ispod rerne", "Gaveta sob o forno"),
        ("#3 - Rerna+ploča", "#3 - Forno+cooktop"),
        ("Rerna+ploča", "Forno+cooktop"),
        ("Rerna+ploca", "Forno+cooktop"),
        ("KORAK 4 - VRATA", "PASSO 4 - PORTAS"),
        ("KORAK 3 - MONTAŽA NA ZID", "PASSO 3 - FIXAÇÃO NA PAREDE"),
        ("Fure the confirmat holes and recorte the groove for the back panel.", "Fure para os parafusos confirmat e faça o canal do painel traseiro."),
        ("Monte the hinges, hang the portas and set 2 mm reveals.", "Monte as dobradiças, pendure as portas e ajuste folgas de 2 mm."),
        ("Run water and confira whether the trap, tap and all connections leak.", "Abra a água e confira se o sifão, a torneira e todas as conexões vazam."),
        ("Only when everything is dry and leak-free should you close the unit and continue to the next module.", "Só feche o módulo e continue para o próximo quando tudo estiver seco e sem vazamentos."),
        ("Fioka ispod rerne", "Gaveta sob o forno"),
        ("rernu", "forno"),
        ("rerne", "forno"),
        ("radnoj ploci", "bancada"),
        ("radnu plocu", "bancada"),
        ("radna ploca", "bancada"),
        ("ploce za kuvanje", "cooktop"),
        ("sablonu", "gabarito"),
        ("šablonu", "gabarito"),
        ("sledeci element", "próximo módulo"),
    ]
    for src, dst in sr_replacements:
        txt = txt.replace(src, dst)

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


def _polish_instruction_line_es(line: str) -> str:
    txt = _translate_instruction_line(line, "en")
    exact = {
        "-- PANEL ELEMENT --": "-- PANEL --",
        "-- SINK BASE UNIT --": "-- MÓDULO BAJO DE FREGADERO --",
        "-- BASE UNIT PARTS LIST --": "-- LISTA DE PIEZAS DEL MÓDULO BAJO --",
        "-- WALL UNIT PARTS LIST --": "-- LISTA DE PIEZAS DEL MÓDULO ALTO --",
        "-- TOP FILLER PARTS LIST --": "-- LISTA DE PIEZAS DEL RELLENO SUPERIOR --",
        "-- FREESTANDING DISHWASHER --": "-- LAVAVAJILLAS INDEPENDIENTE --",
        "-- FREESTANDING RANGE --": "-- COCINA INDEPENDIENTE --",
        "-- FREESTANDING REFRIGERATOR --": "-- FRIGORÍFICO INDEPENDIENTE --",
        "-- DISHWASHER OPENING PARTS LIST --": "-- LISTA DE PIEZAS DEL HUECO DE LAVAVAJILLAS --",
        "-- STEP 1 - VERIFY DIMENSIONS --": "-- PASO 1 - REVISAR MEDIDAS --",
        "-- STEP 2 - POSITIONING --": "-- PASO 2 - POSICIONAMIENTO --",
        "-- STEP 3 - FIXING --": "-- PASO 3 - FIJACIÓN --",
        "-- STEP 4 - FINAL CHECK --": "-- PASO 4 - REVISIÓN FINAL --",
        "-- KORAK 5 - ZAVRSNA PROVERA --": "-- PASO 5 - REVISIÓN FINAL --",
        "-- STEP 1 - PREPARE THE OPENING --": "-- PASO 1 - PREPARAR EL HUECO --",
        "-- STEP 2 - CONNECTIONS --": "-- PASO 2 - CONEXIONES --",
        "-- STEP 3 - INSTALL THE MACHINE --": "-- PASO 3 - INSTALAR LA MÁQUINA --",
        "-- STEP 4 - DISHWASHER FRONT --": "-- PASO 4 - FRENTE DEL LAVAVAJILLAS --",
        "-- STEP 1 - CARCASS --": "-- PASO 1 - CUERPO --",
        "-- STEP 2 - BACK PANEL AND CUT-OUTS --": "-- PASO 2 - FONDO Y RECORTES --",
        "-- STEP 3 - DOORS --": "-- PASO 3 - PUERTAS --",
        "-- STEP 4 - WORKTOP AND SINK --": "-- PASO 4 - ENCIMERA Y FREGADERO --",
        "-- STEP 1 - SIDE PANELS --": "-- PASO 1 - LATERALES --",
        "-- STEP 2 - BOTTOM AND TOP PANEL --": "-- PASO 2 - PANEL INFERIOR Y SUPERIOR --",
        "-- STEP 3 - BACK PANEL --": "-- PASO 3 - FONDO --",
        "-- STEP 4 - DRAWERS --": "-- PASO 4 - CAJONES --",
        "-- STEP 4 - DOORS + DRAWER --": "-- PASO 4 - PUERTAS + CAJÓN --",
        "-- KORAK 4 - VRATA --": "-- PASO 4 - PUERTAS --",
        "-- STEP 4 - WASTE SORTER --": "-- PASO 4 - CUBO EXTRAÍBLE --",
        "-- STEP 4 - NARROW PULL-OUT UNIT --": "-- PASO 4 - MÓDULO ESTRECHO EXTRAÍBLE --",
        "-- STEP 4 - COOKING UNIT --": "-- PASO 4 - MÓDULO DE COCCIÓN --",
        "-- STEP 4 - SHELVES --": "-- PASO 4 - ESTANTES --",
        "-- STEP 4 - HOB --": "-- PASO 4 - PLACA --",
        "-- STEP 4 - BUILT-IN OVEN --": "-- PASO 4 - HORNO ENCASTRADO --",
        "-- STEP 5 - LEGS AND POSITIONING --": "-- PASO 5 - PATAS Y POSICIONAMIENTO --",
        "-- STEP 2 - DOORS / MECHANISM --": "-- PASO 2 - PUERTAS / MECANISMO --",
        "-- STEP 3 - WALL INSTALLATION --": "-- PASO 3 - INSTALACIÓN EN PARED --",
        "-- KORAK 3 - MONTAŽA NA ZID --": "-- PASO 3 - INSTALACIÓN EN PARED --",
        "-- STEP 1 - ASSEMBLE THE TOP UNIT --": "-- PASO 1 - MONTAR EL MÓDULO SUPERIOR --",
        "-- STEP 2 - CONNECT TO THE TALL UNIT --": "-- PASO 2 - UNIR AL MÓDULO ALTO --",
        "-- STEP 3 - SHELF --": "-- PASO 3 - ESTANTE --",
        "-- STEP 2 - BACK PANEL --": "-- PASO 2 - FONDO --",
        "-- STEP 3 - FRIDGE + FREEZER --": "-- PASO 3 - FRIGORÍFICO + CONGELADOR --",
        "-- STEP 3 - BUILT-IN REFRIGERATOR --": "-- PASO 3 - FRIGORÍFICO ENCASTRADO --",
        "-- STEP 3 - OVEN + MICROWAVE --": "-- PASO 3 - HORNO + MICROONDAS --",
        "-- STEP 3 - OVEN TOWER --": "-- PASO 3 - COLUMNA DE HORNO --",
        "-- STEP 3 - GLASS DOORS --": "-- PASO 3 - PUERTAS DE VIDRIO --",
        "-- STEP 4 - POSITIONING --": "-- PASO 4 - POSICIONAMIENTO --",
    }
    if txt in exact:
        return exact[txt]

    replacements = [
        ("Filler panel", "Panel de relleno"),
        ("End side panel", "Panel lateral de remate"),
        ("Left side panel", "Lateral izquierdo"),
        ("Right side panel", "Lateral derecho"),
        ("Back panel", "Panel trasero"),
        ("Top panel", "Panel superior"),
        ("Bottom panel", "Panel inferior"),
        ("Lower service front", "Frente inferior de servicio"),
        ("Upper appliance front", "Frente superior del electrodoméstico"),
        ("Lower appliance front", "Frente inferior del electrodoméstico"),
        ("Appliance front", "Frente del electrodoméstico"),
        ("Drawer fronts", "Frentes de cajón"),
        ("Drawer front", "Frente de cajón"),
        ("Narrow-unit front", "Frente del módulo estrecho"),
        ("Sink-base doors", "Puertas bajo fregadero"),
        ("Doors below sink", "Puertas bajo fregadero"),
        ("Doors below hob", "Puertas bajo placa"),
        ("Oven front", "Frente del horno"),
        ("Glass doors", "Puertas de vidrio"),
        ("Doors", "Puertas"),
        ("Hinges", "Bisagras"),
        ("Glass-door hinges", "Bisagras para vidrio"),
        ("Drawer runners", "Guías de cajón"),
        ("runner", "guía"),
        ("Drawer box", "Caja de cajón"),
        ("Built-in oven", "Horno encastrado"),
        ("Built-in microwave", "Microondas encastrado"),
        ("Hob", "Placa"),
        ("Built-in dishwasher", "Lavavajillas encastrado"),
        ("Front mounting kit", "Kit de montaje del frente"),
        ("Cross rail", "Travesaño"),
        ("Worktop support rail", "Soporte de encimera"),
        ("Legs", "Patas"),
        ("Intermediate shelf", "Estante intermedio"),
        ("Adjustable shelves", "Estantes ajustables"),
        ("Adjustable shelf", "Estante ajustable"),
        ("Shelf supports", "Soportes de estante"),
        ("Narrow pull-out mechanism", "Mecanismo estrecho extraíble"),
        ("Baskets / supports", "Cestos / soportes"),
        ("Lift-up mechanism", "Mecanismo abatible"),
        ("Front connection kits", "Kits de unión de frentes"),
        ("Front connection kit", "Kit de unión del frente"),
        ("Ventilation spacer kit", "Kit separador de ventilación"),
        ("pcs", "uds."),
        ("pc", "ud."),
        ("Carcass", "Cuerpo"),
        ("carcass", "cuerpo"),
        ("worktop", "encimera"),
        ("Worktop", "Encimera"),
        ("sink", "fregadero"),
        ("Sink", "Fregadero"),
        ("oven", "horno"),
        ("Oven", "Horno"),
        ("hob", "placa"),
        ("Hob", "Placa"),
        ("fronts", "frentes"),
        ("front", "frente"),
        ("doors", "puertas"),
        ("door", "puerta"),
        ("wall", "pared"),
        ("Wall", "Pared"),
        ("opening", "hueco"),
        ("Opening", "Hueco"),
        ("factory template", "plantilla del fabricante"),
        ("manufacturer's template", "plantilla del fabricante"),
        ("manufacturer's instructions", "instrucciones del fabricante"),
        ("This appliance has no carcass or front in the cut list.", "Este electrodoméstico no tiene cuerpo ni frente en la lista de corte."),
        ("Connect water, drain and power according to the manufacturer's instructions.", "Conecta agua, desagüe y electricidad según las instrucciones del fabricante."),
        ("After levelling, check door clearance and access to services.", "Después de nivelar, revisa la holgura de la puerta y el acceso a las instalaciones."),
        ("Slide the machine into the opening without force and level it using the factory feet.", "Introduce la máquina en el hueco sin forzar y nivélala con las patas de fábrica."),
        ("Fix the front to the dishwasher door using the factory template and mounting kit.", "Fija el frente a la puerta del lavavajillas con la plantilla de fábrica y el kit de montaje."),
        ("Leave even 2-3 mm reveals relative to adjacent fronts.", "Deja holguras uniformes de 2-3 mm respecto a los frentes vecinos."),
        ("Fit the doors and set 2-3 mm reveals so they open freely below the sink.", "Monta las puertas y ajusta holguras de 2-3 mm para que abran libremente bajo el fregadero."),
        ("Mark the cut-out in the worktop using the sink template.", "Marca el recorte en la encimera con la plantilla del fregadero."),
        ("Protect the cut edge of the opening from moisture before mounting the sink.", "Protege de la humedad el canto cortado antes de montar el fregadero."),
        ("Run water and check whether the trap, tap and all connections leak.", "Abre el agua y revisa si el sifón, el grifo o las conexiones tienen fugas."),
        ("Only when everything is dry and leak-free should you close the unit and continue to the next module.", "Cierra el módulo y continúa al siguiente solo cuando todo esté seco y sin fugas."),
        ("Drill the confirmat holes and cut the groove for the back panel.", "Taladra los agujeros para confirmat y corta la ranura del panel trasero."),
        ("Connect the bottom and top panel between the side panels.", "Une el panel inferior y el superior entre los laterales."),
        ("Insert the back panel and verify the diagonals.", "Inserta el panel trasero y revisa las diagonales."),
        ("Fit the runners, assemble the drawer boxes and align the fronts.", "Monta las guías, arma las cajas de cajón y alinea los frentes."),
        ("Fit the doors first, then the runner and drawer front.", "Monta primero las puertas y después la guía y el frente de cajón."),
        ("Slide the oven into the carcass and cut the hob opening in the worktop using the manufacturer's template.", "Introduce el horno en el cuerpo y corta el hueco de la placa en la encimera con la plantilla del fabricante."),
        ("Fit the dummy front only after checking the clearance around the oven.", "Monta el frente falso solo después de revisar las holguras alrededor del horno."),
        ("Fit the legs, level the cabinet, and only then install the worktop.", "Monta las patas, nivela el módulo y solo entonces instala la encimera."),
        ("Assemble the side panels, bottom and top panel.", "Monta los laterales, el panel inferior y el superior."),
        ("Assemble the side panels and bottom as a standard base cuerpo.", "Monta los laterales y el panel inferior como un cuerpo bajo estándar."),
        ("Do not fit a full top panel across the entire hueco so there is room for the fregadero and services.", "No montes un panel superior completo en todo el hueco, para dejar espacio al fregadero y a las instalaciones."),
        ("Check squareness and insert the back panel.", "Revisa la escuadra e inserta el panel trasero."),
        ("Install the doors or hardware according to the unit type.", "Instala las puertas o herrajes según el tipo de módulo."),
        ("Fit the hinges, hang the puertas and set 2 mm reveals.", "Monta las bisagras, cuelga las puertas y ajusta holguras de 2 mm."),
        ("Fit the hinges, hang the doors and set 2 mm reveals.", "Monta las bisagras, cuelga las puertas y ajusta holguras de 2 mm."),
        ("Fit the puertas and set 2-3 mm reveals so they open freely below the fregadero.", "Monta las puertas y ajusta holguras de 2-3 mm para que abran libremente bajo el fregadero."),
        ("Check that the trap and pipes do not hit the puertas when closing.", "Revisa que el sifón y los tubos no golpeen las puertas al cerrar."),
        ("Mark the fregadero cut-out in the encimera using the template and verify the position before cutting.", "Marca el recorte del fregadero en la encimera con la plantilla y revisa la posición antes de cortar."),
        ("Protect the cut edge of the hueco from moisture before mounting the fregadero.", "Protege de la humedad el canto cortado del hueco antes de montar el fregadero."),
        ("Mark the back panel for the water supply, drain and any required socket.", "Marca el panel trasero para la entrada de agua, el desagüe y cualquier enchufe necesario."),
        ("Cut the huecos only after verifying the actual service positions on the pared, not just by estimate.", "Corta los huecos solo después de verificar las posiciones reales de las instalaciones en la pared, no solo por estimación."),
        ("Umetni dno izmedju bocnih stranica i spoji ga prema busenjima.", "Inserta el panel inferior entre los laterales y únelo según los taladros."),
        ("Umetni dno i gornju plocu izmedju bocnih stranica i spoji ih prema busenjima.", "Inserta el panel inferior y el superior entre los laterales y únelos según los taladros."),
        ("Zatim postavi gornju plocu i proveri da korpus ostane ravan.", "Después coloca el panel superior y revisa que el cuerpo quede recto."),
        ("Pre sledeceg koraka proveri da korpus stoji ravno i da nigde nije uvijen.", "Antes del siguiente paso revisa que el cuerpo esté recto y sin torsión."),
        ("Montiraj šarke, okači vrata i podesi male razmake tako da se vrata lako otvaraju i ne zapinju.", "Monta las bisagras, cuelga las puertas y ajusta las holguras para que abran sin rozar."),
        ("Obeleži tačnu visinu na zidu, montiraj zidni nosač ili šinu i tek onda okači element.", "Marca la altura exacta en la pared, monta el soporte o riel de pared y solo entonces cuelga el módulo."),
        ("Pre završnog stezanja proveri libelom da je element potpuno ravan levo-desno i napred-nazad.", "Antes del apriete final revisa con nivel que el módulo esté recto de izquierda a derecha y de delante hacia atrás."),
        ("Tek kada je element ravan i čvrsto vezan, nastavi na sledeći zidni element ili frente.", "Continúa al siguiente módulo alto o frente solo cuando el módulo esté nivelado y bien fijado."),
        ("Rerna+ploča", "Horno+placa"),
        ("Rerna+ploca", "Horno+placa"),
        ("#3 - Rerna+ploča", "#3 - Horno+placa"),
        ("Type:", "Tipo:"),
        ("Dimensions:", "Medidas:"),
        ("Wall:", "Pared:"),
        ("Pustite vodu i proverite da li sifon, slavina i svi spojevi cure.", "Abre el agua y revisa si el sifón, el grifo o las conexiones tienen fugas."),
        ("Tek kada je sve suvo i bez curenja zatvorite element i nastavite na sledeći modul.", "Cierra el módulo y continúa al siguiente solo cuando todo esté seco y sin fugas."),
        ("Uzmite levu i desnu bočnu ploču i postavite ih uspravno tako da kantovane prednje ivice gledaju napred.", "Toma el lateral izquierdo y el derecho y colócalos en vertical, con los cantos frontales hacia delante."),
        ("Izbušite rupe za konfirmate i žleb za leđnu ploču.", "Taladra los agujeros para confirmat y la ranura del panel trasero."),
        ("Umetnite dno između bočnih stranica i spojite ga prema bušenjima.", "Inserta el panel inferior entre los laterales y únelo según los taladros."),
        ("Zatim postavite gornju ploču i proverite da korpus ostane ravan.", "Después coloca el panel superior y revisa que el cuerpo quede recto."),
        ("Umetnite leđnu ploču na zadnju stranu elementa.", "Inserta el panel trasero en la parte posterior del módulo."),
        ("Umetni ledjnu plocu na zadnju stranu elementa.", "Inserta el panel trasero en la parte posterior del módulo."),
        ("Pre konačnog stezanja proverite dijagonale da element bude pod pravim uglom.", "Antes del apriete final revisa las diagonales para que el módulo quede a escuadra."),
        ("Pre konacnog stezanja proveri dijagonale da element bude pod pravim uglom.", "Antes del apriete final revisa las diagonales para que el módulo quede a escuadra."),
        ("Prvo proverite da li rerna slobodno ulazi u otvor korpusa i da li ima prostora za ventilaciju.", "Primero revisa si el horno entra libremente en el hueco del cuerpo y si queda espacio para ventilación."),
        ("Prvo proveri da li rerna slobodno ulazi u otvor korpusa i da li ima prostora za ventilaciju.", "Primero revisa si el horno entra libremente en el hueco del cuerpo y si queda espacio para ventilación."),
        ("Zatim isecite otvor u radnoj ploči prema šablonu ploče za kuvanje.", "Después corta el hueco de la placa en la encimera según la plantilla del fabricante."),
        ("Zatim isezi otvor u radnoj ploci prema šablonu ploce za kuvanje.", "Después corta el hueco de la placa en la encimera según la plantilla del fabricante."),
        ("Zatim isezi otvor u radnoj ploci prema sablonu ploce za kuvanje.", "Después corta el hueco de la placa en la encimera según la plantilla del fabricante."),
        ("  Zatim isezi otvor u radnoj ploci prema sablonu ploce za kuvanje.", "  Después corta el hueco de la placa en la encimera según la plantilla del fabricante."),
        ("Lažni front ili front fioke montirajte tek nakon probe zazora oko rerne i vrata rerne.", "Monta el frente falso o el frente de cajón solo después de comprobar las holguras alrededor del horno y de su puerta."),
        ("Lazni frente ili frente fioke montiraj tek nakon probe zazora oko rerne i vrata rerne.", "Monta el frente falso o el frente de cajón solo después de comprobar las holguras alrededor del horno y de su puerta."),
        ("Montirajte noge ili stopice, zatim nivelišite element na mestu ugradnje.", "Monta las patas y después nivela el módulo en el lugar de instalación."),
        ("Montiraj noge ili stopice, zatim nivelisi element na mestu ugradnje.", "Monta las patas y después nivela el módulo en el lugar de instalación."),
        ("Tek kada je korpus ravan i stabilan montirajte radnu ploču ili nastavite na sledeći element.", "Instala la encimera o continúa al siguiente módulo solo cuando el cuerpo esté nivelado y estable."),
        ("Tek kada je korpus ravan i stabilan montiraj radnu plocu ili nastavi na sledeci element.", "Instala la encimera o continúa al siguiente módulo solo cuando el cuerpo esté nivelado y estable."),
        ("Ugradna rerna", "Horno encastrado"),
        ("Ploca za kuvanje", "Placa"),
        ("Ploča za kuvanje", "Placa"),
        ("Fioka ispod rerne", "Cajón bajo el horno"),
    ]
    for src, dst in replacements:
        txt = txt.replace(src, dst)
    return txt


def _polish_instruction_line_ru(line: str) -> str:
    txt = _translate_instruction_line(line, "en")
    exact = {
        "-- PANEL ELEMENT --": "-- ПАНЕЛЬ --",
        "-- SINK BASE UNIT --": "-- НИЖНИЙ МОДУЛЬ ПОД МОЙКУ --",
        "-- BASE UNIT PARTS LIST --": "-- СПИСОК ДЕТАЛЕЙ НИЖНЕГО МОДУЛЯ --",
        "-- WALL UNIT PARTS LIST --": "-- СПИСОК ДЕТАЛЕЙ ВЕРХНЕГО МОДУЛЯ --",
        "-- TOP FILLER PARTS LIST --": "-- СПИСОК ДЕТАЛЕЙ ВЕРХНЕЙ ДОБОРНОЙ ПАНЕЛИ --",
        "-- FREESTANDING DISHWASHER --": "-- ОТДЕЛЬНОСТОЯЩАЯ ПОСУДОМОЕЧНАЯ МАШИНА --",
        "-- FREESTANDING RANGE --": "-- ОТДЕЛЬНОСТОЯЩАЯ ПЛИТА --",
        "-- FREESTANDING REFRIGERATOR --": "-- ОТДЕЛЬНОСТОЯЩИЙ ХОЛОДИЛЬНИК --",
        "-- DISHWASHER OPENING PARTS LIST --": "-- СПИСОК ДЕТАЛЕЙ ПРОЁМА ПММ --",
        "-- STEP 1 - VERIFY DIMENSIONS --": "-- ШАГ 1 - ПРОВЕРИТЬ РАЗМЕРЫ --",
        "-- STEP 2 - POSITIONING --": "-- ШАГ 2 - ПОЗИЦИОНИРОВАНИЕ --",
        "-- STEP 3 - FIXING --": "-- ШАГ 3 - КРЕПЛЕНИЕ --",
        "-- STEP 4 - FINAL CHECK --": "-- ШАГ 4 - ФИНАЛЬНАЯ ПРОВЕРКА --",
        "-- KORAK 5 - ZAVRSNA PROVERA --": "-- ШАГ 5 - ФИНАЛЬНАЯ ПРОВЕРКА --",
        "-- STEP 1 - PREPARE THE OPENING --": "-- ШАГ 1 - ПОДГОТОВИТЬ ПРОЁМ --",
        "-- STEP 2 - CONNECTIONS --": "-- ШАГ 2 - ПОДКЛЮЧЕНИЯ --",
        "-- STEP 3 - INSTALL THE MACHINE --": "-- ШАГ 3 - УСТАНОВИТЬ МАШИНУ --",
        "-- STEP 4 - DISHWASHER FRONT --": "-- ШАГ 4 - ФАСАД ПММ --",
        "-- STEP 1 - CARCASS --": "-- ШАГ 1 - КОРПУС --",
        "-- STEP 2 - BACK PANEL AND CUT-OUTS --": "-- ШАГ 2 - ЗАДНИК И ВЫРЕЗЫ --",
        "-- STEP 3 - DOORS --": "-- ШАГ 3 - ДВЕРИ --",
        "-- STEP 4 - WORKTOP AND SINK --": "-- ШАГ 4 - СТОЛЕШНИЦА И МОЙКА --",
        "-- STEP 1 - SIDE PANELS --": "-- ШАГ 1 - БОКОВИНЫ --",
        "-- STEP 2 - BOTTOM AND TOP PANEL --": "-- ШАГ 2 - НИЖНЯЯ И ВЕРХНЯЯ ПАНЕЛЬ --",
        "-- STEP 3 - BACK PANEL --": "-- ШАГ 3 - ЗАДНИК --",
        "-- STEP 4 - DRAWERS --": "-- ШАГ 4 - ЯЩИКИ --",
        "-- STEP 4 - DOORS + DRAWER --": "-- ШАГ 4 - ДВЕРИ + ЯЩИК --",
        "-- KORAK 4 - VRATA --": "-- ШАГ 4 - ДВЕРИ --",
        "-- STEP 4 - COOKING UNIT --": "-- ШАГ 4 - МОДУЛЬ ДУХОВКИ И ПАНЕЛИ --",
        "-- STEP 4 - HOB --": "-- ШАГ 4 - ВАРОЧНАЯ ПАНЕЛЬ --",
        "-- STEP 4 - BUILT-IN OVEN --": "-- ШАГ 4 - ВСТРАИВАЕМАЯ ДУХОВКА --",
        "-- STEP 5 - LEGS AND POSITIONING --": "-- ШАГ 5 - НОЖКИ И ПОЗИЦИОНИРОВАНИЕ --",
        "-- STEP 3 - WALL INSTALLATION --": "-- ШАГ 3 - МОНТАЖ НА СТЕНУ --",
        "-- KORAK 3 - MONTAŽA NA ZID --": "-- ШАГ 3 - МОНТАЖ НА СТЕНУ --",
    }
    if txt in exact:
        return exact[txt]

    replacements = [
        ("Left side panel", "Левая боковина"), ("Right side panel", "Правая боковина"),
        ("Back panel", "Задняя панель"), ("Top panel", "Верхняя панель"), ("Bottom panel", "Нижняя панель"),
        ("Drawer front", "Фасад ящика"), ("Drawer fronts", "Фасады ящиков"), ("Drawer box", "Короб ящика"),
        ("Doors below sink", "Двери под мойкой"), ("Doors below hob", "Двери под варочной панелью"),
        ("Doors", "Двери"), ("Hinges", "Петли"), ("Drawer runners", "Направляющие ящика"),
        ("Built-in oven", "Встраиваемая духовка"), ("Hob", "Варочная панель"), ("Worktop", "Столешница"),
        ("Legs", "Ножки"), ("Carcass", "Корпус"), ("carcass", "корпус"), ("worktop", "столешница"),
        ("sink", "мойка"), ("Sink", "Мойка"), ("oven", "духовка"), ("Oven", "Духовка"),
        ("hob", "варочная панель"), ("fronts", "фасады"), ("front", "фасад"), ("doors", "двери"),
        ("wall", "стена"), ("Wall", "Стена"), ("opening", "проём"), ("Opening", "Проём"),
        ("manufacturer's template", "шаблон производителя"), ("manufacturer's instructions", "инструкции производителя"),
        ("This appliance has no carcass or front in the cut list.", "У этой техники нет корпуса и фасада в карте раскроя."),
        ("Connect water, drain and power according to the manufacturer's instructions.", "Подключите воду, слив и питание по инструкции производителя."),
        ("Fit the doors and set 2-3 mm reveals so they open freely below the sink.", "Установите двери и выставьте зазоры 2-3 мм, чтобы они свободно открывались под мойкой."),
        ("Mark the cut-out in the worktop using the sink template.", "Разметьте вырез в столешнице по шаблону мойки."),
        ("Protect the cut edge of the opening from moisture before mounting the sink.", "Защитите вырезанную кромку от влаги перед установкой мойки."),
        ("Run water and check whether the trap, tap and all connections leak.", "Откройте воду и проверьте, не протекают ли сифон, смеситель и соединения."),
        ("Only when everything is dry and leak-free should you close the unit and continue to the next module.", "Закрывайте модуль и переходите к следующему только когда всё сухо и без протечек."),
        ("Drill the confirmat holes and cut the groove for the back panel.", "Просверлите отверстия под конфирматы и паз для задней панели."),
        ("Connect the bottom and top panel between the side panels.", "Соедините нижнюю и верхнюю панели между боковинами."),
        ("Insert the back panel and verify the diagonals.", "Вставьте заднюю панель и проверьте диагонали."),
        ("Fit the hinges, hang the doors and set 2 mm reveals.", "Установите петли, навесьте двери и выставьте зазоры 2 мм."),
        ("Assemble the side panels, bottom and top panel.", "Соберите боковины, нижнюю и верхнюю панели."),
        ("Assemble the side panels and bottom as a standard base cuerpo.", "Соберите боковины и нижнюю панель как стандартный нижний корпус."),
        ("Do not fit a full top panel across the entire hueco so there is room for the fregadero and services.", "Не ставьте полную верхнюю панель на весь проём, чтобы осталось место для мойки и коммуникаций."),
        ("Check squareness and insert the back panel.", "Проверьте прямой угол и вставьте заднюю панель."),
        ("Install the doors or hardware according to the unit type.", "Установите двери или фурнитуру согласно типу модуля."),
        ("Umetni dno izmedju bocnih stranica i spoji ga prema busenjima.", "Вставьте нижнюю панель между боковинами и соедините по отверстиям."),
        ("Umetni dno i gornju plocu izmedju bocnih stranica i spoji ih prema busenjima.", "Вставьте нижнюю и верхнюю панели между боковинами и соедините по отверстиям."),
        ("Zatim postavi gornju plocu i proveri da korpus ostane ravan.", "Затем установите верхнюю панель и проверьте, что корпус остаётся ровным."),
        ("Pre sledeceg koraka proveri da korpus stoji ravno i da nigde nije uvijen.", "Перед следующим шагом проверьте, что корпус стоит ровно и не перекручен."),
        ("Montiraj šarke, okači vrata i podesi male razmake tako da se vrata lako otvaraju i ne zapinju.", "Установите петли, навесьте двери и выставьте зазоры, чтобы двери открывались без заедания."),
        ("Obeleži tačnu visinu na zidu, montiraj zidni nosač ili šinu i tek onda okači element.", "Отметьте точную высоту на стене, установите настенный крепёж или рейку и только потом навесьте модуль."),
        ("Pre završnog stezanja proveri libelom da je element potpuno ravan levo-desno i napred-nazad.", "Перед окончательной затяжкой проверьте уровнем, что модуль ровный слева направо и спереди назад."),
        ("Tek kada je element ravan i čvrsto vezan, nastavi na sledeći zidni element ili frente.", "Продолжайте к следующему навесному модулю или фасаду только когда модуль ровный и надёжно закреплён."),
        ("Tek kada je element ravan i čvrsto vezan, nastavi na sledeći zidni element ili фасад.", "Продолжайте к следующему навесному модулю или фасаду только когда модуль ровный и надёжно закреплён."),
        ("Rerna+ploča", "Духовка+панель"), ("Rerna+ploca", "Духовка+панель"), ("#3 - Rerna+ploča", "#3 - Духовка+панель"),
        ("Type:", "Тип:"), ("Dimensions:", "Размеры:"), ("Wall:", "Стена:"),
        ("Pustite vodu i proverite da li sifon, slavina i svi spojevi cure.", "Откройте воду и проверьте, не протекают ли сифон, смеситель и все соединения."),
        ("Tek kada je sve suvo i bez curenja zatvorite element i nastavite na sledeći modul.", "Закрывайте модуль и переходите дальше только когда всё сухо и без протечек."),
        ("Uzmite levu i desnu bočnu ploču i postavite ih uspravno tako da kantovane prednje ivice gledaju napred.", "Возьмите левую и правую боковины и поставьте вертикально так, чтобы кромленные передние края смотрели вперёд."),
        ("Izbušite rupe za konfirmate i žleb za leđnu ploču.", "Просверлите отверстия под конфирматы и паз для задней панели."),
        ("Umetnite dno između bočnih stranica i spojite ga prema bušenjima.", "Вставьте нижнюю панель между боковинами и соедините по отверстиям."),
        ("Zatim postavite gornju ploču i proverite da korpus ostane ravan.", "Затем установите верхнюю панель и проверьте, что корпус остаётся ровным."),
        ("Umetnite leđnu ploču na zadnju stranu elementa.", "Вставьте заднюю панель с задней стороны модуля."),
        ("Umetni ledjnu plocu na zadnju stranu elementa.", "Вставьте заднюю панель с задней стороны модуля."),
        ("Pre konačnog stezanja proverite dijagonale da element bude pod pravim uglom.", "Перед окончательной затяжкой проверьте диагонали, чтобы модуль был под прямым углом."),
        ("Pre konacnog stezanja proveri dijagonale da element bude pod pravim uglom.", "Перед окончательной затяжкой проверьте диагонали, чтобы модуль был под прямым углом."),
        ("Prvo proverite da li rerna slobodno ulazi u otvor korpusa i da li ima prostora za ventilaciju.", "Сначала проверьте, свободно ли духовка входит в проём корпуса и есть ли место для вентиляции."),
        ("Prvo proveri da li rerna slobodno ulazi u otvor korpusa i da li ima prostora za ventilaciju.", "Сначала проверьте, свободно ли духовка входит в проём корпуса и есть ли место для вентиляции."),
        ("Zatim isecite otvor u radnoj ploči prema šablonu ploče za kuvanje.", "Затем вырежьте проём в столешнице по шаблону варочной панели."),
        ("Zatim isezi otvor u radnoj ploci prema šablonu ploce za kuvanje.", "Затем вырежьте проём в столешнице по шаблону варочной панели."),
        ("Zatim isezi otvor u radnoj ploci prema sablonu ploce za kuvanje.", "Затем вырежьте проём в столешнице по шаблону варочной панели."),
        ("Lažni front ili front fioke montirajte tek nakon probe zazora oko rerne i vrata rerne.", "Фальш-фасад или фасад ящика устанавливайте только после проверки зазоров вокруг духовки и её дверцы."),
        ("Lazni front ili front fioke montiraj tek nakon probe zazora oko rerne i vrata rerne.", "Фальш-фасад или фасад ящика устанавливайте только после проверки зазоров вокруг духовки и её дверцы."),
        ("Lazni фасад ili фасад fioke montiraj tek nakon probe zazora oko rerne i vrata rerne.", "Фальш-фасад или фасад ящика устанавливайте только после проверки зазоров вокруг духовки и её дверцы."),
        ("Montirajte noge ili stopice, zatim nivelišite element na mestu ugradnje.", "Установите ножки, затем выровняйте модуль на месте монтажа."),
        ("Montiraj noge ili stopice, zatim nivelisi element na mestu ugradnje.", "Установите ножки, затем выровняйте модуль на месте монтажа."),
        ("Tek kada je korpus ravan i stabilan montirajte radnu ploču ili nastavite na sledeći element.", "Устанавливайте столешницу или переходите к следующему модулю только когда корпус ровный и устойчивый."),
        ("Tek kada je korpus ravan i stabilan montiraj radnu plocu ili nastavi na sledeci element.", "Устанавливайте столешницу или переходите к следующему модулю только когда корпус ровный и устойчивый."),
        ("Ugradna rerna", "Встраиваемая духовка"), ("Ploca za kuvanje", "Варочная панель"),
        ("Ploča za kuvanje", "Варочная панель"), ("Fioka ispod rerne", "Ящик под духовкой"),
    ]
    for src, dst in replacements:
        txt = txt.replace(src, dst)
    return txt


def _polish_instruction_line_ptbr(line: str) -> str:
    txt = _polish_instruction_line_en(_translate_instruction_line(line, "en"))
    exact = {
        "-- PANEL ELEMENT --": "-- PAINEL --",
        "-- SINK BASE UNIT --": "-- MÓDULO INFERIOR DA PIA --",
        "-- BASE UNIT PARTS LIST --": "-- LISTA DE PEÇAS DO MÓDULO INFERIOR --",
        "-- WALL UNIT PARTS LIST --": "-- LISTA DE PEÇAS DO MÓDULO SUPERIOR --",
        "-- TOP FILLER PARTS LIST --": "-- LISTA DE PEÇAS DO PREENCHIMENTO SUPERIOR --",
        "-- FREESTANDING DISHWASHER --": "-- LAVA-LOUÇAS DE PISO --",
        "-- FREESTANDING RANGE --": "-- FOGÃO DE PISO --",
        "-- FREESTANDING REFRIGERATOR --": "-- GELADEIRA DE PISO --",
        "-- DISHWASHER OPENING PARTS LIST --": "-- LISTA DE PEÇAS DO VÃO DA LAVA-LOUÇAS --",
        "-- STEP 1 - VERIFY DIMENSIONS --": "-- PASSO 1 - CONFERIR MEDIDAS --",
        "-- STEP 2 - POSITIONING --": "-- PASSO 2 - POSICIONAMENTO --",
        "-- STEP 3 - FIXING --": "-- PASSO 3 - FIXAÇÃO --",
        "-- STEP 4 - FINAL CHECK --": "-- PASSO 4 - CONFERÊNCIA FINAL --",
        "-- KORAK 5 - ZAVRSNA PROVERA --": "-- PASSO 5 - CONFERÊNCIA FINAL --",
        "-- STEP 1 - PREPARE THE OPENING --": "-- PASSO 1 - PREPARAR O VÃO --",
        "-- STEP 2 - CONNECTIONS --": "-- PASSO 2 - CONEXÕES --",
        "-- STEP 3 - INSTALL THE MACHINE --": "-- PASSO 3 - INSTALAR A MÁQUINA --",
        "-- STEP 4 - DISHWASHER FRONT --": "-- PASSO 4 - FRENTE DA LAVA-LOUÇAS --",
        "-- STEP 1 - CARCASS --": "-- PASSO 1 - CORPO --",
        "-- STEP 2 - BACK PANEL AND CUT-OUTS --": "-- PASSO 2 - FUNDO E RECORTES --",
        "-- STEP 3 - DOORS --": "-- PASSO 3 - PORTAS --",
        "-- STEP 4 - WORKTOP AND SINK --": "-- PASSO 4 - BANCADA E PIA --",
        "-- STEP 1 - SIDE PANELS --": "-- PASSO 1 - LATERAIS --",
        "-- STEP 2 - BOTTOM AND TOP PANEL --": "-- PASSO 2 - PAINEL INFERIOR E SUPERIOR --",
        "-- STEP 3 - BACK PANEL --": "-- PASSO 3 - FUNDO --",
        "-- STEP 4 - DRAWERS --": "-- PASSO 4 - GAVETAS --",
        "-- STEP 4 - DOORS + DRAWER --": "-- PASSO 4 - PORTAS + GAVETA --",
        "-- STEP 4 - WASTE SORTER --": "-- PASSO 4 - LIXEIRA DESLIZANTE --",
        "-- STEP 4 - NARROW PULL-OUT UNIT --": "-- PASSO 4 - MÓDULO ESTREITO DESLIZANTE --",
        "-- STEP 4 - COOKING UNIT --": "-- PASSO 4 - MÓDULO DE COZIMENTO --",
        "-- STEP 4 - SHELVES --": "-- PASSO 4 - PRATELEIRAS --",
        "-- STEP 4 - HOB --": "-- PASSO 4 - COOKTOP --",
        "-- STEP 4 - BUILT-IN OVEN --": "-- PASSO 4 - FORNO DE EMBUTIR --",
        "-- STEP 5 - LEGS AND POSITIONING --": "-- PASSO 5 - PÉS E POSICIONAMENTO --",
        "-- STEP 2 - DOORS / MECHANISM --": "-- PASSO 2 - PORTAS / MECANISMO --",
        "-- STEP 3 - WALL INSTALLATION --": "-- PASSO 3 - FIXAÇÃO NA PAREDE --",
        "-- STEP 1 - ASSEMBLE THE TOP UNIT --": "-- PASSO 1 - MONTAR O MÓDULO SUPERIOR --",
        "-- STEP 2 - CONNECT TO THE TALL UNIT --": "-- PASSO 2 - LIGAR AO MÓDULO ALTO --",
        "-- STEP 3 - SHELF --": "-- PASSO 3 - PRATELEIRA --",
        "-- STEP 2 - BACK PANEL --": "-- PASSO 2 - FUNDO --",
        "-- STEP 3 - BUILT-IN REFRIGERATOR --": "-- PASSO 3 - GELADEIRA DE EMBUTIR --",
        "-- STEP 3 - OVEN + MICROWAVE --": "-- PASSO 3 - FORNO + MICRO-ONDAS --",
        "-- STEP 3 - OVEN TOWER --": "-- PASSO 3 - TORRE DO FORNO --",
        "-- STEP 3 - GLASS DOORS --": "-- PASSO 3 - PORTAS DE VIDRO --",
        "-- STEP 4 - POSITIONING --": "-- PASSO 4 - POSICIONAMENTO --",
    }
    if txt in exact:
        return exact[txt]

    sr_replacements = [
        ("Umetni dno izmedju bocnih stranica i spoji ga prema busenjima.", "Insira o painel inferior entre as laterais e una conforme as furações."),
        ("Zatim postavi gornju plocu i proveri da korpus ostane ravan.", "Depois coloque o painel superior e confira se o corpo permanece alinhado."),
        ("Umetni ledjnu plocu na zadnju stranu elementa.", "Insira o painel traseiro na parte de trás do módulo."),
        ("Pre konacnog stezanja proveri dijagonale da element bude pod pravim uglom.", "Antes do aperto final, confira as diagonais para deixar o módulo no esquadro."),
        ("Prvo proveri da li rerna slobodno ulazi u otvor korpusa i da li ima prostora za ventilaciju.", "Primeiro confira se o forno entra livremente no vão do corpo e se há espaço para ventilação."),
        ("Zatim isezi otvor u radnoj ploci prema šablonu ploce za kuvanje.", "Depois recorte a abertura na bancada conforme o gabarito do cooktop."),
        ("Zatim isezi otvor u radnoj ploci prema sablonu ploce za kuvanje.", "Depois recorte a abertura na bancada conforme o gabarito do cooktop."),
        ("Lazni front ili front fioke montiraj tek nakon probe zazora oko rerne i vrata rerne.", "Monte a frente falsa ou a frente da gaveta somente depois de conferir as folgas ao redor do forno e da porta do forno."),
        ("Montiraj noge ili stopice, zatim nivelisi element na mestu ugradnje.", "Monte os pés, depois nivele o módulo no local de instalação."),
        ("Tek kada je korpus ravan i stabilan montiraj radnu plocu ili nastavi na sledeci element.", "Somente quando o corpo estiver nivelado e estável, monte a bancada ou continue para o próximo módulo."),
        ("Izbusiti rupe za konfirmate i zleb za ledjnu plocu.", "Fure para os parafusos confirmat e faça o canal do painel traseiro."),
        ("Ugradna rerna", "Forno de embutir"),
        ("Ploca za kuvanje", "Cooktop"),
        ("Fioka ispod rerne", "Gaveta sob o forno"),
        ("#3 - Rerna+ploča", "#3 - Forno+cooktop"),
        ("Rerna+ploča", "Forno+cooktop"),
        ("Rerna+ploca", "Forno+cooktop"),
        ("KORAK 4 - VRATA", "PASSO 4 - PORTAS"),
        ("KORAK 3 - MONTAŽA NA ZID", "PASSO 3 - FIXAÇÃO NA PAREDE"),
        ("KORAK 5 - ZAVRSNA PROVERA", "PASSO 5 - CONFERÊNCIA FINAL"),
        ("Fure the confirmat holes and recorte the groove for the back panel.", "Fure para os parafusos confirmat e faça o canal do painel traseiro."),
        ("Monte the hinges, hang the portas and set 2 mm reveals.", "Monte as dobradiças, pendure as portas e ajuste folgas de 2 mm."),
        ("Run water and confira whether the trap, tap and all connections leak.", "Abra a água e confira se o sifão, a torneira e todas as conexões vazam."),
        ("Only when everything is dry and leak-free should you close the unit and continue to the next module.", "Só feche o módulo e continue para o próximo quando tudo estiver seco e sem vazamentos."),
        ("Tek kada je element ravan i čvrsto vezan, nastavi na sledeći zidni element ili front.", "Só continue para o próximo módulo superior ou frente quando o módulo estiver nivelado e bem fixado."),
        ("Tek kada je element ravan i čvrsto vezan, nastavi na sledeći zidni element ili frente.", "Só continue para o próximo módulo superior ou frente quando o módulo estiver nivelado e bem fixado."),
        ("rernu", "forno"),
        ("rerne", "forno"),
        ("radnoj ploci", "bancada"),
        ("radnu plocu", "bancada"),
        ("radna ploca", "bancada"),
        ("ploce za kuvanje", "cooktop"),
        ("sablonu", "gabarito"),
        ("šablonu", "gabarito"),
        ("sledeci element", "próximo módulo"),
    ]
    for src, dst in sr_replacements:
        txt = txt.replace(src, dst)

    replacements = [
        ("Filler panel", "Painel de preenchimento"),
        ("End side panel", "Painel lateral de acabamento"),
        ("Left side panel", "Lateral esquerda"),
        ("Right side panel", "Lateral direita"),
        ("Back panel", "Painel traseiro"),
        ("Top panel", "Painel superior"),
        ("Bottom panel", "Painel inferior"),
        ("Lower service front", "Frente de serviço inferior"),
        ("Upper appliance front", "Frente superior do eletrodoméstico"),
        ("Lower appliance front", "Frente inferior do eletrodoméstico"),
        ("Appliance front", "Frente do eletrodoméstico"),
        ("Drawer front", "Frente da gaveta"),
        ("Drawer fronts", "Frentes das gavetas"),
        ("Narrow-unit front", "Frente do módulo estreito"),
        ("Sink-base doors", "Portas do módulo da pia"),
        ("Doors below sink", "Portas sob a pia"),
        ("Doors below hob", "Portas sob o cooktop"),
        ("Oven front", "Frente do forno"),
        ("Glass doors", "Portas de vidro"),
        ("Doors", "Portas"),
        ("Hinges", "Dobradiças"),
        ("Glass-door hinges", "Dobradiças para vidro"),
        ("Drawer runners", "Corrediças da gaveta"),
        ("runner", "corrediça"),
        ("Drawer box", "Caixa da gaveta"),
        ("Built-in oven", "Forno de embutir"),
        ("Built-in microwave", "Micro-ondas de embutir"),
        ("Hob", "Cooktop"),
        ("Built-in dishwasher", "Lava-louças de embutir"),
        ("Front mounting kit", "Kit de montagem da frente"),
        ("Cross rail", "Travessa"),
        ("Worktop support rail", "Suporte da bancada"),
        ("Legs", "Pés"),
        ("Intermediate shelf", "Prateleira intermediária"),
        ("Adjustable shelves", "Prateleiras ajustáveis"),
        ("Adjustable shelf", "Prateleira ajustável"),
        ("Shelf supports", "Suportes de prateleira"),
        ("Narrow pull-out mechanism", "Mecanismo estreito deslizante"),
        ("Baskets / supports", "Cestos / suportes"),
        ("Lift-up mechanism", "Mecanismo basculante"),
        ("Front connection kit", "Kit de conexão da frente"),
        ("Front connection kits", "Kits de conexão das frentes"),
        ("Ventilation spacer kit", "Kit espaçador de ventilação"),
        ("pcs", "un."),
        ("pc", "un."),
        ("Carcass", "Corpo"),
        ("carcass", "corpo"),
        ("worktop", "bancada"),
        ("Worktop", "Bancada"),
        ("sink", "pia"),
        ("Sink", "Pia"),
        ("oven", "forno"),
        ("Oven", "Forno"),
        ("hob", "cooktop"),
        ("Hob", "Cooktop"),
        ("fronts", "frentes"),
        ("front", "frente"),
        ("doors", "portas"),
        ("door", "porta"),
        ("wall", "parede"),
        ("Wall", "Parede"),
        ("opening", "vão"),
        ("Opening", "Vão"),
        ("factory template", "gabarito do fabricante"),
        ("manufacturer's template", "gabarito do fabricante"),
        ("manufacturer's instructions", "instruções do fabricante"),
        ("according to", "conforme"),
        ("before", "antes de"),
        ("after", "depois de"),
        ("Check", "Confira"),
        ("check", "confira"),
        ("Install", "Instale"),
        ("install", "instale"),
        ("Fit", "Monte"),
        ("fit", "monte"),
        ("Attach", "Fixe"),
        ("fix", "fixe"),
        ("Slide", "Insira"),
        ("insert", "insira"),
        ("Verify", "Confira"),
        ("verify", "confira"),
        ("Level", "Nivele"),
        ("level", "nivele"),
        ("Leave", "Deixe"),
        ("leave", "deixe"),
        ("Cut", "Recorte"),
        ("cut", "recorte"),
        ("Protect", "Proteja"),
        ("protect", "proteja"),
        ("Mark", "Marque"),
        ("mark", "marque"),
        ("Assemble", "Monte"),
        ("assemble", "monte"),
        ("Drill", "Fure"),
        ("drill", "fure"),
        ("final check", "conferência final"),
        ("Final check", "Conferência final"),
    ]
    for src, dst in replacements:
        txt = txt.replace(src, dst)
    txt = txt.replace("  ", "  ")
    return txt


def _polish_instruction_line_zhcn(line: str) -> str:
    txt = _translate_instruction_line(line, "en")
    exact = {
        "-- STEP 1 - VERIFY DIMENSIONS --": "-- 步骤 1 - 检查尺寸 --",
        "-- STEP 2 - POSITIONING --": "-- 步骤 2 - 定位 --",
        "-- STEP 3 - FIXING --": "-- 步骤 3 - 固定 --",
        "-- STEP 4 - FINAL CHECK --": "-- 步骤 4 - 最终检查 --",
        "-- STEP 1 - PREPARE THE OPENING --": "-- 步骤 1 - 准备开口 --",
        "-- STEP 2 - CONNECTIONS --": "-- 步骤 2 - 连接 --",
        "-- STEP 3 - INSTALL THE MACHINE --": "-- 步骤 3 - 安装设备 --",
        "-- STEP 4 - DISHWASHER FRONT --": "-- 步骤 4 - 洗碗机门板 --",
        "-- STEP 1 - CARCASS --": "-- 步骤 1 - 柜体 --",
        "-- STEP 2 - BACK PANEL AND CUT-OUTS --": "-- 步骤 2 - 背板和开孔 --",
        "-- STEP 3 - DOORS --": "-- 步骤 3 - 门板 --",
        "-- STEP 4 - WORKTOP AND SINK --": "-- 步骤 4 - 台面和水槽 --",
        "-- STEP 1 - SIDE PANELS --": "-- 步骤 1 - 侧板 --",
        "-- STEP 2 - BOTTOM AND TOP PANEL --": "-- 步骤 2 - 底板和顶板 --",
        "-- STEP 3 - BACK PANEL --": "-- 步骤 3 - 背板 --",
        "-- STEP 4 - DRAWERS --": "-- 步骤 4 - 抽屉 --",
        "-- STEP 4 - DOORS + DRAWER --": "-- 步骤 4 - 门板 + 抽屉 --",
        "-- KORAK 4 - VRATA --": "-- 步骤 4 - 门板 --",
        "-- STEP 2 - DOORS / MECHANISM --": "-- 步骤 2 - 门板 / 机构 --",
        "-- KORAK 3 - MONTAŽA NA ZID --": "-- 步骤 3 - 墙面安装 --",
        "-- STEP 5 - LEGS AND POSITIONING --": "-- 步骤 5 - 柜脚和定位 --",
        "-- KORAK 5 - ZAVRSNA PROVERA --": "-- 步骤 5 - 最终检查 --",
        "-- STEP 3 - WALL INSTALLATION --": "-- 步骤 3 - 墙面安装 --",
    }
    if txt in exact:
        return exact[txt]
    replacements = [
        ("Left side panel", "左侧板"), ("Right side panel", "右侧板"), ("Back panel", "背板"),
        ("Top panel", "顶板"), ("Bottom panel", "底板"), ("Drawer front", "抽屉门板"),
        ("Drawer fronts", "抽屉门板"), ("Drawer box", "抽屉箱体"), ("Doors", "门板"),
        ("Hinges", "铰链"), ("Drawer runners", "抽屉滑轨"), ("Built-in oven", "嵌入式烤箱"),
        ("Hob", "灶具"), ("Worktop", "台面"), ("Legs", "柜脚"), ("Carcass", "柜体"),
        ("sink", "水槽"), ("Sink", "水槽"), ("oven", "烤箱"), ("Oven", "烤箱"),
        ("wall", "墙面"), ("Wall", "墙面"), ("opening", "开口"), ("Opening", "开口"),
        ("manufacturer's template", "厂家模板"), ("manufacturer's instructions", "厂家说明"),
        ("Connect water, drain and power according to the manufacturer's instructions.", "按照厂家说明连接给水、排水和电源。"),
        ("Mark the cut-out in the worktop using the sink template.", "按水槽模板在台面上标记开孔。"),
        ("Protect the cut edge of the opening from moisture before mounting the sink.", "安装水槽前先对开孔切边做防潮处理。"),
        ("Insert the back panel and verify the diagonals.", "装入背板并检查对角线。"),
        ("Fit the hinges, hang the doors and set 2 mm reveals.", "安装铰链，挂上门板，并调到 2 mm 缝隙。"),
        ("Assemble the side panels, bottom and top panel.", "组装侧板、底板和顶板。"),
        ("Install the doors or hardware according to the unit type.", "按模块类型安装门板或五金。"),
        ("Umetni dno izmedju bocnih stranica i spoji ga prema busenjima.", "把底板装在两块侧板之间，并按预钻孔连接。"),
        ("Zatim postavi gornju plocu i proveri da korpus ostane ravan.", "然后装上顶板，并检查柜体是否保持方正。"),
        ("Umetni ledjnu plocu na zadnju stranu elementa.", "把背板装到模块后侧。"),
        ("Pre konacnog stezanja proveri dijagonale da element bude pod pravim uglom.", "最终拧紧前检查对角线，确保模块方正。"),
        ("KORAK 4 - VRATA", "步骤 4 - 门板"),
        ("KORAK 3 - MONTAŽA NA ZID", "步骤 3 - 墙面安装"),
        ("STEP 2 - DOORS / MECHANISM", "步骤 2 - 门板 / 机构"),
        ("STEP 5 - LEGS AND POSITIONING", "步骤 5 - 柜脚和定位"),
        ("KORAK 5 - ZAVRSNA PROVERA", "步骤 5 - 最终检查"),
        ("Montiraj šarke, okači vrata i podesi male razmake tako da se vrata lako otvaraju i ne zapinju.", "安装铰链，挂上门板，并调整缝隙使门板开合顺畅。"),
        ("Obeleži tačnu visinu na zidu, montiraj zidni nosač ili šinu i tek onda okači element.", "先在墙上标出准确高度，安装挂件或挂轨，然后再挂上模块。"),
        ("Pre završnog stezanja proveri libelom da je element potpuno ravan levo-desno i napred-nazad.", "最终拧紧前用水平尺检查模块左右和前后都保持水平。"),
        ("Tek kada je element ravan i čvrsto vezan, nastavi na sledeći zidni element ili front.", "只有模块调平并固定牢靠后，才继续下一个吊柜或门板。"),
    ]
    for src, dst in replacements:
        txt = txt.replace(src, dst)
    return txt


def _polish_instruction_line_hi(line: str) -> str:
    txt = _translate_instruction_line(line, "en")
    exact = {
        "-- STEP 1 - VERIFY DIMENSIONS --": "-- चरण 1 - माप जांचें --",
        "-- STEP 2 - POSITIONING --": "-- चरण 2 - स्थिति तय करें --",
        "-- STEP 3 - FIXING --": "-- चरण 3 - फिक्सिंग --",
        "-- STEP 4 - FINAL CHECK --": "-- चरण 4 - अंतिम जांच --",
        "-- STEP 1 - PREPARE THE OPENING --": "-- चरण 1 - ओपनिंग तैयार करें --",
        "-- STEP 2 - CONNECTIONS --": "-- चरण 2 - कनेक्शन --",
        "-- STEP 3 - INSTALL THE MACHINE --": "-- चरण 3 - मशीन लगाएँ --",
        "-- STEP 4 - DISHWASHER FRONT --": "-- चरण 4 - डिशवॉशर फ्रंट --",
        "-- STEP 1 - CARCASS --": "-- चरण 1 - कार्कस --",
        "-- STEP 2 - BACK PANEL AND CUT-OUTS --": "-- चरण 2 - बैक पैनल और कट-आउट --",
        "-- STEP 3 - DOORS --": "-- चरण 3 - दरवाज़े --",
        "-- STEP 4 - WORKTOP AND SINK --": "-- चरण 4 - वर्कटॉप और सिंक --",
        "-- STEP 1 - SIDE PANELS --": "-- चरण 1 - साइड पैनल --",
        "-- STEP 2 - BOTTOM AND TOP PANEL --": "-- चरण 2 - बॉटम और टॉप पैनल --",
        "-- STEP 3 - BACK PANEL --": "-- चरण 3 - बैक पैनल --",
        "-- STEP 4 - DRAWERS --": "-- चरण 4 - दराज़ --",
        "-- STEP 4 - DOORS + DRAWER --": "-- चरण 4 - दरवाज़े + दराज़ --",
        "-- KORAK 4 - VRATA --": "-- चरण 4 - दरवाज़े --",
        "-- STEP 2 - DOORS / MECHANISM --": "-- चरण 2 - दरवाज़े / मैकेनिज़्म --",
        "-- KORAK 3 - MONTAŽA NA ZID --": "-- चरण 3 - दीवार पर इंस्टॉलेशन --",
        "-- STEP 5 - LEGS AND POSITIONING --": "-- चरण 5 - पैर और पोजिशनिंग --",
        "-- KORAK 5 - ZAVRSNA PROVERA --": "-- चरण 5 - अंतिम जांच --",
        "-- STEP 3 - WALL INSTALLATION --": "-- चरण 3 - दीवार पर इंस्टॉलेशन --",
    }
    if txt in exact:
        return exact[txt]
    replacements = [
        ("Left side panel", "बायां साइड पैनल"), ("Right side panel", "दायां साइड पैनल"),
        ("Back panel", "बैक पैनल"), ("Top panel", "टॉप पैनल"), ("Bottom panel", "बॉटम पैनल"),
        ("Drawer front", "दराज़ फ्रंट"), ("Drawer fronts", "दराज़ फ्रंट"), ("Drawer box", "दराज़ बॉक्स"),
        ("Doors", "दरवाज़े"), ("Hinges", "हिंग"), ("Drawer runners", "दराज़ स्लाइड"),
        ("Built-in oven", "बिल्ट-इन ओवन"), ("Hob", "हॉब"), ("Worktop", "वर्कटॉप"),
        ("Legs", "पैर"), ("Carcass", "कार्कस"), ("sink", "सिंक"), ("Sink", "सिंक"),
        ("oven", "ओवन"), ("Oven", "ओवन"), ("wall", "दीवार"), ("Wall", "दीवार"),
        ("opening", "ओपनिंग"), ("Opening", "ओपनिंग"), ("manufacturer's template", "निर्माता का टेम्पलेट"),
        ("manufacturer's instructions", "निर्माता के निर्देश"),
        ("Connect water, drain and power according to the manufacturer's instructions.", "निर्माता के निर्देश के अनुसार पानी, ड्रेन और पावर जोड़ें।"),
        ("Mark the cut-out in the worktop using the sink template.", "सिंक टेम्पलेट के अनुसार वर्कटॉप पर कट-आउट मार्क करें।"),
        ("Protect the cut edge of the opening from moisture before mounting the sink.", "सिंक लगाने से पहले कट किनारे को नमी से बचाएँ।"),
        ("Insert the back panel and verify the diagonals.", "बैक पैनल लगाएँ और डायगोनल जांचें।"),
        ("Fit the hinges, hang the doors and set 2 mm reveals.", "हिंग लगाएँ, दरवाज़े टाँगें और 2 mm गैप सेट करें।"),
        ("Assemble the side panels, bottom and top panel.", "साइड पैनल, बॉटम और टॉप पैनल जोड़ें।"),
        ("Install the doors or hardware according to the unit type.", "मॉड्यूल प्रकार के अनुसार दरवाज़े या हार्डवेयर लगाएँ।"),
        ("Umetni dno izmedju bocnih stranica i spoji ga prema busenjima.", "बॉटम पैनल को दोनों साइड पैनलों के बीच लगाएँ और ड्रिल होल के अनुसार जोड़ें।"),
        ("Zatim postavi gornju plocu i proveri da korpus ostane ravan.", "फिर टॉप पैनल लगाएँ और जांचें कि कार्कस सीधा रहे।"),
        ("Umetni ledjnu plocu na zadnju stranu elementa.", "मॉड्यूल के पीछे बैक पैनल लगाएँ।"),
        ("Pre konacnog stezanja proveri dijagonale da element bude pod pravim uglom.", "अंतिम कसाव से पहले डायगोनल जांचें ताकि मॉड्यूल स्क्वेयर रहे।"),
        ("KORAK 4 - VRATA", "चरण 4 - दरवाज़े"),
        ("KORAK 3 - MONTAŽA NA ZID", "चरण 3 - दीवार पर इंस्टॉलेशन"),
        ("STEP 2 - DOORS / MECHANISM", "चरण 2 - दरवाज़े / मैकेनिज़्म"),
        ("STEP 5 - LEGS AND POSITIONING", "चरण 5 - पैर और पोजिशनिंग"),
        ("KORAK 5 - ZAVRSNA PROVERA", "चरण 5 - अंतिम जांच"),
        ("Montiraj šarke, okači vrata i podesi male razmake tako da se vrata lako otvaraju i ne zapinju.", "हिंग लगाएँ, दरवाज़े टाँगें और गैप ऐसा सेट करें कि वे आसानी से खुलें और अटकें नहीं।"),
        ("Obeleži tačnu visinu na zidu, montiraj zidni nosač ili šinu i tek onda okači element.", "दीवार पर सही ऊँचाई मार्क करें, वॉल ब्रैकेट या रेल लगाएँ, फिर मॉड्यूल टाँगें।"),
        ("Pre završnog stezanja proveri libelom da je element potpuno ravan levo-desno i napred-nazad.", "अंतिम कसाव से पहले लेवल से जांचें कि मॉड्यूल दाएं-बाएं और आगे-पीछे पूरी तरह सीधा है।"),
        ("Tek kada je element ravan i čvrsto vezan, nastavi na sledeći zidni element ili front.", "जब मॉड्यूल सीधा और मजबूती से फिक्स हो जाए तभी अगले दीवार मॉड्यूल या फ्रंट पर जाएँ।"),
    ]
    for src, dst in replacements:
        txt = txt.replace(src, dst)
    return txt


def _render_instruction_line(line: str, lang: str = "sr") -> str:
    _lang = str(lang or "sr").lower().strip()
    if _lang == "en":
        return _polish_instruction_line_en(_translate_instruction_line(line, "en"))
    if _lang == "de":
        txt = _polish_instruction_line_en(_translate_instruction_line(line, "en"))
        exact = {
            "-- STEP 1 - VERIFY DIMENSIONS --": "-- SCHRITT 1 - MAẞE PRÜFEN --",
            "-- STEP 2 - POSITIONING --": "-- SCHRITT 2 - POSITIONIERUNG --",
            "-- STEP 3 - FIXING --": "-- SCHRITT 3 - BEFESTIGUNG --",
            "-- STEP 4 - FINAL CHECK --": "-- SCHRITT 4 - ENDKONTROLLE --",
            "-- STEP 1 - PREPARE THE OPENING --": "-- SCHRITT 1 - ÖFFNUNG VORBEREITEN --",
            "-- STEP 2 - CONNECTIONS --": "-- SCHRITT 2 - ANSCHLÜSSE --",
            "-- BASE UNIT PARTS LIST --": "-- LISTE DER UNTERSCHRANK-TEILE --",
            "-- SINK BASE UNIT --": "-- SPÜLEN-UNTERSCHRANK --",
            "-- STEP 3 - INSTALL THE MACHINE --": "-- SCHRITT 3 - GERÄT EINBAUEN --",
            "-- STEP 4 - DISHWASHER FRONT --": "-- SCHRITT 4 - GESCHIRRSPÜLERFRONT --",
            "-- STEP 1 - CARCASS --": "-- SCHRITT 1 - KORPUS --",
            "-- STEP 2 - BACK PANEL AND CUT-OUTS --": "-- SCHRITT 2 - RÜCKWAND UND AUSSCHNITTE --",
            "-- STEP 3 - DOORS --": "-- SCHRITT 3 - TÜREN --",
            "-- STEP 4 - WORKTOP AND SINK --": "-- SCHRITT 4 - ARBEITSPLATTE UND SPÜLE --",
            "-- STEP 1 - SIDE PANELS --": "-- SCHRITT 1 - SEITENTEILE --",
            "-- STEP 2 - BOTTOM AND TOP PANEL --": "-- SCHRITT 2 - BODEN UND DECKEL --",
            "-- STEP 3 - BACK PANEL --": "-- SCHRITT 3 - RÜCKWAND --",
            "-- STEP 4 - DRAWERS --": "-- SCHRITT 4 - SCHUBLADEN --",
            "-- STEP 4 - DOORS + DRAWER --": "-- SCHRITT 4 - TÜREN + SCHUBLADE --",
            "-- STEP 4 - WASTE SORTER --": "-- SCHRITT 4 - MÜLLTRENNER --",
            "-- STEP 4 - NARROW PULL-OUT UNIT --": "-- SCHRITT 4 - SCHMALER AUSZUG --",
            "-- STEP 4 - COOKING UNIT --": "-- SCHRITT 4 - KOCHMODUL --",
            "-- STEP 4 - SHELVES --": "-- SCHRITT 4 - BÖDEN --",
            "-- STEP 4 - HOB --": "-- SCHRITT 4 - KOCHFELD --",
            "-- STEP 4 - BUILT-IN OVEN --": "-- SCHRITT 4 - EINBAUBACKOFEN --",
            "-- STEP 5 - LEGS AND POSITIONING --": "-- SCHRITT 5 - FÜSSE UND AUSRICHTUNG --",
            "-- STEP 2 - DOORS / MECHANISM --": "-- SCHRITT 2 - TÜREN / BESCHLÄGE --",
            "-- STEP 3 - WALL INSTALLATION --": "-- SCHRITT 3 - WANDMONTAGE --",
            "-- STEP 1 - ASSEMBLE THE TOP UNIT --": "-- SCHRITT 1 - OBERSCHRANK MONTIEREN --",
            "-- STEP 2 - CONNECT TO THE TALL UNIT --": "-- SCHRITT 2 - MIT HOCHSCHRANK VERBINDEN --",
            "-- STEP 3 - SHELF --": "-- SCHRITT 3 - BODEN --",
            "-- STEP 2 - BACK PANEL --": "-- SCHRITT 2 - RÜCKWAND --",
            "-- STEP 3 - BUILT-IN REFRIGERATOR --": "-- SCHRITT 3 - EINBAUKÜHLSCHRANK --",
            "-- STEP 3 - OVEN + MICROWAVE --": "-- SCHRITT 3 - BACKOFEN + MIKROWELLE --",
            "-- STEP 3 - OVEN TOWER --": "-- SCHRITT 3 - BACKOFENTURM --",
            "-- STEP 3 - GLASS DOORS --": "-- SCHRITT 3 - GLASTÜREN --",
            "-- STEP 4 - POSITIONING --": "-- SCHRITT 4 - POSITIONIERUNG --",
        }
        if txt in exact:
            return exact[txt]
        replacements = [
            ("Left side panel", "Linke Seitenwand"),
            ("Right side panel", "Rechte Seitenwand"),
            ("Back panel", "Rückwand"),
            ("Top panel", "Deckel"),
            ("Bottom panel", "Boden"),
            ("Drawer front", "Schubladenfront"),
            ("Drawer fronts", "Schubladenfronten"),
            ("Drawer box", "Schubladenkasten"),
            ("Doors", "Türen"),
            ("Hinges", "Scharniere"),
            ("Drawer runners", "Schubladenführungen"),
            ("Built-in oven", "Einbaubackofen"),
            ("Hob", "Kochfeld"),
            ("Worktop", "Arbeitsplatte"),
            ("Legs", "Füße"),
            ("Carcass", "Korpus"),
            ("Sink", "Spüle"),
            ("sink", "Spüle"),
            ("Oven", "Backofen"),
            ("oven", "Backofen"),
            ("Wall", "Wand"),
            ("wall", "Wand"),
            ("Opening", "Öffnung"),
            ("opening", "Öffnung"),
            ("manufacturer's template", "Herstellerschablone"),
            ("manufacturer's instructions", "Herstelleranleitung"),
            ("Connect water, drain and power according to the manufacturer's instructions.", "Schließe Wasser, Abfluss und Strom nach der Herstelleranleitung an."),
            ("Mark the cut-out in the worktop using the sink template.", "Markiere den Ausschnitt in der Arbeitsplatte mit der Spülenschablone."),
            ("Protect the cut edge of the opening from moisture before mounting the sink.", "Schütze die Schnittkante des Ausschnitts vor Feuchtigkeit, bevor die Spüle montiert wird."),
            ("Insert the back panel and verify the diagonals.", "Setze die Rückwand ein und prüfe die Diagonalen."),
            ("Fit the hinges, hang the doors and set 2 mm reveals.", "Montiere die Scharniere, hänge die Türen ein und stelle 2 mm Fugen ein."),
            ("Assemble the side panels, bottom and top panel.", "Montiere Seitenwände, Boden und Deckel."),
            ("Install the doors or hardware according to the unit type.", "Montiere Türen oder Beschläge entsprechend dem Modultyp."),
            ("Take the left and right side panel and place them upright so the edged front edges face forward.", "Nimm die linke und rechte Seitenwand und stelle sie so auf, dass die bekanteten Vorderkanten nach vorne zeigen."),
            ("Drill the confirmat holes and machine the groove for the back panel.", "Bohre die Confirmat-Bohrungen und fräse die Nut für die Rückwand."),
            ("Required tools and hardware", "Benötigte Werkzeuge und Beschläge"),
            ("Before assembly check", "Vor der Montage prüfen"),
            ("Montage guide", "Montageanleitung"),
            ("BASE UNIT PARTS LIST", "LISTE DER UNTERSCHRANK-TEILE"),
            ("SINK BASE UNIT", "SPÜLEN-UNTERSCHRANK"),
            ("Check", "Prüfe"),
            ("check", "prüfe"),
            ("Verify", "Prüfe"),
            ("verify", "prüfe"),
            ("Install", "Montiere"),
            ("install", "montiere"),
            ("Mount", "Montiere"),
            ("mount", "montiere"),
            ("Assemble", "Montiere"),
            ("assemble", "montiere"),
            ("Position", "Positioniere"),
            ("position", "positioniere"),
            ("Adjust", "Justiere"),
            ("adjust", "justiere"),
            ("Mark", "Markiere"),
            ("mark", "markiere"),
            ("Protect", "Schütze"),
            ("protect", "schütze"),
            ("Drill", "Bohre"),
            ("drill", "bohre"),
            ("Cut", "Schneide"),
            ("cut", "schneide"),
            ("Final check", "Endkontrolle"),
            ("final check", "Endkontrolle"),
        ]
        for src, dst in replacements:
            txt = txt.replace(src, dst)
        return txt
    if _lang == "es":
        return _polish_instruction_line_es(line)
    if _lang == "ru":
        return _polish_instruction_line_ru(line)
    if _lang == "pt-br":
        return _polish_instruction_line_ptbr(line)
    if _lang == "zh-cn":
        return _polish_instruction_line_zhcn(line)
    if _lang == "hi":
        return _polish_instruction_line_hi(line)
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
                    _line("KORAK 3 - FRIŽIDER + ZAMRZIVAČ"),
                    "  Uvucite uređaj u gotov korpus tek kada je kolona potpuno ravna i stabilna.",
                    "  Proverite obavezne ventilacione zazore pre konačnog pričvršćivanja uređaja.",
                    "  Gornji i donji front montirajte pomoću fabričkog seta za vezu vrata.",
                ]
            else:
                steps += [
                    "",
                    _line("KORAK 3 - UGRADNI FRIŽIDER"),
                    "  Uvucite uređaj u gotov korpus tek nakon nivelacije kolone.",
                    "  Proverite ventilacione zazore i probu otvaranja vrata pre montaže fronta.",
                    "  Front uređaja montirajte tek kada ste sigurni da vrata uređaja rade bez zapinjanja.",
                ]
        elif "OVEN_MICRO" in tid:
            steps += [
                "",
                _line("KORAK 3 - RERNA + MIKROTALASNA"),
                "  Pre unošenja uređaja proverite obe zone i obaveznu ventilaciju.",
                "  Prvo ugradi mikrotalasnu, zatim rernu u donju zonu.",
                "  Donji servisni front montirajte tek nakon probe otvaranja i provere zazora oko oba uređaja.",
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
