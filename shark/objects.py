import math
import time
import inspect
import importlib
from collections import deque, namedtuple
from .base import Cell, get_cells_in_block, get_cells_from_shape, Action, Compass_four


class GameObject:
    """Base class for all game objects."""

    def __init__(self, x=0.0, y=0.0, shape=(1, 1), cells=None, is_alive=True):
        self.x = x
        self.y = y
        self.shape = shape
        self.is_alive = is_alive
        self._cells = cells
        self.action = Action.stand
        self.direction = Compass_four[(0, -1)]

    @property
    def cell(self):
        return Cell(round(self.x), round(self.y))

    @property
    def cells(self):
        if self._cells:
            return set([Cell(self.x + x, self.y + y) for x, y in self._cells])
        else:
            cell_x, cell_y = self.cell
            max_x = cell_x + self.shape[1]
            max_y = cell_y + self.shape[0]
            return get_cells_in_block(cell_x, max_x, cell_y, max_y)

    def __contains__(self, cell):
        return cell in self.cells

    def __repr__(self):
        cls = self.__class__.__name__
        return f"{cls}(x: {self.x:.1f}, y: {self.y:.1f}, is alive: {self.is_alive})"

    def step(self, dt, terrain, objects):
        pass


class Terrain(GameObject):
    """Base class for regions of a level."""

    pass


class Water(Terrain):
    """A water region passable to all."""


class Land(Terrain):
    """A land region passable only to Goodies."""

    pass


class UnPassableTerrain(Terrain):
    """A region unpassable to all Characters."""

    pass


class Goal(GameObject):
    """A point that defines where the Hero must go!."""

    pass


class MoveableObject(GameObject):
    """Class that supports movement."""

    water_speed = 10
    land_speed = 10
    angle = math.cos(math.pi / 4)
    best_directions = {
        (1, 0): [(1, 0), (1, 1), (1, -1)],
        (1, -1): [(1, -1), (1, 0), (0, -1)],
        (0, -1): [(0, -1), (1, -1), (-1, -1)],
        (-1, -1): [(-1, -1), (0, -1), (-1, 0)],
        (-1, 0): [(-1, 0), (-1, -1), (-1, 1)],
        (-1, 1): [(-1, 1), (-1, 0), (0, 1)],
        (0, 1): [(0, 1), (-1, 1), (1, 1)],
        (1, 1): [(1, 1), (0, 1), (1, 0)],
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dirty = True
        self.clear()

    def clear(self):
        self.goal_cell = None
        self.next_cell = None
        self.step_size = 0
        self.direction = Compass_four[(0, -1)]
        self.action = Action.stand

    def recenter(self):
        self.next_cell = self.cell
        self.goal_cell = self.cell

    def move_to(self, cell):
        self.goal_cell = cell
        self.next_cell = self.cell

    def step(self, dt, terrain, objects):
        self.dirty = False
        if self.goal_cell:
            self.dirty = True
            self.set_stepsize(dt, terrain)
            self.move(terrain, objects)

    def set_stepsize(self, dt, terrain):
        is_on_land = isinstance(terrain[self.cell], Land)
        self.action = Action.move if is_on_land else Action.swim
        current_speed = self.land_speed if is_on_land else self.water_speed
        self.step_size = current_speed * dt

    def move(self, terrain, objects):
        while self.step_size > 0:
            if (self.x, self.y) == self.next_cell:
                self.choose_next_cell(terrain, objects)
            if not self.next_cell:
                self.recenter()
            else:
                self.take_step()
            if (self.x, self.y) == self.goal_cell:
                self.clear()

    def convert_to_index(self, num):
        sign = -1 if num < 0 else 1
        value = 1 if num != 0 else 0
        return sign * value

    def choose_next_cell(self, terrain, objects):
        dx = self.goal_cell.x - self.cell.x
        dy = self.goal_cell.y - self.cell.y
        index = (self.convert_to_index(dx), self.convert_to_index(dy))
        best_directions = self.best_directions[index]
        self.set_next_cell(best_directions, terrain, objects)

    def set_next_cell(self, best_directions, terrain, objects):
        self.next_cell = None
        for dx, dy in best_directions:
            cell = Cell(self.cell.x + dx, self.cell.y + dy)
            if self.is_free_cell(terrain[cell]) and self.is_free_cell(objects[cell]):
                self.next_cell = cell
                self.direction = Compass_four[(dx, dy)]
                break

    def is_free_cell(self, game_object=None):
        """To be implemented by subclasses."""
        return True

    def take_step(self):
        sx, sy = self.direction
        step_size = self.step_size * self.angle if sx and sy else self.step_size
        self.update_position(sx * step_size, sy * step_size)

    def update_position(self, sx, sy):
        dx = self.next_cell.x - self.x
        dy = self.next_cell.y - self.y
        if abs(sx) < abs(dx):
            dx_actual = sx
            self.x += sx
        else:
            dx_actual = self.next_cell.x - self.x
            self.x = self.next_cell.x
        if abs(sy) < abs(dy):
            dy_actual = sy
            self.y += sy
        else:
            dy_actual = self.next_cell.y - self.y
            self.y = self.next_cell.y
        self.step_size -= dx_actual + dy_actual


class Character(MoveableObject):
    """Class that has health and supports movement."""

    max_health = 100

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_health = self.max_health

    def step(self, dt, terrain, objects):
        if self.current_health <= 0:
            self.is_alive == False
        else:
            super().step(dt, terrain, objects)

    def __lt__(self, character):
        if self.y == character.y:
            return self.x < character.x
        else:
            return self.y < character.y


class Goodie(Character):
    pass


class Hero(Goodie):
    pass


class Baddie(Character):
    """Character that can do damage to Goodies."""

    max_damage = 35


class Shark(Baddie):
    def __init__(self):
        self.previous_cells = deque(3)


all_classes = inspect.getmembers(importlib.import_module(__name__), inspect.isclass)

all_objects = {obj_name: obj_cls for obj_name, obj_cls in all_classes}
