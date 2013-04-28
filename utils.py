import datetime

def format_timestamp(obj):
    if isinstance(obj, datetime.timedelta):
        now = datetime.datetime.utcnow()
        obj = now - obj
    return obj.strftime("%Y%m%d %H%M%S")
