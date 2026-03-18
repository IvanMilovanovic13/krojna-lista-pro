# Zazori i Otvaranje Vrata

Datum: `12.03.2026`

Svrha:
- da bude jasno koji zazori su vec uracunati u generatoru
- da bude jasno sta jos NIJE puna provera sudara pri otvaranju
- da ovo bude referenca za dalji razvoj, posebno za `L kuhinju`

## 1. Zazori koji su vec uracunati

### 1.1 Front fuga

Aktivni proizvodni profil trenutno koristi:
- `front_gap_mm = 2.0`

Izvor:
- `cutlist.py` -> `MANUFACTURING_PROFILES`

Znacenje:
- generator racuna spoljne i medjufuge izmedju frontova
- to je proizvodna fuga, ne samo vizuelni detalj

### 1.2 Dvoja vrata na jednom elementu

Za element sa 2 vrata generator racuna:
- ukupna korisna sirina fronta:
  - `fw = w - 2 * front_gap`
- sirina jednog krila:
  - `door_w = (fw - front_gap) / 2`
- visina jednog krila:
  - `door_h = h - 2 * front_gap`

To znaci da su po sirini uracunata 3 zazora:
- leva spoljna fuga
- srednja fuga izmedju dva krila
- desna spoljna fuga

Po visini su uracunata 2 zazora:
- gornja fuga
- donja fuga

Primer:
- element `800 x 600`
- `front_gap = 2 mm`

Racun:
- `fw = 800 - 4 = 796 mm`
- `door_w = (796 - 2) / 2 = 397 mm`
- `door_h = 600 - 4 = 596 mm`

Zakljucak:
- za zatvoren polozaj, dva krila `397 x 596` se ne preklapaju i ne sudaraju

### 1.3 Jednokrilna vrata

Za jednokrilni front generator racuna:
- sirina vrata:
  - `door_w = w - 2 * front_gap`
- visina vrata:
  - `door_h = h - 2 * front_gap`

Znaci:
- uracunata je leva i desna fuga
- uracunata je gornja i donja fuga

### 1.4 Fioke

Za frontove fioka generator uracunava:
- po visini:
  - `front_fioke = visina_segmenta - 2 * front_gap`

Za vise fioka postoji i kontrola:
- minimalna fioka ne sme ispod `80 mm`
- zbir fioka mora ostaviti tehnicku rezervu

### 1.5 Vrata + fioka

Za kombi element:
- vrata imaju gornju i donju fugu
- front fioke ima svoje oduzimanje po `front_gap`
- postoji validacija da raspodela vrata/fioka ne bude nerealna

### 1.6 Appliance frontovi

Za appliance frontove (`ugradni frizider`, `frizider + zamrzivac`, `MZS front`, servisni frontovi):
- frontovi se takodje racunaju sa `front_gap`
- nema preklapanja u zatvorenom stanju po samoj meri fronta

### 1.7 Zidni i montazni zazori

U sistemu vec postoje i drugi zazori koji nisu "fuga vrata", ali su bitni:
- levi i desni montazni clearance uz zid
- vertikalni razmak baza -> radna ploca -> gornji elementi
- clearance do plafona za `wall_upper` i `tall_top`
- support span pravilo za `wall_upper` i `tall_top`

## 2. Sta je provereno i uracunato

Trenutno je provereno:
- da se frontovi po meri ne preklapaju kada su zatvoreni
- da dvoja vrata imaju srednju fugu
- da jednokrilna vrata ne budu prevelika za osnovni laicki workflow
- da `wall_upper` i `tall_top` imaju pun oslonac
- da visine fioka i vrata+fioka budu realne
- da moduli ne prolaze kroz vrata/prozore i slicne hard prepreke

## 3. Sta NIJE jos puna provera pri otvaranju

Ovo je vazno:

trenutni sistem NE radi punu kinematicku proveru otvaranja vrata.

To znaci da jos nije potpuno provereno:
- da li ce se vrata otvoriti ako su preblizu zidu sa strane
- da li ce rucka udariti u zid pri otvaranju
- da li ce se vrata susednih elemenata sudariti pri istovremenom otvaranju
- da li ce vrata ugaonog elementa u `L kuhinji` udariti u susedni front
- da li ce se appliance front i susedna vrata sudariti u uglu
- da li ce `WALL_2DOOR` ili `TALL_DOORS` uz bocni zid traziti dodatni filer

Drugim recima:
- `zatvoren polozaj` je matematicki pokriven
- `putanja otvaranja u prostoru` jos nije kompletno simulirana

## 4. Strucni zakljucak

Da, potrebno je uvesti dodatna pravila za sudar vrata pri otvaranju.

Najvazniji otvoreni rizici su:
- element uz levi/desni zid bez dovoljnog servisnog zazora
- `BASE_CORNER` i `WALL_CORNER` sa susednim vratima/frontovima
- `L kuhinja` gde front jednog kraka ulazi u zonu otvaranja drugog kraka
- rucke koje mogu udariti u zid ili susedni front

## 5. Predlog sledecih pravila

### 5.1 Pravilo uz bocni zid

Ako je jednokrilni element direktno uz zid:
- proveriti stranu otvaranja
- traziti minimalni bočni servisni zazor ili `filer`

Prakticni minimum za prvu verziju pravila:
- warning ako je `jednokrilni element` na manje od `30-50 mm` od bocnog zida na strani rucke/otvaranja

### 5.2 Pravilo za dva susedna jednokrilna elementa

Ako su dva jednokrilna elementa susedna:
- proveriti da li se rucke i putanje otvaranja konfliktuju

Prva verzija:
- warning ako su oba jednokrilna i oba otvaraju ka istom spoju

### 5.3 Pravilo za ugaoni element

Za `BASE_CORNER` i `WALL_CORNER`:
- proveriti da li susedni element ima dovoljno mesta
- proveriti da li front ugla i front suseda mogu da se otvore bez udara

### 5.4 Pravilo za L kuhinju

Za `L kuhinju` treba posebna kontrola:
- frontovi na zidu A prema uglu
- frontovi na zidu B prema uglu
- rucke prema uglu
- appliance frontovi prema uglu

Bez ovog pravila `L kuhinja` nije potpuno zatvorena za realno otvaranje frontova.

## 6. Preporuka za agendu

Ovo treba uvesti kao poseban naredni blok:
- `Door Opening Collision Rules`

Minimalni redosled:
1. bočni zid + jednokrilna vrata
2. ugaoni element + sused
3. L kuhinja + ugaoni sudari
4. tek kasnije puna 3D/kinematička simulacija

## 7. Najkraci zakljucak

Trenutno:
- frontovi po meri JESU dobro proracunati za zatvoren polozaj
- dve fronte na elementu od `800 mm` se nece preklapati po merama

Ali:
- puna provera sudara pri otvaranju jos NIJE kompletno uvedena

Zato je sledeci ispravan posao:
- uvesti posebna pravila za otvaranje uz zid i u `L kuhinji`
