from typing import TYPE_CHECKING

from action import Action

if TYPE_CHECKING:
    from plant.base import Plant
    from world import World


class Regrow(Action):
    """식물의 biomass를 amount만큼 회복시킨다(상한 max_biomass). 식물의 passive로 매 틱 수집된다."""

    def __init__(self, plant: "Plant", amount: float):
        self._plant = plant
        self._amount = amount

    def apply(self, world: "World") -> None:
        self._plant.biomass = min(
            self._plant.max_biomass, self._plant.biomass + self._amount
        )
