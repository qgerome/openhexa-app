import responses
from django import test

from ..api import (
    DataElementResult,
    DataSetResult,
    Dhis2Client,
    Dhis2Result,
    IndicatorResult,
    IndicatorTypeResult,
    OrganisationUnitResult,
)
from .mock_data import (
    mock_data_elements_response,
    mock_datasets_response,
    mock_indicator_types_response,
    mock_indicators_response,
    mock_orgunits_response,
)


class Dhis2Test(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dhis2_client = Dhis2Client(
            url="https://play.dhis2.org.invalid/demo",
            username="admin",
            password="district",
        )

    @test.tag("external")
    @responses.activate
    def test_fetch_data_elements(self):
        responses.add(
            responses.GET,
            "https://play.dhis2.org.invalid/demo/api/dataElements.json?fields=%3Aall&pageSize=100&page=1&totalPages=True",
            json=mock_data_elements_response,
            status=200,
        )
        results = []
        for result_batch in self.dhis2_client.fetch_data_elements():
            results.extend(result_batch)

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], DataElementResult)

    @test.tag("external")
    @responses.activate
    def test_fetch_indicator_types(self):
        responses.add(
            responses.GET,
            "https://play.dhis2.org.invalid/demo/api/indicatorTypes.json?fields=%3Aall&pageSize=100&page=1&totalPages=True",
            json=mock_indicator_types_response,
            status=200,
        )
        results = []
        for result_batch in self.dhis2_client.fetch_indicator_types():
            results.extend(result_batch)

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], IndicatorTypeResult)

    @test.tag("external")
    @responses.activate
    def test_fetch_org_unit(self):
        responses.add(
            responses.GET,
            "https://play.dhis2.org.invalid/demo/api/organisationUnits.json?fields=%3Aall&pageSize=100&page=1&totalPages=True",
            json=mock_orgunits_response,
            status=200,
        )
        results = []
        for result_batch in self.dhis2_client.fetch_organisation_units():
            results.extend(result_batch)

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], OrganisationUnitResult)

    @test.tag("external")
    @responses.activate
    def test_fetch_indicators(self):
        responses.add(
            responses.GET,
            "https://play.dhis2.org.invalid/demo/api/indicators.json?fields=%3Aall&pageSize=100&page=1&totalPages=True",
            json=mock_indicators_response,
            status=200,
        )
        results = []
        for result_batch in self.dhis2_client.fetch_indicators():
            results.extend(result_batch)

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], IndicatorResult)

    @test.tag("external")
    @responses.activate
    def test_fetch_datasets(self):
        responses.add(
            responses.GET,
            "https://play.dhis2.org.invalid/demo/api/dataSets.json?fields=%3Aall&pageSize=100&page=1&totalPages=True",
            json=mock_datasets_response,
            status=200,
        )
        results = []
        for result_batch in self.dhis2_client.fetch_datasets():
            results.extend(result_batch)

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], DataSetResult)

    def test_dhis2_result(self):
        class FooResult(Dhis2Result):
            FIELD_SPECS = {"foo": (str, "baz")}

        # property not in specs
        result = FooResult({})
        with self.assertRaises(ValueError):
            result.get_value("bar")

        # property is not translatable
        result = FooResult({"foo": "bar"})
        self.assertIs(result.get_value("foo", "en"), "bar")
        self.assertIs(result.get_value("foo"), "bar")

        # locale is present
        result = FooResult(
            {"translations": [{"property": "FOO", "locale": "en", "value": "bar"}]}
        )
        self.assertIs(result.get_value("foo", "en"), "bar")
        self.assertIs(result.get_value("foo"), "bar")

        # missing locale
        result = FooResult(
            {"translations": [{"property": "FOO", "locale": "fr", "value": "bar"}]}
        )
        self.assertIs(result.get_value("foo", "en"), "bar")
        self.assertIs(result.get_value("foo"), "bar")

        # defaults
        result = FooResult({})
        self.assertIs(result.get_value("foo", "it"), "baz")
        self.assertIs(result.get_value("foo"), "baz")
