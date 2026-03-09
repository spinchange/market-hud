from datetime import datetime, time
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
_OPEN = time(9, 30)
_CLOSE = time(16, 0)


def is_equity_open() -> bool:
    now = datetime.now(ET)
    if now.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    return _OPEN <= now.time() < _CLOSE


def is_live(asset_type: str) -> bool:
    """Crypto and futures are treated as always live."""
    if asset_type in ("crypto", "futures"):
        return True
    return is_equity_open()
