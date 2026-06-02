from typing import TYPE_CHECKING

from actions.consume import Consume
from behavior import Behavior

if TYPE_CHECKING:
    from action import Action
    from dinosaur.base import Dinosaur
    from entity import Entity
    from world import WorldSnapshot


class Eat(Behavior):
    """
    eat_distance 이내에서 target_classes에 해당하는 가장 가까운 엔티티를 먹는다.

    먹이 '종류'를 클래스로 주입받으므로(예: [Plant]) behavior가 concrete 종에 묶이지
    않는다 — 클래스 계층이 곧 분류 체계이고 isinstance가 하위 클래스까지 잡는다.
    포만(에너지 최대)이면 None을 반환해 다음 우선순위(배회)로 넘어간다.
    """

    def __init__(
        self,
        actor: "Dinosaur",
        target_classes: list[type["Entity"]],
        eat_distance: float,
        gain: float,
    ):
        self._actor = actor
        self._target_classes = tuple(target_classes)
        self._eat_distance = eat_distance
        self._gain = gain

    def plan(self, snapshot: "WorldSnapshot", dt: float) -> "Action | None":
        if self._actor.energy >= self._actor.max_energy:
            return None
        for entity in snapshot.query_entities_within(self._actor, self._eat_distance):
            if isinstance(entity, self._target_classes):
                return Consume(self._actor, entity, self._gain)
        return None
