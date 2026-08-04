# START NAPLATE BEZ FIRME (lean pokretanje) + kako preko Lemon Squeezy

**Datum:** 23. jul 2026.
**Za koga:** pokretanje naplate kada je fiksni mesečni paušal ZA SADA preskup, a prihod još nesiguran.
**Poveznica:** ovo je „jeftin start" verzija plana. Pun plan naplate je u [REALIZACIJA_BILLING.md](REALIZACIJA_BILLING.md).

---

## 1. GLAVNA IDEJA

> **Ne otvaraj firmu odmah.** Pusti app, primaj Lemon Squeezy isplate kao **fizičko lice**,
> prijavljuj prihod **po kvartalu** (frilenser / samooporezivanje) i plaćaj **samo kad stварno zaradiš**.
> Firmu (preduzetnik paušalac) otvoriš **tek kad prihod redovno pređe trošak paušala.**

Zašto ovako:

- paušal je fiksno ~20.000–35.000 RSD **svakog meseca**, bez obzira da li imaš kupce → skupo na startu
- frilenser model prati **stварnu zaradu**: nema kupaca → nema poreza taj kvartal
- Lemon Squeezy isplaćuje i fizičkim licima → **firma nije uslov da primiš novac**

---

## 2. KAKO NOVAC UOPŠTE DOLAZI DO TEBE (tok)

```
Kupac plati karticom  →  LEMON SQUEEZY naplati i zadrži svoj deo + porez/PDV kupca
                      →  Lemon isplati TVOJ deo na tvoj payout nalog (PayPal / Wise)
                      →  ti povučeš na svoj račun/karticu u Srbiji
                      →  taj priliv prijaviš Poreskoj po kvartalu (frilenser model)
```

Bitna prednost: Lemon je **Merchant of Record** = on je zvanični prodavac.
On skuplja i plaća PDV/sales tax kupcima umesto tebe. Ti dobijaš **već očišćen svoj deo.**

---

## 3. KAKO POKRENUTI LEMON SQUEEZY ISPLATU (korak po korak)

### DA LI PIŠEŠ LEMON-U? → NE.
Aktivacija isplate je **self-serve** — sve radiš sam u **Settings → Payout**. Ne moraš da pišeš podršci.
Podršci pišeš **samo ako** Srbija ne može da se izabere ili nešto pukne.

### Bitne činjenice (potvrđeno iz Lemon dokumentacije, jul 2026)
- Isplata ide na **PayPal** ili **bankovni račun**. Za Srbiju je najsigurniji **PayPal** (Lemon podržava PayPal isplate u 200+ zemalja; bankovne u ~79). PayPal u Srbiji prima novac i povlačiš ga na Visa/Master karticu.
- **Isplate idu 2x mesečno**, 1. i 15. u mesecu, i obuhvataju sve prodaje od prethodne isplate.
- **Lemon ne naplaćuje naknadu za isplatu** (apsorbuje troškove).
- Postoji **minimalni prag za isplatu** — ako ne skupiš dovoljno, prebacuje se u sledeći ciklus dok ne pređe prag.
- **Isplata je zaključana dok ne popuniš poresku formu.**

### Koraci (redom)
1. **Uloguj se u Lemon Squeezy** → **Settings → Payout**
2. **Izaberi payout metod** → **PayPal** (unesi PayPal email). Proveri da je Srbija izabrana kao zemlja.
3. **Popuni poresku formu (obavezno):** kao osoba van SAD to je **W-8** (utvrđuje da nisi iz US-a). Link na formu je baš u Payout sekciji. Bez ovoga isplata ostaje isključena.
4. **Store podaci** — naziv, logo, valuta
5. **Proizvod + dve varijante** (ako već nisu live):
   - kraći plan: **600 RSD, 5 dana**
   - duži plan: **1200 RSD, 30 dana**
   - (cena i trajanje se podešavaju OVDE, u Lemon-u, ne u kodu)
6. **Test mod** — proveri ceo tok pre pravog novca
7. Kad je PayPal povezan i W-8 popunjen → isplate kreću automatski (1./15.) čim pređeš prag

> Ako na ekranu ne vidiš baš ovako — reci mi šta vidiš pa te provedem korak po korak.

---

## 4. POREZ: GDE I KAKO DA PITAM / PRIJAVIM (frilenser model)

Kad ti Lemon isplati novac, taj priliv iz inostranstva prijavljuješ sam. To je **samooporezivanje frilensera.**

### Gde se prijavljuje
- Poreska uprava Srbije ima **poseban portal za frilensere** (portal za samooporezivanje prihoda iz inostranstva)
- Prijava se podnosi **po kvartalu**, na prihod koji si stvarno primio: Q1 do 30. aprila, Q2 do 30. jula, itd.
- **Biraš model za svaki kvartal posebno** (možeš menjati)

### Aktuelne brojke za 2026 (potvrđeno)
- **Model A** — normirani troškovi (odbitak) **110.647 RSD po kvartalu**; porez 20% na osnovicu (prihod − odbitak); doprinosi PIO 24% + zdravstveno 10,3% na osnovicu.
  - 👉 **Ako u kvartalu zaradiš manje od 110.647 RSD, osnovica je 0 → ne plaćaš porez ni doprinose.**
  - Najbolji za **start / nizak / neredovan prihod** — tačno tvoj slučaj.
- **Model B** — neoporezivo **96.000 RSD po kvartalu** (32.000/mesec) + dodatni procentualni odbitak; niža poreska stopa 10%.
  - Isplati se tek kad prihodi postanu **veći i redovni**.

> Za tebe na startu = **Model A**. Dok si ispod ~110.000 RSD po kvartalu, praktično **ne plaćaš ništa**.
> Napomena: pošto si zaposlen, oko zdravstvenog doprinosa proveri sa knjigovođom (može biti drugačije jer si već osiguran preko posla).

### Kome i šta tačno da pitaš
Najlakše i najjeftinije: **knjigovođa/agencija specijalizovana za frilensere** (rade to rutinski za mali mesečni ili po-prijavi iznos). Pitanja koja poneseš:

1. „Primam prihod iz inostranstva preko Lemon Squeezy (SaaS pretplate). Da li to mogu da prijavljujem kao **frilenser samooporezivanje**, ili moram odmah da otvorim preduzetnika?"
2. „Koji je **neoporezivi prag po kvartalu** i koja je stopa na ostatak za 2026?"
3. „Pošto sam **zaposlen u drugoj firmi**, da li plaćam zdravstveni doprinos ili ne?"
4. „Kako da **evidentiram priliv preko PayPal/Wise** i šta mi treba za devizni priliv?"
5. „Na kojoj mesečnoj/godišnjoj zaradi mi se **više isplati da pređem na paušal**?"

### Alternativa
- Info centar Poreske uprave (telefon/šalter) — za osnovna pitanja besplatno
- Ali za tvoj slučaj (inostranstvo + zaposlen) knjigovođa je brži i sigurniji

---

## 5. KAD PREĆI NA FIRMU (paušal)

| Situacija | Bolji režim |
|---|---|
| Malo / nesigurno prihoda (start) | **Frilenser / samooporezivanje** — plaćaš po zaradi |
| Stabilan prihod koji redovno prelazi trošak paušala | **Preduzetnik paušalac** — fiksno postane jeftinije |

Pravilo: dok je frilenser porez (procenat na stварnu zaradu) **manji** od fiksnog paušala — ostaješ frilenser.
Kad te procenat redovno košta više od paušala — otvaraš paušal. Tada koristiš pun plan iz [REALIZACIJA_BILLING.md](REALIZACIJA_BILLING.md).

---

## 6. NA ŠTA DA PAZIŠ (iskreno)

- Poreska voli da **redovna, sistematska delatnost** bude registrovana firma. Za start i validaciju tržišta frilenser model je uobičajen i odbranjiv; kad krene redovno → pređi na paušal da budeš potpuno čist.
- **Potvrdi klasifikaciju** prihoda kod knjigovođe (SaaS preko Lemon-a kao frilenser prihod) — to je kratak razgovor.
- Čuvaj evidenciju svih Lemon isplata (izveštaji iz Lemon dashboarda) za poresku prijavu.

---

## 7. TVOJ SLEDEĆI POTEZ (redom)

1. [ ] U Lemon Squeezy poveži **payout metod** (PayPal/Wise) i popuni **tax formu (W-8BEN tip)**
2. [ ] Napravi/potvrdi **dve varijante** (600 RSD/5 dana, 1200 RSD/30 dana)
3. [ ] Uradi **test kupovinu** u test modu
4. [ ] Kratko pitaj **knjigovođu za frilensere** (pitanja iz sekcije 4)
5. [ ] Kad je payout spreman → dogovorimo **prelazak na live** (env na hostu iz punog plana)

> Kod i aplikacija su spremni. Ovo je čisto operativni, jeftin start bez firme.

---

## 8. PRIPREMA PRE POVEZIVANJA NA LEMON (čeklist)

Spremi ovo pre nego što uđeš u Lemon → Payout:

**PayPal**
- [ ] otvoren PayPal nalog (Business preporuka; Personal može za start)
- [ ] povezana i verifikovana Visa/Mastercard kartica u tvoje ime

**Podaci za W-8 poresku formu**
- [ ] puno ime i prezime (kao u ličnoj)
- [ ] adresa prebivališta
- [ ] datum rođenja
- [ ] poreski broj (TIN) = **JMBG**

**Identifikacija (KYC)**
- [ ] lična karta ili pasoš (za verifikaciju identiteta ako Lemon zatraži)

**Banka (za karticu)**
- [ ] kartica omogućena za **plaćanje na internetu** i **devizne (inostrane) transakcije**
- [ ] kartica podržava **primanje** novca sa PayPal-a (Visa Direct / Mastercard MoneySend)
- [ ] proverene naknade i kurs pri prilivu iz inostranstva

---

## 9. PAYPAL — DETALJNO (ko otvara, koja kartica, banka)

### Ko otvara i gde
- **PayPal NIJE banka i NIJE vezan za tvoju banku.** To je zasebna internacionalna firma.
- **Ti sam otvaraš nalog online na `paypal.com`** — besplatno, za ~10 minuta. **Ne ideš u banku za ovo.**
- Srbija je podržana za primanje i slanje novca.

### Koji nalog
- **Business** — ispravnije za prihod, veći limiti (preporuka)
- **Personal** — može za sam start
- (možeš kasnije nadograditi Personal u Business)

### Koju karticu povezuješ
- Bilo koju **Visa ili Mastercard** iz bilo koje srpske banke (debitna je dovoljna, ne mora kreditna)
- PayPal je verifikuje malim privremenim iznosom + kodom
- Novac se u Srbiji **povlači NA karticu** (ne na bankovni račun)

### Da li ista kartica na koju primam platu?
- **Tehnički DA** — može ista kartica.
- **ALI preporuka: zasebna kartica/račun** za poslovni priliv, da ti frilenser prijava bude čista i lako se prati šta je od aplikacije. Ako nemaš drugu — ista radi.

### Šta kartica MORA da ispunjava
1. omogućene **internet i devizne transakcije** (da bi se uopšte povezala i verifikovala)
2. da podržava **primanje** novca (Visa Direct / Mastercard MoneySend) — jer PayPal isplaćuje na karticu

### Kako novac stiže
```
Lemon isplati (USD)  →  PayPal balans  →  "Withdraw to card"  →  stigne na karticu u dinarima (par dana)
```
- Postoji mali **kursni trošak** (USD→RSD konverzija) i eventualno mala naknada za povlačenje ispod nekog iznosa.

### Da li i s kim da se konsultujem u banci
- **Za PayPal: NE treba banka** — otvaraš ga sam online.
- **Za karticu: pozovi info liniju banke ili odi u ekspozituru** i pitaj **službu za kartično poslovanje** (nije ti potreban lични „bankar/savetnik"):
  1. „Da li mi je kartica omogućena za plaćanje na internetu i devizne transakcije?"
  2. „Da li kartica može da **prima** uplate sa PayPal-a (Visa Direct / Mastercard MoneySend)?"
  3. „Kolike su naknade i kurs pri prilivu iz inostranstva?"

> Najčešći jedini problem: banka drži karticu isključenu za internet/inostranstvo. Ako je uključe — sve radi.

---

## 10. REDOSLED KORAKA (od nule do prve isplate)

1. [ ] **Otvori PayPal nalog** na `paypal.com` (Business preporuka) — sam, online, besplatno
2. [ ] **Poveži karticu** (Visa/Mastercard u tvoje ime) i **verifikuj** je
3. [ ] **Pozovi/poseti banku** — službu za kartično poslovanje, proveri 3 stvari:
   - kartica omogućena za internet + devizne transakcije
   - kartica prima uplate sa PayPal-a (Visa Direct / Mastercard MoneySend)
   - naknade i kurs pri prilivu iz inostranstva
4. [ ] **Spremi podatke za W-8** (JMBG, adresa, datum rođenja, puno ime)
5. [ ] **Uđi u Lemon → Settings → Payout**, izaberi **PayPal**, popuni **W-8**
6. [ ] Potvrdi **dve varijante** (600 RSD/5 dana, 1200 RSD/30 dana)
7. [ ] **Test kupovina** u test modu
8. [ ] Kratko pitaj **knjigovođu za frilensere** (Model A, pitanja iz sekcije 4)
9. [ ] Kad je payout spreman → dogovorimo **prelazak na live** (env na hostu iz punog plana)

> Napomena: za otvaranje PayPal-a NE treba banka ni bankar. Banku zoveš samo da potvrdiš da je kartica
> otvorena za internet/inostranstvo i da može da prima novac. To je jedini čest problem.
