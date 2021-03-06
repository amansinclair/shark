from .objects import Water
from .base import (
    get_surrounding_cells,
    Cell,
    convert_to_ones,
    get_cells_in_block,
    displacement_preferences,
)
import random
from collections import defaultdict, deque
import numpy as np


class Lemming:
    def __init__(self, current_level):
        self.hero = current_level.hero
        self.goal = current_level.goal
        current_level.update(self.hero, self.get_random_cell())

    def get_random_cell(self):
        row = random.choice([i for i in range(20)])
        col = random.choice([i for i in range(20)])
        return Cell(col, row)

    def update(self, level):
        if not self.hero.is_active:
            level.update(self.hero, self.goal)


class SharkBaseline:
    def __init__(self):
        self.water_idx = 0
        self.food_idx = 1
        self.sharks_idx = 2
        self.histories = None
        self.actions = {
            (0, 1): 0,
            (0, -1): 1,
            (1, 0): 2,
            (-1, 0): 3,
            (1, 1): 4,
            (-1, -1): 5,
            (1, -1): 6,
            (-1, 1): 7,
        }

    def reset(self, state):
        state, info = state
        n_sharks = info.shape[0] // 3
        self.histories = [deque(maxlen=5) for i in range(n_sharks)]
        self.current_cells = [(-1, -1)] * n_sharks
        _, self.max_y, self.max_x = state.shape

    def step(self, state):
        state, info = state
        action = []
        water_layer = state[self.water_idx]
        human_cells = self.get_cells(state[self.food_idx])
        shark_cells = self.get_cells(state[self.sharks_idx])
        for idx, shark_cell in enumerate(shark_cells):
            shark_cell = shark_cell
            old_cell = self.current_cells[idx]
            if shark_cell != old_cell:
                self.histories[idx].append(old_cell)
                self.current_cells[idx] = shark_cell
            if human_cells:
                action.append(self.chase(idx, shark_cell, human_cells, water_layer))
            else:
                action.append(self.patrol(idx, shark_cell, water_layer))
        return action

    def get_cells(self, layer):
        cells = []
        if layer.max() != 0:
            rows, cols = np.where(layer == True)
            cells = [row_col for row_col in zip(rows, cols)]
        return cells

    def chase(self, idx, shark_cell, human_cells, water_layer):
        distances = [
            (self.get_distance(shark_cell, cell), i)
            for i, cell in enumerate(human_cells)
        ]
        _, i = min(distances)
        hx, hy = human_cells[i]
        x, y = shark_cell
        key = (convert_to_ones(hx - x), convert_to_ones(hy - y))
        if key == (0, 0):
            key = random.choice(list(displacement_preferences.keys()))
        actions = displacement_preferences[key]
        return self.get_action(idx, shark_cell, actions, water_layer)

    def get_distance(self, shark_cell, cell):
        sx, sy = shark_cell
        x, y = cell
        return (sx - x) ** 2 + (sy - y) ** 2

    def patrol(self, idx, shark_cell, water_layer):
        actions = list(self.actions.keys())
        random.shuffle(actions)
        return self.get_action(idx, shark_cell, actions, water_layer)

    def get_action(self, idx, shark_cell, actions, water_layer):
        visited_cells = self.histories[idx]
        action = self.get_action_from_group(
            shark_cell, actions, visited_cells, water_layer
        )
        if action == None:
            actions = list(self.actions.keys())
            action = self.get_action_from_group(
                shark_cell, actions, visited_cells, water_layer
            )
        if action == None:
            action = 0
        return action

    def get_action_from_group(self, shark_cell, actions, visited_cells, water_layer):
        action = None
        x, y = shark_cell
        for dx, dy in actions:
            row = y + dy
            col = x + dx
            if self.is_valid_cell(row, col, visited_cells, water_layer):
                action = self.actions[(dx, dy)]
                break
        return action

    def is_valid_cell(self, row, col, visited_cells, water_layer):
        not_visited = (col, row) not in visited_cells
        is_on_map = self.is_on_map(row, col)
        is_water = water_layer[row, col] if is_on_map else False
        return all((not_visited, is_on_map, is_water))

    def is_on_map(self, row, col):
        col_cond = col >= 0 and col < self.max_x
        row_cond = row >= 0 and row < self.max_y
        return col_cond and row_cond

