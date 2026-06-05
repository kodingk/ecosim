import abc
import dataclasses
import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import pygame

from behavior import Behavior

if TYPE_CHECKING:
    from action import Action
    from world import WorldSnapshot


@dataclass(frozen=True)
class EntityStatus:
    loc: pygame.Vector2
    """엔티티의 중심의 위치"""

    level: int
    """엔티티의 그리기 레이어. 값이 클수록 다른 엔티티 위에 그려진다 (예: 익룡)."""

    velocity: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(0, 0))
    """직전 틱의 이동 변위(방향+크기). boids 정렬·요격 등에 쓰인다. 정지·식물은 0."""

    def replace(self, **kwargs: Any) -> "EntityStatus":
        return dataclasses.replace(self, **kwargs)


class Entity(abc.ABC):
    def __hash__(self) -> int:
        return hash(id(self))

    @abc.abstractmethod
    def behaviors(self) -> list[Behavior]:
        """
        해당 엔티티의 행동 패턴들을 우선 순위 내림차순으로 반환하는 함수.
        """

    @property
    @abc.abstractmethod
    def status(self) -> EntityStatus:
        """
        해당 엔티티의 상태를 반환하는 함수.

        update의 판단 단계에서 틱-시작 스냅샷으로 보관되므로, 호출자가 한 틱 동안
        들고 있어도 안전하도록 매번 새 값(loc 복사본 등)을 반환해야 한다.
        """

    @status.setter
    @abc.abstractmethod
    def status(self, value: EntityStatus) -> None:
        """
        해당 엔티티의 상태를 설정하는 함수.
        EntityStatus를 받아 엔티티의 내부 상태를 갱신한다.
        """

    @abc.abstractmethod
    def sprite(self) -> pygame.Surface:
        """
        해당 엔티티의 스프라이트를 반환하는 함수.
        """

    @classmethod
    @abc.abstractmethod
    def gen(cls, world_size: tuple[int, int], rng: random.Random) -> "Entity":
        """
        주어진 월드 크기 안에서 랜덤하게 초기화된 엔티티 인스턴스를 반환하는 함수.
        초기 조건 설정(Simulator 스폰)에 사용된다.
        """

    def passive_actions(self, dt: float, snapshot: "WorldSnapshot") -> list["Action"]:
        """매 틱 항상 수집되는 수동 행동들 (에너지 소모·노화 등). snapshot으로 낮밤 등
        틱-전역 상태를 읽을 수 있다. 기본값은 빈 리스트."""
        return []

    # ================================================================================
    # Derived
    # ================================================================================

    def set_location(self, loc: pygame.Vector2) -> "Entity":
        """
        해당 엔티티의 위치를 설정하는 함수.
        pygame.Vector2를 받아 엔티티의 위치를 갱신한다.

        이동 변위(loc - 직전 loc)를 velocity로 기록해 status가 보고하게 한다 — boids
        정렬에 쓰인다. 안 움직이는 엔티티(식물)는 이 함수가 불리지 않아 velocity가 0이다.
        """
        self.velocity = loc - self.status.loc
        self.status = self.status.replace(loc=loc)
        return self
