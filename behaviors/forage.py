from typing import TYPE_CHECKING

from actions.move import Move
from behavior import Behavior

if TYPE_CHECKING:
    from action import Action
    from dinosaur.base import Dinosaur
    from entity import Entity
    from world import WorldSnapshot


class Forage(Behavior):
    """
    배고플 때(energy < hunger_threshold) seek_distance 이내에서 biomass가 남은 가장 가까운
    식물을 향해 이동한다.

    옛 Seek가 모든 개체를 같은 패치로 몰아 공동 고갈시킨 문제를 두 가지로 막는다:
    ① **배고픔 게이트** — 포만 개체는 탐색하지 않고 배회로 흩어진다(분산).
    ② **빈 패치 건너뛰기** — biomass가 0인 풀은 목표로 삼지 않고 다음으로 가까운 살아있는
       풀을 찾는다. 덕분에 무리가 고갈된 패치에 눌러앉지 않고 신선한 풀로 퍼진다.

    eat_distance 이내면 None을 반환해 앞 우선순위 Graze에 양보하고, 시야에 풀이 없으면
    None을 반환해 다음 우선순위(배회)로 넘긴다.
    """

    def __init__(
        self,
        actor: "Dinosaur",
        plant_class: type["Entity"] | tuple[type["Entity"], ...],
        seek_distance: float,
        eat_distance: float,
        speed: float,
        hunger_threshold: float,
        min_biomass: float = 0.0,
    ):
        self._actor = actor
        self._plant_class = (
            plant_class if isinstance(plant_class, tuple) else (plant_class,)
        )
        self._seek_distance = seek_distance
        self._eat_distance = eat_distance
        self._speed = speed
        self._hunger_threshold = hunger_threshold
        self._min_biomass = min_biomass  # 이보다 많이 남은 '푸른' 풀만 목표로 삼는다

    def plan(self, snapshot: "WorldSnapshot", dt: float) -> "Action | None":
        if self._actor.energy >= self._hunger_threshold:
            return None  # 배부르면 적극 탐색하지 않는다 → 흩어진다
        actor_loc = snapshot.statuses[self._actor].loc
        for entity in snapshot.query_entities_within(self._actor, self._seek_distance):
            if (
                isinstance(entity, self._plant_class)
                and getattr(entity, "biomass", 0.0) > self._min_biomass
            ):
                target_loc = snapshot.statuses[entity].loc
                if actor_loc.distance_to(target_loc) <= self._eat_distance:
                    return None  # 이미 사정거리 — Graze가 처리
                direction = target_loc - actor_loc
                if direction.length() > 0:
                    direction = direction.normalize()
                return Move(self._actor, direction * self._speed * dt)
        return None
