from datetime import datetime

from django.test import TestCase

from badges.models import Badge, UserBadge
from users.models.user import User


class BadgeFreeTest(TestCase):
    def setUp(self):
        now = datetime.utcnow()
        self.badge = Badge.objects.create(code="test_badge", title="Test")
        self.user1 = User.objects.create(
            email="giver@nes.ru",
            slug="giver",
            membership_started_at=now,
            membership_expires_at=now,
        )
        self.user2 = User.objects.create(
            email="receiver@nes.ru",
            slug="receiver",
            membership_started_at=now,
            membership_expires_at=now,
        )

    def test_badge_has_no_price(self):
        self.assertFalse(hasattr(Badge(), "price_days"))

    def test_create_badge_does_not_deduct_balance(self):
        expires_before = self.user1.membership_expires_at
        UserBadge.create_user_badge(
            badge=self.badge,
            from_user=self.user1,
            to_user=self.user2,
            post=None,
            comment=None,
        )
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.membership_expires_at, expires_before)
