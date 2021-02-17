from django import test
from django.conf import settings
from django.urls import reverse

from habari.auth.models import User
from habari.catalog.models import Datasource


class CatalogTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_REGULAR = User.objects.create_user(
            "regular@bluesquarehub.com",
            "regular@bluesquarehub.com",
            "regular",
        )

        cls.DATASOURCE_DHIS2_PLAY = Datasource.objects.create(
            name="DHIS2 Play", datasource_type="DHIS2"
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

    def test_datasource_detail_200(self):
        self.client.login(email="regular@bluesquarehub.com", password="regular")
        response = self.client.get(
            reverse(
                "catalog:datasource_detail",
                kwargs={"datasource_id": self.DATASOURCE_DHIS2_PLAY.id},
            ),
        )
        self.assertEqual(response.status_code, 200)
