from pathlib import Path
import time
from collections import defaultdict

from shark.objects import Hero, Goal, GameObject, MoveableObject
from shark.level import LevelLoader, Level
from shark.server import Server
from shark.base import Cell, get_cells_from_shape, get_cells_in_block


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


def test_loader_loads_specs():
    cwd = Path.cwd()
    loader = LevelLoader(cwd)
    assert len(loader) > 0


def get_level():
    cwd = Path.cwd()
    loader = LevelLoader(cwd)
    level = loader[0]
    return level


def test_loader_builds_level():
    level = get_level()
    assert isinstance(level, Level)


def test_level_has_hero():
    level = get_level()
    assert isinstance(level.hero, Hero)


def test_level_has_goal():
    level = get_level()
    assert isinstance(level.goal, Goal)


def get_server():
    cwd = Path.cwd()
    server = Server(cwd)
    return server


def test_server():
    server = get_server()
    server.start_level()
    print(server)
    c = Cell(3, 3)
    server.add_event(c)
    print(server.user_events)
    for i in range(40):
        time.sleep(0.01)
        server.update()
        print(server)


def test_server_level_start_time():
    server = get_server()
    t = time.time()
    time.sleep(0.01)
    server.start_level()
    assert server.current_time > t


def test_server_level_start_character():
    server = get_server()
    server.start_level()
    assert isinstance(server.selected_character, Hero)


def get_mover():
    return MoveableObject(x=0, y=0)


def test_movement_index():
    mover = get_mover()
    pos = (-0.4, 0.0, 1.0, 5.4)
    ans = (-1, 0, 1, 1)
    for pos, ans in zip(pos, ans):
        assert mover.convert_to_index(pos) == ans


def test_movement_goals():
    mover = get_mover()
    mover.move_to(Cell(2, 3))
    t = defaultdict(GameObject)
    o = defaultdict(GameObject)
    mover.choose_next_cell(t, o)
    assert mover.next_cell == (1, 1)


test_cell_size()
test_cell_iter()
test_cell_get()
test_cells_in_block()
test_get_cells_from_big_shape()
test_get_cells_from_small_shape()
test_movement_index()
test_movement_goals()
test_loader_loads_specs()
test_loader_builds_level()
test_level_has_hero()
test_level_has_goal()
test_server_level_start_character()
test_server_level_start_time()
test_server()
