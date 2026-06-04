import abc
from collections import deque

import pygame

from entity import Entity, EntityStatus


class Overlay(Entity):
    """
    화면 고정 관찰 위젯의 베이스. `Entity`를 상속해 'sprite()로 그려지는 것'이라는 통일된 타입을
    유지하지만, **월드에 spawn되지 않고** Simulator가 직접 보유·렌더한다 — 즉 시뮬레이션 틱·
    snapshot·공간 쿼리에 끼지 않아 모델/뷰 분리를 지킨다.

    sprite()는 자기 패널 Surface를 반환하고 Simulator가 anchor(좌상단 기준)에 blit한다.
    엔티티 계약 중 시뮬레이션 관련 메서드(behaviors·gen·passive)는 오버레이엔 의미가 없어
    여기서 한 번 비활성으로 막아 두므로, 구체 위젯은 sprite()만 구현하면 된다.
    """

    level = 1000  # 개념상 최상단(실제로는 월드 밖이라 Simulator가 따로 그린다)

    def __init__(self, anchor: tuple[float, float], toggle_key: int | None = None):
        self._anchor = pygame.Vector2(anchor)  # 화면 좌상단 기준 위치
        self.toggle_key = toggle_key  # 이 키로 표시 토글(Simulator가 처리)
        self.visible = True

    @property
    def anchor(self) -> pygame.Vector2:
        return pygame.Vector2(self._anchor)

    # --- Entity 계약: 오버레이는 시뮬레이션에 참여하지 않으므로 비활성 -------------------
    def behaviors(self):
        return []

    @classmethod
    def gen(cls, world_size, rng):
        raise NotImplementedError(
            "Overlay는 월드에 spawn되지 않는다(Simulator가 보유한다)."
        )

    @property
    def status(self) -> EntityStatus:
        return EntityStatus(loc=self.anchor, level=self.level)

    @status.setter
    def status(self, value: EntityStatus) -> None:
        self._anchor = value.loc

    @abc.abstractmethod
    def sprite(self) -> pygame.Surface:
        """위젯 자신을 그린 패널 Surface를 반환한다(Simulator가 anchor에 blit)."""


class Telemetry:
    """
    월드를 종(class)별로 제네릭 집계하고 개체수 시계열을 누적하는 **뷰 데이터** 모델.

    매 프레임 sample()로 현재 카운트·총 biomass를 갱신하고, SAMPLE 간격마다 시계열(history)에
    적재한다. 종 식별은 type(e).__name__·e.color로 하므로 새 종을 추가해도 자동 대응한다.
    오버레이(HUD·그래프)는 이 객체를 읽어 그린다 — 집계 로직과 표현을 분리한다.
    """

    def __init__(self, samples: int = 360, interval: float = 0.5):
        self.samples = samples  # 시계열 표시 샘플 수
        self.interval = interval  # 샘플 간격(초). samples×interval = 화면 시간 창
        self.elapsed = 0.0
        self._since = 0.0
        self.counts: dict[str, int] = {}  # 현재 종별 카운트
        self.biomass = 0.0
        self.colors: dict[str, tuple[int, int, int]] = {}  # 누적(한번 본 종은 유지)
        self.levels: dict[str, int] = {}
        self.history: dict[str, deque[int]] = {}  # 종 → 카운트 시계열

    def sample(self, world, dt: float) -> None:
        self.elapsed += dt
        counts: dict[str, int] = {}
        biomass = 0.0
        for e in world.entities:
            name = type(e).__name__
            counts[name] = counts.get(name, 0) + 1
            if name not in self.colors:
                self.colors[name] = getattr(e, "color", (200, 200, 200))
                self.levels[name] = getattr(e, "level", 0)
            biomass += getattr(e, "biomass", 0.0)
        self.counts = counts
        self.biomass = biomass
        # 시계열: 간격마다 알려진 모든 종을 적재(없으면 0) → 길이 정렬
        self._since += dt
        if self._since >= self.interval:
            self._since = 0.0
            for name in set(self.history) | set(counts):
                if name not in self.history:
                    self.history[name] = deque(maxlen=self.samples)
                self.history[name].append(counts.get(name, 0))

    def ordered_names(self) -> list[str]:
        """한 번이라도 본 모든 종을 level 오름차순(동률 이름순)으로. 멸종한 종도 0으로 표시."""
        return sorted(self.colors, key=lambda n: (self.levels.get(n, 0), n))
