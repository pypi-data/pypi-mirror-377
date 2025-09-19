from django.test import TestCase
from datetime import date

from esi.openapi_clients import ESIClientProvider


class TestOpenapiClientProvider(TestCase):

    def test_compatibilitydate_date_to_string(self):
        testdate_1 = date(2024, 1, 1)
        testdate_2 = date(2025, 8, 26)

        self.assertEqual("2024-01-01", ESIClientProvider._date_to_string(testdate_1))
        self.assertEqual("2025-08-26", ESIClientProvider._date_to_string(testdate_2))
