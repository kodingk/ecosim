import os

import pygame

_DIR = os.path.join(os.path.dirname(__file__), "assets", "sprites")
_base_cache: dict[str, pygame.Surface] = {}
_xform_cache: dict[tuple, pygame.Surface] = {}


def _base(name: str) -> pygame.Surface:
    img = _base_cache.get(name)
    if img is None:
        img = pygame.image.load(os.path.join(_DIR, f"{name}.png"))
        try:
            img = img.convert_alpha()
        except pygame.error:
            pass  # 디스플레이 미설정(헤드리스) — 원본 surface 그대로
        _base_cache[name] = img
    return img


def sprite(
    name: str, size: int, angle: float = 0.0, bright: float = 1.0
) -> pygame.Surface:
    """
    name 에셋을 한 변 size로 스케일 + angle(도) 회전 + bright(0~1) 명도 적용.

    (size, angle, bright)를 버킷팅해 캐시하므로 매 프레임 변환을 반복하지 않는다 — 같은 종·
    비슷한 크기·각도의 개체 다수가 한 surface를 공유한다.
    """
    size = max(4, int(size))
    abkt = (int(round(angle)) % 360) // 12 * 12  # 12도 버킷
    bbkt = round(bright * 5) / 5  # 0.2 단계
    key = (name, size, abkt, bbkt)
    img = _xform_cache.get(key)
    if img is None:
        img = pygame.transform.smoothscale(_base(name), (size, size))
        if abkt:
            img = pygame.transform.rotate(img, abkt)
        if bbkt < 0.999:
            img = img.copy()
            v = int(255 * bbkt)
            img.fill((v, v, v), special_flags=pygame.BLEND_RGB_MULT)
        _xform_cache[key] = img
    return img
