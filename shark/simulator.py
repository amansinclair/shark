from .level import LevelLoader
from .ai import SharkAI, Lemming


class Simulator:
    def __init__(self, app_path):
        self.app_path = app_path
        self.level_loader = LevelLoader(app_path)
        self.dt = 0.01

    def run(self, n_times=1):
        results = []
        for i in range(n_times):
            game_status = self.start_level()
            while game_status.game_over != True:
                self.lemming.update(self.level)
                self.sharkai.update(self.level)
                game_status = self.level.step(self.dt)
            print(game_status)
            results.append(game_status.won)
        print(sum(results) / len(results))

    def start_level(self):
        self.level = self.level_loader[0]
        self.sharkai = SharkAI(self.level)
        self.lemming = Lemming(self.level)
        game_status = self.level.step(self.dt)
        return game_status
