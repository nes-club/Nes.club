# tags — User Categorization

User tags for discovery and filtering in the alumni directory.

## Models

| Model | Purpose |
|-------|---------|
| `Tag` | Tag catalog: `code`, `group`, `name` |
| `UserTag` | User-selected tag with visibility setting |

## Tag Groups

`personal`, `tech`, `hobbies`, `club`, `collectible`, `other`

## Tag Colors

No `color` field — color is computed deterministically from hash of `code`. Same tag always gets the same color.

## Usage

- Users select tags on their profile settings page
- `/people/` page aggregates tags with user counts for filtering
- Tags are used for discovery: "find all members interested in economics"

## Visibility

Each `UserTag` has a visibility setting so users can hide certain tags from their public profile.
