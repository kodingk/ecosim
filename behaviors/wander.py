import random
from typing import TYPE_CHECKING

import pygame

from actions.move import Move
from behavior import Behavior

if TYPE_CHECKING:
    from action import Action
    from entity import Entity
    from world import WorldSnapshot


class Wander(Behavior):
    """
    무작위로 배회한다. 진행 방향(heading)을 들고 매 틱 약간 선회해 부드럽게 움직인다.

    결정성·순서 독립을 위해 **엔티티 전용 시드 RNG**를 쓴다 — 공유 RNG를 판단 단계에서
    뽑으면 난수가 엔티티 처리 순서에 좌우돼 순서 독립이 깨진다. heading은 behavior의
    사유 상태(월드 아님)라 갱신해도 2단계 판단 규약을 어기지 않는다.
    """

    def __init__(self, entity: "Entity", rng: random.Random, speed: float):
        self.entity = entity
        self.rng = rng
        self.speed = speed
        self._heading = pygame.Vector2(1, 0).rotate(rng.uniform(0, 360))

    def plan(self, snapshot: "WorldSnapshot", dt: float) -> "Action | None":
        self._heading = self._heading.rotate(self.rng.uniform(-30, 30))
        return Move(self.entity, self._heading * self.speed * dt)
