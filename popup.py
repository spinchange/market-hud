import tkinter as tk
from tkinter import font as tkfont


class Popup:
    BG = "#111111"
    FG_LABEL = "#888888"
    FG_UP = "#00cc66"
    FG_DOWN = "#ff4444"
    FG_FLAT = "#cccccc"
    FG_CLOSED = "#555555"
    FG_FOOTER = "#333333"

    def __init__(self, root: tk.Tk, data_provider):
        self.root = root
        self.dp = data_provider
        self._win: tk.Toplevel | None = None
        self._visible = False

    def toggle(self):
        if self._visible:
            self.hide()
        else:
            self.show()

    def show(self):
        if self._visible:
            self._rebuild()
            return
        self._build()
        self._visible = True

    def hide(self):
        if self._win:
            self._win.destroy()
            self._win = None
        self._visible = False

    def refresh(self):
        if self._visible:
            self._rebuild()

    def _rebuild(self):
        self.hide()
        self._build()
        self._visible = True

    def _build(self):
        items = self.dp.get_items()

        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.attributes("-alpha", 0.95)
        win.configure(bg=self.BG)

        fn_label = tkfont.Font(family="Segoe UI", size=10)
        fn_price = tkfont.Font(family="Courier New", size=11, weight="bold")
        fn_pct = tkfont.Font(family="Courier New", size=10)
        fn_footer = tkfont.Font(family="Segoe UI", size=8)

        outer = tk.Frame(win, bg=self.BG, padx=18, pady=12)
        outer.pack()

        if not items:
            tk.Label(outer, text="Loading...", bg=self.BG, fg=self.FG_LABEL,
                     font=fn_label).pack()
        else:
            for item in items:
                color = self._color(item)
                row = tk.Frame(outer, bg=self.BG)
                row.pack(fill="x", pady=3)

                closed_dot = "  ·" if not item["live"] else ""
                sign = "+" if item["pct"] >= 0 else ""

                name_lbl = tk.Label(row, text=item["name"] + closed_dot,
                                    bg=self.BG, fg=self.FG_LABEL,
                                    font=fn_label, width=16, anchor="w")
                name_lbl.pack(side="left")

                price_lbl = tk.Label(row, text=self._fmt(item["price"]),
                                     bg=self.BG, fg=color,
                                     font=fn_price, width=12, anchor="e")
                price_lbl.pack(side="left")

                pct_lbl = tk.Label(row, text=f"  {sign}{item['pct']:.2f}%",
                                   bg=self.BG, fg=color,
                                   font=fn_pct, width=9, anchor="e")
                pct_lbl.pack(side="left")

        tk.Label(outer, text="click to close  ·  right-click tray for menu",
                 bg=self.BG, fg=self.FG_FOOTER, font=fn_footer).pack(pady=(10, 0))

        # Size and position: bottom-right above taskbar
        win.update_idletasks()
        w = win.winfo_reqwidth()
        h = win.winfo_reqheight()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        win.geometry(f"+{sw - w - 12}+{sh - h - 52}")

        # Click anywhere on popup (including child widgets) closes it
        self._bind_close(win)
        self._win = win

    def _bind_close(self, widget):
        widget.bind("<Button-1>", lambda e: self.hide())
        for child in widget.winfo_children():
            self._bind_close(child)

    def _fmt(self, price: float) -> str:
        if price >= 10_000:
            return f"{price:>10,.0f}"
        elif price >= 1_000:
            return f"{price:>10,.2f}"
        elif price >= 10:
            return f"{price:>10.2f}"
        else:
            return f"{price:>10.4f}"

    def _color(self, item: dict) -> str:
        if not item["live"]:
            return self.FG_CLOSED
        if item["pct"] > 0:
            return self.FG_UP
        if item["pct"] < 0:
            return self.FG_DOWN
        return self.FG_FLAT
