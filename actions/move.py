from typing import TYPE_CHECKING

import pygame

from action import Action

if TYPE_CHECKING:
    from entity import Entity
    from world import World


class Move(Action):
    """엔티티를 displacement만큼 이동시킨다. 적용 시 월드 경계로 클램프한다."""

    def __init__(self, entity: "Entity", displacement: pygame.Vector2):
        self.entity = entity
        self.displacement = pygame.Vector2(displacement)

    def apply(self, world: "World") -> None:
        width, height = world.size
        status = self.entity.status()
        loc = status.loc + self.displacement
        loc.x = max(0.0, min(loc.x, float(width)))
        loc.y = max(0.0, min(loc.y, float(height)))
        self.entity.loc = loc
