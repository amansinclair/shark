from pathlib import Path
import time
from collections import defaultdict

from shark.objects import Hero, Goal, GameObject, MoveableObject
from shark.level import LevelLoader, Level
from shark.base import Cell, get_cells_in_block


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


def test_level_is_filled():
    level = get_level()
    n_rows, n_cols = level.shape
    all_cells = get_cells_in_block(0, n_cols, 0, n_rows)
    terrain_cells = set(level.terrain_cells.keys())
    assert all_cells == terrain_cells
