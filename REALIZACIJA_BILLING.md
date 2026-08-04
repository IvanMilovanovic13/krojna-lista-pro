# REALIZACIJA PROJEKTA — BILLING (naplata i puštanje u rad)

**Datum:** 23. jul 2026.
**Cilj dokumenta:** Jasno i precizno pokazati gde smo, šta je već urađeno i koje tačne korake TI moraš da uradiš da bi aplikacija bila puštena u rad i počela da se naplaćuje — i da radi sve kako treba.

---

## 1. KRAJNJI CILJ (šta znači "gotovo")

Krajnji rezultat koji hoćemo:

- korisnik dođe na pravi domen (npr. `cabinetcutpro.com`)
- napravi nalog, potvrdi email
- izabere plan i **plati pravom karticom**
- posle uplate mu se nalog automatski otključa (PRO pristup)
- može da napravi kuhinju, otvori krojnu listu i preuzme PDF / Excel / CSV
- kad plan istekne, pristup se sam zaključa dok ponovo ne plati
- ti kao vlasnik dobijaš novac na račun firme preko Lemon Squeezy isplate

Kad sve ovo radi na pravom domenu sa pravim novcem — projekat je **pušten u rad**.

---

## 2. GDE SMO SADA (faza)

Projekat je u fazi: **KASNA BETA / PRODUKCIONO OJAČAVANJE.**

To znači: aplikacija i naplata su **napravljeni i testirani lokalno i na stagingu**.
Ostaje **operativni završni korak** — firma, pravi ključevi, pravi domen, pa test pravom uplatom.

> Nije "treba da napravimo naplatu". Naplata je napravljena. Treba je **aktivirati u živom modu.**

Vizuelno:

```
[✅ Napravljeno]  →  [⬜ Firma + live ključevi]  →  [⬜ Deploy na pravi domen]  →  [⬜ Test pravom uplatom]  →  [🎯 U RADU]
     ~90%                  ti radiš                      ti + ja                       ti + ja
```

---

## 3. ŠTA JE VEĆ URAĐENO (ne diramo, radi)

| Oblast | Stanje |
|---|---|
| Nalozi (registracija, login, verifikacija emaila, reset lozinke) | ✅ radi |
| 3 admin naloga + 5 test naloga (model) | ✅ postoji |
| Baza po korisniku (PostgreSQL), svako vidi samo svoje projekte | ✅ radi, zaključano testovima |
| Naplata preko Lemon Squeezy (checkout, webhook, customer portal) | ✅ napravljeno |
| Paywall: Free trial → `PRO 7 dana` / `PRO 1 mesec` | ✅ radi |
| Bez PRO pristupa nema krojne liste ni PDF/Excel/CSV | ✅ radi |
| Zaštićen download (proverava nalog + vlasništvo + plaćen pristup) | ✅ radi |
| Email slanje (Resend, `auth.cabinetcutpro.com`) | ✅ konfigurisano |
| Pravne stranice `/privacy` i `/terms` | ✅ postoje |
| Staging uživo (`staging.cabinetcutpro.com`, HTTPS, Postgres) | ✅ podignut |
| Automatski testovi | ✅ 188/188 prolazi |
| Health / ops / readiness endpointi | ✅ postoje |
| Docker + Render deploy konfiguracija | ✅ postoji |

**Zaključak:** kod je spreman. Naplata je spremna. Fali samo aktivacija u živom modu.

---

## 2.5 AŽURIRANA AGENDA — SLEDEĆI KORACI (04.08.2026)

> Ovo je trenutno važeći redosled rada, dogovoren 04.08.2026. Zamenjuje raniji redosled iz sekcije 6 tamo gde se razlikuju (npr. Korak 1 "firma" — videti napomenu u sekciji 6).

**Faza A — Housekeeping (kod)**
- [x] Commit necomitovanih izmena (popunjen QA smoke test rezultati, sitne config izmene) — urađeno 04.08.2026

**Faza B — Zatvoriti Lemon store**
- [x] Proveriti u Lemon dashboardu zašto piše "store not activated" — **NALAZ (04.08.2026 uveče):** Settings → General → "Store activation" nema dugme za klik; "Identity verification" status = **"In Review"**. Store se ne može aktivirati dok Lemon ne završi pregled identiteta — nije nešto što se sad klikne, čeka se njihov odgovor.
- [x] Proveriti email za Lemon poruku sa zahtevom za dodatne info — **POTVRĐENO 04.08.2026 uveče:** Lemon je tražio ("Your application has been received") primere proizvoda/demo i website URL; Ivan je već odgovorio sa punim opisom proizvoda + staging URL-om (`staging.cabinetcutpro.com`) + pozivom da naprave free nalog. Ovaj korak je zatvoren — dalje se samo čeka njihov review, ništa više da se radi sa naše strane.
- [ ] Dodati `cover_en` sliku u Lemon Media
- [ ] Kad "Identity verification" pređe iz "In Review" u odobreno → store se aktivira (proveriti da li treba dodatni klik ili je automatsko)

**Faza C — Poslednji test u Test modu**
- [x] Test kupovina na stagingu test karticom kroz ceo tok — urađeno 04-05.08.2026. **Usput otkriveno i ispravljeno (5 commit-a, sve push-ovano na staging):**
  1. Webhook je čitao `custom_data` sa pogrešnog mesta (`data.attributes` umesto pravog `meta.custom_data`) → uplata se pripisivala pogrešnom nalogu (Lemon-ovom `attributes.user_email`, ne ulogovanom app nalogu). **Ovo je bio glavni bag i sad je ispravljen.**
  2. Billing webhook je mogao tiho da skine admin nalog na paid/trial tier — dodata zaštita.
  3. Event ID za idempotenciju/audit log se čitao sa pogrešnog mesta (`meta.webhook_id`, ne top-level `id`) — ispravljeno.
  4. Trial: 7 → 10 dana, aktivira se automatski (bez klika) pri prvom loginu, toast obaveštenje + odbrojavanje u toolbaru.
  5. Bag u računanju dana triala zbog odsečenog timezone offseta (10 dana se prikazivalo kao 9 ili 11 zavisno od servera) — ispravljeno.
  Sve potvrđeno uživo na stagingu: test kupovina ispravno otključava nalog, trial radi i pokazuje tačan broj dana.
- [ ] Ponovo proveriti E1-E3 (customer portal) iz QA dokumenta — i dalje čeka aktivaciju Lemon store-a (Faza B)

**Faza D — Test → Live u Lemonu**
- [ ] Prebaciti Lemon store iz Test u Live mod (korisnik, u Lemon dashboardu)
- [ ] Uzeti LIVE Lemon API ključeve

**Faza E — Produkcioni env**
- [ ] Na Render-u: `APP_ENV=production`, HTTPS BASE_URL na pravom domenu, nov produkcioni `SECRET_KEY`, live Lemon ključevi
- [ ] Proveriti da pravi domen (cabinetcutpro.com) pokazuje na Render produkcioni servis

**Faza F — E2E sa pravim novcem**
- [ ] Jedna prava uplata malim iznosom na produkciji, potvrditi ceo lanac (naplata → webhook → unlock → PayPal payout)
- [ ] Provera da payout stvarno stigne na PayPal/karticu

**Faza G — Puštanje**
- [ ] Formalno "live" — pratiti prvih par dana (ops/health endpointi već postoje)
- [ ] GDPR finiš (brisanje naloga / export podataka) — može i odmah posle starta ako nije hitno pravno

> Napomena o realnosti: Faze B, D, F imaju korake koje radi isključivo korisnik (Lemon dashboard, banka/PayPal, prava kartica) — Claude ne može da klikne "Activate store" niti da unosi finansijske/lične podatke.

---

## 4. ŠTA TAČNO FALI DO PRVE UPLATE

Readiness provera (`production`) trenutno prijavljuje **4 blokera** — ali su sva 4 samo **podešavanja na hostu**, ne greške u kodu:

| Bloker | Šta je sad | Šta treba |
|---|---|---|
| `APP_ENV` | `development` | `production` na hostu |
| `BASE_URL` HTTPS | `localhost` | pravi domen `https://cabinetcutpro.com` |
| `SECRET_KEY` | dev default | pravi produkcioni ključ |
| checkout success URL | localhost | uskladiti sa pravim domenom |

Lemon Squeezy ključevi (API, store, webhook, varijante) su **već konfigurisani** u okruženju.

> **Najvažnije razumeti:** checkout u kodu automatski ide u **test mod** dok `APP_ENV` nije `production`.
> Čim se na hostu postavi `APP_ENV=production` + live API ključ → naplata je prava. **Bez promene koda.**

---

## 5. CENE I PLANOVI (5 dana / 30 dana, 600 / 1200 din)

Ovo je važno da bude jasno:

- Aplikacija ima **tačno dva plaćena plana (dva slota):**
  - `pro_weekly`  → varijanta "weekly"  → ovo je tvoj **kraći plan (5 dana, 600 din)**
  - `pro_monthly` → varijanta "monthly" → ovo je tvoj **duži plan (30 dana, 1200 din)**
- **Cena i trajanje se NE podešavaju u kodu.** Podešavaju se u **Lemon Squeezy dashboardu**, na te dve varijante.
- Kod samo poziva varijantu po ID-ju (`LEMON_SQUEEZY_VARIANT_ID_WEEKLY` / `..._MONTHLY`). Koliko košta i koliko traje — određuje Lemon.
- Trajanje plaćenog pristupa se posle uplate vezuje za `renews_at` iz Lemon webhooka — automatski.

**Praktično za tebe:** u Lemon dashboardu postaviš dve cene (600 i 1200 din) i dva intervala (5 i 30 dana). Ništa u kodu se ne menja.

> ⚠️ Jedina sitnica koju ja treba da proverim: kod prepoznaje koji je plan po imenu varijante (traži reč "week"/"month" u imenu). Ako 5-dnevni plan nazoveš tako da ne sadrži "week", mapiranje treba blago doraditi. **To je moj zadatak — reci mi kad kreiraš varijante pa proverim.**

---

## 6. KORACI KOJE TI MORAŠ DA URADIŠ (redom)

### KORAK 1 — Firma / preduzetnik  ⚪ PREVAZIĐENO (zamenjeno freelancer modelom)
> **Ažurirano:** odlučeno je da se NE otvara firma odmah, nego se krene kao fizičko lice preko PayPal isplate (Stripe Express onboarding kao Individual, W-8 forma) — videti [START_NAPLATA_BEZ_FIRME.md](START_NAPLATA_BEZ_FIRME.md). Ovaj korak se preskače za sada; firma se otvara tek kad prihod redovno pređe trošak paušala. Trenutna aktivna agenda je u sekciji 2.5.

~~Lemon Squeezy isplaćuje novac samo na firmu/preduzetnika.~~
~~- [ ] Otvori preduzetničku radnju (paušal je najjednostavniji za početak)~~
~~- [ ] Pribavi PIB i tekući račun~~
~~- [ ] Pripremi podatke za Lemon Squeezy verifikaciju (naziv, adresa, račun)~~

### KORAK 2 — Aktiviraj Lemon Squeezy store (live mod)
- [ ] Uloguj se u Lemon Squeezy, unesi podatke firme, sačekaj verifikaciju store-a
- [ ] Napravi (ili prebaci u live) proizvod sa **dve varijante:**
  - kraći plan: **600 din, 5 dana**
  - duži plan: **1200 din, 30 dana**
- [ ] Prekopiraj **live** vrednosti: `API key`, `Store ID`, `Store subdomain`, `Webhook secret`, oba `Variant ID`
- [ ] Javi mi kad su varijante napravljene → proverim mapiranje plana (tačka iz sekcije 5)

### KORAK 3 — Domen
- [ ] Potvrdi da imaš `cabinetcutpro.com` (ili koji domen želiš) i pristup DNS-u
- [ ] Usmeri domen na Render produkcioni servis

### KORAK 4 — Produkcioni env na hostu (Render)
Ovo su ona 4 blokera iz sekcije 4. Postavljaju se kao env varijable na Render-u:
- [ ] `APP_ENV=production`
- [ ] `BASE_URL=https://cabinetcutpro.com`
- [ ] `SECRET_KEY=` (jak, novogenerisani ključ — ja ti dam komandu da ga napraviš)
- [ ] `LEMON_SQUEEZY_*` = **live** vrednosti iz Koraka 2
- [ ] `EMAIL_ENABLED=true` + Resend live ključ
- [ ] `DATABASE_URL` = produkcioni Postgres

> Pomoć: kad dođemo dovde, ja ti napravim tačnu listu "kopiraj-nalepi" env varijabli.

### KORAK 5 — Webhook u Lemon Squeezy
- [ ] U Lemon dashboardu podesi webhook URL: `https://cabinetcutpro.com/api/billing/webhook`
- [ ] Uključi evente: `subscription_created`, `subscription_updated`, `subscription_cancelled`, `order_created`, `order_refunded`
- [ ] `Signing secret` iz Lemon-a mora biti isti kao `LEMON_SQUEEZY_WEBHOOK_SECRET` na hostu

### KORAK 6 — Test pravom uplatom (E2E, zajedno)
- [ ] Napravi svež nalog na pravom domenu
- [ ] Potvrdi da stigne verifikacioni email i da link aktivira nalog
- [ ] Kupi kraći plan pravom karticom (može tvojom, pa refund)
- [ ] Potvrdi: posle uplate nalog pređe u PRO, krojna lista i PDF/Excel/CSV se otključaju
- [ ] Potvrdi: customer portal se otvara
- [ ] Potvrdi: kad plan istekne / otkažeš, pristup se zaključa

### KORAK 7 — GDPR finiš (pre prvih pravih korisnika)
- [ ] Potvrdi da postoji "Obriši nalog" i "Izvezi moje podatke" (proveravam u kodu)
- [ ] Cookie pristanak ako se koristi analytics
- [ ] Pročitaj `/privacy` i `/terms` da odgovaraju stvarnosti (firma, kontakt)

### KORAK 8 — Puštanje
- [ ] Pusti 3–5 pravih korisnika (stolari) kao zatvorenu betu
- [ ] Isprati prvi realan checkout i export
- [ ] Kad je stabilno → javno

---

## 7. ŠTA JA RADIM (moj deo)

- provera mapiranja plana kad napraviš varijante (sekcija 5)
- generisanje `SECRET_KEY` i tačna env lista za Render (Korak 4)
- provera da GDPR "Obriši nalog" / "Izvezi podatke" postoje i rade (Korak 7)
- podrška u E2E testu i troubleshooting ako nešto pukne (Korak 6)
- svaka doradа koda ako se u živom testu pojavi problem

---

## 8. KRITERIJUM "GOTOVO" (acceptance)

Projekat je pušten u rad kada je SVE ovo tačno na pravom domenu:

- [ ] `readiness (production)` = **0 blokera**
- [ ] nov korisnik se registruje i dobije pravi verifikacioni email
- [ ] plaćanje pravom karticom prolazi
- [ ] webhook otključa nalog automatski
- [ ] PRO korisnik preuzme PDF/Excel/CSV
- [ ] neplaćen korisnik NE može do exporta (ni direktnim linkom)
- [ ] istek plana ponovo zaključa pristup
- [ ] novac stigne na račun firme

---

## 9. NAJKRAĆI PUT (ako hoćeš jednu rečenicu)

> **Otvori firmu → aktiviraj Lemon store sa 2 cene → postavi 4 env varijable na host → testiraj jednom pravom uplatom → pusti.**

Sve ostalo je već napravljeno.
