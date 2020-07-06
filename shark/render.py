import pyglet
import json
from pathlib import Path
from collections import defaultdict
from .base import Direction, Action
from .objects import Character


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
        object_name = specs["obj_name"]
        frames = specs["frames"]
        animations = specs["animations"]
        n_rows = int(specs["n_rows"])
        n_cols = int(specs["n_cols"])
        if animations:
            img_grid = pyglet.image.ImageGrid(img, n_rows, n_cols)
            for i, animation in enumerate(animations):
                key = object_name + "_" + animation["name"]
                imgs[key] = self.extract_animation(img_grid, i, animation)
        elif frames:
            img_grid = pyglet.image.ImageGrid(img, n_rows, n_cols)
            for i, frame in enumerate(frames):
                key = object_name + "_" + frame["name"]
                imgs[key] = img_grid[i]
        else:
            imgs[object_name] = img

    def extract_animation(self, img_grid, row, animation):
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
    def __init__(self, app_path, hud, cell_size=24):
        self.hud = hud
        self.hud_offset = self.hud.H
        self.cell_size = cell_size
        self.offset = cell_size // 2
        self.imgs = ImageLoader(app_path)
        self.selected = pyglet.sprite.Sprite(img=self.imgs["Selected_box"], x=0, y=0)

    def start_level(self, terrain_objects=None):
        self.previous_imgs = {}
        self.sprites = {}
        self.bg = pyglet.graphics.Batch()
        if terrain_objects:
            for terrain_object in terrain_objects:
                x, y = self.convert_coords(terrain_object)
                img = self.get_img(terrain_object)
                self.sprites[terrain_object] = pyglet.sprite.Sprite(
                    img=img, x=x, y=y, batch=self.bg
                )

    def get_img(self, game_object):
        key = self.get_key(game_object.name, game_object.direction, game_object.action)
        return self.imgs[key]

    def get_key(self, name, direction=None, action=None):
        key = str(name)
        if action:
            key += "_" + str(action.name)
        if direction:
            key += "_" + str(direction.name)
        return key

    def draw(self, game_objects):
        self.bg.draw()
        for game_object in game_objects:  # sort
            sprite = self.get_sprite(game_object)
            sprite.draw()
        self.draw_hud()

    def get_sprite(self, game_object):
        img = self.get_img(game_object)
        x, y = self.convert_coords(game_object)
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
            return (self.convert_character_x(x), self.convert_character_y(y))
        else:
            return (self.convert_terrain_coord_x(x), self.convert_terrain_coord_y(y))

    def convert_character_x(self, x):
        return int((x + 0.5) * self.cell_size) - 16

    def convert_character_y(self, y):
        return int((y * self.cell_size)) + 8 + self.hud_offset

    def convert_terrain_coord_x(self, x):
        return int(x * self.cell_size)

    def convert_terrain_coord_y(self, y):
        return int(y * self.cell_size) + self.hud_offset

    def draw_hud(self):
        x = self.hud.selected_x
        self.selected.x = x
        self.selected.draw()

