from typing import TYPE_CHECKING, cast

from actions.bite import Bite
from behavior import Behavior

if TYPE_CHECKING:
    from action import Action
    from dinosaur.base import Dinosaur
    from entity import Entity
    from plant.base import Plant
    from world import WorldSnapshot


class Graze(Behavior):
    """
    배고플 때 eat_distance 이내에서 biomass가 남은 가장 가까운 식물을 한 입 뜯는다.

    Eat(통째로 Consume→despawn)과 달리, 식물을 죽이지 않고 graze_rate*dt 만큼의 biomass만
    에너지로 옮긴다(Bite). 매 틱 호출되므로 식물 위에 머무는 동안 연속적으로 풀을 뜯는 셈이고,
    소비가 graze_rate(에너지/초)로 **율속**되어 한 틱에 패치를 통째로 증발시키지 못한다 —
    이 율속이 과소비를 막는 또 하나의 음성 피드백이다.

    포만(에너지 최대)이면 None을 반환해 다음 우선순위로 넘어간다 → 배부른 개체는 풀밭을
    떠나고, 그 사이 식물이 회복한다.
    """

    def __init__(
        self,
        actor: "Dinosaur",
        plant_class: type["Entity"] | tuple[type["Entity"], ...],
        eat_distance: float,
        graze_rate: float,
        min_biomass: float = 0.0,
    ):
        self._actor = actor
        self._plant_class = (
            plant_class if isinstance(plant_class, tuple) else (plant_class,)
        )
        self._eat_distance = eat_distance
        self._graze_rate = graze_rate
        self._min_biomass = (
            min_biomass  # 이보다 적게 남은 풀은 버린다(giving-up density)
        )

    def plan(self, snapshot: "WorldSnapshot", dt: float) -> "Action | None":
        if self._actor.energy >= self._actor.max_energy:
            return None
        for entity in snapshot.query_entities_within(self._actor, self._eat_distance):
            if (
                isinstance(entity, self._plant_class)
                and getattr(entity, "biomass", 0.0) > self._min_biomass
            ):
                return Bite(self._actor, cast("Plant", entity), self._graze_rate * dt)
        return None
