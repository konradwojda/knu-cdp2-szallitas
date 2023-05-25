import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
from io import TextIOWrapper
from itertools import islice
from pathlib import Path
from typing import IO, Final, Iterable, Mapping
from zipfile import ZipFile

from django.db import connection, transaction
from django.db.models import Max

from ..models import Agency, Calendar, CalendarException, Line, Pattern, PatternStop, Stop, Trip


class CalendarFileNotFound(Exception):
    """Calendar file was not found in gtfs zip"""


@dataclass
class Stoptime:
    stop_id: str
    stop_seq: int
    departure: str


@dataclass(frozen=True)
class PatternStopData:
    stop_id: str
    travel_time: timedelta


@dataclass(frozen=True)
class PatternData:
    headsign: str
    direction: int | None
    line_id: str
    stops: tuple[PatternStopData, ...]


class GTFSLoader:
    BATCH_SIZE: Final[int] = 999
    # According to https://docs.djangoproject.com/en/4.2/ref/models/querysets/#bulk-create
    # sqlite can handle at most 999 rows inserted at one time.

    def __init__(self):
        self.agency_mapping: dict[str, int] = dict()
        self.stop_mapping: dict[str, int] = dict()
        self.line_mapping: dict[str, int] = dict()
        self.calendar_mapping: dict[str, int] = dict()
        self.stop_times: dict[str, list[Stoptime]] = {}
        self.pattern_ids: dict[PatternData, int] = {}

        # Temporary caches for bulk-insertion of trips
        self.patterns_to_add: list[Pattern] = []
        self.pattern_data_to_add: list[tuple[int, PatternData]] = []
        self.trips_to_add: list[Trip] = []

        # Counters for generating Pattern IDs. These need to be eagerly generated
        # for PatternStop insertion. Otherwise, after a Pattern has been inserted,
        # and before its PatternStops are inserted; a fetch to the database for the ID
        # would need to be performed.
        self.pattern_id_counter: int = (Pattern.objects.aggregate(Max("id"))["id__max"] or 0) + 1

    @transaction.atomic
    def from_zip(self, zip_path: str | Path | IO[bytes]) -> None:
        with ZipFile(zip_path, "r") as zip:
            if "calendar.txt" not in zip.namelist() and "calendar_dates.txt" not in zip.namelist():
                raise CalendarFileNotFound()
            with zip.open("agency.txt", "r") as stream:
                self.import_agencies(TextIOWrapper(stream, encoding="utf-8-sig", newline=""))
            with zip.open("routes.txt", "r") as stream:
                self.import_lines(TextIOWrapper(stream, encoding="utf-8-sig", newline=""))
            with zip.open("stops.txt", "r") as stream:
                self.import_stops(TextIOWrapper(stream, encoding="utf-8-sig", newline=""))
            if "calendar.txt" in zip.namelist():
                with zip.open("calendar.txt", "r") as stream:
                    self.import_calendars(TextIOWrapper(stream, encoding="utf-8-sig", newline=""))
            if "calendar_dates.txt" in zip.namelist():
                with zip.open("calendar_dates.txt", "r") as stream:
                    self.import_calendar_exceptions(
                        TextIOWrapper(stream, encoding="utf-8-sig", newline="")
                    )
            with zip.open("trips.txt", "r") as trips_stream, zip.open(
                "stop_times.txt", "r"
            ) as stop_times_stream:
                self.import_patterns(
                    TextIOWrapper(trips_stream, encoding="utf-8-sig", newline=""),
                    TextIOWrapper(stop_times_stream, encoding="utf-8-sig", newline=""),
                )

    def import_agencies(self, file_handler: Iterable[str]) -> None:
        for row in csv.DictReader(file_handler):
            agency_id = row["agency_id"]
            name = row["agency_name"]
            website = row["agency_url"]
            timezone = row["agency_timezone"]
            telephone = row.get("agency_phone")
            new_agency = Agency.objects.create(
                name=name, website=website, timezone=timezone, telephone=telephone
            )
            self.agency_mapping[agency_id] = new_agency.id

    def import_stops(self, file_handler: Iterable[str]) -> None:
        for row in csv.DictReader(file_handler):
            stop_id = row["stop_id"]
            code = row.get("stop_code")
            name = row["stop_name"]
            lat = row["stop_lat"]
            lon = row["stop_lon"]
            wheelchair_accessible = int(row.get("wheelchair_boarding") or 0)

            new_stop = Stop.objects.create(
                name=name, code=code, lat=lat, lon=lon, wheelchair_accessible=wheelchair_accessible
            )
            self.stop_mapping[stop_id] = new_stop.id

    def import_lines(self, file_handler: Iterable[str]) -> None:
        for row in csv.DictReader(file_handler):
            line_id = row["route_id"]
            code = row["route_short_name"]
            description = row["route_long_name"]
            line_type = int(row["route_type"])
            agency_id = row["agency_id"]
            new_line = Line.objects.create(
                code=code,
                description=description,
                line_type=line_type,
                agency_id=self.agency_mapping[agency_id],
            )
            self.line_mapping[line_id] = new_line.id

    def import_calendars(self, file_handler: Iterable[str]) -> None:
        for row in csv.DictReader(file_handler):
            service_id = row["service_id"]
            desc = row.get("service_desc") or service_id
            start_date = datetime.strptime(row["start_date"], "%Y%m%d")
            end_date = datetime.strptime(row["end_date"], "%Y%m%d")
            monday = row["monday"]
            tuesday = row["tuesday"]
            wednesday = row["wednesday"]
            thursday = row["thursday"]
            friday = row["friday"]
            saturday = row["saturday"]
            sunday = row["sunday"]
            new_calendar = Calendar.objects.create(
                name=desc,
                start_date=start_date,
                end_date=end_date,
                monday=monday,
                tuesday=tuesday,
                wednesday=wednesday,
                thursday=thursday,
                friday=friday,
                saturday=saturday,
                sunday=sunday,
            )
            self.calendar_mapping[service_id] = new_calendar.id

    def import_calendar_exceptions(self, file_handler: Iterable[str]) -> None:
        for row in csv.DictReader(file_handler):
            service_id = row["service_id"]
            day = datetime.strptime(row["date"], "%Y%m%d")
            added = row["exception_type"] == "1"
            if service_id not in self.calendar_mapping.keys():
                calendar = Calendar.objects.create(
                    name=service_id,
                    start_date="2000-01-01",
                    monday=0,
                    tuesday=0,
                    wednesday=0,
                    thursday=0,
                    friday=0,
                    saturday=0,
                    sunday=0,
                )
                self.calendar_mapping[service_id] = calendar.id
                calendar_id = calendar.id
            else:
                calendar_id = self.calendar_mapping[service_id]
            CalendarException.objects.create(day=day, added=added, calendar_id=calendar_id)

    def load_stop_times(self, stop_times_fh: Iterable[str]) -> None:
        self.stop_times.clear()
        for row in csv.DictReader(stop_times_fh):
            pickup_type = row.get("pickup_type")
            drop_off_type = row.get("drop_off_type")
            if pickup_type == "1" and drop_off_type == "1":
                continue
            trip_id = row["trip_id"]
            stop_id = row["stop_id"]
            stop_seq = int(row["stop_sequence"])
            departure = row["departure_time"]
            if trip_id not in self.stop_times:
                self.stop_times[trip_id] = [Stoptime(stop_id, stop_seq, departure)]
            else:
                self.stop_times[trip_id].append(Stoptime(stop_id, stop_seq, departure))

        for stop_time in self.stop_times.values():
            stop_time.sort(key=lambda x: x.stop_seq)

    def load_trip(self, row: Mapping[str, str]) -> None:
        line_id = row["route_id"]
        service_id = row["service_id"]
        trip_id = row["trip_id"]
        headsign = (
            row.get("trip_headsign")
            or Stop.objects.get(id=self.stop_mapping[self.stop_times[trip_id][-1].stop_id]).name
        )
        direction = int(row["direction_id"]) if "direction_id" in row else None
        wheelchair_accessible = int(row.get("wheelchair_accessible") or 0)

        pattern_stops: list[PatternStopData] = []
        trip_start_time = get_time_as_timedelta(self.stop_times[trip_id][0].departure)
        for elem in self.stop_times[trip_id]:
            travel_time = get_time_as_timedelta(elem.departure) - trip_start_time
            pattern_stops.append(PatternStopData(elem.stop_id, travel_time))

        pattern_data = PatternData(headsign, direction, line_id, tuple(pattern_stops))
        pattern_id = self.pattern_ids.get(pattern_data)
        if not pattern_id:
            pattern_id = self.pattern_id_counter
            self.pattern_id_counter += 1

            self.pattern_ids[pattern_data] = pattern_id
            self.patterns_to_add.append(
                Pattern(
                    id=pattern_id,
                    headsign=headsign,
                    direction=direction,
                    line_id=self.line_mapping[line_id],
                )
            )
            self.pattern_data_to_add.append((pattern_id, pattern_data))

        self.trips_to_add.append(
            Trip(
                wheelchair_accessible=wheelchair_accessible,
                departure=get_time_as_timedelta(self.stop_times[trip_id][0].departure),
                pattern_id=pattern_id,
                calendar_id=self.calendar_mapping[service_id],
            )
        )

    def insert_current_batch(self) -> None:
        Pattern.objects.bulk_create(self.patterns_to_add)
        Trip.objects.bulk_create(self.trips_to_add)
        PatternStop.objects.bulk_create(
            PatternStop(
                pattern_id=pattern_id,
                stop_id=self.stop_mapping[pattern_stop.stop_id],
                travel_time=pattern_stop.travel_time,
                index=idx,
            )
            for pattern_id, pattern_data in self.pattern_data_to_add
            for idx, pattern_stop in enumerate(pattern_data.stops)
        )

        self.patterns_to_add.clear()
        self.pattern_data_to_add.clear()
        self.trips_to_add.clear()

    def import_patterns(self, trips_fh: Iterable[str], stop_times_fh: Iterable[str]) -> None:
        self.load_stop_times(stop_times_fh)

        trips = csv.DictReader(trips_fh)
        while batch := list(islice(trips, self.BATCH_SIZE)):
            for trip in batch:
                self.load_trip(trip)
            self.insert_current_batch()


def clear_tables() -> None:
    cur = connection.cursor()
    cur.execute('DELETE FROM "transportation_trip";')
    cur.execute('DELETE FROM "transportation_patternstop";')
    cur.execute('DELETE FROM "transportation_pattern";')
    cur.execute('DELETE FROM "transportation_calendarexception";')
    cur.execute('DELETE FROM "transportation_calendar";')
    cur.execute('DELETE FROM "transportation_line";')
    cur.execute('DELETE FROM "transportation_stop";')
    cur.execute('DELETE FROM "transportation_agency";')


def get_time_as_timedelta(time_str: str) -> timedelta:
    hours, minutes, seconds = time_str.split(":")
    return timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds))
