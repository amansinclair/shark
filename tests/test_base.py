from shark.base import Cell, get_cells_from_shape, get_cells_in_block, get_resolution


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


def test_cells_in_block():
    x_min = 0
    x_max = 2
    y_min = 0
    y_max = 2
    cells = get_cells_in_block(x_min, x_max, y_min, y_max)
    assert len(cells) == x_max * y_max


def test_get_cells_from_big_shape():
    cell = get_unit_cell()
    shape = (100, 100)
    block_of_cells = get_cells_from_shape(cell, shape)
    assert len(block_of_cells) == 9


def test_get_cells_from_small_shape():
    cell = get_unit_cell()
    shape = (2, 2)
    block_of_cells = get_cells_from_shape(cell, shape)
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
