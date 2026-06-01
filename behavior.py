import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from action import Action
    from world import WorldSnapshot


class Behavior(abc.ABC):
    "특정 엔티티의 행동 패턴을 나타내는 타입."

    @abc.abstractmethod
    def plan(self, snapshot: "WorldSnapshot", dt: float) -> "Action | None":
        """
        틱-시작 스냅샷을 보고 수행할 행동(Action)을 계산해 반환하는 함수.

        이 단계(판단)에서는 월드를 변경하지 않으므로 엔티티 처리 순서와 무관하다.
        수행할 행동이 없으면 None을 반환하고, 그러면 다음 우선순위 행동을 시도한다.
        """
