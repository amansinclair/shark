import pyglet
import math
from .level import LevelLoader
from .render import Renderer
from .base import Cell
from .ai import SharkBaseline
from .env import SharkEnvPlay
from pathlib import Path
import time


class App(pyglet.window.Window):
    def __init__(self, app_path, H=920, W=768, show_all=False):
        super().__init__(W, H, fullscreen=False)
        pyglet.gl.glClearColor(0.1, 0.1, 0.1, 1)
        self.cell_size = 24
        self.app_path = app_path
        self.show_all = show_all
        self.renderer = Renderer(app_path, hud_height=128, hud_width=W, hud_cols=6)
        self.level_loader = LevelLoader(app_path)
        self.current_level_idx = 0
        self.current_level = None
        self.time_remaining = 0
        self.env = SharkEnvPlay()
        self.ai = SharkBaseline()
        self.level_running = False
        self.clicked = None
        self.objects_to_draw = []
        self.start_game()

    def start_game(self):
        self.current_level = self.level_loader[self.current_level_idx]
        obs = self.env.reset(self.current_level)
        self.ai.reset(obs)
        self.renderer.start_level(self.current_level)
        self.level_running = True
        self.time_remaining = self.current_level.time_limit
        pyglet.clock.schedule_interval(self.update_game, 1 / 60.0)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            self.clicked = x, y

    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            x, y = self.clicked
            if not self.renderer.hud.was_clicked(x, y):
                x = math.floor(x / self.cell_size)
                y = math.floor((y - self.renderer.hud.H) / self.cell_size)
                self.current_level.update(
                    self.renderer.hud.selected_character, Cell(x, y)
                )
            self.clicked = None

    def on_draw(self):
        self.clear()
        self.renderer.draw(self.objects_to_draw, self.time_remaining)

    def on_close(self):
        self.close()

    def update_game(self, dt):
        obs = self.env.get_obs()
        if obs:
            action = self.ai.step(obs)
            self.env.step(action)
        game_status = self.current_level.step(dt)
        if game_status.game_over:
            self.end_level(game_status)
        if self.show_all:
            visible_baddies = game_status.baddies
        else:
            visible_baddies = [
                baddie for baddie in game_status.baddies if baddie.is_visible
            ]
        self.objects_to_draw = game_status.goodies + visible_baddies
        self.time_remaining = int(
            self.current_level.time_limit - self.current_level.time_elapsed
        )

    def end_level(self, game_status):
        if game_status.won:
            print("you won!")
            self.current_level_idx += 1
        else:
            print("you lost!")
        self.current_level.save_log("replay_" + str(int(time.time())) + ".json")
        self.close()

    def run(self):
        pyglet.app.run()

    def __repr__(self):
        return f"Shark(Level: {self.current_level})"

