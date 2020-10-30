# Copyright (c) 2020, DCSO GmbH

from datetime import datetime, timedelta, timezone
from typing import Optional


def utc_now() -> datetime:
    """Returns now as non-naive UTC `datetime.datetime` instance."""
    return datetime.utcnow().replace(tzinfo=timezone.utc)


def diff_utc_now(dt: datetime) -> timedelta:
    """Returns difference between now UTC and the given datetime `dt`.

    A positive time delta means dt comes after current UTC time stamp.
    If dt is naive, timezone is first set, assuming it to be UTC.
    """
    if not dt.timetz():
        dt.replace(tzinfo=timezone.utc)

    return dt - utc_now()


def decode_utc_iso8601(s: str) -> datetime:
    """Decodes a UTC ISO 8601 formatted timestamp and returns it as a
    non-naive `datetime.datetime` instance.

    Since the Python method datetime.fromisoformat does only support
    timezone designator offsets, we must translate zone designators.

    The 'Z' and ' UTC' (note space) zone designators are translated
    as '+00:00'.

    Any timestamp that does not contain a timezone designator, offset
    or name, or is not UTC, is considered invalid and ValueError is raised.

    Note that only microsecond precision is supported. For example,
    nanoseconds will be truncated and rounded till microseconds.
    """
    zero_hour = '+00:00'
    try:
        if not s[-6:] == zero_hour:
            if s[-1:] == 'Z':
                s = s.replace('Z', zero_hour)
            elif s[-4:] == ' UTC':
                s = s.replace(' UTC', zero_hour)
            elif s[-3:] == '+00':
                s = s.replace('+00', zero_hour)
            else:
                raise ValueError("timezone UTC not recognized")
        dot_index = s.index('.')
        tz_index = s.index('+')
        if dot_index > 0 and tz_index > dot_index + 7:
            # we make sure that the fraction has 6 digits
            # allowing microseconds, but not nanoseconds
            fraction = s[dot_index + 1:tz_index]
            s = s.replace('.' + fraction, '.' + str(round(int(fraction) / 1000)))
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        raise ValueError
