# Deploy Production

Ovo je najkraci produkcioni put za `krojna_lista_pro` sa Docker + Nginx slojem.

## 1. Sta ovaj setup sada pokriva

- Python app u Docker kontejneru
- Nginx reverse proxy ispred aplikacije
- health check endpointi
- env/config sloj za Lemon Squeezy i bazu
- spreman put za domen i HTTPS

## 2. Sta jos moras imati pre pravog pustanja

- pravi `BASE_URL`
- jak `SECRET_KEY`
- pravi `DATABASE_URL`
- pravi Lemon Squeezy kljucevi i variant ID-jevi
- backup baze
- domen
- HTTPS

## 3. Minimalni `.env.production`

Primer:

```env
APP_ENV=production
BASE_URL=https://tvoj-domen.rs
HOST=0.0.0.0
PORT=8080
WEB_WORKERS=2
EXPORT_WORKER_MODE=dedicated_process
EXPORT_WORKER_POLL_SECONDS=2
SECRET_KEY=ovde-jak-produkcioni-kljuc
DATABASE_URL=postgresql://user:pass@host:5432/dbname
LEMON_SQUEEZY_API_KEY=api_key...
LEMON_SQUEEZY_WEBHOOK_SECRET=webhook_secret...
LEMON_SQUEEZY_STORE_ID=12345
LEMON_SQUEEZY_STORE_SUBDOMAIN=your-store
LEMON_SQUEEZY_VARIANT_ID_WEEKLY=123456
LEMON_SQUEEZY_VARIANT_ID_MONTHLY=123456
LEMON_SQUEEZY_CHECKOUT_SUCCESS_URL=https://tvoj-domen.rs/nalog?checkout=success
```

Osnova je sada vec pripremljena i kao fajl:

- `.env.production.example`

## 4. Start produkcije

```powershell
docker compose --env-file .\.env.production -f .\docker-compose.production.yml up --build -d
```

## 5. HTTP sloj

Trenutni `docker-compose.production.yml` podize:

- app kontejner
- export worker kontejner
- Nginx na portu `80`

Preporuceni prvi production start za worker-e:

- `WEB_WORKERS=2` za pocetak
- `EXPORT_WORKER_MODE=dedicated_process`
- `EXPORT_WORKER_POLL_SECONDS=2`
- kasnije `3-4` tek posle merenja CPU, RAM i DB konekcija

Nginx konfiguracija je u:

- `infra/nginx/krojna-lista-pro.conf`

HTTPS-ready sablon je u:

- `infra/nginx/krojna-lista-pro-https.conf`

## 6. HTTPS put

Najprakticnije je:

1. domen usmeri na server
2. potvrdi da HTTP radi
3. napravi pravi `.env.production` iz `.env.production.example`
4. iza toga uvedi TLS preko:
   - Certbot na hostu
   - ili spoljnog reverse proxy sloja
5. kad cert postoji, koristi `infra/nginx/krojna-lista-pro-https.conf`
6. zameni:
   - `tvoj-domen.rs`
   - putanje do sertifikata
7. tada HTTP ide na redirect, a app radi iza `443`

## 7. Obavezna provera posle deploy-a

- `GET /healthz`
- `GET /readyz`
- login
- logout
- demo projekat
- save/load
- Lemon Squeezy checkout session creation
- Lemon Squeezy webhook test

## 8. Napomena

Ovaj setup je dobar produkcioni temelj, ali nije poslednja rec.
Pre javnog pustanja i dalje treba:

- pravi Postgres runtime test
- HTTPS finalizacija
- backup/restore test
- monitoring i alerting

## Export worker napomena

Kada je `EXPORT_WORKER_MODE=dedicated_process`, app samo queue-uje export job u bazi,
a `krojna-lista-pro-export-worker` ga obradjuje kao poseban proces. To je prvi pravi
korak van in-process export modela.

Lokalno isti worker mozes pokrenuti i direktno:

```powershell
python .\export_worker_cli.py
```
