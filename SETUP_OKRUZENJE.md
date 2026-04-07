# Setup Okruzenje

## Preporuka

- preporuceni Python za projekat: `3.13`
- lokalno pokretanje: projektni `venv`
- komanda za start: `RUN_KITCHEN.ps1`

## Prvo postavljanje

U PowerShell-u:

```powershell
cd C:\Users\Korisnik\krojna_lista_pro
powershell -ExecutionPolicy Bypass -File .\SETUP_VENV.ps1
```

Ovo radi:

- pronalazi dostupan Python
- preferira `Python 3.13`
- pravi `venv`
- instalira pakete iz `requirements.txt`

## Pokretanje aplikacije

```powershell
cd C:\Users\Korisnik\krojna_lista_pro
powershell -ExecutionPolicy Bypass -File .\RUN_KITCHEN.ps1
```

Alternativno:

```powershell
venv\Scripts\python.exe app.py
```

## Readiness i ops provera

Za readiness i runtime dijagnostiku koristi projektni `venv`, ne sistemski Python.

Preporucena komanda:

```powershell
powershell -ExecutionPolicy Bypass -File .\RUN_READINESS.ps1 staging
```

ili:

```powershell
powershell -ExecutionPolicy Bypass -File .\RUN_READINESS.ps1 production
```

Alternativno direktno:

```powershell
venv\Scripts\python.exe ops_diagnostics_cli.py --readiness --target staging
venv\Scripts\python.exe ops_diagnostics_cli.py --readiness --target production
```

Napomena:

- ako se `ops_diagnostics_cli.py` pokrene preko pogresnog Python interpretera, Postgres readiness moze lazno izgledati kao da nije spreman
- u ovom projektu je `psycopg` instaliran u projektnom `venv`
- zato za app, testove i ops komande koristi projektni `venv`

## Napomena za Python 3.14

NiceGUI zavisnost `vbuild` koristi stariji API (`pkgutil.find_loader`).
Zato projekat u [app.py](/C:/Users/Korisnik/krojna_lista_pro/app.py) ima compatibility shim pre `nicegui` importa.

To znaci:

- normalno pokretanje aplikacije radi iz repoa
- ipak je preporuceni produkcioni target i dalje `Python 3.13`
