from .level import LevelLoader
from .objects import Water, Land, UnPassableTerrain
from .base import Cell
import gym
import numpy as np

Movements = {
    0: (0, 1),
    1: (0, -1),
    2: (1, 0),
    3: (-1, 0),
    4: (1, 1),
    5: (-1, -1),
    6: (1, -1),
    7: (-1, 1),
}


class SharkEnvPlay:
    def __init__(self):
        self.n_layers = 3

    def reset(self, level):
        self.current_level = level
        self.n_sharks = len(self.current_level.baddies)
        self.water = np.zeros(self.current_level.shape, dtype="bool")
        water_cells = [
            terrain
            for terrain in self.current_level.terrain
            if isinstance(terrain, Water)
        ]
        for water_cell in water_cells:
            col, row = water_cell.cell
            self.water[row, col] = True
        return self.format_state()

    def get_obs(self):
        if not self.sharks_active():
            return self.format_state()
        return []

    def format_state(self):
        rows, cols = self.current_level.shape
        layout = np.zeros((self.n_layers, rows, cols), dtype="bool")
        shark_info = np.zeros(((3 * self.n_sharks) + 1), dtype="float32")
        layout[0] = self.water
        for goodie in self.current_level.goodies:
            if self.is_water(goodie.cell) and goodie.is_alive:
                row, col = goodie.cell
                layout[1, row, col] = True
        idx = 0
        for baddie in self.current_level.baddies:
            row, col = baddie.cell
            layout[2, row, col] = True
            shark_info[idx] = baddie.current_health / baddie.max_health
            shark_info[idx + 1] = baddie.cell.x / cols
            shark_info[idx + 2] = baddie.cell.y / rows
            idx += 3
        shark_info[-1] = self.current_level.time_elapsed / self.current_level.time_limit
        return [layout, shark_info]

    def is_water(self, cell):
        terrain = self.current_level.terrain_cells[cell]
        return isinstance(terrain, Water)

    def step(self, action):
        """Updates character goals but doesn't step the current level forward."""
        for idx, a in enumerate(action):
            dx, dy = Movements[a]
            character = self.current_level.baddies[idx]
            cell = Cell(character.cell.x + dx, character.cell.y + dy)
            self.current_level.update(character, cell)

    def sharks_active(self):
        return any(shark.is_active for shark in self.current_level.baddies)


class SharkEnvTrain(SharkEnvPlay):
    def __init__(self, app_path, level_idx=0, dt=0.01):
        super().__init__()
        self.levels = LevelLoader(app_path)
        self.level_idx = level_idx
        self.dt = dt

    def reset(self):
        state = super().reset(self.levels[self.level_idx])
        return state

    def step(self, action):
        """Updates character goals and steps the current level forward until a shark is has reached next goal."""
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


class HumanEnvPlay:
    def _init__(self):
        self.n_players = 4
        self.n_layers = 4

    def reset(self, level):
        self.current_level = level
        self.water = self.get_map_of_type(Water)
        self.unpassable = self.get_map_of_type(UnPassableTerrain)
        return self.format_state()

    def get_map_of_type(self, cell_type):
        a = np.zeros(self.current_level.shape, dtype="bool")
        cells = [
            terrain.cell
            for terrain in self.current_level.terrain
            if isinstance(terrain, cell_type)
        ]
        for cell in cells:
            col, row = cell
            a[row, col] = True
        return a

    def format_state(self):
        rows, cols = self.current_level.shape
        layout = np.zeros((self.n_layers, rows, cols), dtype="bool")
        goodie_info = np.zeros(((3 * self.n_players) + 1), dtype="float32")
        layout[0] = self.water
        layout[1] = self.unpassable
        idx = 0
        for goodie in self.current_level.goodies:
            row, col = goodie.cell
            layout[2, row, col] = True
            goodie_info[idx] = goodie.current_health / goodie.max_health
            goodie_info[idx + 1] = goodie.cell.x / cols
            goodie_info[idx + 2] = goodie.cell.y / rows
            idx += 3
        goodie_info[-1] = (
            self.current_level.time_elapsed / self.current_level.time_limit
        )
        for baddie in self.current_level.baddies:
            row, col = baddie.cell
            layout[3, row, col] = True
        return [layout, goodie_info]


class TrainingEnv:
    def __init__(self, app_path, human_ai, shark_ai, dt=0.01, level_idx=0):
        self.app_path = app_path
        self.human_ai = human_ai
        self.shark_ai = shark_ai
        self.levels = LevelLoader(app_path)
        self.level_idx = level_idx
        self.dt = dt

    def run(self):
        self.current_level = self.levels[self.level_idx]
        self.n_goodies = len(self.current_level.goodies)
        game_over = False
        human_reward = None
        shark_reward = None
        while not game_over:
            if self.ready_for_action(self.current_level.goodies):
                human_action = self.human_ai.step(
                    self.format_state_for_humans(), human_reward, game_over
                )
                self.update_level_for_humans(human_action)
            if self.ready_for_action(self.current_level.baddies):
                shark_action = self.shark_ai.step(
                    self.format_state_for_sharks(), shark_reward, game_over
                )
                self.update_level_for_sharks(shark_action)
            game_over, won, goodies, baddies = self.current_level.step(self.dt)
            human_reward = -self.n_goodies
            shark_reward = self.n_goodies
        human_reward, shark_reward = self.get_final_rewards(won)
        self.shark_ai.step(self.format_state_for_sharks(), shark_reward, game_over)
        self.human_ai.step(self.format_state_for_humans(), human_reward, game_over)

    def ready_for_action(self, characters):
        return any((not character.is_active for character in characters))

    def format_state_for_humans(self):
        pass

    def format_state_for_sharks(self):
        pass

    def update_level_for_humans(self, action):
        # translate actions
        # self.current_level.update(character, cell)
        pass

    def update_level_for_sharks(self, action):
        # translate actions
        # self.current_level.update(character, cell)
        pass

    def get_final_rewards(self, won):
        human_reward = -self.n_goodies
        shark_reward = self.n_goodies
        shark_speed = self.current_level.goodies[0].land_speed
        time_remaining = self.current_level.time_limit - self.current_level.time_elapsed
        total_points = shark_speed * self.current_level.time_limit * self.n_goodies
        reward_remaining = shark_speed * time_remaining * self.n_goodies
        if won:
            human_reward += total_points
            shark_reward -= total_points
        else:
            human_reward -= reward_remaining
            shark_reward += reward_remaining
        return human_reward, shark_reward

