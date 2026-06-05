from typing import TYPE_CHECKING

from actions.sip import Sip
from behavior import Behavior

if TYPE_CHECKING:
    from action import Action
    from dinosaur.base import Dinosaur
    from entity import Entity
    from world import WorldSnapshot


class Drink(Behavior):
    """
    수분이 가득 차지 않았고 drink_distance 이내에 물이 있으면 한 모금 마신다(Sip).

    Graze(풀뜯기)의 물 버전이다 — 연못 곁에 머무는 동안 매 틱 호출돼 drink_rate(수분/초)로
    **율속**되어 채워진다. 수분이 최대면 None을 반환해 다음 우선순위(섭식 등)로 넘긴다.
    """

    def __init__(
        self,
        actor: "Dinosaur",
        water_class: type["Entity"] | tuple[type["Entity"], ...],
        drink_distance: float,
        drink_rate: float,
    ):
        self._actor = actor
        self._water_class = (
            water_class if isinstance(water_class, tuple) else (water_class,)
        )
        self._drink_distance = drink_distance
        self._drink_rate = drink_rate

    def plan(self, snapshot: "WorldSnapshot", dt: float) -> "Action | None":
        if self._actor.water >= self._actor.max_water:
            return None
        for entity in snapshot.query_entities_within(self._actor, self._drink_distance):
            if isinstance(entity, self._water_class):
                return Sip(self._actor, self._drink_rate * dt)
        return None
