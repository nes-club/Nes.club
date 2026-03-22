# users — User Profiles & Access Control

Core user model, onboarding flow, roles, membership, friends/mutes, achievements, geographic map.

## Onboarding Flow

```
New user → /intro/ (UserInitialIntroForm)
  → Post(type="intro") created → moderation_status = "on_review"
  → Moderator approves → moderation_status = "approved"
  → Full access granted
```

## Key Models

| Model | Purpose |
|-------|---------|
| `User` | Central model: roles, membership, moderation status, Telegram link |
| `Friend` | Bidirectional friend relationships |
| `UserMuted` | Block/mute another user |
| `UserNote` | Private moderator notes on a user |
| `Achievement` | Achievement catalog (gamification) |
| `UserAchievement` | Progress per user |

## User.moderation_status Lifecycle

`intro` → `on_review` → `approved` / `rejected` / `deleted`

Only `approved` users with non-expired membership have full access (`is_member` property).

## Roles (ArrayField)

| Role | Permissions |
|------|------------|
| `god` | Full access to everything |
| `moderator` | Approve/reject posts and users |
| `curator` | View-only admin |
| `bank` | Manage badges |

## NES-Specific Fields

| Field | Purpose |
|-------|---------|
| `year_of_graduation` | Year user graduated from РЭШ (PositiveSmallIntegerField) |
| `faculty` | Program/faculty name (e.g. "Магистр экономики") |

Both fields are shown in `users/forms/intro.py` and the intro HTML template.

## Profile Publicity Levels

- `private` — only the user sees their full profile
- `normal` — members see the profile
- `public` — visible to unauthenticated visitors

## Key Views

- `views/intro.py` — intro form submission
- `views/profile.py` — public profile, achievements, post history
- `views/settings.py` — edit profile, email prefs, Telegram linking
- `views/people.py` — alumni directory with tags and map

## Membership

`is_active_member = is_member AND membership_expires_at >= now()`

For alumni portal: membership is granted for a long term at registration (no payment required). Badge gifting deducts days from `membership_expires_at`.
