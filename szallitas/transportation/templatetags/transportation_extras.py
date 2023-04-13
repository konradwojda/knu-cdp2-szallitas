from django import template

register = template.Library()

ROUTE_TYPE_DATA: dict[int, str] = {
    0: "🚊",
    1: "🚇",
    2: "🚆",
    3: "🚌",
    4: "⛴️",
    5: "🚋",
    6: "🚠",
    7: "🚞",
    11: "🚎",
    12: "🚝",
}


@register.filter(name="line_emoji")
def line_type_to_emoji(value: int) -> str:
    return ROUTE_TYPE_DATA[value]
