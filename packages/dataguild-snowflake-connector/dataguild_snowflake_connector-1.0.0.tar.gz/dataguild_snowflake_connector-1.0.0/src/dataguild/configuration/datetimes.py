"""
DataGuild DateTime Configuration Parser

This module provides utilities for parsing and validating datetime strings
used in DataGuild configuration files and API endpoints.

Supports ISO 8601 datetime formats with optional timezone information.
"""

import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Optional, Union, List
from dateutil import parser as dateutil_parser
from dateutil.tz import tzutc, tzlocal, tzoffset

logger = logging.getLogger(__name__)


def parse_absolute_time(time_str: str) -> Optional[datetime]:
    """
    Parse an absolute datetime string into a datetime object.

    Supports various ISO 8601 formats with optional timezone information:
    - 2023-09-01T12:34:56
    - 2023-09-01 12:34:56
    - 2023-09-01T12:34:56Z
    - 2023-09-01T12:34:56+00:00
    - 2023-09-01T12:34:56.123456
    - 2023-09-01T12:34:56-05:00

    Args:
        time_str: Absolute datetime string to parse

    Returns:
        datetime object if parsing succeeds, None otherwise

    Examples:
        >>> parse_absolute_time('2023-09-01T12:34:56')
        datetime.datetime(2023, 9, 1, 12, 34, 56)

        >>> parse_absolute_time('2023-09-01T12:34:56Z')
        datetime.datetime(2023, 9, 1, 12, 34, 56, tzinfo=datetime.timezone.utc)

        >>> parse_absolute_time('invalid-datetime')
        None
    """
    if not time_str or not isinstance(time_str, str):
        return None

    time_str = time_str.strip()

    # Try Python's built-in fromisoformat first (fastest for standard ISO formats)
    try:
        # Normalize space separator to T for ISO format
        normalized_str = time_str.replace(' ', 'T', 1)  # Only replace first space
        return datetime.fromisoformat(normalized_str)
    except ValueError:
        pass

    # Try dateutil parser for more flexible parsing
    try:
        return dateutil_parser.parse(time_str)
    except (ValueError, TypeError):
        pass

    # Manual regex parsing as final fallback
    return _parse_datetime_regex(time_str)


def _parse_datetime_regex(time_str: str) -> Optional[datetime]:
    """
    Manual regex-based datetime parsing for edge cases.

    Args:
        time_str: Datetime string to parse

    Returns:
        datetime object if successful, None otherwise
    """
    # Comprehensive ISO 8601 regex pattern
    iso_pattern = re.compile(
        r'^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})'
        r'[T\s]'  # T or space separator
        r'(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})'
        r'(?:\.(?P<microsecond>\d{1,6}))?'  # Optional fractional seconds
        r'(?P<tzinfo>Z|[+-]\d{2}:?\d{2})?$'  # Optional timezone
    )

    match = iso_pattern.match(time_str)
    if not match:
        return None

    try:
        # Extract datetime components
        year = int(match.group('year'))
        month = int(match.group('month'))
        day = int(match.group('day'))
        hour = int(match.group('hour'))
        minute = int(match.group('minute'))
        second = int(match.group('second'))

        # Handle microseconds
        microsecond = 0
        if match.group('microsecond'):
            # Pad or truncate to 6 digits
            microsecond_str = match.group('microsecond').ljust(6, '0')[:6]
            microsecond = int(microsecond_str)

        # Create datetime object
        dt = datetime(year, month, day, hour, minute, second, microsecond)

        # Handle timezone
        tzinfo = match.group('tzinfo')
        if tzinfo:
            if tzinfo == 'Z':
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                # Parse timezone offset (+/-HH:MM or +/-HHMM)
                tz_offset = _parse_timezone_offset(tzinfo)
                if tz_offset is not None:
                    dt = dt.replace(tzinfo=tz_offset)

        return dt

    except (ValueError, OverflowError) as e:
        logger.debug(f"Failed to parse datetime components from '{time_str}': {e}")
        return None


def _parse_timezone_offset(tz_str: str) -> Optional[timezone]:
    """
    Parse timezone offset string into timezone object.

    Args:
        tz_str: Timezone string like '+05:00', '-0800', etc.

    Returns:
        timezone object if successful, None otherwise
    """
    try:
        # Remove colons and normalize
        tz_normalized = tz_str.replace(':', '')

        # Extract sign and offset
        sign = 1 if tz_str[0] == '+' else -1

        if len(tz_normalized) == 5:  # +HHMM format
            hours = int(tz_normalized[1:3])
            minutes = int(tz_normalized[3:5])
        elif len(tz_normalized) == 3:  # +HH format
            hours = int(tz_normalized[1:3])
            minutes = 0
        else:
            return None

        # Calculate total offset in minutes
        total_minutes = sign * (hours * 60 + minutes)

        # Create timezone object
        return timezone(timedelta(minutes=total_minutes))

    except (ValueError, IndexError):
        return None


def parse_relative_time(time_str: str, base_time: Optional[datetime] = None) -> Optional[datetime]:
    """
    Parse relative time expressions into absolute datetime.

    Supports expressions like:
    - "1 hour ago"
    - "2 days ago"
    - "30 minutes ago"
    - "1 week ago"

    Args:
        time_str: Relative time string
        base_time: Base time for relative calculation (default: now)

    Returns:
        datetime object if parsing succeeds, None otherwise
    """
    if not time_str or not isinstance(time_str, str):
        return None

    if base_time is None:
        base_time = datetime.now()

    time_str = time_str.strip().lower()

    # Regex pattern for relative time expressions
    relative_pattern = re.compile(
        r'^(\d+)\s+(second|minute|hour|day|week|month|year)s?\s+ago$'
    )

    match = relative_pattern.match(time_str)
    if not match:
        return None

    try:
        amount = int(match.group(1))
        unit = match.group(2)

        if unit == 'second':
            delta = timedelta(seconds=amount)
        elif unit == 'minute':
            delta = timedelta(minutes=amount)
        elif unit == 'hour':
            delta = timedelta(hours=amount)
        elif unit == 'day':
            delta = timedelta(days=amount)
        elif unit == 'week':
            delta = timedelta(weeks=amount)
        elif unit == 'month':
            # Approximate month as 30 days
            delta = timedelta(days=amount * 30)
        elif unit == 'year':
            # Approximate year as 365 days
            delta = timedelta(days=amount * 365)
        else:
            return None

        return base_time - delta

    except (ValueError, OverflowError):
        return None


def parse_time_range(range_str: str) -> Optional[tuple[datetime, datetime]]:
    """
    Parse time range string into start and end datetime objects.

    Supports formats like:
    - "2023-09-01T00:00:00 to 2023-09-02T00:00:00"
    - "2023-09-01 00:00:00 - 2023-09-02 00:00:00"

    Args:
        range_str: Time range string

    Returns:
        Tuple of (start_time, end_time) if successful, None otherwise
    """
    if not range_str or not isinstance(range_str, str):
        return None

    # Split on common separators
    separators = [' to ', ' - ', ' -- ', '..', ' until ']

    parts = None
    for sep in separators:
        if sep in range_str:
            parts = range_str.split(sep, 1)
            break

    if not parts or len(parts) != 2:
        return None

    start_str, end_str = [part.strip() for part in parts]

    start_time = parse_absolute_time(start_str)
    end_time = parse_absolute_time(end_str)

    if start_time and end_time:
        return start_time, end_time

    return None


def validate_datetime_format(time_str: str, required_timezone: bool = False) -> bool:
    """
    Validate if datetime string is in acceptable format.

    Args:
        time_str: Datetime string to validate
        required_timezone: Whether timezone information is required

    Returns:
        True if format is valid, False otherwise
    """
    parsed_dt = parse_absolute_time(time_str)

    if parsed_dt is None:
        return False

    if required_timezone and parsed_dt.tzinfo is None:
        return False

    return True


def normalize_datetime_string(time_str: str, target_format: str = "%Y-%m-%dT%H:%M:%S") -> Optional[str]:
    """
    Normalize datetime string to a standard format.

    Args:
        time_str: Input datetime string
        target_format: Target format string (default: ISO format)

    Returns:
        Normalized datetime string if successful, None otherwise
    """
    parsed_dt = parse_absolute_time(time_str)

    if parsed_dt is None:
        return None

    try:
        # Convert to naive datetime for formatting if needed
        if parsed_dt.tzinfo is not None and 'Z' not in target_format and '%z' not in target_format:
            # Convert to UTC and remove timezone for formatting
            parsed_dt = parsed_dt.astimezone(timezone.utc).replace(tzinfo=None)

        return parsed_dt.strftime(target_format)
    except (ValueError, AttributeError):
        return None


def get_current_time_string(include_timezone: bool = True, format_string: Optional[str] = None) -> str:
    """
    Get current time as formatted string.

    Args:
        include_timezone: Whether to include timezone information
        format_string: Custom format string (default: ISO format)

    Returns:
        Formatted current time string
    """
    now = datetime.now(timezone.utc) if include_timezone else datetime.now()

    if format_string:
        return now.strftime(format_string)

    if include_timezone:
        return now.isoformat()
    else:
        return now.strftime("%Y-%m-%dT%H:%M:%S")


def parse_duration(duration_str: str) -> Optional[timedelta]:
    """
    Parse duration string into timedelta object.

    Supports formats like:
    - "1h30m" (1 hour 30 minutes)
    - "2d" (2 days)
    - "45s" (45 seconds)
    - "1w" (1 week)

    Args:
        duration_str: Duration string to parse

    Returns:
        timedelta object if successful, None otherwise
    """
    if not duration_str or not isinstance(duration_str, str):
        return None

    duration_str = duration_str.strip().lower()

    # Pattern to match duration components
    duration_pattern = re.compile(r'(\d+)([smhdw])')
    matches = duration_pattern.findall(duration_str)

    if not matches:
        return None

    total_delta = timedelta()

    try:
        for amount_str, unit in matches:
            amount = int(amount_str)

            if unit == 's':
                total_delta += timedelta(seconds=amount)
            elif unit == 'm':
                total_delta += timedelta(minutes=amount)
            elif unit == 'h':
                total_delta += timedelta(hours=amount)
            elif unit == 'd':
                total_delta += timedelta(days=amount)
            elif unit == 'w':
                total_delta += timedelta(weeks=amount)

        return total_delta

    except (ValueError, OverflowError):
        return None


# Export all functions
__all__ = [
    'parse_absolute_time',
    'parse_relative_time',
    'parse_time_range',
    'parse_duration',
    'validate_datetime_format',
    'normalize_datetime_string',
    'get_current_time_string',
]
