from typing import Any, Optional

from django.core.management.base import BaseCommand, CommandParser

from ...gtfs_tools.gtfs_import import GTFSLoader, clear_tables


class Command(BaseCommand):
    help = "Import data from GTFS zip file. By default it cleans database from previous data."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--no-clean",
            action="store_true",
            help="Do not clean database before inserting new data, may result some errors",
        )
        parser.add_argument("path", type=str, help="Path to zip archive with GTFS files")

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        if not options["no_clean"]:
            clear_tables()
        else:
            self.stdout.write("Skipped database cleaning. It may cause errors!")

        self.stdout.write("Loading data")
        GTFSLoader().from_zip(options["path"])

        self.stdout.write("Data loaded successfully")
