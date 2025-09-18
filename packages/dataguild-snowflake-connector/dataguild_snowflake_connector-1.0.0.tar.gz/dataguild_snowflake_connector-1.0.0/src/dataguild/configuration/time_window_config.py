"""
Time window configuration for incremental data extraction.

This module provides configuration classes and utilities for managing
time-based filtering and incremental processing of data sources.
"""

import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import List, Optional, Tuple, Union
from pydantic import BaseModel, Field, validator, root_validator

from dataguild.configuration.common import ConfigModel

logger = logging.getLogger(__name__)


class TimeWindowType(str, Enum):
    """Enumeration of supported time window types."""
    FIXED = "fixed"  # Fixed start and end times
    SLIDING = "sliding"  # Sliding window based on current time
    INCREMENTAL = "incremental"  # Incremental processing from last checkpoint


class BucketDuration(str, Enum):
    """Enumeration of supported bucket durations for time-based aggregation."""
    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    QUARTER = "QUARTER"
    YEAR = "YEAR"


class BaseTimeWindowConfig(ConfigModel):
    """
    Base configuration for time window filtering and incremental processing.

    Provides comprehensive time-based filtering capabilities for data sources
    that support temporal filtering and incremental extraction.
    """

    start_time: Optional[datetime] = Field(
        default=None,
        description="Start time for the ingestion window (inclusive)"
    )

    end_time: Optional[datetime] = Field(
        default=None,
        description="End time for the ingestion window (exclusive)"
    )

    bucket_duration: Optional[BucketDuration] = Field(
        default=BucketDuration.DAY,
        description="Duration for time-based bucketing and aggregation"
    )

    window_type: TimeWindowType = Field(
        default=TimeWindowType.FIXED,
        description="Type of time window to use"
    )

    lookback_days: Optional[int] = Field(
        default=None,
        description="Number of days to look back from end_time if start_time not specified",
        ge=1,
        le=3650  # ~10 years max
    )

    timezone: str = Field(
        default="UTC",
        description="Timezone for time window calculations"
    )

    ignore_start_time_lineage: bool = Field(
        default=False,
        description="Whether to ignore start_time for lineage extraction"
    )

    @validator("start_time", "end_time")
    def validate_datetime_timezone(cls, v):
        """Ensure datetime objects have timezone information."""
        if v is not None and v.tzinfo is None:
            # Assume UTC if no timezone provided
            v = v.replace(tzinfo=timezone.utc)
            logger.warning("No timezone specified for datetime, assuming UTC")
        return v

    @root_validator
    def validate_time_window(cls, values):
        """Validate time window configuration consistency."""
        start_time = values.get("start_time")
        end_time = values.get("end_time")
        lookback_days = values.get("lookback_days")
        window_type = values.get("window_type")

        # For fixed windows, validate start/end time relationship
        if window_type == TimeWindowType.FIXED:
            if start_time and end_time:
                if start_time >= end_time:
                    raise ValueError("start_time must be before end_time")

            # If lookback_days is specified but no start_time, calculate start_time
            if lookback_days and end_time and not start_time:
                calculated_start = end_time - timedelta(days=lookback_days)
                values["start_time"] = calculated_start
                logger.info(f"Calculated start_time from lookback_days: {calculated_start}")

        return values

    def get_effective_time_window(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Get the effective time window based on configuration.

        Returns:
            Tuple of (start_time, end_time) with any necessary calculations applied
        """
        start_time = self.start_time
        end_time = self.end_time

        if self.window_type == TimeWindowType.SLIDING:
            # For sliding windows, calculate based on current time
            now = datetime.now(timezone.utc)
            if self.lookback_days:
                start_time = now - timedelta(days=self.lookback_days)
                end_time = now
            elif not end_time:
                end_time = now

        elif self.window_type == TimeWindowType.INCREMENTAL:
            # For incremental processing, end_time defaults to now if not specified
            if not end_time:
                end_time = datetime.now(timezone.utc)

        return start_time, end_time

    def get_time_buckets(self) -> List[Tuple[datetime, datetime]]:
        """
        Generate time buckets based on the configured bucket duration.

        Returns:
            List of (bucket_start, bucket_end) tuples
        """
        start_time, end_time = self.get_effective_time_window()

        if not start_time or not end_time:
            logger.warning("Cannot generate time buckets without both start and end times")
            return []

        buckets = []
        current_time = start_time

        while current_time < end_time:
            bucket_end = self._get_next_bucket_boundary(current_time)
            if bucket_end > end_time:
                bucket_end = end_time

            buckets.append((current_time, bucket_end))
            current_time = bucket_end

        return buckets

    def _get_next_bucket_boundary(self, current_time: datetime) -> datetime:
        """Calculate the next bucket boundary based on bucket_duration."""
        if self.bucket_duration == BucketDuration.MINUTE:
            # Round up to next minute
            return current_time.replace(second=0, microsecond=0) + timedelta(minutes=1)

        elif self.bucket_duration == BucketDuration.HOUR:
            # Round up to next hour
            return current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

        elif self.bucket_duration == BucketDuration.DAY:
            # Round up to next day
            return current_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

        elif self.bucket_duration == BucketDuration.WEEK:
            # Round up to next Monday
            days_until_monday = (7 - current_time.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7  # If it's already Monday, go to next Monday
            return current_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday)

        elif self.bucket_duration == BucketDuration.MONTH:
            # Round up to next month
            if current_time.month == 12:
                return current_time.replace(year=current_time.year + 1, month=1, day=1, hour=0, minute=0, second=0,
                                            microsecond=0)
            else:
                return current_time.replace(month=current_time.month + 1, day=1, hour=0, minute=0, second=0,
                                            microsecond=0)

        elif self.bucket_duration == BucketDuration.QUARTER:
            # Round up to next quarter
            quarter_start_months = [1, 4, 7, 10]
            current_quarter = (current_time.month - 1) // 3
            next_quarter_month = quarter_start_months[(current_quarter + 1) % 4]

            if next_quarter_month == 1:  # Next year
                return current_time.replace(year=current_time.year + 1, month=1, day=1, hour=0, minute=0, second=0,
                                            microsecond=0)
            else:
                return current_time.replace(month=next_quarter_month, day=1, hour=0, minute=0, second=0, microsecond=0)

        elif self.bucket_duration == BucketDuration.YEAR:
            # Round up to next year
            return current_time.replace(year=current_time.year + 1, month=1, day=1, hour=0, minute=0, second=0,
                                        microsecond=0)

        else:
            # Default to daily buckets
            return current_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

    def is_time_in_window(self, timestamp: datetime) -> bool:
        """
        Check if a timestamp falls within the configured time window.

        Args:
            timestamp: Timestamp to check

        Returns:
            True if timestamp is within the window, False otherwise
        """
        start_time, end_time = self.get_effective_time_window()

        if start_time and timestamp < start_time:
            return False

        if end_time and timestamp >= end_time:
            return False

        return True

    def get_window_duration(self) -> Optional[timedelta]:
        """
        Get the duration of the time window.

        Returns:
            Duration as timedelta if both start and end times are available, None otherwise
        """
        start_time, end_time = self.get_effective_time_window()

        if start_time and end_time:
            return end_time - start_time

        return None

    def format_time_window(self) -> str:
        """Get human-readable representation of the time window."""
        start_time, end_time = self.get_effective_time_window()

        start_str = start_time.isoformat() if start_time else "unbounded"
        end_str = end_time.isoformat() if end_time else "unbounded"

        return f"[{start_str} to {end_str})"


def validate_time_window(
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        allow_none: bool = True
) -> bool:
    """
    Validate time window parameters.

    Args:
        start_time: Start time to validate
        end_time: End time to validate
        allow_none: Whether None values are allowed

    Returns:
        True if time window is valid, False otherwise
    """
    if not allow_none and (start_time is None or end_time is None):
        return False

    if start_time and end_time and start_time >= end_time:
        return False

    return True


def get_time_buckets(
        start_time: datetime,
        end_time: datetime,
        bucket_duration: BucketDuration
) -> List[Tuple[datetime, datetime]]:
    """
    Generate time buckets for a given time range and bucket duration.

    Args:
        start_time: Start of time range
        end_time: End of time range
        bucket_duration: Duration for each bucket

    Returns:
        List of (bucket_start, bucket_end) tuples
    """
    config = BaseTimeWindowConfig(
        start_time=start_time,
        end_time=end_time,
        bucket_duration=bucket_duration
    )

    return config.get_time_buckets()


def create_sliding_window_config(
        lookback_days: int,
        bucket_duration: BucketDuration = BucketDuration.DAY
) -> BaseTimeWindowConfig:
    """
    Create a sliding time window configuration.

    Args:
        lookback_days: Number of days to look back from current time
        bucket_duration: Duration for time buckets

    Returns:
        Configured BaseTimeWindowConfig instance
    """
    return BaseTimeWindowConfig(
        window_type=TimeWindowType.SLIDING,
        lookback_days=lookback_days,
        bucket_duration=bucket_duration
    )


def create_fixed_window_config(
        start_time: datetime,
        end_time: datetime,
        bucket_duration: BucketDuration = BucketDuration.DAY
) -> BaseTimeWindowConfig:
    """
    Create a fixed time window configuration.

    Args:
        start_time: Fixed start time
        end_time: Fixed end time
        bucket_duration: Duration for time buckets

    Returns:
        Configured BaseTimeWindowConfig instance
    """
    return BaseTimeWindowConfig(
        window_type=TimeWindowType.FIXED,
        start_time=start_time,
        end_time=end_time,
        bucket_duration=bucket_duration
    )
