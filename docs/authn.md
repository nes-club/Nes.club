# authn — Authentication

Email one-time-code login and session management. No passwords, no OAuth/OpenID, no social login.

## Entry Points

- `GET/POST /join/` — registration (`views/auth.py::join`)
- `GET/POST /auth/login/` — login (`views/auth.py::login`)
- `POST /auth/email/` → send one-time code (`views/email.py::email_login`)
- `GET /auth/email/code/` → verify code, create session (`views/email.py::email_login_code`)
- `/godmode/dev_login/`, `/godmode/random_login/` — dev only (`views/debug.py`, disabled when `DEBUG=false`)

## Models

| Model | Purpose |
|-------|---------|
| `Session` | Auth token stored in the `token` cookie (1-year expiry) |
| `Code` | One-time login code (6-char, max 3 attempts, rate-limited) |

## NES Access Gate

`views/auth.py` validates that the email domain is `@nes.ru` **or** that a valid invite code is provided. See `authn/views/auth.py` for the exact check.

## Session Lifetime

`Session.create_for_user()` issues a long-lived session (access is perpetual — no paid membership). Middleware (`club/middleware.py`) injects `request.me` on every request via the `token` cookie.

## External Dependencies

- `django-q2` — async one-time-code email dispatch
- email delivery via `django-anymail` (Resend / Brevo — see `docs/notifications.md`)
