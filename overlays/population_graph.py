import pygame

from overlay import Overlay, Telemetry


class PopulationGraph(Overlay):
    """우상단 패널: 종별 개체수 시계열을 색 폴리라인으로 그린다(포식-피식 진동 시각화)."""

    def __init__(
        self,
        telemetry: Telemetry,
        small_font: pygame.font.Font,
        screen_size: tuple[int, int],
        width: int = 300,
        height: int = 120,
    ):
        anchor = (screen_size[0] - width - 10, 10)  # 우상단 정렬
        super().__init__(anchor, toggle_key=pygame.K_g)
        self._tel = telemetry
        self._small = small_font
        self._w = width
        self._h = height

    def sprite(self) -> pygame.Surface:
        tel = self._tel
        w, h = self._w, self._h
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((10, 12, 16, 160))
        pygame.draw.rect(surf, (70, 70, 80), (0, 0, w, h), 1)

        pad = 6
        gx, gy, gw, gh = pad, pad, w - 2 * pad, h - 2 * pad
        if tel.history:
            ymax = max((max(s) for s in tel.history.values() if s), default=1)
            ymax = max(ymax, 1)
            step = gw / (tel.samples - 1)
            for name in tel.ordered_names():
                series = tel.history.get(name)
                if not series or len(series) < 2:
                    continue
                n = len(series)
                color = tel.colors.get(name, (200, 200, 200))
                # 최신 샘플을 오른쪽 끝에 정렬(오른쪽에서 흘러들어오는 모양)
                points = [
                    (gx + gw - (n - 1 - i) * step, gy + gh - (v / ymax) * gh)
                    for i, v in enumerate(series)
                ]
                pygame.draw.lines(surf, color, False, points, 2)
            surf.blit(self._small.render(f"max {ymax}", True, (170, 170, 170)), (4, 2))
        surf.blit(
            self._small.render("pop / time  (g:toggle)", True, (140, 140, 140)),
            (4, h - 16),
        )
        return surf
