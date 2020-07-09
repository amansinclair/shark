from .level import LevelLoader
from .objects import Water, Land, UnPassableTerrain
from .base import Cell
import gym
import numpy as np


class SharkEnvPlay:
    def __init__(self, n_layers=2):
        self.n_layers = 2
        self.movements = {
            0: (0, 1),
            1: (0, -1),
            2: (1, 0),
            3: (-1, 0),
            4: (1, 1),
            5: (-1, -1),
            6: (1, -1),
            7: (-1, 1),
        }

    def reset(self, level):
        self.current_level = level
        self.water = np.zeros(self.current_level.shape, dtype="bool")
        water_cells = [
            terrain
            for terrain in self.current_level.terrain
            if isinstance(terrain, Water)
        ]
        for water_cell in water_cells:
            col, row = water_cell.cell
            self.water[row, col] = True
        self.n_layers += len(self.current_level.baddies)
        return self.format_state()

    def get_obs(self):
        if not self.sharks_active():
            return self.format_state()
        return np.zeros((1))

    def format_state(self):
        state = np.zeros((self.n_layers, *self.current_level.shape), dtype="bool")
        state[0] = self.water
        for goodie in self.current_level.goodies:
            if self.is_water(goodie.cell) and goodie.is_alive:
                row, col = goodie.cell
                state[1, row, col] = True
        for idx, baddie in enumerate(self.current_level.baddies):
            row, col = baddie.cell
            state[idx + 2, row, col] = True
        return state

    def is_water(self, cell):
        terrain = self.current_level.terrain_cells[cell]
        return isinstance(terrain, Water)

    def step(self, action):
        for idx, a in enumerate(action):
            dx, dy = self.movements[a]
            character = self.current_level.baddies[idx]
            cell = Cell(character.cell.x + dx, character.cell.y + dy)
            self.current_level.update(character, cell)

    def sharks_active(self):
        return any(shark.is_active for shark in self.current_level.baddies)


class SharkEnvTrain(SharkEnvPlay):
    def __init__(self, app_path, level=0, n_layers=2, dt=0.01):
        super().__init__(self, n_layers)
        self.levels = LevelLoader(app_path)
        self.level = level
        self.water = None
        self.dt = dt

    def reset(self):
        state = super().reset(self.levels[self.level])
        return state

    def step(self, action):
        super().step(action)
        game_over = False
        reward = 1
        info = {}
        while self.sharks_active() or not game_over:
            game_over, won, goodies, baddies = level.step(self.dt)
        if game_over and not won:  # won implies goodies won
            reward += int(
                self.current_level.time_limit - self.current_level.time_elapsed
            )
        return self.format_state, reward, game_over, info


class HumanEnvTrain:
    def __init__(self):
        self.n_layers = 2
        self.movements = {
            0: (0, 1),
            1: (0, -1),
            2: (1, 0),
            3: (-1, 0),
            4: (1, 1),
            5: (-1, -1),
            6: (1, -1),
            7: (-1, 1),
        }

    def reset(self, level):
        self.current_level = level
        self.water = np.zeros(self.current_level.shape, dtype="bool")
        water_cells = [
            terrain
            for terrain in self.current_level.terrain
            if isinstance(terrain, Water)
        ]
        for water_cell in water_cells:
            col, row = water_cell.cell
            self.water[row, col] = True
        self.n_layers += len(self.current_level.baddies)
        return self.format_state()
