# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NES alumni community platform — a private, invite-driven fork of [vas3k.club](https://github.com/vas3k/vas3k.club). Django monolith with integrated Telegram bots and a hybrid Vue.js frontend.

## Local Development with Docker

### First-time setup

```bash
cp club/.env.example club/.env
# Edit club/.env — at minimum set SECRET_KEY
```

The dev Docker Compose bakes in all DB/Redis credentials, so only `SECRET_KEY` is strictly required to boot. Telegram tokens are optional for local work (bots will fail to start but the web app is unaffected).

### Start / stop

```bash
# Start everything (builds images on first run, hot-reloads code)
docker compose up --build

# Start without bots (faster, enough for web development)
docker compose up club_app queue postgres redis webpack

# Stop and wipe DB (full reset)
docker compose down -v

# Restart a single container after code changes
docker compose restart club_app
```

### Dev URLs

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000/ | App |
| http://127.0.0.1:8000/godmode/dev_login/ | Log in as a fixed admin user |
| http://127.0.0.1:8000/godmode/random_login/ | Log in as a random test user |

### What each container does

| Container | Command | Purpose |
|-----------|---------|---------|
| `club_app` | `make docker-run-dev` | Django dev server (port 8000). Runs `migrate` and `update_tags` on each start. |
| `queue` | `make docker-run-queue` | django-q2 worker. Runs `setup_schedules` first to register all CRON tasks. |
| `postgres` | postgres:14 image | Database. Credentials: `postgres/postgres`, DB: `nes_club`. |
| `redis` | redis:alpine image | Cache and django-q2 broker. |
| `webpack` | `npm run watch` | Webpack dev server — hot-reloads JS/CSS, writes `webpack-stats.json`. |
| `bot` | `make docker-run-bot` | Main Telegram bot (polling mode in dev). Optional. |
| `helpdeskbot` | `make docker-run-helpdeskbot` | Support Telegram bot. Optional. |

### Logs

```bash
docker compose logs -f club_app     # Web server logs
docker compose logs -f queue        # Background task logs
docker compose logs -f bot          # Telegram bot logs
```

### Database

```bash
# Apply new migrations (also runs automatically on club_app start)
docker compose exec club_app python3 manage.py migrate

# Open psql inside the container
docker compose exec postgres psql -U postgres nes_club

# Local psql (if postgres port is forwarded)
make psql
```

### Testing & Linting

```bash
make test           # Run Django tests (with pipenv)
make test-ci        # Run Django tests (CI mode, no pipenv)
make lint           # flake8 (syntax errors only, warnings are exit-zero)
```

### Frontend (without Docker)

```bash
make build-frontend   # One-time webpack build (uses npm in frontend/)
# The webpack container in docker compose handles this automatically
```

## Architecture

### Stack
- **Backend**: Django 5.1, Python 3.12, PostgreSQL 14, Redis, django-q2 (task queue)
- **Frontend**: Vue.js 2 components embedded in Django templates (not SPA), Webpack 5
- **Bots**: python-telegram-bot 20.7 (`bot/`, `helpdeskbot/`) — async, Application builder pattern
- **Production server**: Gunicorn + Uvicorn workers (ASGI)

### Django Apps
| App | Purpose |
|-----|---------|
| `authn/` | Email one-time-code login, sessions |
| `users/` | Profiles, roles, intro flow, access control |
| `posts/` | Feed, post types (incl. `job`), RSS, rendering pipeline |
| `comments/` | Comments, voting, rate limiting |
| `invites/` | Invite codes and activation |
| `notifications/` | Email/Telegram notifications and weekly digests |
| `godmode/` | Admin panel, moderation, bulk actions |
| `rooms/` | Telegram channel directory and subscriptions |
| `search/` | Full-text search (PostgreSQL, Russian stemming) |
| `badges/` | Peer recognition badges (free), `clickers/` markdown checklists |
| `misc/` | Stats, crew, network map, ical/google invites |
| `club/` | Django project core: settings, URLs, middleware, feature flags, scheduled tasks |
| `common/` | Shared utilities, Markdown renderer, data catalogs |

### Hybrid Frontend Pattern
Vue.js components are **not a SPA** — they are compiled by webpack and mounted directly inside Django HTML templates. `frontend/static/js/main.js` is the webpack entry point that registers all Vue components. Webpack outputs a `webpack-stats.json` manifest; Django uses it to inject asset hashes into templates via `django-webpack-loader`.

### Key Flows

**Email login**: `/auth/login/` → send one-time code → `/auth/email/code/` → create `Session`

**New user intro**: `/join/` (creates user with status `intro`) → `/intro/` (submit) → godmode moderation → status `approved`

**Invite activation**: `/invite/<code>/` → POST activate → create/login user, grant long-access token, mark invite used

**Background jobs**: All async work (emails, Telegram notifications, digests) goes through django-q2; failures reported to Sentry.

### Feature Flags
`club/features.py` — toggle features without deployment.

### Key Files
- `club/settings.py` — all config, env-driven
- `club/urls.py` — full URL routing (80+ routes)
- `club/middleware.py` — request/session middleware
- `frontend/webpack.config.js` — webpack config
- `common/markdown/` — custom mistune 3 renderers
- `notifications/digests.py` — weekly digest generation

## Environment Setup

`club/.env.example` lists all supported variables. For local Docker development only `SECRET_KEY` is required — DB and Redis are pre-configured in `docker-compose.yml`. For production copy `.env.production.example` and fill in all values.

Key variables:
- `SECRET_KEY` — Django secret key
- `TELEGRAM_TOKEN` — main bot token
- `EMAIL_BACKEND` + provider key (`RESEND_API_KEY` or `BREVO_API_KEY`) — email delivery via django-anymail (Railway blocks SMTP)
- `MEDIA_UPLOAD_URL` / `MEDIA_UPLOAD_CODE` — image upload service

## Production

### On a VPS (docker-compose.production.yml)

Production uses `docker-compose.production.yml` with:
- Gunicorn: 5 Uvicorn workers, port `$PORT` (default 8814), behind Nginx
- Containers: `club_app`, `queue` (also runs scheduled tasks via django-q2), `bot`, `helpdeskbot`, `redis`
- No separate cron container — all scheduled tasks run inside the `queue` container via `setup_schedules` + `qcluster`
- Redis with health checks; JSON log driver with rotation

```bash
docker compose -f docker-compose.production.yml up -d --build
```

### On Railway

Railway deploys directly from the `Dockerfile` — no docker-compose needed. A `railway.json` is included in the repo root.

**Start command mechanism.** All services run from the same repo and differ only by their start command. Set it explicitly per service (Railway-native, no ambiguity): **Service → Settings → Deploy → Custom Start Command.**

| Service | Custom Start Command | What it runs |
|---------|----------------------|--------------|
| `club_app` | `make docker-run-production` | migrate + update_achievements + collectstatic (+ create_admin if `INITIAL_ADMIN_*`), then serves web on `$PORT`. Expose HTTP port. |
| `queue` | `make docker-run-queue` | `setup_schedules` + django-q2 `qcluster` — background jobs **and** all scheduled/cron tasks. No port. |
| `bot` _(optional)_ | `make docker-run-bot` | main Telegram bot (`bot/main.py`), webhook mode. No port. |
| `helpdeskbot` _(optional)_ | `make docker-run-helpdeskbot` | helpdesk Telegram bot (`helpdeskbot/main.py`), webhook mode. No port. |

`SERVICE_CMD` is **not** a Railway feature — it's a plain env var that this repo's `start.sh` reads when no Custom Start Command is set (`railway.json` → `bash start.sh` → `make $SERVICE_CMD`). You can set `SERVICE_CMD=docker-run-queue` etc. as a variable instead, but a Custom Start Command always overrides it — prefer the explicit command if unsure.

**Required env vars for Railway** (set `DEBUG=false` — this disables all dev login endpoints):
```
MODE=production
DEBUG=false
SERVICE_CMD=docker-run-production
SECRET_KEY=<long random string>
APP_HOST=https://<your-app>.railway.app
POSTGRES_HOST=${{Postgres.PGHOST}}
POSTGRES_DB=${{Postgres.PGDATABASE}}
POSTGRES_USER=${{Postgres.PGUSER}}
POSTGRES_PASSWORD=${{Postgres.PGPASSWORD}}
REDIS_HOST=${{Redis.REDISHOST}}
REDIS_PASSWORD=${{Redis.REDISPASSWORD}}
```

**Email (Railway блокирует исходящий SMTP — используй HTTP API через django-anymail).**

Отправка кода backend-агностична (`send_mail`/`EmailMultiAlternatives` в `notifications/email/sender.py`), поэтому смена провайдера — только переменные окружения. Поддерживаются Resend и Brevo (ключи читаются в `club/settings.py → ANYMAIL`).

Resend (рекомендуется — бесплатный тариф, HTTP API):
```
EMAIL_BACKEND=anymail.backends.resend.EmailBackend
RESEND_API_KEY=<ключ из Resend → API Keys>
DEFAULT_FROM_EMAIL=Название <no-reply@yourdomain.com>
```
Перед отправкой подтверди домен в Resend → Domains (добавь DNS-записи SPF/DKIM), и `DEFAULT_FROM_EMAIL` должен быть на этом домене.

Brevo (альтернатива):
```
EMAIL_BACKEND=anymail.backends.brevo.EmailBackend
BREVO_API_KEY=<ключ из Brevo → SMTP & API → API Keys>
DEFAULT_FROM_EMAIL=Название <no-reply@yourdomain.com>
```

**Telegram (сервис `club_app`):**
```
TELEGRAM_TOKEN=<токен от @BotFather>
TELEGRAM_BOT_URL=https://t.me/<username_бота>
TELEGRAM_ADMIN_CHAT_ID=<ID чата модераторов>
TELEGRAM_CLUB_CHANNEL_ID=<ID основного канала>
TELEGRAM_CLUB_CHAT_ID=<ID основного чата>
```

**Telegram (сервис `bot`):**
```
SERVICE_CMD=docker-run-bot
TELEGRAM_TOKEN=<тот же токен>
TELEGRAM_BOT_WEBHOOK_HOST_URL=https://<bot-service-url>.railway.app
# + все остальные TELEGRAM_* переменные
```

**Telegram (сервис `helpdeskbot`):**
```
SERVICE_CMD=docker-run-helpdeskbot
TELEGRAM_HELP_DESK_BOT_TOKEN=<токен helpdeskbot>
TELEGRAM_HELP_DESK_BOT_QUESTION_CHANNEL_ID=<ID канала вопросов>
TELEGRAM_HELP_DESK_BOT_QUESTION_CHANNEL_DISCUSSION_ID=<ID чата обсуждений>
TELEGRAM_HELPDESK_WEBHOOK_HOST_URL=https://<helpdeskbot-service-url>.railway.app
```

⚠️ **Переменные не подтягиваются автоматически** — их нужно добавить вручную через Variables → Raw Editor. Если переменные не заданы, контейнер стартует молча и сразу падает с 502.

**Debugging 502**: Deploy Logs → если после "Starting Container" пусто → переменные не заданы. Добавь переменные, Railway автоматически передеплоит.

**Dev login protection:** `authn/views/debug.py` checks `if not (settings.DEBUG or settings.TESTS_RUN)` before allowing dev/random login. Setting `DEBUG=false` makes these endpoints return 403 Access Denied.

**First admin in production** — add these vars to Railway, redeploy, then delete them:
```
INITIAL_ADMIN_EMAIL=your@email.com
INITIAL_ADMIN_SLUG=admin
INITIAL_ADMIN_NAME=Your Name
```
The `create_admin` management command runs on startup, creates the user, and is idempotent (safe to re-run). Login via `/auth/login/` with that email — one-time code sent to inbox. Management command: `users/management/commands/create_admin.py`.

**Auth rate limit reset** — if login codes are exhausted, add this var and redeploy `club_app`, then remove:
```
CLEAR_AUTH_EMAIL=your@email.com
```
