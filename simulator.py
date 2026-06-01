import pygame

from world import World


class Simulator:
    def __init__(self):
        pygame.init()
        self.world = World()
        self.running = False
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("백악기 시뮬레이터")

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
            dt = self.clock.tick(self.fps) / 1000
            self.world.update(dt=dt)
            self.render()
        pygame.quit()

    def render(self):
        """
        월드의 현재 상태를 화면에 그리는 함수. (렌더링은 Simulator의 책임)
        World.entities가 level 오름차순이라, 순서대로 그리면 높은 level이 위에 온다.
        위치의 정본은 각 엔티티의 status()다.
        """
        self.screen.fill((0, 0, 0))
        for entity in self.world.entities:
            status = entity.status()
            sprite = entity.sprite()
            self.screen.blit(sprite, sprite.get_rect(center=status.loc))
        pygame.display.flip()
