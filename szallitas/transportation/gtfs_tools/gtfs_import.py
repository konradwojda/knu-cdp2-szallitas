import csv
from datetime import datetime
from typing import Iterable

from ..models import *


class GTFSLoader:
    def __init__(self):
        self.agency_mapping: dict[str, int] = dict()
        self.stop_mapping: dict[str, int] = dict()
        self.line_mapping: dict[str, int] = dict()
        self.calendar_mapping: dict[str, int] = dict()

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

    def import_lines(self, file_handler: Iterable[str]) -> None:
        for row in csv.DictReader(file_handler):
            line_id = row["route_id"]
            code = row["route_short_name"]
            description = row["route_long_name"]
            line_type = int(row["route_type"])
            agency_id = row["agency_id"]
            agency = Agency.objects.get(id=self.agency_mapping[agency_id])
            new_line = Line.objects.update_or_create(
                code=code, description=description, line_type=line_type, agency=agency
            )[0]
            self.line_mapping[line_id] = new_line.id

    def import_calendars(self, file_handler: Iterable[str]) -> None:
        for row in csv.DictReader(file_handler):
            service_id = row["service_id"]
            start_date = datetime.strptime(row["start_date"], "%Y%m%d")
            end_date = datetime.strptime(row["end_date"], "%Y%m%d")
            monday = row["monday"]
            tuesday = row["tuesday"]
            wednesday = row["wednesday"]
            thursday = row["thursday"]
            friday = row["friday"]
            saturday = row["saturday"]
            sunday = row["sunday"]
            new_calendar = Calendar.objects.update_or_create(
                name=service_id,
                start_date=start_date,
                end_date=end_date,
                monday=monday,
                tuesday=tuesday,
                wednesday=wednesday,
                thursday=thursday,
                friday=friday,
                saturday=saturday,
                sunday=sunday,
            )[0]
            self.calendar_mapping[service_id] = new_calendar.id

    def import_calendar_exceptions(self, file_handler: Iterable[str]) -> None:
        for row in csv.DictReader(file_handler):
            service_id = row["service_id"]
            day = datetime.strptime(row["date"], "%Y%m%d")
            added = row["exception_type"] == 1
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
            else:
                calendar = Calendar.objects.get(id=self.calendar_mapping[service_id])
            CalendarException.objects.update_or_create(day=day, added=added, calendar=calendar)
