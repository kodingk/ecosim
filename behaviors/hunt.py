from typing import TYPE_CHECKING

from actions.consume import Consume
from actions.move import Move
from behavior import Behavior

if TYPE_CHECKING:
    from action import Action
    from dinosaur.base import Dinosaur
    from entity import Entity
    from world import WorldSnapshot


class Hunt(Behavior):
    """
    sight 이내에서 target_classes에 해당하는 가장 가까운 먹이를 쫓는다.

    attack_distance 안에 들면 잡아먹고(`Consume`), 아니면 먹이 쪽으로 이동(`Move`)한다 —
    즉 추격(seek) + 사냥(kill)을 한 behavior로 합쳤고, 둘 다 기존 Action을 재사용한다.
    먹이 '종류'는 클래스로 주입(예: [Psittacosaurus])하므로 동족은 쫓지 않는다.
    포만이면 None을 반환해 다음 우선순위(배회)로 넘어간다.
    """

    def __init__(
        self,
        actor: "Dinosaur",
        target_classes: list[type["Entity"]],
        sight: float,
        attack_distance: float,
        speed: float,
        gain: float,
    ):
        self._actor = actor
        self._target_classes = tuple(target_classes)
        self._sight = sight
        self._attack_distance = attack_distance
        self._speed = speed
        self._gain = gain

    def plan(self, snapshot: "WorldSnapshot", dt: float) -> "Action | None":
        if self._actor.energy >= self._actor.max_energy:
            return None
        prey = next(
            (
                entity
                for entity in snapshot.query_entities_within(self._actor, self._sight)
                if isinstance(entity, self._target_classes)
            ),
            None,
        )
        if prey is None:
            return None
        actor_loc = snapshot.statuses[self._actor].loc
        prey_loc = snapshot.statuses[prey].loc
        if actor_loc.distance_to(prey_loc) <= self._attack_distance:
            return Consume(self._actor, prey, self._gain)
        direction = prey_loc - actor_loc
        if direction.length() > 0:
            direction = direction.normalize()
        return Move(self._actor, direction * self._speed * dt)
