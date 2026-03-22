# godmode — Admin Panel

Internal admin interface for moderation, bulk actions, digest management, and site configuration.

## Access Control

- `god` role — full access
- `moderator` role — moderation queue, user/post actions
- `curator` role — read-only view

Roles stored as `ArrayField` on `User.roles`.

## Key Pages

| URL | Purpose |
|-----|---------|
| `/godmode/` | Dashboard |
| `/godmode/moderation/` | Moderation queue (pending posts + intro users) |
| `/godmode/compose_weekly_digest/` | Preview and send weekly digest |
| `/godmode/mass_email/` | Broadcast email to all members |
| `/godmode/badge_generator/` | Create/manage badge types |
| `/godmode/invite_user_by_email/` | Send invite by email |
| `/godmode/achievements/` | Manage achievement catalog |

## Bulk Actions

`godmode/actions/` — handlers for:
- Ban / unban users
- Delete / restore posts
- Assign / remove roles
- Award hats (cosmetic profile items)
- Force moderation status transitions

All bulk actions are transactional (atomic).

## Models

`ClubSettings` — key/value store for site-wide settings. Get/set via:
```python
ClubSettings.get("digest_title")
ClubSettings.set("digest_title", "Some title")
```
