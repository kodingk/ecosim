from collections import deque

import pygame

from world import World


class Simulator:
    """
    루프·화면을 소유하고 월드 상태를 읽어 그리는 오케스트레이션 + 표현 계층.

    렌더링은 전적으로 여기 있다(World 아님). 개체 스프라이트 위에 관찰용 오버레이를 그린다:
    종별 실시간 카운트 HUD와 개체수 시계열 그래프. 종 집계는 type(e).__name__·e.color로
    **제네릭**하게 하므로 새 종을 추가해도 오버레이가 자동 대응한다(구체 종에 결합하지 않음).
    """

    # 그래프 표시 샘플 수와 샘플 간격(초). N×간격 = 화면에 보이는 시간 창.
    GRAPH_SAMPLES = 360
    SAMPLE_INTERVAL = 0.5  # → 약 3분 창

    def __init__(self):
        pygame.init()
        self.size = (800, 600)
        self.world = World(size=self.size)
        self.running = False
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("백악기 시뮬레이터")

        # 온스크린 텍스트는 기본 폰트(ASCII)만 쓴다 — 종 이름·수치가 ASCII라 안전.
        self.font = pygame.font.Font(None, 22)
        self.small_font = pygame.font.Font(None, 18)

        self.elapsed = 0.0  # 누적 시뮬레이션 시간(초)
        self._since_sample = 0.0
        # 종 이름 → 카운트 시계열(deque). 색·level은 표시 정렬/범례에 쓴다.
        self.history: dict[str, deque[int]] = {}
        self.series_color: dict[str, tuple[int, int, int]] = {}
        self.series_level: dict[str, int] = {}
        self.show_hud = True
        self.show_graph = True

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_h:
                        self.show_hud = not self.show_hud
                    elif event.key == pygame.K_g:
                        self.show_graph = not self.show_graph
            dt = self.clock.tick(self.fps) / 1000
            self.world.update(dt=dt)
            self.elapsed += dt
            self._sample(dt)
            self.render()
        pygame.quit()

    # --------------------------------------------------------------------------
    # 집계 / 샘플링
    # --------------------------------------------------------------------------
    def _stats(self):
        """현재 월드를 종(class)별로 제네릭 집계: 이름→카운트, 색, level, 총 biomass."""
        counts: dict[str, int] = {}
        biomass = 0.0
        for e in self.world.entities:
            name = type(e).__name__
            counts[name] = counts.get(name, 0) + 1
            if name not in self.series_color:
                self.series_color[name] = getattr(e, "color", (200, 200, 200))
                self.series_level[name] = getattr(e, "level", 0)
            biomass += getattr(e, "biomass", 0.0)
        return counts, biomass

    def _sample(self, dt: float):
        """SAMPLE_INTERVAL마다 종별 카운트를 시계열에 적재한다(그래프용)."""
        self._since_sample += dt
        if self._since_sample < self.SAMPLE_INTERVAL:
            return
        self._since_sample = 0.0
        counts, _ = self._stats()
        # 알려진 모든 종에 대해 매 샘플 적재(없으면 0) → 모든 시계열 길이가 정렬된다.
        names = set(self.history) | set(counts)
        for name in names:
            if name not in self.history:
                self.history[name] = deque(maxlen=self.GRAPH_SAMPLES)
            self.history[name].append(counts.get(name, 0))

    # --------------------------------------------------------------------------
    # 렌더링
    # --------------------------------------------------------------------------
    def render(self):
        """
        월드 상태를 화면에 그린다. (렌더링은 Simulator의 책임)
        World.entities가 level 오름차순이라 순서대로 그리면 높은 level이 위에 온다.
        그 위에 관찰용 오버레이(HUD·그래프)를 얹는다.
        """
        self.screen.fill((18, 20, 16))
        for entity in self.world.entities:
            sprite = entity.sprite()
            self.screen.blit(sprite, sprite.get_rect(center=entity.status.loc))
        if self.show_graph:
            self._draw_graph()
        if self.show_hud:
            self._draw_hud()
        pygame.display.flip()

    def _ordered_series(self):
        """표시 순서: level 오름차순(식물→초식→포식), 동률은 이름순."""
        return sorted(
            self.history, key=lambda n: (self.series_level.get(n, 0), n)
        )

    def _draw_hud(self):
        counts, biomass = self._stats()
        lines = [f"t={int(self.elapsed)}s   biomass={int(biomass)}"]
        # 패널 배경(반투명)
        names = self._ordered_series()
        height = 24 + 20 * (len(names) + 1)
        panel = pygame.Surface((210, height), pygame.SRCALPHA)
        panel.fill((10, 12, 10, 150))
        self.screen.blit(panel, (8, 8))

        y = 14
        self.screen.blit(self.font.render(lines[0], True, (230, 230, 230)), (16, y))
        y += 24
        for name in names:
            color = self.series_color.get(name, (200, 200, 200))
            pygame.draw.rect(self.screen, color, (16, y + 3, 12, 12))
            pygame.draw.rect(self.screen, (60, 60, 60), (16, y + 3, 12, 12), 1)
            label = f"{name[:16]}: {counts.get(name, 0)}"
            self.screen.blit(self.small_font.render(label, True, (220, 220, 220)), (34, y))
            y += 20

    def _draw_graph(self):
        if not self.history:
            return
        w, h = 300, 120
        x0, y0 = self.size[0] - w - 10, 10
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill((10, 12, 16, 160))
        self.screen.blit(panel, (x0, y0))
        pygame.draw.rect(self.screen, (70, 70, 80), (x0, y0, w, h), 1)

        pad = 6
        gx, gy = x0 + pad, y0 + pad
        gw, gh = w - 2 * pad, h - 2 * pad
        # y 스케일: 모든 시계열 통틀어 최댓값(최소 1).
        ymax = max(
            (max(series) for series in self.history.values() if series), default=1
        )
        ymax = max(ymax, 1)

        for name in self._ordered_series():
            series = self.history[name]
            n = len(series)
            if n < 2:
                continue
            color = self.series_color.get(name, (200, 200, 200))
            step = gw / (self.GRAPH_SAMPLES - 1)
            # 최신 샘플을 오른쪽 끝에 정렬(오른쪽에서 흘러들어오는 모양).
            points = [
                (
                    gx + gw - (n - 1 - i) * step,
                    gy + gh - (val / ymax) * gh,
                )
                for i, val in enumerate(series)
            ]
            pygame.draw.lines(self.screen, color, False, points, 2)

        # y축 최댓값 라벨
        self.screen.blit(
            self.small_font.render(f"max {ymax}", True, (170, 170, 170)),
            (x0 + 4, y0 + 2),
        )
        self.screen.blit(
            self.small_font.render("pop / time  (g:toggle)", True, (140, 140, 140)),
            (x0 + 4, y0 + h - 16),
        )
