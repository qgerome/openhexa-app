from django import test
from django.conf import settings
from django.db.models import QuerySet
from django.urls import reverse

from habari.auth.models import User


class CatalogTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_REGULAR = User.objects.create_user(
            "regular@bluesquarehub.com",
            "regular@bluesquarehub.com",
            "regular",
        )

    def test_catalog_index_302(self):
        response = self.client.get(
            reverse(
                "catalog:index",
            ),
        )

        # Check that the response is temporary redirection to /login.
        self.assertEqual(response.status_code, 302)
        self.assertIn(settings.LOGIN_URL, response.url)

    def test_catalog_index_200(self):
        self.client.login(email="regular@bluesquarehub.com", password="regular")
        response = self.client.get(
            reverse(
                "catalog:index",
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["datasources"], QuerySet)