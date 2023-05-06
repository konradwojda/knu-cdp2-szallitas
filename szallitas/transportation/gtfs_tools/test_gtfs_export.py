from io import StringIO

from django.test import TestCase

from ..management.commands.load_sample_data import load_wkd_fixture_database
from . import gtfs_export
from .gtfs_export import GTFSExporter


def first_lines(f: StringIO, n_lines: int = 10) -> str:
    return "\r\n".join(f.getvalue().split("\r\n")[:n_lines]) + "\r\n"


class SecondsToGTFSTimeTestCase(TestCase):
    def test(self) -> None:
        self.assertEqual(gtfs_export.seconds_to_gtfs_time(8 * 3600 + 15 * 60 + 30), "08:15:30")
        self.assertEqual(gtfs_export.seconds_to_gtfs_time(12 * 3600 + 5 * 60), "12:05:00")
        self.assertEqual(gtfs_export.seconds_to_gtfs_time(25 * 3600 + 48 * 60 + 20), "25:48:20")


class GTFSExportTestCase(TestCase):
    def setUp(self) -> None:
        load_wkd_fixture_database()

    def test_export_agencies(self) -> None:
        f = StringIO()
        GTFSExporter.export_agencies(f)
        self.assertMultiLineEqual(
            f.getvalue(),
            (
                "agency_id,agency_name,agency_url,agency_timezone,agency_phone\r\n"
                "1,WKD,https://wkd.com.pl,Europe/Warsaw,\r\n"
            ),
        )

    def test_export_routes(self) -> None:
        f = StringIO()
        GTFSExporter.export_routes(f)
        self.assertMultiLineEqual(
            f.getvalue(),
            (
                "route_id,agency_id,route_short_name,route_long_name,route_type\r\n"
                "1,1,A1,Warszawa Śródmieście WKD — Grodzisk Mazowiecki Radońska,2\r\n"
                "2,1,ZA1,Podkowa Leśna Główna — Grodzisk Mazowiecki Radońska (ZKA),3\r\n"
                "3,1,ZA12,Podkowa Leśna Główna — Milanówek Grudów (ZKA),3\r\n"
            ),
        )

    def test_export_stops(self) -> None:
        f = StringIO()
        GTFSExporter.export_stops(f)
        self.assertMultiLineEqual(
            first_lines(f, 6),
            (
                "stop_id,stop_name,stop_code,stop_lat,stop_lon,wheelchair_boarding\r\n"
                "1,Warszawa Śródmieście WKD,,52.227686,21.000404,2\r\n"
                "2,Warszawa Ochota WKD,,52.225420,20.989605,2\r\n"
                "3,Warszawa Zachodnia WKD,,52.219443,20.965556,2\r\n"
                "4,Warszawa Reduta Ordona,,52.214385,20.947908,1\r\n"
                "5,Warszawa Aleje Jerozolimskie,,52.205325,20.942254,1\r\n"
            ),
        )

    def test_export_calendars(self) -> None:
        f = StringIO()
        GTFSExporter.export_calendars(f)
        self.assertMultiLineEqual(
            f.getvalue(),
            (
                "service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,"
                "start_date,end_date,service_desc\r\n"
                "1,0,0,0,0,0,1,1,20230313,20240229,Sat-Sun\r\n"
                "2,1,1,1,1,1,0,0,20230313,20240229,Mon-Fri\r\n"
            ),
        )

    def test_export_calendar_dates(self) -> None:
        f = StringIO()
        GTFSExporter.export_calendars_dates(f)
        self.assertMultiLineEqual(
            first_lines(f, 6),
            (
                "service_id,date,exception_type\r\n"
                "2,20230410,2\r\n"
                "1,20230410,1\r\n"
                "2,20230501,2\r\n"
                "1,20230501,1\r\n"
                "2,20230503,2\r\n"
            ),
        )

    def test_export_trips_and_stop_times(self) -> None:
        f_trips = StringIO()
        f_times = StringIO()
        GTFSExporter.export_trips_and_stop_times(f_trips, f_times)

        trips = f_trips.getvalue().split("\r\n")
        self.assertEqual(len(trips), 378)
        self.assertEqual(
            trips[0],
            "route_id,service_id,trip_id,trip_headsign,direction_id,wheelchair_accessible",
        )
        self.assertEqual(trips[1], "1,1,1,Podkowa Leśna Główna,0,1")
        self.assertEqual(trips[101], "1,2,101,Podkowa Leśna Główna,0,1")
        self.assertEqual(trips[201], "1,1,201,Warszawa Śródmieście WKD,1,1")
        self.assertEqual(trips[301], "1,2,301,Warszawa Śródmieście WKD,1,1")

        times = f_times.getvalue().split("\r\n")
        self.assertEqual(len(times), 6290)
        self.assertEqual(times[0], "trip_id,stop_sequence,stop_id,arrival_time,departure_time")
        self.assertEqual(times[1], "1,0,1,05:05:00,05:05:00")
        self.assertEqual(times[2], "1,1,2,05:07:00,05:07:00")
        self.assertEqual(times[3], "1,2,3,05:10:00,05:10:00")
        self.assertEqual(times[19], "1,18,19,05:46:00,05:46:00")
        self.assertEqual(times[20], "2,0,1,05:40:00,05:40:00")
