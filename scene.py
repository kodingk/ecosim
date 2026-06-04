import abc

import pygame


class Scene(abc.ABC):
    """
    하나의 화면(타이틀·시뮬레이션·설정 등)을 나타내는 뷰-앱 계층의 단위.

    Simulator(앱 셸)가 현재 Scene 하나를 들고 매 프레임 handle_event→update→render로 위임한다.
    Scene은 app 참조로 화면 전환(app.switch(other))·종료(app.quit())를 요청한다. 모델(Entity)·
    위젯(Overlay)과 달리 입력·갱신·전체 화면 렌더를 모두 책임지는 더 큰 단위다.
    """

    @abc.abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """pygame 이벤트 하나를 처리한다(키·마우스 등). 전환은 app.switch로 요청."""

    @abc.abstractmethod
    def update(self, dt: float) -> None:
        """dt(초)만큼 상태를 진행한다."""

    @abc.abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """화면 전체를 그린다(flip은 앱 루프가 한다)."""

    def on_enter(self) -> None:
        """이 Scene으로 전환될 때 1회 호출(선택)."""

    def on_exit(self) -> None:
        """이 Scene에서 벗어날 때 1회 호출(선택)."""
