from typing import TYPE_CHECKING

import pygame

from actions.move import Move
from behavior import Behavior

if TYPE_CHECKING:
    from action import Action
    from entity import Entity
    from world import WorldSnapshot


class Flee(Behavior):
    """
    flee_radius 이내에 포식자(predator_classes)가 있으면 가장 가까운 포식자의 **반대 방향**으로
    도주한다. 보통 최우선 순위에 둔다 — 잡아먹히지 않는 것이 먹는 것보다 우선이다.

    포식자(dein)가 더 빨라 개체가 직선으로 못 도망치더라도, 무리가 포식자에게서 멀어지는
    방향으로 흐르면 포식자가 한곳에 머물며 사냥할 수 없게 된다('공포의 지형'). 즉 개체 생존이
    아니라 **개체군 차원의 포식 효율 저하**로 작동해 과포식→먹이 붕괴를 막는 안정자다.

    포식자가 없으면 None을 반환해 다음 우선순위(채식·번식·배회)로 넘긴다.
    """

    def __init__(
        self,
        actor: "Entity",
        predator_classes: type["Entity"] | tuple[type["Entity"], ...],
        flee_radius: float,
        speed: float,
        vigilance_radius: float = 0.0,
        vigilance_bonus: float = 0.0,
        vigilance_cap: int = 0,
    ):
        self._actor = actor
        self._predator_classes = (
            predator_classes
            if isinstance(predator_classes, tuple)
            else (predator_classes,)
        )
        self._flee_radius = flee_radius
        self._speed = speed
        # 집단 경계(many-eyes): vigilance_radius 내 동족 1마리당 감지 반경 +vigilance_bonus,
        # 최대 vigilance_cap마리까지. 무리가 클수록 포식자를 일찍 감지해 도주 → 무리가 보호가 된다.
        self._vigilance_radius = vigilance_radius
        self._vigilance_bonus = vigilance_bonus
        self._vigilance_cap = vigilance_cap

    def plan(self, snapshot: "WorldSnapshot", dt: float) -> "Action | None":
        actor_loc = snapshot.statuses[self._actor].loc
        radius = self._flee_radius
        if self._vigilance_bonus > 0:
            kin = sum(
                1
                for e in snapshot.query_entities_within(
                    self._actor, self._vigilance_radius
                )
                if type(e) is type(self._actor)
            )
            radius += self._vigilance_bonus * min(kin, self._vigilance_cap)
        # query는 가까운 순 — 첫 포식자가 가장 가깝다.
        for entity in snapshot.query_entities_within(self._actor, radius):
            if isinstance(entity, self._predator_classes):
                pred_loc = snapshot.statuses[entity].loc
                away = actor_loc - pred_loc
                if away.length() > 0:
                    away = away.normalize()
                else:
                    away = pygame.Vector2(1, 0)  # 정확히 겹친 드문 경우
                return Move(self._actor, away * self._speed * dt)
        return None
