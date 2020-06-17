from itertools import product

from shark.base import (
    Cell,
    get_surrounding_cells,
    get_cells_in_block,
    get_resolution,
    Direction,
    Compass_eight,
    Compass_four,
    Timer,
)


def get_unit_cell():
    return Cell(1, 1)


def test_cell_size():
    cell = get_unit_cell()
    assert len(cell) == 2


def test_cell_iter():
    cell = get_unit_cell()
    for i in cell:
        assert i == 1


def test_cell_get():
    cell = get_unit_cell()
    assert cell.x == 1
    assert cell.y == 1


def test_cell_equals_tuple():
    cell = get_unit_cell()
    assert cell == (1, 1)


def test_cells_in_block():
    x_min = 0
    x_max = 2
    y_min = 0
    y_max = 2
    cells = get_cells_in_block(x_min, x_max, y_min, y_max)
    assert len(cells) == x_max * y_max


def test_get_surrounding_cells_free_zone():
    cell = get_unit_cell()
    block_of_cells = get_surrounding_cells(cell)
    assert len(block_of_cells) == 9


def test_get_surrounding_cells_corner():
    cell = get_unit_cell()
    map_shape = (2, 2)
    block_of_cells = get_surrounding_cells(cell, bounds=map_shape)
    assert len(block_of_cells) == 4


def test_no_overlap_res():
    dim = 5
    object_size = 32
    ans = dim * object_size
    assert (ans, ans) == get_resolution((dim, dim), object_size=object_size, overlap=0)


def test_overlap_res():
    dim = 2
    object_size = 32
    overlap = 0.125
    ans = int(object_size * (dim - ((dim - 1) * 2 * overlap)))
    assert (ans, ans) == get_resolution(
        (dim, dim), object_size=object_size, overlap=overlap
    )


def get_eight_displacements():
    ds = set((x, y) for x, y in product(range(-1, 2), range(-1, 2)))
    ds.remove((0, 0))
    return ds


def test_compass_eight_keys():
    keys = set(Compass_eight.keys())
    ds = get_eight_displacements()
    assert keys == ds


def test_compass_four_keys():
    keys = set(Compass_four.keys())
    ds = get_eight_displacements()
    assert keys == ds


def test_compass_eight():
    for d in Direction:
        assert d in Compass_eight.values()


def test_timer():
    interval = 0.5
    dt = 0.11
    timer = Timer(interval)
    total = 0
    n_iter = 100000
    for i in range(n_iter):
        total += int(timer(dt))
    assert int((dt * n_iter) / interval) == total
