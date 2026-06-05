import random
from typing import TYPE_CHECKING

import pygame

import sprites
from actions.regrow import Regrow
from behaviors.spread import Spread
from entity import Entity, EntityStatus

if TYPE_CHECKING:
    from action import Action
    from behavior import Behavior
    from world import WorldSnapshot


class Plant(Entity):
    """
    생산자(식물) 베이스. 판단 행동은 확산(Spread)뿐이고 이동하지 않으며, 렌더 최하층
    (level=0)으로 다른 개체 아래에 깔린다.

    핵심은 **biomass(현존량)** 다 — 초식자가 뜯으면(Bite) biomass가 줄고, 매 틱 regrow_rate
    로 회복한다. biomass가 0이어도 **죽지 않고**(초지 영속) 계속 회복하므로 먹이가 절대 0으로
    붕괴하지 않는다. 즉 식물은 '소멸하는 토큰'이 아니라 '재생 가능한 연속 자원'이며, 이것이
    초식자 개체수 폭락(zero-floor collapse)을 막는 토대다.

    구체 식물(양치·침엽수 등)은 색·크기·level·biomass 파라미터만 바꿔 상속한다.
    """

    color: tuple[int, int, int] = (50, 150, 60)
    size: int = 10
    level: int = 0
    spread_rate: float = 0.2  # 스폰/초
    spread_radius: float = 150.0  # 넓은 반경으로 지역 고갈 완화
    max_plants: int = 150  # 월드 내 식물 개체 상한
    max_biomass: float = 20.0  # 포기당 최대 현존량(= 초식자가 뜯어갈 수 있는 에너지)
    # biomass/초 회복(광합성). 낮·밤에서 daylight를 곱하면 사이클 평균이 절반이 되므로,
    # 평균 공급을 종전(≈1.3)과 맞추려 약 2배로 둔다 — 낮에 몰리되 총 부양력은 보존.
    regrow_rate: float = 2.6
    spread_min_biomass: float = 10.0  # 이 이상 건강할 때만 번식(과방목 시 확산 정지)

    def __init__(
        self,
        loc: pygame.Vector2,
        rng: random.Random | None = None,
        world_size: tuple[int, int] | None = None,
    ):
        self._loc = pygame.Vector2(loc)
        self.biomass = self.max_biomass  # 가득 찬 상태로 시작
        rng = rng or random.Random()
        ws = world_size
        self._spread = Spread(
            self,
            rng=rng,
            rate=self.spread_rate,
            radius=self.spread_radius,
            max_plants=self.max_plants,
            plant_class=Plant,
            factory=lambda loc: Plant(loc, random.Random(rng.random()), ws),
            world_size=ws,
            min_biomass=self.spread_min_biomass,
        )

    def behaviors(self) -> list["Behavior"]:
        return [self._spread]

    def passive_actions(self, dt: float, snapshot: "WorldSnapshot") -> list["Action"]:
        # 광합성: daylight에 비례해 회복(낮엔 빠르게, 한밤엔 정지). 판단 체인과 독립.
        return [Regrow(self, self.regrow_rate * snapshot.daylight * dt)]

    @property
    def status(self) -> EntityStatus:
        # status는 스냅샷으로 한 틱 보관되므로 매번 새 loc 복사본을 반환한다.
        return EntityStatus(loc=pygame.Vector2(self._loc), level=self.level)

    @status.setter
    def status(self, value: EntityStatus) -> None:
        self._loc = value.loc

    def sprite(self) -> pygame.Surface:
        # 에셋 식물 — biomass 비율로 크기·명도가 변한다(과방목된 풀은 작고 어둡다).
        frac = max(0.25, self.biomass / self.max_biomass)
        px = int(self.size * frac * 2.8)
        return sprites.sprite("plant", px, bright=0.5 + 0.5 * frac)

    @classmethod
    def gen(cls, world_size: tuple[int, int], rng: random.Random) -> "Plant":
        # 월드 안 임의 위치에 생성. rng를 넘겨 Spread가 결정적으로 작동하게 한다.
        loc = pygame.Vector2(
            rng.uniform(0, world_size[0]), rng.uniform(0, world_size[1])
        )
        return cls(loc, rng)
