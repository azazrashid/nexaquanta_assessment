from datetime import datetime, date, timedelta, timezone

import pytz


class Datetime:
    def __init__(self, *args):
        self.utc_now = datetime.now(timezone.utc)
        self.timedelta = 0

    @classmethod
    def datetime(cls, diff: int = 0) -> datetime:
        return (
            cls().utc_now + timedelta(hours=diff)
            if diff > 0
            else cls().utc_now + timedelta(hours=diff)
        )

    @classmethod
    def date(cls, diff: int = 0) -> date:
        return cls.datetime(diff=diff).date()

    @classmethod
    def date_num(cls, diff: int = 0) -> int:
        return int(cls.date(diff=diff).strftime("%Y%m%d"))

    @classmethod
    def convert_utc_to_local(cls, utc_dt, time_zone) -> datetime:
        time_zone = pytz.timezone(time_zone)
        utc_timezone = pytz.timezone("UTC")
        local_dt = utc_timezone.localize(utc_dt, is_dst=None).astimezone(time_zone)
        # Remove timezone info to make it naive
        return local_dt.replace(tzinfo=None)

    @classmethod
    def parse_timezone_offset(cls, offset_str):
        """Parses a timezone offset string in the format of ±HH:MM."""
        sign = 1 if offset_str[0] == '+' else -1
        hours, minutes = map(int, offset_str[1:].split(':'))
        return sign * (hours * 60 + minutes)