from .objects import Water
from .base import get_surrounding_cells, Cell, convert_to_ones, get_cells_in_block
import random
from collections import defaultdict, deque
import numpy as np


class Sector:
    def __init__(self):
        self.cells = set()
        self.n_visited = random.choice([0, 1, 2])

    def add(self, cell):
        self.cells.add(cell)

    def update(self):
        self.n_visited += 1

    def reset(self):
        self.n_visited = 0

    def get_cell(self):
        return random.choice(list(self.cells))

    def __lt__(self, other_cell):
        return self.n_visited < other_cell.n_visited

    def __contains__(self, cell):
        return cell in self.cells

    def __len__(self):
        return len(self.cells)

    def __repr__(self):
        return f"Sector(n_cells:{len(self)}, n_visited:{self.n_visited})"


class SharkAI:
    def __init__(self, current_level):
        self.shark = current_level.baddies[0]
        self.current_cell = self.shark.cell
        self.sectors = self.create_sectors(current_level)
        self.chasing = False

    def create_sectors(self, current_level):
        sectors = defaultdict(Sector)
        n_rows, n_cols = current_level.shape
        self.row_spacing, self.col_spacing = self.set_spacing(n_rows, n_cols)
        for cell in get_cells_in_block(0, n_cols, 0, n_rows):
            if isinstance(current_level.terrain_cells[cell], Water):
                idx = self.get_index(cell)
                sectors[idx].add(cell)
        return sectors

    def set_spacing(self, n_rows, n_cols, factor=4):
        return n_rows // factor, n_cols // factor

    def get_index(self, cell):
        return cell.y // self.row_spacing, cell.x // self.col_spacing

    def update_sectors(self):
        idx = self.get_index(self.shark.cell)
        self.sectors[idx].update()
        self.current_cell = self.shark.cell

    def update(self, level):
        if self.shark.cell != self.current_cell:
            self.update_sectors()
        goodie_in_water = self.goodie_in_water(level)
        if self.should_patrol(goodie_in_water, self.shark.is_active):
            print("PATROL")
            self.patrol(level)
        elif self.should_chase(goodie_in_water, self.shark.is_active):
            print("CHASE")
            self.get_goodie(goodie_in_water, level)

    def goodie_in_water(self, level):
        for goodie in level.goodies:
            goodie_in_water = isinstance(level.terrain_cells[goodie.cell], Water)
            goodie_is_visible = True  # self.shark.can_see(goodie.cell)
            if goodie_in_water and goodie_is_visible and goodie.is_alive:
                return goodie
        return False

    def should_patrol(self, goodie_in_water, is_active):
        if not goodie_in_water and self.chasing:
            return True
        if not goodie_in_water and not is_active and not self.chasing:
            return True
        return False

    def should_chase(self, goodie_in_water, is_active):
        if goodie_in_water:
            if not (is_active and self.chasing):
                return True
        return False

    def patrol(self, level):
        self.chasing = False
        sectors = list(self.sectors.values())
        for sector in sorted(sectors):
            cell = sector.get_cell()
            if cell not in self.shark.previous_cells:
                level.update_ai(0, cell)
                break

    def get_goodie(self, hero, level):
        self.chasing = True
        hero_x, hero_y = hero.cell
        shark_x, shark_y = self.current_cell
        dx = convert_to_ones(hero_x - shark_x)
        dy = convert_to_ones(hero_y - shark_y)
        if (dx, dy) != (0, 0):
            print(dx, dy)
            level.update_ai(0, Cell(shark_x + dx, shark_y + dy))
        else:
            print("zeros")
            self.patrol(level)


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
        self.actions = {(0, 1): 0, (0, -1): 1, (1, 0): 2, (-1, 0): 3}
        self.displacement_prefs = {
            (1, 0): [(1, 0), (0, 1), (0, -1), (-1, 0)],
            (1, -1): [(1, 0), (0, -1), (-1, 0), (0, -1)],
            (0, -1): [(0, -1), (1, 0), (-1, 0), (0, 1)],
            (-1, -1): [(-1, 0), (0, -1), (1, 0), (0, 1)],
            (-1, 0): [(-1, 0), (0, 1), (0, -1), (1, 0)],
            (-1, 1): [(-1, 0), (0, 1), (1, 0), (0, -1)],
            (0, 1): [(0, 1), (1, 0), (-1, 0), (0, -1)],
            (1, 1): [(1, 0), (0, 1), (-1, 0), (0, -1)],
        }

    def reset(self, state):
        n_sharks = state.shape[0] - self.sharks_idx
        self.histories = [deque(maxlen=6) for i in range(n_sharks)]
        self.current_cells = [(-1, -1)] * n_sharks
        _, self.max_y, self.max_x = state.shape

    def step(self, state):
        action = []
        water_layer = state[self.water_idx]
        human_cells = self.get_cells(state[self.food_idx])
        shark_cells = [
            self.get_cells(shark_layer) for shark_layer in state[self.sharks_idx :]
        ]
        for idx, shark_cell in enumerate(shark_cells):
            shark_cell = shark_cell[0]
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
        print("CHASE", idx)
        distances = [
            (self.get_distance(shark_cell, cell), i)
            for i, cell in enumerate(human_cells)
        ]
        _, i = min(distances)
        hx, hy = human_cells[idx]
        x, y = shark_cell
        key = (convert_to_ones(hx - x), convert_to_ones(hy - y))
        if key == (0, 0):
            key = random.choice(list(self.displacement_prefs.keys()))
        actions = self.displacement_prefs[key]
        return self.get_action(idx, shark_cell, actions, water_layer)

    def get_distance(self, shark_cell, cell):
        sx, sy = shark_cell
        x, y = cell
        return (sx - x) ** 2 + (sy - y) ** 2

    def patrol(self, idx, shark_cell, water_layer):
        print("PATROL")
        actions = list(self.actions.keys())
        random.shuffle(actions)
        return self.get_action(idx, shark_cell, actions, water_layer)

    def get_action(self, idx, shark_cell, actions, water_layer):
        visited_cells = self.histories[idx]
        action = None
        x, y = shark_cell
        for dx, dy in actions:
            row = y + dy
            col = x + dx
            if (
                (col, row) not in visited_cells
                and self.is_valid_cell((col, row))
                and water_layer[row, col]
            ):
                action = self.actions[(dx, dy)]
                break
        if action == None:
            print("STUCK")
            action = 0
        return action

    def is_valid_cell(self, cell):
        x, y = cell
        x_cond = x >= 0 and x < self.max_x
        y_cond = y >= 0 and y < self.max_y
        return x_cond and y_cond

