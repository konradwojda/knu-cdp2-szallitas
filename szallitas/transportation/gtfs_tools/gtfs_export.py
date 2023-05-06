import csv
from dataclasses import dataclass
from typing import IO, Any, Callable, Iterable

from ..models import Agency, Calendar, CalendarException, Line, Pattern, Stop


def seconds_to_gtfs_time(s: int) -> str:
    """seconds_to_gtfs_time converts seconds-since-midnight into a GTFS-compliant string."""
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:0>2}:{m:0>2}:{s:0>2}"


@dataclass(frozen=True)
class FieldMapping:
    model: str
    gtfs: str
    fallback: str = ""
    converter: Callable[[Any], Any] | None = None


class GTFSExporter:
    @staticmethod
    def export_simple_table(
        to: IO[str], objects: Iterable[Any], fields: list[FieldMapping]
    ) -> None:
        w = csv.writer(to)
        w.writerow(f.gtfs for f in fields)
        w.writerows(
            (
                f.converter(getattr(obj, f.model))
                if f.converter
                else (getattr(obj, f.model) or f.fallback)
                for f in fields
            )
            for obj in objects
        )

    @staticmethod
    def export_agencies(to: IO[str]) -> None:
        GTFSExporter.export_simple_table(
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

    @staticmethod
    def export_routes(to: IO[str]) -> None:
        GTFSExporter.export_simple_table(
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

    @staticmethod
    def export_stops(to: IO[str]) -> None:
        GTFSExporter.export_simple_table(
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

    @staticmethod
    def export_calendars(to: IO[str]) -> None:
        GTFSExporter.export_simple_table(
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

    @staticmethod
    def export_calendars_dates(to: IO[str]) -> None:
        GTFSExporter.export_simple_table(
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

    @staticmethod
    def export_trips_and_stop_times(f_trips: IO[str], f_times: IO[str]) -> None:
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
            pattern_stops = pattern.pattern_stop_set.all()

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
