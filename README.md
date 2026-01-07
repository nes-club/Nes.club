<div align="center">
  <br>
  <img src="frontend/static/images/logo/logo-256.png" alt="">
  <h1>Сообщество выпускников РЭШ</h1>
</div>

Welcome to the NES alumni community (non-official) codebase. We're building a private alumni community. We've opensourced the code so that every member could contribute or implement a feature that they want.

This project is based on the vas3k.club engine and adapted for the NES alumni community. It is a private, invite-driven space focused on thoughtful conversations, networking, and mutual help for alumni, staff, and friends of NES.

Our values: honesty, fair share, respect for other members, rationality, friendliness and usefulness. We have a zero-tolerance policy on anonymity, insults and toxicity. But we always try to stay in touch with reality, so we're also not tolerant of witch hunting and call-out culture.

We're a bullshitless community!

## 🛠 Tech stack

👨‍💻 **TL;DR: Django, Postgres, Redis, Vue.js, Webpack**

We try to keep our stack as simple and stupid as possible. Because we're not very smart either.

The trickiest part of our stack is how we develop the frontend and backend as a single service. We don't use SPA, as many people do, but only make parts of the page dynamic by inserting Vue.js components directly into Django templates. This may seem weird, but it actually makes it very easy for one person to develop and maintain the entire site.

You don't really need to understand how the magic of webpack <-> django communication works under the hood to develop new components. Just run `django runserver` and `npm run watch` at the same time and enjoy your coding.

Feel free to propose "state of the art" refactorings for UI or backend code if you know how to do it better. We're open for best practices from both worlds.

## 🔮 Installing and running locally (Docker)

1. Install Docker Desktop.
2. Open the repository folder in your terminal.
3. Build and run all dev services:

    ```sh
    docker compose up --build
    ```

This starts the app in dev mode on http://127.0.0.1:8000/ plus Postgres, Redis, queue workers, and webpack.

After the containers are up:

1. Wait for `Starting development server at http://0.0.0.0:8000/`.
2. Open http://127.0.0.1:8000/.
3. Quick admin session: http://127.0.0.1:8000/godmode/dev_login/
4. Random test user: http://127.0.0.1:8000/godmode/random_login/

Hot reload works for both backend and frontend. If assets look stale:

```sh
docker compose restart club_app webpack
```

If you changed templates and still see old texts, check the page source in the DB (docs pages are stored in the database).
If you need to fully reset everything:

```sh
docker compose down -v
docker compose up --build
```

## 🔗 Local links

- Home: http://127.0.0.1:8000/
- Join: http://127.0.0.1:8000/join/
- Django admin: http://127.0.0.1:8000/admin/
- Dev login (admin): http://127.0.0.1:8000/godmode/dev_login/
- Random user: http://127.0.0.1:8000/godmode/random_login/

Create a Django superuser (optional):

```sh
docker compose exec club_app python3 manage.py createsuperuser
```

## 🧩 Docker compose profiles

Quick comparison:

1. `docker-compose.yml` (dev/local)
   - Services: app, queue, postgres, redis, webpack
   - Hot-reload via `${PWD}:/app`
   - Runs on `:8000`
2. `docker-compose.production.yml` (prod/server)
   - Services: app, queue, redis, optional bots/cron
   - No webpack; frontend is built in Dockerfile
   - External Postgres
   - Runs on `127.0.0.1:8814` (behind reverse proxy)
3. `docker-compose.test.yml` (tests/CI)
   - Minimal stack for running tests
   - Not intended for real use

Run commands:

```sh
# Dev/local
docker compose up --build

# Production
docker compose -f docker-compose.production.yml up -d

# Tests (example)
docker compose -f docker-compose.test.yml up -d
```

## 🤖 Telegram bots (optional)

There are two optional bots:

1. **Main club bot** (`bot/`)
   - Sends auth/login links and notifications
   - Handles comment replies, upvotes, and moderation callbacks
   - Supports AI replies when mentioned (if enabled)
2. **Helpdesk bot** (`helpdeskbot/`)
   - Collects questions from members
   - Posts them to a helpdesk channel
   - Tracks replies in the linked discussion

Local dev uses polling (no public webhook needed).

1. Set env vars (minimum for main bot):
   - `TELEGRAM_TOKEN`
   - `TELEGRAM_ADMIN_CHAT_ID`
   - `TELEGRAM_BOT_URL` (public bot link)
2. For helpdesk bot (optional):
   - `TELEGRAM_HELP_DESK_BOT_TOKEN`
   - `TELEGRAM_HELP_DESK_BOT_QUESTION_CHANNEL_ID`
   - `TELEGRAM_HELP_DESK_BOT_QUESTION_CHANNEL_DISCUSSION_ID`
3. Uncomment `bot` and/or `helpdeskbot` in `docker-compose.yml`.
4. Start the bot containers:

```sh
docker compose up --build bot helpdeskbot
```

## ✉️ Настройка отправки почты (SMTP)

Коды входа и уведомления отправляются через SMTP.

Минимальные переменные:
- `EMAIL_BACKEND` (optional, default SMTP; for local debug use `django.core.mail.backends.console.EmailBackend`)
- `EMAIL_HOST`
- `EMAIL_PORT` (обычно 587)
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`

Пример (Gmail):

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your@nes.ru
EMAIL_HOST_PASSWORD=app_password
DEFAULT_FROM_EMAIL=Сообщество выпускников РЭШ <your@nes.ru>
```

Важно: для Gmail нужен App Password, обычный пароль не подойдет.

После изменения `.env` перезапустите:

```sh
docker compose restart club_app queue
```

## 🧪 Dev environment on a server

Same stack as local, but run it in the background and point `APP_HOST` to your dev domain.

1. Create a `.env` file with:
   - `APP_HOST=https://test.ru` (or `http://<server-ip>:8000`)
   - Optional bot vars if you need Telegram bots (see below)
2. Run:

```sh
docker compose up --build -d
```

3. Check logs if something failed:

```sh
docker compose logs -f club_app
```

Open the site on your dev domain or `http://<server-ip>:8000/` and use the same links as in local:

- Admin: `http://<server-ip>:8000/admin/`
- Dev login: `http://<server-ip>:8000/godmode/dev_login/`
- Random user: `http://<server-ip>:8000/godmode/random_login/`

If you want HTTPS and a clean domain, put Nginx/Traefik in front of `127.0.0.1:8000` and set `APP_HOST` to the public URL.

To update code in dev:

```sh
git pull
docker compose up --build -d
docker compose restart club_app webpack
```

To reset dev data:

```sh
docker compose down -v
docker compose up --build -d
```

## 🏭 Production environment on a server

Production is described in `docker-compose.production.yml` and expects an external Postgres.
All domains and secrets are read from `.env` (see `.env.production.example`).

1. Create `.env` with at least:
   - `APP_HOST=https://test.ru`
   - `CLUB_IMAGE=nesclub/club:latest` (optional; image name in registry)
   - `MEDIA_UPLOAD_URL=` (optional; leave empty for local media)
   - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
   - `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`
   - `TELEGRAM_TOKEN`, `TELEGRAM_ADMIN_CHAT_ID` (if bots are enabled)
2. Start production services:

```sh
docker compose -f docker-compose.production.yml up -d
```

3. Put a reverse proxy in front of the app:
   - App listens on `127.0.0.1:8814`
   - Bot webhooks (if enabled) should be reachable at `${APP_HOST}/telegram/webhook/`

Optional services for prod:

```sh
docker compose -f docker-compose.production.yml up -d bot helpdeskbot cron queue
```

### ✅ Production checklist

1. Nginx/Traefik
   - Reverse proxy to `127.0.0.1:8814`
   - Pass `Host` and `X-Forwarded-*` headers
   - Gzip/brotli enabled
2. SSL
   - Get TLS certs (Let’s Encrypt or your CA)
   - Force HTTPS redirects
   - Update `APP_HOST=https://your-domain`
3. Healthchecks
   - Add an external monitor for `GET /` (200)
   - Optional: monitor `GET /metrics` if you expose it
4. Backups
   - Postgres daily dump (off-host)
   - `gdpr/downloads` volume backup if you use it
   - Store backups encrypted and test restore monthly

### 📦 Nginx пример

```nginx
server {
    listen 80;
    server_name test.ru;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name test.ru;

    ssl_certificate /etc/letsencrypt/live/test.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/test.ru/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8814;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
    }
}
```

### 🗄️ Postgres backup script

Use `scripts/backup_postgres.sh` and run it from cron on the server.

```sh
export POSTGRES_HOST=localhost
export POSTGRES_DB=nes_club
export POSTGRES_USER=nes
export POSTGRES_PASSWORD=your_password
export BACKUP_KEEP_DAYS=14
./scripts/backup_postgres.sh /var/backups/nes_club
```

Example cron entry (daily at 03:30):

```cron
30 3 * * * cd /srv/nes.club && /usr/bin/env POSTGRES_HOST=localhost POSTGRES_DB=nes_club POSTGRES_USER=nes POSTGRES_PASSWORD=your_password BACKUP_KEEP_DAYS=14 ./scripts/backup_postgres.sh /var/backups/nes_club
```

## 🧑‍💻 Advanced setup for devs

For more information on how to test the telegram bot, run project without docker and other useful notes, read [docs/setup.md](docs/setup.md).

## ☄️ Testing

We use standard Django testing framework. No magic, really. You can run them from PyCharm or using Django CLI. 

See [docs/test.md](docs/test.md) for more insights.

> We don't have UI tests, sorry. Maybe in the future

## 🚢 Deployment

No k8s, no AWS, we ship dockers directly via ssh and it's beautiful!

The entire production configuration is described in the [docker-compose.production.yml](docker-compose.production.yml) file. 

Then, [Github Actions](.github/workflows/deploy.yml) have to take all the dirty work. They build, test and deploy changes to production on every merge to master (only official maintainers can do it).

Explore the whole [.github](.github) folder for more insights.

We're open for proposals on how to improve our deployments without overcomplicating it with modern devops bullshit.

### GitHub Actions deployment (detailed setup)

Workflow: `.github/workflows/deploy.yml`

How it works:
1. Triggers on every `push` to `master`.
2. Builds and pushes Docker images to GHCR.
3. Connects to your server via SSH and runs `docker compose -f docker-compose.production.yml --env-file=.env up -d`.

Prerequisites on the server:
- Docker and Docker Compose installed
- Project directory (default): `/srv/nes.club/`
- SSH access with a deploy key (no password)

Required GitHub Secrets (Settings → Secrets and variables → Actions):

Minimal (required for deploy):
- `TOKEN` (PAT or GitHub token with `write:packages` for GHCR)
- `PRODUCTION_SSH_HOST`
- `PRODUCTION_SSH_USERNAME`
- `PRODUCTION_SSH_KEY` (private key)
- `SECRET_KEY`
- `APP_HOST`
- `POSTGRES_PASSWORD`
- `EMAIL_HOST`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`

Media / images (optional):
- `MEDIA_UPLOAD_URL`
- `MEDIA_UPLOAD_CODE`

Monitoring (optional):
- `SENTRY_DSN`

Telegram bots (optional):
- `TELEGRAM_TOKEN`
- `TELEGRAM_BOT_URL`
- `TELEGRAM_ADMIN_CHAT_ID`
- `TELEGRAM_CLUB_CHANNEL_URL`
- `TELEGRAM_CLUB_CHANNEL_ID`
- `TELEGRAM_CLUB_CHAT_URL`
- `TELEGRAM_CLUB_CHAT_ID`
- `TELEGRAM_ONLINE_CHANNEL_URL`
- `TELEGRAM_ONLINE_CHANNEL_ID`
- `TELEGRAM_HELP_DESK_BOT_QUESTION_CHANNEL_DISCUSSION_ID`
- `TELEGRAM_HELP_DESK_BOT_QUESTION_CHANNEL_ID`
- `TELEGRAM_HELP_DESK_BOT_TOKEN`

Payments (optional, if enabled):
- `STRIPE_ACTIVE`
- `STRIPE_API_KEY`
- `STRIPE_TICKETS_API_KEY`
- `STRIPE_PUBLIC_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_TICKETS_WEBHOOK_SECRET`

Patreon (optional, if enabled):
- `PATREON_CLIENT_ID`
- `PATREON_CLIENT_SECRET`

Auth / integrations (optional):
- `JWT_PRIVATE_KEY`
- `WEBHOOK_SECRETS`
- `OPENAI_API_KEY`

Notes and customization:
- If your default branch is not `master`, update `on.push.branches` in the workflow.
- If your server path is different, update the `scp`/`ssh` paths in `deploy.yml`.
- The workflow writes all `secret_*` variables to `.env` on the server.

## 🛤 Forking and tweaking

Forks are welcome. We're small and our engine is not universal like Wordpress, but with sufficient programming skills (and using grep), you can launch your own Club website in a couple of weeks. 

Three huge requests for everyone:

- Please give kudos the original authors. "Works on vas3k.club engine" in the footer of your site will be enough.
- Please share new features you implement with us, so other folks can also benefit from them, and your own codebase minimally diverges from the original one (so you can sync updates and security fixes) . Use our [feature-flags](club/features.py).

> ♥️ [Feature-flags](club/features.py) are great. Use them to tweak your fork. Create new flags to upstream your new features or disable existing ones.

## 🙋‍♂️ Support and contributions

- Для этой копии используйте внутренний трекер задач вашей команды.
- Вопросы по безопасности и доступам: atishin@nes.ru.
- Правила и ценности описаны в разделе `/docs/` внутри этого проекта.


## 👩‍💼 License 

[MIT](LICENSE)

In other words, you can use the code for private and commercial purposes with an author attribution (by including the original license file or mentioning the Club 🎩).

Feel free to contact us via email [atishin@nes.ru](mailto:atishin@nes.ru).

❤️
