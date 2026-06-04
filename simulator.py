import pygame

from overlay import Telemetry
from overlays.hud import Hud
from overlays.population_graph import PopulationGraph
from world import World


class Simulator:
    """
    루프·화면을 소유하고 월드 상태를 읽어 그리는 오케스트레이션 + 표현 계층.

    렌더링은 전적으로 여기 있다(World 아님). 개체 스프라이트를 level 순으로 그린 뒤, 관찰용
    오버레이(HUD·그래프)를 얹는다. 오버레이는 Overlay(Entity) 위젯이지만 **월드에 spawn하지
    않고** Simulator가 보유한다 — 시뮬레이션 틱·snapshot에 끼지 않아 모델/뷰 분리를 지킨다.
    종 집계·시계열은 Telemetry가 맡고, 위젯은 그걸 읽어 그린다(집계와 표현의 분리).
    """

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
        font = pygame.font.Font(None, 22)
        small_font = pygame.font.Font(None, 18)

        self.telemetry = Telemetry()
        # 화면 고정 오버레이(월드 밖, Simulator 보유). h/g 키로 각각 토글.
        self.overlays = [
            Hud(self.telemetry, font, small_font),
            PopulationGraph(self.telemetry, small_font, self.size),
        ]

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    else:
                        for overlay in self.overlays:
                            if overlay.toggle_key == event.key:
                                overlay.visible = not overlay.visible
            dt = self.clock.tick(self.fps) / 1000
            self.world.update(dt=dt)
            self.telemetry.sample(self.world, dt)
            self.render()
        pygame.quit()

    def render(self):
        """
        월드 상태를 화면에 그린다. (렌더링은 Simulator의 책임)
        World.entities가 level 오름차순이라 순서대로 그리면 높은 level이 위에 온다.
        그 위에 관찰용 오버레이를 얹는다.
        """
        self.screen.fill((18, 20, 16))
        for entity in self.world.entities:
            sprite = entity.sprite()
            self.screen.blit(sprite, sprite.get_rect(center=entity.status.loc))
        for overlay in self.overlays:
            if overlay.visible:
                self.screen.blit(overlay.sprite(), overlay.anchor)
        pygame.display.flip()
