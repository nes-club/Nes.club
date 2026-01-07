#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/backup_postgres.sh /path/to/backup/dir
#
# Required env vars:
#   POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
#
# Optional env vars:
#   BACKUP_PREFIX (default: nes_club)
#   BACKUP_KEEP_DAYS (default: 14)

BACKUP_DIR="${1:-}"
if [ -z "$BACKUP_DIR" ]; then
  echo "Usage: $0 /path/to/backup/dir" >&2
  exit 1
fi

if [ -z "${POSTGRES_HOST:-}" ] || [ -z "${POSTGRES_DB:-}" ] || [ -z "${POSTGRES_USER:-}" ] || [ -z "${POSTGRES_PASSWORD:-}" ]; then
  echo "Missing required env vars: POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD" >&2
  exit 1
fi

BACKUP_PREFIX="${BACKUP_PREFIX:-nes_club}"
BACKUP_KEEP_DAYS="${BACKUP_KEEP_DAYS:-14}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILE="${BACKUP_DIR}/${BACKUP_PREFIX}_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

export PGPASSWORD="$POSTGRES_PASSWORD"
pg_dump -h "$POSTGRES_HOST" -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$BACKUP_FILE"
unset PGPASSWORD

# Rotate old backups
find "$BACKUP_DIR" -type f -name "${BACKUP_PREFIX}_*.sql.gz" -mtime "+${BACKUP_KEEP_DAYS}" -delete

echo "Backup saved to: $BACKUP_FILE"
