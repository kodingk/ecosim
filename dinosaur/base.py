from typing import TYPE_CHECKING

import pygame

from entity import Entity, EntityStatus

if TYPE_CHECKING:
    from behavior import Behavior


class Dinosaur(Entity):
    """
    공룡 베이스. 가변 위치(loc)를 소유하고 status/sprite를 색·크기·level로 일반화한다.
    구체 종은 color/size/level/speed를 바꾸고 behaviors()를 구현한다.
    loc는 Move 등 Action이 갱신하는 가변 상태이며, status()는 스냅샷 안전을 위해
    매번 복사본을 반환한다.
    """

    color: tuple[int, int, int] = (200, 200, 200)
    size: int = 14
    level: int = 1  # 식물(0) 위에 그려진다
    max_energy: float = 100.0

    def __init__(self, loc: pygame.Vector2):
        self.loc = pygame.Vector2(loc)
        self.energy = (
            self.max_energy / 2
        )  # 절반에서 시작(처음엔 배고픔); 소진·사망은 5단계

    def behaviors(self) -> list["Behavior"]:
        return []

    def status(self) -> EntityStatus:
        return EntityStatus(loc=pygame.Vector2(self.loc), level=self.level)

    def sprite(self) -> pygame.Surface:
        surface = pygame.Surface((self.size, self.size))
        surface.fill(self.color)
        return surface
