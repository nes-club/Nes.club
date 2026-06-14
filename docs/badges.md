# badges — User Recognition

User-to-user badge gifting system. **Badges are free** — there is no cost/currency (the old `price_days` charge and the paid-membership model were removed).

## Models

| Model | Purpose |
|-------|---------|
| `Badge` | Badge catalog: `code`, `title` |
| `UserBadge` | Badge instance: `from_user` → `to_user`, linked to a post or comment |

## Flow

1. User visits a post/comment
2. Clicks "give badge" → selects badge type
3. `UserBadge` created (free, atomic transaction)
4. Notification sent to recipient

## Constraints

- Cannot badge yourself
- One badge per type per post/comment (integrity constraint)
- "Thanks" badge is for intro posts only
- Cached in `post.metadata["badges"]` / `comment.metadata["badges"]` for display performance

## Badge Display

Badge counts shown on post/comment cards via cached metadata. Full badge list visible on user profile.
