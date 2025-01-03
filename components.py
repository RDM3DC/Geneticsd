# components.py
import tkinter as tk
from tkinter import ttk
from constants import BACKGROUND_COLOR

class ScrollableFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        canvas = tk.Canvas(self, bg=BACKGROUND_COLOR)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
