import pygame

from scene import Scene


class Simulator:
    """
    앱 셸 — 창·클럭·메인 루프와 **현재 Scene 하나**를 소유한다.

    화면 단위 로직(시뮬레이션 진행·렌더·입력)은 Scene이 맡고, 여기서는 매 프레임
    handle_event→update→render로 위임하고 화면을 flip한다. 화면 전환은 switch(scene),
    종료는 quit()으로 Scene이 요청한다. (이전엔 Simulator가 시뮬을 직접 돌렸으나,
    SimulationScene으로 분리해 타이틀·설정 등 여러 화면을 둘 수 있게 됐다.)
    """

    def __init__(self, size: tuple[int, int] = (800, 600), fps: int = 60):
        pygame.init()
        self.size = size
        self.fps = fps
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("백악기 시뮬레이터")
        self.clock = pygame.time.Clock()
        self.running = False
        self._scene: Scene | None = None

    def switch(self, scene: Scene) -> None:
        """현재 Scene을 교체한다(이전 Scene on_exit → 새 Scene on_enter)."""
        if self._scene is not None:
            self._scene.on_exit()
        self._scene = scene
        scene.on_enter()

    def quit(self) -> None:
        self.running = False

    def run(self, scene: Scene) -> None:
        self.switch(scene)
        self.running = True
        while self.running:
            dt = self.clock.tick(self.fps) / 1000
            current = self._scene
            assert current is not None  # switch가 루프 진입 전 항상 설정한다
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    current.handle_event(event)
            current.update(dt)
            current.render(self.screen)
            pygame.display.flip()
        pygame.quit()
