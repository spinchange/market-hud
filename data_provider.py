import csv
import threading
import time as time_mod
from pathlib import Path

import yfinance as yf

from market_hours import is_live


class DataProvider:
    def __init__(self, csv_path: Path, interval: int = 30):
        self.csv_path = csv_path
        self.interval = interval
        self._symbols: list[dict] = []
        self._cache: dict[str, dict] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None
        self.load_symbols()

    def load_symbols(self):
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            self._symbols = list(csv.DictReader(f))

    def start(self):
        self._running = True
        self._fetch_all()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def force_refresh(self):
        threading.Thread(target=self._fetch_all, daemon=True).start()

    def get_items(self) -> list[dict]:
        with self._lock:
            items = [
                self._cache[s["symbol"]]
                for s in self._symbols
                if s["symbol"] in self._cache
            ]
            return sorted(items, key=lambda x: x["pct"], reverse=True)

    def _loop(self):
        while self._running:
            time_mod.sleep(self.interval)
            self._fetch_all()

    def _fetch_all(self):
        for sym in self._symbols:
            result = self._fetch_one(sym)
            if result is not None:
                with self._lock:
                    self._cache[sym["symbol"]] = result

    def _fetch_one(self, sym: dict) -> dict | None:
        symbol = sym["symbol"]
        asset_type = sym.get("asset_type", "equity")
        try:
            ticker = yf.Ticker(symbol)
            fi = ticker.fast_info
            price = fi.last_price
            prev_close = fi.previous_close

            if price is None:
                return None

            live = is_live(asset_type)

            if live:
                display = price
                change = price - (prev_close or price)
                pct = (change / prev_close * 100) if prev_close else 0.0
            else:
                # Market closed: show last close vs prior close
                hist = ticker.history(period="5d")
                if len(hist) >= 2:
                    display = float(hist["Close"].iloc[-1])
                    prior = float(hist["Close"].iloc[-2])
                    change = display - prior
                    pct = (change / prior * 100) if prior else 0.0
                else:
                    display = prev_close or price
                    change = 0.0
                    pct = 0.0

            return {
                "symbol": symbol,
                "name": sym["name"],
                "price": display,
                "change": change,
                "pct": pct,
                "live": live,
                "asset_type": asset_type,
            }
        except Exception:
            return None  # Keep previous cached value on failure
