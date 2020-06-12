from shark.render import ImageLoader, get_key
from shark.base import Action, Direction
from pathlib import Path
from pyglet.image import Animation, ImageData


def get_image_loader():
    cwd = Path.cwd()
    return ImageLoader(cwd)


def test_image_loader_size():
    loader = get_image_loader()
    assert len(loader) > 0


def test_image_loader_return_type():
    loader = get_image_loader()
    key = get_key("Water", Action.stand, Direction.south)
    img = loader[key]
    assert (isinstance(img, ImageData) or isinstance(img, Animation)
