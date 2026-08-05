# VIDEO AUTOMATION MASTER PLAN — CabinetCut PRO / Krojna lista PRO

**Vlasnik dokumenta:** Ivan Milovanovic
**Kreiran:** 05.08.2026.
**Poslednja izmena:** 05.08.2026.
**Status:** FAZA 0 (dokumentacija i analiza) — završeno. Čeka se odobrenje pre FAZE 1 (PoC implementacija).

**Svrha ovog dokumenta:** glavni izvor istine za izradu svih promotivnih i tutorijalnih videa za CabinetCut PRO — hero video, onboarding, tutorijali, mikro-tutorijali, vertikalni sadržaj. Živi dokument, ažurira se posle svake faze.

**Pravilo rada:** ništa u ovoj fazi nije diralo produkcionu logiku, produkcionu bazu ili produkcioni billing. Sve što sledi (FAZA 1+) ide isključivo protiv staging/local okruženja i zahteva odobrenje pre implementacije.

---

## 1. CILJ SISTEMA

**Zašto pravimo video sistem:** aplikacija je vizuelan proizvod (2D/3D dizajn kuhinje) — najjači način da se dokaže vrednost je da se PROIZVOD VIDI u akciji, ne da se opisuje tekstom.

**Kome su videi namenjeni:** primarnoj ciljnoj grupi definisanoj u `MASTER_PROJEKAT.md` i `MARKETING_MASTER_PLAN.md` — običnom čoveku bez stolarskog iskustva koji želi sam da isplanira i sklopi kuhinju.

**Koju prepreku rešavamo:** glavna psihološka barijera je

> "Nisam stolar i verovatno neću znati da koristim aplikaciju."

Video mora vizuelno da dokaže suprotno:

> "Možeš da napraviš projekat kuhinje čak i bez prethodnog iskustva."

**Kako video to pokazuje:** brzim, jasnim tokom (klik → rezultat → klik → rezultat) bez tehničkog žargona, sa gotovim rezultatom prikazanim odmah na početku (ne kao nagrada na kraju dugog procesa).

### Checklista
- [x] Cilj i ciljna grupa definisani
- [x] Psihološka prepreka i poruka definisane

---

## 2. VRSTE VIDEA

| Tip | Trajanje | Format | Prioritet | Status |
|---|---|---|---|---|
| A. Hero video (landing/login) | 35–55s | 16:9 | P1 | Nije počelo |
| B. Kratki onboarding | 2–3 min | 16:9 | P3 | Nije počelo |
| C. Kompletan tutorijal | 5–10 min | 16:9 | P3 | Nije počelo |
| D. Mikro-tutorijali (1 funkcija) | 30–90s | 16:9/9:16 | P4 | Nije počelo |
| E. Vertikalni sadržaj (Reels/TikTok/Shorts) | 15–45s | 9:16 | P2 | Nije počelo |
| F. "What's new" video | varira | 16:9 | P4 | Nije počelo (čeka buduće feature-e) |

Svi tipovi se oslanjaju na ISTU tehničku infrastrukturu (Playwright snimanje + FFmpeg obrada) definisanu u sekciji 7, samo sa različitim scenario/montažnim parametrima.

### Checklista
- [x] Tipovi videa definisani i prioritizovani

---

## 3. GLAVNI DEMO SCENARIO

**Kuhinja koja se demonstrira:** jednostavna kuhinja "jedan zid" (layout koji aplikacija već podržava kao podrazumevani — `state.kitchen_layout = 'jedan_zid'`), dužine zida ~3000mm — dovoljno velika da stane par prepoznatljivih elemenata, dovoljno mala da ne oduzme vreme.

**Tačan tok kroz stvarni UI (potvrđeno čitanjem koda):**

1. **Login** — `/login` ruta, unos email/lozinka test naloga, klik "PRIJAVI SE" (`ui_public_site.py`)
2. **Novi projekat** — na dashboard-u (`ui_nova_tab.py`) klik na karticu "Nova kuhinja" / wizard step 1 (`ui_wizard_tab.py: _start_new_kitchen`)
3. **Mod merenja** — wizard step 2, izbor "Standard" moda (`_go_standard` u `ui_wizard_tab.py`) — brži tok za demo, "Pro" mod je opcioni naprednički put
4. **Dimenzije prostorije** — wizard step 3/4, room setup (`room_setup_wizard.py`) — unos dužine/visine zida
5. **Dodavanje elemenata** — glavni app ekran, sidebar katalog (`ui_catalog_panel.py`, `ui_sidebar_panel.py`) — klik na kategoriju ("Donji"/"Gornji"/"Visoki"), pa na konkretan element. Predlog redosleda za vizuelnu prepoznatljivost:
   - sudopera (`SINK_BASE`)
   - fioke (donji element sa fiokama)
   - ploča/rerna (`BASE_HOB` ili `BASE_COOKING_UNIT`)
   - visoki element/frižider (`TALL_FRIDGE`)
   - gornji elementi (wall zona)
6. **Prilagođavanje dimenzije** — klik na postavljeni element → edit panel (`ui_edit_panel.py`) → promena širine jednog elementa
7. **2D prikaz** — već podrazumevani prikaz (canvas toolbar, `ui_canvas_toolbar.py`)
8. **3D prikaz** — promena `ui.select(['2D','3D'])` na "3D" (stabilna, jezički-nezavisna vrednost)
9. **Krojna lista tab** — klik na tab "Krojna lista" (`ui_cutlist_tab.py`)
10. **Plan bušenja/kantovanje** — prikazano u istom tabu ili posebnom "Plan bušenja" tabu (postoji u toolbaru — potvrđeno u toolbar screenshot-ovima iz ranijeg dela sesije)
11. **Export PDF/Excel/CSV** — klik na dugme (`cutlist.btn_pdf` / `btn_excel` / `btn_csv`) — **VAŽNA TEHNIČKA NAPOMENA:** export je ASINHRON (background job preko `ThreadPoolExecutor`, `export_jobs.py`), UI prati status pollingom na svakih 0.5s i po završetku otvara download URL u NOVOM TABU. Za snimak ovo znači: treba računati ~1-3 sekunde čekanja između klika i vidljivog rezultata (notifikacija "export started" + otvaranje novog taba), NE trenutan rezultat.
12. **Završni CTA** — povratak na dashboard ili prikaz "Kreiraj besplatan nalog" poruke (za hero video, ovo je overlay tekst, ne stvarna app akcija)

**Napomena:** scenario je namerno linearan i kratak — ne uključuje room wizard "Pro" mod, ne uključuje sve moguće tipove elemenata, ne uključuje editovanje boje/materijala (može biti mikro-tutorijal posebno, tip D iz sekcije 2).

### Checklista
- [x] Scenario mapiran na stvarne funkcije/fajlove u kodu
- [ ] Potvrditi tačan redosled tabova/dugmadi vizuelno (screenshot prolazak) pre snimanja

---

## 4. STORYBOARD HERO VIDEA (16:9, cilj ~50s)

| Vreme | Scena | Tekst na ekranu (SR) | Napomena za montažu |
|---|---|---|---|
| 0–3s | Gotov 3D prikaz kuhinje (rezultat, ne proces) | "Planiraš novu kuhinju?" | Počinje na rezultatu — bez logo intro-a |
| 3–8s | Wizard: izbor "Nova kuhinja" → unos dimenzija | "Unesi dimenzije prostora" | Ubrzano 1.5-2x ako je unos spor |
| 8–22s | Dodavanje 4-5 elemenata redom (sudopera, fioke, ploča, visoki, gornji) | "Dodaj i prilagodi elemente" | Najbrži deo, cut između svakog dodavanja, bez praznog hoda |
| 22–29s | Prebacivanje 2D → 3D (select dropdown) | "Proveri raspored u 2D i 3D prikazu" | Blagi zoom na 3D prikaz posle prebacivanja |
| 29–40s | Klik na "Krojna lista" tab, prikaz tabele/plana bušenja | "Automatski dobijaš krojnu listu i plan bušenja" | Zoom/pan preko tabele da se vidi da su brojevi stvarni |
| 40–48s | Klik na export dugmad (PDF/Excel/CSV), prikaz notifikacije | "Dokumentacija spremna za radionicu" | Sakriti stvarni browser "Save As" dijalog ako se pojavi — cut pre njega |
| 48–55s | Logo + CTA | "Isplaniraj svoju kuhinju. Dobij krojnu listu spremnu za radionicu." + dugme "Kreiraj besplatan nalog" | Fade in, drži 3-4s |

**Napomena o prilagođavanju:** ovaj storyboard će se precizno uskladiti sa stvarnim tajmingom TEK nakon prvog sirovog PoC snimka (Faza 1) — trenutni brojevi su procena.

### Checklista
- [x] Storyboard po sekundama napravljen
- [ ] Uskladiti sa stvarnim tajmingom posle PoC snimka

---

## 5. VOICE-OVER

**Ton:** jednostavan, pouzdan, nenametljiv, bez tehničkog žargona, obraća se čoveku koji nikad nije koristio CAD alat.

### Verzija A — bez naracije (samo tekst + muzika)
Koristi tekstove iz storyboard-a (sekcija 4) kao on-screen overlay, uz laganu instrumentalnu muziku u pozadini. Preporučeno za prvu verziju (najjednostavnije za produkciju, nema potrebe za snimanjem glasa).

### Verzija B — kratak voice-over (hero video, ~45-50s teksta)

> "Planiraš novu kuhinju? Ne moraš da budeš stolar da bi je isplanirao sam. Unesi dimenzije prostora, dodaj elemente koje želiš, i odmah vidi kako izgleda — u 2D i 3D. Aplikacija automatski napravi krojnu listu i plan bušenja. Preuzmi dokumentaciju i odnesi je u bilo koju radionicu. Isplaniraj svoju kuhinju. Dobij krojnu listu spremnu za radionicu. Kreiraj besplatan nalog — probaj besplatno."

### Verzija C — duži voice-over (onboarding, ~2 min teksta)
_(dodaje se u Fazi 3, kad se pravi onboarding video — nije prioritet za prvu fazu)_

### Checklista
- [x] Verzija bez naracije definisana (tekstovi postoje u sekciji 4)
- [x] Kratka voice-over verzija napisana
- [ ] Duža onboarding voice-over verzija (odložiti za kasniju fazu)

---

## 6. TEKSTOVI NA EKRANU

### Srpski (koristi se u storyboard-u, sekcija 4)
1. "Planiraš novu kuhinju?"
2. "Unesi dimenzije prostora"
3. "Dodaj i prilagodi elemente"
4. "Proveri raspored u 2D i 3D prikazu"
5. "Automatski dobijaš krojnu listu i plan bušenja"
6. "Dokumentacija spremna za radionicu"
7. "Isplaniraj svoju kuhinju. Dobij krojnu listu spremnu za radionicu."
8. CTA: "Kreiraj besplatan nalog"

### English
1. "Planning a new kitchen?"
2. "Enter your room dimensions"
3. "Add and adjust cabinets"
4. "Check the layout in 2D and 3D"
5. "Get your cutlist and drilling plan automatically"
6. "Documentation ready for the workshop"
7. "Design your kitchen. Get a cutlist ready for the workshop."
8. CTA: "Create a free account"

**Pravilo:** svaki tekst maksimalno 6-8 reči, čitljivo za manje od 2 sekunde.

### Checklista
- [x] Svi tekstovi za hero video napisani na oba jezika
- [ ] Tekstovi za vertikalnu verziju (kraći, veći font — sekcija 12)

---

## 7. TEHNIČKA ARHITEKTURA

**Stanje mašine (provereno 05.08.2026):**
- Playwright: **NIJE instaliran** (ni sistemski ni u venv)
- FFmpeg: **NIJE instaliran** (nema u PATH-u)
- Node.js v24.14.0 i npm v11.9.0: dostupni
- Python 3.13.9 (venv) i 3.14.3 (sistemski): dostupni

### Poređenje opcija

| Opcija | Prednosti | Mane | Rizik | Zahtevnost | Kvalitet | Ponovljivost |
|---|---|---|---|---|---|---|
| **A. Playwright video recording** (ugrađeno snimanje konteksta) | Ugrađeno u Playwright (`record_video_dir`), nema dodatnih zavisnosti za snimanje, pouzdano | Snima ceo browser prozor, fiksna rezolucija po kontekstu, bez naprednih efekata | Nizak | Nizak | Dobar (WebM, čist) | Visoka |
| **B. Playwright + FFmpeg** (obrada posle) | Playwright snima sirovi materijal, FFmpeg radi rezanje/ubrzanje/tekst overlay/format konverziju | FFmpeg tekst/animacije su tekstualno-komandni, teže za složene prelaze | Srednji (FFmpeg treba instalirati) | Srednji | Dobar do vrlo dobar | Visoka |
| **C. Playwright + Remotion** (React-bazirana video montaža) | Vrlo precizna kontrola animacija/prelaza/teksta (kod umesto komandne linije) | Zahteva Node/React ekosistem za montažu, veća početna investicija u učenje/setup | Srednji-visok | Visok | Vrlo dobar do profesionalan | Visoka (jednom podešeno) |
| **D. Poseban staging-only demo mode u aplikaciji** | Mogao bi da ubrza/automatizuje same akcije unutar app-a | Menja produkcionu logiku (rizik), nepotrebno za snimanje browsera spolja | Visok (dodirujemo app kod) | Visok | Ne utiče direktno na kvalitet snimka | Zavisi od implementacije |
| **E. Ručno OBS snimanje (fallback)** | Nema tehničkog seta, brzo za jednokratan snimak | Nije ponovljivo/automatizovano, zavisi od ljudskog izvođenja svaki put | Nizak (ali ne rešava "sistem") | Nizak | Zavisi od operatera | Niska |

### Preporuka za prvu verziju

**Playwright (Python) za automatizaciju + ugrađeno video snimanje (opcija A), FFmpeg za obradu (opcija B).** Razlozi:
- Projekat je već Python (NiceGUI) — Playwright Python se prirodno uklapa u postojeći venv/tooling
- Ne zahteva dodirivanje aplikacionog koda (osim eventualno minimalnih, bezbednih `data-testid` atributa — sekcija 8)
- FFmpeg rešava rezanje/ubrzavanje/tekst overlay dovoljno dobro za prvu verziju — Remotion (opcija C) se razmatra tek ako FFmpeg tekstualni overlay postane nepraktičan za složenije animacije (eksplicitno predviđeno u Fazi 2 ovog plana)
- FFmpeg nije instaliran na mašini — predlog: koristiti Python paket `imageio-ffmpeg` (povlači statički FFmpeg binarni fajl automatski preko pip-a, bez potrebe za ručnom sistemskom instalacijom) ILI ručna instalacija (winget/choco) ako Ivan preferira sistemski FFmpeg

**Opcija D (ugrađeni demo mode) se NE preporučuje za prvu fazu** — nema jasnu prednost za snimanje browsera spolja i nosi nepotreban rizik dodirivanja produkcione logike. Razmatra se tek u Fazi 4 ako se pokaže konkretna potreba (npr. potreba da se demo pokreće bez pravog naloga).

### Checklista
- [x] Opcije istražene i upoređene
- [x] Preporuka data (Playwright + FFmpeg)
- [ ] Instalirati Playwright u venv (`pip install playwright` + `playwright install chromium`) — čeka odobrenje
- [ ] Rešiti FFmpeg dostupnost (`imageio-ffmpeg` ili sistemska instalacija) — čeka odobrenje

---

## 8. STABILNI SELEKTORI

**Nalaz:** u celom kodu (`grep` po `data-testid`, `data-video-step`, `aria-label`) **ne postoji nijedan stabilan test-selektor**. Sav UI tekst ide kroz `tr_fn()`/`i18n.py` i menja se po jeziku.

**Dobra vest:** dva ključna dela UI-ja VEĆ imaju stabilne, jezički-nezavisne vrednosti bez ikakve izmene koda:
- **2D/3D prekidač** (`ui_canvas_toolbar.py`) — `ui.select(['2D', '3D'], ...)` — vrednosti su bukvalno stringovi "2D"/"3D", ne prevode se
- **Template ID-jevi elemenata** (`ui_catalog_panel.py`) — svaki element u katalogu ima stabilan `tid` (npr. `SINK_BASE`, `BASE_HOB`, `TALL_FRIDGE`) nezavisan od jezika — koristi se interno u state-u, ali trenutno nije izložen kao DOM atribut

**Preporuka (minimalna, bezbedna izmena):** dodati `data-testid` atribut preko NiceGUI-jevog `.props('data-testid=...')` na:
1. Toolbar tabove (Početak/Elementi/Krojna lista/Plan bušenja) — trenutno raspoznatljivi samo po prevedenom tekstu
2. Katalog kartice elemenata — koristeći postojeći `tid` kao vrednost (npr. `data-testid="catalog-SINK_BASE"`) — prirodno se nadovezuje na već postojeći identifikator, nema nove logike
3. Export dugmad (PDF/Excel/CSV) u `ui_cutlist_tab.py`
4. Dugme "Nova kuhinja" / "Kreiraj besplatan nalog" na wizard step 1

Ovo su **isključivo dodati atributi** (`.props('data-testid=X')` na već postojeće `ui.button()`/`ui.card()` pozive) — ne menjaju izgled, ponašanje, ni poslovnu logiku. Rizik: minimalan. Pokrivenost testom: postojeći `test_post_login_dashboard.py` stil (grep po tekstu fajla) može se proširiti da proveri prisustvo ovih atributa, sprečavajući da se slučajno obrišu.

**Alternativa bez ikakve izmene koda (fallback za PoC):** fiksirati jezik naloga za snimanje na "sr" (ili "en"), i koristiti Playwright `get_by_role("button", name="Krojna lista")` / `get_by_text(...)` sa TAČNO poznatim prevedenim stringovima iz `i18n.py` za taj jezik. Ovo radi odmah, bez ijedne izmene aplikacije — preporučeno za PoC (Faza 1), dok se `data-testid` dodaje kasnije ako se pokaže da su tekstualni selektori krhki (npr. duplirani tekst na više mesta).

### Checklista
- [x] Analizirano postojeće stanje selektora (nema ih)
- [x] Identifikovani stabilni podaci koji već postoje (2D/3D vrednosti, template `tid`)
- [ ] Odluka: da li PoC ide sa tekstualnim selektorima (bez izmene koda) ili se prvo dodaju `data-testid` — **čeka odobrenje**

---

## 9. DEMO PODACI

**Princip:** svako pokretanje mora krenuti iz čistog, predvidivog stanja — bez ručnog čišćenja između snimanja.

### Preporučen pristup: dedikovan "video demo" nalog + reset pre svakog snimanja

- Napraviti **jedan poseban staging nalog rezervisan samo za snimanje** (ne mešati sa postojećim test/admin nalozima koji imaju "prljavu" istoriju iz ranijeg ručnog testiranja billing-a).
- Ovaj nalog treba da ima **trajno aktivan PRO pristup** (postavljen ručno u bazi, ne kroz pravi checkout) da bi krojna lista/export bili odmah dostupni bez potrebe da se u svakom snimku prolazi kroz plaćanje.
- Pre svakog pokretanja skripte: obrisati sve postojeće projekte tog naloga (jedan SQL/CLI poziv, slično postojećem `gdpr_account_tool.py` obrascu) da bi svaki snimak počeo od "Moji projekti: nema projekata".

### Alternative razmotrene

- **Novi projekat pri svakom pokretanju bez brisanja starih** — jednostavnije, ali dashboard će vremenom pokazivati gomilu starih demo projekata u pozadini (vidljivo ako se snimi dashboard ekran) — nije idealno za javni video.
- **Seed skripta koja priprema GOTOV demo projekat** — korisno za scenarije koji počinju "od već postojeće kuhinje" (npr. mikro-tutorijal "kako izmeniti postojeći element"), ali NIJE dobar za hero video jer hero video mora da pokaže kreiranje OD NULE.

**Zaključak:** kombinacija — mali CLI alat (npr. `video_automation/reset_demo_account.py`) koji briše projekte dedikovanog demo naloga pre snimanja, plus mogućnost da se opcionalno pre-seeduje gotov projekat za scenarije kojima to treba.

### Checklista
- [ ] Napraviti dedikovan demo nalog na stagingu (van ove faze — čeka odobrenje pošto uključuje kreiranje naloga i ručno postavljanje PRO pristupa)
- [ ] Napraviti reset skriptu za taj nalog

---

## 10. BEZBEDNOST

Pravila koja važe za CEO video sistem, bez izuzetka:

- ✅ Samo staging ili lokalno okruženje — **nikad produkcija**
- ✅ Bez realne kupovine — demo nalog ima ručno postavljen PRO pristup, ne prolazi kroz pravi Lemon Squeezy checkout
- ✅ Bez prikazivanja pravih korisničkih podataka — koristi se isključivo dedikovani demo nalog, nikad pravi korisnički nalog/projekti
- ✅ Bez tajni u snimku — email/lozinka demo naloga dolaze isključivo iz environment varijabli, nikad hardkodovano u kodu ili vidljivo na ekranu tokom snimanja (polje za lozinku se ionako maskira u UI-ju)
- ✅ Bez admin/ops ekrana u javnim videima — demo nalog NIJE admin nalog, nema pristup "Ops" tabu
- ✅ Environment varijable (nazivi finalno usaglašeni u Fazi 1):
  - `VIDEO_DEMO_BASE_URL` — staging URL
  - `VIDEO_DEMO_EMAIL` — email dedikovanog demo naloga
  - `VIDEO_DEMO_PASSWORD` — lozinka dedikovanog demo naloga
  - `VIDEO_DEMO_OUTPUT_DIR` — gde se snima sirovi/obrađeni video

### Checklista
- [x] Pravila definisana
- [ ] Env varijable stvarno postavljene (`.env.video.local`, gitignored) — čeka Fazu 1

---

## 11. VIDEO IZLAZI

| Format | Rezolucija | Namena |
|---|---|---|
| A. 16:9 | 1920×1080 | Landing stranica, YouTube, help centar |
| B. 9:16 | 1080×1920 | Reels, TikTok, Shorts |
| C. 1:1 (opciono) | 1080×1080 | Društvene mreže (feed post) |

**Za landing verziju (16:9) optimizacija:**
- MP4, H.264 kodek (najširа kompatibilnost)
- Web-friendly bitrate (cilj: dobra čitljivost teksta bez prevelike veličine fajla — konkretna brojka se određuje empirijski u Fazi 2 nakon prvog exporta)
- Poster/thumbnail slika (frame iz gotovog 3D prikaza, ne prazan ekran)
- BEZ autoplay zvuka (landing autoplay video mora biti mut po web konvenciji/browser politici)

### Checklista
- [x] Formati i namene definisani
- [ ] Prva 16:9 verzija (Faza 2)
- [ ] Prva 9:16 verzija (Faza 3)

---

## 12. TITLOVI

- SRT srpski — primarni jezik
- SRT engleski — za međunarodnu publiku (CabinetCut PRO brend)
- Opciono "burned-in" (utisnuti) titlovi za društvene mreže — TikTok/Reels korisnici često gledaju bez zvuka, utisnut tekst povećava zadržavanje

Tajming SRT fajlova se generiše iz istih timestamp-ova koji definišu on-screen tekstove (sekcija 4 i 6) — jedan izvor istine, dva izlaza (overlay u videu + SRT fajl).

### Checklista
- [ ] SRT SR (Faza 2)
- [ ] SRT EN (Faza 2)
- [ ] Burned-in verzija za vertikalni sadržaj (Faza 3)

---

## 13. ORGANIZACIJA FAJLOVA

```
video_automation/
    README.md                  # tačne komande za pokretanje (sekcija 14)
    requirements.txt            # playwright, imageio-ffmpeg, itd. (odvojeno od glavnog requirements.txt)
    playwright/
        record_demo.py          # glavna Playwright skripta (Faza 1 PoC)
        scenario_hero.py        # definicija koraka za hero scenario
    scenarios/
        hero_scenario.json      # opciono - podaci o koracima kao konfiguracija (Faza 4)
    overlays/
        texts_sr.json
        texts_en.json
    subtitles/
        hero_sr.srt
        hero_en.srt
    ffmpeg/
        process_video.sh        # ili .ps1 - rezanje/ubrzavanje/overlay/export
        crop_vertical.sh        # 9:16 verzija
    output/
        raw/                    # sirovi snimci (gitignored)
        final/                  # gotovi MP4 (gitignored, ili samo najbolja verzija se commit-uje ako je mala)
    assets/
        fonts/                  # ako treba poseban font za overlay tekst
```

Ova struktura je odvojena od glavnog aplikacionog koda (`video_automation/` kao poseban direktorijum na root nivou repoa) — jasno signalizira da je ovo pomoćni alat, ne deo produkcione aplikacije. Sirovi/gotovi video fajlovi idu u `.gitignore` (veliki binarni fajlovi ne pripadaju git istoriji) — objavljivanje gotovog videa ide direktno na landing/YouTube/social, ne kroz repo.

### Checklista
- [ ] Napraviti strukturu direktorijuma (Faza 1)
- [ ] Dodati `video_automation/output/` u `.gitignore`

---

## 14. KOMANDE I POKRETANJE

Planirane komande (tačan oblik se potvrđuje u Fazi 1):

```bash
# Instalacija (jednom)
pip install -r video_automation/requirements.txt
playwright install chromium

# Snimanje sirovog materijala (hero scenario)
python video_automation/playwright/record_demo.py --scenario hero

# Obrada u finalni 16:9 MP4
bash video_automation/ffmpeg/process_video.sh --input output/raw/hero.webm --output output/final/hero_16x9.mp4

# Obrada u 9:16 verziju
bash video_automation/ffmpeg/crop_vertical.sh --input output/final/hero_16x9.mp4 --output output/final/hero_9x16.mp4
```

### Checklista
- [ ] Tačne komande implementirane i testirane (Faza 1-3)

---

## 15. QA CHECKLISTA

Pre nego što se bilo koji video objavi javno, proveriti:

- [ ] Nema prikazanih tajni (lozinka, token, API ključ)
- [ ] Nema privatnih/pravih korisničkih podataka (samo demo nalog)
- [ ] Nema loading grešaka vidljivih u snimku
- [ ] Nema isečenih UI elemenata (posebno pri 9:16 crop-u)
- [ ] Tekst je čitljiv (dovoljno veliki font, dovoljno dugo na ekranu)
- [ ] Kursor ne zaklanja bitan sadržaj
- [ ] Nema predugih pauza/praznog hoda
- [ ] Aplikacija izgleda stabilno (nema vidljivih grešaka/glitch-eva u UI-ju)
- [ ] Krojna lista i export su STVARNO prikazani (ne lažni/mock podaci)
- [ ] CTA na kraju je jasan i čitljiv
- [ ] Zvuk (ako ima) nije preglasan u odnosu na govor/muziku
- [ ] Mobilni (9:16) crop ne seče ključan sadržaj (npr. dugme ili broj)

### Checklista
- [x] QA lista definisana — koristi se pri svakom finalnom exportu

---

## 16. STATUS I ROADMAP

| Faza | Opis | Status | Zavisnosti | Ključni fajlovi | Rizici | Verifikacija |
|---|---|---|---|---|---|---|
| P0 | Plan i dokaz koncepta (ovaj dokument) | **Završeno** | — | `VIDEO_AUTOMATION_MASTER_PLAN.md` | — | Ovaj dokument postoji i pregledan je |
| P1 | Hero video 16:9 (PoC → montaža) | Nije počelo — čeka odobrenje | Playwright/FFmpeg instalacija, demo nalog | `video_automation/playwright/record_demo.py`, `ffmpeg/process_video.sh` | Krhki selektori ako se ne reši sekcija 8; async export tajming (sekcija 3, tačka 11) | Sirovi snimak postoji, QA checklista (sekcija 15) prođe |
| P2 | Vertikalna verzija (9:16) | Nije počelo | Uspešan P1 | `ffmpeg/crop_vertical.sh` | Gubitak bitnog sadržaja pri cropu | Vizuelna provera da ništa bitno nije odsečeno |
| P3 | Onboarding video (2-3 min) | Nije počelo | Uspešan P1 | Prošireni scenario | Duži scenario = veći rizik krhkosti | QA checklista |
| P4 | Biblioteka mikro-tutorijala | Nije počelo | Uspešan P1-P3, stabilni selektori | Više scenario fajlova | Održavanje raste sa brojem scenarija | Svaki mikro-tutorijal prolazi QA |
| P5 | Dugoročni automatizovani demo sistem (JSON/YAML scenariji, Remotion, multi-jezik) | Nije počelo — razmatra se tek posle P1-P4 | Dokazan P1-P4 pristup | TBD | Prevremena kompleksnost ako se krene prerano | N/A |

### Checklista
- [x] Roadmap definisan sa jasnim redosledom faza

---

## 17. CHANGELOG

| Datum | Šta je urađeno | Fajlovi | Kako je provereno | Sledeće |
|---|---|---|---|---|
| 05.08.2026. | Kreiran `VIDEO_AUTOMATION_MASTER_PLAN.md` (Faza 0) — analiziran kod (`ui_wizard_tab.py`, `ui_canvas_toolbar.py`, `ui_catalog_panel.py`, `ui_cutlist_tab.py`, `export_jobs.py`), potvrđeno da Playwright/FFmpeg nisu instalirani, potvrđeno da ne postoje `data-testid` selektori, identifikovane stabilne vrednosti (2D/3D, template `tid`) | `VIDEO_AUTOMATION_MASTER_PLAN.md` (novi) | Pregled koda (grep/read), provera env-a (node/npm/python/ffmpeg verzije) | Čeka se odobrenje za Fazu 1 (PoC) — videti rezime na kraju odgovora u chatu |

---

*(Kraj dokumenta — FAZA 0 završena. Sledeći update ide posle FAZE 1 PoC-a.)*
