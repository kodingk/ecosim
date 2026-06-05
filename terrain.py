import random

import pygame


def make_ground(size: tuple[int, int], seed: int = 7) -> pygame.Surface:
    """
    절차적 '땅' 배경을 한 장의 불투명 Surface로 생성한다(시각 전용 — 모델이 아니다).

    단색 채우기 대신 흙·이끼 톤의 부드러운 얼룩을 흩뿌려 유기적인 지면 질감을 준다. Scene 진입
    시 1회 만들어 캐시하고 매 프레임 그대로 blit하므로 런타임 비용은 blit 한 번뿐이다. 결정적
    시드를 써 실행마다 같은 지면이 나온다. (물·생물은 Entity라 이 위에 얹혀 그려진다.)
    """
    w, h = size
    # 24비트(알파 채널 없음)로 만든다. 32비트로 두면 cocoa(macOS) 등 디스플레이 포맷에 알파
    # 채널이 있어, 아래 SRCALPHA 얼룩 레이어를 blit하는 순간 배경 surface의 알파가 0으로
    # 오염된다 → 화면에 투명하게 깔려 땅이 안 보이고 생물만 검은 배경 위에 뜬 것처럼 보인다.
    # 알파 채널이 아예 없으면 오염될 것이 없어 항상 불투명하게 칠해진다.
    surf = pygame.Surface((w, h), 0, 24)
    surf.fill((44, 52, 38))  # 기본 이끼낀 흙색
    rng = random.Random(seed)
    palette = [
        (50, 60, 42),
        (38, 46, 32),
        (58, 64, 46),
        (48, 44, 34),  # 마른 흙
        (40, 56, 44),  # 이끼
    ]
    # 부드러운 얼룩 — 반투명 타원을 다수 흩뿌려 모틀링(mottling). 한 장에 모아 1회 blit.
    blot = pygame.Surface((w, h), pygame.SRCALPHA)
    for _ in range(900):
        cx = rng.randint(0, w)
        cy = rng.randint(0, h)
        r = rng.randint(6, 26)
        col = rng.choice(palette)
        a = rng.randint(18, 40)
        pygame.draw.ellipse(blot, (*col, a), (cx - r, cy - r, 2 * r, r + r // 2))
    surf.blit(blot, (0, 0))
    return surf
