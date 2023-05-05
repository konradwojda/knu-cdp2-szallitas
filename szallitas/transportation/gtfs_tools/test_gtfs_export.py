from django.test import TestCase

from ..management.commands.load_sample_data import load_wkd_fixture_database
from ..models import Agency, Line


class GTFSExportTestCase(TestCase):
    def setUp(self) -> None:
        load_wkd_fixture_database()

    def test(self) -> None:
        self.assertEqual(Agency.objects.count(), 1)
        self.assertEqual(Line.objects.count(), 3)
