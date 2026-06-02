from typing import TYPE_CHECKING

from action import Action

if TYPE_CHECKING:
    from dinosaur.base import Dinosaur
    from entity import Entity
    from world import World, WorldSnapshot


class Consume(Action):
    """
    target을 먹어 치운다 — 월드에서 제거하고 actor의 에너지를 올린다.

    같은 틱에 다른 개체가 먼저 먹었으면(이미 제거됨) 아무 일도 하지 않는다. 이 '먼저
    적용된 쪽이 먹는다'는 apply 순서에 의존하므로, 포식자 2 ↔ 먹이 1 충돌의 명시적·공정
    해결은 4단계의 충돌 해결 훅에서 다룬다.
    """

    def __init__(self, actor: "Dinosaur", target: "Entity", gain: float):
        self._actor = actor
        self._target = target
        self._gain = gain

    def claim(self) -> "Entity":
        return self._target

    def contest_key(self, snapshot: "WorldSnapshot") -> float:
        # '가까운 포식자 우선': 틱-시작 기준 포식자와 먹이 사이 거리가 작을수록 이긴다.
        actor_loc = snapshot.statuses[self._actor].loc
        target_loc = snapshot.statuses[self._target].loc
        return actor_loc.distance_to(target_loc)

    def apply(self, world: "World") -> None:
        if self._target not in world.entities:
            return  # 이미 다른 개체가 먹음
        world.despawn(self._target)
        self._actor.energy = min(
            self._actor.max_energy, self._actor.energy + self._gain
        )
