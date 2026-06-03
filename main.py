import random

from dinosaur.deinonychus import Deinonychus
from dinosaur.psittacosaurus import Psittacosaurus
from dinosaur.pteranodon import Pteranodon
from plant.base import Plant
from simulator import Simulator

if __name__ == "__main__":
    simulator = Simulator()

    # 결정성/재현성을 위해 고정 시드. 각 개체에는 전용 RNG 스트림을 나눠 준다(순서 독립).
    master = random.Random(42)
    size = simulator.world.size

    # 초기 개체수는 안정 공존이 검증된 수용력 근처 값(헤드리스 5/5 시드).
    for _ in range(120):
        simulator.world.spawn(Plant.gen(size, random.Random(master.random())))

    for _ in range(40):
        simulator.world.spawn(Psittacosaurus.gen(size, random.Random(master.random())))

    for _ in range(3):
        simulator.world.spawn(Deinonychus.gen(size, random.Random(master.random())))

    for _ in range(12):
        simulator.world.spawn(Pteranodon.gen(size, random.Random(master.random())))

    simulator.run()
