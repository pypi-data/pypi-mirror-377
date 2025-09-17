from datetime import datetime, timezone
import pytz

class DateUtility:

    @staticmethod
    def date_time_to_est(date_time_str: str) -> datetime:
        eastern = pytz.timezone("America/New_York")
        # Parse the UTC datetime string from Splunk
        date_time_utc = datetime.fromisoformat(date_time_str.replace("Z", "+00:00"))
        return date_time_utc.astimezone(eastern)

    @staticmethod
    def date_time_to_utc(date_time_str: str) -> datetime:
        dt = datetime.fromisoformat(date_time_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
