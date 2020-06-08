import pyglet
import os
from .server import Server


class MainWindow(pyglet.window.Window):
    def __init__(self, app_path, map_size=(10, 10), obj_size=32, overlap=0.125):
        self.overlap = overlap
        self.offset = int(obj_size * overlap)
        self.cell_size = obj_size - self.offset
        W = self.get_res(map_size[1], obj_size)
        H = self.get_res(map_size[0], obj_size)
        self.map_size = map_size
        self.obj_size = obj_size
        super().__init__(W, H, fullscreen=False)  # w, h
        self.app_path = app_path
        self.server = Server(self.app_path)
        self.clicked = self.reset_click()

    def get_res(self, S, s):
        return int(s * ((2 * self.overlap) + ((1 - (2 * self.overlap)) * S)))

    def reset_click(self):
        return (None, None)

    def start_game(self):
        # self.server.start_level()
        # self.level_running = True
        pyglet.clock.schedule_interval(self.update_game, 1 / 120.0)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            print(x, y)
            self.clicked = (
                max(0, (x - self.offset)) // self.cell_size,
                max(0, (y - self.offset)) // self.cell_size,
            )

    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            print(self.clicked)
            self.server.add_event(self.clicked)
            self.clicked = self.reset_click()

    def on_draw(self):
        self.clear()
        # self.renderer.render()

    def on_close(self):
        self.close()

    def update_game(self, dt):
        pass
        # self.server.update(dt)

    def run(self):
        pyglet.app.run()
