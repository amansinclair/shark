from .objects import Water
from .base import get_surrounding_cells, Cell, convert_to_ones, get_cells_in_block
import random
from collections import defaultdict


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
        hero_in_water = self.hero_in_water(level)
        if self.should_patrol(hero_in_water, self.shark.is_active):
            self.patrol(level)
        elif self.should_chase(hero_in_water, self.shark.is_active):
            self.get_goodie(hero_in_water, level)

    def hero_in_water(self, level):
        for goodie in level.goodies:
            hero_in_water = isinstance(level.terrain_cells[goodie.cell], Water)
            hero_is_visible = self.shark.can_see(goodie.cell)
            if hero_in_water and hero_is_visible:
                return goodie
        return False

    def should_patrol(self, hero_in_water, is_active):
        if not hero_in_water and self.chasing:
            return True
        if not hero_in_water and not is_active and not self.chasing:
            return True
        return False

    def should_chase(self, hero_in_water, is_active):
        if hero_in_water:
            if not (is_active and self.chasing):
                return True
        return False

    def patrol(self, level):
        self.chasing = False
        sectors = list(self.sectors.values())
        for sector in sorted(sectors):
            cell = sector.get_cell()
            if cell not in self.shark.previous_cells:
                level.update_ai(cell)
                break

    def get_goodie(self, hero, level):
        self.chasing = True
        hero_x, hero_y = hero.cell
        shark_x, shark_y = self.current_cell
        dx = convert_to_ones(hero_x - shark_x)
        dy = convert_to_ones(hero_y - shark_y)
        if (dx, dy) != (0, 0):
            level.update_ai(Cell(shark_x + dx, shark_y + dy))
        else:
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
