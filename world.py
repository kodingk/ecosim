import bisect
import itertools
from dataclasses import dataclass

from action import Action
from entity import Entity, EntityStatus


@dataclass(frozen=True)
class WorldSnapshot:
    """틱-시작 시점의 모든 엔티티 상태를 담은 읽기 전용 뷰."""

    statuses: dict[Entity, EntityStatus]

    def query_entities_within(self, actor: Entity, distance: float) -> list[Entity]:
        """
        actor의 틱-시작 위치 기준 distance 이내의 다른 엔티티를 가까운 순으로 반환한다.
        위치는 스냅샷(틱 시작)을 쓰므로 처리 순서에 결과가 좌우되지 않는다.
        """
        origin = self.statuses[actor].loc
        found = []
        for entity, status in self.statuses.items():
            if entity is actor:
                continue
            d = origin.distance_to(status.loc)
            if d <= distance:
                found.append((d, entity))
        found.sort(key=lambda item: item[0])  # 가까운 순 (동률은 안정 정렬로 결정적)
        return [entity for _, entity in found]


class World:
    def __init__(self, size: tuple[int, int] = (800, 600)):
        self.size = size  # 시뮬레이션 공간 범위 (width, height) — 이동 클램프 등에 사용
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
        2) 적용: 충돌(같은 대상 독점)을 해결한 뒤 Action들을 월드에 반영한다.
        """
        snapshot = self.snapshot()
        actions: list[Action] = []
        for _, _, entity in self._entities:
            for behavior in entity.behaviors():
                action = behavior.plan(snapshot, dt)
                if action is not None:
                    actions.append(action)
                    break
        for action in self._resolve(actions, snapshot):
            action.apply(self)

    def _resolve(self, actions: list[Action], snapshot: WorldSnapshot) -> list[Action]:
        """
        충돌 해결 훅: 같은 대상을 독점(claim)하려는 액션이 여럿이면 단 하나만 남긴다.
        승자는 contest_key 최소값 — Consume의 경우 '가까운 포식자 우선'. 동률은 수집
        순서(= 정렬 순서)로 안정적으로 결정한다. claim이 없는 액션은 그대로 통과한다.
        """
        by_claim: dict[Entity, list[Action]] = {}
        for action in actions:
            target = action.claim()
            if target is not None:
                by_claim.setdefault(target, []).append(action)
        winners = {
            min(claimers, key=lambda a: a.contest_key(snapshot))
            for claimers in by_claim.values()
        }
        return [a for a in actions if a.claim() is None or a in winners]
