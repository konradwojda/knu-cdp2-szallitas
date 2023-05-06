from typing import Any, Optional

from django.core.management.base import BaseCommand, CommandParser

from ...gtfs_tools import gtfs_export


class Command(BaseCommand):
    help = "Export currently stored data as GTFS."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("path", type=str, help="Path to the output ZIP file")

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        with open(options["path"], mode="wb") as f:
            gtfs_export.export_all(f)
