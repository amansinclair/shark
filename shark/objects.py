import math
import time
import inspect
import importlib
from collections import deque, namedtuple
from .base import Cell, get_cells_in_block, Action, Compass_four, Direction


class GameObject:
    """Base class for all game objects."""

    def __init__(self, name=None, x=0.0, y=0.0, shape=(1, 1)):
        self.name = name
        self.x = x
        self.y = y
        self.shape = shape
        self.action = Action.stand
        self.direction = Direction.south

    @property
    def cell(self):
        return Cell(round(self.x), round(self.y))

    @property
    def cells(self):
        if self.shape != (1, 1):
            cell_x, cell_y = self.cell
            max_x = cell_x + self.shape[1]
            max_y = cell_y + self.shape[0]
            return get_cells_in_block(cell_x, max_x, cell_y, max_y)
        else:
            return set([self.cell])

    def __contains__(self, cell):
        return cell in self.cells

    def __repr__(self):
        cls = self.__class__.__name__
        return f"{cls}(name: {self.name}, x: {self.x:.1f}, y: {self.y:.1f})"

    def step(self, dt, terrain, objects):
        pass


class Terrain(GameObject):
    """Base class for regions of a level."""


class Water(Terrain):
    """A water region passable to all."""


class Land(Terrain):
    """A land region passable only to Goodies."""


class UnPassableTerrain(Terrain):
    """A region unpassable to all Characters."""


class Goal(GameObject):
    """A point that defines where the Hero must go!."""


class MoveableObject(GameObject):
    """Class that supports movement."""

    water_speed = 1
    land_speed = 2
    angle = math.cos(math.pi / 4)
    displacement_prefs = {
        (1, 0): [(1, 0), (1, 1), (1, -1)],
        (1, -1): [(1, -1), (1, 0), (0, -1)],
        (0, -1): [(0, -1), (1, -1), (-1, -1)],
        (-1, -1): [(-1, -1), (0, -1), (-1, 0)],
        (-1, 0): [(-1, 0), (-1, -1), (-1, 1)],
        (-1, 1): [(-1, 1), (-1, 0), (0, 1)],
        (0, 1): [(0, 1), (-1, 1), (1, 1)],
        (1, 1): [(1, 1), (0, 1), (1, 0)],
    }

    def __init__(self, is_on_land=True, **kwargs):
        super().__init__(**kwargs)
        self.dirty = True
        self.is_on_land = is_on_land
        self.clear()

    @property
    def is_active(self):
        return bool(self.goal_cell)

    def clear(self):
        self.goal_cell = None
        self.next_cell = None
        self.next_displacement = None
        self.step_size = 0
        self.direction = Direction.south
        self.action = Action.stand if self.is_on_land else Action.tread_water

    def recenter(self):
        self.next_cell = self.cell
        self.goal_cell = self.cell

    def move_to(self, cell):
        if not self.goal_cell:
            self.next_cell = self.cell
        self.goal_cell = cell

    def step(self, dt, terrain, objects):
        self.dirty = False
        if self.goal_cell:
            self.dirty = True
            self.set_stepsize(dt, terrain)
            self.move(terrain, objects)

    def set_stepsize(self, dt, terrain):
        self.is_on_land = isinstance(terrain[self.cell], Land)
        self.action = Action.walk if self.is_on_land else Action.swim
        current_speed = self.land_speed if self.is_on_land else self.water_speed
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
        displacement_prefs = self.displacement_prefs[index]
        self.set_next_cell(displacement_prefs, terrain, objects)

    def set_next_cell(self, displacement_prefs, terrain, objects):
        self.next_cell = None
        for dx, dy in displacement_prefs:
            cell = Cell(self.cell.x + dx, self.cell.y + dy)
            if self.is_free_cell(cell, terrain, objects):
                self.next_cell = cell
                self.next_displacement = (dx, dy)
                self.direction = Compass_four[(dx, dy)]
                break

    def is_free_cell(self, cell, terrain, objects):
        """To be implemented by subclasses."""
        return True

    def take_step(self):
        sx, sy = self.next_displacement
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
        self.step_size -= abs(dx_actual) + abs(dy_actual)


class Character(MoveableObject):
    """Class that has health and supports movement."""

    max_health = 100

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_health = self.max_health

    @property
    def is_alive(self):
        return bool(self.current_health > 0)

    def step(self, dt, terrain, objects):
        if self.is_alive:
            super().step(dt, terrain, objects)

    def take_damage(self, damage):
        if self.is_alive:
            self.current_health -= damage
            self.action = Action.attacked if self.is_alive else Action.die
            self.dirty = True

    def __lt__(self, character):
        if self.y == character.y:
            return self.x < character.x
        else:
            return self.y < character.y


class Goodie(Character):
    """Character that needs to reach goal."""

    def is_free_cell(self, cell, terrain, objects):
        if isinstance(terrain[cell], UnPassableTerrain) or isinstance(
            objects[cell], Goodie
        ):
            return False
        return True


class Hero(Goodie):
    pass


class Baddie(Character):
    """Character that can do damage to Goodies."""


class Shark(Baddie):
    land_speed = 0
    water_speed = 2
    damage = 10

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.action = Action.swim
        self.previous_cells = deque(maxlen=6)

    def step(self, dt, terrain, objects):
        if self.is_alive:
            super().step(dt, terrain, objects)
            goodie_in_cell = objects[self.cell]
            if goodie_in_cell:
                self.attack(goodie_in_cell, dt)

    def attack(self, goodie, dt):
        damage = self.damage * dt
        self.action = Action.attack
        goodie.take_damage(damage)

    def is_free_cell(self, cell, terrain, objects):
        if isinstance(terrain[cell], Land) or cell in self.previous_cells:
            return False
        return True


all_classes = inspect.getmembers(importlib.import_module(__name__), inspect.isclass)

all_objects = {obj_name: obj_cls for obj_name, obj_cls in all_classes}
