import random

import pygame

from behaviors.forage import Forage
from behaviors.graze import Graze
from behaviors.reproduce import Reproduce
from behaviors.wander import Wander
from dinosaur.base import Dinosaur
from plant.base import Plant


class Pteranodon(Dinosaur):
    """
    나는 초식 익룡(백악기). 풀을 뜯어 Psittacosaurus와 경쟁하지만, 날아다니므로 지상 포식자
    Deinonychus의 사냥 대상이 아니다(Hunt가 Psittacosaurus만 표적). 따라서 도주(Flee)도 없다.

    level=3으로 모든 지상 개체 위에 그려지고, 날개 실루엣 스프라이트로 구분된다. 비행은
    에너지를 많이 쓰므로(높은 drain) 개체수가 모델하게 유지돼 식물 경쟁이 과하지 않다.
    Dinosaur(동물 베이스)를 상속해 대사·생활사·gen을 그대로 재사용한다.
    """

    color = (120, 200, 210)  # 하늘빛 — 지상 개체와 대비
    size = 11
    level = 3  # 초식(1)·포식(2) 위에 그려진다(나는 존재)
    max_energy = 100.0
    drain_rate = 3.5  # 비행 비용 — 높은 대사로 개체수 자기 제한
    speed = 100.0  # 빠른 비행
    eat_distance = 40.0
    seek_distance = 160.0
    forage_hunger = 70.0
    graze_rate = 22.0
    # niche 분할: 풀을 '스치듯' 뜯고 8에서 떠난다(표면 채식). psitta(5까지)에게 5~8 하층 refuge.
    graze_min_biomass = 8.0
    # 개체수 상한 — 한 자원(식물)을 psitta와 공유하면 경쟁 배제가 일어나(시드 의존) 종종 익룡이
    # 전부 몰아낸다. 제한된 둥지터를 본떠 상한을 둬 boom을 막고 modest하게 유지 → 4종 공존 보장.
    max_count = 15
    # 생활사
    maturity_age = 18.0
    senescence_age = 85.0
    mortality_rate = 0.025
    reproduce_threshold = 95.0
    reproduce_cost = 55.0
    reproduce_radius = 25.0

    def __init__(self, loc, rng: random.Random):
        senesce_rng = random.Random(rng.random())
        super().__init__(loc, senesce_rng)
        repr_rng = random.Random(rng.random())
        wander_rng = random.Random(rng.random())
        child_src = random.Random(rng.random())
        # 우선순위: 풀뜯기 > 먹이탐색 > 번식 > 배회 (포식자가 무시하므로 도주 없음)
        self._behaviors = [
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
                factory=lambda loc: Pteranodon(loc, random.Random(child_src.random())),
                maturity_age=self.maturity_age,
                max_own_count=self.max_count,  # 개체수 상한 → boom·경쟁배제 방지
            ),
            Wander(self, wander_rng, self.speed),
        ]

    def behaviors(self):
        return self._behaviors

    def sprite(self) -> pygame.Surface:
        # 전진(+x) 방향 갈매기 실루엣 — 두 날개가 뒤로 젖혀진 형태. velocity로 회전해 난다.
        frac = min(1.0, 0.4 + 0.6 * (self.age / self.maturity_age))
        ln = max(6, int(self.size * 1.8 * frac))  # 앞뒤 길이
        sw = max(5, int(self.size * 1.4 * frac))  # 날개 폭(반)
        body = self.color
        dark = (int(body[0] * 0.6), int(body[1] * 0.6), int(body[2] * 0.6))
        surf = pygame.Surface((ln, 2 * sw), pygame.SRCALPHA)
        cy = sw
        # 앞쪽 머리(오른쪽) → 양 날개가 뒤(왼쪽)로 젖혀진 화살형 + 가운데 노치
        pygame.draw.polygon(
            surf,
            body,
            [(ln - 1, cy), (0, 0), (int(ln * 0.45), cy), (0, 2 * sw - 1)],
        )
        pygame.draw.line(surf, dark, (int(ln * 0.45), cy), (ln - 1, cy), 1)  # 몸통선
        if self.velocity.length_squared() > 0.01:
            surf = pygame.transform.rotate(surf, -self.velocity.as_polar()[1])
        return surf
