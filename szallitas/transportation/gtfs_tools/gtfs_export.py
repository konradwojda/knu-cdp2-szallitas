import csv
import logging
from typing import IO

from ..models import Agency

logger = logging.getLogger(__name__)


class GTFSExporter:
    @staticmethod
    def export_agencies(to: IO[str]) -> None:
        w = csv.writer(to)
        w.writerow(("agency_id", "agency_name", "agency_url", "agency_timezone", "agency_phone"))

        for agency in Agency.objects.all():
            # Warn if required GTFS fields are missing
            if not agency.timezone:
                logger.warn(
                    "Agency %s (ID %d) has no timezone - using UTC",
                    agency.name,
                    agency.id,
                )

            w.writerow(
                (
                    agency.id,
                    agency.name,
                    agency.website,
                    agency.timezone or "UTC",
                    agency.telephone or "",
                )
            )
