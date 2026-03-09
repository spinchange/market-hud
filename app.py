import threading
import tkinter as tk
from pathlib import Path

import pystray
from PIL import Image, ImageDraw

from data_provider import DataProvider
from popup import Popup

BASE = Path(__file__).parent
SYMBOLS_CSV = BASE / "symbols.csv"
REFRESH_INTERVAL = 30  # seconds


def _make_icon() -> Image.Image:
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Simple green bar chart
    bars = [
        (6,  42, 18, 58),
        (22, 26, 34, 58),
        (38, 34, 50, 58),
        (54, 14, 60, 58),  # rightmost bar, tallest
    ]
    for bar in bars:
        d.rectangle(bar, fill=(0, 204, 102, 255))
    return img


def main():
    root = tk.Tk()
    root.withdraw()

    provider = DataProvider(SYMBOLS_CSV, interval=REFRESH_INTERVAL)
    provider.start()

    popup = Popup(root, provider)

    def on_click(icon, item=None):
        root.after(0, popup.toggle)

    def on_refresh(icon, item):
        provider.force_refresh()
        root.after(600, popup.refresh)

    def on_quit(icon, item):
        icon.stop()
        root.after(0, root.quit)

    menu = pystray.Menu(
        pystray.MenuItem("Show / Hide", on_click, default=True),
        pystray.MenuItem("Refresh", on_refresh),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", on_quit),
    )

    icon = pystray.Icon("market_hud", _make_icon(), "Market HUD", menu=menu)

    # pystray runs in background; tkinter owns the main thread
    threading.Thread(target=icon.run, daemon=True).start()

    root.mainloop()
    provider.stop()


if __name__ == "__main__":
    main()
