import random

import pygame

from dinosaur.deinonychus import Deinonychus
from dinosaur.psittacosaurus import Psittacosaurus
from dinosaur.pteranodon import Pteranodon
from overlay import Telemetry
from overlays.hud import Hud
from overlays.population_graph import PopulationGraph
from plant.base import Plant
from scene import Scene
from world import World


class SimulationScene(Scene):
    """
    생태계 시뮬레이션 화면 — 월드를 소유·진행하고 개체·오버레이를 그린다.

    이전엔 Simulator가 직접 하던 일(월드 update·telemetry 샘플·렌더)을 여기로 옮겨, Simulator는
    창·루프·씬 전환만 맡는 셸이 됐다. ESC로 타이틀로 돌아가고, h/g로 HUD·그래프를 토글한다.
    """

    def __init__(self, app, seed: int = 42):
        self._app = app
        self.world = World(size=app.size)
        self.telemetry = Telemetry()

        font = pygame.font.Font(None, 22)
        small_font = pygame.font.Font(None, 18)
        self.overlays = [
            Hud(self.telemetry, font, small_font),
            PopulationGraph(self.telemetry, small_font, app.size),
        ]
        self._spawn_initial(seed)

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

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                from scenes.title import TitleScene

                self._app.switch(TitleScene(self._app))
            else:
                for overlay in self.overlays:
                    if overlay.toggle_key == event.key:
                        overlay.visible = not overlay.visible

    def update(self, dt: float) -> None:
        self.world.update(dt)
        self.telemetry.sample(self.world, dt)

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((18, 20, 16))
        for entity in self.world.entities:
            sprite = entity.sprite()
            screen.blit(sprite, sprite.get_rect(center=entity.status.loc))
        for overlay in self.overlays:
            if overlay.visible:
                screen.blit(overlay.sprite(), overlay.anchor)
