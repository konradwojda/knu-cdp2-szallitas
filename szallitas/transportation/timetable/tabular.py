from collections import defaultdict
from typing import List, Tuple

from ..models import PatternStop

Hour = str
Minutes = list[str]
CalendarName = str
DepartureBoard = list[tuple[Hour, Minutes]]
DepartureBoardByCalendar = list[tuple[CalendarName, DepartureBoard]]


def generate_tabular_timetable(pattern_stop: PatternStop) -> DepartureBoardByCalendar:
    timetable: DepartureBoardByCalendar = []

    trips = pattern_stop.pattern.trip_set.all()

    timetables: defaultdict[str, defaultdict[str, List[str]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for trip in trips:
        departure_time = trip.departure + pattern_stop.travel_time
        hours, remainder = divmod(departure_time.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)

        calendar_name = trip.calendar.name

        hour = str(int(hours)).zfill(2)
        minute = str(int(minutes)).zfill(2)

        timetables[calendar_name][hour].append(minute)

    for calendar_name, timetable_board in timetables.items():
        timetable.append((calendar_name, list(timetable_board.items())))

    return timetable
