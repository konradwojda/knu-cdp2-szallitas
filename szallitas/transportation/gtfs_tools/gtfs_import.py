import csv
from datetime import datetime, timedelta
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

    def import_patterns(self, trips_fh: Iterable[str], stop_times_fh: Iterable[str]) -> None:
        stop_times: dict[str, list[tuple[str, str, str]]] = dict()
        for row in csv.DictReader(stop_times_fh):
            trip_id = row["trip_id"]
            stop_id = row["stop_id"]
            stop_seq = row["stop_sequence"]
            departure = row["departure_time"]
            if trip_id not in stop_times.keys():
                stop_times[trip_id] = [(stop_id, stop_seq, departure)]
            else:
                stop_times[trip_id].append((stop_id, stop_seq, departure))
        for stop_time in stop_times.values():
            stop_time.sort(key=lambda x: int(x[1]))
        for row in csv.DictReader(trips_fh):
            line_id = row["route_id"]
            service_id = row["service_id"]
            trip_id = row["trip_id"]
            headsign = row.get("trip_headsign")
            direction = row.get("direction_id")
            if direction:
                direction = int(direction)
            wheelchair_accessible = row.get("wheelchair_accessible")
            if wheelchair_accessible:
                wheelchair_accessible = int(wheelchair_accessible)
            else:
                wheelchair_accessible = 0

            # TODO: Cache patterns instead of query every time
            pattern = Pattern.objects.update_or_create(
                headsign=headsign,
                direction=direction,
                line=Line.objects.get(id=self.line_mapping[line_id]),
            )[0]
            previous_departure = get_time_as_timedelta(stop_times[trip_id][0][2])
            for elem in stop_times[trip_id]:
                travel_time = get_time_as_timedelta(elem[2]) - previous_departure
                PatternStop.objects.update_or_create(
                    pattern=pattern,
                    stop=Stop.objects.get(id=self.stop_mapping[elem[0]]),
                    travel_time=travel_time,
                    index=elem[1],
                )
            Trip.objects.update_or_create(
                wheelchair_accessible=wheelchair_accessible,
                departure=get_time_as_timedelta(stop_times[trip_id][0][2]),
                pattern=pattern,
                calendar=Calendar.objects.get(id=self.calendar_mapping[service_id]),
            )


def get_time_as_timedelta(time_str: str) -> timedelta:
    hours, minutes, seconds = time_str.split(":")
    return timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds))
