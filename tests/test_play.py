from pathlib import Path
import time
from collections import defaultdict

from shark.objects import Hero, Goal, GameObject, MoveableObject
from shark.level import LevelLoader, Level
from shark.server import Server
from shark.base import Cell


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
        server.update(0.05)
        print(server)


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
