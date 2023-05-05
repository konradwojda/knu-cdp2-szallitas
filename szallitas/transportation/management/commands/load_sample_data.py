import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Optional

from django.core.management.base import BaseCommand

from ...models import (
    Agency,
    Calendar,
    CalendarException,
    Line,
    Pattern,
    PatternStop,
    Stop,
    Trip,
    WheelchairAccessibility,
)

# Data based on https://mkuran.pl/gtfs/wkd.zip (feed_version=20230313)
# Available under CC0-1.0 (public domain)

FIXTURE_SCHEDULES_FILE = Path(__file__).parent / "fixtures" / "schedules.json"

FIXTURE_AGENCY = Agency(id=1, name="WKD", website="https://wkd.com.pl", timezone="Europe/Warsaw")

FIXTURE_STOPS = {
    "wsrod": Stop(
        id=1,
        name="Warszawa Śródmieście WKD",
        lat=52.22768605033,
        lon=21.00040372159,
        wheelchair_accessible=2,
    ),
    "wocho": Stop(
        id=2,
        name="Warszawa Ochota WKD",
        lat=52.2254204,
        lon=20.9896052,
        wheelchair_accessible=2,
    ),
    "wzach": Stop(
        id=3,
        name="Warszawa Zachodnia WKD",
        lat=52.2194428,
        lon=20.9655565,
        wheelchair_accessible=2,
    ),
    "wreor": Stop(
        id=4,
        name="Warszawa Reduta Ordona",
        lat=52.2143846,
        lon=20.9479076,
        wheelchair_accessible=1,
    ),
    "walje": Stop(
        id=5,
        name="Warszawa Aleje Jerozolimskie",
        lat=52.2053252,
        lon=20.9422535,
        wheelchair_accessible=1,
    ),
    "wrako": Stop(
        id=6,
        name="Warszawa Raków",
        lat=52.1944620,
        lon=20.9358376,
        wheelchair_accessible=2,
    ),
    "wsalo": Stop(
        id=7,
        name="Warszawa Salomea",
        lat=52.1865168,
        lon=20.9246206,
        wheelchair_accessible=1,
    ),
    "opacz": Stop(
        id=8,
        name="Opacz",
        lat=52.1813825,
        lon=20.9046328,
        wheelchair_accessible=1,
    ),
    "micha": Stop(
        id=9,
        name="Michałowice",
        lat=52.1753726,
        lon=20.8812869,
        wheelchair_accessible=1,
    ),
    "regul": Stop(
        id=10,
        name="Reguły",
        lat=52.1704016,
        lon=20.8590621,
        wheelchair_accessible=1,
    ),
    "malic": Stop(
        id=11,
        name="Malichy",
        lat=52.1693915,
        lon=20.8411556,
        wheelchair_accessible=1,
    ),
    "twork": Stop(
        id=12,
        name="Tworki",
        lat=52.1690033,
        lon=20.8232948,
        wheelchair_accessible=1,
    ),
    "prusz": Stop(
        id=13,
        name="Pruszków WKD",
        lat=52.1616392,
        lon=20.8166108,
        wheelchair_accessible=1,
    ),
    "komor": Stop(
        id=14,
        name="Komorów",
        lat=52.1481518,
        lon=20.8113778,
        wheelchair_accessible=1,
    ),
    "nwwar": Stop(
        id=15,
        name="Nowa Wieś Warszawska",
        lat=52.1404979,
        lon=20.7956386,
        wheelchair_accessible=1,
    ),
    "kanie": Stop(
        id=16,
        name="Kanie Helenowskie",
        lat=52.1316424,
        lon=20.7742801,
        wheelchair_accessible=1,
    ),
    "otreb": Stop(
        id=17,
        name="Otrębusy",
        lat=52.1263816,
        lon=20.7615852,
        wheelchair_accessible=1,
    ),
    "plwsc": Stop(
        id=18,
        name="Podkowa Leśna Wschodnia",
        lat=52.1237864,
        lon=20.7384324,
        wheelchair_accessible=1,
    ),
    "plglo": Stop(
        id=19,
        name="Podkowa Leśna Główna",
        lat=52.1223734,
        lon=20.7251796,
        wheelchair_accessible=1,
    ),
    "plzac": Stop(
        id=20,
        name="Podkowa Leśna Zachodnia",
        lat=52.1207776,
        lon=20.7116318,
        wheelchair_accessible=1,
    ),
    "poles": Stop(
        id=21,
        name="Polesie",
        lat=52.121852,
        lon=20.697222,
        wheelchair_accessible=1,
    ),
    "milgr": Stop(
        id=22,
        name="Milanówek Grudów",
        lat=52.12226923002,
        lon=20.6822946245,
        wheelchair_accessible=1,
    ),
    "kazim": Stop(
        id=23,
        name="Kazimierówka",
        lat=52.1110880,
        lon=20.6983763,
        wheelchair_accessible=1,
    ),
    "brzoz": Stop(
        id=24,
        name="Brzózki",
        lat=52.1048841,
        lon=20.6776750,
        wheelchair_accessible=1,
    ),
    "gmokr": Stop(
        id=25,
        name="Grodzisk Mazowiecki Okrężna",
        lat=52.1006961,
        lon=20.6601977,
        wheelchair_accessible=1,
    ),
    "gmpia": Stop(
        id=26,
        name="Grodzisk Mazowiecki Piaskowa",
        lat=52.1025545,
        lon=20.6515664,
        wheelchair_accessible=1,
    ),
    "gmjor": Stop(
        id=27,
        name="Grodzisk Mazowiecki Jordanowice",
        lat=52.1030389,
        lon=20.6360364,
        wheelchair_accessible=1,
    ),
    "gmrad": Stop(
        id=28,
        name="Grodzisk Mazowiecki Radońska",
        lat=52.1006450,
        lon=20.6284350,
        wheelchair_accessible=1,
    ),
}

FIXTURE_LINES = {
    "A1": Line(
        id=1,
        code="A1",
        description="Warszawa Śródmieście WKD — Grodzisk Mazowiecki Radońska",
        line_type=Line.LineType.RAIL,
        agency=FIXTURE_AGENCY,
    ),
    "ZA1": Line(
        id=2,
        code="ZA1",
        description="Podkowa Leśna Główna — Grodzisk Mazowiecki Radońska (ZKA)",
        line_type=Line.LineType.BUS,
        agency=FIXTURE_AGENCY,
    ),
    "ZA12": Line(
        id=3,
        code="ZA12",
        description="Podkowa Leśna Główna — Milanówek Grudów (ZKA)",
        line_type=Line.LineType.BUS,
        agency=FIXTURE_AGENCY,
    ),
}

FIXTURE_CALENDARS = {
    "C": Calendar(
        id=1,
        name="Sat-Sun",
        start_date=date(2023, 3, 13),
        end_date=date(2024, 2, 29),
        monday=0,
        tuesday=0,
        wednesday=0,
        thursday=0,
        friday=0,
        saturday=1,
        sunday=1,
    ),
    "D": Calendar(
        id=2,
        name="Mon-Fri",
        start_date=date(2023, 3, 13),
        end_date=date(2024, 2, 29),
        monday=1,
        tuesday=1,
        wednesday=1,
        thursday=1,
        friday=1,
        saturday=0,
        sunday=0,
    ),
}

FIXTURE_CALENDAR_EXCEPTIONS = [
    CalendarException(day=date(2023, 4, 10), added=False, calendar=FIXTURE_CALENDARS["D"]),
    CalendarException(day=date(2023, 4, 10), added=True, calendar=FIXTURE_CALENDARS["C"]),
    CalendarException(day=date(2023, 5, 1), added=False, calendar=FIXTURE_CALENDARS["D"]),
    CalendarException(day=date(2023, 5, 1), added=True, calendar=FIXTURE_CALENDARS["C"]),
    CalendarException(day=date(2023, 5, 3), added=False, calendar=FIXTURE_CALENDARS["D"]),
    CalendarException(day=date(2023, 5, 3), added=True, calendar=FIXTURE_CALENDARS["C"]),
    CalendarException(day=date(2023, 6, 8), added=False, calendar=FIXTURE_CALENDARS["D"]),
    CalendarException(day=date(2023, 6, 8), added=True, calendar=FIXTURE_CALENDARS["C"]),
    CalendarException(day=date(2023, 8, 15), added=False, calendar=FIXTURE_CALENDARS["D"]),
    CalendarException(day=date(2023, 8, 15), added=True, calendar=FIXTURE_CALENDARS["C"]),
    CalendarException(day=date(2023, 11, 1), added=False, calendar=FIXTURE_CALENDARS["D"]),
    CalendarException(day=date(2023, 11, 1), added=True, calendar=FIXTURE_CALENDARS["C"]),
    CalendarException(day=date(2023, 12, 25), added=False, calendar=FIXTURE_CALENDARS["D"]),
    CalendarException(day=date(2023, 12, 25), added=True, calendar=FIXTURE_CALENDARS["C"]),
    CalendarException(day=date(2023, 12, 26), added=False, calendar=FIXTURE_CALENDARS["D"]),
    CalendarException(day=date(2023, 12, 26), added=True, calendar=FIXTURE_CALENDARS["C"]),
    CalendarException(day=date(2024, 1, 1), added=False, calendar=FIXTURE_CALENDARS["D"]),
    CalendarException(day=date(2024, 1, 1), added=True, calendar=FIXTURE_CALENDARS["C"]),
]


FIXTURE_PATTERNS: list[Pattern] = []
FIXTURE_PATTERN_STOPS: list[PatternStop] = []
FIXTURE_TRIPS: list[Trip] = []


def load_schedule_fixture() -> None:
    # Ensure initialization is only done once
    if FIXTURE_PATTERNS:
        return

    with FIXTURE_SCHEDULES_FILE.open() as f:
        data = json.load(f)

    for json_pattern in data["patterns"]:
        pattern = Pattern(
            headsign=json_pattern["headsign"],
            direction=json_pattern["direction"],
            line=FIXTURE_LINES[json_pattern["line"]],
        )
        FIXTURE_PATTERNS.append(pattern)

        for idx, json_stop in enumerate(json_pattern["stops"]):
            pattern_stop = PatternStop(
                pattern=pattern,
                stop=FIXTURE_STOPS[json_stop["stop"]],
                travel_time=timedelta(seconds=json_stop["travel_time"]),
                index=idx,
            )
            FIXTURE_PATTERN_STOPS.append(pattern_stop)

        for json_trip in json_pattern["trips"]:
            trip = Trip(
                wheelchair_accessible=WheelchairAccessibility.ACCESSIBLE,
                departure=timedelta(seconds=json_trip["departure"]),
                pattern=pattern,
                calendar=FIXTURE_CALENDARS[json_trip["calendar"]],
            )
            FIXTURE_TRIPS.append(trip)


load_schedule_fixture()


def load_wkd_fixture_database() -> None:
    Trip.objects.all().delete()
    PatternStop.objects.all().delete()
    Pattern.objects.all().delete()
    CalendarException.objects.all().delete()
    Calendar.objects.all().delete()
    Line.objects.all().delete()
    Stop.objects.all().delete()
    Agency.objects.all().delete()

    FIXTURE_AGENCY.save()
    for stop in FIXTURE_STOPS.values():
        stop.save()
    for line in FIXTURE_LINES.values():
        line.save()
    for calendar in FIXTURE_CALENDARS.values():
        calendar.save()
    for calendar_exception in FIXTURE_CALENDAR_EXCEPTIONS:
        calendar_exception.save()
    for pattern in FIXTURE_PATTERNS:
        pattern.save()
    for pattern_stop in FIXTURE_PATTERN_STOPS:
        pattern_stop.save()
    for trip in FIXTURE_TRIPS:
        trip.save()


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        load_wkd_fixture_database()
