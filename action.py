import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world import World


class Action(abc.ABC):
    "엔티티가 수행하기로 결정한 행동. 적용 단계에서 월드/엔티티 상태를 변경한다."

    @abc.abstractmethod
    def apply(self, world: "World") -> None:
        """
        판단 단계에서 결정된 행동을 실제 월드에 반영하는 함수.
        (World.update의 적용 단계에서 호출된다.)
        """
