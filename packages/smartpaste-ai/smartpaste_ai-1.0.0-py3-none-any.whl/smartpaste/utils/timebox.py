"""
Time and date utilities for SmartPaste.

This module provides utilities for time management, date formatting,
and file organization based on timestamps.
"""

from datetime import datetime, timezone
from typing import Optional


class TimeboxUtils:
    """Utility class for time and date operations."""
    
    DEFAULT_DATE_FORMAT = "%Y-%m-%d"
    DEFAULT_TIME_FORMAT = "%H:%M:%S"
    DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"
    
    @staticmethod
    def get_current_timestamp() -> str:
        """Get current timestamp in ISO format.
        
        Returns:
            Current timestamp as ISO formatted string
        """
        return datetime.now().isoformat()
    
    @staticmethod
    def get_current_utc_timestamp() -> str:
        """Get current UTC timestamp in ISO format.
        
        Returns:
            Current UTC timestamp as ISO formatted string
        """
        return datetime.now(timezone.utc).isoformat()
    
    @staticmethod
    def get_date_string(
        date: Optional[datetime] = None, 
        format_string: str = DEFAULT_DATE_FORMAT
    ) -> str:
        """Get date as formatted string.
        
        Args:
            date: Date to format (defaults to current date)
            format_string: Format string for date
            
        Returns:
            Formatted date string
        """
        if date is None:
            date = datetime.now()
        return date.strftime(format_string)
    
    @staticmethod
    def get_time_string(
        time: Optional[datetime] = None,
        format_string: str = DEFAULT_TIME_FORMAT
    ) -> str:
        """Get time as formatted string.
        
        Args:
            time: Time to format (defaults to current time)
            format_string: Format string for time
            
        Returns:
            Formatted time string
        """
        if time is None:
            time = datetime.now()
        return time.strftime(format_string)
    
    @staticmethod
    def get_datetime_string(
        dt: Optional[datetime] = None,
        format_string: str = DEFAULT_DATETIME_FORMAT
    ) -> str:
        """Get datetime as formatted string.
        
        Args:
            dt: Datetime to format (defaults to current datetime)
            format_string: Format string for datetime
            
        Returns:
            Formatted datetime string
        """
        if dt is None:
            dt = datetime.now()
        return dt.strftime(format_string)
    
    @staticmethod
    def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp string to datetime object.
        
        Args:
            timestamp_str: Timestamp string to parse
            
        Returns:
            Parsed datetime object or None if parsing fails
        """
        # Try different timestamp formats
        formats = [
            "%Y-%m-%dT%H:%M:%S.%f",  # ISO with microseconds
            "%Y-%m-%dT%H:%M:%S",     # ISO without microseconds
            "%Y-%m-%d %H:%M:%S.%f",  # Standard with microseconds
            "%Y-%m-%d %H:%M:%S",     # Standard without microseconds
            "%Y-%m-%d",              # Date only
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def get_file_timestamp() -> str:
        """Get timestamp suitable for filenames (no special characters).
        
        Returns:
            Filename-safe timestamp string
        """
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    @staticmethod
    def get_week_start_date(date: Optional[datetime] = None) -> datetime:
        """Get the start of the week (Monday) for a given date.
        
        Args:
            date: Date to get week start for (defaults to current date)
            
        Returns:
            Start of week datetime
        """
        if date is None:
            date = datetime.now()
        
        days_since_monday = date.weekday()
        week_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = week_start.replace(day=date.day - days_since_monday)
        
        return week_start
    
    @staticmethod
    def get_month_start_date(date: Optional[datetime] = None) -> datetime:
        """Get the start of the month for a given date.
        
        Args:
            date: Date to get month start for (defaults to current date)
            
        Returns:
            Start of month datetime
        """
        if date is None:
            date = datetime.now()
        
        return date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to human-readable string.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f}h"
        else:
            days = seconds / 86400
            return f"{days:.1f}d"
    
    @staticmethod
    def get_relative_time_description(dt: datetime) -> str:
        """Get relative time description (e.g., '2 hours ago').
        
        Args:
            dt: Datetime to describe
            
        Returns:
            Relative time description
        """
        now = datetime.now()
        if dt.tzinfo and not now.tzinfo:
            now = now.replace(tzinfo=timezone.utc)
        elif not dt.tzinfo and now.tzinfo:
            dt = dt.replace(tzinfo=timezone.utc)
        
        diff = now - dt
        total_seconds = diff.total_seconds()
        
        if total_seconds < 60:
            return "just now"
        elif total_seconds < 3600:
            minutes = int(total_seconds / 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif total_seconds < 86400:
            hours = int(total_seconds / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif total_seconds < 604800:  # 7 days
            days = int(total_seconds / 86400)
            return f"{days} day{'s' if days > 1 else ''} ago"
        elif total_seconds < 2592000:  # 30 days
            weeks = int(total_seconds / 604800)
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        elif total_seconds < 31536000:  # 365 days
            months = int(total_seconds / 2592000)
            return f"{months} month{'s' if months > 1 else ''} ago"
        else:
            years = int(total_seconds / 31536000)
            return f"{years} year{'s' if years > 1 else ''} ago"
    
    @staticmethod
    def is_business_hours(
        dt: Optional[datetime] = None,
        start_hour: int = 9,
        end_hour: int = 17,
        weekdays_only: bool = True
    ) -> bool:
        """Check if datetime falls within business hours.
        
        Args:
            dt: Datetime to check (defaults to current time)
            start_hour: Business day start hour (24-hour format)
            end_hour: Business day end hour (24-hour format)
            weekdays_only: If True, only Monday-Friday are business days
            
        Returns:
            True if within business hours
        """
        if dt is None:
            dt = datetime.now()
        
        # Check weekday if required
        if weekdays_only and dt.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Check hour
        return start_hour <= dt.hour < end_hour