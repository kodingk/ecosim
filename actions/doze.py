from typing import TYPE_CHECKING

from action import Action

if TYPE_CHECKING:
    from world import World


class Doze(Action):
    """
    휴면 — 아무 것도 하지 않는 no-op 액션.

    Rest behavior가 비활동기(주행성은 밤)에 반환해 '이 틱엔 쉰다'는 선택을 점유한다.
    엔티티당 틱당 1액션이므로, 이게 채택되면 하위 우선순위(섭식·사냥·번식·배회)가 막혀
    개체가 그 자리에 머문다. 자는 동안의 대사 절감은 passive(daylight 기반)에서 처리한다.
    """

    def apply(self, world: "World") -> None:
        pass  # 의도적 no-op — 휴면은 월드를 바꾸지 않는다
