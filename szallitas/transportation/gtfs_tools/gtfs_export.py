import csv
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import IO, Any, Callable, Iterable
from zipfile import ZIP_DEFLATED, ZipFile

from ..models import Agency, Calendar, CalendarException, Line, Pattern, Stop


def seconds_to_gtfs_time(s: int) -> str:
    """seconds_to_gtfs_time converts seconds-since-midnight into a GTFS-compliant string."""
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:0>2}:{m:0>2}:{s:0>2}"


def open_table(path: Path) -> IO[str]:
    return path.open(mode="w", encoding="utf-8", newline="")


@dataclass(frozen=True)
class FieldMapping:
    """FieldMapping describes mapping from model fields into GTFS columns,
    with the following parameters:

    - model: name of Model class attribute
    - gtfs: name of GTFS column
    - fallback: string to use if Model attribute is None. Defaults to an empty string,
      as str(None) == "None", which is not how None should be serialized into CSV.
    - converter: if present, `str(converter(attr))` will be used
      when saving a field into CSV. If None (default):
      `str(attr) if attr is not None else fallback` is used.
    """

    model: str
    gtfs: str
    fallback: str = ""
    converter: Callable[[Any], Any] | None = None

    def serialize_attribute(self, attr: Any) -> Any:
        # NOTE: csv.writer automatically calls str on the result

        if self.converter:
            return self.converter(attr)
        else:
            return attr if attr is not None else self.fallback


def export_simple_table(
    to: IO[str],
    objects: Iterable[Any],
    fields: list[FieldMapping],
) -> None:
    """export_simple_table exports model objects into GTFS as per the provided FieldMappings"""
    w = csv.writer(to)
    w.writerow(f.gtfs for f in fields)
    w.writerows((f.serialize_attribute(getattr(obj, f.model)) for f in fields) for obj in objects)


def export_agencies(to: IO[str]) -> None:
    """export_agencies exports all known agencies into GTFS agency.txt table"""
    export_simple_table(
        to,
        Agency.objects.all(),
        [
            FieldMapping(model="id", gtfs="agency_id"),
            FieldMapping(model="name", gtfs="agency_name"),
            FieldMapping(model="website", gtfs="agency_url"),
            FieldMapping(model="timezone", gtfs="agency_timezone", fallback="UTC"),
            FieldMapping(model="telephone", gtfs="agency_phone"),
        ],
    )


def export_routes(to: IO[str]) -> None:
    """export_routes exports all known lines into GTFS routes.txt table"""
    export_simple_table(
        to,
        Line.objects.all(),
        [
            FieldMapping(model="id", gtfs="route_id"),
            FieldMapping(model="agency_id", gtfs="agency_id"),
            FieldMapping(model="code", gtfs="route_short_name"),
            FieldMapping(model="description", gtfs="route_long_name"),
            FieldMapping(model="line_type", gtfs="route_type"),
        ],
    )


def export_stops(to: IO[str]) -> None:
    """export_stops exports all known stops into GTFS stops.txt table"""
    export_simple_table(
        to,
        Stop.objects.all(),
        [
            FieldMapping(model="id", gtfs="stop_id"),
            FieldMapping(model="name", gtfs="stop_name"),
            FieldMapping(model="code", gtfs="stop_code"),
            FieldMapping(model="lat", gtfs="stop_lat"),
            FieldMapping(model="lon", gtfs="stop_lon"),
            FieldMapping(model="wheelchair_accessible", gtfs="wheelchair_boarding"),
        ],
    )


def export_calendars(to: IO[str]) -> None:
    """export_calendars exports all known calendars into GTFS calendar.txt table"""
    export_simple_table(
        to,
        Calendar.objects.all(),
        [
            FieldMapping(model="id", gtfs="service_id"),
            FieldMapping(model="monday", gtfs="monday", converter=int),
            FieldMapping(model="tuesday", gtfs="tuesday", converter=int),
            FieldMapping(model="wednesday", gtfs="wednesday", converter=int),
            FieldMapping(model="thursday", gtfs="thursday", converter=int),
            FieldMapping(model="friday", gtfs="friday", converter=int),
            FieldMapping(model="saturday", gtfs="saturday", converter=int),
            FieldMapping(model="sunday", gtfs="sunday", converter=int),
            FieldMapping(
                model="start_date",
                gtfs="start_date",
                converter=lambda d: d.strftime("%Y%m%d"),
            ),
            FieldMapping(
                model="end_date",
                gtfs="end_date",
                converter=lambda d: d.strftime("%Y%m%d"),
            ),
            FieldMapping(model="name", gtfs="service_desc"),
        ],
    )


def export_calendars_dates(to: IO[str]) -> None:
    """export_calendars_dates exports all known calendar exceptions
    into GTFS calendar_dates.txt table"""
    export_simple_table(
        to,
        CalendarException.objects.all(),
        [
            FieldMapping(model="calendar_id", gtfs="service_id"),
            FieldMapping(
                model="day",
                gtfs="date",
                converter=lambda d: d.strftime("%Y%m%d"),
            ),
            FieldMapping(
                model="added",
                gtfs="exception_type",
                converter=lambda added: "1" if added else "2",
            ),
        ],
    )


def export_trips_and_stop_times(f_trips: IO[str], f_times: IO[str]) -> None:
    """export_trips_and_stop_times exports all patterns and their trips
    into GTFS trips.txt and stop_times.txt tables."""
    w_trips = csv.writer(f_trips)
    w_trips.writerow(
        (
            "route_id",
            "service_id",
            "trip_id",
            "trip_headsign",
            "direction_id",
            "wheelchair_accessible",
        )
    )

    w_times = csv.writer(f_times)
    w_times.writerow(("trip_id", "stop_sequence", "stop_id", "arrival_time", "departure_time"))

    for pattern in Pattern.objects.all():
        pattern_stops = list(pattern.pattern_stop_set.all())

        for trip in pattern.trip_set.all():
            w_trips.writerow(
                (
                    pattern.line_id,
                    trip.calendar_id,
                    trip.id,
                    pattern.headsign or "",
                    pattern.direction if pattern.direction is not None else "",
                    trip.wheelchair_accessible,
                )
            )

            for pattern_stop in pattern_stops:
                time_at_stop = trip.departure + pattern_stop.travel_time
                gtfs_time_at_stop = seconds_to_gtfs_time(round(time_at_stop.total_seconds()))
                w_times.writerow(
                    (
                        trip.id,
                        pattern_stop.index,
                        pattern_stop.stop_id,
                        gtfs_time_at_stop,
                        gtfs_time_at_stop,
                    )
                )


def export_all(to_zip: IO[bytes]) -> None:
    """export_all exports currently stored data as GTFS.
    The resulting ZIP archive is written to the provided handle.
    """

    # NOTE: TemporaryDirectory necessary for simultaneous opening
    #       of trips.txt and stop_times.txt

    with TemporaryDirectory(prefix="szallitas-gtfs-export") as temp_dir_str:
        temp_dir = Path(temp_dir_str)

        # Export files
        with open_table(temp_dir / "agency.txt") as f:
            export_agencies(f)
        with open_table(temp_dir / "routes.txt") as f:
            export_routes(f)
        with open_table(temp_dir / "stops.txt") as f:
            export_stops(f)
        with open_table(temp_dir / "calendar.txt") as f:
            export_calendars(f)
        with open_table(temp_dir / "calendar_dates.txt") as f:
            export_calendars_dates(f)
        with (
            open_table(temp_dir / "trips.txt") as f_trips,
            open_table(temp_dir / "stop_times.txt") as f_times,
        ):
            export_trips_and_stop_times(f_trips, f_times)

        # Export to GTFS zip
        with ZipFile(to_zip, mode="w", compression=ZIP_DEFLATED) as archive:
            file_names = [
                "agency.txt",
                "routes.txt",
                "stops.txt",
                "calendar.txt",
                "calendar_dates.txt",
                "trips.txt",
                "stop_times.txt",
            ]

            for file_name in file_names:
                archive.write(temp_dir / file_name, file_name)
