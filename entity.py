import abc
from dataclasses import dataclass

import pygame

from behavior import Behavior


@dataclass(frozen=True)
class EntityStatus:
    loc: pygame.Vector2
    """엔티티의 중심의 위치"""

    level: int
    """엔티티의 그리기 레이어. 값이 클수록 다른 엔티티 위에 그려진다 (예: 익룡)."""


class Entity(abc.ABC):
    def __hash__(self) -> int:
        return hash(id(self))

    @abc.abstractmethod
    def behaviors(self) -> list[Behavior]:
        """
        해당 엔티티의 행동 패턴들을 우선 순위 내림차순으로 반환하는 함수.
        """

    @abc.abstractmethod
    def status(self) -> EntityStatus:
        """
        해당 엔티티의 상태를 반환하는 함수.

        update의 판단 단계에서 틱-시작 스냅샷으로 보관되므로, 호출자가 한 틱 동안
        들고 있어도 안전하도록 매번 새 값(loc 복사본 등)을 반환해야 한다.
        """

    @abc.abstractmethod
    def sprite(self) -> pygame.Surface:
        """
        해당 엔티티의 스프라이트를 반환하는 함수.
        """
