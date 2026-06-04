import math
import random
from typing import TYPE_CHECKING

import pygame

from actions.spawn_offspring import SpawnOffspring
from behavior import Behavior

if TYPE_CHECKING:
    from action import Action
    from dinosaur.base import Dinosaur
    from world import WorldSnapshot


class Reproduce(Behavior):
    """
    성체이고 에너지가 임계값 이상일 때 인근에 자식을 스폰한다(에너지 cost 소모).

    factory(loc) → Entity로 자식 종류를 주입받으므로 behavior가 구체 종에 묶이지 않는다.

    개체수 제어는 인위적 캡이 아니라 **에너지 경제**에서 창발한다: 번식은 cost를 소모하고
    그 에너지는 먹이(grazing/hunting)에서 오므로, 개체가 늘어 먹이 1인당 몫이 줄면 임계값에
    도달하는 개체가 줄어 번식이 저절로 둔화된다(밀도 의존). 여기에 maturity_age(성숙 지연)가
    출생→번식자 전환을 늦춰 과폭발을 감쇠한다.

    min_food_ratio / max_own_count는 과거 호환용 안전장치로 남겨두되 기본은 비활성(0)이다.
    """

    def __init__(
        self,
        actor: "Dinosaur",
        threshold: float,
        cost: float,
        radius: float,
        rng: random.Random,
        factory,  # Callable[[pygame.Vector2], Entity]
        maturity_age: float = 0.0,
        cooldown: float = 0.0,
        crowd_radius: float = 0.0,
        food_class: type | None = None,
        min_food_ratio: float = 0.0,
        max_own_count: int = 0,
    ):
        self._actor = actor
        self._threshold = threshold
        self._cost = cost
        self._radius = radius
        self._rng = rng
        self._factory = factory
        self._maturity_age = maturity_age
        self._cooldown = cooldown
        self._crowd_radius = crowd_radius
        self._food_class = food_class
        self._min_food_ratio = min_food_ratio
        self._max_own_count = max_own_count

    def plan(self, snapshot: "WorldSnapshot", dt: float) -> "Action | None":
        if self._actor.energy < self._threshold:
            return None
        # 미성숙 개체는 번식하지 않는다 — 출생 폭증이 즉시 번식자 폭증이 되지 않게 지연시켜
        # 개체수 overshoot를 감쇠한다(생활사 지연).
        if self._actor.age < self._maturity_age:
            return None
        # 번식 쿨다운(임신·육아 휴지기): 마지막 번식 후 cooldown초 안에는 다시 낳지 않는다.
        # 식량·공간과 무관하게 개체당 출생률을 1/cooldown으로 하드캡 → 포식자 개체수 폭증
        # (boom)을 구조적으로 막는 가장 강한 브레이크. age는 매 틱 갱신돼 순서 독립적이다.
        if self._actor.age - self._actor.last_breed_age < self._cooldown:
            return None
        # 영역성(territoriality): crowd_radius 내에 동족이 있으면 번식하지 않는다 — 포식자
        # 밀도를 구조적으로 제한해 개체수 폭증을 막는다. 자식은 부모 곁(reproduce_radius)에
        # 태어나 곧장 서로의 영역에 들므로, 흩어져 영역을 확보하기 전엔 추가 번식이 억제된다.
        if self._crowd_radius > 0:
            for e in snapshot.query_entities_within(self._actor, self._crowd_radius):
                if type(e) is type(self._actor):
                    return None
        # 개체수 상한 — 이미 max_own_count마리 이상이면 번식하지 않는다.
        # 비율 기반 체크보다 확실하게 과폭발(overshoot)을 막는다.
        if self._max_own_count > 0:
            if snapshot.count_exact(type(self._actor)) >= self._max_own_count:
                return None
        # 밀도 의존 번식 억제: food/pop 비율이 min_food_ratio 미만이면 번식하지 않는다.
        if self._food_class and self._min_food_ratio > 0:
            food = snapshot.count(self._food_class)
            pop = max(1, snapshot.count_exact(type(self._actor)))
            if food / pop < self._min_food_ratio:
                return None
        loc = snapshot.statuses[self._actor].loc
        angle = self._rng.uniform(0, 2 * math.pi)
        dist = self._rng.uniform(5.0, self._radius)
        spawn_loc = loc + pygame.Vector2(math.cos(angle) * dist, math.sin(angle) * dist)
        offspring = self._factory(spawn_loc)
        return SpawnOffspring(self._actor, self._cost, offspring)
