# P0B Template Audit

Datum: 12.03.2026
Opseg: aktivni `template_id` iz `module_templates.json`
Ukupno aktivnih template-a: `52`

Scope odluka:
- `krojna_lista_pro` je kitchen-only app
- TV i wardrobe template-i su trenutno prisutni u kodu kao istorijski/legacy materijal
- za dalji razvoj ove app oni se vode kao `OUT OF SCOPE`

Status legend:
- `OK` = pokriveno dovoljno dobro za trenutni engine
- `PARTIAL` = radi, ali je logika genericka ili nepotpuna za proizvodni/laicki workflow
- `FAIL` = ozbiljan jaz izmedju kataloga i proizvodnog izlaza
- `OUT` = van scope-a ove aplikacije; ne razvijati dalje u `krojna_lista_pro`

Kolone:
- `Render` = 2D/3D preview stabilan
- `Cutlist` = carcass/fronts/backs/drawer/worktop logika
- `HW` = okovi i potrosni materijal
- `Asm` = assembly instructions
- `Risk` = prioritet za sanaciju

## 1. Executive Summary

Zakljucak:
- `Render`: svi aktivni template-i prolaze osnovni smoke preview.
- `Cutlist`: jezgro je dobro za standardne kuhinjske module.
- `Najveci problem`: engine i dalje prepoznaje mnogo modula preko substring pravila, a deo legacy ne-kuhinjskih template-a je i dalje u kodu.
- `Kriticni FAIL template-i`: nema otvorenih kitchen-only critical fail modula iz prvog talasa
- `Van scope-a`: TV moduli i wardrobe porodica

## 2. Matrix po template-u

| Template | Zona | Render | Cutlist | HW | Asm | Risk | Napomena |
|---|---|---|---|---|---|---|---|
| `BASE_1DOOR` | `base` | OK | OK | OK | OK | Closed | Standardni bazni 1-vrata uskladjen sa laickim assembly tokom |
| `BASE_2DOOR` | `base` | OK | OK | OK | OK | Closed | Standardni bazni 2-vrata uskladjen sa laickim assembly tokom |
| `BASE_DOORS` | `base` | OK | OK | OK | OK | Closed | Alias standardnih vrata zatvoren kroz isti assembly workflow |
| `BASE_DRAWERS` | `base` | OK | OK | OK | OK | Closed | Fiokar sada u assembly sastavnici eksplicitno navodi frontove i klizace |
| `BASE_DRAWERS_3` | `base` | OK | OK | OK | OK | Closed | Stabilan standardni fiokar sa laicki citljivom assembly sastavnicom |
| `BASE_DOOR_DRAWER` | `base` | OK | OK | OK | OK | Closed | Kombi vrata+fioka dobio eksplicitnu sastavnicu vrata, fronta fioke i klizaca |
| `BASE_DISHWASHER` | `base` | OK | OK | OK | OK | Closed | Zatvoreno 12.03.2026: MZS dobila appliance stavku, montažni set i poseban assembly bez lažnog korpusa |
| `BASE_DISHWASHER_FREESTANDING` | `base` | OK | OK | OK | OK | Closed | Dodato 12.03.2026: samostojeca MZS bez korpusa/fronta sa appliance assembly tokom |
| `BASE_COOKING_UNIT` | `base` | OK | OK | OK | OK | Closed | Zatvoreno 12.03.2026: appliance stavke + lažni front + assembly za rernu i ploču |
| `BASE_OVEN_HOB_FREESTANDING` | `base` | OK | OK | OK | OK | Closed | Dodato 12.03.2026: samostojeci sporet bez korpusa/fronta sa appliance assembly tokom |
| `SINK_BASE` | `base` | OK | OK | OK | OK | Closed | Zatvoreno 12.03.2026: instalaciona napomena, shopping stavke i poseban assembly za sudoperu |
| `BASE_NARROW` | `base` | OK | OK | OK | OK | Closed | Zatvoreno 12.03.2026: uski izvlačni modul dobio front, cargo hardware i assembly |
| `BASE_CORNER` | `base` | OK | OK | OK | OK | Closed | Zatvoreno 12.03.2026: ugaoni front + hardware + assembly |
| `BASE_OPEN` | `base` | OK | OK | OK | OK | Closed | Otvoreni bazni element dobio police, klince i poseban assembly za police |
| `WALL_1DOOR` | `wall` | OK | OK | OK | OK | Closed | Standardni zidni 1-vrata ima jasan assembly i zidni workflow |
| `WALL_2DOOR` | `wall` | OK | OK | OK | OK | Closed | Standardni zidni 2-vrata ima jasan assembly i zidni workflow |
| `WALL_DOORS` | `wall` | OK | OK | OK | OK | Closed | Alias standardnih zidnih vrata zatvoren kroz isti assembly workflow |
| `WALL_GLASS` | `wall` | OK | OK | OK | OK | Closed | Zatvoreno 12.03.2026: stakleni hardware + assembly za vitrinu |
| `WALL_OPEN` | `wall` | OK | OK | OK | OK | Closed | Otvoreni zidni element dobio police, klince i jasan assembly za kacenje i police |
| `WALL_LIFTUP` | `wall` | OK | OK | OK | OK | Closed | Zatvoreno 12.03.2026: lift-up hardware dopunjen i assembly usklađen |
| `WALL_CORNER` | `wall` | OK | OK | OK | OK | Closed | Zatvoreno 12.03.2026: ugaoni front + hardware + assembly |
| `WALL_NARROW` | `wall` | OK | OK | OK | OK | Closed | Zatvoreno 12.03.2026: dodat front, šarke i usklađen proizvodni izlaz |
| `WALL_HOOD` | `wall` | OK | OK | OK | OK | Closed | Zatvoreno 12.03.2026: appliance + ventilacioni set + assembly + napomena za odvod |
| `WALL_MICRO` | `wall` | OK | OK | OK | OK | Closed | Zatvoreno 12.03.2026: appliance + ventilaciona napomena + assembly |
| `TALL_FRIDGE` | `tall` | OK | OK | OK | OK | Closed | Zatvoreno 12.03.2026: korpus + appliance front + hardware za integrisani frižider |
| `TALL_FRIDGE_FREESTANDING` | `tall` | OK | OK | OK | OK | Closed | Dodato 12.03.2026: samostojeci frizider bez korpusa/fronta sa appliance assembly tokom |
| `TALL_FRIDGE_FREEZER` | `tall` | OK | OK | OK | OK | Closed | Zatvoreno 12.03.2026: korpus + 2 appliance fronta + hardware za integrisani frižider/zamrzivač |
| `TALL_OVEN_MICRO` | `tall` | OK | OK | OK | Closed | Medium | Appliance kolona zatvorena: ugradna mikrotalasna + rerna + donji servisni front + assembly uskladjen |
| `TALL_PANTRY` | `tall` | OK | OK | OK | OK | Closed | Pantry assembly dopunjen policama i raspodelom tereta za laicki workflow |
| `TALL_DOORS` | `tall` | OK | OK | OK | OK | Closed | Standardna visoka kolona sa vratima ima jasan assembly i anti-tip korak |
| `TALL_OVEN` | `tall` | OK | OK | OK | Closed | Medium | Appliance kolona zatvorena: ugradna rerna + donji servisni front + assembly uskladjen |
| `TALL_OPEN` | `tall` | OK | OK | OK | OK | Closed | Otvoreni visoki element dobio police, klince i poseban assembly za police |
| `TALL_TOP_DOORS` | `tall_top` | OK | OK | OK | OK | Closed | Gornja popuna iznad visokog elementa dobila poseban assembly bez laznih nogica i sa vezom na kolonu |
| `TALL_TOP_OPEN` | `tall_top` | OK | OK | OK | OK | Closed | Otvorena gornja popuna dobila police, klince i poseban assembly bez laznih nogica |
| `WALL_UPPER_1DOOR` | `wall_upper` | OK | OK | OK | OK | Closed | Gornji 1-vrata dobio poseban gornji-element assembly workflow |
| `WALL_UPPER_2DOOR` | `wall_upper` | OK | OK | OK | OK | Closed | Gornji 2-vrata dobio poseban gornji-element assembly workflow |
| `WALL_UPPER_OPEN` | `wall_upper` | OK | OK | OK | OK | Closed | Gornji otvoreni modul dobio police, klince i jasan assembly za montazu na zid |
| `TALL_GLASS` | `tall` | OK | OK | OK | OK | Closed | Zatvoreno 12.03.2026: stakleni hardware + tall assembly za vitrinu |
| `BASE_TRASH` | `base` | OK | OK | OK | OK | Closed | Sortirnik logika zatvorena 12.03.2026: front + pull-out hardware + assembly |
| `BASE_HOB` | `base` | OK | OK | OK | OK | Closed | HOB bazni modul zatvoren 12.03.2026: vrata + hardware + assembly |
| `FILLER_PANEL` | `base` | OK | OK | OK | OK | Closed | Panel-only logika zatvorena 12.03.2026 |
| `BASE_TV_2DOOR` | `base` | OUT | OUT | OUT | OUT | Out | Legacy TV modul; prebaciti u `krojna_studio` |
| `BASE_TV_DRAWERS` | `base` | OUT | OUT | OUT | OUT | Out | Legacy TV modul; prebaciti u `krojna_studio` |
| `WALL_TV_OPEN` | `wall` | OUT | OUT | OUT | OUT | Out | Legacy TV modul; prebaciti u `krojna_studio` |
| `TALL_WARDROBE_2DOOR` | `tall` | OUT | OUT | OUT | OUT | Out | Wardrobe modul je van scope-a ove app |
| `TALL_WARDROBE_DRAWERS` | `tall` | OUT | OUT | OUT | OUT | Out | Wardrobe modul je van scope-a ove app |
| `TALL_WARDROBE_2DOOR_SLIDING` | `tall` | OUT | OUT | OUT | OUT | Out | Wardrobe modul je van scope-a ove app |
| `BASE_TV_OPEN` | `base` | OUT | OUT | OUT | OUT | Out | Legacy TV modul; prebaciti u `krojna_studio` |
| `END_PANEL` | `base` | OK | OK | OK | OK | Closed | Panel-only logika zatvorena 12.03.2026 |
| `TALL_WARDROBE_AMERICAN` | `tall` | OUT | OUT | OUT | OUT | Out | Wardrobe modul je van scope-a ove app |
| `TALL_WARDROBE_CORNER` | `tall` | OUT | OUT | OUT | OUT | Out | Wardrobe modul je van scope-a ove app |
| `TALL_WARDROBE_CORNER_SLIDING` | `tall` | OUT | OUT | OUT | OUT | Out | Wardrobe modul je van scope-a ove app |
| `TALL_WARDROBE_INT_SHELVES` | `tall` | OUT | OUT | OUT | OUT | Out | Wardrobe modul je van scope-a ove app |
| `TALL_WARDROBE_INT_DRAWERS` | `tall` | OUT | OUT | OUT | OUT | Out | Wardrobe modul je van scope-a ove app |
| `TALL_WARDROBE_INT_HANG` | `tall` | OUT | OUT | OUT | OUT | Out | Wardrobe modul je van scope-a ove app |

## 3. Grupni nalazi

### 3A. Standardni kuhinjski moduli

Status:
- Uglavnom `OK` na nivou osnovnog cutlist engine-a

Obuhvata:
- bazni sa vratima
- bazni sa fiokama
- standardni gornji
- standardni visoki
- open/pantry/basic glass

Glavni nedostatak:
- standardni moduli su sada uglavnom zatvoreni; preostali posao je siri `P0A` servis/shopping/checklist paket za laika

### 3B. Appliance i specijalni kuhinjski moduli

Status:
- `OK`

Obuhvata:
- `BASE_DISHWASHER`
- `BASE_COOKING_UNIT`
- `SINK_BASE`
- `WALL_HOOD`
- `WALL_MICRO`
- `TALL_OVEN`
- `TALL_OVEN_MICRO`
- `TALL_FRIDGE*`

Glavni problem:
- appliance modelovanje je zatvoreno po template-ima, ali kompletan servis/shopping paket za laika ostaje posao u `P0A`
- dodatno pravilo od 12.03.2026:
  - svaki veliki uredjaj mora biti eksplicitno modelovan kao `samostojeci` ili `ugradni`
  - `samostojeci` = bez korpusa, bez fronta
  - `ugradni` = sa korpusom i sa frontom/frontovima ako ih uredjaj koristi
  - ovo mora biti odvojeno za:
    - frizider
    - masina za sudove
    - sporet / rerna + ploca

### 3C. Panel-only i specijalni non-carcass moduli

Status:
- `OK`

Obuhvata:
- `FILLER_PANEL`
- `END_PANEL`

Status 12.03.2026:
- zatvoreno
- paneli sada imaju poseban carcass red, bez laznih ledja/frontova, sa minimalnim panel hardware i posebnim assembly tokom

### 3D. TV i ne-kuhinjski moduli

Status:
- `OUT`

Obuhvata:
- `BASE_TV_2DOOR`
- `BASE_TV_DRAWERS`
- `BASE_TV_OPEN`
- `WALL_TV_OPEN`

Napomena:
- ne razvijati dalje u `krojna_lista_pro`
- prebaciti ili odrzavati u `krojna_studio`

### 3E. Wardrobe porodica

Status:
- `OUT`

Obuhvata:
- hinged wardrobe
- drawer wardrobe
- sliding wardrobe
- american wardrobe
- corner wardrobe
- interior-only wardrobe sections

Napomena:
- wardrobe porodica vise nije razvojni prioritet ove app
- ostaje materijal za `krojna_studio`

## 4. Prioritet sanacije

### P0B-1 Critical - odmah

Nema preostalih otvorenih `critical` kitchen-only modula iz prvog talasa.

### P0B-2 High - sledeci talas

1. `BASE_DISHWASHER`
2. `BASE_COOKING_UNIT`
3. `SINK_BASE`
4. `WALL_NARROW`

### P0B-3 Medium - posle toga

1. corner kitchen moduli
2. stakleni moduli
3. appliance kolone
4. narrow moduli
5. wall_upper / tall_top dopune

## 5. Predlog implementacije P0B

Redosled:
1. Uvesti centralni klasifikacioni sloj:
   - `template_class`
   - `has_carcass`
   - `has_backs`
   - `front_mode`
   - `hardware_mode`
   - `assembly_mode`
2. Izbaciti kriticne `substring-only` pogodke za specijalne module
3. Dodati per-template audit smoke:
   - svaka sekcija mora imati ocekivane redove
4. Posle toga tek siriti shopping list i servis paket

## 6. Operativni sledeci korak

Prva naredna implementaciona meta:
- `BASE_DISHWASHER`
- `BASE_COOKING_UNIT`
- `SINK_BASE`
- `WALL_NARROW`

To je sledeci kuhinjski skup sa najvecim odnosom rizik / korist.
