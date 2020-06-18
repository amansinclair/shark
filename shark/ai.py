from .objects import Water
from .base import get_surrounding_cells, Cell, convert_to_ones, get_cells_in_block
import random
from collections import defaultdict


class Sector:
    def __init__(self):
        self.cells = set()
        self.n_visited = 0

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
        self.patrolling = True

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
        hero_in_water = isinstance(level.terrain_cells[level.hero.cell], Water)
        if hero_in_water and self.shark.goal_cell:
            print("shit")
            self.get_goodie(level)
        else:
            self.patrol(level)

    def patrol(self, level):
        sectors = list(self.sectors.values())
        for sector in sorted(sectors):
            cell = sector.get_cell()
            if cell not in self.shark.previous_cells:
                self.shark.move_to(cell)
                break

    def get_goodie(self, level):
        hero_x, hero_y = level.hero.cell
        shark_x, shark_y = self.current_cell
        dx = convert_to_ones(hero_x - shark_x)
        dy = convert_to_ones(hero_y - shark_y)
        if (dx, dy) != (0, 0):
            self.shark.move_to(Cell(shark_x + dx, shark_y + dy))
        else:
            self.patrol(level)
