import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entity import Entity
    from world import World, WorldSnapshot


class Action(abc.ABC):
    "엔티티가 수행하기로 결정한 행동. 적용 단계에서 월드/엔티티 상태를 변경한다."

    def claim(self) -> "Entity | None":
        """
        이 액션이 독점하려는 대상(없으면 None). 같은 대상을 노린 액션이 여럿이면
        apply 직전 충돌 해결로 단 하나만 살아남는다 (World._resolve).
        """
        return None

    def contest_key(self, snapshot: "WorldSnapshot") -> float:
        """
        충돌 시 승자 선택 키 — 값이 **작을수록** 우선한다. 기본은 동률(0.0).
        (Consume은 '가까운 포식자 우선'을 위해 포식자↔먹이 거리를 반환한다.)
        """
        return 0.0

    @abc.abstractmethod
    def apply(self, world: "World") -> None:
        """
        판단 단계에서 결정된 행동을 실제 월드에 반영하는 함수.
        (World.update의 적용 단계에서 호출된다.)
        """
