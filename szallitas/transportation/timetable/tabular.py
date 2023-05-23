from collections import defaultdict

from ..models import PatternStop

Hour = str
Minutes = list[str]
CalendarName = str
DepartureBoard = list[tuple[Hour, Minutes]]
DepartureBoardByCalendar = list[tuple[CalendarName, DepartureBoard]]


def generate_tabular_timetable(pattern_stop: PatternStop) -> DepartureBoardByCalendar:
    # Collect all departures and figure out the time range
    boards: defaultdict[str, defaultdict[int, list[int]]] = defaultdict(lambda: defaultdict(list))
    min_hours = 8
    max_hours = 20

    for trip in pattern_stop.pattern.trip_set.all():
        seconds = int((trip.departure + pattern_stop.travel_time).total_seconds())
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        boards[trip.calendar.name][hours].append(minutes)

        min_hours = min(min_hours, hours)
        max_hours = max(max_hours, hours)

    # Generate the timetables
    return [
        (
            calendar,
            [
                (f"{h:02}", [f"{m:02}" for m in sorted(boards[calendar][h])])
                for h in range(min_hours, max_hours + 1)
            ],
        )
        for calendar in sorted(boards)
    ]
