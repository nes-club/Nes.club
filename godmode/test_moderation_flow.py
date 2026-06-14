from django.test import TestCase, Client, override_settings

from authn.models.session import Session
from posts.models.post import Post
from users.models.user import User


@override_settings(TELEGRAM_TOKEN=None)  # keep notifications as no-ops during the test
class ModerationFlowTest(TestCase):
    def setUp(self):
        self.moderator = User.objects.create(
            slug="mod", email="mod@nes.ru", full_name="Mod",
            moderation_status=User.MODERATION_STATUS_APPROVED, roles=[User.ROLE_GOD],
        )
        session = Session.create_for_user(self.moderator)
        self.client = Client()
        self.client.cookies["token"] = session.token

    def _make_newbie(self, slug="newbie"):
        newbie = User.objects.create(
            slug=slug, email=f"{slug}@nes.ru", full_name="Newbie",
            moderation_status=User.MODERATION_STATUS_ON_REVIEW,
        )
        intro = Post.objects.create(
            author=newbie, type=Post.TYPE_INTRO, slug=f"{slug}-intro",
            title="#intro", text="hello world", visibility=Post.VISIBILITY_DRAFT,
            moderation_status=Post.MODERATION_PENDING,
        )
        return newbie, intro

    def _make_post(self, slug="p1"):
        author = User.objects.create(
            slug=f"author-{slug}", email=f"author-{slug}@nes.ru",
            moderation_status=User.MODERATION_STATUS_APPROVED,
        )
        return Post.objects.create(
            author=author, type=Post.TYPE_POST, slug=slug, title="title", text="body",
            visibility=Post.VISIBILITY_DRAFT, moderation_status=Post.MODERATION_PENDING,
        )

    def test_approve_intro_user_publishes_intro(self):
        newbie, intro = self._make_newbie()
        resp = self.client.post(f"/godmode/users/{newbie.id}/action/approve/")
        self.assertEqual(resp.status_code, 200)

        newbie.refresh_from_db()
        intro.refresh_from_db()
        self.assertEqual(newbie.moderation_status, User.MODERATION_STATUS_APPROVED)
        self.assertEqual(intro.moderation_status, Post.MODERATION_APPROVED)
        self.assertEqual(intro.visibility, Post.VISIBILITY_EVERYWHERE)
        self.assertIsNotNone(intro.published_at)

    def test_reject_intro_user(self):
        newbie, _ = self._make_newbie(slug="rejectme")
        resp = self.client.post(f"/godmode/users/{newbie.id}/action/reject/")
        self.assertEqual(resp.status_code, 200)

        newbie.refresh_from_db()
        self.assertEqual(newbie.moderation_status, User.MODERATION_STATUS_REJECTED)

    def test_approve_post(self):
        post = self._make_post(slug="approve-me")
        resp = self.client.post(f"/godmode/posts/{post.id}/action/approve/")
        self.assertEqual(resp.status_code, 200)

        post.refresh_from_db()
        self.assertEqual(post.moderation_status, Post.MODERATION_APPROVED)
        self.assertEqual(post.visibility, Post.VISIBILITY_EVERYWHERE)

    def test_reject_post(self):
        post = self._make_post(slug="reject-me")
        resp = self.client.post(f"/godmode/posts/{post.id}/action/reject/")
        self.assertEqual(resp.status_code, 200)

        post.refresh_from_db()
        self.assertEqual(post.moderation_status, Post.MODERATION_REJECTED)
        self.assertEqual(post.visibility, Post.VISIBILITY_DRAFT)

    def test_double_approve_is_idempotent(self):
        newbie, _ = self._make_newbie(slug="twice")
        self.client.post(f"/godmode/users/{newbie.id}/action/approve/")
        resp = self.client.post(f"/godmode/users/{newbie.id}/action/approve/")
        self.assertEqual(resp.status_code, 200)  # "already approved" message, no crash
        newbie.refresh_from_db()
        self.assertEqual(newbie.moderation_status, User.MODERATION_STATUS_APPROVED)

    def test_non_moderator_cannot_approve(self):
        plain = User.objects.create(
            slug="plain", email="plain@nes.ru",
            moderation_status=User.MODERATION_STATUS_APPROVED, roles=[],
        )
        session = Session.create_for_user(plain)
        attacker = Client()
        attacker.cookies["token"] = session.token

        newbie, _ = self._make_newbie(slug="victim")
        attacker.post(f"/godmode/users/{newbie.id}/action/approve/")

        newbie.refresh_from_db()
        # state must be unchanged — non-moderator has no godmode access
        self.assertEqual(newbie.moderation_status, User.MODERATION_STATUS_ON_REVIEW)
