import pyglet
import os
import math
from .level import LevelLoader
from .render import Renderer
from .base import Cell
from .ai import SharkAI
from pathlib import Path


class App(pyglet.window.Window):
    def __init__(self, app_path, H=480, W=480, show_all=True):
        super().__init__(W, H, fullscreen=False)
        self.app_path = app_path
        self.show_all = show_all
        self.renderer = Renderer(app_path)
        self.level_loader = LevelLoader(app_path)
        self.current_level_idx = 0
        self.current_level = None
        self.selected_character = None
        self.ai = None
        self.level_running = False
        self.clicked = self.reset_click()
        self.objects_to_draw = []
        self.start_game()

    def reset_click(self):
        return (None, None)

    def start_game(self):
        self.current_level = self.level_loader[self.current_level_idx]
        self.selected_character = self.current_level.hero
        self.ai = SharkAI(self.current_level)
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

    def on_close(self):
        self.close()

    def update_game(self, dt):
        self.ai.update(self.current_level)
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

    def end_level(self, game_status):
        if game_status.won:
            print("you won!")
            self.current_level_idx += 1
        else:
            print("you lost!")
        self.close()

    def run(self):
        pyglet.app.run()

    def __repr__(self):
        return f"Shark(Level: {self.current_level})"
