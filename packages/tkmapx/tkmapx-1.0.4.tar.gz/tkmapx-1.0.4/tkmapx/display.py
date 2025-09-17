"""
Tkinter-based rendering for TKMap.
"""

import tkinter as tk
from typing import Dict, Tuple, List


class MapDisplay:
    def __init__(self,
                 locations: Dict[str, Tuple[int, int]],
                 paths: List[Tuple[str, str]],
                 title: str,
                 width: int,
                 height: int):
        self.locations = locations
        self.paths = paths
        self.title = title
        self.width = width
        self.height = height

    def render(self) -> None:
        """
        Render the map in a Tkinter window.
        """
        root = tk.Tk()
        root.title(self.title)

        canvas = tk.Canvas(root, width=self.width, height=self.height, bg="white")
        canvas.pack(fill="both", expand=True)

        # Draw locations
        for name, (x, y) in self.locations.items():
            self._draw_node(canvas, x, y, name)

        # Draw paths
        for start, end in self.paths:
            self._draw_line(canvas, start, end)

        root.mainloop()

    def _draw_node(self, canvas: tk.Canvas, x: int, y: int, label: str) -> None:
        """
        Draw a single map node (location) with a label above it.
        """
        radius = 6
        cx, cy = x, y

        # Draw circle
        canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                           fill="blue", outline="black")

        # Draw label slightly above circle
        canvas.create_text(cx, cy - (radius + 10), text=label,
                           font=("Arial", 10, "bold"), anchor="s")

    def _draw_line(self, canvas: tk.Canvas, from_name: str, to_name: str) -> None:
        """
        Draw a line (path) between two locations.
        """
        x1, y1 = self.locations[from_name]
        x2, y2 = self.locations[to_name]
        canvas.create_line(x1, y1, x2, y2, fill="black")