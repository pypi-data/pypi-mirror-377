"""
This module provides utility functions for the feature factory.
"""

from typing import Optional, List
from datetime import datetime, timedelta
import calendar


def widget_prefix(prefix: Optional[str]) -> str:
    """
    Puts prefix in front of notebook name based on its location
    """

    prefix = "" if prefix is None else prefix

    return f"[{prefix}] "


# pylint: disable=too-many-branches, too-many-statements
# pylint: disable=C
def generate_timestamp_range(start_timestamp: str, end_timestamp: str, interval: str) -> List[str]:
    """
    Generate a list of timestamps between start_timestamp and end_timestamp with the specified interval.

    Parameters:
    -----------
    start_timestamp : str
        The start timestamp in 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' format.
    end_timestamp : str
        The end timestamp in 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' format.
    interval : str
        The interval for timestamp generation, e.g., '1 day', '2 hours', '30 minutes', '1 month', '1 week'.

    Returns:
    --------
    list of str
        A list of timestamps in 'YYYY-MM-DD HH:MM:SS' format.

    Raises:
    -------
    ValueError
        If the interval format is incorrect or unsupported.
    """

    if isinstance(start_timestamp, str):
        start_timestamp = (
            datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S")
            if " " in start_timestamp
            else datetime.strptime(start_timestamp, "%Y-%m-%d")
        )
    if isinstance(end_timestamp, str):
        end_timestamp = (
            datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S")
            if " " in end_timestamp
            else datetime.strptime(end_timestamp, "%Y-%m-%d")
        )

    try:
        amount, unit = interval.split()
        amount = int(amount)
    except ValueError as exc:
        raise ValueError("Interval must be in the format '<number> <unit>', e.g., '1 day', '2 hours'.") from exc

    interval_mapping = {
        "day": "days",
        "days": "days",
        "hour": "hours",
        "hours": "hours",
        "minute": "minutes",
        "minutes": "minutes",
        "second": "seconds",
        "seconds": "seconds",
        "month": "months",
        "months": "months",
        "week": "weeks",
        "weeks": "weeks",
    }

    if unit not in interval_mapping:
        raise ValueError(
            f"Unsupported interval unit: {unit}. Supported units are day(s), hour(s), minute(s), second(s), month(s), week(s)."
        )

    current_timestamp = start_timestamp
    timestamp_range = []

    def add_months(dt, months):
        month = dt.month - 1 + months
        year = dt.year + month // 12
        month = month % 12 + 1
        day = min(dt.day, calendar.monthrange(year, month)[1])
        return dt.replace(year=year, month=month, day=day)

    def is_first_day_of_month(dt):
        return dt.day == 1

    def is_last_day_of_month(dt):
        return dt.day == calendar.monthrange(dt.year, dt.month)[1]

    def is_first_day_of_week(dt):
        return dt.weekday() == 0  # Monday

    def is_last_day_of_week(dt):
        return dt.weekday() == 6  # Sunday

    # pylint: disable=too-many-nested-blocks
    while current_timestamp <= end_timestamp:
        timestamp_range.append(current_timestamp.strftime("%Y-%m-%d %H:%M:%S"))

        if unit in ["month", "months"]:
            if is_first_day_of_month(current_timestamp):
                current_timestamp = add_months(current_timestamp.replace(day=1), amount)
            elif is_last_day_of_month(current_timestamp):
                next_month = add_months(current_timestamp.replace(day=1), amount)
                current_timestamp = next_month.replace(day=calendar.monthrange(next_month.year, next_month.month)[1])
            else:
                raise ValueError("For monthly granularity, start_timestamp must be the first or last day of the month.")
        elif unit in ["week", "weeks"]:
            if is_first_day_of_week(current_timestamp):
                current_timestamp += timedelta(days=amount * 7)  # Move to the next specified number of weeks
            elif is_last_day_of_week(current_timestamp):
                current_timestamp += timedelta(days=amount * 7)  # Move to the next specified number of weeks
            else:
                raise ValueError("For weekly granularity, start_timestamp must be the first or last day of the week.")
        else:
            current_timestamp += timedelta(**{interval_mapping[unit]: amount})

    return timestamp_range
