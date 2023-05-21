from datetime import timedelta, time
from typing import List, Tuple
from ..models import PatternStop

Hour = str
Minutes = List[str]
CalendarName = str
DepartureBoard = List[Tuple[Hour, Minutes]]
DepartureBoardByCalendar = List[Tuple[CalendarName, DepartureBoard]]

def generate_tabular_timetable(_pattern_stop: PatternStop) -> DepartureBoardByCalendar:
    timetable: DepartureBoardByCalendar = []

    trips = _pattern_stop.pattern.trip_set.all()

    for trip in trips:
        departure_time = trip.departure + _pattern_stop.travel_time
        departure_time += timedelta(days=1)
        departure_time = departure_time.total_seconds() % (24 * 3600)
        departure_time = time(hour=int(departure_time // 3600), minute=int((departure_time // 60) % 60))

        calendar_name = trip.calendar.name

        departure_board: DepartureBoard = []
        for entry in timetable:
            if entry[0] == calendar_name:
                departure_board = entry[1]
                break

        if not departure_board:
            timetable.append((calendar_name, departure_board))

        hour = str(departure_time.hour).zfill(2)
        minutes = str(departure_time.minute).zfill(2)

        for entry in departure_board:
            if entry[0] == hour:
                entry[1].append(minutes)
                break
        else:
            departure_board.append((hour, [minutes]))

    return timetable
