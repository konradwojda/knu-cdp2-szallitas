from django.test import TestCase

from ..management.commands.load_sample_data import load_wkd_fixture_database
from ..models import PatternStop
from .tabular import generate_tabular_timetable


class GenerateTabularTimetableTestCase(TestCase):
    def setUp(self) -> None:
        load_wkd_fixture_database()

    def test(self) -> None:
        ps = PatternStop.objects.filter(stop_id=22, pattern__direction=1).first()
        assert ps is not None  # normal assertion for type checking

        # Check the calendars and their ordering
        tt = generate_tabular_timetable(ps)
        self.assertEqual(len(tt), 2)

        self.assertEqual(tt[0][0], "Mon-Fri")
        self.assertListEqual(
            tt[0][1],
            [
                ("04", ["50"]),
                ("05", ["32"]),
                ("06", ["22"]),
                ("07", ["08"]),
                ("08", ["20"]),
                ("09", ["08"]),
                ("10", ["00"]),
                ("11", ["00"]),
                ("12", ["00"]),
                ("13", ["00"]),
                ("14", ["09"]),
                ("15", ["09"]),
                ("16", ["09", "57"]),
                ("17", ["57"]),
                ("18", ["57", "57"]),
                ("19", []),
                ("20", ["47"]),
                ("21", []),
                ("22", ["00"]),
                ("23", ["00"]),
            ],
        )

        self.assertEqual(tt[1][0], "Sat-Sun")
        self.assertListEqual(
            tt[1][1],
            [
                ("04", []),
                ("05", ["12"]),
                ("06", ["17"]),
                ("07", ["02"]),
                ("08", ["02"]),
                ("09", ["02"]),
                ("10", ["02"]),
                ("11", ["02"]),
                ("12", ["02"]),
                ("13", ["02"]),
                ("14", ["02"]),
                ("15", ["02"]),
                ("16", ["02"]),
                ("17", ["02"]),
                ("18", ["02"]),
                ("19", ["02"]),
                ("20", ["02"]),
                ("21", ["02"]),
                ("22", ["12"]),
                ("23", ["12"]),
            ],
        )
