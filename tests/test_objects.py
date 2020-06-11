from shark.objects import GameObject, MoveableObject
from shark.base import Direction, Action, Cell


def test_object_default_action():
    obj = GameObject()
    assert obj.action in Action


def test_object_default_direction():
    obj = GameObject()
    assert obj.direction in Direction


def test_object_cell():
    obj = GameObject()
    assert isinstance(obj.cell, Cell)


def test_object_contains():
    obj = GameObject(x=0, y=0, cells=((0, 0), (1, 1)))
    assert (1, 1) in obj


def test_object_without_cells_contains():
    obj = GameObject()
    assert (0, 0) in obj and (1, 1) not in obj


def test_moveableobject_default_action():
    obj = MoveableObject()
    assert obj.action in Action


def test_moveableobject_default_direction():
    obj = MoveableObject()
    assert obj.direction in Direction


def test_moveableobject_is_initially_dirty():
    obj = MoveableObject()
    assert obj.dirty == True
