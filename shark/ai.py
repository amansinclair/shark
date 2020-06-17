from .objects import Water


class SharkAI:
    def __init__(self, shark):
        self.shark = shark

    def update(self, level):
        if isinstance(level.terrain_cells[level.hero.cell], Water):
            self.get_goodie(level)
        else:
            self.patrol(level)

    def patrol(self, level):
        # get nearest_cell to goal
        # get_free_cells
        pass

    def get_goodie(self, level):
        pass
