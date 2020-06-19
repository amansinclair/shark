import pyglet
import json
from collections import deque
from shark.level import LevelLoader, Event
from shark.render import Renderer
from shark.base import Cell
from pathlib import Path


class Replayer(pyglet.window.Window):
    def __init__(self, app_path, log_file, speed=3, H=480, W=480):
        super().__init__(W, H, fullscreen=False)
        self.app_path = app_path
        self.speed = speed
        self.level_loader = LevelLoader(app_path)
        self.renderer = Renderer(app_path)
        self.log = self.load_log(log_file)
        self.objects_to_draw = []
        self.start_level()

    def load_log(self, log_path):
        log_path = self.app_path / log_path
        with open(log_path, "r") as log_file:
            log = json.load(log_file)
        return log

    def start_level(self):
        self.level = self.level_loader[self.log["name"]]
        self.events = deque(Event(*args) for args in self.log["events"])
        self.current_time = 0.0
        self.next_event = self.events.popleft()
        self.renderer.start_level(self.level.terrain)
        dt = self.log["total_time"] / self.log["n_updates"]
        pyglet.clock.schedule_interval(self.update, dt)

    def update(self, dt):
        for i in range(self.speed):
            self.current_time += dt
            if self.next_event and self.current_time >= self.next_event.time:
                self.run_event()
                if self.events:
                    self.next_event = self.events.popleft()
            game_status = self.level.step(dt)
            if game_status.game_over:
                self.close()
        self.objects_to_draw = game_status.goodies + game_status.baddies

    def run_event(self):
        cell = Cell(self.next_event.x, self.next_event.y)
        if self.next_event.character_type == "Baddie":
            self.level.update_ai(cell)
        else:
            self.level.update(self.level.goodies[0], cell)

    def on_draw(self):
        self.clear()
        self.renderer.draw(self.objects_to_draw)


if __name__ == "__main__":
    cwd = Path.cwd()
    replay = Replayer(cwd, "test.json")
    pyglet.app.run()
