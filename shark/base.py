from itertools import product
from collections import namedtuple

Cell = namedtuple("Cell", "x, y")


def get_cells_from_shape(cell, shape):
    cell_x, cell_y = cell
    x_min = max(0, cell_x - 1)
    x_max = min(cell_x + 2, shape[1])
    y_min = max(0, cell_y - 1)
    y_max = min(cell_y + 2, shape[0])
    return get_cells_in_block(x_min, x_max, y_min, y_max)


def get_cells_in_block(x_min, x_max, y_min, y_max):
    return set(Cell(x, y) for x, y in product(range(x_min, x_max), range(y_min, y_max)))
