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
3. Create `.env` in the repo root (it is already in `.gitignore`).
4. Build and run all dev services:

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

If you need a clean rebuild without cache:

```sh
docker compose down -v
docker compose build --no-cache
docker compose up --build
```

### Troubleshooting

Clean rebuild (no cache):

```sh
docker compose down -v
docker compose build --no-cache
docker compose up --build
```

### Minimal local `.env`

```dotenv
APP_HOST=http://127.0.0.1:8000
SECRET_KEY=
DEBUG=true

POSTGRES_DB=nes_club
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=postgres

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=Сообщество выпускников РЭШ <atishin@nes.ru>

TELEGRAM_TOKEN=
TELEGRAM_BOT_URL=
TELEGRAM_ADMIN_CHAT_ID=
TELEGRAM_CLUB_CHANNEL_URL=
TELEGRAM_CLUB_CHAT_URL=
TELEGRAM_ONLINE_CHANNEL_URL=

TELEGRAM_HELP_DESK_BOT_TOKEN=
TELEGRAM_HELP_DESK_BOT_QUESTION_CHANNEL_ID=
TELEGRAM_HELP_DESK_BOT_QUESTION_CHANNEL_DISCUSSION_ID=
```

## 🔗 Local links

- Home: http://127.0.0.1:8000/
- Join: http://127.0.0.1:8000/join/
- Django admin: http://127.0.0.1:8000/admin/
- Dev login (admin): http://127.0.0.1:8000/godmode/dev_login/
- Random user: http://127.0.0.1:8000/godmode/random_login/

> ⚠️ Dev login endpoints (`/godmode/dev_login/`, `/godmode/random_login/`) are only active when `DEBUG=true`.
> In production (`DEBUG=false`) they return 403 Access Denied.

## 🚀 Deploying to Railway

Railway deploys via the existing `Dockerfile` and `railway.json`. No docker-compose needed.

### Services to create in Railway

Create separate Railway services from the **same** GitHub repo. They differ only by their **start command**. The most explicit (and Railway-native) way to set it is per service:
**Service → Settings → Deploy → Custom Start Command.**

| Service | Custom Start Command | What it runs |
|---------|---------------------|--------------|
| `club_app` | `make docker-run-production` | Applies migrations + `update_achievements`, runs `collectstatic`, optionally creates the first admin (if `INITIAL_ADMIN_*` set), then serves the web app on `$PORT` (Gunicorn + Uvicorn workers). **Expose an HTTP port.** |
| `queue` | `make docker-run-queue` | Registers scheduled tasks (`setup_schedules`) and runs the django-q2 worker (`qcluster`) — background jobs **and** all cron tasks. No port. |
| `bot` _(optional)_ | `make docker-run-bot` | Runs the main Telegram bot (`bot/main.py`) in webhook mode. No port. |
| `helpdeskbot` _(optional)_ | `make docker-run-helpdeskbot` | Runs the helpdesk Telegram bot (`helpdeskbot/main.py`) in webhook mode. No port. |

All four wait for Postgres + migrations before starting (`utils/wait_for_*`).

> **Note on `SERVICE_CMD`.** If you don't set a Custom Start Command, the repo falls back to `railway.json`'s `startCommand` (`bash start.sh`), which runs `make $SERVICE_CMD` — so you can instead just set a `SERVICE_CMD` **variable** per service (`docker-run-production` / `docker-run-queue` / `docker-run-bot` / `docker-run-helpdeskbot`). `SERVICE_CMD` is **not** a Railway feature — it's a plain env var this repo's `start.sh` reads. A Custom Start Command always overrides it, so prefer the explicit command if in doubt.

Also add **Postgres** and **Redis** as Railway plugins (`+ New → Database`).

### Required environment variables

Set these in each Railway service (all services share the same set except where noted):

```dotenv
# Core
MODE=production
DEBUG=false
SECRET_KEY=<generate: python3 -c "import secrets; print(secrets.token_urlsafe(50))">
APP_HOST=https://<your-app>.up.railway.app
APP_NAME=Сообщество выпускников РЭШ
APP_TITLE=Сообщество выпускников РЭШ

# Database — используй Railway reference variables из Postgres плагина
POSTGRES_HOST=${{Postgres.PGHOST}}
POSTGRES_PORT=${{Postgres.PGPORT}}
POSTGRES_DB=${{Postgres.PGDATABASE}}
POSTGRES_USER=${{Postgres.PGUSER}}
POSTGRES_PASSWORD=${{Postgres.PGPASSWORD}}

# Redis — из Redis плагина
REDIS_HOST=${{Redis.REDISHOST}}
REDIS_PORT=${{Redis.REDISPORT}}
REDIS_DB=0

# Email — без этого пользователи не смогут войти (коды логина уходят на почту)
# ⚠️ Railway блокирует исходящий SMTP (Gmail и т.п. не работают) — нужен HTTP API через django-anymail.
# Рекомендуется Resend (бесплатный тариф). Альтернатива — Brevo. Подробнее: docs/notifications.md
EMAIL_BACKEND=anymail.backends.resend.EmailBackend
RESEND_API_KEY=<ключ из Resend → API Keys>
DEFAULT_FROM_EMAIL=Сообщество выпускников РЭШ <no-reply@yourdomain.com>
# ⚠️ Домен в DEFAULT_FROM_EMAIL должен быть подтверждён в Resend → Domains (DNS-записи SPF/DKIM)

# Telegram — основной бот (опционально: без токенов боты не стартуют, веб-приложение работает).
# Эти переменные нужны и сервису `club_app` (шлёт уведомления/анонсы), и сервису `bot`.
TELEGRAM_TOKEN=                      # токен от @BotFather
TELEGRAM_BOT_URL=https://t.me/your_bot
TELEGRAM_ADMIN_CHAT_ID=              # чат модераторов (кнопки одобрить/отклонить)
TELEGRAM_CLUB_CHANNEL_URL=
TELEGRAM_CLUB_CHANNEL_ID=            # основной канал (анонсы постов)
TELEGRAM_CLUB_CHAT_URL=
TELEGRAM_CLUB_CHAT_ID=               # основной чат
TELEGRAM_ONLINE_CHANNEL_URL=
TELEGRAM_ONLINE_CHANNEL_ID=
# Только для сервиса `bot` (webhook-режим в проде — нужен публичный HTTPS):
TELEGRAM_BOT_WEBHOOK_HOST_URL=https://<bot-service>.up.railway.app

# Telegram — helpdesk-бот (опционально, отдельный сервис `helpdeskbot`)
TELEGRAM_HELP_DESK_BOT_TOKEN=
TELEGRAM_HELP_DESK_BOT_QUESTION_CHANNEL_ID=
TELEGRAM_HELP_DESK_BOT_QUESTION_CHANNEL_DISCUSSION_ID=
TELEGRAM_HELPDESK_WEBHOOK_HOST_URL=https://<helpdeskbot-service>.up.railway.app

# Медиа (опционально — без этого аватарки не загружаются, приложение не падает)
# Подробнее о вариантах: docs/media-storage.md
MEDIA_UPLOAD_URL=
MEDIA_UPLOAD_CODE=

# OG-превью постов (опционально)
OG_IMAGE_GENERATOR_URL=

# Мониторинг (опционально)
SENTRY_DSN=
```

### First deploy checklist

1. Push code to GitHub
2. Create Railway project → "Deploy from GitHub repo" → выбери ветку `master`
3. Добавь **Postgres** и **Redis**: в проекте нажми `+ New` → `Database` → выбери тип
4. **⚠️ Критически важно: добавь переменные окружения** — без них контейнер стартует но сразу падает с 502:
   - Открой сервис → вкладка **Variables** → кнопка **Raw Editor**
   - Вставь все переменные из раздела выше
   - Railway автоматически передеплоит сервис после сохранения
5. Установи **custom domain**: Settings → Networking → Generate Domain (или свой домен), затем обнови `APP_HOST`
6. После первого деплоя `club_app` автоматически запустит `migrate` и `update_achievements`

### Troubleshooting: 502 Bad Gateway

**Симптом**: сайт открывается, но возвращает 502. Deploy Logs содержат только "Starting Container" и ничего больше.

**Причина**: переменные окружения не заданы — Django/Gunicorn не может подключиться к БД и падает на старте до первого лога.

**Решение**:
1. Открой сервис → **Variables** → убедись что там **не "0 Variables"**
2. Если пусто — добавь переменные через **Raw Editor** (см. раздел выше)
3. После сохранения Railway автоматически передеплоит, в Deploy Logs появятся реальные логи Gunicorn

**Проверка после деплоя**:
```bash
# Установи Railway CLI
npm i -g @railway/cli
railway login
railway link  # выбери проект

# Логи в реальном времени
railway logs --service club_app

# Django checks
railway shell --service club_app
python3 manage.py check
python3 manage.py showmigrations
```

### Static files and Cloudflare

Static files (CSS, JS, images) are served by **WhiteNoise** — a library that lets Gunicorn serve static files without Nginx. On every deploy `collectstatic` runs automatically and collects files into `staticfiles/` with content hashes in filenames.

For production, put **Cloudflare** in front of Railway so static files are cached at the edge:

1. Add your domain to Cloudflare (free plan)
2. Create a CNAME record pointing to your Railway domain (with **Proxied** enabled)
3. Update `APP_HOST` in Railway Variables to your custom domain
4. In Cloudflare → Rules → Cache Rules: cache `/static/*` with 1-year TTL

Full setup guide: [docs/cloudflare-setup.md](docs/cloudflare-setup.md)

### After first deploy — create the first admin

There is no dev_login in production (`DEBUG=false` makes it return 403).

Add these three variables in Railway → Variables, then redeploy:

```
INITIAL_ADMIN_EMAIL=your@email.com
INITIAL_ADMIN_SLUG=admin
INITIAL_ADMIN_NAME=Your Name
```

On startup the `create_admin` management command will run, create the user, and print `Admin user created: your@email.com` in Deploy Logs.

**After the deploy succeeds — delete all three `INITIAL_ADMIN_*` variables** from Railway. They are no longer needed and Railway will redeploy without them.

Then log in via `/auth/login/` — enter your email, receive a one-time code, done.

**Security notes:**
- Login is email-only (no passwords) — only someone with access to your inbox can log in
- The command checks for duplicates — re-running it with the same email does nothing
- `INITIAL_ADMIN_*` vars only take effect at deploy time, not at runtime
- Dev login endpoints (`/godmode/dev_login/`, `/godmode/random_login/`) return 403 when `DEBUG=false`

### Production vs dev differences

| | Dev (local) | Production (Railway) |
|---|---|---|
| Server | Django dev server | Gunicorn + 5 Uvicorn workers |
| Port | 8000 | `$PORT` (Railway-assigned) |
| `DEBUG` | `true` | `false` |
| Dev login | ✅ available | ❌ returns 403 |
| Webpack | runs as a separate container | built into the Docker image at build time |
| Database | local postgres container | Railway Postgres plugin |
| Static files | served by Django dev server | copied to `/tmp/static`, served by Gunicorn |
| Telegram bots | polling mode | webhook mode (requires public HTTPS domain) |

## 🧱 Architecture overview (3 levels deep)

### Level 1 — top‑level modules

- `club/` — Django project core: settings, urls, middleware, feature flags, scheduled tasks.
- `authn/` — authentication: email one‑time‑code login + sessions (no passwords, no OAuth/OpenID).
- `users/` — user profiles, roles, intro/moderation, settings. Access is perpetual (no paid membership).
- `posts/` — posts (13 types), feeds, RSS, rendering pipeline.
- `comments/` — comments (3 levels), voting, rate limiting, moderation tools.
- `invites/` — invite codes, activation flow.
- `notifications/` — email + telegram notifications and the weekly digest.
- `godmode/` — custom admin panel, moderation actions, bulk operations.
- `rooms/` — telegram channels/chats directory, subscriptions, mutes.
- `search/` — full‑text search (PostgreSQL tsvector) — index maintained live + incremental rebuild.
- `frontend/` — Django templates, CSS, Vue 2 components, webpack.
- `bot/` — main Telegram bot (auth, moderation buttons, /horo /random /top /whois).
- `helpdeskbot/` — helpdesk Telegram bot (question → channel → answer routing).
- `common/` — shared utils, data catalogs, markdown renderers, image upload.
- `utils/` — shared helpers and wait‑for‑db/migrations scripts.
- `misc/` — stats, crew, network map, robots, ical/google invites.
- `badges/` — peer badges (free), `bookmarks/`, `tags/`, `clickers/` (markdown checklists) — supporting features.

### Level 2 — key files per module

**Core**
- `club/settings.py` — env‑driven settings, integrations, defaults.
- `club/urls.py` — URL routing for site + API.
- `club/middleware.py` — request/session middleware.
- `club/context_processors.py` — globals for templates.
- `club/features.py` — feature flags.

**Auth**
- `authn/views/auth.py` — `/join`, `/login`, `/logout`.
- `authn/views/email.py` — email login code flow.
- `authn/views/debug.py` — dev/random login (only when `DEBUG=true`).
- `authn/models/session.py` — sessions + one‑time codes.
- `authn/decorators/auth.py` — `require_auth` decorator.
- `authn/helpers.py` — auth cookies/session helpers.

**Users**
- `users/models/user.py` — main user model + roles + state.
- `users/views/profile.py` — profile pages and tabs.
- `users/views/intro.py` — intro submission + moderation.
- `users/views/settings.py` — profile/account/notifications/bot/data.
- `users/services/access.py` — long‑access handling.

**Posts**
- `posts/models/post.py` — post model + counters + helpers.
- `posts/views/feed.py` — main feed.
- `posts/views/posts.py` — show/edit/create/delete posts.
- `posts/views/api.py` — upvotes/bookmarks/subscriptions/RSVP.
- `posts/forms/compose.py` — compose forms by type.
- `posts/renderers.py` — prepares post/comment render data.
- `posts/rss.py`, `posts/user_rss.py` — RSS.

**Comments**
- `comments/models.py` — comment model.
- `comments/views.py` — create/edit/delete/pin.
- `comments/api.py` — comment API (fetch lists).
- `comments/rate_limits.py` — rate limits.

**Invites**
- `invites/models.py` — invite model + status helpers.
- `invites/views.py` — list/show/activate/create.
- `invites/api.py` — invite API for admins/bank.

**Notifications**
- `notifications/email/*` — email templates + sending.
- `notifications/telegram/*` — Telegram notifications.
- `notifications/digests.py` — digest generator.
- `notifications/views.py` — email/telegram actions.
- `notifications/webhooks.py` — inbound webhooks.

**Godmode (Admin)**
- `godmode/config.py` — admin UI config and sections.
- `godmode/views/main.py` — admin CRUD rendering.
- `godmode/pages/*` — special admin pages.
- `godmode/actions/*` — user/post moderation actions.

**Frontend**
- `frontend/html/*.html` — main templates.
- `frontend/static/js/main.js` — JS entry.
- `frontend/static/js/common/api.service.js` — AJAX helper.
- `frontend/static/css/theme.css` — theme tokens.
- `frontend/webpack.config.js` — build config.

**Bots**
- `bot/main.py`, `bot/handlers/*` — main bot logic.
- `helpdeskbot/main.py`, `helpdeskbot/handlers/*` — helpdesk bot.

**Shared**
- `common/data/*` — catalogs (achievements, tags, labels).
- `common/markdown/*` — Markdown rendering.
- `utils/*` — small helpers + wait scripts.

### Level 3 — internal sub‑modules

- `posts/templatetags/*` — template filters for posts.
- `comments/templatetags/*` — template filters for comments.
- `users/templatetags/*` — template filters for users.
- `godmode/pages/*` — moderation/digest/invite workflows.
- `notifications/email/*` — users, invites, badges, achievements.
- `notifications/telegram/*` — posts/comments/users/moderation.
- `frontend/html/posts/*` — per‑post type templates.
- `frontend/html/comments/*` — comment templates.
- `frontend/static/js/components/*` — Vue components (upvotes, bookmark, tags).

## 🔁 End‑to‑End flows

### New user → intro → moderation → access

1) `/join/` → `authn/views/auth.py::join`  
   - Validates email + invite (if needed).
   - Creates user with `moderation_status=intro` (access is perpetual — no paid membership).
   - Sends login code.
2) `/auth/email/code/` → `authn/views/email.py::email_login_code`  
   - Verifies code, creates session, logs user in.
3) `/intro/` → `users/views/intro.py`  
   - User submits intro, status → `on_review`.
4) `godmode/pages/moderation.py` + actions  
   - Moderator approves → status → `approved`.

### Email login

- `/auth/login/` → `authn/views/auth.py::login` (form)  
- POST `/auth/email/` → `authn/views/email.py::email_login` (send code)  
- GET `/auth/email/code/` → `authn/views/email.py::email_login_code` (session)

### Invite activation

- `/invites/` → `invites/views.py::list_invites`
- `/invite/<code>/` → `invites/views.py::show_invite`
- POST `/invite/<code>/activate/` → `invites/views.py::activate_invite`
  - Creates or logs in user, grants long access, marks invite used.

### Flow diagram (auth + moderation)

```text
join -> email_code -> intro -> on_review -> approved
      (invite optional)             |
                                 godmode decision
```

### Models used by core scenarios

- Email login: `User`, `Code`, `Session`
- Invite activation: `Invite`, `User`, `Code`, `Session`
- Intro + moderation: `User`, `Post` (intro), `Geo`
- Feed + post view: `Post`, `PostView`, `Room`, `Tag`
- Comments + reactions: `Comment`, `CommentVote`, `Post`, `PostVote`
- Bookmarks + subscriptions: `PostBookmark`, `PostSubscription`
- Rooms/chats: `Room`, `RoomSubscription`, `RoomMuted`
- Notifications: `User` (telegram fields), `WebhookEvent`

## 🧩 View functions (full index, inputs/outputs)

### authn/views/auth.py

- `join(request)` — Input: `POST email, invite_code, iconsent`; Output: create/verify user, send code, render email screen.
- `login(request)` — Input: `GET goto,email`; Output: login form.
- `logout(request)` — Input: auth cookie; Output: session deletion + redirect.

### authn/views/email.py

- `email_login(request)` — Input: `POST email_or_login, goto`; Output: send code + email screen.
- `email_login_code(request)` — Input: `GET email, code, goto`; Output: session cookie + redirect.

### authn/views/debug.py

- `debug_dev_login(request)` — Input: dev only; Output: admin session + redirect.
- `debug_random_login(request)` — Input: none; Output: random user session + redirect.
- `debug_login(request, user_slug)` — Input: slug; Output: session + redirect.

### users/views/profile.py

- `profile(request, user_slug)` — Input: slug; Output: profile page.
- `profile_comments(request, user_slug)` — Input: slug; Output: profile comments tab.
- `profile_posts(request, user_slug)` — Input: slug; Output: profile posts tab.
- `profile_badges(request, user_slug)` — Input: slug; Output: profile badges tab.
- `toggle_tag(request, tag_code)` — Input: POST tag; Output: JSON tag toggle.

### users/views/intro.py

- `intro(request)` — Input: intro form; Output: create intro post + status to `on_review`.

### users/views/settings.py

- `profile_settings(request, user_slug)` — Input: slug; Output: settings root.
- `edit_profile(request, user_slug)` — Input: profile form; Output: saved profile.
- `edit_account(request, user_slug)` — Input: account form; Output: saved account.
- `edit_notifications(request, user_slug)` — Input: notification form; Output: saved prefs.
- `edit_bot(request, user_slug)` — Input: bot settings; Output: saved bot links.

### users/views/friends.py

- `api_friend(request, user_slug)` — Input: POST friend/unfriend; Output: JSON state.
- `friends(request, user_slug)` — Input: slug; Output: friends list.

### users/views/muted.py

- `toggle_mute(request, user_slug)` — Input: POST mute/unmute; Output: JSON state.
- `muted(request, user_slug)` — Input: slug; Output: muted list.

### users/views/notes.py

- `edit_note(request, user_slug)` — Input: POST note; Output: saved note + redirect.

### users/views/people.py

- `people(request)` — Input: filters; Output: people directory.

### users/views/messages.py

- `on_review(request)` — Input: none; Output: “on review” page.
- `rejected(request)` — Input: none; Output: rejection page.
- `banned(request)` — Input: none; Output: ban page.

### posts/views/feed.py

- `feed(request, post_type=..., room_slug=None, label_code=None, ordering=..., ordering_param=None)` — Input: filters; Output: feed list.

### posts/views/posts.py

- `show_post(request, post_type, post_slug)` — Input: slug + type; Output: post page.
- `unpublish_post(request, post_slug)` — Input: slug; Output: mark hidden + redirect.
- `clear_post(request, post_slug)` — Input: slug; Output: clear content + redirect.
- `delete_post(request, post_slug)` — Input: slug; Output: delete + redirect.
- `compose(request)` — Input: GET/POST; Output: compose form or redirect.
- `compose_type(request, post_type)` — Input: type; Output: compose form.
- `edit_post(request, post_slug)` — Input: slug; Output: edit form.
- `create_or_edit(request, post_type, post=None, mode="create")` — Input: form; Output: create/update + redirect.

### posts/views/api.py

- `toggle_post_bookmark(request, post_slug)` — Input: POST; Output: JSON bookmarked state.
- `upvote_post(request, post_slug)` — Input: POST; Output: JSON vote counts.
- `retract_post_vote(request, post_slug)` — Input: POST; Output: JSON vote counts.
- `toggle_post_subscription(request, post_slug)` — Input: POST; Output: JSON subscription state.
- `toggle_post_event_participation(request, post_slug)` — Input: POST; Output: JSON RSVP state.

### comments/views.py

- `create_comment(request, post_slug)` — Input: POST; Output: render/redirect.
- `show_comment(request, post_slug, comment_id)` — Input: ids; Output: comment page.
- `edit_comment(request, comment_id)` — Input: POST; Output: redirect/JSON.
- `delete_comment(request, comment_id)` — Input: POST; Output: redirect/JSON.
- `delete_comment_thread(request, comment_id)` — Input: POST; Output: redirect.
- `pin_comment(request, comment_id)` — Input: POST; Output: redirect.
- `upvote_comment(request, comment_id)` — Input: POST; Output: JSON counts.
- `retract_comment_vote(request, comment_id)` — Input: POST; Output: JSON counts.

### invites/views.py

- `list_invites(request)` — Input: auth user; Output: invite list.
- `show_invite(request, invite_code)` — Input: code; Output: invite details.
- `activate_invite(request, invite_code)` — Input: code + email; Output: login session.
- `godmode_generate_invite_code(request)` — Input: POST; Output: new invite JSON.
- `create_invite(request)` — Input: POST; Output: invite + redirect.

### notifications/views.py

- `email_confirm(request, secret, legacy_code=None)` — Input: secret; Output: confirm email.
- `email_unsubscribe(request, user_id, secret)` — Input: secret; Output: unsubscribe.
- `email_digest_switch(request, digest_type, user_id, secret)` — Input: secret; Output: toggle digest.
- `render_weekly_digest(request)` — Input: debug; Output: digest preview.
- `link_telegram(request)` — Input: signed payload; Output: link Telegram.
- `is_valid_telegram_data(data, bot_token)` — Input: payload; Output: bool.

### rooms/views.py

- `list_rooms(request)` — Input: none; Output: rooms list.
- `redirect_to_room_chat(request, room_slug)` — Input: slug; Output: redirect to chat.
- `toggle_room_subscription(request, room_slug)` — Input: POST; Output: JSON state.
- `toggle_room_mute(request, room_slug)` — Input: POST; Output: JSON state.

### search/views.py

- `search(request)` — Input: query + filters; Output: search results.

### misc/views.py

- `stats(request)` — Input: none; Output: stats page.
- `crew(request)` — Input: none; Output: crew page.
- `write_to_crew(request, crew)` — Input: form; Output: send message.
- `show_achievement(request, achievement_code)` — Input: code; Output: achievement page.
- `network(request)` — Input: none; Output: network page.
- `robots(request)` — Input: none; Output: robots.txt.
- `generate_ical_invite(request)` — Input: event data; Output: ICS file.
- `generate_google_invite(request)` — Input: event data; Output: Google URL.

### landing/views.py

- `landing(request)` — Input: none; Output: landing page.

### badges/views.py

- `create_badge_for_post(request, post_slug)` — Input: POST; Output: badge created.
- `create_badge_for_comment(request, comment_id)` — Input: POST; Output: badge created.

### bookmarks/views.py

- `bookmarks(request)` — Input: auth user; Output: bookmark list.

### tags/views.py

- No public view functions (placeholder).

### clickers/api.py

- `api_clicker(request, clicker_id)` — Input: POST click; Output: JSON counter.

### godmode/views/main.py

- `godmode(request)` — Input: auth admin; Output: admin home.
- `godmode_list_model(request, model_name)` — Input: model; Output: list.
- `godmode_edit_model(request, model_name, item_id)` — Input: model + id; Output: edit form.
- `godmode_delete_model(request, model_name, item_id)` — Input: model + id; Output: delete + redirect.
- `godmode_create_model(request, model_name)` — Input: model; Output: create form.
- `godmode_show_page(request, page_name)` — Input: page; Output: admin page.
- `godmode_action(request, model_name, item_id, action_code)` — Input: action; Output: action result.

## 🧠 Data flow into templates / JS

### Feed rendering

- `posts/views/feed.py` loads posts list.
- `posts/renderers.py` attaches derived fields: upvotes, subscription state, user badges, etc.
- Templates: `frontend/html/feed.html` + `frontend/html/posts/items/*.html`.

### Post page

- `posts/views/posts.py::show_post` gets post + comments.
- `posts/renderers.py` prepares comment list with upvote state.
- Templates: `frontend/html/posts/show/*.html` + `frontend/html/comments/types/*.html`.

### Profile

- `users/views/profile.py` composes user, tags, stats.
- Templates: `frontend/html/users/profile*.html` + `frontend/html/users/widgets/*`.

### JS components (AJAX actions)

- `frontend/static/js/common/api.service.js`  
  Adds CSRF + `fetch` wrappers for POST/GET.
- `PostUpvote.vue` → calls `posts/views/api.py::upvote_post`.
- `CommentUpvote.vue` → calls comment upvote endpoints.
- `PostBookmark.vue` → calls `toggle_post_bookmark`.
- `PostRSVP.vue` → calls `toggle_post_event_participation`.
- `UserTag.vue` → calls `users/views/profile.py::toggle_tag`.

Create a Django superuser (optional):

```sh
docker compose exec club_app python3 manage.py createsuperuser
```

### ✅ Local/Dev checklist

1. `.env` создан в корне репозитория (в `.gitignore`)
2. `docker compose up --build` завершился без ошибок
3. `http://127.0.0.1:8000/` открывается
4. `/join/` ведет на форму без оплаты
5. `EMAIL_BACKEND` настроен (console локально; Resend/Brevo через HTTP API в проде — SMTP на Railway заблокирован)
6. Telegram URL‑ы заданы полными ссылками (`https://t.me/...`) если боты нужны
7. Боты запущены только если заданы токены

## 🧩 Docker compose profiles

Quick comparison:

1. `docker-compose.yml` (dev/local)
   - Services: app, queue, postgres, redis, webpack
   - Hot-reload via `${PWD}:/app`
   - Runs on `:8000`
2. `docker-compose.production.yml` (prod/server)
   - Services: club_app, queue (also runs scheduled tasks), redis, optional bots
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
   - `TELEGRAM_BOT_URL` (public bot link, full URL like `https://t.me/your_bot`)
2. For helpdesk bot (optional):
   - `TELEGRAM_HELP_DESK_BOT_TOKEN`
   - `TELEGRAM_HELP_DESK_BOT_QUESTION_CHANNEL_ID`
   - `TELEGRAM_HELP_DESK_BOT_QUESTION_CHANNEL_DISCUSSION_ID`
3. Start the bot containers:

```sh
docker compose up --build bot helpdeskbot
```

If you see “relation rooms does not exist” on first boot, restart helpdeskbot after migrations finish:

```sh
docker compose restart helpdeskbot
```

## ✉️ Настройка отправки почты

Коды входа и уведомления отправляются через бэкенд, заданный в `EMAIL_BACKEND`. Код отправки backend‑агностичен (`send_mail` / `EmailMultiAlternatives` в `notifications/email/sender.py`), так что провайдер меняется только переменными окружения. Ключи провайдеров читаются в `club/settings.py → ANYMAIL`.

**Локально** ничего настраивать не нужно — письма печатаются в консоль:
```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

**Прод (Railway).** ⚠️ Railway блокирует исходящий SMTP, поэтому Gmail/SMTP не работает — нужен HTTP API через `django-anymail`.

Resend (рекомендуется, бесплатный тариф):
```
EMAIL_BACKEND=anymail.backends.resend.EmailBackend
RESEND_API_KEY=<ключ из Resend → API Keys>
DEFAULT_FROM_EMAIL=Сообщество выпускников РЭШ <no-reply@yourdomain.com>
```
Перед отправкой подтверди домен в **Resend → Domains** (добавь DNS‑записи SPF/DKIM); адрес в `DEFAULT_FROM_EMAIL` должен быть на этом домене.

Brevo — альтернатива (тоже HTTP API):
```
EMAIL_BACKEND=anymail.backends.brevo.EmailBackend
BREVO_API_KEY=<ключ из Brevo → SMTP & API → API Keys>
DEFAULT_FROM_EMAIL=Сообщество выпускников РЭШ <no-reply@yourdomain.com>
```

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
   - `EMAIL_BACKEND`, plus the matching provider key (`RESEND_API_KEY` or `BREVO_API_KEY`), `DEFAULT_FROM_EMAIL` (see “Настройка отправки почты”)
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
docker compose -f docker-compose.production.yml up -d bot helpdeskbot queue
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
   - Store backups encrypted and test restore monthly

### ✅ Deployment checklist

1. DNS
   - `APP_HOST` соответствует домену (например, `https://test.ru`)
   - A/AAAA записи указывают на сервер
2. `.env` на сервере
   - Заполнены `POSTGRES_HOST/DB/USER/PASSWORD`
   - Заполнены email‑переменные (`EMAIL_BACKEND` + `RESEND_API_KEY`/`BREVO_API_KEY` + `DEFAULT_FROM_EMAIL`)
   - `SECRET_KEY` установлен
3. Docker images
   - Указан `CLUB_IMAGE` или доступна сборка из репозитория
4. Migrations
   - После обновления кода: `docker compose -f docker-compose.production.yml up -d`
5. Webhooks (если используются)
   - `/telegram/webhook/` доступен по `APP_HOST`
6. Smoke check
   - `GET /` возвращает 200
   - Авторизация через email работает
7. GitHub Actions
   - `TOKEN` с правами `write:packages`
   - `PRODUCTION_SSH_HOST`, `PRODUCTION_SSH_USERNAME`, `PRODUCTION_SSH_KEY`
   - Секреты приложения: `SECRET_KEY`, `APP_HOST`, `POSTGRES_PASSWORD`, `RESEND_API_KEY` (или `BREVO_API_KEY`)
   - Опционально: `MEDIA_UPLOAD_URL`, `MEDIA_UPLOAD_CODE`, `SENTRY_DSN`, `TELEGRAM_*`

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
- `EMAIL_BACKEND` + `RESEND_API_KEY` (или `BREVO_API_KEY`) + `DEFAULT_FROM_EMAIL`

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
