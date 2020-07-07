from .level import LevelLoader
from .objects import Water, Land, UnPassableTerrain
import gym
import numpy as np


class SharkEnv(gym.Env):
    def __init__(self, app_path, level=0):
        self.levels = LevelLoader(app_path)
        self.current_level = self.levels[0]
        self.n_layers = 3
        self.water = None
        self.dt = 0.01

    def reset(self):
        self.current_level = self.levels[0]
        self.water = np.zeros(self.current_level.shape, dtype="bool")
        water_cells = [
            terrain
            for terrain in self.current_level.terrain
            if isinstance(terrain, Water)
        ]
        for water_cell in water_cells:
            self.water[water_cell.cell] = True
        return self.format_state()

    def format_state(self):
        state = np.zeros((self.n_layers, *self.current_level.shape), dtype="bool")
        state[0] = self.water
        for goodie in self.current_level.goodies:
            row, col = goodie.cell
            state[1, row, col] = True
        for baddie in self.current_level.baddies:
            row, col = baddie.cell
            state[2, row, col] = True
        return state

    def step(self, action):
        # level.move_ai or something
        # sharks_moving = any(shark.is_active for shark in baddies)
        # game_over = False
        # while sharks_moving or not game_over: level.step(self.dt)
        # return self.format_state, reward, game_over, info
        pass

