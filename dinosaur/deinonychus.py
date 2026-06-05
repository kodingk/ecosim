import random

import pygame

from behavior import Behavior
from behaviors.drink import Drink
from behaviors.hunt import Hunt
from behaviors.reproduce import Reproduce
from behaviors.seek_water import SeekWater
from behaviors.wander import Wander
from dinosaur.base import Dinosaur
from dinosaur.psittacosaurus import Psittacosaurus
from water.base import Water


class Deinonychus(Dinosaur):
    """중형 드로마이오사우루스 육식자. 사냥하고, 성체이고 배부르면 번식하고, 그 외엔 배회한다."""

    color = (170, 70, 60)
    size = 14
    level = 2  # 초식(1) 위에 그려져 시각적으로 구분
    sprite_name = "deinonychus"
    max_energy = 130.0  # 큰 에너지 reserve — 먹이 저점(prey trough)을 버틴다
    drain_rate = (
        2.5  # 저대사 — 포식 압력↓ + 기근 생존(130/2.5≈52초)으로 trough를 넘긴다
    )
    speed = 90.0  # 초식(60)보다 빨라 추격 가능
    sight = 140.0
    attack_distance = 18.0
    eat_gain = 48.0  # 킬당 이득 — 추격 비용과 균형
    hunt_hunger = 70.0  # 에너지가 이 값 이상이면 사냥 안 함(포만 → 개체당 포식률 상한)
    max_chase = 8.0  # 이 시간 동안 못 잡으면 지쳐 포기(피식자 탈출 창 보장)
    rest_duration = 3.0  # 포기 후 휴식 시간
    pack_radius = 0.0  # 0=솔로 사냥(검증된 안정 공존). >0이면 협동 사냥(무리와 함께 쓰면 재조정 필요)
    # 생활사: K-전략(늦게 성숙·긴 수명)
    maturity_age = 25.0
    senescence_age = 160.0
    mortality_rate = 0.012
    reproduce_threshold = 110.0  # 높은 임계값(max_energy 130 기준)
    reproduce_cost = 68.0
    reproduce_radius = 25.0
    breed_cooldown = 50.0  # 번식 후 휴지기(초) — 출생률 하드캡으로 boom 차단
    breed_territory = 250.0  # 이 반경 내 동족 있으면 번식 안 함(영역성 → 밀도 캡)
    # 수분: 포식자는 넓게 배회하므로 더 가뭄에 강하게(큰 리저브·낮은 임계·먼 시야).
    max_water = 120.0
    thirst_threshold = 35.0
    water_sight = 280.0
    # 낮·밤: cathemeral(상시 활동) — 밤에도 사냥한다. 야간 시야만 완만히 감소시켜 과포식 방지.
    vision_floor = 0.7  # 한밤 시야 배율(주간 대비 70%) — '밤 사냥꾼'이되 학살은 막는다

    def __init__(self, loc: pygame.Vector2, rng: random.Random):
        senesce_rng = random.Random(rng.random())
        super().__init__(loc, senesce_rng)
        repr_rng = random.Random(rng.random())
        wander_rng = random.Random(rng.random())
        child_src = random.Random(rng.random())
        # 우선순위: 물(마시기·찾기) > 사냥 > 번식 > 배회 (물은 게이트라 평소엔 사냥에 양보)
        self._behaviors: list[Behavior] = [
            Drink(self, Water, self.drink_distance, self.drink_rate),
            SeekWater(
                self,
                Water,
                self.water_sight,
                self.drink_distance,
                self.speed,
                self.thirst_threshold,
            ),
            Hunt(
                actor=self,
                target_classes=[Psittacosaurus],
                sight=self.sight,
                attack_distance=self.attack_distance,
                speed=self.speed,
                gain=self.eat_gain,
                hunt_hunger=self.hunt_hunger,
                max_chase=self.max_chase,
                rest_duration=self.rest_duration,
                pack_radius=self.pack_radius,  # 협동 사냥(공유 표적)
                vision_floor=self.vision_floor,  # 야간 시야 — 밤에도 사냥(cathemeral)
            ),
            Reproduce(
                self,
                threshold=self.reproduce_threshold,
                cost=self.reproduce_cost,
                radius=self.reproduce_radius,
                rng=repr_rng,
                factory=lambda loc: Deinonychus(loc, random.Random(child_src.random())),
                maturity_age=self.maturity_age,
                cooldown=self.breed_cooldown,  # 출생률 하드캡(boom 차단)
                crowd_radius=self.breed_territory,  # 영역성으로 포식자 밀도 캡
            ),
            Wander(self, wander_rng, self.speed),
        ]

    def behaviors(self):
        return self._behaviors

    def activity(self, daylight: float) -> float:
        return 1.0  # cathemeral — 밤에도 사냥하므로 휴면하지 않고 대사도 항시 정상
