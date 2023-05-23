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

    timetables: defaultdict[str, List[Tuple[int, int]]] = defaultdict(list)

    for trip in trips:
        departure_time = trip.departure + pattern_stop.travel_time
        hours, remainder = divmod(departure_time.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)

        calendar_name = trip.calendar.name

        hour = int(hours)
        minute = int(minutes)

        timetables[calendar_name].append((hour, minute))

    for calendar_name, timetable_board in timetables.items():
        sorted_timetable = sorted(timetable_board, key=lambda x: x[0])

        sorted_hours = [hour for hour, _ in sorted_timetable]
        sorted_minutes = [minute for _, minute in sorted_timetable]

        min_hour = min(sorted_hours)
        max_hour = max(sorted_hours)
        all_hours = list(range(min_hour, max_hour + 1))

        grouped_minutes: List[List[int]] = [[] for _ in range(len(all_hours))]
        for hour, minute in zip(sorted_hours, sorted_minutes):
            index = all_hours.index(hour)
            grouped_minutes[index].append(minute)

        timetable.append(
            (
                calendar_name,
                [
                    (
                        str(hour).zfill(2),
                        [str(minute).zfill(2) for minute in minutes],
                    )
                    for hour, minutes in zip(all_hours, grouped_minutes)
                ],
            )
        )

    return timetable
