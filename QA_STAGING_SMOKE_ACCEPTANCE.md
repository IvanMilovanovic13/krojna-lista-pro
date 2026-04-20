# QA Staging Smoke + Acceptance

Ovaj dokument je operativna checklista za stvarno testiranje hostovane staging verzije.

Aktuelni cilj nije novi lokalni development blok, nego potvrda da staging host radi kroz najvaznije korisnicke i billing tokove.

Primarni staging domen:

- `https://staging.cabinetcutpro.com`

Datum referentnog statusa:

- `20. april 2026.`

## 1. Cilj testa

Potvrditi da staging okruzenje prolazi:

- javni pristup i auth tok
- billing ulaz i checkout
- customer portal
- exporte i zasticeni download
- i18n / UI polish
- multi-user izolaciju
- admin / ops kontrole

## 2. Pravilo rada

- test radi redom kako je naveden u ovom dokumentu
- svaku stavku oznaci kao `PASS`, `FAIL` ili `BLOCKED`
- za svaki `FAIL` upisi:
  - sta si kliknuo
  - sta si ocekivao
  - sta se desilo
  - screenshot ili URL ako postoji
- ne preskaci billing i export deo, jer su oni glavni acceptance kriterijumi

## 3. Pre pocetka

Pre nego sto krenes:

- proveri da je staging deploy zavrsen
- proveri da je na hostu najnoviji commit koji zelis da testiras
- pripremi bar 4 naloga:
  - novi korisnik za registraciju
  - neplaceni korisnik
  - placeni ili admin korisnik
  - drugi korisnik za multi-user izolaciju
- pripremi bar 1 primer projekta za export test
- otvori jedan browser prozor za glavni test i jedan private/incognito prozor za drugi nalog

## 4. Brzi status zapis

Popuni ovo pre i posle testa:

| Polje | Vrednost |
|---|---|
| Datum testa | |
| Tester | |
| Staging URL | `https://staging.cabinetcutpro.com` |
| Commit / build | |
| Browser | |
| Ukupan rezultat | |
| Napomena | |

## 5. Glavni redosled testiranja

Radi ovim redom:

1. anonimni tok
2. registracija + verifikacija + sesija
3. access gate i billing ulaz
4. Lemon checkout
5. customer portal
6. exporti
7. UI polish / i18n / layout
8. multi-user izolacija
9. admin / ops

## 6. Checklista po blokovima

### 6.1 Anonimni tok

| # | Korak | Ocekivanje | Status | Napomena |
|---|---|---|---|---|
| A1 | Otvori landing stranu | Strana se ucita bez greske | | |
| A2 | Promeni jezik na javnom delu | Label-e se dosledno promene | | |
| A3 | Otvori pricing | Pricing strana radi i nema mesanih SR/EN labela | | |
| A4 | Otvori login | Login forma radi i copy je smislen | | |
| A5 | Otvori register | Register forma radi i nema polomljenog layout-a | | |
| A6 | Proveri da nema lazno otkljucanog PRO pristupa bez logina | Bez sesije nema placenog pristupa | | |

### 6.2 Registracija + verifikacija + sesija

| # | Korak | Ocekivanje | Status | Napomena |
|---|---|---|---|---|
| B1 | Registruj potpuno nov nalog | Registracija prodje bez pucanja forme | | |
| B2 | Proveri verify-email tok | Korisnik dobije ili vidi validan verification flow | | |
| B3 | Pokusaj login pre verifikacije ako je primenljivo | Pristup je blokiran ili jasno ogranicen dok nalog nije verifikovan | | |
| B4 | Zavrsena verifikacija | Nalog prelazi u validno aktivno stanje | | |
| B5 | Login sa verifikovanim nalogom | Korisnik ulazi u validnu sesiju | | |
| B6 | Logout | Sesija se gasi bez polomljenog redirect-a | | |
| B7 | Ponovni login | Sesija se normalno obnavlja | | |

### 6.3 Access gate i billing ulaz

| # | Korak | Ocekivanje | Status | Napomena |
|---|---|---|---|---|
| C1 | Uloguj se kao neplaceni korisnik | Aplikacija radi bez lazno otkljucanog PRO pristupa | | |
| C2 | Klikni `Krojna lista` bez placenog pristupa | Korisnik ide ka `Nalog` / billing toku | | |
| C3 | Probaj `Sacuvaj` i `Ucitaj` ako su zakljucani pravilom pristupa | Redirekcija ide na pravi account/billing tok | | |
| C4 | Otvori `Nalog` | Jasno su vidljive plan opcije i status naloga | | |

### 6.4 Lemon checkout

Ovo je najvazniji acceptance blok.

| # | Korak | Ocekivanje | Status | Napomena |
|---|---|---|---|---|
| D1 | Klikni weekly plan | Otvara se pravi Lemon checkout | | |
| D2 | Vrati se iz checkout-a kroz cancel tok | Pristup ne sme lazno da ostane otkljucan | | |
| D3 | Klikni monthly plan | Otvara se pravi Lemon checkout | | |
| D4 | Prodji success povratak | Povratak ide na `/login?checkout=success` | | |
| D5 | Posle webhook / session refresh-a proveri nalog | Tier i billing status su azurirani | | |
| D6 | Proveri da su PRO funkcije otkljucane samo kada treba | Nema preuranjenog niti izostalog unlock-a | | |

### 6.5 Customer portal

| # | Korak | Ocekivanje | Status | Napomena |
|---|---|---|---|---|
| E1 | Otvori customer portal iz `Nalog` taba | Portal se otvara bez greske | | |
| E2 | Vrati se nazad u aplikaciju | Sesija ostaje validna | | |
| E3 | Posle povratka proveri account status | UI ne puca i status je citljiv | | |

### 6.6 Exporti

Koristi nalog koji ima pravo pristupa exportu.

| # | Korak | Ocekivanje | Status | Napomena |
|---|---|---|---|---|
| F1 | Napravi ili ucitaj projekat | Projekat se otvara bez greske | | |
| F2 | Otvori `Krojna lista` | Tab se ucitava normalno | | |
| F3 | Generisi PDF | PDF se generise i preuzima | | |
| F4 | Generisi Excel | Excel se generise i preuzima | | |
| F5 | Generisi CSV | CSV se generise i preuzima | | |
| F6 | Proveri protected export download | Download radi samo za validan token i pravog korisnika | | |
| F7 | Proveri sadrzaj exporta | Nema `NaN`, `None`, polomljenih sekcija ni praznog okova | | |

### 6.7 UI polish / i18n / layout

| # | Korak | Ocekivanje | Status | Napomena |
|---|---|---|---|---|
| G1 | Promeni jezik u aplikaciji | UI odmah menja tekstove | | |
| G2 | Proveri canvas posle promene jezika | Canvas labele se osveze odmah | | |
| G3 | Proveri cutlist legendu i nazive delova | Tekstovi su prevedeni i smisleni | | |
| G4 | Dodaj element sa sirinom blizu limita | Inline hint za slobodan prostor radi | | |
| G5 | Edituj postojeci element sa prevelikom sirinom | Inline upozorenje radi i ne oslanja se samo na notify | | |
| G6 | Skroluj duboko u listi elemenata i izaberi donji element | Skrol ne sme da skoci na vrh pri selekciji | | |
| G7 | Proveri `Početak` za ulogovanog korisnika | Ne sme biti duplog dashboard / wizard toka | | |
| G8 | Proveri `Podešavanja` tab | Tab je vidljiv i stvarno vodi na settings ekran | | |
| G9 | Proveri duzu kuhinju ili gust raspored | Layout ostaje citljiv | | |

### 6.8 Multi-user izolacija

Za ovo koristi glavni browser i private/incognito prozor.

| # | Korak | Ocekivanje | Status | Napomena |
|---|---|---|---|---|
| H1 | Uloguj korisnika A u glavni prozor | Sesija A radi normalno | | |
| H2 | Uloguj korisnika B u private prozor | Sesija B radi normalno | | |
| H3 | Proveri listu projekata za korisnika A | Ne vidi projekte korisnika B | | |
| H4 | Proveri listu projekata za korisnika B | Ne vidi projekte korisnika A | | |
| H5 | Probaj export link / rezultat korisnika A iz sesije B | Preuzimanje mora biti blokirano | | |
| H6 | Probaj export link / rezultat korisnika B iz sesije A | Preuzimanje mora biti blokirano | | |

### 6.9 Admin / ops

| # | Korak | Ocekivanje | Status | Napomena |
|---|---|---|---|---|
| I1 | Uloguj admin nalog | Admin sesija radi | | |
| I2 | Otvori `Ops` tab | Tab je dostupan samo adminu | | |
| I3 | Uloguj obican korisnicki nalog | `Ops` nije dostupan | | |
| I4 | Otvori `/healthz` | Endpoint vraca zdravo stanje | | |
| I5 | Otvori `/readyz` | Endpoint vraca zdravo stanje | | |
| I6 | Otvori `/ops/runtime` | Runtime odgovara staging okruzenju | | |
| I7 | Otvori `/ops/readiness` | Rezultat odgovara stvarnom staging runtimu | | |

## 7. Najvazniji acceptance kriterijumi

Staging prolaz smatramo validnim samo ako su `PASS` sledece tacke:

1. `checkout`
2. `webhook`
3. `upgrade korisnika`
4. `customer portal`
5. `protected export download`

Ako bilo koja od ovih 5 stavki padne, staging acceptance nije zatvoren.

## 8. Zavrsna odluka

Na kraju upisi jednu od ove 3 odluke:

- `PASS` - staging je spreman za dalje acceptance korake
- `PASS WITH ISSUES` - glavni tok radi, ali postoje neblokirajuce regresije
- `FAIL` - staging ne prolazi i mora nova korekcija pre nastavka

## 9. Blok za rezultat testa

```text
Datum:
Tester:
Build / commit:
Ukupan rezultat:

Glavni nalazi:
- 
- 
- 

Blokirajuce stavke:
- 
- 

Sledeci korak:
- 
```
