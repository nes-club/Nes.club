# club — Django Project Core

Django project settings, URL routing, middleware, scheduled tasks, and feature flags.

## Key Files

| File | Purpose |
|------|---------|
| `settings.py` | All configuration: DB, cache, apps, email, Telegram |
| `urls.py` | 80+ URL routes for all apps |
| `middleware.py` | Session extraction, `request.me` injection, exception handling |
| `features.py` | Feature flags (`PRIVATE_FEED`, etc.) |
| `context_processors.py` | Inject `settings`, `features`, `me` into all templates |
| `tasks.py` | django-q2 task wrapper functions (14 tasks) |
| `management/commands/setup_schedules.py` | Idempotent Schedule setup |
| `exceptions.py` | `NotFound`, `Forbidden`, `AccessDenied` etc. |

## Scheduled Tasks (`club/tasks.py`)

All tasks call `management.call_command()` internally. Set up via:
```
python manage.py setup_schedules
```

The current schedule (source of truth: `club/management/commands/setup_schedules.py`):

| Task function | Schedule (cron) | Command |
|--------------|----------|---------|
| `run_notify_expired_intros` | Tue 13:00 | `notify_expired_intros` |
| `run_send_weekly_digest` | Mon 10:00 | `send_weekly_digest` |
| `run_cleanup_post_views` | Sat 02:00 | `cleanup_post_views` |
| `run_rebuild_search_index` | Sun 02:00 | `rebuild_search_index` (incremental) |
| `run_replay_pending_moderation` | Every 6h at :20 | `replay_pending_moderation_posts` |
| `run_update_hotness` | Every 6h at :13 | `update_hotness` |
| `run_promote_old_post` | Wed & Sat 07:00 | `promote_one_old_post_on_main` |

## Middleware

`club/middleware.py` runs on every request:
1. Extracts session from cookie → finds `User`
2. Sets `request.me` (User or None)
3. Updates `last_activity_at` (throttled, max once per 5 min)
4. Catches `NotFound`/`Forbidden` → renders 404/403

## Feature Flags (`club/features.py`)

- `PRIVATE_FEED` — hide feed from unauthenticated users; show landing page instead
- Injected into templates via context processor

## Models

`ClubSettings` — key/value store for site-wide configuration (editable in godmode admin). Used for: digest title/intro, feature overrides.
