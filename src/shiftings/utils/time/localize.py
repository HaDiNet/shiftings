from datetime import datetime, timedelta

from django.utils.timesince import timeuntil


def localize_timedelta(delta: timedelta) -> str:
    now = datetime.now()
    return timeuntil(now + delta, now)
