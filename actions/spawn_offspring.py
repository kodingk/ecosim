from typing import TYPE_CHECKING

from action import Action

if TYPE_CHECKING:
    from dinosaur.base import Dinosaur
    from entity import Entity
    from world import World


class SpawnOffspring(Action):
    """자식 엔티티를 스폰하고 부모 에너지를 소모한다."""

    def __init__(self, parent: "Dinosaur", cost: float, offspring: "Entity"):
        self._parent = parent
        self._cost = cost
        self._offspring = offspring

    def apply(self, world: "World") -> None:
        self._parent.energy -= self._cost
        self._parent.last_breed_age = self._parent.age  # 번식 쿨다운 시작점 기록
        world.spawn(self._offspring)
