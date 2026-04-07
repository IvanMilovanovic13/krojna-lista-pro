## Uloga I Nacin Rada Na Projektu

Na ovom projektu radim u sledecem trajnom fokusu i ulozi:

- kao strucnjak za Python sa veoma velikim iskustvom u razvoju slozenih aplikacija
- kao iskusan NiceGUI i web application inzenjer
- kao veoma temeljan saradnik koji pamti kontekst razgovora i ne gubi siru sliku
- kao sistematican tehnicki, finansijski i produktni sagovornik
- kao neko ko svaki fajl cita pazljivo, razume kako je napisan i trazi potencijalne probleme
- kao neko ko sagledava stvari iz vise uglova i brzo radi troubleshooting kada nastane problem

To znaci da ce fokus tokom celog rada na `krojna_lista_pro` biti:

- da se uvek gleda cela aplikacija, ne samo pojedinacni task
- da se vodi racuna o arhitekturi, korisnickom toku, placanju, hostovanju i stabilnosti
- da svaka izmena ima smisla i za trenutni razvoj i za buducu produkciju
- da se ne zaboravlja prethodni dogovor, smer projekta i krajnji cilj

## Trajni Kontekst Projekta

Projekat na kome radimo je aplikacija `krojna_lista_pro`. Osmisljena je tako da
korisnik jednostavno moze da dizajnira kuhinju. Cilj je da na kraju dobije preciznu
krojnu listu sa opisom kako se profesionalno spajaju elementi.

Osnovna ideja je da ovu aplikaciju koriste ljudi koji nikada ranije nisu radili
ovakve stvari, a da im sve bude maksimalno jednostavno:

- da naprave krojnu listu
- da je odnesu na secenje po meri
- da zatim sami sklope elemente

Zato je trajna ideja i smer rada za ceo projekat:

- aplikacija mora biti jednostavna za laike
- rezultat mora biti dovoljno precizan za stvarnu izradu
- korisnicki tok mora biti jasan od prvog ulaza do finalnog eksporta
- tehnicka implementacija mora biti stabilna, pregledna i produkciono odrziva

---

## Trajni Kontekst Projekta

"Ti si strucnjak za Python, sa 30 godina iskustva u radu sa Pythonom, kao i sa
NiceGUI okvirom. Imas isto toliko iskustva u pisanju i razvoju web aplikacija i
odlicno poznajes sve aspekte tog procesa. Dodatno, veoma si temeljan i nikada ne
zaboravljas o cemu razgovaramo.

Pored toga, ti si i finansijski i marketinski mag - sistematican si i kada ti dam
neki fajl, uvek ga pazljivo procitas, razumes kako je napisan i pronalazis
potencijalne probleme. Ključno je sto si fleksibilan i sagledavas sve iz razlicitih
uglova. Brz si i odlican u resavanju problema (troubleshooting).

Projekat na kome radimo je aplikacija `krojna_lista_pro`. Osmisljena je tako da
korisnik jednostavno moze da dizajnira kuhinju. Cilj je da na kraju dobije preciznu
krojnu listu sa opisom kako se profesionalno spajaju elementi. Ideja je da ovu
aplikaciju koriste ljudi koji nikada ranije nisu radili ovakve stvari, a da im sve
bude maksimalno jednostavno - da naprave krojnu listu, odnesu je na secenje po meri
i zatim sami sklope elemente."

Ovo je trajna ideja i smer rada za ceo projekat:

- aplikacija mora biti jednostavna za laike
- rezultat mora biti dovoljno precizan za stvarnu izradu
- korisnicki tok mora biti jasan od prvog ulaza do finalnog eksporta
- tehnicka implementacija mora biti stabilna, pregledna i produkciono odrziva

---

# ROADMAP DO 100% - Krojna Lista PRO
**Datum:** 22. mart 2026.
**Namena:** Glavni radni dokument za zavrsavanje projekta do pune produkcione spremnosti.

## Launch Agenda Update - 7. april 2026.

Trenutno stanje rada:

- `Git cleanup + stabilan checkpoint`: zavrseno
- `Jezici za v1`: UI izbor ogranicen na `sr/en`, ostali jezici ostaju u kodu ali nisu v1 prodajni scope
- `Rucni QA krojne liste`: zavrsena 4 v1 scenarija i upisana kao PASS u `QA_LAUNCH_5.md`
- `Skupljivi sidebar`: zavrseno
- `Wizard nazad`: zavrseno

Odlozeno dok ne budu dostupni stvarni operativni podaci:

- `Lemon Squeezy` konfiguracija:
  - `LEMON_SQUEEZY_API_KEY`
  - `LEMON_SQUEEZY_WEBHOOK_SECRET`
  - `LEMON_SQUEEZY_STORE_ID`
  - `LEMON_SQUEEZY_STORE_SUBDOMAIN`
  - weekly/monthly variant ID-jevi
- `HTTPS BASE_URL` za staging/production domen
- non-default `SECRET_KEY` za staging/production
- readiness spustiti na `0 blockers` tek posle stvarnih env vrednosti

Sledeci lokalni blok pre hostinga:

1. final full test + git checkpoint
2. manual smoke kroz aplikaciju na `sr/en`
3. proveriti admin/login stanje ako je potrebno za finalni tok
4. pripremiti `Lemon/hosting checklist` za trenutak kada domen i Lemon Squeezy podaci budu spremni

## Reality Check - 28. mart 2026.

Ovaj roadmap je od sada obavezan zivi dokument i mora pratiti stvarno stanje repoa, testova i runtime-a.

Realno stanje danas:

- core kitchen workflow je stabilan
- javni web sloj vise nije samo plan:
  - postoje `/pricing`, `/login`, `/register`
- auth vise nije samo agenda:
  - postoje korisnici, auth session-i, password reset tokeni i cleanup logika
- billing vise nije samo ideja:
  - postoje billing modeli, webhook obrada i access gate UI
- dashboard posle logina vise nije samo plan:
  - postoji post-login `Dashboard / Projekti` tok
- export worker vise nije samo koncept:
  - postoji `export_jobs` queue, status lifecycle i dedicated worker mode
- ops/readiness vise nije samo TODO:
  - postoje CLI, endpoint i interni ops ekran
- deploy osnova vise nije samo nacrt:
  - postoje `Dockerfile`, staging/production compose fajlovi i deploy dokumentacija

Potvrdeno lokalnom proverom:

- automatski testovi: `186/186 PASS`
- shared export dataset / consistency sloj: implementiran
- auth + billing + ops + export worker testovi: postoje u repo-u
- Postgres runtime je potvrdjen kroz projektni `venv`
- readiness sada ima jasan `venv` wrapper: `RUN_READINESS.ps1`
- `tall_top` 2D rucke sada su centrirane po visini elementa umesto da budu prenisko kao kod standardnih wall vrata
- `tall` 2D rucke su dodatno uskladjene tako da i visoki hinged elementi vise ne ostaju sa ruckama prenisko
- `.env` loader je ojacan tako da `.env.staging` i `.env.staging.local` stvarno rade kao staging override sloj
- dodat `.env.staging.example` i regression test za env loading precedence
- dodat `RUN_STAGING.ps1` i staging runner contract test, tako da lokalni staging start i readiness vise ne zavise od rucnog setovanja `APP_ENV`
- readiness sada razlikuje stvarne Stripe test/live vrednosti od placeholder primera, da staging ne moze lazno da izgleda spremno
- `RUN_READINESS.ps1` sada uvek forsira trazeni target (`staging` / `production`), tako da readiness rezultat vise ne zavisi od nasledjenog `APP_ENV`
- readiness je dodatno uskladjen sa planom: `staging` sada takodje tretira `HTTP BASE_URL` kao blocker, ne samo kao warning
- billing provider je prebacen sa direktnog Stripe puta na `Lemon Squeezy`, uz novi config/runtime/webhook sloj i staging env sablone
- `P1.4` worktop PDF clarity je dodatno ojacan: servisna napomena sada eksplicitno razlikuje finished dimension i CUT osnovu, uz PDF regression test
- `P1.7` validation sloj je dodatno prosiren warningom za module koji pocinju pre pocetka zida (`x < 0`), bez rusenja exporta
- `P1.6` PDF readability je dodatno poboljsan: duge napomene u tabelama sada se prelamaju u vise jasnih redova i poravnate su odozgo
- `P1.6` hardware PDF raspored je dodatno ociscen: kriticna upozorenja sada stoje ispred pune tabele okova, uz regression test redosleda
- `P1.7` validation sloj sada hvata i `tall_top` popune koje su vise od raspolozivog prostora iznad nosivog visokog elementa
- `P1.7` validation sloj sada hvata i previsok `wall_upper` drugi red kada nema dovoljno slobodnog prostora do plafona
- ugaoni susedni warning scenariji (`CORNER_OPENING_CLEARANCE` i `CORNER_FRONT_COLLISION`) su sada zakljucani regression testom
- ugaona `CORNER_DOOR_SWING` zastita je sada takodje pokrivena regression testom
- support warning scenariji za `wall_upper` i `tall_top` su sada dodatno zakljucani regression testovima
- `SIDE_WALL_DOOR` warning za jednokrilna vrata uz levi/desni zid je sada dodatno pokriven regression testom
- `MODULE_OUT_OF_BOUNDS` warning za element koji izlazi van duzine zida je sada dodatno pokriven regression testom
- globalni `FRONT_GAP` warning za nepreporucen zazor fronta je sada dodatno pokriven regression testom
- `SINGLE_DOOR_WIDTH` warning za preiroka jednokrilna vrata je sada dodatno pokriven regression testom
- `DRAWER_STACK` warning za zbir fioka koji prakticno puni celu visinu modula je sada dodatno pokriven regression testom
- `DRAWER_FRONT_MIN` warning za prenisku fioku je sada dodatno pokriven regression testom
- obe `DOOR_DRAWER` warning grane (`DOOR_DRAWER_DOOR_MIN` i `DOOR_DRAWER_DRAWER_MIN`) su sada dodatno pokrivene regression testom
- `WALL_DEPTH` warning za predubok viseci element je sada dodatno pokriven regression testom
- `BASE_DEPTH` warning za preplitak donji element je sada dodatno pokriven regression testom
- `TALL_DEPTH` warning za preplitak visoki element je sada dodatno pokriven regression testom
- `DISHWASHER_WIDTH` warning za usku masinu za sudove je sada dodatno pokriven regression testom
- `FRIDGE_WIDTH` warning za uski frizider modul je sada dodatno pokriven regression testom
- `COOKING_WIDTH` warning za preusku rernu/plocu kolonu je sada dodatno pokriven regression testom
- `HOB_WIDTH` warning za preusku samostalnu plocu je sada dodatno pokriven regression testom
- `SINK_WIDTH` warning za preuski sudoperski element je sada dodatno pokriven regression testom
- dodatno su zakljucani regression testovima i warning minimumi za `DRAWER_DEPTH`, `LIFTUP_WIDTH` i `TALL_HEIGHT`
- dodatno su zakljucani regression testovima i appliance warning minimumi za `WALL_APPLIANCE_WIDTH`, `WALL_APPLIANCE_DEPTH` i `TALL_APPLIANCE_WIDTH`
- dodatno su zakljucani regression testovima i depth warning minimumi za `TALL_APPLIANCE_DEPTH`, `FREESTANDING_DEPTH` i `FREESTANDING_FRIDGE_DEPTH`
- multi-user owner check je ojacan: store load sada odbija projekat koji ne pripada aktivnom korisniku, uz regression test za cross-user izolaciju
- export job owner check je dodatno ojacan: cross-user citanje export job zapisa preko tudjeg `job_id` vise nije dozvoljeno
- audit log vidljivost je suzena: globalne audit tragove sada vidi samo `admin`, dok `local_beta` i ostali korisnici vide samo svoje
- project store `touch/open` tok je dodatno owner-aware: ni `last_opened_at` vise ne moze da se osvezi nad tudjim projektom preko stranog `project_id`
- `ops` tab je suzen samo na `admin`, pa `local_beta` vise nema UI pristup globalnim runtime, auth i billing brojkama
- dodat je i backend guard za `get_ops_runtime_summary()`: ne-admin korisnik sada dobija samo `admin_only` odgovor bez globalnog payload-a
- dodat je i backend guard za `get_release_readiness_summary()`: ne-admin korisnik vise ne moze direktnim pozivom da dobije staging/production readiness payload
- release readiness je dodatno ojacan: Stripe checkout success/cancel i portal return URL sada moraju da odgovaraju `BASE_URL` origin-u da bi staging/production konfiguracija prosla kao spremna
- engleski brend naziv je uskladjen kroz UI i export sloj: koristi se `Cut List PRO`, a ne vise mesovito `Cutting List PRO`
- auth/logout tok je dodatno ojacan: lokalni logout sada uspeva i kada revoke/audit upis u backend storage sloju privremeno padne, uz regression test za resilience
- session restore resilience je dodatno ojacana: ako persisted token/storage citanje pukne pri inicijalizaciji, app sada sigurno vraca lokalnu fallback sesiju umesto da ostane u polu-stanju
- local fallback/session reset sada cisti i `current_project_*` binding, tako da posle logout ili fallback inicijalizacije ne ostaju zalepljeni metapodaci tudjeg aktivnog projekta
- session refresh je dodatno ucvrscen: ako aktivni korisnik vise ne postoji u storage sloju, runtime sada bezbedno pada na lokalnu fallback sesiju umesto da ostane zalepljen za stale account state
- billing helperi su dodatno suzeni: local fallback sesija vise ne dobija billing summary ni checkout/portal putanje, koje sada rade samo za stvarne auth korisnike
- billing helperi sada imaju i Stripe runtime readiness guard: checkout i portal vracaju jasan odgovor kada env nije stvarno konfigurisan, umesto da pokusavaju nedovrsen Stripe tok
- billing UI je dodatno uskladjen sa runtime stanjem: dashboard, auth i access-gate vise ne prikazuju checkout/portal akcije kada `stripe_ready` nije stvarno spreman
- Stripe action tok je dodatno resilientan: ako checkout ili portal URL uspesno stigne iz Stripe-a, lokalni `subscription` persist vise ne prekida korisnicki billing tok nego ostaje best-effort
- Stripe customer create tok je dodatno resilientan: ako Stripe vrati validan `customer_id`, lokalni persist tog ID-ja vise ne obara dalji billing tok nego ostaje best-effort
- export queue limiter je dodatno ojacan: stale `queued/running` jobovi se automatski zatvaraju pre novog enqueue-a, tako da zaglavljeni stari eksporti vise ne blokiraju novi CSV/PDF/XLSX zahtev
- export status update SQL je prepravljen tako da bude bezbedan i za Postgres/`psycopg`, bez `NULL`-ambiguous parametara pri prelazu u `running/done/failed`
- pri promeni korisnickog identiteta `_apply_session_state()` sada resetuje `current_project_*` binding, tako da login/register prelaz ne prenosi metapodatke aktivnog projekta iz prethodne sesije
- dashboard auth akcije (`logout` i `vrati lokalnu sesiju`) sada osvezavaju i toolbar, pa session label i gumbi ostaju sinhronizovani sa runtime stanjem odmah po promeni sesije
- session access refresh je dodatno resilientan: ako storage lookup pukne tokom refresh-a, runtime sada bezbedno pada na lokalnu fallback sesiju umesto da ostane zalepljen za stale korisnika
- login/register tok je dodatno ucinjen atomskim: novi korisnicki state se primenjuje tek posle uspesnog `create_auth_session()`, pa session creation greska vise ne ostavlja runtime na pogresnom identitetu
- auth atomicity je dodatno prosirena i na user-storage persist: ako upis session tokena u browser storage padne, novokreirana auth sesija se odmah revoke-uje i runtime ne prelazi u polulogovano stanje; audit upis je spusten na best-effort da ne obara uspesan login/register

## Novi Dogovoreni Proizvodni Model - 1. april 2026.

Ovo je novi obavezni produktni i UX pravac za aplikaciju. Dalji rad na auth, billing, dashboard i export sloju mora da prati bas ovaj model.

Osnovna ideja:

- aplikacija mora da ostane maksimalno jednostavna i ne sme da daje prenatrpane ekrane
- javni ulaz mora da bude cist login / signup tok
- prvi ekran posle logina mora da bude jednostavan izbor pristupa, a ne veliki dashboard sa previse kartica
- naplata se ne vezuje za sam ulaz u aplikaciju, nego za otkljucavanje PRO funkcija

Dogovoreni nivoi pristupa:

1. `Demo`
- javni demo mora da postoji kao odvojen i vrlo prost ulaz
- demo korisnik moze da vidi kako aplikacija radi
- demo korisnik moze da vidi krojnu listu samo za unapred pripremljen demo projekat
- demo ne daje puni rad nad licnim projektima niti puni export tok

2. `Free`
- korisnik pravi nalog i prijavljuje se
- posle logina bira `Free` varijantu ogranicenog trajanja, trenutno planirana kao oko `5h`
- free korisnik moze da dizajnira kuhinju i radi osnovni editor tok
- free korisnik ne sme da otvara svoju krojnu listu
- free korisnik ne sme da preuzima `PDF`, `Excel`, `CSV` niti druge eksport dokumente

3. `Paid`
- korisnik posle logina bira placeni pristup:
  - `7 dana`
  - `1 mesec`
- ako izabere placenu varijantu, aplikacija ga vodi na poseban checkout prozor
- posle uspesne uplate pristup se vezuje za njegov nalog / email kroz billing i webhook tok
- placeni korisnik tokom aktivnog perioda dobija pun pristup:
  - krojna lista
  - PDF
  - Excel
  - CSV
  - ostale PRO funkcije

Obavezna pravila UX-a:

- javni `/login` mora da bude cist ekran:
  - naziv aplikacije
  - email
  - password
  - `Forgot password?`
  - `Sign up`
- javni `/register` mora da bude isti takav cist ekran bez suvisnih elemenata
- posle `logout` korisnik ne sme da ostane na internom wizard/dashboard ekranu, nego mora da ode na javni login ekran
- post-login ekran mora da bude jednostavan, bez duplih lista projekata, bez previse billing/admin kartica i bez zbunjujuceg rasporeda

Obavezna pravila pristupa unutar aplikacije:

- free korisnik moze da crta i cuva projekat
- free korisnik ne moze da udje u svoju krojnu listu
- free korisnik ne moze da eksportuje dokumente
- paid korisnik moze sve sto je vezano za krojnu listu i eksport
- demo tok ostaje odvojen od pravog korisnickog rada

Operativna posledica za roadmap:

- billing i access-gate UI vise ne treba razvijati kao genericki dashboard
- sledeci rad treba da usmeri aplikaciju na jednostavan `plan selection -> editor access -> gated exports` model
- Lemon Squeezy ostaje billing provider za ovu fazu, jer je to realan pravac za rad iz Srbije
- prvi konkretan implementiran korak iz ovog modela je vec uradjen:
  - `free/trial` korisnik moze da koristi editor i da cuva projekat
  - `free/trial` korisnik ne moze da otvori `Krojna lista`
  - `free/trial` korisniku je `Krojna lista` uklonjena iz toolbar-a
  - demo projekat i dalje moze da prikaze krojnu listu
- sledeci konkretan implementiran korak je takodje uradjen:
  - post-login ekran za `free/trial` korisnika vise nije genericki dashboard
  - korisnik sada dobija jasan izbor:
    - `Free 5h`
    - `PRO 7 dana`
    - `PRO 1 mesec`
  - `7 dana` checkout sada koristi weekly Lemon Squeezy plan
  - `1 mesec` checkout sada koristi monthly Lemon Squeezy plan
- backend export zastita je dodatno uvedena:
  - novi export download vise nije javni staticki link
  - download sada proverava sesiju, vlasnistvo export job-a i placeni pristup
  - free korisnik ne moze da dodje do PDF/Excel/CSV fajla ni direktnim linkom

Gde smo sada:

- zavrsni `P1.6 / P1.7` polish-hardening blok je prakticno zakljucan
- auth/session/billing runtime hardening je otisao znacajno dalje od starijeg plana
- multi-user owner/scope izolacija je zatvorena na projektima, export jobovima, audit i ops/readiness payload-ima
- billing tok je sada dodatno uskladjen:
  - local fallback nema billing helpere
  - helperi imaju Stripe runtime guard
  - UI ne nudi checkout/portal kada runtime nije spreman
  - checkout/portal redirect ne pada vise samo zbog internog `subscription` persist problema

## TACNO GDE SMO STALI I ODAVDE NASTAVLJAMO

Ovo je obavezna referentna tacka za sledece otvaranje dokumenta.

### Prioriteti Posle PDF/UI Review-a

Zvanični prioritetni red:

1. `i18n + dijakritika u PDF-u`
2. `PDF polish`
3. `Canvas + sidebar`
4. `Wizard navigacija`
5. `Inline validacija`
6. `matplotlib -> SVG` kao posebna faza

Pravilo:

- prvo popravljamo ono sto korisnik odmah vidi i po cemu stice poverenje u proizvod
- `SVG` nije deo trenutnog polish bloka nego odvojena veca faza
- staging i hosting ostaju posle lokalnog zatvaranja proizvoda

### Tacna Agenda

Prvi konkretni blok rada:

1. `Kompletan i18n UI finish`
2. `PDF i18n + dijakritika`
3. `PDF polish`
4. `Canvas + sidebar`
5. `Wizard navigacija`
6. `Inline validacija`

### Operativni i18n Roadmap

Cilj:

- cela aplikacija mora da prati `state.language`
- sav UI, editor, canvas, warning poruke i export tekstovi moraju ici kroz `tr(key, lang)`
- fallback na `en` sme da postoji, ali korisnik ne sme da vidi `?????`, sirove kljuceve ni hardcoded srpske stringove

Faza 1. `UI hardcoded konstante`

- `ui_panels.py`
- `ui_edit_panel.py`
- `ui_add_above_dialogs.py`
- `ui_color_picker.py`
- ukloniti stare `BTN_*`, `DLG_*`, `LBL_*` konstante koje su samo srpske tamo gde se jos koriste kao tekst za UI
- svuda koristiti `tr(key, getattr(state, "language", "sr"))`

Faza 2. `Elementi / katalog / param panel`

- tabovi `Donji / Gornji / Visoki / Ugradni`
- nazivi svih elemenata u katalogu
- param panel za izabrani element
- edit panel labele i akcije
- poruke posle dodavanja / izmene elementa

Faza 3. `Canvas / visualization`

- `visualization.py`
- sve inline `if lang == "en" else "sr"` pattern-e prebaciti na `tr()`
- oznake zidova, zone, kotne i pomocne labele moraju biti prevodive na svih 7 jezika

Faza 4. `PDF export`

- `ui_pdf_export.py`
- ukloniti lokalne `_t(sr, en)` helper pattern-e
- koristiti postojeci `cutlist.*` / `common.*` / `nova.*` gde se poklapaju
- sta ne postoji dodati kao novi prevodivi kljuc
- montazne instrukcije, naslovi sekcija i legende moraju biti na izabranom jeziku

Faza 5. `Cutlist / Excel / CSV`

- `cutlist.py`
- kolone tabela moraju ici kroz `cutlist.col_*`
- sekcije kroz `cutlist.section_*`
- helper tekstovi, summary i warning poruke ne smeju ostati SR/EN-only

Faza 6. `Refresh pri promeni jezika`

- ne raditi reload cele strane kao default
- koristiti ciljani refresh po panelima:
  - toolbar
  - `nova`
  - `elementi`
  - po potrebi `podesavanja`
- jezik mora ostati upisan u `state.language` i da se normalno vraca kroz sesiju

Faza 7. `Verifikacija`

- `python test_i18n.py`
- cilj: `0 FAIL`
- manuelna provera:
  - `Español`
  - `Русский`
  - `中文 (简体)`
  - `हिन्दी`
- proveriti:
  - dashboard
  - elementi
  - param panel
  - krojna lista tab
  - PDF
  - Excel / CSV

### Ukupno Preostalo Do Lokalno Zatvorenog Proizvoda

1. `Kompletan i18n finish`
- UI komponente bez hardcoded SR stringova
- katalog elemenata i tabovi
- param / edit panel
- canvas labele
- warning poruke
- PDF / Excel / CSV

2. `PDF i18n / dijakritika cleanup`
- montazne instrukcije
- koraci
- pomocni tekstovi
- fallback i18n provere kroz stvarne PDF exporte

3. `PDF polish`
- by-element preview
- citljivost tabela
- uklanjanje praznih / duplih / nelogicnih stavki

4. `Krojna lista i export tacnost`
- nastavak QA scenarija
- appliance moduli
- worktop logika
- warning i servis paket logika

5. `Canvas + sidebar UX`
- vise prostora za crtanje
- manji vizuelni pritisak na manjim ekranima
- bolja citljivost duzih kuhinja
- ciljani refresh bez nepotrebnog rerendera canvasa

6. `Wizard UX`
- vracanje nazad
- cuvanje prethodnih izbora
- laksa korekcija koraka

7. `Inline validacija`
- trajne poruke uz polja
- jasna objasnjenja greske
- manje oslanjanje na prolazne poruke

8. `Sistematski QA`
- scenario checklists
- PDF / Excel / CSV doslednost
- runtime provereni korisnicki tokovi
- `test_i18n.py` mora biti zelen

9. `Staging / hosting`
- env
- readiness
- deploy
- finalni operativni prolaz

10. `matplotlib -> SVG`
- posebna arhitektonska faza
- ne blokira trenutni finish proizvoda

Tacno smo stali ovde:

- poslednji zavrseni radni blok je:
  - auth/session/billing hardening
  - Stripe runtime guard i resilience
  - export queue stale cleanup
  - Postgres-safe export status update
- trenutno potvrdeno stanje repoa:
  - `186/186 PASS`
  - dokumentacija uskladjena sa kodom
  - nema otvorenog poznatog regresionog testa

Najtacniji status projekta sada:

- core app je stabilan
- `P1.6 / P1.7` je prakticno zatvoren
- multi-user i admin scope hardening su uradjeni
- auth/session/billing runtime je znacajno ucvrscen
- sledeca velika faza vise nije sitan polish, nego:
  - lokalno zatvaranje proizvoda pre hostinga
  - pa tek onda staging readiness i zavrsni produkcioni/runtime blok

Sledeci korak od kog treba odmah nastaviti:

1. lokalno zatvoriti proizvod pre hostinga
2. odraditi i proveriti:
   - UI/UX tokove kroz celu aplikaciju
   - ostale jezike i i18n konzistentnost
   - krojnu listu, PDF/Excel/CSV i warning/logiku do maksimalne tacnosti
   - sistematski QA kroz realne kuhinjske scenarije
3. tek posle toga zavrsiti stvarni staging readiness:
   - `APP_ENV=staging`
   - non-default `SECRET_KEY`
   - validan `HTTPS BASE_URL`
   - pravi Lemon Squeezy staging/API podaci
   - webhook secret
   - variant ID-jevi
4. ponovo pustiti readiness i spustiti blockere na `0`

Tek posle toga nastavljamo:

1. finalni staging/prod operativni prolaz
2. eventualni sledeci veci app/runtime blok iz plana

Ako se ovaj dokument cita u novoj sesiji, nastavak treba da krene upravo od:

- lokalne zavrsnice proizvoda pre staging-a
- ne od starog `P1` polish-a
- ne od auth skeleton-a
- ne od billing osnove, jer su ti slojevi vec znacajno odradjeni

Otvoreni prakticni blocker koji trenutno najvise vredi zatvoriti:

- production-like Postgres runtime vise nije blokiran drajverom u projektu
- potvrdeno je da `project_store` radi kao `Postgres` kada se koristi projektni interpreter
- preostali readiness blockeri su sada stvarno produkcioni:
  - `APP_ENV`
  - `HTTPS BASE_URL`
  - custom `SECRET_KEY`
  - pravi `Stripe` kljucevi, webhook secret i price ID-jevi

Zakljucak:

- projekat vise nije samo u `P0/P1` polish fazi
- realno je u fazi:
  - late beta
  - production hardening
  - lokalnog zatvaranja proizvoda pre staging-a
- `P2/P3` temelj je vec dobrim delom implementiran

Sledeci konkretan operativni korak:

- prvo lokalno zakljucati proizvod:
  - zavrsiti UI/UX i tokove
  - zavrsiti jezike
  - proveriti i zakljucati tacnost krojne liste i eksporta
  - odraditi sistematski QA
- zatim pripremiti stvarni staging env:
  - `APP_ENV=staging`
  - non-default `SECRET_KEY`
  - validan staging `BASE_URL`
  - Lemon Squeezy staging kljuceve i variant ID-jeve
- tek onda ponovo pokrenuti readiness i spustiti broj blockera na nulu za staging

Operativni QA blok za krojnu listu pre hostinga:

Za svaku referentnu kuhinju proveriti:

- mere modula
- carcass/front/back/worktop logiku
- hardware i potrosni materijal
- warning sloj
- `summary_all` i `summary_detaljna`
- PDF / Excel / CSV doslednost
- rucni obracun nekoliko kljucnih stavki

Obavezni scenariji za rucni prolaz:

1. jedan zid - mala jednostavna kuhinja
2. jedan zid - sudopera + ploca za kuvanje
3. jedan zid - fioke + masina za sudove
4. tall block - frizider + oven/micro kolona
5. L-kuhinja sa ugaonim donjim elementom
6. galley kuhinja sa dve linije
7. U-kuhinja sa vise worktop segmenata
8. raised dishwasher scenario
9. filler / end panel scenario
10. namerno problematican scenario za warning proveru

Preporuceni redosled:

1. `1 / 2 / 3`
2. `5 / 6 / 7`
3. `4 / 8 / 9`
4. `10`

## Pravilo Dokumentacije - Obavezno Odmah Azuriranje

Od 27.03.2026 vazi trajno pravilo rada:

- svaka funkcionalna izmena u aplikaciji mora odmah da bude zabelezena u dokumentaciji
- obavezno se azuriraju:
  - `ROADMAP_DO_100.md`
  - `MASTER_PROJEKAT.md`
- ako izmena menja arhitekturu, runtime, deploy, auth, billing, export ili korisnicki tok,
  to mora biti upisano u istoj radnoj sesiji
- task nije zavrsen dok dokumentacija nije uskladjena sa kodom

Radni redosled od sada:

1. izmena koda
2. provera testom ili runtime proverom
3. odmah update roadmap-a
4. odmah update glavnog repo dokumenta
5. tek onda zatvaranje taska

---

## Vizija Cele Aplikacije

Ovaj dokument vise nije samo lista sitnih taskova za polish, nego glavni plan za
ceo proizvodni tok aplikacije:

- javni ulaz / landing
- login i registracija
- reset lozinke
- placanje i access kontrola
- ulazak u aplikaciju
- rad na projektu
- autosave i recent projekti
- krojna lista i eksport
- SQL baza i centralni storage
- priprema za hosting i produkciju

Krajnji cilj nije samo da "radi kod nas", nego da aplikacija radi kao prava web
aplikacija koju korisnik moze da otvori, plati, koristi, zatvori, vrati se kasnije
i nastavi rad bez gubitka podataka i bez pucanja sistema.

---

## Krajnji Cilj Proizvoda

Korisnicki zeljeni tok treba da bude:

1. Korisnik otvori sajt.
2. Vidi jasnu pocetnu stranu sa nazivom aplikacije i login/register ulazom.
3. Napravi nalog ili se prijavi.
4. Tek posle prijave ulazi u aplikaciju.
5. Pravi ili otvara svoje projekte.
6. Radi izmene, autosave se cuva, projekat se pamti centralno.
7. Dobija krojnu listu, PDF/Excel/CSV eksport i tehnicki izlaz.
8. Po potrebi placa plan i dobija odgovarajuci pristup.
9. Kasnije se vraca i nalazi isti nalog, iste projekte i isti status pristupa.

Tehnicki cilj je da sve to radi stabilno, sa centralnom SQL bazom, urednim auth
tokom i bez zavisnosti od local-only state logike.

---

## Prva Ozbiljna Produkciona Meta

Prva prava meta nije `10000+` korisnika, nego:

- stabilnih `100-300` istovremenih korisnika
- bez pucanja aplikacije
- bez gubljenja sesije
- bez blokiranja drugih korisnika kada neko radi eksport
- bez mesanja podataka izmedju korisnika

To je tacka kada aplikacija prestaje da bude "lokalni alat sa loginom" i postaje
"prava web aplikacija spremna za placenu upotrebu i hosting".

---

## Faza U Kojoj Smo Sada

Realno se trenutno nalazimo izmedju dve faze:

- izlazimo iz lokalne/dev faze
- ulazimo u fazu produkcionog ucvrscivanja

Sta je vec uradjeno u tom pravcu:

- postoji javni login/register ulaz
- `/app` vise ne treba da bude otvoren bez stvarne prijave
- lokalni PostgreSQL je podignut i povezan sa aplikacijom
- auth, project store, autosave i export idu ka centralnom SQL modelu
- postoji `export_jobs` osnova
- postoje deploy i production fajlovi

Sta jos nije do kraja zatvoreno:

- session lifecycle mora biti potpuno centralizovan
- billing tok mora biti dovrsen do pune produkcione sigurnosti
- export worker treba dodatno odvojiti i ucvrstiti
- dashboard posle logina treba zavrsiti
- hosting/deploy treba zavrsiti kao operativnu celinu

---

## Arhitektura Za 100-300 Korisnika

Za prvu ozbiljnu produkciju ciljna arhitektura treba da bude:

- `Nginx` ili slican reverse proxy
- `2-4` app worker procesa
- `PostgreSQL` kao glavni source of truth
- opcioni `Redis` za shared ephemeral state i queue sloj
- poseban background worker za eksport i teze zadatke

Minimalna produkciona logika:

- korisnici, projekti, sesije, subscription status i autosave moraju biti centralni
- app ne sme da zavisi od local JSON ili RAM-only state-a kao primarnog izvora istine
- tezi poslovi ne smeju da blokiraju UI tok
- baza mora da ima kontrolisan connection/pooling model

---

## Sta Mora Biti Centralno

Sledece stavke moraju biti centralno cuvane i ne smeju zavisiti od pojedinacne
instance aplikacije:

- korisnici
- auth sessions
- password reset tokeni
- subscription i billing status
- projekti
- autosave
- recent/open history
- export job status
- login attempts
- audit i admin tragovi

Prakticna podela:

- `PostgreSQL`
  - source of truth za korisnike, projekte, sesije, billing status i export evidenciju
- `Redis`
  - kratkotrajni shared state, lockovi, queue, rate limiting i privremeni statusi
- `App proces`
  - UI, validacija, lagani CRUD, slanje poslova u queue
- `Background worker`
  - PDF/Excel/CSV eksport, tezi render i batch obrada

---

## Glavne Zone Rizika

Za Krojna Lista PRO najveci rizici nisu u tome da li aplikacija "ima funkcije",
nego da li svi delovi rade zajedno pod opterecenjem.

### 1. Login / Session / Access Gate

- session ne sme da zavisi od local procesa
- sledeci request moze zavrsiti na drugom worker-u
- pristup mora biti validan gde god zahtev zavrsi

### 2. Project Store

- projekat mora biti transakciono i centralno sacuvan
- local JSON ne sme biti produkcioni source of truth
- treba cuvati `updated_at` i vremenom dodati verzionost / overwrite zastitu

### 3. Export i Render

- PDF/XLSX/CSV ne smeju blokirati glavni UI tok
- korisnik treba da dobije `queued/running/done/failed` lifecycle
- jedan spor eksport ne sme da zakuca druge korisnike

### 4. Baza

- connection pool mora biti kontrolisan
- schema mora raditi isto na SQLite i Postgres tokom tranzicije
- produkcija mora zavrsiti na Postgres-u, ne na SQLite fallback-u

### 5. Hosting i Observability

- health endpoint, readiness, logging i backup nisu opcioni
- mora da se vidi kada sistem usporava, kada raste broj konekcija i kada queue zapinje

---

## Redosled Zavrsavanja Do Stabilnih 300 Korisnika

### Faza A - Stabilan Auth Ulaz

Cilj:

- javni landing/login/register tok mora biti cist i jednoznacan
- bez automatskog "local" logina
- `/app` ulaz samo uz stvarnu prijavu

Zadaci:

- zavrsiti javni login/register/reset UX
- ucvrstiti session lifecycle
- dovrsiti admin/account tok
- jasno odvojiti javni deo i app deo

### Faza B - Postgres Kao Glavni Backend

Cilj:

- `PostgreSQL` postaje glavni produkcioni backend

Zadaci:

- ukloniti zavisnost od local JSON kao primarnog toka
- dovrsiti SQLite -> Postgres migraciju svih bitnih tabela
- ucvrstiti auth_sessions, password_reset_tokens, login_attempts, audit_logs
- pripremiti production `DATABASE_URL` i environment model

### Faza C - Export Worker i Teski Poslovi

Cilj:

- eksport ne sme blokirati UI ili druge korisnike

Zadaci:

- dovrsiti `export_jobs` lifecycle
- izdvojiti background worker logiku
- cuvati rezultat eksporta u deljenom storage-u
- ograniciti paralelne eksporete po korisniku

### Faza D - Billing i Access Kontrola

Cilj:

- placanje mora pouzdano menjati status pristupa

Zadaci:

- ucvrstiti Stripe checkout i customer portal tok
- webhook idempotency
- cuvanje billing event tragova
- jasna pravila `trial / paid / admin / restricted`

### Faza E - Dashboard Posle Logina

Cilj:

- prvi ekran posle logina mora biti cist korisnicki dashboard

Zadaci:

- recent projekti
- novi projekat
- autosave status
- account/logout/status
- kasnije billing entry i pomoc

### Faza F - Hosting i Produkcija

Cilj:

- aplikacija mora da se podigne i radi kao hostovan servis

Zadaci:

- reverse proxy
- `2-4` workera
- Postgres produkcioni deployment
- backup plan
- health/readiness
- logovi i osnovni monitoring

### Faza G - Load Test i Realni QA

Cilj:

- potvrditi da sistem zaista podnosi ciljano opterecenje

Zadaci:

- test scenariji:
  - login
  - otvaranje projekta
  - cuvanje projekta
  - edit elementa
  - autosave
  - PDF/Excel/CSV eksport
- proveriti response time, DB konekcije, queue duzinu i greske
- ciljna tacka za prvu ozbiljnu produkciju:
  - `100-300` korisnika bez pucanja aplikacije

---

## Trenutni Status

Moj realan trenutni sud:

- Ukupan status aplikacije: `91% - 93%`
- Krojna lista i eksport: `92% - 94%`
- Worktop logika: `88% - 90%`
- Internacionalizacija: `88% - 91%`
- UI/UX polish: `86% - 90%`

Zakljucak:

- aplikacija je vrlo blizu ozbiljne produkcione bete
- dovoljno je zrela za interni rad i pilot produkciju
- jos nije punih `100%` za potpuno bezbrizno pustanje bez dodatnog QA

---

## Sta Je Vec Dobro

- Glavni workflow radi:
  - `Wizard -> Elements -> Settings -> Cut List -> PDF/Excel`
- Automatski testovi prolaze stabilno:
  - `93/93 PASS`
- Quick testovi prolaze stabilno:
  - `18/18 PASS`
- Stres test sa eksportom prolazi
- Krojna lista je jaka za standardne pravougaone delove
- PDF i Excel eksport rade stabilno
- panel-only elementi sada imaju jasniji servisni eksport (`FILLER_PANEL`, `END_PANEL`)
- `Cut List` i PDF `by unit` prikaz sada su dodatno zakljucani regression slojem da
  `summary_detaljna` zadrzi kompatibilne kolone `ID`, `PartCode` i `Kol.`
- raised dishwasher logika je dodatno zakljucana eksport-prevod testom
  (`Dishwasher lower filler`, `Dishwasher platform / support`)
- validation sloj je dodatno zakljucan regression testovima za:
  - `INVALID_DIMENSIONS`
  - `INVALID_WALL_REFERENCE`
  - `MISSING_TEMPLATE`
  - `BASE_ALIGNMENT_INVALID`
  - `WORKTOP_TOO_SHORT`
  - `CUTOUT_OUT_OF_BOUNDS`
  - `FILLER_TOO_WIDE`
- Worktop logika je znacajno unapredjena:
  - po zidu, ne po zbiru elemenata
  - rezerva za montazu
  - nabavna duzina
  - field cut
  - front overhang
  - edge protection
  - cutout opis
  - `Base alignment invalid`
  - `Worktop too short`
  - `Cutout out of bounds`
  - poseban `Specifikacija radne ploce / Worktop spec` izlaz u PDF i Excel
- Glavni UI je u velikoj meri preveden na `sr/en`
- `BASE_COOKING_UNIT` je dodatno razjasnjen kroz:
  - realniji 2D i 3D prikaz
  - fiksnu logiku ručke rerne
  - prikaz visine fioke u panelima
- katalog ikonica sada pouzdano čita i `card` blokove sa dodatnim atributima iz `icons_preview_new.html`

---

## Glavne Preostale Slabosti

### 1. Internacionalizacija nije jos apsolutno zavrsena

- jos mogu da se pojave sporadicni srpski tragovi u PDF-u, greskama, warning porukama i redjim ekranima
- cilj je da `sr` bude potpuno srpski i `en` potpuno engleski, bez mesanja

### 2. Worktop nije jos punih 100%

- backend je znatno ojacan
- nedostaje puni UI za precizan unos `sink/hob cutout` koordinata
- nedostaje validacija nivelacije donjih elemenata pre radne ploce
- preostaje jos fini polish worktop prikaza i kontrola u UI/export sloju

### 3. Proizvodna pravila jos nisu do kraja zatvorena

- ugaoni spojevi
- filleri
- zavrsne bocne
- appliance nise
- pojedine montazne napomene
- pojedini appliance moduli jos traze fini domen polish:
  - kuhinjska jedinica (rerna + ploca + fioka)
  - masina za sudove
  - sudopera
  - visoke appliance kolone
  - ugaoni i fridge moduli jos traze zavrsni vizuelni i real-world QA, iako panel/info sloj sada postoji

### 4. Zavrsni real-world QA jos nije uradjen

- mora se proveriti sa 10-20 stvarnih kuhinja iz prakse

---

## P0 - Obavezno Pre Produkcije

Ovo je blok koji mora da bude zavrsen pre nego sto app mozemo da proglasimo produkciono kompletnom.

### P0.1 Finalni Jezicki QA

Cilj:

- kada je `sr`, sve mora biti na srpskom
- kada je `en`, sve mora biti na engleskom

Obuhvat:

- `Settings`
- `Elements`
- `Cut List`
- PDF
- Excel
- notify / error / warning poruke

Definicija gotovo:

- nema mesanja jezika u glavnom toku
- nema sirovih i18n kljuceva u UI
- nema srpskih materijala i naziva delova u engleskom PDF-u

### P0.2 Worktop Finalizacija

Cilj:

- radna ploca mora biti tretirana kao kontinualan element po zidu

Preostalo:

- UI za:
  - `mounting_reserve_mm`
  - `front_overhang_mm`
  - `joint_type`
  - `field_cut`
  - `edge_protection`
  - `edge_protection_type`
  - `sink/hob cutout` koordinate
- validacija:
  - `Base alignment invalid`
  - `Worktop too short`
- PDF prikaz:
  - required length
  - purchase length
  - field cut
  - cutouts
  - protection
  - joint type

Definicija gotovo:

- worktop pravila su jasna u UI, cutlist, PDF i Excel
- korisnik moze da kontrolise kljucne parametre
- servis dobija dovoljno jasan izlaz za teren

### P0.3 Realni Projekti Iz Prakse

Cilj:

- proveriti da rezultat app odgovara stvarnoj radionici

Minimum:

- 10-20 stvarnih kuhinja

Trenutni napredak:

- uvedeni su prvi reprezentativni referentni scenariji u automatski suite:
  - linearna kuhinja sa MZS + sudoperom + rernom
  - visoki blok sa frižiderom i appliance kolonama
  - utility scenario sa uglom, hob modulom, filerom i završnom bočnom
  - povišena donja linija sa raised dishwasher modulom
  - L-kuhinja preko dva zida sa ugaonim modulom
  - galley kuhinja preko dva paralelna zida
  - U-kuhinja preko tri zida

Obavezno proveriti:

- korpus
- frontove
- ledja
- soklu
- radnu plocu
- appliance zone
- warning poruke

Definicija gotovo:

- nema kriticnih odstupanja izmedju app izlaza i realnog stolar/servis ocekivanja

### P0.4 Finalni QA Aktivnih Modula

Cilj:

- da svaki cesto koriscen modul bude istovremeno ispravan u:
  - katalog ikoni
  - 2D prikazu
  - 3D prikazu
  - parametrima
  - krojnoj listi

Prioritet moduli:

- `BASE_COOKING_UNIT`
- `SINK_BASE`
- `BASE_DISHWASHER`
- `BASE_TRASH`
- `BASE_CORNER`
- `TALL_OVEN`
- `TALL_OVEN_MICRO`
- `TALL_FRIDGE`
- `TALL_FRIDGE_FREEZER`

Trenutni napredak:

- `BASE_COOKING_UNIT`: visoko odmaklo
- `SINK_BASE`: visoko odmaklo
- `BASE_DISHWASHER`: panel/info sloj zavrsen
- `BASE_TRASH`: panel/info sloj zavrsen
- `BASE_CORNER`: panel/info sloj zavrsen
- `FILLER_PANEL`: panel/info sloj zavrsen
- `END_PANEL`: panel/info sloj zavrsen
- `TALL_OVEN`: panel/info sloj zavrsen
- `TALL_OVEN_MICRO`: panel/info sloj zavrsen
- `TALL_FRIDGE`: panel/info sloj zavrsen
- `TALL_FRIDGE_FREEZER`: panel/info sloj zavrsen

Definicija gotovo:

- nema vizuelne zabune izmedju modula
- 2D/3D izgled prati stvarni nacin otvaranja i koriscenja
- parametri pokazuju bitne proizvodne mere
- krojna lista odgovara stvarnom modulu

---

## P1 - Veoma Vazno

Ovo nije apsolutni blok za pustanje, ali jako podize kvalitet i sigurnost.

### P1.1 Proizvodna Pravila

Treba dodatno ucvrstiti:

- ugaone module
- fillere
- zavrsne bocne
- appliance nise
- dodatne warning poruke za rizicne konfiguracije

### P1.2 PDF / Excel Polish

Treba srediti:

- jos citljiviji servisni opis
- radni nalog da bude jos jasniji za radionicu
- worktop i machining deo da budu istaknutiji
- preglednost dugih napomena
- zavrsni export polish po formatu:
  - `PDF`
  - `CSV`
  - `XLSX`

Trenutni napredak:

- worktop je sada izdvojen i kao poseban `Specifikacija radne ploce / Worktop spec` blok u PDF i Excel izvozu

Zavrsni export zadaci:

#### PDF

Najveci problemi:

- encoding / dijakritika
- pojedini ASCII srpski oblici u finalnom izlazu
- u nekim scenarijima sekcije mogu delovati poluprazno
- naslov i uvodni red moraju biti potpuno cisti

Sta mora da se zatvori:

- `č/ć/ž/đ/š` moraju svuda raditi bez `?`
- ukloniti oblike tipa:
  - `secenje`
  - `uredjaji`
  - `ploca`
  - `montaza`
- proveriti da realni korisnicki PDF ne izlazi poluprazan kada elementi postoje
- dodatno ispolirati assembly i servisni tekst da izgleda kao finalni tehnicki dokument

Status procena:

- `75% - 80%`

Prioritet:

- `P0` po utisku kvaliteta

#### CSV

Najveci problemi:

- jos je previse sirov za spoljnog korisnika
- nazivi modula i delova nisu finalno standardizovani
- `sr/en` nije jos potpuno zakljucan po izlazu

Sta mora da se zatvori:

- standardizovati nazive modula i delova
- zakljucati puni `sr` i puni `en`
- proveriti da CSV uvek koristi isti finalni dataset kao PDF/XLSX
- po potrebi dodati jos 1-2 korisne servisne kolone, ali bez lomljenja postojece strukture

Status procena:

- `85% - 88%`

Prioritet:

- `P1`

#### XLSX

Najveci problemi:

- sheet-ovi imaju naslovni red iznad tabele, pa nisu idealni za strogo tabelarni import
- nazivi sheet-ova, kolona i sekcija nisu jos potpuno standardizovani
- jezik nije jos potpuno ujednacen po svim sheet-ovima

Sta mora da se zatvori:

- odluciti da li XLSX ostaje primarno:
  - lep za coveka
  - ili strogo tabelaran za import
- standardizovati nazive sheet-ova, kolona i sekcija
- zakljucati puni `sr/en`
- potvrditi da svi vazni sheet-ovi koriste isti finalni dataset

Status procena:

- `89% - 92%`

Prioritet:

- `P1`

Redosled rada u export polishu:

1. `PDF encoding + jezik cleanup`
2. `PDF content completeness`
3. `CSV standardizacija`
4. `XLSX standardizacija i polish`

### P1.3 PDF Po Elementima - Detalji i Sklapanje Za Laika

Cilj:

- da `PDF po elementima` postane stvarno upotrebljiv vodic za korisnika bez stolarskog znanja
- da korisnik moze da:
  - prepozna svaki deo elementa
  - odnese ploce iz servisa kuci
  - sam sastavi element bez nagadjanja

Obavezne sekcije po elementu:

- zaglavlje elementa:
  - redni broj
  - naziv elementa
  - tip elementa
  - dimenzije
  - zid
- vizuelni prikaz:
  - 2D
  - 3D
- oznake delova na slici:
  - `C01`, `C02`, `B01`, `F01`
- mapa delova za sklapanje:
  - `PartCode`
  - `Deo`
  - `Gde ide`
  - `Korak`
  - `Kom.`
- tabela delova / rezova:
  - `PartCode`
  - `Deo`
  - `Pozicija`
  - `Korak`
  - `Dužina [mm]`
  - `Širina [mm]`
  - `Deb.`
  - `Kol.`
  - `Kant`
- `Uputstvo za montažu`
- `Potreban alat i okov`

Obavezni usability zahtevi:

- oznake na slici, u tabeli i u tekstu moraju biti iste
- korisnik ne sme da pogadja koji deo je koji
- koraci sklapanja moraju biti numerisani:
  - `Korak 1`
  - `Korak 2`
  - `Korak 3`
- tekst mora biti kratak, jednostavan i praktican
- `MDF 18` i `MDF 8` moraju biti jasno razdvojeni po nameni:
  - `MDF Front`
  - `MDF Leđa`
- kant mora biti objasnjen ljudski:
  - legenda `T/B/L/R/F`
  - ili jasna tekstualna kolona tipa `kantovana prednja ivica`

Dodatni blokovi koje treba dodati ako je moguce bez lomljenja strukture:

- `Legenda oznaka`
- `Legenda kanta`
- `Napomena za početnika`
- `Proveri pre sklapanja`
- `Ne mešaj MDF 18 i MDF 8`

Relevantni fajlovi:

- [cutlist.py](/C:/Users/Korisnik/krojna_lista_pro/cutlist.py)
- [ui_pdf_export.py](/C:/Users/Korisnik/krojna_lista_pro/ui_pdf_export.py)
- [ui_assembly.py](/C:/Users/Korisnik/krojna_lista_pro/ui_assembly.py)
- [visualization.py](/C:/Users/Korisnik/krojna_lista_pro/visualization.py)
- [render_3d.py](/C:/Users/Korisnik/krojna_lista_pro/render_3d.py)
- [i18n.py](/C:/Users/Korisnik/krojna_lista_pro/i18n.py)

Redosled implementacije:

1. uskladiti `by unit` dataset i kratke oznake delova
2. unaprediti assembly map i tekst korak-po-korak
3. dodati alat/okov po elementu
4. dodati legende i beginner blokove
5. ispolirati PDF layout da bude `IKEA-like`, ali tehnicki tacan

Definicija gotovo:

- laik moze da otvori jedan element i odmah razume:
  - koji su delovi
  - gde ide svaki deo
  - kojim redom se sklapa
  - koji alat i okov su potrebni
- `PDF by unit` vise ne izgleda kao interni tehnicki dump, nego kao stvarni vodic za samostalnu montazu

### P1.4 Vizuelni Polish

Treba doterati:

- `Settings`
- pojedine edit panele
- gustinu i razmake UI polja
- PDF layout i preglednost tabela

---

## P2 - Posle 100% Jezgra

Ovo nije uslov da app bude produkciono kompletna za osnovni scenario, ali je vazno za narednu fazu.

### P2.1 Wall Follow Mode

- `STANDARD`
- `WALL_FOLLOW`

Cilj:

- radna ploca i/ili servisni izlaz da mogu bolje da prate kriv zid

### P2.2 Napredni CNC / Nesting Sloj

Trenutno stanje:

- app daje kvalitetnu krojnu listu
- nije jos pun optimizer / nesting / CNC workflow

Kasnije:

- nesting-friendly export
- sheet optimization
- CNC priprema

### P2.3 Napredni Worktop UI

- precizan unos svih cutout parametara
- vizuelni prikaz cutout pozicija
- vise tipova spojeva

---

## Redosled Rada

Pravilan redosled daljeg rada:

1. `P0.1 Finalni Jezicki QA`
2. `P0.4 Finalni QA aktivnih modula`
3. `P0.2 Worktop finalizacija`
4. `P0.3 Realni projekti iz prakse`
5. `P1.1 Proizvodna pravila`
6. `P1.2 PDF / Excel polish`
7. `P1.3 Vizuelni polish`
8. `P2` stvari

---

## Definicija 100%

Mozemo da kazemo da je app `100%` kada:

- glavni tok radi bez kriticnih gresaka
- `sr/en` su dosledni
- krojna lista je stabilna i proizvodno logicna
- worktop je potpuno pokriven pravilima i izlazom
- PDF/Excel su jasni za radionicu
- 10-20 stvarnih kuhinja prodju bez ozbiljnih odstupanja
- testovi i stres testovi prolaze

---

## Sledeci Aktivni Korak

Trenutni fokus:

- `P0.1 Finalni jezicki QA` i `P0.4 Finalni QA aktivnih modula`
- trenutno najosetljiviji aktivni modul: `BASE_COOKING_UNIT`
- posle njega slede:
  - `SINK_BASE`
  - `BASE_DISHWASHER`
  - `TALL_OVEN`
  - `TALL_OVEN_MICRO`

- zavrsni `sr/en` QA na glavnom toku
- worktop UI i izlaz dovesti do punog proizvodnog nivoa
- posle toga proveriti 10-20 stvarnih kuhinja

Prvi konkretan sledeci zadatak:

- pregledati `Settings`, `Elements`, `Cut List`, PDF i Excel na `sr` i `en`
- hvatati preostale mesane stringove i warning poruke
- zatim zavrsiti worktop cutout UI i validacije

---

## Operativna Lista

### Zavrseno

- Glavni workflow stabilan
- Automatski testovi prolaze
- Glavni `sr/en` sloj uveden
- PDF/Excel rade
- Worktop backend znacajno unapredjen

### U Toku

- Finalni jezicki QA
- Worktop finalizacija
- UI / PDF polish
- Validation layer improvements

### Sledece

- Realni projekti iz prakse
- Zavrsni PDF/Excel polish
- Proizvodna pravila za retke scenarije

---

## Kako Cemo Raditi Po Ovom Dokumentu

Pravilo rada:

1. Radimo samo `P0` dok ne bude zatvoren.
2. Svaku vecu izmenu proveravamo testovima.
3. Sve sto prijavis preko screenshot-a ulazi odmah u `Finalni jezicki QA`.
4. Tek posle toga prelazimo na `P1`.

Prag za prelaz na narednu fazu:

- `P0.1` prakticno ociscen u glavnom toku i potvrden screenshot/real-world QA prolazom
- `P0.2` potvrden kroz UI, PDF, Excel i realne module
- bar nekoliko stvarnih kuhinja provereno bez ozbiljnih odstupanja

## P0.5 Export Consistency & Data Integrity (CRITICAL)

Cilj:
osigurati da svi export formati (`PDF`, `XLSX`, `CSV`) koriste isti validirani dataset i da ne postoje prazni ili nekonzistentni redovi.

Identifikovani problemi:

1. CSV export trenutno može biti prazan iako PDF/XLSX sadrže podatke.
2. U worktop machining sekciji pojavljuju se redovi sa:
   - zid = NaN
   - dužina = 0 mm
   - spoj u uglu = NaN
   - izrezi = NaN
3. Pojedine prazne vrednosti izlaze kao "nan", "None" ili slični interni stringovi.

Očekivano stanje:

- PDF, XLSX i CSV moraju koristiti isti finalni dataset iz cutlist pipeline-a.
- Nijedan export ne sme sadržati:
  - NaN
  - None
  - null
  - 0 mm elemente bez funkcionalnog značenja
- CSV mora sadržati identične ključne redove kao PDF/XLSX.

Tehnički zadaci:

### A. Jedinstveni dataset sloj

proveriti pipeline:

- [state_logic.py](C:/Users/Korisnik/krojna_lista_pro/state_logic.py)
- [cutlist.py](C:/Users/Korisnik/krojna_lista_pro/cutlist.py)
- [ui_cutlist_tab.py](C:/Users/Korisnik/krojna_lista_pro/ui_cutlist_tab.py)
- [ui_project_io.py](C:/Users/Korisnik/krojna_lista_pro/ui_project_io.py)

definisati jedinstvenu funkciju:

`get_final_cutlist_dataset()`

koja:

- vraca kompletan dataset za sve export formate
- uklanja interne pomocne elemente
- uklanja prazne zapise
- normalizuje vrednosti

Napomena:

- ovo ima smisla samo ako ostane kao tanak shared sloj nad postojecim cutlist pipeline-om
- ne uvoditi novu arhitekturu ni paralelni model podataka

### B. Data sanitation sloj

u cutlist pipeline dodati normalizaciju:

- `NaN -> ""`
- `None -> ""`
- `invalid numeric -> 0` samo ako je logicno
- `invalid record -> remove`

filter pravila:

element mora imati:

- `part_name`
- `length_mm > 0`
- `width_mm > 0`
- `material != empty`

ako nije ispunjeno -> ne eksportovati

### C. Worktop machining cleanup

proveriti:

- [cutlist.py](C:/Users/Korisnik/krojna_lista_pro/cutlist.py)
- [module_rules.py](C:/Users/Korisnik/krojna_lista_pro/module_rules.py)
- [state_logic.py](C:/Users/Korisnik/krojna_lista_pro/state_logic.py)

osigurati da:

- internal support elementi
- privremeni worktop placeholder elementi
- interne strukture za `field_cut`

ne izlaze u machining tabelu.

validni worktop red mora imati:

- `wall_id`
- `required_length_mm`
- `purchase_length_mm`
- `joint_type` ili `STRAIGHT`
- `field_cut`
- opis izreza ili prazan string

### D. CSV export consistency

u [ui_project_io.py](C:/Users/Korisnik/krojna_lista_pro/ui_project_io.py):

CSV mora koristiti isti dataset kao XLSX i PDF.

obavezna polja CSV:

- `module`
- `part_name`
- `material`
- `length_mm`
- `width_mm`
- `qty`
- `edge_front_mm`
- `edge_back_mm`
- `edge_left_mm`
- `edge_right_mm`
- `notes`

redosled kolona mora biti stabilan.

CSV ne sme biti prazan ako postoje elementi u projektu.

### E. Testovi

dopuniti test_stress.py ili dodati novi:

- [test_export_consistency.py](C:/Users/Korisnik/krojna_lista_pro/test_export_consistency.py)

test mora proveriti:

isti broj elemenata u:

- `pdf dataset`
- `xlsx dataset`
- `csv dataset`

assert:

- `len(csv_rows) == len(xlsx_rows)`
- `len(csv_rows) > 0`

Definicija gotovo:

- CSV nikada nije prazan ako projekat ima elemente
- PDF/XLSX/CSV imaju isti broj validnih delova ili jasno definisanu istu bazu podataka
- worktop machining sekcija nema `NaN` redove
- nijedan export ne sadrzi `nan`, `None` ili `null`
- dataset prolazi consistency test
- sve postojece test suite i dalje prolaze

Status:

- `ZATVORENO / IMPLEMENTIRANO`
- uveden je shared `get_final_cutlist_dataset()`
- `PDF`, `XLSX`, `CSV` i `Cut List` ekran koriste isti finalni dataset
- dodati consistency i sanitization testovi
- dodati warning testovi
- trenutno stanje testova: `74/74 PASS`
- trenutno stanje testova: `89/89 PASS`

## P1.4 Worktop UX clarity

Cilj:
uciniti worktop logiku jasnijom korisniku i servisu.

dodati vizuelno izdvojenu sekciju u PDF:

`WORKTOP SPECIFICATION`

obavezna polja:

- `wall`
- `required_length_mm`
- `purchase_length_mm`
- `field_cut`
- `front_overhang_mm`
- `mounting_reserve_mm`
- `joint_type`
- `edge_protection`
- `cutouts`

PDF mora jasno razdvajati:

- `finished dimension`
- `cut dimension`
- `field cut dimension`

tekstualna napomena:

`Servis radi iskljucivo po CUT merama.`

Fajl:

- [ui_pdf_export.py](C:/Users/Korisnik/krojna_lista_pro/ui_pdf_export.py)

## P1.5 UI clarity improvements (non-breaking)

vizuelni problemi:

dimenzije u 2D tehničkom prikazu su previše crvene
crvenu koristiti samo za error ili konflikt

grid opacity smanjiti na 10-20%

slobodan prostor oznake pomeriti iznad linije dimenzije

3D kamera default pozicija:

distance ≈ 2.8 m
height ≈ 1.6 m

fajlovi:

- [visualization.py](C:/Users/Korisnik/krojna_lista_pro/visualization.py)
- [render_3d.py](C:/Users/Korisnik/krojna_lista_pro/render_3d.py)
- [ui_canvas_2d.py](C:/Users/Korisnik/krojna_lista_pro/ui_canvas_2d.py)

bez menjanja postojeće logike pozicioniranja elemenata.

## P1.6 Export readability polish

PDF:

grupisati sekcije u 3 logičke celine:

ZA KORISNIKA
ZA SERVIS
ZA MONTAŽU

bez promene strukture podataka.

Fajl:

- [ui_pdf_export.py](C:/Users/Korisnik/krojna_lista_pro/ui_pdf_export.py)

Status:

- `DELIMICNO ZAVRSENO`
- PDF sada ima sekcijske markere:
  - `ZA KORISNIKA`
  - `ZA SERVIS`
  - `ZA MONTAŽU`
- preostaje dodatni fini raspored i citljivost dugih napomena

## P1.7 Validation layer improvements

dodati validation pre export:

ako postoji:

- element overlapping
- negative dimension
- invalid wall reference
- missing module template

prikazati warning ali ne rušiti export.

fajl:

- [layout_engine.py](C:/Users/Korisnik/krojna_lista_pro/layout_engine.py)
- [state_logic.py](C:/Users/Korisnik/krojna_lista_pro/state_logic.py)
- [room_constraints.py](C:/Users/Korisnik/krojna_lista_pro/room_constraints.py)

Pravila:

- warning prikazati korisniku
- ne rusiti export
- ne menjati postojeci workflow

Status:

- `DELIMICNO ZAVRSENO`
- warning sloj sada pokriva:
  - `MISSING_TEMPLATE`
  - `INVALID_WALL_REFERENCE`
  - overlap warninge
  - base alignment warning za worktop
- overlap warning je dodatno pokriven automatskim testom
- preostaje jos dublji validation polish za retke room/layout scenarije

## Dodatna Napomena

Tvoj predlog ima smisla i dopunjuje postojeći roadmap u pravom smeru:

- ne menja arhitekturu
- ne uvodi breaking changes
- fokusira se na stvarne preostale rizike do `100%`

Stvari koje imaju najviše smisla i ostaju prioritet:

1. `P0.5 Export Consistency & Data Integrity`
2. `P1.4 Worktop UX clarity`
3. `P1.5 UI clarity improvements`
4. `P1.6 Export readability polish`
5. `P1.7 Validation layer improvements`

---

## P2 - Login, Zastita i Pretplata

Ovo je sledeci veliki poslovni sloj posle zavrsetka core produkcionog polish-a.

Cilj:

- da aplikaciju mogu koristiti samo odobreni korisnici
- da pristup bude vremenski ogranicen po placenom paketu
- da istek pristupa automatski blokira koriscenje app
- da se ne menja postojeci kitchen workflow, nego samo doda access sloj oko njega

### P2.1 Auth osnova

Potrebno:

- login / logout
- korisnicki nalog
- sigurno cuvanje sesije
- reset lozinke

Minimalni ekran:

- login
- aktivna pretplata / istekao pristup
- logout

Preporucena tehnologija:

- `Supabase Auth`

Definicija gotovo:

- korisnik ne moze da udje u app bez prijave
- sesija ostaje stabilna
- logout radi pouzdano

### P2.2 Model pristupa po trajanju

Tvoj trazeni poslovni model:

- korisnik plati paket
- dobije pristup na odredjeni broj dana
- primer:
  - `10 EUR = 10 dana`

Za backend model treba dodati:

- `user_id`
- `plan_name`
- `price_eur`
- `duration_days`
- `access_starts_at`
- `access_expires_at`
- `status`
  - `active`
  - `expired`
  - `blocked`
  - `pending_payment`

Definicija gotovo:

- pristup se racuna po datumu isteka
- kada datum istekne, app vise nije dostupna za rad

### P2.3 Billing i aktivacija

Potrebno:

- naplata
- evidencija transakcije
- aktivacija pristupa posle uplate

Preporucena tehnologija:

- `Stripe`

Minimalna logika:

- korisnik vidi paket
- plati paket
- nakon uspesne uplate dobija `access_expires_at`
- app pri svakom ulasku proverava status pristupa

Definicija gotovo:

- uspešna uplata aktivira pristup bez ručnog rada u kodu
- neuspešna ili nepostojeca uplata ne otvara app

### P2.4 Access gate u aplikaciji

Potrebno:

- pre otvaranja glavnog UI toka proveriti:
  - da li je korisnik ulogovan
  - da li je pretplata aktivna

Ako nije:

- ne prikazivati `Wizard -> Elements -> Settings -> Cut List`
- prikazati:
  - login ekran
  - ili ekran `pretplata istekla`

Pravila:

- ne menjati postojece stranice
- samo dodati gate pre njih

Definicija gotovo:

- bez aktivnog pristupa korisnik ne moze koristiti aplikaciju
- sa aktivnim pristupom app radi isto kao i sada

### P2.5 Admin pregled

Minimalno:

- lista korisnika
- status pretplate
- datum isteka
- rucna aktivacija / produzenje

Definicija gotovo:

- moze se brzo videti ko ima aktivan pristup
- moze se rucno produziti pristup ako treba

### P2.6 Sigurnost i zastita

Potrebno:

- server-side provera pretplate
- ne oslanjati se samo na frontend
- ograniciti pristup exportima ako pretplata nije aktivna
- logovati pokusaje pristupa bez aktivne licence

Definicija gotovo:

- korisnik ne moze zaobici proveru samo promenom UI stanja

### P2.7 Faze implementacije

Predlozeni redosled:

1. `Auth skeleton`
2. `Subscription table / access model`
3. `Access gate ispred aplikacije`
4. `Manual admin activation`
5. `Stripe billing`
6. `Automatska aktivacija / deaktivacija`

### P2.8 Definition of Done

Ovaj blok je gotov kada:

- korisnik mora da se uloguje
- korisnik moze da koristi app samo dok mu traje pristup
- istek pretplate automatski blokira app
- postoji admin pregled statusa korisnika
- billing i status pristupa su povezani

Napomena:

- ovo ne treba raditi pre nego sto zavrsimo aktuelni `P0/P1` core polish
- ali agenda je sada spremna i moze da se koristi kao sledeci veliki radni blok

---

## P3 - SaaS / Internet Produkcija

Ovaj blok pokriva prelazak aplikacije iz lokalnog alata u placeni online servis.

Cilj:

- korisnik moze da dodje na sajt
- napravi nalog
- plati pretplatu
- dobije pristup aplikaciji
- koristi svoje projekte online

Napomena:

- ovaj blok dolazi posle stabilizacije `P0/P1/P2`
- ne ulaziti u javnu prodaju pre nego sto je core aplikacija zatvorena

### P3.1 Produkciona beta osnova

Potrebno:

- zakljucati stabilnu produkcionu bazu koda
- uvesti production config:
  - `APP_ENV`
  - `BASE_URL`
  - `SECRET_KEY`
  - `DATABASE_URL`
  - `STRIPE_SECRET_KEY`
  - `STRIPE_WEBHOOK_SECRET`
- uvesti centralni logging
- dodati health check
- obezbediti reproducibilno pokretanje iz `venv`

Definicija gotovo:

- aplikacija se pokrece konzistentno
- testovi realno prijavljuju stanje
- postoji jasan production config

### P3.2 Korisnici i baza

Potrebno:

- uvesti `Postgres`
- napraviti tabele:
  - `users`
  - `projects`
  - `subscriptions`
  - `payments`
  - `audit_logs`
- dodati login sistem:
  - email + lozinka
  - hash lozinke
  - reset lozinke
  - session cookie
- odvojiti podatke po korisniku
- save/load projekata prebaciti na bazu

Definicija gotovo:

- svaki korisnik vidi samo svoje projekte
- login radi stabilno
- projekti ostaju trajno sacuvani

### P3.3 Naplata

Potrebno:

- koristiti `Stripe Checkout` za pretplatu
- koristiti `Stripe Customer Portal` za upravljanje pretplatom
- ne otkljucavati pristup odmah po kliku na placanje
- pristup aktivirati iskljucivo preko webhook potvrde
- obraditi webhook evente:
  - `checkout.session.completed`
  - `customer.subscription.created`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
  - `invoice.paid`
  - `invoice.payment_failed`

Pravila pristupa:

- app otkljucati samo za `active`
- po potrebi dozvoliti i `trialing`
- `past_due` tretirati po jasno definisanom pravilu

Definicija gotovo:

- korisnik plati
- webhook potvrdi status
- nalog dobije pristup
- otkazivanje i promena plana rade bez ruÄnog rada

### P3.4 SaaS aplikacioni sloj

Potrebno:

- dodati odvojene stranice:
  - `/`
  - `/pricing`
  - `/login`
  - `/register`
  - `/app`
  - `/billing`
- zakljucati `/app` iza auth + aktivne pretplate
- ograniciti pristup po planu:
  - broj projekata
  - eksport
  - 3D preview
  - broj sacuvanih varijanti
- dodati trial ili demo mod
- dodati osnovni admin pregled

Definicija gotovo:

- postoji jasan prodajni tok
- postoji jasan korisnicki tok
- pristup aplikaciji zavisi od statusa pretplate

### P3.5 Deploy

Potrebno:

- spakovati app u `Docker`
- postaviti:
  - domen
  - `HTTPS`
  - reverse proxy
  - production env vars
  - backup baze
- izabrati deployment model:
  - `Hetzner VPS + Docker + Nginx + Postgres`
  - ili `Railway / Render / Fly.io` za brzi start

Definicija gotovo:

- aplikacija je dostupna na domenu
- login radi
- billing radi
- baza ima backup
- eksport radi i u produkciji

### P3.6 Obavezno pre javnog pustanja

Potrebno:

- `Terms of Service`
- `Privacy Policy`
- support kontakt
- monitoring i alerting
- backup / restore procedura
- rate limiting
- test sa 5-10 pilot korisnika
- test sa 10-20 stvarnih kuhinja
- provera PDF/Excel izlaza na realnim projektima

Definicija gotovo:

- postoji poslovna i pravna osnova za javno pustanje
- postoji operativna kontrola nad sistemom
- aplikacija je proverena sa stvarnim korisnicima

### P3.7 Preporuceni redosled

1. Stabilizacija produkcione baze koda
2. `Postgres + user accounts`
3. `Stripe Checkout + webhooks + portal`
4. access gate ispred aplikacije
5. deploy na domen
6. pilot korisnici
7. tek onda javna prodaja

### P3.8 MVP SaaS verzija

Najpragmaticniji prvi placeni release:

- jedan plan pretplate
- login
- `Postgres`
- korisnik moze da cuva projekte
- PDF/Excel eksport
- admin vidi status korisnika
- billing preko `Stripe`

Definicija gotovo:

- korisnik realno moze da plati i koristi aplikaciju preko interneta
### P3.9 Operativna agenda - kako radimo

Glavni princip:

- ovo mora biti app za potpune laike
- korisnik mora da moze da udje, razume sta radi i dodje do rezultata bez tehnickog znanja
- svaki sledeci korak mora biti jasniji od prethodnog, ne komplikovaniji

Zbog toga redosled rada nije:

- prvo billing
- pa kasnije UX

nego:

- prvo jasan tok za laika
- zatim pouzdano cuvanje i pristup
- zatim naplata
- zatim internet produkcija

#### Faza A - UX za potpune laike

Cilj:

- da prvi korisnik bez prethodnog iskustva moze da dodje do prve kuhinje bez pomoci

Obavezno uraditi:

- pojednostaviti pocetni ekran
- jasno razdvojiti:
  - `Nova kuhinja`
  - `Otvori projekat`
  - `Demo primer`
- uvesti jasan onboarding tok:
  - `1. prostorija`
  - `2. elementi`
  - `3. materijali`
  - `4. pregled`
  - `5. PDF / Excel`
- smanjiti broj odluka koje laik mora odmah da donese
- sakriti napredne opcije iza:
  - `Napredno`
  - `Dodatna podesavanja`
- svuda koristiti jezik koji laik razume

Definicija gotovo:

- korisnik prvi put otvara app i razume sta da klikne dalje
- moze da napravi osnovni projekat bez objasnjenja sa strane

#### Faza B - Sigurno cuvanje rada

Cilj:

- korisnik ne sme da izgubi projekat

Obavezno uraditi:

- automatsko cuvanje projekta
- `Sacuvaj kao`
- lista skorijih projekata
- potvrda da je projekat sacuvan
- zastita od gubitka podataka pri zatvaranju ili refresh-u

Definicija gotovo:

- korisnik ne razmislja da li je nesto izgubio
- app deluje sigurno i pouzdano

#### Faza C - Nalog korisnika

Cilj:

- svaki korisnik ima svoj prostor i svoje projekte

Obavezno uraditi:

- registracija
- login
- reset lozinke
- profil korisnika
- lista korisnickih projekata

Definicija gotovo:

- korisnik moze da udje sa bilo kog uredjaja i vidi svoje projekte

#### Faza D - Access model

Cilj:

- app zna ko sme da koristi puni sistem

Obavezno uraditi:

- status naloga
- status pretplate
- trial / demo pravilo
- jasna poruka kada pristup nije aktivan

Definicija gotovo:

- niko ne koristi placeni deo bez validnog pristupa
- blokada je jasna i kulturno objasnjena

#### Faza E - Billing

Cilj:

- korisnik moze sam da plati i sam da upravlja pretplatom

Obavezno uraditi:

- `Stripe Checkout`
- `Stripe Customer Portal`
- webhook aktivacija pristupa
- webhook gasenje pristupa
- ekran `Moj plan`

Definicija gotovo:

- nema rucnog ukljucivanja korisnika posle uplate

#### Faza F - Javni sajt

Cilj:

- da neko ko prvi put cuje za aplikaciju moze da razume sta dobija i da se prijavi

Obavezno uraditi:

- landing stranu
- pricing stranu
- primer izlaza:
  - screenshot
  - PDF primer
  - Excel primer
- objasniti za koga je app

Definicija gotovo:

- sajt prodaje vrednost aplikacije i vodi korisnika do registracije i placanja

#### Faza G - Produkcija

Cilj:

- sistem radi stabilno na internetu

Obavezno uraditi:

- deploy
- domen
- `HTTPS`
- backup baze
- monitoring
- logovi
- recovery plan

Definicija gotovo:

- sistem moze da radi svaki dan bez rucnog gasenja pozara

### P3.10 Prioriteti - sta radimo prvo

Redosled implementacije:

1. `Laik UX / onboarding`
2. `Auto-save + sigurnost projekta`
3. `Postgres + user projects`
4. `Login / register / reset lozinke`
5. `Access gate`
6. `Stripe billing`
7. `Landing + pricing`
8. `Deploy + domen + HTTPS`
9. `Pilot korisnici`
10. `Javno pustanje`

### P3.11 Pravila dizajna za laike

Ovo mora da se postuje kroz celu SaaS fazu:

- jedan ekran = jedna glavna odluka
- jedno primarno dugme po koraku
- bez pretrpavanja sidebar-a
- bez skrivenih kriticnih akcija
- korisnik uvek mora da zna:
  - gde je
  - sta je sledeci korak
  - da li je projekat sacuvan
  - kako da se vrati nazad
- warning poruke moraju da budu ljudske i korisne
- greska mora da kaze sta korisnik da uradi dalje

### P3.12 Prvi izvrsni sprint

Predlog prvog sprinta:

1. ocistiti glavni tok za laike
2. ubaciti `Demo primer`
3. dodati auto-save
4. dodati recent projects
5. definisati bazu i modele za `users/projects`

### P3.13 Razbijanje prvog sprinta po fajlovima

Da bismo isporucili P3.12 brzo i bez lutanja, radimo ovim redom:

1. `ui_wizard_tab.py`
- pojednostaviti prvi ekran za potpune laike
- jasno odvojiti:
  - `Nova kuhinja`
  - `Učitaj projekat`
  - `Šta sledi`
- u izboru merenja oznaciti sta je preporuceno za pocetnika

2. `room_setup_wizard.py`
- skratiti tekstove koji zvuce tehnicki
- sakriti napredne opcije dok ne zatrebaju
- obavezno uvek pokazati:
  - gde je korisnik
  - sta je sledeci korak
  - da li moze bezbedno da nastavi dalje

3. `ui_navigation.py` i `ui_main_content.py`
- obezbediti jasan povratak na pocetak
- kasnije dodati status projekta:
  - `nije sacuvano`
  - `auto-saved`
  - `sacuvano`

4. `ui_nova_tab.py` i `ui_project_io.py`
- ubaciti laksi tok za:
  - otvaranje poslednjih projekata
  - demo primer
  - cuvanje bez razmisljanja o fajlovima

5. `state_logic.py`
- pripremiti osnovu za:
  - auto-save
  - recent projects
  - user owned projects
  - kasnije vezivanje na bazu

7. `project_store.py`
- uvesti minimalni SQLite storage sloj za:
  - `users`
  - `projects`
- odvojiti lokalni JSON workflow od buduceg SaaS persistence sloja
- omoguciti kasniji prelaz na Postgres bez ponovnog menjanja UI logike

6. `i18n.py`
- sve pocetne korake pisati jezikom koji razume potpuni laik
- izbaciti terminologiju koja trazi prethodno znanje gde god nije neophodna

### P3.14 Operativna agenda - kako sprovodimo

### P3.15 Produkciona checklista pre servera

Ova sekcija je prakticna kontrolna lista za trenutak kada budemo spremali app za pravi server, internet pristup i naplatu.

#### P3.15.1 Sta je vec uradjeno

- pocetni onboarding je znatno pojednostavljen za laike
- postoji `Demo primer`
- postoji `Recent projects`
- postoji `Auto-save`
- postoji lokalni storage sloj za:
  - `users`
  - `projects`
- postoji osnovni session model:
  - lokalni korisnik
  - aktivni projekat
  - access status
- postoji prvi auth skeleton:
  - registracija
  - login
  - povratak na lokalnu sesiju
- postoji access gate osnova za:
  - `trial`
  - `paid`
  - `inactive`

#### P3.15.2 Sta je u toku

- UX za potpune laike se i dalje doteruje
- auth tok se pojednostavljuje da bude potpuno jasan pri prvom otvaranju
- lokalni SQLite storage se priprema kao prelazni sloj ka `Postgres`
- session i access model se pripremaju za billing pravila

#### P3.15.3 Sta jos nije zavrseno

Pre pravog pustanja na internet moramo zavrsiti:

1. korisnicki projekti
- svaki korisnik mora da vidi samo svoje projekte
- save/load mora da radi po korisniku, ne globalno

2. produkcioni auth
- pravi `logout`
- session cookie / session management
- reset lozinke preko email-a
- zastita login toka od brute-force napada
- jasan profil korisnika

3. baza za server
- prelaz na `Postgres`
- migracije baze
- odvojeno `dev / staging / production` okruzenje

4. billing
- `Stripe Checkout`
- `Stripe Customer Portal`
- webhook potvrda uplate
- webhook gasenje pristupa
- statusi:
  - `trial`
  - `active`
  - `past_due`
  - `canceled`
  - `inactive`

5. pristup aplikaciji
- `/app` mora biti zakljucan iza:
  - login-a
  - aktivne pretplate
- eksport mora biti ogranicen po pravilima plana

6. javni sajt
- landing strana
- pricing strana
- `/login`
- `/register`
- `/billing`
- primeri izlaza i vrednosti proizvoda

7. deploy
- `Docker`
- domen
- `HTTPS`
- reverse proxy
- production env vars
- backup baze
- restore provera
- monitoring
- logovi
- error tracking

8. pravni i poslovni minimum
- `Terms of Service`
- `Privacy Policy`
- support kontakt
- refund / failed payment pravila

#### P3.15.4 Sta direktno blokira pustanje na server

Ako hocemo da korisnik:

- otvori sajt
- napravi nalog
- plati
- koristi app preko interneta

onda sledece stavke direktno blokiraju pustanje dok nisu gotove:

- odvajanje projekata po korisniku
- `Postgres`
- pravi login/session model
- `Stripe` billing
- webhook aktivacija pristupa
- deploy na domen sa `HTTPS`
- backup i monitoring

#### P3.15.5 Redosled pre produkcije

Najbezbedniji redosled rada je:

1. zavrsiti UX za laike
2. odvojiti projekte po korisniku
3. prebaciti persistence na `Postgres`
4. zavrsiti `login / logout / reset lozinke`
5. zavrsiti access model
6. zavrsiti `Stripe billing + webhooks`
7. napraviti landing i pricing stranice
8. podici staging verziju na test domen
9. proveriti pilot korisnike
10. tek onda javna produkcija

#### P3.15.6 Arhitektura aplikacije danas

Trenutna aplikacija nije klasicno odvojena na:

- poseban frontend
- poseban backend

nego je trenutno:

- `NiceGUI` server-side web aplikacija
- jedan Python projekat vodi i UI i aplikacionu logiku

To prakticno znaci:

- ovo je monolitna web aplikacija
- nije `React frontend + FastAPI backend`
- moze na internet i u ovom obliku
- ali auth, billing, baza i deploy moraju biti uradjeni ozbiljno

#### P3.15.7 Definicija gotovo za internet produkciju

Mozemo reci da je app spremna za javno pustanje tek kada:

- korisnik moze sam da napravi nalog
- korisnik moze sam da plati
- pristup se automatski ukljucuje i iskljucuje po statusu pretplate
- svaki korisnik vidi samo svoje projekte
- app radi na domenu sa `HTTPS`
- baza ima backup i restore proceduru
- postoji monitoring i podrska
- pilot korisnici su prosli bez kriticnih problema

#### P3.15.8 Trenutno implementiran deploy temelj

Do sada je pripremljeno:

- `Dockerfile`
- `docker-compose.staging.yml`
- `docker-compose.production.yml`
- `healthz`
- `readyz`
- `ops/runtime`
- Nginx HTTP proxy sablon
- Nginx HTTPS-ready sablon
- `.env.example`
- `.env.production.example`
- staging i production deploy dokumentacija

To znaci da deployment vise nije samo ideja, nego postoji realan operativni temelj.

Pre stvarnog javnog pustanja i dalje fale:

- pravi server
- pravi Postgres URL
- pravi Stripe kljucevi i price ID-jevi
- domen
- sertifikat
- finalni staging/prod test

### P3.16 Frontend i Backend za ovu aplikaciju

Ova aplikacija trenutno ima:

- frontend sloj
- backend sloj

ali nema:

- odvojenu frontend aplikaciju
- odvojenu backend aplikaciju

To znaci da danas radimo sa:

- jednom `NiceGUI` / Python web aplikacijom
- jednim projektom koji sadrzi i UI i server logiku

Najprecizniji opis danasnjeg stanja:

- server-side / backend-driven web app
- Python monolitna web aplikacija

To nije problem samo po sebi.
Za prvi javni SaaS izlazak ovo je i dalje potpuno validan pristup,
ako auth, baza, billing i deploy budu uradjeni kako treba.

#### P3.16.1 Sta je kod nas frontend sloj

Frontend sloj je ono sto korisnik vidi i koristi:

- tabovi
- forme
- wizard
- toolbar
- onboarding
- account ekran
- settings ekran
- cutlist prikaz

Glavni frontend fajlovi su:

- `ui_panels.py`
- `ui_main_content.py`
- `ui_wizard_tab.py`
- `ui_nova_tab.py`
- `ui_auth_tab.py`
- `ui_settings_tab.py`
- `ui_elements_tab.py`
- `ui_toolbar.py`

To je UI sloj, ali nije poseban React/Vue projekat.

#### P3.16.2 Sta je kod nas backend sloj

Backend sloj je ono sto radi:

- logiku aplikacije
- raspored elemenata
- cuvanje projekata
- korisnike
- sesije
- billing model
- webhook obradu
- PDF/Excel export

Glavni backend fajlovi su:

- `app.py`
- `state_logic.py`
- `layout_engine.py`
- `drawer_logic.py`
- `project_store.py`
- `storage_backend.py`
- `postgres_store_migration.py`
- `auth_models.py`
- `billing_models.py`
- `billing_webhooks.py`
- `cutlist.py`

#### P3.16.3 Sta to znaci u praksi

Prakticno to znaci:

- UI i backend nisu odvojeni u dva repozitorijuma
- nema posebnog REST API projekta
- nema posebnog JS frontend build sistema
- server i UI zive u istoj Python aplikaciji

To je za sada prihvatljivo i ne mora odmah da se menja.

#### P3.16.4 Sta jos fali na frontend strani

Pre internet produkcije frontend strana jos trazi:

1. javni web sloj
- landing stranica
- pricing stranica
- jasan login / register / forgot password tok
- billing ekran koji izgleda kao proizvod

2. UX za potpune laike
- jos jednostavniji prvi tok
- manje tehnickih odluka odjednom
- jasnija objasnjenja i greske
- jos bolji onboarding
- cistiji prvi susret sa aplikacijom

3. produkcioni UI polish
- jasnija navigacija
- bolja vidljivost kljucnih akcija
- bolji responsive prikaz
- manje osecaja internog alata, vise osecaja gotovog proizvoda

### P3.17 Release readiness i operativna provera

Da ne bismo pred server opet radili rucnu proveru po secanju, uveden je poseban readiness sloj.

Trenutno postoji:

- `ops_diagnostics_cli.py`
- `/ops/runtime`
- `/ops/readiness`

Readiness proverava najvaznije blokere za staging i produkciju:

- da li `APP_ENV` odgovara cilju
- da li je `BASE_URL` postavljen i validan
- da li produkcija koristi `HTTPS`
- da li `SECRET_KEY` vise nije default
- da li je baza spremna
- da li je backend za bazu stvarno `Postgres` za staging/production
- da li su `Stripe` kljucevi, webhook secret i price ID-jevi postavljeni
- da li su Checkout / Portal URL-jevi validni

Prakticna korist:

- vise ne moramo rucno da tumacimo da li je app spremna za staging ili produkciju
- dobijamo tacan spisak:
  - `blockers`
  - `warnings`
  - `passed checks`

Definicija gotovo za ovaj blok:

- jedna komanda ili jedan endpoint odmah pokazuje sta jos blokira internet pustanje

### P3.18 Interni Ops ekran

Pored CLI i endpoint provere, dodat je i interni UI ekran za operativni pregled.

Trenutno postoji:

- toolbar tab `Ops`
- staging readiness kartica
- production readiness kartica
- runtime pregled:
  - `APP_ENV`
  - `BASE_URL`
  - storage backend/status
  - Stripe readiness flagovi
- poslednji audit tragovi

Pravila vidljivosti:

- `Ops` tab vide samo lokalni ili admin pristupi
- obican korisnik ne dobija dodatnu konfuziju u glavnom toku

Prakticna korist:

- support i staging provera vise ne zavise od citanja logova ili baze rucno
- odmah se vidi:
  - sta je spremno
  - sta blokira produkciju
  - koji auth/billing dogadjaji su se poslednji desili

#### P3.16.5 Sta jos fali na backend strani

Pre internet produkcije backend strana jos trazi:

1. baza
- pravi rad sa `Postgres` serverom
- staging i production DB provera
- migracioni postupak

2. auth i session
- stabilan produkcioni session tok
- restore sesije u browseru
- reset lozinke preko email-a
- zastita login toka
- cleanup isteklih sesija

3. authorization
- jasna pravila sta sme `local`
- sta sme `trial`
- sta sme `paid`
- sta sme `admin`

4. billing
- pravi `Stripe Checkout`
- pravi `Stripe Customer Portal`
- webhook provisioning i deprovisioning pristupa
- statusi pretplate koji direktno uticu na pristup app-u

5. operativa
- backup
- restore provera
- logging
- monitoring
- error tracking
- health check

#### P3.16.6 Sta sada ne treba raditi

Za sada ne treba odmah raditi:

- razdvajanje na poseban frontend projekat
- razdvajanje na poseban backend projekat
- veliki refactor u `React + API` arhitekturu

To sada ne donosi najbolji odnos vrednosti i vremena.

Najbolji pristup je:

1. zavrsiti postojeci monolit kako treba
2. pustiti stabilan internet MVP / beta SaaS
3. tek kasnije proceniti da li ima smisla vece arhitektonsko razdvajanje

#### P3.16.7 Kratak zakljucak

Trenutna aplikacija:

- ima frontend sloj
- ima backend sloj
- nema dve odvojene aplikacije

I to je za sada u redu.

Pravi fokus pre produkcije nije:

- novo frontend/backend razdvajanje

nego:

- `Postgres`
- produkcioni auth/session
- `Stripe`
- deploy
- `HTTPS`
- monitoring
- backup

Sprint 1:

1. ocistiti pocetni onboarding
2. uvesti preporuceni put za prvog korisnika
3. proveriti da laik moze da stigne do prvog elementa bez objasnjenja

Sprint 2:

1. ubaciti `Demo primer`
2. ubaciti `Recent projects`
3. ubaciti `Auto-save`

Sprint 3:

1. dodati `users/projects` model
2. odvojiti lokalni projekat od korisnickog projekta
3. pripremiti login i naplatu

Pravilo rada:

- posle svake UX izmene mora da prodje:
  - import check
  - smoke test
  - kratka manuelna provera glavnog toka

Definicija gotovo:

- imamo UX osnovu za internet verziju
- imamo bazu za korisnicke projekte
- imamo realan temelj za billing i deploy
- sistem ne zavisi od ruÄnog otkljucavanja pristupa
