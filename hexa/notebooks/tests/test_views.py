from django import test
from django.urls import reverse

from hexa.user_management.models import User


class ViewsTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks2",
            is_superuser=True,
        )

    def test_credentials_200(self):
        self.client.force_login(self.USER_JANE)
        response = self.client.post(
            reverse(
                "notebooks:credentials",
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"username": "jane@bluesquarehub.com", "env": {}, "files": {}},
        )

    def test_credentials_401(self):
        response = self.client.post(reverse("notebooks:credentials"))

        self.assertEqual(response.status_code, 401)
        response_data = response.json()
        self.assertEqual(0, len(response_data))
