from .objects import Water
from .base import get_surrounding_cells, Cell, convert_to_ones
import random


class SharkAI:
    def __init__(self, shark):
        self.shark = shark
        self.displacement = (1, 0)
        self.movement_count = 0
        self.goodie_position = None
        self.cells = []

    def update(self, level):
        if not self.shark.goal_cell:
            if isinstance(level.terrain_cells[level.hero.cell], Water):
                self.get_goodie(level)
            else:
                self.patrol(level)
                self.goodie_position = None

    def patrol(self, level):
        x, y = self.shark.cell
        dx, dy = self.displacement
        cell = Cell(x + dx, y + dy)
        next_cells = set(
            cell
            for cell in get_surrounding_cells(self.shark.cell)
            if self.is_valid_cell(cell, level)
        )
        if next_cells:
            if self.movement_count < 3 and cell in next_cells:
                self.shark.move_to(cell)
                self.movement_count += 1
            else:
                next_cell = random.choice(list(next_cells))
                self.shark.move_to(next_cell)
                self.displacement = (next_cell.x - x, next_cell.y - y)
                self.movement_count = 0

    def is_valid_cell(self, cell, level):
        is_water = isinstance(level.terrain_cells[cell], Water)
        not_visited = cell not in self.shark.previous_cells
        return bool(is_water and not_visited)

    def get_goodie(self, level):
        x_offset = 0
        y_offset = 0
        current_x, current_y = level.hero.cell
        if self.goodie_position:
            x, y = self.goodie_position
            x_offset = current_x - x
            y_offset = current_y - y
        self.goodie_position = level.hero.cell
        dx = convert_to_ones(current_x - self.shark.x)
        dy = convert_to_ones(current_y - self.shark.y)
        print(dx, dy)
        self.shark.move_to(Cell(self.shark.cell.x + dx, self.shark.cell.y + dy))
