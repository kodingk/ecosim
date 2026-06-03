from typing import TYPE_CHECKING

from action import Action

if TYPE_CHECKING:
    from dinosaur.base import Dinosaur
    from world import World


class DrainEnergy(Action):
    """매 틱 에너지를 소모한다. 소진되면 엔티티를 월드에서 제거한다."""

    def __init__(self, actor: "Dinosaur", amount: float):
        self._actor = actor
        self._amount = amount

    def apply(self, world: "World") -> None:
        self._actor.energy = max(0.0, self._actor.energy - self._amount)
        if self._actor.energy <= 0.0:
            world.despawn(self._actor)
