import random
from typing import TYPE_CHECKING

import pygame

from actions.age import Age
from actions.drain_energy import DrainEnergy
from entity import Entity, EntityStatus

if TYPE_CHECKING:
    from action import Action
    from behavior import Behavior


class Dinosaur(Entity):
    """
    공룡 베이스. 가변 위치(loc)·에너지·나이(age)를 소유한다.

    생활사(life history)를 나이로 모델링한다 — 미성숙 개체(age < maturity_age)는 번식하지
    못하고 작게 그려지며, 노쇠기(age ≥ senescence_age)에 들면 매 틱 확률적으로 죽는다(Age).
    이 둘이 출생/사망에 지연·기저사망률을 더해 개체수 과폭발을 인위적 캡 없이 감쇠한다.

    구체 종은 color/size/level/speed와 생활사 파라미터를 바꾸고 behaviors()를 구현한다.
    """

    color: tuple[int, int, int] = (200, 200, 200)
    size: int = 14
    level: int = 1  # 식물(0) 위에 그려진다
    max_energy: float = 100.0
    drain_rate: float = 5.0  # 에너지/초
    # 생활사 — 나이 기반
    maturity_age: float = 15.0  # 이 나이 이상이어야 번식 가능(미성숙은 작게 렌더)
    senescence_age: float = 120.0  # 이 나이부터 노화사(확률적) 시작
    mortality_rate: float = 0.02  # 노쇠기 진입 후 초당 사망 확률(hazard)

    def __init__(self, loc: pygame.Vector2, rng: random.Random | None = None):
        self.loc = pygame.Vector2(loc)
        self.velocity = pygame.Vector2(0, 0)  # 직전 틱 이동 변위(set_location이 갱신). boids 정렬용.
        self.energy = self.max_energy / 2  # 절반에서 시작(처음엔 배고픔)
        self.age = 0.0
        self.last_breed_age = -1.0e9  # 마지막 번식 시점(나이). 번식 쿨다운 계산용.
        self._rng = rng or random.Random()  # 노화사 판정용 전용 스트림(순서 독립)

    def behaviors(self) -> list["Behavior"]:
        return []

    def passive_actions(self, dt: float) -> list["Action"]:
        return [
            DrainEnergy(self, self.drain_rate * dt),
            Age(self, dt, self.senescence_age, self.mortality_rate, self._rng),
        ]

    @property
    def status(self) -> EntityStatus:
        return EntityStatus(
            loc=pygame.Vector2(self.loc),
            level=self.level,
            velocity=pygame.Vector2(self.velocity),
        )

    @status.setter
    def status(self, value: EntityStatus) -> None:
        self.loc = value.loc
        self.level = value.level

    def sprite(self) -> pygame.Surface:
        # 미성숙 개체는 작게 — 나이에 따라 크기가 자란다(0.4→1.0배).
        if self.maturity_age > 0:
            frac = min(1.0, 0.4 + 0.6 * (self.age / self.maturity_age))
        else:
            frac = 1.0
        s = max(3, int(self.size * frac))
        surface = pygame.Surface((s, s))
        surface.fill(self.color)
        return surface

    @classmethod
    def gen(cls, world_size: tuple[int, int], rng: random.Random) -> "Dinosaur":
        # 월드 안 임의 위치에 전용 rng를 들려 생성한다. 구체 종은 __init__(loc, rng)을
        # 공유하므로 Psittacosaurus·Deinonychus가 그대로 상속한다(중복 제거).
        loc = pygame.Vector2(
            rng.uniform(0, world_size[0]), rng.uniform(0, world_size[1])
        )
        return cls(loc, rng)
