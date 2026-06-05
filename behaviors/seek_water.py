from typing import TYPE_CHECKING

from actions.move import Move
from behavior import Behavior

if TYPE_CHECKING:
    from action import Action
    from dinosaur.base import Dinosaur
    from entity import Entity
    from world import WorldSnapshot


class SeekWater(Behavior):
    """
    목마를 때(water < thirst_threshold) sight 이내에서 가장 가까운 물을 향해 이동한다.

    Forage(먹이탐색)의 물 버전이다 — 임계 미만일 때만 켜지는 '목마름 게이트'라, 평소엔 None을
    반환해 섭식·사냥·번식에 양보한다. drink_distance 이내면 None을 반환해 Drink에 넘기고,
    시야에 물이 없으면 None을 반환해 다음 우선순위(배회)로 넘긴다.
    """

    def __init__(
        self,
        actor: "Dinosaur",
        water_class: type["Entity"] | tuple[type["Entity"], ...],
        sight: float,
        drink_distance: float,
        speed: float,
        thirst_threshold: float,
    ):
        self._actor = actor
        self._water_class = (
            water_class if isinstance(water_class, tuple) else (water_class,)
        )
        self._sight = sight
        self._drink_distance = drink_distance
        self._speed = speed
        self._thirst_threshold = thirst_threshold

    def plan(self, snapshot: "WorldSnapshot", dt: float) -> "Action | None":
        if self._actor.water >= self._thirst_threshold:
            return None  # 충분히 수분 — 적극 탐색하지 않는다
        actor_loc = snapshot.statuses[self._actor].loc
        for entity in snapshot.query_entities_within(self._actor, self._sight):
            if isinstance(entity, self._water_class):
                target_loc = snapshot.statuses[entity].loc
                if actor_loc.distance_to(target_loc) <= self._drink_distance:
                    return None  # 이미 사정거리 — Drink가 처리
                direction = target_loc - actor_loc
                if direction.length() > 0:
                    direction = direction.normalize()
                return Move(self._actor, direction * self._speed * dt)
        return None
