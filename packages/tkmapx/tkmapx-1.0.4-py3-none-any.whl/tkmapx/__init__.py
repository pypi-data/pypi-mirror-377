from .core import MapCore
from functools import partial

_map = MapCore()

add_location = partial(_map.add_location)
draw_path = partial(_map.draw_path)
show = partial(_map.show)