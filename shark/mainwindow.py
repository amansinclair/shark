import pyglet
import os
from .server import Server
from .render import Renderer


class MainWindow(pyglet.window.Window):
    def __init__(self, app_path, H=776, W=680):
        super().__init__(W, H, fullscreen=False)
        self.app_path = app_path
        self.server = Server(self.app_path)
        self.renderer = Renderer(self.app_path)
        self.level_running = False
        self.clicked = self.reset_click()
        self.objects_to_draw = []

    def reset_click(self):
        return (None, None)

    def start_game(self):
        bg = self.server.start_level()
        self.renderer.set_bg(bg)
        self.level_running = True
        pyglet.clock.schedule_interval(self.update_game, 1 / 120.0)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            self.clicked = (x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            self.server.add_event(self.clicked)
            self.clicked = self.reset_click()

    def on_draw(self):
        self.clear()
        self.renderer.draw(self.objects_to_draw)
        # render cursor?

    def on_close(self):
        self.close()

    def update_game(self, dt):
        update_result = self.server.update(dt)
        self.objects_to_draw = update_result.characters

    def run(self):
        pyglet.app.run()
