# invites — Invite Codes

Private community access via one-time invite codes.

## Model

`Invite`:
- `code` — 14-char random alphanumeric string
- `user` — creator of the invite
- `invited_email` — optional email pre-assigned to invite
- `invited_user` — FK to User after invite is used
- `used_at` — timestamp of activation
- Expires 365 days after creation

## Flow

1. Existing member creates invite (from `/invites/` page)
2. Gets unique code to share
3. New user visits `/join/?invite=<code>` instead of regular join
4. `authn/views/auth.py` validates invite code at registration
5. On activation: `invited_user` set, `used_at` recorded, long membership granted

## Generation

`Invite.create_for_user()` — generates code with 5-retry uniqueness check.

## Quota

Each approved member gets a configurable number of invites (`settings.INVITES_PER_USER`).
