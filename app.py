import queue
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
POLL_MS = 100  # how often the main thread checks for tray commands


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

    # pystray callbacks run on its own thread and tkinter is not thread-safe,
    # so callbacks only enqueue commands; poll() runs them on the main thread.
    commands: queue.Queue[str] = queue.Queue()

    def on_click(icon, item=None):
        commands.put("toggle")

    def on_refresh(icon, item):
        provider.force_refresh()  # open popup updates when the fetch lands

    def on_quit(icon, item):
        icon.stop()
        commands.put("quit")

    def poll():
        while True:
            try:
                cmd = commands.get_nowait()
            except queue.Empty:
                break
            if cmd == "toggle":
                popup.toggle()
            elif cmd == "quit":
                root.quit()
                return
        popup.refresh_if_stale()
        root.after(POLL_MS, poll)

    root.after(POLL_MS, poll)

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
