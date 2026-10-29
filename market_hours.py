from datetime import date, datetime, time, timedelta
from functools import lru_cache
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
_OPEN = time(9, 30)
_CLOSE = time(16, 0)


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """nth weekday (Monday=0) of a month; n=-1 for the last one."""
    if n > 0:
        d = date(year, month, 1)
        d += timedelta(days=(weekday - d.weekday()) % 7)
        return d + timedelta(weeks=n - 1)
    d = date(year, month + 1, 1) - timedelta(days=1)
    return d - timedelta(days=(d.weekday() - weekday) % 7)


def _easter(year: int) -> date:
    """Western Easter Sunday (anonymous Gregorian algorithm)."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(h + l - 7 * m + 114, 31)
    return date(year, month, day + 1)


def _observed(d: date) -> date:
    """Saturday holidays move to Friday, Sunday holidays to Monday."""
    if d.weekday() == 5:
        return d - timedelta(days=1)
    if d.weekday() == 6:
        return d + timedelta(days=1)
    return d


@lru_cache(maxsize=4)
def nyse_holidays(year: int) -> frozenset[date]:
    """Full-day NYSE closures. Ad hoc closures (e.g. national mourning)
    and 1 p.m. early closes are not included."""
    days = {
        _nth_weekday(year, 1, 0, 3),         # Martin Luther King Jr. Day
        _nth_weekday(year, 2, 0, 3),         # Washington's Birthday
        _easter(year) - timedelta(days=2),   # Good Friday
        _nth_weekday(year, 5, 0, -1),        # Memorial Day
        _observed(date(year, 7, 4)),         # Independence Day
        _nth_weekday(year, 9, 0, 1),         # Labor Day
        _nth_weekday(year, 11, 3, 4),        # Thanksgiving
        _observed(date(year, 12, 25)),       # Christmas
    }
    if year >= 2022:
        days.add(_observed(date(year, 6, 19)))  # Juneteenth
    # When Jan 1 is a Saturday the NYSE stays open on Friday Dec 31.
    new_year = date(year, 1, 1)
    if new_year.weekday() != 5:
        days.add(_observed(new_year))
    return frozenset(days)


def is_equity_open() -> bool:
    now = datetime.now(ET)
    if now.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    if now.date() in nyse_holidays(now.year):
        return False
    return _OPEN <= now.time() < _CLOSE


def is_live(asset_type: str) -> bool:
    """Crypto and futures are treated as always live."""
    if asset_type in ("crypto", "futures"):
        return True
    return is_equity_open()
