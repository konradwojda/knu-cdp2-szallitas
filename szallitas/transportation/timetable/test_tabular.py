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
        self.assertEqual(tt[1][0], "Sat-Sun")

        # Check the hour ranges
        self.assertEqual(len(tt[0][1]), 20)
        self.assertEqual(tt[0][1][0][0], "04")
        self.assertEqual(tt[0][1][-1][0], "23")

        self.assertEqual(len(tt[1][1]), 20)
        self.assertEqual(tt[1][1][0][0], "04")
        self.assertEqual(tt[1][1][-1][0], "23")

        # Check generated minutes
        self.assertListEqual(tt[0][1][0][1], ["50"])
        self.assertListEqual(tt[0][1][12][1], ["09", "57"])
        self.assertListEqual(tt[0][1][15][1], [])
        self.assertListEqual(tt[0][1][-1][1], ["00"])
