import datetime

def format_timestamp(dt):
    """Given a UTC datetime object, format as 'yyyymmdd hhmmss'.

    If the supplied object is a timedelta, subtract it from the
    current UTC datetime.
    """
    if isinstance(dt, datetime.timedelta):
        now = datetime.datetime.utcnow()
        dt = now - dt
    return dt.strftime("%Y%m%d %H%M%S")

def split_timestamp(dt):
    """Return a (date, time) tuple of a formatted timestamp.
    """
    return tuple(format_timestamp(dt).split(" "))

