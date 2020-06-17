import math
import time
import inspect
import json
from collections import namedtuple, defaultdict
from .objects import (
    Hero,
    Goal,
    Goodie,
    Baddie,
    Terrain,
    Water,
    Character,
    all_objects,
    GameObject,
    Surrounds,
)
from .base import get_surrounding_cells, get_cells_in_block, Cell


class LevelLoader:

    fields = ["name", "shape", "time_limit", "terrain", "game_objects"]

    def __init__(self, app_path):
        level_paths = self.get_level_files(app_path)
        self.level_specs = self.load_levels(level_paths)

    def __len__(self):
        return len(self.level_specs)

    def __getitem__(self, idx):
        level_spec = self.level_specs[idx]
        return self.build_level(level_spec)

    def __repr__(self):
        return f"LevelLoader({len(self)})"

    def get_level_files(self, app_path):
        level_folder = app_path / "shark" / "levels"
        level_paths = [
            file_path
            for file_path in level_folder.iterdir()
            if file_path.suffix == ".json"
        ]
        return level_paths

    def load_levels(self, level_paths):
        level_specs = []
        for level_path in level_paths:
            with open(level_path, "r") as level_file:
                level_specs.append(json.load(level_file))
        return level_specs

    def build_level(self, level_spec):
        args = [level_spec[key] for key in self.fields]
        return Level(*args)


class Level:
    def __init__(self, name, shape, time_limit, terrain, game_objects):
        self.name = name
        self.shape = shape
        self.time_limit = time_limit
        self.time_elapsed = 0.0
        self.terrain = self.build_terrain(terrain)
        self.terrain_cells = self.get_cell_dict(self.terrain)
        self.hero = None
        self.goal = None
        self.goodies = []
        self.baddies = []
        self.characters = []
        self.build_game_objects(game_objects)
        self.goodie_cells = self.get_cell_dict(self.goodies)
        self.baddie_cells = self.get_cell_dict(self.baddies)

    def __repr__(self):
        return f"Level(name: {self.name}, shape: {self.shape}, time: {self.time_elapsed:.1f} / {self.time_limit})"

    def build_terrain(self, terrain):
        terrain_objects = self.spawn_objects(terrain)
        all_cells = get_cells_in_block(0, self.shape[1], 0, self.shape[0])
        taken_cells = set(terrain_object.cell for terrain_object in terrain_objects)
        free_cells = all_cells.difference(taken_cells)
        for free_cell in free_cells:
            terrain_objects.append(Water(name="Water", x=free_cell.x, y=free_cell.y))
        return terrain_objects

    def build_game_objects(self, game_objects):
        spawned_objects = self.spawn_objects(game_objects)
        for game_object in spawned_objects:
            self.classify_object(game_object)

    def spawn_objects(self, game_objects):
        spawned_objects = []
        for object_name, kwargs in game_objects:
            if object_name in all_objects:
                object_class = all_objects[object_name]
                spawned_objects.append(object_class(**kwargs))
        return spawned_objects

    def get_cell_dict(self, game_objects):
        cell_dict = defaultdict(GameObject)
        for game_object in game_objects:
            for cell in game_object.cells:
                cell_dict[cell] = game_object
        return cell_dict

    def classify_object(self, game_object):
        if isinstance(game_object, Goal):
            self.goal = game_object
        if isinstance(game_object, Character):
            self.characters.append(game_object)
        if isinstance(game_object, Goodie):
            self.goodies.append(game_object)
        if isinstance(game_object, Hero):
            self.hero = game_object
        if isinstance(game_object, Baddie):
            self.baddies.append(game_object)

    @property
    def times_up(self):
        return self.time_elapsed > self.time_limit

    @property
    def is_completed(self):
        return bool(self.hero.is_alive and not self.times_up)

    def update(self, selected_goodie, cell):
        if cell in self.goodie_cells:
            character = self.goodie_cells[cell]
            self.check_for_follow(selected_goodie, character)
        else:
            selected_goodie.move_to(cell)

    def check_for_follow(self, selected_goodie, character):
        if character != selected_goodie:
            pass  # setup following

    def step(self, dt):
        self.time_elapsed += dt
        if self.hero.cell in self.goal:
            return Result(game_over=True, won=True)
        elif self.times_up or not self.hero.is_alive:
            return Result(game_over=True, won=False)
        else:
            self.step_characters(dt)
            self.goodie_cells = self.get_cell_dict(self.goodies)
            self.baddie_cells = self.get_cell_dict(self.baddies)
        return Result(game_over=False, characters=self.characters)

    def step_characters(self, dt):
        for character in self.characters:
            if character.is_active:
                cells = get_surrounding_cells(
                    character.cell, character.shape, self.shape
                )
                terrain = self.get_surrounding_objects(cells, self.terrain_cells)
                goodies = self.get_surrounding_objects(cells, self.goodie_cells)
                baddies = self.get_surrounding_objects(cells, self.baddie_cells)
                character.step(dt, Surrounds(terrain, goodies, baddies))

    def get_surrounding_objects(self, cells, cell_dict):
        d = defaultdict(GameObject)
        for cell in cells:
            d[cell] = cell_dict[cell]
        return d


class Result:
    def __init__(self, game_over, won=False, characters=None):
        self.game_over = game_over
        self.won = won
        self.characters = characters if characters else []

    def __bool__(self):
        return self.game_over
