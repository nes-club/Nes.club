import logging
import os
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management import BaseCommand

log = logging.getLogger(__name__)

MAX_AGE_DAYS = 3


class Command(BaseCommand):
    help = "Delete GDPR download archives older than 3 days"

    def handle(self, *args, **options):
        downloads_dir = settings.GDPR_ARCHIVE_STORAGE_PATH
        if not os.path.isdir(downloads_dir):
            self.stdout.write(f"Directory {downloads_dir} does not exist, skipping")
            return

        cutoff = datetime.utcnow() - timedelta(days=MAX_AGE_DAYS)
        deleted = 0

        for filename in os.listdir(downloads_dir):
            filepath = os.path.join(downloads_dir, filename)
            if not os.path.isfile(filepath):
                continue
            mtime = datetime.utcfromtimestamp(os.path.getmtime(filepath))
            if mtime < cutoff:
                os.remove(filepath)
                deleted += 1
                log.info(f"Deleted old GDPR archive: {filename}")

        self.stdout.write(f"Deleted {deleted} old GDPR archive(s). Done 🥙")
