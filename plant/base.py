import random
from typing import TYPE_CHECKING

import pygame

from entity import Entity, EntityStatus

if TYPE_CHECKING:
    from behavior import Behavior


class Plant(Entity):
    """
    생산자(식물) 베이스. 행동하지 않고 자리에 존재하며, 렌더 최하층(level=0)으로
    그려져 다른 개체들 아래에 깔린다. 구체 식물(양치·침엽수 등)은 색·크기·level만
    바꿔 상속한다.
    """

    color: tuple[int, int, int] = (50, 150, 60)
    size: int = 10
    level: int = 0

    def __init__(self, loc: pygame.Vector2):
        self._loc = pygame.Vector2(loc)

    def behaviors(self) -> list["Behavior"]:
        return []

    def status(self) -> EntityStatus:
        # status는 스냅샷으로 한 틱 보관되므로 매번 새 loc 복사본을 반환한다.
        return EntityStatus(loc=pygame.Vector2(self._loc), level=self.level)

    def sprite(self) -> pygame.Surface:
        surface = pygame.Surface((self.size, self.size))
        surface.fill(self.color)
        return surface

    @classmethod
    def gen(cls, world_size: tuple[int, int], rng: random.Random) -> "Plant":
        loc = pygame.Vector2(
            rng.uniform(0, world_size[0]), rng.uniform(0, world_size[1])
        )
        return cls(loc)
