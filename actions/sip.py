from typing import TYPE_CHECKING

from action import Action

if TYPE_CHECKING:
    from dinosaur.base import Dinosaur
    from world import World


class Sip(Action):
    """
    물을 마셔 actor의 수분(water)을 amount만큼 회복시킨다(상한 max_water).

    연못은 무한 샘이라 **고갈시키지 않는다** — Bite가 식물 biomass를 깎는 것과 대비된다.
    여러 동물이 같은 연못을 같은 틱에 마실 수 있고 서로 독점하지 않으므로 claim도 없다.
    """

    def __init__(self, actor: "Dinosaur", amount: float):
        self._actor = actor
        self._amount = amount

    def apply(self, world: "World") -> None:
        self._actor.water = min(self._actor.max_water, self._actor.water + self._amount)
