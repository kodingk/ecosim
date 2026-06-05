import math


class DayNightCycle:
    """
    낮·밤 시계 — 시간을 누적해 phase[0,1)와 daylight[0,1]을 낸다. 순수 모델(pygame 무관).

    daylight = 0.5·(1 − cos(2π·phase)) 라 부드러운 사인 곡선이다:
      phase 0.0 = 한밤(daylight 0), 0.5 = 정오(1), 0.25/0.75 = 새벽/황혼(0.5).
    behavior는 임계(예: <0.35 = 밤)로, 뷰는 연속 밝기로 읽는다. World가 소유·전진시킨다.
    """

    def __init__(self, day_length: float = 36.0, start_phase: float = 0.5) -> None:
        # day_length: 한 사이클(초). start_phase=0.5 → 정오에서 시작(낮부터 돌아간다).
        self._day_length = day_length
        self._time = start_phase * day_length

    def advance(self, dt: float) -> None:
        self._time += dt

    @property
    def phase(self) -> float:
        return (self._time / self._day_length) % 1.0

    @property
    def daylight(self) -> float:
        return 0.5 * (1.0 - math.cos(2.0 * math.pi * self.phase))
