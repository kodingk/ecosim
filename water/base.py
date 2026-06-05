import random
from typing import TYPE_CHECKING

import pygame

import sprites
from entity import Entity, EntityStatus

if TYPE_CHECKING:
    from behavior import Behavior


class Water(Entity):
    """
    식수원(연못). 동물이 찾아와 마시는 **고정 자원**이다 — 이동하지 않고 판단 행동도 없다.

    먹이(Plant)와 대칭이되 한 가지가 다르다: 연못은 마셔도 **고갈되지 않는다**(무한 샘).
    이 '완만한' 설정이 탈수를 대량 사망 요인이 아니라 '물 찾기 행동'의 유발자로 만들어,
    어렵게 맞춘 4종 공존을 흔들지 않는다. (유한·고갈하는 물웅덩이는 '치명적' 업그레이드 경로.)

    렌더 최하층(level=-1)으로 풀(0)·동물 아래에 깔려 땅의 일부처럼 보인다.
    """

    color: tuple[int, int, int] = (70, 130, 165)  # HUD 범례용 물색
    size: int = 42  # 연못 반경 스케일(스프라이트 크기)
    level: int = -1  # 식물(0) 아래 — 땅처럼 깔린다
    sprite_name: str = "water"  # assets/sprites/water.png

    def __init__(
        self,
        loc: pygame.Vector2,
        rng: random.Random | None = None,
        world_size: tuple[int, int] | None = None,
    ):
        # rng·world_size는 gen/factory 시그니처 호환용(정적 자원이라 실사용 없음).
        self._loc = pygame.Vector2(loc)

    def behaviors(self) -> list["Behavior"]:
        return []  # 정적 자원 — 판단 행동 없음

    @property
    def status(self) -> EntityStatus:
        # 매 틱 새 loc 복사본(스냅샷 오염 방지). 안 움직이므로 velocity는 0(기본값).
        return EntityStatus(loc=pygame.Vector2(self._loc), level=self.level)

    @status.setter
    def status(self, value: EntityStatus) -> None:
        self._loc = value.loc

    def sprite(self) -> pygame.Surface:
        return sprites.sprite(self.sprite_name, int(self.size * 2.1))

    @classmethod
    def gen(cls, world_size: tuple[int, int], rng: random.Random) -> "Water":
        loc = pygame.Vector2(
            rng.uniform(0, world_size[0]), rng.uniform(0, world_size[1])
        )
        return cls(loc, rng, world_size)
