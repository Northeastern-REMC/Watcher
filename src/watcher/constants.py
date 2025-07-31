from datetime import datetime
from zoneinfo import ZoneInfo

NREMC_TIMEZONE_NAME = "America/New_York"
NREMC_TIMEZONE = ZoneInfo(NREMC_TIMEZONE_NAME)
IGNITION_EPOCH = datetime(2024, 12, 1, 0, 0, 0, 0, NREMC_TIMEZONE)
