import math
import random
from typing import TYPE_CHECKING

import pygame

from actions.spawn import Spawn
from behavior import Behavior

if TYPE_CHECKING:
    from action import Action
    from world import WorldSnapshot


class Spread(Behavior):
    """
    확률적으로 반경 내에 새 식물을 스폰한다.

    max_plants 초과이면 씨앗을 퍼뜨리지 않는다 — 스냅샷 기준으로 확인하므로 같은 틱에
    여러 식물이 동시에 결정하면 최대치를 소폭 초과할 수 있으나, 다음 틱에 수렴한다.
    식물 종류는 plant_class로 주입받아 behavior가 구체 종에 묶이지 않는다.
    """

    def __init__(
        self,
        plant,
        rng: random.Random,
        rate: float,
        radius: float,
        max_plants: int,
        plant_class: type,
        factory,  # Callable[[pygame.Vector2], Entity]
        world_size: tuple[int, int] | None = None,
        min_biomass: float = 0.0,
    ):
        self._plant = plant
        self._rng = rng
        self._rate = rate  # 스폰/초
        self._radius = radius
        self._max_plants = max_plants
        self._plant_class = plant_class
        self._factory = factory
        self._world_size = world_size  # 설정 시 전역 랜덤 위치로 스폰
        self._min_biomass = min_biomass  # 이 이상 건강할 때만 번식(밀도 의존)

    def plan(self, snapshot: "WorldSnapshot", dt: float) -> "Action | None":
        # 뜯겨서 약해진 식물은 번식하지 않는다 — 과방목된 초지는 확산을 멈춘다(음성 피드백).
        if getattr(self._plant, "biomass", float("inf")) < self._min_biomass:
            return None
        if snapshot.count(self._plant_class) >= self._max_plants:
            return None
        if self._rng.random() >= self._rate * dt:
            return None
        if self._world_size:
            # 전역 랜덤: 월드 어디에나 균일 분포 → 국지 식물 고갈 방지
            w, h = self._world_size
            new_loc = pygame.Vector2(self._rng.uniform(0, w), self._rng.uniform(0, h))
        else:
            loc = snapshot.statuses[self._plant].loc
            angle = self._rng.uniform(0, 2 * math.pi)
            dist = self._rng.uniform(0, self._radius)
            new_loc = loc + pygame.Vector2(
                math.cos(angle) * dist, math.sin(angle) * dist
            )
        return Spawn(self._factory(new_loc))
