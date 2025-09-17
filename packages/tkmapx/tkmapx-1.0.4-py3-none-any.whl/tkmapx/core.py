"""
Core logic for TKMap.
"""

from typing import Dict, Tuple, List
from .display import MapDisplay


class MapCore:
    """
    Core class to create and visualize maps.
    """

    def __init__(self):
        self.locations: Dict[str, Tuple[int, int]] = {}
        self.paths: List[Tuple[str, str]] = []

    def add_location(self, x: int, y: int, name: str) -> None:
        """
        Add a named location to the map.
        """
        if not isinstance(x, int) or not isinstance(y, int):
            raise TypeError("Coordinates must be integers.")
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        if name in self.locations:
            raise ValueError(f"Location '{name}' already exists.")

        self.locations[name] = (x, y)

    def draw_path(self, from_name: str, to_name: str) -> None:
        """
        Draw a path between two existing locations.
        """
        if from_name not in self.locations:
            raise ValueError(f"Location '{from_name}' not found.")
        if to_name not in self.locations:
            raise ValueError(f"Location '{to_name}' not found.")

        self.paths.append((from_name, to_name))

    def show(self, title: str = "TKMap Viewer", width: int = 800, height: int = 600) -> None:
        """
        Display the map in a Tkinter window.
        """
        display = MapDisplay(self.locations, self.paths, title, width, height)
        display.render()