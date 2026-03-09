# Market HUD

A lightweight Python system tray app that shows live market prices on demand. Click the tray icon to toggle the popup; click anywhere on it to dismiss.

![Market HUD screenshot](screenshot.png)

## Features

- Live prices for S&P 500, Nasdaq, Dow Jones, Russell 2000, Gold, Oil (WTI), and Bitcoin
- Green/red coloring for up/down; dimmed with `·` when market is closed (shows last close vs prior close)
- U.S. equity hours aware — crypto and futures treated as always live
- Refreshes every 30 seconds; cached on failure so the popup always shows something
- Click tray icon to show/hide · right-click for Refresh and Quit

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Use `pythonw app.py` to run without a terminal window.

## Adding symbols

Edit `symbols.csv`. Columns: `symbol,name,asset_type` where `asset_type` is `equity`, `futures`, or `crypto`.

```csv
symbol,name,asset_type
^GSPC,S&P 500,equity
GC=F,Gold,futures
BTC-USD,Bitcoin,crypto
```

## Requirements

- Python 3.9+
- yfinance, pystray, Pillow, tzdata
