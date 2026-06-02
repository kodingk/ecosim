import random

import pygame

from dinosaur.deinonychus import Deinonychus
from dinosaur.psittacosaurus import Psittacosaurus
from plant.base import Plant
from simulator import Simulator

if __name__ == "__main__":
    simulator = Simulator()
    width, height = simulator.screen.get_size()

    # 결정성/재현성을 위해 고정 시드. 각 동물에는 전용 RNG 스트림을 나눠 준다(순서 독립).
    master = random.Random(42)

    for _ in range(40):
        loc = pygame.Vector2(master.uniform(0, width), master.uniform(0, height))
        simulator.world.spawn(Plant(loc))

    for _ in range(8):
        loc = pygame.Vector2(master.uniform(0, width), master.uniform(0, height))
        simulator.world.spawn(Psittacosaurus(loc, random.Random(master.random())))

    for _ in range(3):
        loc = pygame.Vector2(master.uniform(0, width), master.uniform(0, height))
        simulator.world.spawn(Deinonychus(loc, random.Random(master.random())))

    simulator.run()
