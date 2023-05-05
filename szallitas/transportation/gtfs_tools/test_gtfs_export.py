from io import StringIO

from django.test import TestCase

from ..management.commands.load_sample_data import load_wkd_fixture_database
from .gtfs_export import GTFSExporter


def first_lines(f: StringIO, n_lines: int = 10) -> str:
    return "\r\n".join(f.getvalue().split("\r\n")[:n_lines]) + "\r\n"


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
