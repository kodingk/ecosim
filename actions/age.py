from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import random

    from dinosaur.base import Dinosaur
    from world import World

from action import Action


class Age(Action):
    """
    동물을 dt만큼 나이 들게 하고, 노쇠기(senescence_age 이상)에 들면 확률적으로 죽인다.

    노화사를 **확률적**으로 둔 이유: 고정 수명이면 같은 시각에 태어난 코호트가 한꺼번에
    죽어 개체수가 톱니처럼 출렁인다. 매 틱 작은 사망 확률(mortality_rate*dt)로 흩뿌리면
    사망이 시간축에 퍼져 진동이 매끄러워진다 — 먹이와 무관한 기저 사망률이라 개체수의
    자연 상한도 만든다. rng는 엔티티 전용 스트림이라 처리 순서와 무관하게 결정적이다.
    """

    def __init__(
        self,
        animal: "Dinosaur",
        dt: float,
        senescence_age: float,
        mortality_rate: float,
        rng: "random.Random",
    ):
        self._animal = animal
        self._dt = dt
        self._senescence_age = senescence_age
        self._mortality_rate = mortality_rate
        self._rng = rng

    def apply(self, world: "World") -> None:
        self._animal.age += self._dt
        if self._animal.age >= self._senescence_age:
            if self._rng.random() < self._mortality_rate * self._dt:
                world.despawn(self._animal)
