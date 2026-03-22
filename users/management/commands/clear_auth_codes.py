from django.core.management.base import BaseCommand

from authn.models.session import Code


class Command(BaseCommand):
    help = "Clear auth codes for an email to reset rate limit. Usage: manage.py clear_auth_codes --email you@example.com"

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)

    def handle(self, *args, **options):
        email = options["email"].lower()
        deleted, _ = Code.objects.filter(recipient=email).delete()
        self.stdout.write(f"Deleted {deleted} auth codes for {email}")
