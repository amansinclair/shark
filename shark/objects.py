import math
import time
import inspect
import importlib
from collections import deque, namedtuple
from itertools import chain
from .base import (
    Cell,
    get_cells_in_block,
    Action,
    Compass_four,
    Direction,
    get_surrounding_cells,
    convert_to_ones,
    displacement_preferences,
)


Surrounds = namedtuple("Surrounds", "terrain goodies baddies")


class GameObject:
    """Base class for all game objects."""

    def __init__(self, name=None, x=0.0, y=0.0, shape=(1, 1)):
        self.name = name
        self.x = x
        self.y = y
        self.shape = shape
        self.action = None
        self.direction = Direction.south
        self.visible = True

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

    def step(self, dt, surrounds):
        pass

    def __bool__(self):
        if self.__class__.__name__ == "GameObject":
            return False
        return True


class Terrain(GameObject):
    """Base class for regions of a level."""


class Water(Terrain):
    """A water region passable to all."""


class Land(Terrain):
    """A land region passable only to Goodies."""


class UnPassableTerrain(Land):
    """A region unpassable to all Characters."""


class Goal(GameObject):
    """A point that defines where the Hero must go!."""


class MoveableObject(GameObject):
    """Class that supports movement."""

    water_speed = 1.5
    land_speed = 3
    displacement_prefs = displacement_preferences

    def __init__(self, is_on_land=True, **kwargs):
        super().__init__(**kwargs)
        self.default_action = Action.tread_water
        self.is_on_land = True
        self.clear()

    @property
    def is_active(self):
        return bool(self.goal_cell)

    def clear(self):
        self.goal_cell = None
        self.next_cell = None
        self.dx_dy = None
        self.step_size = 0
        self.direction = Direction.south
        self.action = Action.stand if self.is_on_land else self.default_action

    def move_to(self, cell):
        if cell != self.cell:
            if not self.goal_cell:
                self.next_cell = self.cell
            self.goal_cell = cell

    def step(self, dt, surrounds):
        if self.goal_cell:
            distance = self.get_distance(dt, surrounds.terrain)
            self.move(distance, surrounds)

    def get_distance(self, dt, terrain):
        self.is_on_land = isinstance(terrain[self.cell], Land)
        self.action = Action.walk if self.is_on_land else Action.swim
        current_speed = self.land_speed if self.is_on_land else self.water_speed
        return current_speed * dt

    def move(self, distance, surrounds):
        while distance > 0:
            self.confirm_next_cell(surrounds)
            if self.next_cell:
                distance = self.take_step(distance)
            else:
                self.clear()
                break

    def confirm_next_cell(self, surrounds):
        if not self.next_cell or (self.x, self.y) == self.next_cell:
            self.choose_next_cell(surrounds)
        else:
            if not self.is_free_cell(self.next_cell, surrounds):
                if self.next_cell == self.goal_cell:
                    self.goal_cell = self.cell  # stop
                self.next_cell = self.cell  # recenter self

    def choose_next_cell(self, surrounds):
        self.next_cell = None
        self.direction = None
        self.dx_dy = None
        dx = self.goal_cell.x - self.cell.x
        dy = self.goal_cell.y - self.cell.y
        idx = (convert_to_ones(dx), convert_to_ones(dy))
        if idx != (0, 0):
            displacement_prefs = self.displacement_prefs[idx]
            self.set_best_cell(displacement_prefs, surrounds)

    def set_best_cell(self, displacement_prefs, surrounds):
        for dx, dy in displacement_prefs:
            cell = Cell(self.cell.x + dx, self.cell.y + dy)
            if self.is_free_cell(cell, surrounds):
                self.next_cell = cell
                self.dx_dy = (dx, dy)
                self.direction = Compass_four[self.dx_dy]
                break

    def is_free_cell(self, cell, surrounds):
        """To be implemented by subclasses."""
        return True

    def take_step(self, displacement):
        sx, sy = self.dx_dy
        displacement -= self.update_position(sx * displacement, sy * displacement)
        return displacement

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
        return abs(dx_actual) + abs(dy_actual)


class Character(MoveableObject):
    """Class that has health and supports movement."""

    max_health = 100
    visible_distance = 4

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_health = self.max_health
        self.is_visible = False

    @property
    def is_alive(self):
        return bool(self.current_health > 0)

    def step(self, dt, surrounds):
        if self.is_alive:
            super().step(dt, surrounds)

    def take_damage(self, damage):
        if self.is_alive:
            self.current_health -= damage
            # self.action = Action.attacked if self.is_alive else Action.die

    def __lt__(self, character):
        if self.y == character.y:
            return self.x < character.x
        else:
            return self.y < character.y

    def can_see(self, cell):
        x = abs(self.cell.x - cell.x)
        y = abs(self.cell.y - cell.y)
        return bool(x <= self.visible_distance and y <= self.visible_distance)

    def is_spotted(self, spotters):
        self.is_visible = False
        for spotter in spotters:
            if spotter.can_see(self.cell):
                self.is_visible = True
                break


class Goodie(Character):
    """Character that needs to reach goal."""

    def is_free_cell(self, cell, surrounds):
        is_not_terrain = not isinstance(surrounds.terrain[cell], Terrain)
        is_unpassable = isinstance(surrounds.terrain[cell], UnPassableTerrain)
        is_occupied = (
            isinstance(surrounds.goodies[cell], Goodie)
            and surrounds.goodies[cell].is_alive
        )
        return not any((is_not_terrain, is_unpassable, is_occupied))


class Hero(Goodie):
    pass


class Baddie(Character):
    """Character that can do damage to Goodies."""


class Shark(Baddie):
    land_speed = 0
    water_speed = 3
    damage = 100

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.default_action = Action.swim
        self.action = Action.swim
        self.previous_cells = deque(maxlen=3)
        self.previous_cells.append(self.cell)

    def step(self, dt, surrounds):
        if self.is_alive:
            # add die if position doesn't change
            cell = self.cell
            x, y = self.x, self.y
            super().step(dt, surrounds)
            if (self.x, self.y) == (x, y):
                self.current_health -= 40
                # set action to dead
            else:
                self.current_health = self.max_health
                if self.cell != cell:
                    self.previous_cells.append(self.cell)
                goodie_in_cell = surrounds.goodies[self.cell]
                if goodie_in_cell:
                    self.attack(goodie_in_cell, dt)

    def attack(self, goodie, dt):
        # print("goodie is", goodie)
        damage = self.damage * dt
        self.action = Action.attack
        goodie.take_damage(damage)

    def is_free_cell(self, cell, surrounds):
        is_not_terrain = not isinstance(surrounds.terrain[cell], Terrain)
        is_land = isinstance(surrounds.terrain[cell], Land)
        have_visited = cell in self.previous_cells
        is_occupied = isinstance(surrounds.baddies[cell], Baddie)
        return not any((is_land, have_visited, is_occupied, is_not_terrain))


all_classes = inspect.getmembers(importlib.import_module(__name__), inspect.isclass)

all_objects = {obj_name: obj_cls for obj_name, obj_cls in all_classes}
