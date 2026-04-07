# QA Launch 4 - rucna provera pre v1

Ovaj dokument je minimalni QA blok za v1 launch. Cilj nije da proveri sve moguce kuhinje, nego da potvrdi da najvazniji korisnicki tokovi daju tacan PDF i Excel pre naplate.

Pravila:

- aplikaciju testirati na `sr` ili `en` jeziku
- za svaki scenario napraviti screenshot rasporeda, PDF export i Excel export
- scenario ne moze biti `PASS` ako PDF ili Excel imaju ocigledno pogresne mere, `nan`, prazan okov ili pogresnu radnu plocu
- svaku gresku upisati sa: sta si uneo, sta si ocekivao, sta je aplikacija dala

## Status

| # | Scenario | Fokus | Status | PDF | Excel | Napomena |
|---|---|---|---|---|---|---|
| 1 | Jedan zid - osnovna kuhinja | carcass, frontovi, worktop, okov | PASS | `export_job_27_20260407_122029.pdf` | `export_job_28_20260407_122035.xlsx` | Provereno: 600+800 donji elementi, worktop 1420 mm, okov i dijakritika OK. |
| 2 | Jedan zid - sudopera + ploca | cutout, worktop, servisne napomene | PASS | `export_job_31_20260407_123517.pdf` | `export_job_32_20260407_123523.xlsx` | Provereno: worktop 2220 mm, cutout sudopera/ploca OK, parcijalna ledja OK, sokla CUT 2200x100 OK. |
| 3 | Jedan zid - fioke + masina za sudove | drawer box, klizaci, appliance | PASS | `export_job_35_20260407_130120.pdf` | `export_job_36_20260407_130126.xlsx` | Provereno: worktop 2820 mm, sokla 2800x100, klizaci OK, MZS front + vezna letva OK, sudopera cutout OK. |
| 4 | Visoki blok | visoki moduli, appliance, paneli | PASS | `export_job_44_20260407_140333.pdf` | `export_job_45_20260407_140340.xlsx` | Provereno: worktop 820 mm samo iznad donjeg elementa, ventilacija frižidera OK, špajz/frižider dijakritika OK, nema nan/None/null, W01 finalni rez bez M0-W01 duplikata u Servis obrada. |

## Opsta provera za svaki scenario

Proveri u aplikaciji:

- elementi se dodaju bez greske
- nema neocekivanog overlap/out-of-bounds warninga
- selekcija i izmena elementa rade
- krojna lista se otvara

Proveri u PDF-u:

- nazivi delova imaju dijakritiku (`Leđna`, `Ploča`, `Šta radiš`)
- nema `nan`, `None`, `null`
- postoji jasan deo za okov / hardware
- radna ploca prati stvarni raspon donjih elemenata, ne celu duzinu zida ako nema donjih elemenata
- servisne napomene za sudoperu/plocu/uredjaje postoje kad scenario to trazi

Proveri u Excel-u:

- kolone imaju `CUT Dužina`, `FIN Dužina`, `Dužina [mm]`
- nema `?` u header/subtitle tekstu
- sheet `Okovi` postoji i ima realne stavke
- nazivi modula su uskladjeni (`ploča`, `šarke`, `bušenje`, `šablon`)

## Scenario 1 - Jedan zid, osnovna kuhinja

Prostorija:

- layout: jedan zid
- zid A: `2400 mm`
- visina: `2600 mm`

Elementi sleva nadesno:

- `BASE_1DOOR` / Donji (1 vrata): `600 x 720 x 560`
- `BASE_2DOOR` / Donji (2 vrata): `800 x 720 x 560`
- `WALL_2DOOR` / Gornji (2 vrata): `800 x 720 x 320`

Napomena:

- ako prvi element uz levi zid prijavi warning za sarku, promeni stranu rucke. To je ocekivano.
- ocekivana radna ploca je oko `1420 mm`, ne `2420 mm`.

Rucno proveri:

- dno za `BASE_1DOOR` oko `564 x 540`
- dno za `BASE_2DOOR` oko `764 x 540`
- frontovi: 1 kom za `600`, 2 kom za `800`

## Scenario 2 - Jedan zid, sudopera + ploca za kuvanje

Prostorija:

- layout: jedan zid
- zid A: `3000 mm`
- visina: `2600 mm`

Elementi sleva nadesno:

- `BASE_2DOOR` / Donji (2 vrata): `800 x 720 x 560`
- `SINK_BASE` / Donji (sudopera): `800 x 720 x 560`
- `BASE_COOKING_UNIT` / Donji (kuhinjska jedinica: rerna + ploča za kuvanje): `600 x 720 x 560`
- `WALL_2DOOR` / Gornji (2 vrata): `800 x 720 x 320`
- `WALL_2DOOR` / Gornji (2 vrata): `800 x 720 x 320`
- opciono `WALL_HOOD` / Gornji (aspirator / napa): `600 x 720 x 320`, ako zelis da pokrijes prostor iznad ploce

Ocekivanje:

- radna ploca oko `2220 mm` za donji raspon `2200 mm`
- PDF ima cutout napomene za sudoperu i plocu
- sink modul u PDF preview-u nema laznju cesmu bez radne ploce
- cooking unit ima parcijalna ledja / servisnu napomenu za ventilaciju

## Scenario 3 - Jedan zid, fioke + masina za sudove

Prostorija:

- layout: jedan zid
- zid A: `3200 mm`
- visina: `2600 mm`

Elementi sleva nadesno:

- `BASE_DRAWERS_3` / Donji (fioke): `600 x 720 x 560`
- `BASE_DISHWASHER` / Donji (masina za sudove): `600 x 720 x 560`
- `SINK_BASE` / Donji (sudopera): `800 x 720 x 560`
- `BASE_2DOOR` / Donji (2 vrata): `800 x 720 x 560`
- `WALL_2DOOR` / Gornji (2 vrata): `800 x 720 x 320`
- `WALL_2DOOR` / Gornji (2 vrata): `800 x 720 x 320`

Ocekivanje:

- u okovu postoje klizaci za fioke
- masina za sudove nema nelogicne carcass delove kao obican ormarić
- worktop prati donji raspon oko `2800 mm` plus rezerva
- servisne napomene za sudoperu ostaju prisutne

## Scenario 4 - Visoki blok

Prostorija:

- layout: jedan zid
- zid A: `3600 mm`
- visina: `2600 mm`

Elementi sleva nadesno:

- `TALL_FRIDGE` / Visoki (frizider integrisani): `600 x 2100 x 560`
- `TALL_OVEN_MICRO` / Visoki kolona (rerna + mikrotalasna): `600 x 2100 x 560`
- `TALL_PANTRY` / Visoki ostava / spajz (police): `600 x 2100 x 560`
- `BASE_2DOOR`: `800 x 720 x 560`
- `WALL_2DOOR`: `800 x 720 x 320`

Ocekivanje:

- visoki elementi imaju logicne bokove, police, frontove i ledja
- appliance elementi imaju realne servisne napomene
- okov ukljucuje sarke/nosace polica gde treba
- worktop postoji samo iznad donjeg elementa, ne preko visokih elemenata

## Kako saljes rezultat za proveru

Za svaki scenario posalji:

- screenshot iz aplikacije
- putanju do PDF-a, npr. `C:\Users\Korisnik\Downloads\export_job_XX_....pdf`
- putanju do Excel-a, npr. `C:\Users\Korisnik\Downloads\export_job_XX_....xlsx`
- da li si video warning i tacan tekst warninga ako postoji

Posle toga proveravam PDF/Excel i upisujemo status u ovaj dokument.
