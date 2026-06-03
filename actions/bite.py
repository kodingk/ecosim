from typing import TYPE_CHECKING

from action import Action

if TYPE_CHECKING:
    from dinosaur.base import Dinosaur
    from plant.base import Plant
    from world import World


class Bite(Action):
    """
    식물의 biomass를 bite만큼 깎아 actor의 에너지로 옮긴다.

    식물은 죽지 않는다 — biomass는 0까지만 줄고(초지 영속), 매 틱 Regrow로 회복하므로
    먹이가 절대 0으로 붕괴하지 않는다. 이것이 개체수 폭락(zero-floor)을 막는 핵심이다.

    풀은 **공유 자원**이라 claim하지 않는다 — 여러 초식자가 같은 포기를 같은 틱에 뜯을 수
    있고, apply가 순차로 돌며 각자 '현재 남은 잔량' 한도 내에서만 가져가므로(min) biomass가
    음수로 가지 않는다. 독점 대상인 포식(Consume)과 의도적으로 대비되는 설계다.
    """

    def __init__(self, actor: "Dinosaur", plant: "Plant", bite: float):
        self._actor = actor
        self._plant = plant
        self._bite = bite

    def apply(self, world: "World") -> None:
        taken = min(self._bite, self._plant.biomass)
        if taken <= 0.0:
            return
        self._plant.biomass -= taken
        self._actor.energy = min(self._actor.max_energy, self._actor.energy + taken)
