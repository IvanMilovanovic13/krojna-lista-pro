# QA Cutlist Scenarios

Ovaj dokument sluzi za rucnu proveru krojne liste i eksporta pre staging-a i hostinga.

Cilj:

- potvrditi da je krojna lista funkcionalno tacna
- potvrditi da su PDF / Excel / CSV medjusobno dosledni
- potvrditi da warning logika hvata realne probleme
- potvrditi da su najvazniji kuhinjski scenariji pokriveni i rucno provereni

## Kako se koristi

Za svaki scenario:

1. napravi ili ucitaj odgovarajucu probnu kuhinju
2. proveri sve stavke iz checkliste
3. upisi status:
   - `PASS`
   - `PARTIAL`
   - `FAIL`
4. upisi kratku napomenu sta nije dobro ako postoji problem
5. ako postoji bug:
   - napravi screenshot
   - navedi korake za reprodukciju
   - navedi ocekivano i stvarno ponasanje

## Obavezna checklist po scenariju

Za svaku probnu kuhinju proveriti:

- dimenzije svih modula
- carcass delove:
  - leva / desna stranica
  - dno
  - plafon / gornja ploca
  - police
  - ledja
- frontove:
  - broj
  - mere
  - raspored
- fioke i drawer box logiku
- worktop:
  - ukupnu duzinu
  - segmentaciju po zidu
  - cutout logiku
- hardware i potrosni materijal
- warning logiku
- `summary_all`
- `summary_detaljna`
- PDF / Excel / CSV doslednost
- rucni obracun nekoliko kljucnih stavki

## Pravilo rucnog obracuna

Za svaki scenario rucno proveriti najmanje:

- 2 carcass stavke
- 1 front stavku
- 1 worktop ili hardware stavku ako scenario to ima

Ako rucni obracun ne poklapa aplikaciju:

- scenario ne moze biti oznacen kao `PASS`

## Redosled rada

Preporuceni red:

1. scenariji `1 / 2 / 3`
2. scenariji `5 / 6 / 7`
3. scenariji `4 / 8 / 9`
4. scenario `10`

## Tabela scenarija

| # | Scenario | Sta je fokus | Status | Napomena |
|---|---|---|---|---|
| 1 | Jedan zid - mala jednostavna kuhinja | osnovni carcass, frontovi, summary | TODO |  |
| 2 | Jedan zid - sudopera + ploca za kuvanje | cutout, worktop, warning | TODO |  |
| 3 | Jedan zid - fioke + masina za sudove | drawer logic, appliance, hardware | TODO |  |
| 4 | Tall block - frizider + oven/micro kolona | tall moduli, appliance frontovi, hardware | TODO |  |
| 5 | L-kuhinja sa ugaonim donjim elementom | corner logika, clearance, worktop | TODO |  |
| 6 | Galley kuhinja sa dve linije | multi-wall raspodela, summary, eksport | TODO |  |
| 7 | U-kuhinja sa vise worktop segmenata | worktop segmentacija i warning | TODO |  |
| 8 | Raised dishwasher scenario | visine, worktop, consistency | TODO |  |
| 9 | Filler / end panel scenario | panel obrada, summary_detaljna | TODO |  |
| 10 | Namerno problematican scenario | warning i fail-safe logika | TODO |  |

## Operativni template po scenariju

Kopiraj ovaj blok za scenario koji proveravas:

```text
Scenario:
Status: TODO

Provera:
- Modul mere:
- Carcass:
- Frontovi:
- Fioke / drawer box:
- Worktop:
- Hardware:
- Warning:
- Summary all:
- Summary detaljna:
- PDF / Excel / CSV:
- Rucni obracun:

Bugovi:
- 

Napomena:
- 
```

## Prva serija za rad

Prvo odraditi scenario 1, 2 i 3.

To je minimalni ulazni blok koji mora biti zavrsen pre nego sto predjemo na:

- L / galley / U rasporede
- tall block
- raised dishwasher
- filler / panel edge case

## Zavrsni kriterijum

QA blok je zatvoren tek kada:

- svih 10 scenarija imaju upisan status
- nema otvorenih `FAIL` scenarija
- svi `PARTIAL` imaju jasan razlog i plan popravke
- PDF / Excel / CSV su provereni na vise scenarija
- rucni obracun je potvrdio kljucne mere u svakom scenariju
