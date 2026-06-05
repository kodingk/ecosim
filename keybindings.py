from collections.abc import Callable

import pygame


class KeyBindings:
    """
    key → (label, callback) 선언적 매핑. KEYDOWN을 등록된 콜백으로 디스패치하고, 도움말용
    (키 이름, 설명) 목록을 제공한다.

    Scene이 입력을 인라인 if 체인 대신 선언적으로 묶게 해, 바인딩을 한곳에서 추가·표시할 수
    있다(도움말 오버레이도 이 목록에서 자동 생성).
    """

    def __init__(self) -> None:
        self._bindings: dict[int, tuple[str, Callable[[], object]]] = {}
        self._order: list[int] = []  # 표시 순서(등록 순)

    def bind(self, key: int, label: str, callback: Callable[[], object]) -> None:
        if key not in self._bindings:
            self._order.append(key)
        self._bindings[key] = (label, callback)

    def handle(self, event: pygame.event.Event) -> bool:
        """KEYDOWN이 바인딩되어 있으면 콜백을 호출하고 True. 아니면 False."""
        if event.type == pygame.KEYDOWN:
            entry = self._bindings.get(event.key)
            if entry is not None:
                entry[1]()
                return True
        return False

    def help_lines(self) -> list[tuple[str, str]]:
        """(키 이름, 설명) 목록 — 도움말 오버레이용."""
        return [(pygame.key.name(k).upper(), self._bindings[k][0]) for k in self._order]
