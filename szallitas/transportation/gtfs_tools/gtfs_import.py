import csv
from typing import Iterable

from ..models import *


class GTFSLoader:
    def __init__(self):
        self.agency_mapping: dict[str, int] = dict()
        self.stop_mapping: dict[str, int] = dict()

    def import_agencies(self, file_handler: Iterable[str]) -> None:
        for row in csv.DictReader(file_handler):
            agency_id = row["agency_id"]
            name = row["agency_name"]
            website = row["agency_url"]
            timezone = row["agency_timezone"]
            telephone = row.get("agency_phone")
            new_agency = Agency.objects.update_or_create(
                name=name, website=website, timezone=timezone, telephone=telephone
            )[0]
            self.agency_mapping[agency_id] = new_agency.id

    def import_stops(self, file_handler: Iterable[str]) -> None:
        for row in csv.DictReader(file_handler):
            stop_id = row["stop_id"]
            code = row.get("stop_code")
            name = row["stop_name"]
            lat = row["stop_lat"]
            lon = row["stop_lon"]
            wheelchair_accessible = int(row.get("wheelchair_boarding", 0))
            new_stop = Stop.objects.update_or_create(
                name=name, code=code, lat=lat, lon=lon, wheelchair_accessible=wheelchair_accessible
            )[0]
            self.stop_mapping[stop_id] = new_stop.id
