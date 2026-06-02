import random

from behaviors.hunt import Hunt
from behaviors.wander import Wander
from dinosaur.base import Dinosaur
from dinosaur.psittacosaurus import Psittacosaurus


class Deinonychus(Dinosaur):
    """중형 드로마이오사우루스 육식자. 초식 공룡을 쫓아 사냥하고, 배부르면 배회한다."""

    color = (170, 70, 60)
    size = 14
    level = 2  # 초식(1) 위에 그려져 시각적으로 구분
    speed = 90.0  # 초식(60)보다 빨라 추격 가능
    sight = 180.0
    attack_distance = 18.0
    eat_gain = 35.0

    def __init__(self, loc, rng: random.Random):
        super().__init__(loc)
        # 우선순위: 사냥 > 배회. 먹이 종류(초식 공룡)는 클래스로 주입한다.
        self._behaviors = [
            Hunt(
                actor=self,
                target_classes=[Psittacosaurus],
                sight=self.sight,
                attack_distance=self.attack_distance,
                speed=self.speed,
                gain=self.eat_gain,
            ),
            Wander(self, rng, self.speed),
        ]

    def behaviors(self):
        return self._behaviors
