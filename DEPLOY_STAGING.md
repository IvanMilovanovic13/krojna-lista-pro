# Deploy Staging

Ovaj fajl opisuje najkraci staging put za `krojna_lista_pro`.

## 1. Priprema env vrednosti

Minimalno pripremi:

```env
APP_ENV=staging
BASE_URL=https://staging.tvoj-domen.rs
SECRET_KEY=change-me-in-staging
DATABASE_URL=postgresql://user:pass@host:5432/dbname
LEMON_SQUEEZY_API_KEY=api_key...
LEMON_SQUEEZY_WEBHOOK_SECRET=webhook_secret...
LEMON_SQUEEZY_STORE_ID=12345
LEMON_SQUEEZY_STORE_SUBDOMAIN=your-store
LEMON_SQUEEZY_VARIANT_ID_WEEKLY=123456
LEMON_SQUEEZY_VARIANT_ID_MONTHLY=123456
LEMON_SQUEEZY_CHECKOUT_SUCCESS_URL=https://staging.tvoj-domen.rs/login?checkout=success
HOST=0.0.0.0
PORT=8080
WEB_WORKERS=2
EXPORT_WORKER_MODE=in_process
```

Preporuka:

- kopiraj `.env.staging.example` u `.env.staging`
- zatim dopuni stvarne staging vrednosti
- lokalni loader sada podrzava:
  - `.env`
  - `.env.local`
  - `.env.staging`
  - `.env.staging.local`
- staging env fajlovi imaju prednost nad baznim `.env` vrednostima, ali ne pregaze eksplicitne sistemske env varijable
- za lokalni staging start koristi:
  - `RUN_STAGING.ps1`
- za readiness koristi:
  - `RUN_READINESS.ps1 staging`
- placeholder vrednosti iz `.env.staging.example` ne racunaju se kao stvarno spremna Lemon Squeezy konfiguracija

## 2. Start preko Docker Compose

```powershell
docker compose -f .\docker-compose.staging.yml up --build
```

## 3. Health check

```text
http://localhost:8080/healthz
http://localhost:8080/readyz
```

## 4. Sta staging sada pokriva

- app start
- Postgres runtime
- auth/session tok
- billing service sloj
- Lemon Squeezy config readiness
- webhook endpoint

## 5. Readiness cilj za staging

Kada je staging env dobro popunjen, sledeca komanda treba da vrati `0 blockers`:

```powershell
powershell -ExecutionPolicy Bypass -File .\RUN_READINESS.ps1 staging
```

To znaci:

- nije dovoljno samo kopirati example fajl
- moraju postojati stvarne Lemon Squeezy vrednosti, ne `api_key...`, `webhook_secret...`, `12345`, `123456`

## 6. Sta jos nije finalna produkcija

- pravi Postgres server runtime test
- reverse proxy i HTTPS
- domen
- monitoring i alerting
- backup/restore procedura
- finalni Lemon Squeezy kljucevi i variant ID-jevi
