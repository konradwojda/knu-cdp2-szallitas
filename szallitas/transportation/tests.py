from datetime import datetime
from decimal import Decimal
from io import StringIO

from django.test import TestCase

from .gtfs_tools import gtfs_import
from .models import *


class GTFSImportTestCase(TestCase):
    # TODO: Add more tests for this case
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

    def test_import_stops(self):
        # TODO: Add test files instead of strings
        test_csv = """stop_id,stop_name,stop_code,stop_lat,stop_lon
114-3,Łomianki Buraków 03,ŁB03,52.324181,20.910699"""
        importer = gtfs_import.GTFSLoader()
        importer.import_stops(StringIO(test_csv))
        stop = Stop.objects.get(id=importer.stop_mapping["114-3"])
        self.assertEqual(stop.name, "Łomianki Buraków 03")
        self.assertEqual(stop.code, "ŁB03")
        self.assertEqual(stop.lat, Decimal("52.324181"))
        self.assertEqual(stop.lon, Decimal("20.910699"))
        self.assertEqual(stop.wheelchair_accessible, 0)

    def test_import_lines(self):
        # TODO: Add test files instead of strings
        test_csv = """agency_id,route_id,route_short_name,route_long_name,route_type
0,1,1,"Dziekanów Leśny — Dąbrowa Zachodnia (— Osiedle Równoległa)",3"""
        agency = Agency.objects.create(name="Test Agency", website="www.test.com")
        importer = gtfs_import.GTFSLoader()
        importer.agency_mapping["0"] = agency.id
        importer.import_lines(StringIO(test_csv))
        line = Line.objects.get(id=importer.line_mapping["1"])
        self.assertEqual(line.code, "1")
        self.assertEqual(
            line.description, "Dziekanów Leśny — Dąbrowa Zachodnia (— Osiedle Równoległa)"
        )
        self.assertEqual(line.line_type, 3)
        self.assertEqual(line.agency.name, agency.name)

    def test_import_calendars(self):
        # TODO: Add test files instead of strings
        test_csv = """service_id,start_date,end_date,monday,tuesday,wednesday,thursday,friday,saturday,sunday
Robocze,20230126,20240117,1,1,1,1,1,0,0"""
        importer = gtfs_import.GTFSLoader()
        importer.import_calendars(StringIO(test_csv))
        calendar = Calendar.objects.get(id=importer.calendar_mapping["Robocze"])
        self.assertEqual(calendar.name, "Robocze")
        self.assertEqual(calendar.start_date, datetime.strptime("20230126", "%Y%m%d").date())
        self.assertEqual(calendar.end_date, datetime.strptime("20240117", "%Y%m%d").date())
        self.assertTrue(calendar.monday)
        self.assertTrue(calendar.tuesday)
        self.assertTrue(calendar.wednesday)
        self.assertTrue(calendar.thursday)
        self.assertTrue(calendar.friday)
        self.assertFalse(calendar.saturday)
        self.assertFalse(calendar.sunday)
