import pyglet
from pathlib import Path
from .base import Direction, Action

"""

- Start of level returns landscape
- Update of level returns characters

Render needs to:
Draw HUD and Landscape as batch
Draw each Character:
 - check action and select sprite
 - rescale X and Y positions
 - move sprite
 - draw sprite

 """


class Renderer:
    def __init__(self, app_path, cell_size=24):
        self.app_path = app_path
        self.cell_size = cell_size
        self.offset = cell_size // 2
        self.imgs = self.load_resources()
        self.reset()

    def load_resources(self):
        return {}

    def reset(self):
        self.previous_imgs = {}
        self.sprites = {}
        self.bg = self.set_bg()

    def set_bg(self, terrain_objects=None):
        bg = pyglet.graphics.Batch()
        if terrain_objects:
            for terrain_object in terrain_objects:
                x, y = self.convert_coords(terrain_object)
                img = self.get_img(terrain_object)
                self.sprites[terrain_object] = pyglet.sprite.Sprite(
                    img=img, x=x, y=y, batch=bg
                )
        return bg

    def get_img(self, game_object):
        key = self.get_key(game_object)
        return self.imgs[key]

    def get_key(self, game_object):
        class_name = game_object.__class__.__name__
        action = game_object.action
        direction = game_object.direction
        return "_".join((class_name, action, direction))

    def draw(self, game_objects):
        self.bg.draw()
        for game_object in game_objects:  # sort
            sprite = self.get_sprite(game_object)
            sprite.draw()
        # self.hud.draw() LATER

    def get_sprite(self, game_object):
        sprite = self.sprites[game_object]
        if game_object.is_dirty:
            x, y = self.convert_coords(game_object)
            img = self.get_img(game_object)
            if img == self.previous_imgs[game_object]:
                sprite.x = x
                sprite.y = y
            else:
                sprite = pyglet.sprite.Sprite(img=img, x=x, y=y)
                self.sprites[game_object] = sprite
        return sprite

    def convert_coords(self, game_object):
        return self.convert_coord(game_object.x), self.convert_coord(game_object.y)

    def convert_coord(self, x):
        return int(x * self.cell_size) + self.offset
