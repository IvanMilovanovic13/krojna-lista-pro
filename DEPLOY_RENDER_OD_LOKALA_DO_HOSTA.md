# Deploy na Render - od lokalnog racunara do hosta

Ovaj dokument je praktican vodic kako da izmenu koju si proverio lokalno pustis na host.

Vodic je pisan za trenutni projekat:

- repo: `IvanMilovanovic13/krojna-lista-pro`
- remote: `origin`
- aktivna deploy grana: `master`
- hosting: `Render`

Ako u buducnosti promenis granu ili hosting model, azuriraj ovaj dokument pre sledeceg deploy-a.

---

## 1. Sta treba da bude tacno pre deploy-a

Pre nego sto krenes na host, proveri:

1. izmena radi lokalno
2. nema sintaksne greske
3. znas koje fajlove hoces da pustis
4. ne gurash lokalne pomocne fajlove koji ne treba da idu na repo

Tipicni fajlovi koje ne treba gurati:

- `.claude/settings.local.json`
- lokalni preview fajlovi tipa `logo_preview.html`
- privatni `.env` fajlovi i tajne vrednosti

---

## 2. Lokalna provera pre Git push-a

Otvori PowerShell u root folderu projekta:

```powershell
cd C:\Users\Korisnik\krojna_lista_pro
```

Ako venv jos nije spreman:

```powershell
powershell -ExecutionPolicy Bypass -File .\SETUP_VENV.ps1
```

Po potrebi pokreni lokalni app:

```powershell
powershell -ExecutionPolicy Bypass -File .\RUN_KITCHEN.ps1
```

Za host-like staging proveru lokalno:

```powershell
powershell -ExecutionPolicy Bypass -File .\RUN_STAGING.ps1
powershell -ExecutionPolicy Bypass -File .\RUN_READINESS.ps1 staging
```

Preporuceni minimalni sanity check:

```powershell
python -m py_compile ui_panels.py ui_main_content.py ui_settings_tab.py
python test_i18n.py
python smoke_scenarios.py
```

Ako to prolazi i rucni UI test je dobar, idi na Git korak.

---

## 3. Proveri sta je menjano

Pogledaj status:

```powershell
git status --short
```

Pogledaj diff:

```powershell
git diff --stat
```

Ako vidis lokalne fajlove koji ne treba da idu na host, nemoj ih stage-ovati.

---

## 4. Stage samo ono sto treba da ide na host

Primer:

```powershell
git add ui_panels.py ui_main_content.py ui_settings_tab.py ROADMAP_DO_100.md MASTER_PROJEKAT.md
```

Ako imas vise projektnih fajlova, navedi ih sve eksplicitno.

Posle toga proveri staged set:

```powershell
git diff --cached --name-only
git diff --cached --stat
```

Ako je staged set dobar, idi na commit.

---

## 5. Napravi commit

Primer:

```powershell
git commit -m "Restore settings tab and finalize staging polish"
```

Posle toga proveri:

```powershell
git log --oneline --decorate -3
```

Zapamti poslednji commit hash. On ti treba da proveris da li je isti patch stigao na host.

---

## 6. Push na GitHub

Za ovaj projekat koristi se `master`, ne `main`.

Push:

```powershell
git push origin master
```

Posle toga proveri:

```powershell
git log --oneline --decorate -1
```

Treba da vidis da `HEAD -> master` i `origin/master` pokazuju na isti commit.

Ako push nije uspeo, ne idi dalje na Render dok to ne resis.

---

## 7. Sta znaci "izmena je stigla do hosta"

`git push` sam po sebi ne znaci da je host vec azuriran.

To znaci samo:

- izmena je stigla na GitHub
- Render sada moze da je povuce

Da bi izmena bila stvarno na hostu, Render mora:

- da prati pravu granu
- da povuce najnoviji commit
- da uspe da ga izgradi i podigne

---

## 8. Idi na Render - ali na postojeci service

Otvori:

- [https://dashboard.render.com](https://dashboard.render.com)

Vrlo vazno:

- ako vec imas staging service, ne idi na `New Web Service`
- treba da otvoris postojeci staging service

Ispravan put:

1. otvori workspace
2. otvori listu servisa
3. klikni postojeci staging web service za ovaj projekat

Tek kada si usao u postojeci service, prelazis na deploy proveru.

---

## 9. Proveri branch na Render-u

U okviru postojeceg service-a idi na:

- `Settings`
- ili `Build & Deploy`

Proveri koja je branch podesena.

Za ovaj projekat treba da bude:

```text
master
```

Ako tamo pise:

```text
main
```

onda Render nece povuci nas najnoviji patch sa `master`.

Ako branch nije dobra:

1. promeni branch na `master`
2. sacuvaj promenu

---

## 10. Manual deploy na Render-u

Kada je branch dobra, idi na:

- `Events`
- ili `Deploys`

Zatim:

1. klikni `Manual Deploy`
2. klikni `Deploy latest commit`

Sacekaj da deploy zavrsi.

Ne zatvaraj proveru pre nego sto status bude nesto tipa:

- `Live`
- `Deploy successful`
- `Active`

Ako deploy padne:

1. otvori `Logs`
2. procitaj build gresku
3. vrati se lokalno, popravi, pa ponovi Git + Render tok

---

## 11. Kako da proveris da li je Render stvarno povukao bas tvoj patch

U poslednjem deploy-u proveri:

1. branch
2. commit hash
3. commit message

To treba da se poklapa sa tvojim poslednjim lokalnim push-om.

Primer provere:

- lokalno si push-ovao commit `745518a`
- na Render deploy-u takodje mora da pise `745518a`

Ako na Render-u pise stariji commit:

- host jos nije pokupio novu izmenu
- ili branch nije dobra
- ili nije pokrenut novi deploy

---

## 12. Tehnicka provera posle deploy-a

Kada deploy prodje, otvori staging URL i health endpoint-e.

Primer:

```text
https://staging.cabinetcutpro.com/healthz
https://staging.cabinetcutpro.com/readyz
https://staging.cabinetcutpro.com/ops/readiness?target=staging
```

Proveri:

- da app odgovara
- da readiness ne vraca blocker za staging
- da ne gledas star deploy

---

## 13. Funkcionalna provera posle deploy-a

Posle tehnickog health check-a obavezno proveri i sam UI.

Primer redosleda:

1. otvori staging sajt
2. proveri da li se vidi konkretna izmena koju si pustio
3. klikni kroz osnovni korisnicki tok
4. proveri da ne postoji regresija

Ako si pustio UI izmenu, proveri bas taj ekran.

Na primer za vracanje `Podešavanja` taba:

1. toolbar mora da prikazuje `Podešavanja`
2. klik na `Podešavanja` mora da otvori pravi settings ekran
3. ne sme da radi redirect na `Wizard`
4. mora da se vide:
   - materijali
   - debljine
   - boja fronta
   - dubine zona
   - worktop pravila

---

## 14. Ako auto deploy postoji

Ako je Render service podesen na auto-deploy sa `master`, onda cesto nije potreban rucni klik na deploy.

I dalje uradi proveru:

1. da li je deploy zaista krenuo
2. da li je povukao pravi commit
3. da li je deploy prosao

Nikad nemoj pretpostaviti da je host azuran samo zato sto je push na GitHub uspeo.

---

## 15. Najcesce greske

### Greska 1: gledas `New Web Service`

To nije postojeci host.
Ako vec imas staging service, treba da otvoris bas njega.

### Greska 2: Render prati `main`, a repo se gura na `master`

To znaci:

- GitHub ima novu izmenu
- Render je ne vidi

Resenje:

- podesi branch na `master`

### Greska 3: push-ovan je i lokalni smeće fajl

Primer:

- `.claude/settings.local.json`
- preview fajlovi

Resenje:

- stage-uj samo konkretne projektne fajlove

### Greska 4: proveravas sajt, ali ne i commit na Render-u

Mozes gledati stari deploy i misliti da novi patch ne radi.

Resenje:

- prvo proveri commit hash na Render-u

### Greska 5: deploy je prosao, ali nije proverena funkcionalnost

Deploy bez UI provere nije dovoljan.

Resenje:

- obavezno uradi health check i funkcionalni smoke

---

## 16. Najkraci prakticni tok

Ako hoces ultra-kratku verziju:

1. lokalno proveri izmenu
2. `git status --short`
3. `git add ...`
4. `git commit -m "..."`
5. `git push origin master`
6. otvori postojeci Render staging service
7. proveri da branch pise `master`
8. `Manual Deploy -> Deploy latest commit`
9. proveri da Render prikazuje isti commit hash koji si push-ovao
10. proveri `/healthz`, `/readyz`, `/ops/readiness`
11. proveri UI na staging sajtu

---

## 17. Kratak checklist za svaku sledecu izmenu

Pre deploy-a:

- lokalno radi
- sanity check prosao
- staged su samo pravi fajlovi
- commit je napravljen
- push na `origin/master` je uspeo

Na Render-u:

- otvoren je postojeci service
- branch je `master`
- deploy je povukao pravi commit
- deploy je prosao

Posle deploy-a:

- `healthz` radi
- `readyz` radi
- readiness nema blocker
- UI promena je stvarno vidljiva na hostu

---

## 18. Komande na jednom mestu

```powershell
cd C:\Users\Korisnik\krojna_lista_pro
git status --short
git diff --stat
git add <fajl1> <fajl2> <fajl3>
git diff --cached --name-only
git commit -m "opis izmene"
git push origin master
```

Lokalna staging provera:

```powershell
powershell -ExecutionPolicy Bypass -File .\RUN_STAGING.ps1
powershell -ExecutionPolicy Bypass -File .\RUN_READINESS.ps1 staging
```

---

Ako se hosting model promeni sa Render-a na nesto drugo, napravi novu verziju ovog dokumenta umesto da menjas nasumicno stare korake.
