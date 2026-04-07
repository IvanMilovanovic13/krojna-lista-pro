# Production Config

Ovaj projekat trenutno radi lokalno preko `SQLite`, ali je pripremljen za sledeci korak ka serveru i internet produkciji.

## Obavezne env varijable

- `APP_ENV`
- `BASE_URL`
- `HOST`
- `PORT`
- `WEB_WORKERS`
- `EXPORT_WORKER_MODE`
- `EXPORT_WORKER_POLL_SECONDS`
- `SECRET_KEY`
- `DATABASE_URL`
- `LEMON_SQUEEZY_API_KEY`
- `LEMON_SQUEEZY_WEBHOOK_SECRET`
- `LEMON_SQUEEZY_STORE_ID`
- `LEMON_SQUEEZY_STORE_SUBDOMAIN`
- `LEMON_SQUEEZY_VARIANT_ID_WEEKLY`
- `LEMON_SQUEEZY_VARIANT_ID_MONTHLY`
- `LEMON_SQUEEZY_CHECKOUT_SUCCESS_URL`

App sada automatski ucitava:

- `.env`
- `.env.local`
- `.env.<APP_ENV>`
- `.env.<APP_ENV>.local`

Ako je vrednost vec postavljena u sistemskim env varijablama, ona ima prioritet.

Primer:

```env
APP_ENV=development
BASE_URL=http://localhost:8080
HOST=127.0.0.1
PORT=8080
WEB_WORKERS=0
EXPORT_WORKER_MODE=in_process
EXPORT_WORKER_POLL_SECONDS=2
SECRET_KEY=change-me-in-production
DATABASE_URL=sqlite:///C:/Users/Korisnik/krojna_lista_pro/data/project_store.db
LEMON_SQUEEZY_API_KEY=
LEMON_SQUEEZY_WEBHOOK_SECRET=
LEMON_SQUEEZY_STORE_ID=
LEMON_SQUEEZY_STORE_SUBDOMAIN=
LEMON_SQUEEZY_VARIANT_ID_WEEKLY=
LEMON_SQUEEZY_VARIANT_ID_MONTHLY=
LEMON_SQUEEZY_CHECKOUT_SUCCESS_URL=http://localhost:8080/nalog?checkout=success
```

## Trenutno podrzano

- `sqlite:///...` radi
- `postgres://...` i `postgresql://...` se prepoznaju i imaju kompatibilan store adapter
- Lemon Squeezy checkout / portal mogu da se pripreme ako su kljucevi i variant ID-jevi postavljeni
- export worker moze da radi kao `in_process` ili `dedicated_process`

## Provera config-a

```powershell
python .\app_config_cli.py
```

## Provera store runtime-a

```powershell
python .\project_store_cli.py runtime
```

## Provera server spremnosti

Za sirovi runtime status:

```powershell
python .\ops_diagnostics_cli.py
```

Za staging readiness:

```powershell
python .\ops_diagnostics_cli.py --readiness --target staging
```

Za production readiness:

```powershell
python .\ops_diagnostics_cli.py --readiness --target production
```

API endpointi:

- `/healthz`
- `/readyz`
- `/ops/runtime`
- `/ops/readiness?target=production`

## Maintenance cleanup

Za ciscenje isteklih sesija, reset tokena i starih login attempt zapisa:

```powershell
python .\maintenance_cli.py
```

Za staging/production preporuka je:

- `HOST=0.0.0.0`
- `PORT=8080`
- `WEB_WORKERS=2` za pocetak
- `EXPORT_WORKER_MODE=dedicated_process`
- `EXPORT_WORKER_POLL_SECONDS=2`

To nije finalni scaling sloj, ali je prvi obavezni korak da app ne ostane zakucan
na development start konfiguraciji.

## Export worker

Za izdvojeni export worker:

```powershell
python .\export_worker_cli.py
```

Za jednokratnu obradu jednog job-a:

```powershell
python .\export_worker_cli.py --once
```

## Postgres migracioni koraci

Izvezi trenutni SQLite store:

```powershell
python .\project_store_cli.py export --out .\data\project_store_snapshot.json
```

Prikazi Postgres schema SQL:

```powershell
python .\project_store_cli.py postgres-schema
```

Importuj snapshot u Postgres kada `DATABASE_URL` pokazuje na Postgres i kada je `psycopg` dostupan:

```powershell
python .\project_store_cli.py postgres-import --snapshot .\data\project_store_snapshot.json --database-url "postgresql://..."
```
