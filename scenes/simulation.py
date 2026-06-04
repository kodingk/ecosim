import random

import pygame

from dinosaur.deinonychus import Deinonychus
from dinosaur.psittacosaurus import Psittacosaurus
from dinosaur.pteranodon import Pteranodon
from keybindings import KeyBindings
from overlay import Telemetry
from overlays.hud import Hud
from overlays.population_graph import PopulationGraph
from plant.base import Plant
from scene import Scene
from world import World


class SimulationScene(Scene):
    """
    생태계 시뮬레이션 화면 — 월드를 소유·진행하고 개체·오버레이를 그린다.

    입력은 KeyBindings로 선언적으로 묶는다(일시정지·속도·스텝·오버레이 토글·도움말·타이틀).
    속도는 고정 timestep(1/60) + accumulator로 구현해 배속에도 per-tick 동역학이 보존된다.
    """

    FIXED_DT = 1 / 60
    MAX_SUBSTEPS = 10  # 프레임당 최대 서브스텝(나선 방지)

    def __init__(self, app, seed: int = 42):
        self._app = app
        self.world = World(size=app.size)
        self.telemetry = Telemetry()

        self._font = pygame.font.Font(None, 22)
        self._small = pygame.font.Font(None, 18)
        self._hud = Hud(self.telemetry, self._font, self._small)
        self._graph = PopulationGraph(self.telemetry, self._small, app.size)
        self.overlays = [self._hud, self._graph]

        self._speed = 1.0
        self._paused = False
        self._accum = 0.0
        self._show_help = False
        self._keys = self._make_bindings()

        self._spawn_initial(seed)

    def _make_bindings(self) -> KeyBindings:
        k = KeyBindings()
        k.bind(pygame.K_SPACE, "pause / resume", self._toggle_pause)
        k.bind(pygame.K_PERIOD, "step (when paused)", self._step_once)
        k.bind(pygame.K_1, "speed 0.5x", lambda: self._set_speed(0.5))
        k.bind(pygame.K_2, "speed 1x", lambda: self._set_speed(1.0))
        k.bind(pygame.K_3, "speed 2x", lambda: self._set_speed(2.0))
        k.bind(pygame.K_4, "speed 4x", lambda: self._set_speed(4.0))
        k.bind(pygame.K_h, "toggle HUD", lambda: self._toggle(self._hud))
        k.bind(pygame.K_g, "toggle graph", lambda: self._toggle(self._graph))
        k.bind(pygame.K_F1, "toggle this help", self._toggle_help)
        k.bind(pygame.K_ESCAPE, "back to title", self._to_title)
        return k

    def _spawn_initial(self, seed: int) -> None:
        # 안정 공존이 검증된 수용력 근처 값(헤드리스 다중 시드). 각 개체에 전용 RNG 스트림.
        master = random.Random(seed)
        size = self.world.size
        for _ in range(120):
            self.world.spawn(Plant.gen(size, random.Random(master.random())))
        for _ in range(40):
            self.world.spawn(Psittacosaurus.gen(size, random.Random(master.random())))
        for _ in range(3):
            self.world.spawn(Deinonychus.gen(size, random.Random(master.random())))
        for _ in range(12):
            self.world.spawn(Pteranodon.gen(size, random.Random(master.random())))

    # --- 명령(키 콜백) ---------------------------------------------------------
    def _toggle_pause(self) -> None:
        self._paused = not self._paused

    def _step_once(self) -> None:
        if self._paused:
            self._advance(self.FIXED_DT)

    def _set_speed(self, speed: float) -> None:
        self._speed = speed
        self._paused = False

    def _toggle(self, overlay) -> None:
        overlay.visible = not overlay.visible

    def _toggle_help(self) -> None:
        self._show_help = not self._show_help

    def _to_title(self) -> None:
        from scenes.title import TitleScene

        self._app.switch(TitleScene(self._app))

    # --- Scene 인터페이스 ------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        self._keys.handle(event)

    def _advance(self, dt: float) -> None:
        self.world.update(dt)
        self.telemetry.sample(self.world, dt)

    def update(self, frame_dt: float) -> None:
        if self._paused:
            return
        # 고정 timestep accumulator: 배속이어도 per-tick 동역학 보존.
        self._accum += frame_dt * self._speed
        steps = 0
        while self._accum >= self.FIXED_DT and steps < self.MAX_SUBSTEPS:
            self._advance(self.FIXED_DT)
            self._accum -= self.FIXED_DT
            steps += 1
        if self._accum > self.FIXED_DT:  # 못 따라가면 잔여 시간을 버려 나선 방지
            self._accum = 0.0

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((18, 20, 16))
        for entity in self.world.entities:
            sprite = entity.sprite()
            screen.blit(sprite, sprite.get_rect(center=entity.status.loc))
        for overlay in self.overlays:
            if overlay.visible:
                screen.blit(overlay.sprite(), overlay.anchor)
        self._render_status(screen)
        if self._show_help:
            self._render_help(screen)

    # --- 상태줄 / 도움말 -------------------------------------------------------
    def _render_status(self, screen: pygame.Surface) -> None:
        h = screen.get_height()
        state = "PAUSED" if self._paused else f"{self._speed:g}x"
        color = (240, 200, 120) if self._paused else (160, 170, 160)
        screen.blit(self._font.render(state, True, color), (10, h - 28))
        screen.blit(
            self._small.render("[F1] help", True, (110, 120, 110)), (70, h - 26)
        )

    def _render_help(self, screen: pygame.Surface) -> None:
        lines = self._keys.help_lines()
        w, h = screen.get_size()
        pw, ph = 320, 34 + 22 * len(lines)
        x0, y0 = (w - pw) // 2, (h - ph) // 2
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((12, 14, 18, 225))
        pygame.draw.rect(panel, (90, 95, 100), (0, 0, pw, ph), 1)
        panel.blit(self._font.render("CONTROLS", True, (220, 225, 210)), (14, 8))
        y = 34
        for key_name, label in lines:
            panel.blit(self._small.render(key_name, True, (240, 220, 150)), (16, y))
            panel.blit(self._small.render(label, True, (205, 210, 200)), (110, y))
            y += 22
        screen.blit(panel, (x0, y0))
