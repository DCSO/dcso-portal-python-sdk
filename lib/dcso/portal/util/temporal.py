# Copyright (c) 2020, 2021, DCSO GmbH

from datetime import datetime, timedelta, timezone


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

        dot_index = s.find('.')
        tz_index = s.find('+')
        if dot_index > 0 and tz_index > dot_index + 7:
            # we make sure that the fraction has 6 digits
            # allowing microseconds, but not nanoseconds
            fraction = s[dot_index + 1:tz_index]
            s = s.replace('.' + fraction, '.' + str(round(int(fraction) / 1000)))

        try:
            return datetime.fromisoformat(s)
        except AttributeError:
            # for Python 3.6
            return fromisoformat(s)
    except (ValueError, TypeError):
        raise ValueError


def fromisoformat(date_string: str) -> datetime:
    """Construct a datetime from the output of datetime.isoformat().

    Back-ported and inspired from Python 3.7, including helper functions.

    https://github.com/python/cpython/blob/3.7/Lib/datetime.py
    """
    if not isinstance(date_string, str):
        raise TypeError('fromisoformat: argument must be str')

    # Split this at the separator
    dstr = date_string[0:10]
    tstr = date_string[11:]

    try:
        date_components = _parse_isoformat_date(dstr)
    except ValueError:
        raise ValueError(f'Invalid isoformat string: {date_string!r}')

    if tstr:
        try:
            time_components = _parse_isoformat_time(tstr)
        except ValueError:
            raise ValueError(f'Invalid isoformat string: {date_string!r}')
    else:
        time_components = [0, 0, 0, 0, None]

    return datetime(*(date_components + time_components))


# Helpers for parsing the result of isoformat()
def _parse_isoformat_date(dtstr):
    # It is assumed that this function will only be called with a
    # string of length exactly 10, and (though this is not used) ASCII-only
    year = int(dtstr[0:4])
    if dtstr[4] != '-':
        raise ValueError('Invalid date separator: %s' % dtstr[4])

    month = int(dtstr[5:7])

    if dtstr[7] != '-':
        raise ValueError('Invalid date separator')

    day = int(dtstr[8:10])

    return [year, month, day]


def _parse_isoformat_time(tstr):
    # Format supported is HH[:MM[:SS[.fff[fff]]]][+HH:MM[:SS[.ffffff]]]
    len_str = len(tstr)
    if len_str < 2:
        raise ValueError('Isoformat time too short')

    # This is equivalent to re.search('[+-]', tstr), but faster
    tz_pos = (tstr.find('-') + 1 or tstr.find('+') + 1)
    timestr = tstr[:tz_pos - 1] if tz_pos > 0 else tstr

    time_comps = _parse_hh_mm_ss_ff(timestr)

    tzi = None
    if tz_pos > 0:
        tzstr = tstr[tz_pos:]

        # Valid time zone strings are:
        # HH:MM               len: 5
        # HH:MM:SS            len: 8
        # HH:MM:SS.ffffff     len: 15

        if len(tzstr) not in (5, 8, 15):
            raise ValueError('Malformed time zone string')

        tz_comps = _parse_hh_mm_ss_ff(tzstr)
        if all(x == 0 for x in tz_comps):
            tzi = timezone.utc
        else:
            tzsign = -1 if tstr[tz_pos - 1] == '-' else 1

            td = timedelta(hours=tz_comps[0], minutes=tz_comps[1],
                           seconds=tz_comps[2], microseconds=tz_comps[3])

            tzi = timezone(tzsign * td)

    time_comps.append(tzi)

    return time_comps


def _parse_hh_mm_ss_ff(tstr):
    # Parses things of the form HH[:MM[:SS[.fff[fff]]]]
    len_str = len(tstr)

    time_comps = [0, 0, 0, 0]
    pos = 0
    for comp in range(0, 3):
        if (len_str - pos) < 2:
            raise ValueError('Incomplete time component')

        time_comps[comp] = int(tstr[pos:pos + 2])

        pos += 2
        next_char = tstr[pos:pos + 1]

        if not next_char or comp >= 2:
            break

        if next_char != ':':
            raise ValueError('Invalid time separator: %c' % next_char)

        pos += 1

    if pos < len_str:
        if tstr[pos] != '.':
            raise ValueError('Invalid microsecond component')
        else:
            pos += 1

            len_remainder = len_str - pos
            if len_remainder not in (3, 6):
                raise ValueError('Invalid microsecond component')

            time_comps[3] = int(tstr[pos:])
            if len_remainder == 3:
                time_comps[3] *= 1000

    return time_comps
