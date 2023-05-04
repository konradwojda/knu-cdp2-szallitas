import csv
from typing import Iterable

from ..models import *


class GTFSLoader:
    def __init__(self):
        self.agency_mapping: dict[str, int] = dict()

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
