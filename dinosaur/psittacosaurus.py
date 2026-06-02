import random

from behaviors.eat import Eat
from behaviors.wander import Wander
from dinosaur.base import Dinosaur
from plant.base import Plant


class Psittacosaurus(Dinosaur):
    """소형 각룡 초식자(다산·무리). 식물을 먹고, 배고프지 않으면 배회한다."""

    color = (210, 180, 120)
    size = 12
    level = 1
    speed = 60.0  # px/s
    eat_distance = 16.0
    eat_gain = 20.0

    def __init__(self, loc, rng: random.Random):
        super().__init__(loc)
        # 우선순위: 먹기 > 배회. 먹이 종류(식물)는 클래스로 주입한다.
        self._behaviors = [
            Eat(self, [Plant], self.eat_distance, self.eat_gain),
            Wander(self, rng, self.speed),
        ]

    def behaviors(self):
        return self._behaviors
