import pygame

from keybindings import KeyBindings
from scene import Scene


class TitleScene(Scene):
    """시작 화면 — SPACE/ENTER로 시뮬레이션 진입, ESC로 종료."""

    # 범례용 종 색(시각적 장식 겸 안내)
    _LEGEND = [
        ((50, 150, 60), "Plants"),
        ((210, 180, 120), "Psittacosaurus"),
        ((170, 70, 60), "Deinonychus"),
        ((120, 200, 210), "Pteranodon"),
    ]

    def __init__(self, app):
        self._app = app
        self._title_font = pygame.font.Font(None, 76)
        self._font = pygame.font.Font(None, 30)
        self._small = pygame.font.Font(None, 22)
        self._keys = KeyBindings()
        self._keys.bind(pygame.K_RETURN, "start", self._start)
        self._keys.bind(pygame.K_SPACE, "start", self._start)
        self._keys.bind(pygame.K_ESCAPE, "quit", self._app.quit)

    def _start(self) -> None:
        from scenes.simulation import SimulationScene

        self._app.switch(SimulationScene(self._app))

    def handle_event(self, event: pygame.event.Event) -> None:
        self._keys.handle(event)

    def update(self, dt: float) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        w, h = screen.get_size()
        screen.fill((12, 14, 18))

        title = self._title_font.render("CRETACEOUS", True, (220, 225, 210))
        screen.blit(title, title.get_rect(center=(w // 2, h // 2 - 90)))
        subtitle = self._font.render("ecosystem simulator", True, (150, 160, 150))
        screen.blit(subtitle, subtitle.get_rect(center=(w // 2, h // 2 - 48)))

        # 종 범례
        y = h // 2 + 4
        for color, name in self._LEGEND:
            row = self._small.render(name, True, (200, 205, 195))
            cx = w // 2 - 70
            pygame.draw.rect(screen, color, (cx, y + 3, 13, 13))
            pygame.draw.rect(screen, (60, 60, 60), (cx, y + 3, 13, 13), 1)
            screen.blit(row, (cx + 22, y))
            y += 24

        prompt = self._font.render(
            "[SPACE] start     [ESC] quit", True, (180, 190, 200)
        )
        screen.blit(prompt, prompt.get_rect(center=(w // 2, h - 70)))
