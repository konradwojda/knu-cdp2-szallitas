from io import StringIO

from django.test import TestCase

from .gtfs_tools import gtfs_import
from .models import *


class GTFSImportTestCase(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_import_agencies(self):
        # TODO: Add test files instead of strings
        test_csv = """agency_id,agency_name,agency_url,agency_timezone,agency_lang
0,"Komunikacja Miejska Łomianki","http://kmlomianki.info/",Europe/Warsaw,pl"""
        importer = gtfs_import.GTFSLoader()
        importer.import_agencies(StringIO(test_csv))
        agency = Agency.objects.get(id=importer.agency_mapping["0"])
        self.assertEqual(agency.name, "Komunikacja Miejska Łomianki")
        self.assertEqual(agency.website, "http://kmlomianki.info/")
        self.assertEqual(agency.timezone, "Europe/Warsaw")
        self.assertIsNone(agency.telephone)
