from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from users.models.user import User


class Command(BaseCommand):
    help = "Create initial admin user. Usage: manage.py create_admin --email you@example.com --slug admin --name 'Your Name'"

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--slug", default="admin")
        parser.add_argument("--name", default="Admin")

    def handle(self, *args, **options):
        email = options["email"]
        slug = options["slug"]
        name = options["name"]

        if User.objects.filter(email=email).exists():
            self.stdout.write(f"User with email {email} already exists")
            return

        if User.objects.filter(slug=slug).exists():
            self.stdout.write(f"User with slug '{slug}' already exists, using slug '{slug}2'")
            slug = slug + "2"

        User.objects.create(
            slug=slug,
            email=email,
            full_name=name,
            moderation_status="approved",
            roles=["god"],
            membership_started_at=datetime.utcnow(),
            membership_expires_at=datetime.utcnow() + timedelta(days=365 * 10),
            balance=10000,
            is_email_verified=True,
        )
        self.stdout.write(f"Admin user created: {email} (slug: {slug})")
