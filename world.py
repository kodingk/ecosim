import bisect
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
        # level 오름차순으로 유지되는 리스트. spawn 때 bisect로 제자리에 끼워넣는다.
        # 동률 level에서 Entity끼리 비교되지 않도록 counter로 tie-break(+ 삽입 순서 안정).
        # 주의: level은 spawn 시 정렬 키로 굳으므로, 런타임에 바뀌면 re-spawn해야 순서가 맞다.
        self._entities: list[tuple[int, int, Entity]] = []
        self._counter = itertools.count()

    @property
    def entities(self) -> list[Entity]:
        """
        모든 엔티티를 level 오름차순으로 반환하는 프로퍼티. (읽기 전용)
        이미 정렬돼 있어 매번 정렬하지 않고 추출만 한다 — 낮은 level이 앞.
        """
        return [entity for _, _, entity in self._entities]

    def spawn(self, entity: Entity):
        # 정렬을 유지하도록 level 위치에 삽입한다 (O(log n) 탐색 + O(n) 시프트).
        bisect.insort(
            self._entities, (entity.status().level, next(self._counter), entity)
        )

    def despawn(self, entity: Entity):
        # 정렬 리스트에서 제거해도 나머지 순서는 유지된다 (O(n)).
        self._entities = [item for item in self._entities if item[2] is not entity]

    def snapshot(self) -> WorldSnapshot:
        """현재 모든 엔티티의 상태를 떠 읽기 전용 스냅샷을 만든다."""
        return WorldSnapshot(
            statuses={entity: entity.status() for _, _, entity in self._entities}
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
        for _, _, entity in self._entities:
            for behavior in entity.behaviors():
                action = behavior.plan(snapshot, dt)
                if action is not None:
                    actions.append(action)
                    break
        for action in actions:
            action.apply(self)
