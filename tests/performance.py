from shark.level import LevelLoader
from shark.base import Cell
from pathlib import Path
import time

dt = 0.01
loader = LevelLoader(Path.cwd())
level_one = loader[0]
hero = level_one.hero
level_one.update(hero, Cell(18, 18))
i = 0
t1 = time.time()
while hero.is_active:
    i += 1
    level_one.step(dt)
dt = time.time() - t1
print(i, dt / i)
