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
