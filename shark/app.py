import pyglet
import os
import math
from .level import LevelLoader
from .render import Renderer
from .base import Cell
from pathlib import Path


class App(pyglet.window.Window):
    def __init__(self, app_path, H=480, W=480):
        super().__init__(W, H, fullscreen=False)
        self.app_path = app_path
        self.renderer = Renderer(app_path)
        self.level_loader = LevelLoader(app_path)
        self.current_level_idx = 0
        self.current_level = None
        self.selected_character = None
        self.level_running = False
        self.clicked = self.reset_click()
        self.objects_to_draw = []
        self.start_game()

    def reset_click(self):
        return (None, None)

    def start_game(self):
        self.current_level = self.level_loader[self.current_level_idx]
        self.selected_character = self.current_level.hero
        self.renderer.start_level(self.current_level.terrain)
        self.level_running = True
        pyglet.clock.schedule_interval(self.update_game, 1 / 120.0)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            x = math.floor(x / 24)
            y = math.floor(y / 24)
            self.clicked = Cell(x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            self.current_level.update(self.selected_character, self.clicked)
            self.clicked = self.reset_click()

    def on_draw(self):
        self.clear()
        self.renderer.draw(self.objects_to_draw)
        # render cursor?

    def on_close(self):
        self.close()

    def update_game(self, dt):
        game_status = self.current_level.step(dt)
        if game_status:
            self.end_level(game_status)
        self.objects_to_draw = game_status.characters

    def end_level(self, game_status):
        if game_status.won:
            self.current_level_idx += 1

    def run(self):
        pyglet.app.run()

    def __repr__(self):
        return f"Shark(Level: {self.current_level})"