from ..models import PatternStop

Hour = str
Minutes = list[str]
CalendarName = str
DepartureBoard = list[tuple[Hour, Minutes]]
DepartureBoardByCalendar = list[tuple[CalendarName, DepartureBoard]]


def generate_tabular_timetable(_pattern_stop: PatternStop) -> DepartureBoardByCalendar:
    return [
        (
            "Weekday",
            [(f"{h:0>2}", ["00", "20", "40"]) for h in range(6, 21)],
        ),
        (
            "Saturday",
            [(f"{h:0>2}", ["15", "45"]) for h in range(7, 20)],
        ),
        (
            "Sunday",
            [(f"{h:0>2}", ["30"]) for h in range(8, 19)],
        ),
    ]
