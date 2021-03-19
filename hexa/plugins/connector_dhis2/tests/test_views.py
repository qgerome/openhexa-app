from django import test
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone

from hexa.user_management.models import User
from hexa.catalog.models import Datasource
from ..models import Instance, DataElement, Indicator


class CatalogTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_REGULAR = User.objects.create_user(
            "bjorn@bluesquarehub.com",
            "bjorn@bluesquarehub.com",
            "regular",
        )
        cls.DHIS2_INSTANCE_PLAY = Instance.objects.create(
            name="DHIS2 Play",
            short_name="Play",
            description="The DHIS2 official demo instance with realistic sample medical data",
            api_url="https://play.dhis2.org/demo",
            api_username="admin",
            api_password="district",
        )
        cls.DATA_ELEMENT_1 = DataElement.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="O1BccPF5yci",
            dhis2_name="ANC First visit",
            dhis2_created=timezone.now(),
            dhis2_last_updated=timezone.now(),
            dhis2_external_access=False,
            dhis2_favorite=False,
        )
        cls.DATA_ELEMENT_2 = DataElement.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="eLW6jbvVcPZ",
            dhis2_name="ANC Second visit",
            dhis2_created=timezone.now(),
            dhis2_last_updated=timezone.now(),
            dhis2_external_access=False,
            dhis2_favorite=False,
        )
        cls.DATA_ELEMENT_3 = DataElement.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="kmaHyZXMHCz",
            dhis2_name="C-sections",
            dhis2_created=timezone.now(),
            dhis2_last_updated=timezone.now(),
            dhis2_external_access=False,
            dhis2_favorite=False,
        )
        cls.DATA_INDICATOR_1 = Indicator.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="xaG3AfYG2Ts",
            dhis2_name="Ante-Natal Care visits",
            dhis2_description="Uses different ANC data indicators",
            dhis2_created=timezone.now(),
            dhis2_last_updated=timezone.now(),
            dhis2_external_access=False,
            dhis2_favorite=False,
            dhis2_annualized=False,
        )
        cls.DATA_INDICATOR_2 = Indicator.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="oNzq8duNBx6",
            dhis2_name="Medical displays",
            dhis2_created=timezone.now(),
            dhis2_last_updated=timezone.now(),
            dhis2_external_access=False,
            dhis2_favorite=False,
            dhis2_annualized=False,
        )

    def test_datasource_detail_200(self):
        self.client.login(email="bjorn@bluesquarehub.com", password="regular")
        response = self.client.get(
            reverse(
                "connector_dhis2:datasource_detail",
                kwargs={"datasource_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["datasource"], Datasource)
        self.assertIsInstance(response.context["data_elements_list_params"], dict)
        self.assertIsInstance(response.context["indicators_list_params"], dict)

    @test.tag("external")
    def test_datasource_sync_success_302(self):
        self.client.login(email="bjorn@bluesquarehub.com", password="regular")
        http_referer = (
            f"https://localhost/catalog/datasource/{self.DHIS2_INSTANCE_PLAY.pk}"
        )
        response = self.client.get(
            reverse(
                "connector_dhis2:datasource_sync",
                kwargs={"datasource_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
            HTTP_REFERER=http_referer,
        )

        # Check that the response is temporary redirection to referer
        self.assertEqual(response.status_code, 302)
        self.assertEqual(http_referer, response.url)

        # Test that all data elements have a value type and an aggregation type
        self.assertEqual(0, len(DataElement.objects.filter(dhis2_value_type=None)))
        self.assertEqual(
            0, len(DataElement.objects.filter(dhis2_aggregation_type=None))
        )

    def test_data_elements_200(self):
        self.client.login(email="bjorn@bluesquarehub.com", password="regular")
        response = self.client.get(
            reverse(
                "connector_dhis2:data_element_list",
                kwargs={"datasource_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["datasource"], Datasource)
        self.assertIsInstance(response.context["data_elements_list_params"], dict)

    def test_indicators_200(self):
        self.client.login(email="bjorn@bluesquarehub.com", password="regular")
        response = self.client.get(
            reverse(
                "connector_dhis2:indicator_list",
                kwargs={"datasource_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["datasource"], Datasource)
        self.assertIsInstance(response.context["indicators_list_params"], dict)

    def test_catalog_quick_search_dhis2_200(self):
        self.client.login(email="bjorn@bluesquarehub.com", password="regular")

        # "foo" should have zero matches
        response = self.client.get(f"{reverse('catalog:quick_search')}?query=foo")
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.json()["results"]))

        # "anc" should match 2 data elements and 1 indicator
        response = self.client.get(f"{reverse('catalog:quick_search')}?query=anc")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        results = response.json()["results"]
        self.assertEqual(3, len(results))
        self.assertTrue(
            any(
                r
                for r in results
                if r["app_label"] == "connector_dhis2"
                and r["content_type_name"] == "DHIS2 Data Element"
                and r["name"] == "ANC First visit"
            )
        )
        self.assertTrue(
            any(
                r
                for r in results
                if r["app_label"] == "connector_dhis2"
                and r["content_type_name"] == "DHIS2 Data Element"
                and r["name"] == "ANC Second visit"
            )
        )
        self.assertTrue(
            any(
                r
                for r in results
                if r["app_label"] == "connector_dhis2"
                and r["content_type_name"] == "DHIS2 Indicator"
                and r["name"] == "Ante-Natal Care visits"
            )
        )

        # "display" should match 1 data source and 1 indicator
        response = self.client.get(f"{reverse('catalog:quick_search')}?query=medical")
        results = response.json()["results"]
        self.assertEqual(2, len(results))
        self.assertTrue(
            any(
                r
                for r in results
                if r["app_label"] == "connector_dhis2"
                and r["content_type_name"] == "DHIS2 Instance"
                and r["name"] == "DHIS2 Play"
            )
        )
        self.assertTrue(
            any(
                r
                for r in results
                if r["app_label"] == "connector_dhis2"
                and r["content_type_name"] == "DHIS2 Indicator"
                and r["name"] == "Medical displays"
            )
        )