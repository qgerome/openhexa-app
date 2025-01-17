from django import test
from django.urls import reverse

from hexa.user_management.models import User


class ViewsTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_REGULAR = User.objects.create_user(
            "john@bluesquarehub.com",
            "regular",
            is_superuser=True,
        )

    def test_any_page_anonymous_302(self):
        response = self.client.get(reverse("core:dashboard"))

        # Check that the response is temporary redirection to /login.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/?next=/dashboard")

    def test_any_page_anonymous_200(self):
        self.client.login(email="john@bluesquarehub.com", password="regular")
        response = self.client.get(reverse("core:dashboard"))

        self.assertEqual(response.status_code, 200)

    def test_logout_302(self):
        self.client.login(email="john@bluesquarehub.com", password="regular")
        response = self.client.get(reverse("logout"))

        # Check that the response is temporary redirection to /login.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

    def test_account_200(self):
        self.client.login(email="john@bluesquarehub.com", password="regular")
        response = self.client.get(reverse("user:account"))

        self.assertEqual(response.status_code, 200)


class AceptTosTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_REGULAR = User.objects.create_user(
            "john@bluesquarehub.com",
            "regular",
        )

    @test.override_settings(USER_MUST_ACCEPT_TOS=True)
    def test_tos(self):
        self.client.login(email="john@bluesquarehub.com", password="regular")

        # without validation -> page should ask to accept tos
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"TEST-KEY: ACCEPT_TOS" in response.content, True)

        # let's accept -> should redirect to index
        response = self.client.post(reverse("user:accept_tos"))
        self.assertEqual(response.status_code, 302)

        # let's retry to load the dashboard -> not an accept_tos page
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"TEST-KEY: ACCEPT_TOS" in response.content, False)


class InviteUserAdminTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_ADMIN = User.objects.create_user(
            "john@bluesquarehub.com",
            "passwd",
            is_superuser=True,
            is_staff=True,
        )

    def test_invite_user(self):
        # an admin can invite a new user via django admin pages
        self.client.force_login(self.USER_ADMIN)
        self.assertEqual(User.objects.all().count(), 1)
        response = self.client.post(
            "/admin/user_management/user/add/",
            data={
                "email": "invited@bluesquarehub.com",
                "first_name": "daniel",
                "last_name": "mote",
                "password1": "",
                "password2": "",
                "_save": "Save",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.all().count(), 2)
