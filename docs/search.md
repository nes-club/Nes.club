# search — Full-Text Search

PostgreSQL full-text search across posts, comments, and user profiles with Russian language support.

## Model

`SearchIndex` — denormalized table with `SearchVectorField` (GIN index).

| Field | Weight | Source |
|-------|--------|--------|
| `title` | A (highest) | Post title |
| `text` | B | Post/comment body |
| `author` | C | User full_name / slug |
| `room` | C | Room name |

## Indexing

Updated on save via Django signals in `search/models.py`. Also rebuilt daily by `rebuild_search_index` management command.

Both simple and Russian-stemmed (`russian` text search config) vectors are stored.
Rank combines both with a multiplier to balance simple vs. stemmed relevance.

## Query Flow

1. `GET /search/?q=query`
2. Tokenized and searched against both vectors
3. Results filtered by minimum rank threshold
4. Ranked by weighted score + recency

## Language Support

PostgreSQL `russian` text search configuration handles Russian morphology (stemming). Ensures searches for "экономик" match "экономика", "экономического", etc.
