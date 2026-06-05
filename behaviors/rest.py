from typing import TYPE_CHECKING

from actions.doze import Doze
from behavior import Behavior

if TYPE_CHECKING:
    from action import Action
    from dinosaur.base import Dinosaur
    from world import WorldSnapshot


class Rest(Behavior):
    """
    비활동기엔 휴면한다 — Doze를 반환해 섭식·사냥·번식·배회를 막고 그 자리에 머문다.

    활동도는 actor.activity(daylight)로 판단한다 — 종마다 주행(diurnal)·야행·상시(cathemeral)를
    다르게 둘 수 있다. 활동도가 rest_threshold 미만이면 쉰다.

    **Flee보다 아래**에 두는 게 핵심이다: 자는 개체도 포식자가 다가오면 깨어 도망하므로(Flee가
    먼저 채택) 밤이 '앉은 오리' 학살이 되지 않는다. 대사 절감(에너지 보존)은 passive에서.
    """

    def __init__(self, actor: "Dinosaur", rest_threshold: float):
        self._actor = actor
        self._rest_threshold = rest_threshold

    def plan(self, snapshot: "WorldSnapshot", dt: float) -> "Action | None":
        if self._actor.activity(snapshot.daylight) >= self._rest_threshold:
            return None  # 활동 시간 — 다음 우선순위(섭식·사냥 등)로
        return Doze()
