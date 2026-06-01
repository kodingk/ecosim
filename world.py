import heapq
import itertools
from dataclasses import dataclass

from action import Action
from entity import Entity, EntityStatus


@dataclass(frozen=True)
class WorldSnapshot:
    """틱-시작 시점의 모든 엔티티 상태를 담은 읽기 전용 뷰."""

    statuses: dict[Entity, EntityStatus]


class World:
    def __init__(self):
        # level 기준 최소 힙. 동률 level에서 Entity끼리 비교되지 않도록 counter로 tie-break한다.
        # 주의: level은 spawn 시점에 힙 키로 굳으므로, 런타임에 바뀌면 re-spawn해야 순서가 맞다.
        self._heap: list[tuple[int, int, Entity]] = []
        self._counter = itertools.count()

    @property
    def entities(self) -> list[Entity]:
        """
        모든 엔티티를 level 오름차순으로 반환하는 프로퍼티. (읽기 전용)
        힙 복사본을 pop하며 추출하므로 낮은 level이 앞 — 순서대로 그리면 높은 level이 위에 온다.
        """
        heap = list(self._heap)
        return [heapq.heappop(heap)[2] for _ in range(len(heap))]

    def spawn(self, entity: Entity):
        heapq.heappush(self._heap, (entity.status().level, next(self._counter), entity))

    def despawn(self, entity: Entity):
        # 힙에서 임의 원소 제거는 O(n): 걸러낸 뒤 다시 heapify한다.
        self._heap = [item for item in self._heap if item[2] is not entity]
        heapq.heapify(self._heap)

    def snapshot(self) -> WorldSnapshot:
        """현재 모든 엔티티의 상태를 떠 읽기 전용 스냅샷을 만든다."""
        return WorldSnapshot(
            statuses={entity: entity.status() for _, _, entity in self._heap}
        )

    def update(self, dt: float):
        """
        2단계로 모든 엔티티를 업데이트한다.

        1) 판단: 모든 엔티티가 동일한 틱-시작 스냅샷을 보고 Action을 계산한다.
           월드를 변경하지 않으므로 처리 순서에 결과가 좌우되지 않는다.
        2) 적용: 계산된 Action들을 월드에 반영한다.
        """
        snapshot = self.snapshot()
        actions: list[Action] = []
        for _, _, entity in self._heap:
            for behavior in entity.behaviors():
                action = behavior.plan(snapshot, dt)
                if action is not None:
                    actions.append(action)
                    break
        for action in actions:
            action.apply(self)
