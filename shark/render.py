import pyglet
import json
from pathlib import Path
from collections import defaultdict
from .base import Direction, Action
from .objects import Character


def get_key(name, action, direction):
    return "_".join((str(name), str(action), str(direction)))


class ImageLoader:
    def __init__(self, app_path):
        self.folder = app_path / "shark" / "graphics"
        img_spec_paths = self.get_file_paths(".json")
        img_paths = self.get_file_paths(".png")
        self.imgs = self.create_imgs(img_spec_paths, img_paths)

    def get_file_paths(self, file_type):
        paths = [
            file_path
            for file_path in self.folder.iterdir()
            if file_path.suffix == file_type
        ]
        return paths

    def create_imgs(self, img_spec_paths, img_paths):
        imgs = {}
        img_names = [path.name for path in img_paths]
        for img_spec_path in img_spec_paths:
            specs = self.load_specs(img_spec_path)
            img_filename = specs["filename"]
            if img_filename in img_names:
                self.create_img(imgs, specs, img_filename)
        return imgs

    def load_specs(self, spec_path):
        with open(spec_path, "r") as spec_file:
            specs = json.load(spec_file)
        return specs

    def create_img(self, imgs, specs, img_name):
        img = pyglet.image.load(self.folder / img_name)
        object_name = specs["name"]
        animations = specs["animations"]
        n_rows = int(specs["n_rows"])
        n_cols = int(specs["n_cols"])
        if animations:
            img_grid = pyglet.image.ImageGrid(img, n_rows, n_cols)
            for i, animation in enumerate(animations):
                action = Action[animation["action"]]
                direction = Direction[animation["direction"]]
                key = get_key(object_name, action, direction)
                imgs[key] = self.extract_img_seq(img_grid, i, animation)
        else:
            action = Action.stand
            direction = Direction.south
            key = get_key(object_name, action, direction)
            if key not in imgs.keys():
                imgs[key] = img

    def extract_img_seq(self, img_grid, row, animation):
        length = int(animation["length"])
        loop = animation["loop"]
        dt = float(animation["dt"])
        start = row * img_grid.columns
        stop = start + length
        return pyglet.image.Animation.from_image_sequence(
            img_grid[start:stop], dt, loop
        )

    def __len__(self):
        return len(self.imgs)

    def __getitem__(self, index):
        return self.imgs[index]


class Renderer:
    def __init__(self, app_path, cell_size=24):
        self.cell_size = cell_size
        self.offset = cell_size // 2
        self.imgs = ImageLoader(app_path)
        self.reset()

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
        key = get_key(game_object.name, game_object.action, game_object.direction)
        return self.imgs[key]

    def draw(self, game_objects):
        self.bg.draw()
        for sprite in self.sprites.values():
            sprite.draw()
        for game_object in game_objects:  # sort
            sprite = self.get_sprite(game_object)
            sprite.draw()
        # self.hud.draw() LATER

    def get_sprite(self, game_object):
        x, y = self.convert_coords(game_object)
        img = self.get_img(game_object)
        if game_object in self.previous_imgs and img == self.previous_imgs[game_object]:
            sprite = self.move_sprite(game_object, x, y)
        else:
            sprite = self.create_new_sprite(game_object, img, x, y)
        return sprite

    def create_new_sprite(self, game_object, img, x, y):
        sprite = pyglet.sprite.Sprite(img=img, x=x, y=y)
        self.sprites[game_object] = sprite
        self.previous_imgs[game_object] = img
        return sprite

    def move_sprite(self, game_object, x, y):
        sprite = self.sprites[game_object]
        sprite.x = x
        sprite.y = y
        return sprite

    def convert_coords(self, game_object):
        x = game_object.x
        y = game_object.y
        if isinstance(game_object, Character):
            return (self.convert_character_coord(x), self.convert_character_coord(y))
        else:
            return (self.convert_terrain_coord(x), self.convert_terrain_coord(y))

    def convert_character_coord(self, x):
        return int(x * self.cell_size) + self.offset

    def convert_terrain_coord(self, x):
        return int(x * self.cell_size)
