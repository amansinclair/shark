from shark.env import SharkEnvPlay
from shark.level import LevelLoader
from shark.ai import SharkBaseline
from pathlib import Path
import matplotlib.pyplot as plt

levels = LevelLoader(Path.cwd())

env = SharkEnvPlay()
level = levels[0]
shark = SharkBaseline()
obs = env.reset(level)
shark.reset(obs)
action = shark.step(obs)
print(action)
# plt.imshow(obs[2])
# plt.show()

