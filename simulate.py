from pathlib import Path
from shark.simulator import Simulator

cwd = Path.cwd()
sim = Simulator(cwd)
sim.run(20)
