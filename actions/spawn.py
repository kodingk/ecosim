from typing import TYPE_CHECKING

from action import Action

if TYPE_CHECKING:
    from entity import Entity
    from world import World


class Spawn(Action):
    """엔티티를 월드에 추가한다."""

    def __init__(self, entity: "Entity"):
        self._entity = entity

    def apply(self, world: "World") -> None:
        world.spawn(self._entity)
