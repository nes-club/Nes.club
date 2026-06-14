from django.test import TestCase

from badges.models import Badge, UserBadge
from posts.models.post import Post
from users.models.user import User


class BadgeFreeTest(TestCase):
    def setUp(self):
        self.badge = Badge.objects.create(code="test_badge", title="Test")
        self.giver = User.objects.create(email="giver@nes.ru", slug="giver")
        self.receiver = User.objects.create(email="receiver@nes.ru", slug="receiver")
        self.post = Post.objects.create(
            author=self.receiver, type=Post.TYPE_POST, slug="badge-post",
            title="title", text="body", visibility=Post.VISIBILITY_EVERYWHERE,
        )

    def test_badge_has_no_price(self):
        self.assertFalse(hasattr(Badge(), "price_days"))

    def test_create_badge_is_free(self):
        # badges are free — giving one just creates the UserBadge, with no balance/membership to charge
        user_badge = UserBadge.create_user_badge(
            badge=self.badge, from_user=self.giver, to_user=self.receiver, post=self.post,
        )
        self.assertIsNotNone(user_badge)
        self.assertTrue(
            UserBadge.objects.filter(from_user=self.giver, to_user=self.receiver).exists()
        )
        # the paid-membership model is gone entirely — nothing to deduct
        self.assertFalse(hasattr(self.giver, "membership_expires_at"))
        self.assertFalse(hasattr(self.giver, "balance"))
