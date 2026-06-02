import random

import pygame

from plant.base import Plant
from simulator import Simulator

if __name__ == "__main__":
    simulator = Simulator()

    # 결정성/재현성을 위해 고정 시드로 식물을 흩뿌린다.
    width, height = simulator.screen.get_size()
    rng = random.Random(42)
    for _ in range(40):
        loc = pygame.Vector2(rng.uniform(0, width), rng.uniform(0, height))
        simulator.world.spawn(Plant(loc))

    simulator.run()
