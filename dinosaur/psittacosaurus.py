import random

from behaviors.flee import Flee
from behaviors.flock import Flock
from behaviors.forage import Forage
from behaviors.graze import Graze
from behaviors.reproduce import Reproduce
from behaviors.wander import Wander
from dinosaur.base import Dinosaur
from plant.base import Plant


class Psittacosaurus(Dinosaur):
    """소형 각룡 초식자(다산·무리). 포식자를 피하고, 풀을 찾아 뜯고, 성체이고 배부르면 번식한다."""

    color = (210, 180, 120)
    size = 12
    level = 1
    drain_rate = 2.5  # 에너지/초
    speed = 60.0  # px/s
    flee_speed = 80.0  # 도주 속도 — 포식자(90)보다 살짝 느려 추격은 가능하되 비용이 큼
    flee_radius = 120.0  # 단독 감지 반경(무리면 vigilance로 더 멀리)
    vigilance_bonus = 0.0  # 0=집단경계 비활성(무리를 꺼서 불필요). >0이면 many-eyes 활성
    vigilance_cap = 3  # 최대 가산 동족 수(vigilance_bonus>0일 때만 의미)
    eat_distance = 40.0
    seek_distance = 150.0  # 이 반경의 풀을 향해 이동(Forage)
    forage_hunger = 70.0  # 에너지가 이 값 미만일 때만 적극 탐색
    graze_rate = 25.0  # 에너지/초 — 풀(biomass)을 뜯는 속도
    graze_min_biomass = 5.0  # 풀이 이만큼 남으면 버리고 이동(giving-up density)
    # 무리(Flock) 비활성: clustering이 prey를 과보호(떼 도주 → 포식자 catch율↓)해 포식자를
    # 굶겨 공존을 깬다. 다중 시드 검증 결과 보이는 무리와 안정 공존은 양립 불가라, 안정을 위해
    # herd_radius=0으로 끈다(이웃을 못 찾아 Flock이 항상 None → baseline 동작). 올리면 무리 부활.
    herd_radius = 0.0  # >0이면 이 반경의 동족과 무리짓기(boids)
    herd_separation = 24.0  # 이보다 가까운 동족은 밀어낸다
    herd_cohesion = 0.5  # 응집 가중치
    herd_alignment = 0.4  # 정렬 가중치
    # 생활사: r-전략(빨리 성숙·짧은 수명)
    maturity_age = 12.0
    senescence_age = 80.0
    mortality_rate = 0.02
    reproduce_threshold = 90.0
    reproduce_cost = 50.0
    reproduce_radius = 20.0

    def __init__(self, loc, rng: random.Random):
        senesce_rng = random.Random(rng.random())
        super().__init__(loc, senesce_rng)
        repr_rng = random.Random(rng.random())
        wander_rng = random.Random(rng.random())
        child_src = random.Random(rng.random())
        # 우선순위: 도주 > 풀뜯기 > 먹이탐색 > 번식 > 무리 > 배회
        # Forage(분산)가 Flock(응집)보다 위라, 배고프면 풀 찾아 흩어지고 배부르면 무리로 합류한다.
        # (Deinonychus는 import 시 순환을 피하려 지역 import)
        from dinosaur.deinonychus import Deinonychus

        self._behaviors = [
            Flee(
                self,
                Deinonychus,
                self.flee_radius,
                self.flee_speed,
                vigilance_radius=self.herd_radius,
                vigilance_bonus=self.vigilance_bonus,
                vigilance_cap=self.vigilance_cap,
            ),
            Graze(
                self, Plant, self.eat_distance, self.graze_rate, self.graze_min_biomass
            ),
            Forage(
                self,
                Plant,
                self.seek_distance,
                self.eat_distance,
                self.speed,
                self.forage_hunger,
                self.graze_min_biomass,
            ),
            Reproduce(
                self,
                threshold=self.reproduce_threshold,
                cost=self.reproduce_cost,
                radius=self.reproduce_radius,
                rng=repr_rng,
                factory=lambda loc: Psittacosaurus(
                    loc, random.Random(child_src.random())
                ),
                maturity_age=self.maturity_age,
            ),
            Flock(
                self,
                self.herd_radius,
                self.herd_separation,
                self.speed,
                w_cohesion=self.herd_cohesion,
                w_alignment=self.herd_alignment,
            ),
            Wander(self, wander_rng, self.speed),
        ]

    def behaviors(self):
        return self._behaviors
