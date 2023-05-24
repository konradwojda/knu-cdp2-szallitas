from django.test import TestCase

from ..management.commands.load_sample_data import load_wkd_fixture_database
from ..models import PatternStop
from .tabular import generate_tabular_timetable


class GenerateTabularTimetableTestCase(TestCase):
    def setUp(self) -> None:
        load_wkd_fixture_database()

    def test_single(self) -> None:
        # Milanówek Grudów for Warszawa Śródmieście WKD
        ps = PatternStop.objects.filter(stop_id=22, pattern__direction=1).first()
        assert ps is not None  # normal assertion for type checking

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

    def test_multiple(self) -> None:
        # Komorów for Warszawa Śródmieście WKD; 2 patterns
        pattern_stops = PatternStop.objects.filter(stop_id=14, pattern__direction=1).all()
        self.assertEqual(pattern_stops.count(), 2)

        tt = generate_tabular_timetable(*pattern_stops)
        self.assertEqual(len(tt), 2)

        self.assertEqual(tt[0][0], "Mon-Fri")
        self.assertListEqual(
            tt[0][1],
            [
                ("04", ["11", "33", "55"]),
                ("05", ["17", "39", "59"]),
                ("06", ["19", "37", "49"]),
                ("07", ["01", "13", "24", "35", "46", "57"]),
                ("08", ["08", "19", "32", "47"]),
                ("09", ["02", "14", "24", "35", "46", "57"]),
                ("10", ["12", "27", "42", "57"]),
                ("11", ["12", "27", "42", "57"]),
                ("12", ["12", "27", "42", "57"]),
                ("13", ["12", "27", "42", "57"]),
                ("14", ["12", "24", "36", "48"]),
                ("15", ["00", "12", "24", "36", "48"]),
                ("16", ["00", "12", "24", "36", "48", "59"]),
                ("17", ["09", "24", "36", "48", "59"]),
                ("18", ["09", "24", "36", "48", "59"]),
                ("19", ["09", "24", "36", "48"]),
                ("20", ["09", "19", "29", "44", "59"]),
                ("21", ["14", "30", "52"]),
                ("22", ["12", "27", "48"]),
                ("23", ["27", "57"]),
                ("24", ["12", "28"]),
            ],
        )

        self.assertEqual(tt[1][0], "Sat-Sun")
        self.assertListEqual(
            tt[1][1],
            [
                ("04", ["55"]),
                ("05", ["17", "39"]),
                ("06", ["09", "29", "49"]),
                ("07", ["09", "29", "49"]),
                ("08", ["09", "29", "49"]),
                ("09", ["09", "29", "49"]),
                ("10", ["09", "29", "49"]),
                ("11", ["09", "29", "49"]),
                ("12", ["09", "29", "49"]),
                ("13", ["09", "29", "49"]),
                ("14", ["09", "29", "49"]),
                ("15", ["09", "29", "49"]),
                ("16", ["09", "29", "49"]),
                ("17", ["09", "29", "49"]),
                ("18", ["09", "29", "49"]),
                ("19", ["09", "29", "49"]),
                ("20", ["09", "29", "49"]),
                ("21", ["09", "29", "49"]),
                ("22", ["09", "39"]),
                ("23", ["09", "39"]),
                ("24", ["12", "28"]),
            ],
        )
