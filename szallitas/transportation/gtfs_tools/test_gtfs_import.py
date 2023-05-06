from datetime import datetime, timedelta
from decimal import Decimal
from io import StringIO
from pathlib import Path

from django.test import TestCase

from . import gtfs_import
from ..models import *

FIXTURES_DIR = Path(__file__).with_name("fixtures")


class GTFSImportTestCase(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_import_agencies(self):
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

    def test_import_calendar_exceptions(self):
        test_csv = """service_id,date,exception_type
Robocze,20230410,2"""
        importer = gtfs_import.GTFSLoader()
        importer.import_calendar_exceptions(StringIO(test_csv))
        calendar = Calendar.objects.get(id=importer.calendar_mapping["Robocze"])
        calendar_exception = calendar.calendar_exception_set.first()
        assert calendar_exception is not None
        self.assertEqual(calendar_exception.day, datetime.strptime("20230410", "%Y%m%d").date())
        self.assertFalse(calendar_exception.added)
        self.assertEqual(calendar.start_date, datetime.strptime("20000101", "%Y%m%d").date())
        self.assertEqual(calendar.name, "Robocze")
        self.assertFalse(calendar.monday)
        self.assertFalse(calendar.tuesday)
        self.assertFalse(calendar.wednesday)
        self.assertFalse(calendar.thursday)
        self.assertFalse(calendar.friday)
        self.assertFalse(calendar.saturday)
        self.assertFalse(calendar.sunday)

    def test_load_zip(self):
        loader = gtfs_import.GTFSLoader()
        loader.from_zip(FIXTURES_DIR / "lomianki.zip")

        self.assertEqual(Agency.objects.count(), 1)
        agency = Agency.objects.first()
        assert agency is not None
        self.assertEqual(agency.name, "Komunikacja Miejska Łomianki")
        self.assertEqual(agency.website, "http://kmlomianki.info/")
        self.assertEqual(agency.timezone, "Europe/Warsaw")
        self.assertIsNone(agency.telephone)

        self.assertEqual(Stop.objects.count(), 75)
        stop = Stop.objects.get(id=loader.stop_mapping["114-3"])
        assert stop is not None
        self.assertEqual(stop.name, "Łomianki Buraków 03")
        self.assertIsNone(stop.code)
        self.assertEqual(stop.lat, Decimal("52.324181"))
        self.assertEqual(stop.lon, Decimal("20.910699"))
        self.assertEqual(stop.wheelchair_accessible, 0)

        self.assertEqual(Line.objects.count(), 3)
        line = Line.objects.get(id=loader.line_mapping["1"])
        self.assertEqual(line.code, "1")
        self.assertEqual(
            line.description, "Dziekanów Leśny — Dąbrowa Zachodnia (— Osiedle Równoległa)"
        )
        self.assertEqual(line.line_type, 3)
        self.assertEqual(line.agency.name, agency.name)

        self.assertEqual(Calendar.objects.count(), 2)
        calendar = Calendar.objects.get(id=loader.calendar_mapping["Robocze"])
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

        self.assertEqual(CalendarException.objects.count(), 16)
        calendar = Calendar.objects.get(id=loader.calendar_mapping["Robocze"])
        calendar_exception = calendar.calendar_exception_set.first()
        assert calendar_exception is not None
        self.assertEqual(calendar_exception.day, datetime.strptime("20230410", "%Y%m%d").date())
        self.assertFalse(calendar_exception.added)
        self.assertEqual(calendar.start_date, datetime.strptime("20230126", "%Y%m%d").date())
        self.assertEqual(calendar.name, "Robocze")
        self.assertTrue(calendar.monday)
        self.assertTrue(calendar.tuesday)
        self.assertTrue(calendar.wednesday)
        self.assertTrue(calendar.thursday)
        self.assertTrue(calendar.friday)
        self.assertFalse(calendar.saturday)
        self.assertFalse(calendar.sunday)

        self.assertEqual(Pattern.objects.count(), 11)
        pattern = Pattern.objects.first()
        assert pattern is not None
        self.assertEqual(pattern.headsign, "Osiedle Równoległa")
        self.assertEqual(pattern.direction, 0)
        self.assertEqual(pattern.line.code, "1")

        self.assertEqual(PatternStop.objects.count(), 186)
        patternstop = PatternStop.objects.first()
        assert patternstop is not None
        self.assertEqual(patternstop.pattern.id, 1)
        self.assertEqual(patternstop.stop.name, "Dziekanów Leśny 01")
        self.assertEqual(patternstop.travel_time, timedelta(0))
        self.assertEqual(patternstop.index, 1)

        self.assertEqual(Trip.objects.count(), 61)
        trip = Trip.objects.first()
        assert trip is not None
        self.assertEqual(trip.wheelchair_accessible, 0)
        self.assertEqual(trip.departure, timedelta(seconds=23220))
        self.assertEqual(trip.pattern.id, 1)
        self.assertEqual(trip.calendar.name, "Robocze")
