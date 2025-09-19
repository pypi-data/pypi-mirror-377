from datetime import timedelta


def format_duration(value: timedelta) -> str:
    """Format a timedelta to a duration string as HH:MM:SS or MM:SS."""
    if not value:
        return "--:--"
    result = []
    seconds = value.total_seconds()
    if seconds >= 3600:
        hours, seconds = divmod(seconds, 3600)
        result.append(f"{hours:02n}")
    minutes, seconds = divmod(seconds, 60)
    result.append(f"{minutes:02n}")
    result.append(f"{seconds:02n}")
    return ":".join(result)
