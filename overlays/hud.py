import pygame

from overlay import Overlay, Telemetry


class Hud(Overlay):
    """좌상단 패널: 경과 시간·총 biomass + 종별 실시간 카운트(색 범례 포함)."""

    def __init__(
        self,
        telemetry: Telemetry,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        anchor: tuple[float, float] = (8, 8),
        width: int = 210,
    ):
        super().__init__(anchor, toggle_key=pygame.K_h)
        self._tel = telemetry
        self._font = font
        self._small = small_font
        self._w = width

    def sprite(self) -> pygame.Surface:
        tel = self._tel
        names = tel.ordered_names()
        height = 38 + 20 * len(names)
        surf = pygame.Surface((self._w, height), pygame.SRCALPHA)
        surf.fill((10, 12, 10, 150))

        title = f"t={int(tel.elapsed)}s   biomass={int(tel.biomass)}"
        surf.blit(self._font.render(title, True, (230, 230, 230)), (8, 6))
        y = 32
        for name in names:
            color = tel.colors.get(name, (200, 200, 200))
            pygame.draw.rect(surf, color, (8, y + 3, 12, 12))
            pygame.draw.rect(surf, (60, 60, 60), (8, y + 3, 12, 12), 1)
            label = f"{name[:16]}: {tel.counts.get(name, 0)}"
            surf.blit(self._small.render(label, True, (220, 220, 220)), (26, y))
            y += 20
        return surf
