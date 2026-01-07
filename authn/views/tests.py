from datetime import datetime, timedelta

import django
from django.test import TestCase
from django.urls import reverse
from django.http.response import HttpResponseNotAllowed, HttpResponseBadRequest
from django_q import brokers
from django_q.signing import SignedPackage

django.setup()  # todo: how to run tests from PyCharm without this workaround?

from authn.models.session import Code
from debug.helpers import HelperClient, JWT_STUB_VALUES
from users.models.user import User


class ViewsAuthTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.new_user: User = User.objects.create(
            email="testemail@xx.com",
            membership_started_at=datetime.now() - timedelta(days=5),
            membership_expires_at=datetime.now() + timedelta(days=5),
            slug="ujlbu4"
        )

    def setUp(self):
        self.client = HelperClient(user=self.new_user)

    def test_join_anonymous(self):
        response = self.client.get(reverse("join"))
        # check auth/join.html is rendered
        self.assertContains(response=response, text="Всегда рады новым членам", status_code=200)

    def test_join_authorised(self):
        self.client.authorise()

        response = self.client.get(reverse("join"))
        self.assertRedirects(response=response, expected_url=f"/user/{self.new_user.slug}/",
                             fetch_redirect_response=False)

    def test_login_anonymous(self):
        response = self.client.get(reverse("login"))
        # check auth/join.html is rendered
        self.assertContains(response=response, text="Вход по почте или нику", status_code=200)

    def test_login_authorised(self):
        self.client.authorise()

        response = self.client.get(reverse("login"))
        self.assertRedirects(response=response, expected_url=f"/user/{self.new_user.slug}/",
                             fetch_redirect_response=False)

    def test_logout_success(self):
        self.client.authorise()

        response = self.client.post(reverse("logout"))

        self.assertRedirects(response=response, expected_url=f"/", fetch_redirect_response=False)
        self.assertFalse(self.client.is_authorised())

    def test_logout_unauthorised(self):
        response = self.client.post(reverse("logout"))
        self.assertTrue(self.client.is_access_denied(response))
        self.assertFalse(self.client.is_authorised())

    def test_logout_wrong_method(self):
        self.client.authorise()

        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, HttpResponseNotAllowed.status_code)

        response = self.client.put(reverse("logout"))
        self.assertEqual(response.status_code, HttpResponseNotAllowed.status_code)

        response = self.client.delete(reverse("logout"))
        self.assertEqual(response.status_code, HttpResponseNotAllowed.status_code)

    def test_debug_dev_login_unauthorised(self):
        response = self.client.post(reverse("debug_dev_login"))
        self.assertTrue(self.client.is_authorised())

        me = self.client.print_me()
        self.assertIsNotNone(me["id"])
        self.assertEqual(me["email"], "dev@dev.dev")
        self.assertTrue(me["is_email_verified"])
        self.assertTrue(me["slug"], "dev")
        self.assertEqual(me["moderation_status"], "approved")
        self.assertEqual(me["roles"], ["god"])
        # todo: check created post (intro)

    def test_debug_dev_login_authorised(self):
        self.client.authorise()

        response = self.client.post(reverse("debug_dev_login"))
        self.assertTrue(self.client.is_authorised())

        me = self.client.print_me()
        self.assertTrue(me["slug"], self.new_user.slug)

    def test_debug_random_login_unauthorised(self):
        response = self.client.post(reverse("debug_random_login"))
        self.assertTrue(self.client.is_authorised())

        me = self.client.print_me()
        self.assertIsNotNone(me["id"])
        self.assertIn("@random.dev", me["email"])
        self.assertTrue(me["is_email_verified"])
        self.assertEqual(me["moderation_status"], "approved")
        self.assertEqual(me["roles"], [])
        # todo: check created post (intro)


class ViewEmailLoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.new_user: User = User.objects.create(
            email="testemail@xx.com",
            membership_started_at=datetime.now() - timedelta(days=5),
            membership_expires_at=datetime.now() + timedelta(days=5),
            slug="ujlbu4"
        )

        cls.broker = brokers.get_broker()
        cls.assertTrue(cls.broker.ping(), "broker is not available")

    def setUp(self):
        self.client = HelperClient(user=self.new_user)

        self.broker.purge_queue()

    def test_login_by_email_positive(self):
        # when
        response = self.client.post(reverse("email_login"),
                                    data={"email_or_login": self.new_user.email, })

        # then
        self.assertContains(response=response, text="Вам отправлен код!", status_code=200)
        issued_code = Code.objects.filter(recipient=self.new_user.email).get()
        self.assertIsNotNone(issued_code)

        # check email was sent
        packages = self.broker.dequeue()
        task_signed = packages[0][1]
        task = SignedPackage.loads(task_signed)
        self.assertEqual(task["func"].__name__, "send_auth_email")
        self.assertEqual(task["args"][0].id, self.new_user.id)
        self.assertEqual(task["args"][1].id, issued_code.id)

        # check notify wast sent
        packages = self.broker.dequeue()
        task_signed = packages[0][1]
        task = SignedPackage.loads(task_signed)
        self.assertEqual(task["func"].__name__, "notify_user_auth")
        self.assertEqual(task["args"][0].id, self.new_user.id)
        self.assertEqual(task["args"][1].id, issued_code.id)

        # it"s not yet authorised, only code was sent
        self.assertFalse(self.client.is_authorised())

    def test_login_user_not_exist(self):
        response = self.client.post(reverse("email_login"),
                                    data={"email_or_login": "not-existed@user.com", })
        self.assertContains(response=response, text="Такого юзера нет 🤔", status_code=404)

    def test_email_login_missed_input_data(self):
        response = self.client.post(reverse("email_login"), data={})
        self.assertRedirects(response=response, expected_url=f"/auth/login/",
                             fetch_redirect_response=False)

    def test_email_login_wrong_method(self):
        response = self.client.get(reverse("email_login"))
        self.assertRedirects(response=response, expected_url=f"/auth/login/",
                             fetch_redirect_response=False)

        response = self.client.put(reverse("email_login"))
        self.assertRedirects(response=response, expected_url=f"/auth/login/",
                             fetch_redirect_response=False)

        response = self.client.delete(reverse("email_login"))
        self.assertRedirects(response=response, expected_url=f"/auth/login/",
                             fetch_redirect_response=False)


class ViewEmailLoginCodeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.new_user: User = User.objects.create(
            email="testemail@xx.com",
            membership_started_at=datetime.now() - timedelta(days=5),
            membership_expires_at=datetime.now() + timedelta(days=5),
            slug="ujlbu4"
        )
        cls.code = Code.create_for_user(user=cls.new_user, recipient=cls.new_user.email)

    def setUp(self):
        self.client = HelperClient(user=self.new_user)

    def test_correct_code(self):
        # given
        # email is not verified yet
        self.assertFalse(User.objects.get(id=self.new_user.id).is_email_verified)

        # when
        response = self.client.get(reverse("email_login_code"),
                                   data={"email": self.new_user.email, "code": self.code.code})

        self.assertRedirects(response=response, expected_url=f"/user/{self.new_user.slug}/",
                             fetch_redirect_response=False)
        self.assertTrue(self.client.is_authorised())
        self.assertTrue(User.objects.get(id=self.new_user.id).is_email_verified)

    def test_empty_params(self):
        response = self.client.get(reverse("email_login_code"), data={})
        self.assertRedirects(response=response, expected_url=f"/auth/login/",
                             fetch_redirect_response=False)
        self.assertFalse(self.client.is_authorised())
        self.assertFalse(User.objects.get(id=self.new_user.id).is_email_verified)

    def test_wrong_code(self):
        response = self.client.get(reverse("email_login_code"),
                                   data={"email": self.new_user.email, "code": "intentionally-wrong-code"})

        self.assertEqual(response.status_code, HttpResponseBadRequest.status_code)
        self.assertFalse(self.client.is_authorised())
        self.assertFalse(User.objects.get(id=self.new_user.id).is_email_verified)
