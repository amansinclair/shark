import pyglet
import math
from .level import LevelLoader
from .render import Renderer
from .base import Cell
from .ai import SharkAI
from pathlib import Path


class App(pyglet.window.Window):
    def __init__(self, app_path, H=896, W=768, show_all=False):
        super().__init__(W, H, fullscreen=False)
        pyglet.gl.glClearColor(0.1, 0.1, 0.1, 1)
        self.app_path = app_path
        self.show_all = show_all
        self.hud = HUD(H=128, W=W)
        self.renderer = Renderer(app_path, self.hud)
        self.level_loader = LevelLoader(app_path)
        self.current_level_idx = 0
        self.current_level = None
        self.ai = None
        self.level_running = False
        self.clicked = None
        self.objects_to_draw = []
        self.start_game()

    def start_game(self):
        self.current_level = self.level_loader[self.current_level_idx]
        self.hud.reset(self.current_level.goodies)
        self.ai = SharkAI(self.current_level)
        self.renderer.start_level(self.current_level.terrain)
        self.level_running = True
        pyglet.clock.schedule_interval(self.update_game, 1 / 120.0)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            self.clicked = x, y

    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            x, y = self.clicked
            if not self.hud.was_clicked(x, y):
                x = math.floor(x / 24)
                y = math.floor((y - self.hud.H) / 24)
                self.current_level.update(self.hud.selected_character, Cell(x, y))
            self.clicked = None

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
        # self.current_level.save_log("test.json")
        self.close()

    def run(self):
        pyglet.app.run()

    def __repr__(self):
        return f"Shark(Level: {self.current_level})"


class HUD:
    def __init__(self, H, W, n_cols=6):
        self.H = H
        self.W = W
        self.dx = W // n_cols
        self.characters = None
        self.selected_x = None

    def reset(self, characters):
        self.characters = characters
        self.selected_x = 0
        self.selected_character = characters[0]

    def was_clicked(self, x, y):
        if x < self.W and y < self.H:
            self.process_click(x, y)
            return True
        return False

    def process_click(self, x, y):
        idx = x // self.dx
        character = self.characters[idx]
        if character.is_alive:
            self.selected_character = character
            self.selected_x = idx * self.dx

