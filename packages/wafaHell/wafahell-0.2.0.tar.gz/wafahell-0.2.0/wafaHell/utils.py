from datetime import datetime, timedelta

def is_block_expired(blocked_time_str: str) -> bool:
    blocked_time = datetime.strptime(blocked_time_str, "%H:%M:%S")
    now = datetime.now()
    blocked_time = blocked_time.replace(year=now.year, month=now.month, day=now.day)

    diff = now - blocked_time
    return diff >= timedelta(minutes=1)

