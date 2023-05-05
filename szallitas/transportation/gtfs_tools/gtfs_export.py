import csv
from dataclasses import dataclass
from typing import IO, Any, Iterable

from ..models import Agency, Line, Stop


@dataclass(frozen=True)
class FieldMapping:
    model: str
    gtfs: str
    fallback: str = ""


class GTFSExporter:
    @staticmethod
    def export_simple_table(
        to: IO[str], objects: Iterable[Any], fields: list[FieldMapping]
    ) -> None:
        w = csv.writer(to)
        w.writerow(f.gtfs for f in fields)
        w.writerows((getattr(obj, f.model) or f.fallback for f in fields) for obj in objects)

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
