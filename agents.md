# agents.md — NES.club Architecture Overview

NES.club is a Django 5.1 monolith alumni portal for the New Economic School (РЭШ). It is a fork of vas3k.club, adapted for alumni use. The platform combines a server-rendered Django app with embedded Vue.js 2 components (hybrid, not SPA), PostgreSQL for persistence, Redis for caching and task queue, and two Telegram bots.

---

## Component Index

| Component | Description | Docs |
|-----------|-------------|------|
| **authn** | Email OTP login, OAuth2/OIDC provider | [docs/authn.md](docs/authn.md) |
| **users** | Profiles, roles, membership, onboarding | [docs/users.md](docs/users.md) |
| **posts** | Feed, 13 post types, RSS, voting | [docs/posts.md](docs/posts.md) |
| **comments** | Nested discussions, upvotes | [docs/comments.md](docs/comments.md) |
| **notifications** | Email digests, Telegram alerts | [docs/notifications.md](docs/notifications.md) |
| **rooms** | Telegram channel directory | [docs/rooms.md](docs/rooms.md) |
| **search** | PostgreSQL full-text search (Russian) | [docs/search.md](docs/search.md) |
| **godmode** | Admin panel, moderation queue | [docs/godmode.md](docs/godmode.md) |
| **bot** | Main Telegram bot (v20, async) | [docs/bot.md](docs/bot.md) |
| **helpdeskbot** | Support Telegram bot | [docs/helpdeskbot.md](docs/helpdeskbot.md) |
| **invites** | Invite-code access | [docs/invites.md](docs/invites.md) |
| **badges** | User-to-user recognition | [docs/badges.md](docs/badges.md) |
| **tags** | User categorization/discovery | [docs/tags.md](docs/tags.md) |
| **gdpr** | Data export and account deletion | [docs/gdpr.md](docs/gdpr.md) |
| **common** | Markdown renderers, shared utilities | [docs/common.md](docs/common.md) |
| **frontend** | Vue.js 2 + Webpack 5 | [docs/frontend.md](docs/frontend.md) |
| **club** | Django project core (settings, URLs, tasks) | [docs/club.md](docs/club.md) |

---

## High-Level Architecture

```
Browser
  └── Nginx
        ├── Gunicorn (web) ──── Django views ──── PostgreSQL
        │                              │
        │                              ├── Redis (cache, sessions)
        │                              └── django-q2 (async tasks)
        │                                     └── worker (queue container)
        │
Telegram ──── bot container ──── Django ORM
         └── helpdeskbot container
```

### Request Flow
1. Request hits Django middleware: session extracted → `request.me` = User or None
2. View checks membership/moderation status, raises `Forbidden`/`NotFound` as needed
3. Template rendered with Django context + Vue components mounted client-side
4. Async side-effects (emails, Telegram notifications) dispatched to django-q2

### Background Jobs
All scheduled tasks run via django-q2 `Schedule` (CRON type). Set up with:
```
python manage.py setup_schedules
python manage.py qcluster
```
Task wrappers are in `club/tasks.py`, which call management commands.

---

## Key Domain Concepts

### Access Model
- Entry: @nes.ru email **or** invite code (validated in `authn/views/auth.py`)
- New users start at `moderation_status = "intro"`, fill intro form, go to `"on_review"`
- Moderator approves → `"approved"` → full access
- Rejected or deleted users cannot log in

### Post Types
`post`, `intro`, `link`, `question`, `idea`, `project`, `event`, `battle`, `weekly_digest`, `guide`, `thread`, `docs`, `job`

All defined in `posts/models/post.py` with `TYPE_TO_EMOJI` and `TYPE_TO_PREFIX` dicts.

### Membership
- `membership_expires_at` controls session lifetime (non-expired = active member)
- For alumni portal: membership granted at registration, long-term (bossless)
- Badge gifting costs membership days from giver

### Moderation Workflow
```
Post created → PENDING → Admin approves → APPROVED (visible)
                       → Community upvotes > threshold → APPROVED
                       → Admin rejects → REJECTED (soft-deleted)
```

### Telegram Integration
- Two bots: main (`bot/`) + helpdesk (`helpdeskbot/`)
- Both use python-telegram-bot v20 (async, Application builder pattern)
- Sync Django code calls bot via `asyncio.run()` wrapper in `notifications/telegram/bot.py`
- Bot containers run separately, connect to same DB

---

## Data Flow Examples

### New User Registration
```
GET /auth/ → email check (@nes.ru or invite)
  → OTP code sent → verified → Session created
  → Redirect to /intro/
  → POST /intro/ → UserInitialIntroForm saved
  → Post(type=intro) created → moderation queue
  → Moderator approves → user.moderation_status = "approved"
  → Welcome notifications sent
```

### Weekly Digest
```
django-q2 CRON → run_send_weekly_digest()
  → generate_weekly_digest() → HTML template
  → Post(type=weekly_digest) saved for homepage
  → Email sent to subscribers (is_email_verified, not unsubscribed)
  → Telegram DM to subscribers with telegram_id
  → Announcement to CLUB_CHANNEL (production only)
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| Framework | Django 5.1 |
| Database | PostgreSQL 14 |
| Cache / Queue broker | Redis |
| Task queue | django-q2 |
| Frontend | Vue.js 2 + Webpack 5 (hybrid, not SPA) |
| Markdown | mistune 3 with custom plugins |
| Telegram | python-telegram-bot 20.7 (async) |
| Auth | Email OTP + OAuth2/OIDC (authlib) |
| Full-text search | PostgreSQL FTS with Russian stemming |
| Containerization | Docker Compose |
| Error tracking | Sentry |

---

## NES-Specific Customizations (vs. upstream vas3k.club)

1. **@nes.ru domain gate** — `authn/views/auth.py` validates email domain
2. **`year_of_graduation` + `faculty`** — added to User model and intro form
3. **`TYPE_JOB`** — new post type for job postings
4. **Removed:** Patreon, OpenAI/GPT, crypto payments, GDAL
5. **Cron → django-q2** — cron container replaced with Schedule-based tasks
6. **python-telegram-bot 12 → 20** — full async migration
