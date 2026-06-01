from dataclasses import dataclass

from action import Action
from entity import Entity, EntityStatus


@dataclass(frozen=True)
class WorldSnapshot:
    """틱-시작 시점의 모든 엔티티 상태를 담은 읽기 전용 뷰."""

    statuses: dict[Entity, EntityStatus]


class World:
    def __init__(self):
        self._entities: list[Entity] = []

    @property
    def entities(self) -> list[Entity]:
        """
        모든 엔티티를 level 오름차순으로 반환하는 프로퍼티. (읽기 전용)
        낮은 level이 앞에 와서, 순서대로 그리면 높은 level이 위에 그려진다 (z-order).
        """
        return sorted(self._entities, key=lambda entity: entity.status().level)

    def spawn(self, entity: Entity):
        self._entities.append(entity)

    def despawn(self, entity: Entity):
        self._entities.remove(entity)

    def snapshot(self) -> WorldSnapshot:
        """현재 모든 엔티티의 상태를 떠 읽기 전용 스냅샷을 만든다."""
        return WorldSnapshot(
            statuses={entity: entity.status() for entity in self._entities}
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
        for entity in self._entities:
            for behavior in entity.behaviors():
                action = behavior.plan(snapshot, dt)
                if action is not None:
                    actions.append(action)
                    break
        for action in actions:
            action.apply(self)
