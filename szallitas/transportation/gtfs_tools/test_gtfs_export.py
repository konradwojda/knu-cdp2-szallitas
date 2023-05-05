from io import StringIO

from django.test import TestCase

from ..management.commands.load_sample_data import load_wkd_fixture_database
from .gtfs_export import GTFSExporter


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
