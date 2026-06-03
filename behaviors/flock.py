from typing import TYPE_CHECKING

import pygame

from actions.move import Move
from behavior import Behavior

if TYPE_CHECKING:
    from action import Action
    from entity import Entity
    from world import WorldSnapshot


class Flock(Behavior):
    """
    같은 종 이웃에 boids 3규칙을 적용해 무리/팩 이동을 만든다(Reynolds).

    - 분리(separation): 너무 가까운 이웃 반대 방향으로 → 겹침 방지
    - 응집(cohesion):  이웃 무게중심 쪽으로 → 무리 유지
    - 정렬(alignment): 이웃 평균 속도 방향으로 → 함께 흐름(EntityStatus.velocity 사용)

    snapshot만 읽고 Move만 반환하므로 2단계·순서독립을 지킨다. 반경 내 동족이 없으면 None을
    반환해 다음 우선순위(Wander)로 넘긴다 — 무리가 있을 때만 무리답게 움직이고 혼자면 배회한다.
    psitta(무리)·dein(팩) 모두 파라미터만 바꿔 공유한다(DRY).
    """

    def __init__(
        self,
        actor: "Entity",
        radius: float,
        separation_dist: float,
        speed: float,
        w_separation: float = 1.5,
        w_cohesion: float = 1.0,
        w_alignment: float = 0.8,
    ):
        self._actor = actor
        self._radius = radius  # 이 반경 내 동족을 이웃으로 인식
        self._separation_dist = separation_dist  # 이보다 가까우면 밀어낸다
        self._speed = speed
        self._w_sep = w_separation
        self._w_coh = w_cohesion
        self._w_align = w_alignment

    def plan(self, snapshot: "WorldSnapshot", dt: float) -> "Action | None":
        actor_loc = snapshot.statuses[self._actor].loc
        kin_type = type(self._actor)
        neighbors = [
            e
            for e in snapshot.query_entities_within(self._actor, self._radius)
            if type(e) is kin_type
        ]
        if not neighbors:
            return None

        center = pygame.Vector2(0, 0)
        align = pygame.Vector2(0, 0)
        sep = pygame.Vector2(0, 0)
        for e in neighbors:
            st = snapshot.statuses[e]
            center += st.loc
            align += st.velocity
            offset = actor_loc - st.loc
            d = offset.length()
            if 0 < d < self._separation_dist:
                sep += offset / (d * d)  # 가까울수록(1/d²) 강하게 밀어낸다

        cohesion = center / len(neighbors) - actor_loc

        steer = pygame.Vector2(0, 0)
        if cohesion.length() > 0:
            steer += self._w_coh * cohesion.normalize()
        if sep.length() > 0:
            steer += self._w_sep * sep.normalize()
        if align.length() > 0:
            steer += self._w_align * align.normalize()
        if steer.length() == 0:
            return None
        return Move(self._actor, steer.normalize() * self._speed * dt)
