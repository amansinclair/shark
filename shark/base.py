from itertools import product
from collections import namedtuple
from enum import Enum

Cell = namedtuple("Cell", "x, y")


def get_surrounding_cells(cell, shape=(1, 1), bounds=(20, 20), thickness=1):
    cell_x, cell_y = cell
    bound_x, bound_y = bounds
    x_min = max(0, cell_x - thickness)
    x_max = min(cell_x + shape[1] + thickness, bound_x)
    y_min = max(0, cell_y - thickness)
    y_max = min(cell_y + shape[1] + thickness, bound_y)
    return get_cells_in_block(x_min, x_max, y_min, y_max)


def get_cells_in_block(x_min, x_max, y_min, y_max):
    return set(Cell(x, y) for x, y in product(range(x_min, x_max), range(y_min, y_max)))


def get_resolution(map_shape, object_size=32, overlap=0.125):
    offset = int(2 * overlap * object_size)
    cell_size = object_size - offset
    return tuple((dim * cell_size) + offset for dim in map_shape)


def convert_to_ones(num):
    sign = -1 if num < 0 else 1
    value = 1 if num != 0 else 0
    return sign * value


"""
displacement_preferences = {
    (1, 0): [(1, 0), (0, 1), (0, -1), (-1, 0)],
    (1, -1): [(1, 0), (0, -1), (-1, 0), (0, -1)],
    (0, -1): [(0, -1), (1, 0), (-1, 0), (0, 1)],
    (-1, -1): [(-1, 0), (0, -1), (1, 0), (0, 1)],
    (-1, 0): [(-1, 0), (0, 1), (0, -1), (1, 0)],
    (-1, 1): [(-1, 0), (0, 1), (1, 0), (0, -1)],
    (0, 1): [(0, 1), (1, 0), (-1, 0), (0, -1)],
    (1, 1): [(1, 0), (0, 1), (-1, 0), (0, -1)],
}
"""
displacement_preferences = {
    (1, 0): [(1, 0), (1, 1), (1, -1)],
    (1, -1): [(1, -1), (1, 0), (0, -1)],
    (0, -1): [(0, -1), (1, -1), (-1, -1)],
    (-1, -1): [(-1, -1), (0, -1), (-1, 0)],
    (-1, 0): [(-1, 0), (-1, -1), (-1, 1)],
    (-1, 1): [(-1, 1), (-1, 0), (0, 1)],
    (0, 1): [(0, 1), (-1, 1), (1, 1)],
    (1, 1): [(1, 1), (0, 1), (1, 0)],
}


class Direction(Enum):
    north = 0
    south = 1
    east = 2
    west = 3
    northeast = 4
    southeast = 5
    northwest = 6
    southwest = 7


class Action(Enum):
    stand = 0
    tread_water = 1
    walk = 2
    swim = 3
    attack = 4
    attacked = 5
    die = 6


Compass_four = {
    (0, 1): Direction.north,
    (0, -1): Direction.south,
    (1, 0): Direction.east,
    (1, 1): Direction.east,
    (1, -1): Direction.east,
    (-1, 0): Direction.west,
    (-1, 1): Direction.west,
    (-1, -1): Direction.west,
}

Compass_diag = {
    (1, 1): Direction.northeast,
    (1, -1): Direction.southeast,
    (-1, 1): Direction.northwest,
    (-1, -1): Direction.southwest,
}

Compass_eight = {**Compass_four, **Compass_diag}


class Timer:
    def __init__(self, interval):
        self.interval = interval
        self.next_interval = self.interval
        self.total = 0

    def __call__(self, dt):
        self.total = round(self.total + dt, ndigits=5)
        if self.total >= self.next_interval:
            self.next_interval += self.interval
            return True
        return False
