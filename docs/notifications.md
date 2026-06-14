# notifications — Email & Telegram

The weekly digest, transactional emails, and Telegram notifications.

## Email delivery

Sending is backend-agnostic (`email/sender.py` uses Django `send_mail` / `EmailMultiAlternatives`); the provider is chosen via `EMAIL_BACKEND`. Railway blocks outbound SMTP, so production uses an HTTP API via `django-anymail`:

- **Resend** (recommended, free tier): `EMAIL_BACKEND=anymail.backends.resend.EmailBackend` + `RESEND_API_KEY`
- **Brevo** (alternative): `EMAIL_BACKEND=anymail.backends.brevo.EmailBackend` + `BREVO_API_KEY`
- **Local**: `django.core.mail.backends.console.EmailBackend` (prints to console)

Provider keys are read in `club/settings.py → ANYMAIL`. `DEFAULT_FROM_EMAIL` must use a domain verified with the provider.

## Email Digest (weekly only)

The daily digest has been removed — only the weekly digest remains.

- Management command: `send_weekly_digest`
- Scheduled: Mondays 10:00 (via django-q2 Schedule)
- Content: top posts, hot comments, upcoming events, community stats
- Saves result as `Post(type=weekly_digest)` for the homepage
- Sends email to: `is_email_verified=True`, not unsubscribed
- Sends Telegram DM to users with `telegram_id` linked
- Sends channel announcement (production only)

## Transactional Emails

| Module | Emails |
|--------|--------|
| `email/users.py` | Auth OTP codes, welcome emails |
| `email/badges.py` | Badge received notifications |
| `email/achievements.py` | Achievement unlocked |
| `email/invites.py` | Invite email to new users |

## Telegram Notifications

- `telegram/posts.py` — new post notifications to subscribers and rooms
- `telegram/common.py` — `send_telegram_message()`, `render_html_message()`, Chat/CLUB_CHANNEL helpers
- `telegram/common.py` — shared helpers for all Telegram notifications

## Email Unsubscribe & Bounce Handling

- `GET /notifications/unsubscribe/<user_id>/<secret_code>/` — one-click unsubscribe
- `POST /notifications/webhooks/ses/` — SES bounce/complaint processing
  - Stores `WebhookEvent` and sets `is_email_unsubscribed = True` on complaints

## Models

| Model | Purpose |
|-------|---------|
| `WebhookEvent` | Stores SES bounce/complaint events |

## Digest User Preferences

Controlled by `user.email_digest_type`:
- `nope` — no emails
- `weekly` — weekly digest (default)

(Legacy `daily` links redirect to `weekly`.)
