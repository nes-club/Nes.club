# authn — Authentication

Email OTP login, session management, and OAuth2/OIDC provider for third-party integrations.

## Entry Points

- `GET/POST /auth/` — main join/login flow (`views/auth.py`)
- `POST /auth/email/` → send OTP code
- `GET /auth/email/code/` → verify OTP, create session
- `GET/POST /openid/authorize/` — OAuth2 authorization endpoint
- `POST /openid/token/` — token exchange
- `GET /.well-known/openid-configuration` — OIDC discovery

## Models

| Model | Purpose |
|-------|---------|
| `Session` | Auth token stored in cookie; expires when membership ends |
| `Code` | One-time login code (6-char, max 3 attempts, rate-limited) |
| `OAuth2App` | Registered third-party apps (client_id, secret, redirect URIs) |
| `OAuth2Token` | Issued access/refresh tokens |
| `OAuth2AuthorizationCode` | Short-lived authorization codes |

## NES Access Gate

`views/auth.py` validates that the email domain is `@nes.ru` **or** that a valid invite code is provided. Both paths are required for entry; see `authn/views/auth.py` for the exact check.

## Session Lifetime

`Session.create_for_user()` sets expiry based on `membership_expires_at`. Non-members get a short session. Middleware (`club/middleware.py`) injects `request.me` on every request.

## External Dependencies

- `authlib` — OAuth2/OIDC implementation
- `django-q2` — async OTP email dispatch
