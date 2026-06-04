"""스프라이트 에셋 생성기 — 음영 들어간 탑다운 생물을 PNG로 렌더한다.

repo 루트에서 `python tools/gen_sprites.py` 실행 → assets/sprites/*.png + _sprite_preview.png.
모두 +x(오른쪽)를 향하게 그린다(런타임에 velocity로 회전). 64×64 캔버스, 음영 3톤.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

pygame.init()
S = 64
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "sprites")
os.makedirs(OUT, exist_ok=True)


def shades(base, lf=1.4, df=0.55):
    light = tuple(min(255, int(c * lf)) for c in base)
    dark = tuple(int(c * df) for c in base)
    return light, dark


def canvas():
    return pygame.Surface((S, S), pygame.SRCALPHA)


def deinonychus():
    """날렵한 이족 포식자(탑다운, 오른쪽 향)."""
    surf = canvas()
    base = (175, 72, 60)
    light, dark = shades(base)
    cx, cy = 30, 32
    # 긴 꼬리(뒤로)
    pygame.draw.polygon(surf, dark, [(cx - 6, cy - 5), (cx - 6, cy + 5), (cx - 26, cy)])
    pygame.draw.polygon(surf, base, [(cx - 6, cy - 4), (cx - 6, cy + 4), (cx - 24, cy)])
    # 몸통
    pygame.draw.ellipse(surf, dark, (cx - 12, cy - 11, 34, 22))
    pygame.draw.ellipse(surf, base, (cx - 11, cy - 10, 32, 20))
    pygame.draw.ellipse(surf, light, (cx - 4, cy - 5, 16, 10))  # 등 하이라이트
    # 다리(뒤쪽 양옆)
    for dy in (-12, 12):
        pygame.draw.ellipse(surf, dark, (cx - 4, cy + dy - 3, 12, 7))
    # 목+머리(앞)
    pygame.draw.circle(surf, dark, (cx + 22, cy), 9)
    pygame.draw.circle(surf, base, (cx + 22, cy), 8)
    pygame.draw.polygon(
        surf, base, [(cx + 28, cy - 4), (cx + 28, cy + 4), (cx + 38, cy)]
    )  # 주둥이
    pygame.draw.polygon(
        surf, dark, [(cx + 28, cy - 4), (cx + 28, cy + 4), (cx + 38, cy)], 1
    )
    # 눈 두 개
    for dy in (-4, 4):
        pygame.draw.circle(surf, (245, 230, 90), (cx + 23, cy + dy), 2)
        pygame.draw.circle(surf, (20, 18, 18), (cx + 24, cy + dy), 1)
    return surf


def psittacosaurus():
    """작고 다부진 각룡(탑다운, 오른쪽 향)."""
    surf = canvas()
    base = (212, 180, 120)
    light, dark = shades(base, 1.18, 0.62)
    cx, cy = 30, 32
    # 짧은 꼬리
    pygame.draw.polygon(
        surf, base, [(cx - 10, cy - 4), (cx - 10, cy + 4), (cx - 22, cy)]
    )
    # 다부진 몸통
    pygame.draw.ellipse(surf, dark, (cx - 14, cy - 13, 34, 26))
    pygame.draw.ellipse(surf, base, (cx - 13, cy - 12, 32, 24))
    pygame.draw.ellipse(surf, light, (cx - 5, cy - 6, 16, 12))
    # 네 다리(탑다운 — 네 귀퉁이)
    for lx, ly in [(cx - 8, -13), (cx - 8, 13), (cx + 8, -12), (cx + 8, 12)]:
        pygame.draw.ellipse(surf, dark, (lx - 3, cy + ly - 3, 9, 7))
    # 머리 + 부리 + 작은 frill
    pygame.draw.circle(surf, dark, (cx + 19, cy), 9)
    pygame.draw.circle(surf, base, (cx + 19, cy), 8)
    pygame.draw.polygon(
        surf, dark, [(cx + 25, cy - 4), (cx + 25, cy + 4), (cx + 33, cy)]
    )  # 부리
    pygame.draw.polygon(
        surf, base, [(cx + 25, cy - 3), (cx + 25, cy + 3), (cx + 31, cy)]
    )
    for dy in (-4, 4):
        pygame.draw.circle(surf, (30, 25, 20), (cx + 21, cy + dy), 1)
    return surf


def pteranodon():
    """펼친 날개의 익룡(탑다운, 오른쪽 향)."""
    surf = canvas()
    base = (120, 200, 210)
    light, dark = shades(base, 1.2, 0.62)
    cx, cy = 28, 32
    # 양 날개(뒤로 젖혀짐)
    for sgn in (-1, 1):
        pygame.draw.polygon(
            surf,
            dark,
            [(cx + 4, cy), (cx - 22, cy + sgn * 22), (cx - 6, cy + sgn * 3)],
        )
        pygame.draw.polygon(
            surf,
            base,
            [(cx + 4, cy), (cx - 18, cy + sgn * 19), (cx - 5, cy + sgn * 3)],
        )
    # 몸통(앞뒤로 긴)
    pygame.draw.ellipse(surf, base, (cx - 6, cy - 4, 26, 8))
    pygame.draw.ellipse(surf, light, (cx - 2, cy - 2, 14, 4))
    # 머리 + 길쭉한 볏(crest, 뒤로)
    pygame.draw.circle(surf, base, (cx + 20, cy), 5)
    pygame.draw.polygon(
        surf, dark, [(cx + 18, cy - 2), (cx + 18, cy + 2), (cx + 30, cy)]
    )  # 부리
    pygame.draw.polygon(
        surf, light, [(cx + 16, cy), (cx + 8, cy - 6), (cx + 10, cy)]
    )  # 볏
    pygame.draw.circle(surf, (20, 30, 30), (cx + 21, cy), 1)
    return surf


def plant():
    """양치/풀 포기(탑다운 로제트)."""
    surf = canvas()
    base = (60, 160, 70)
    light, dark = shades(base, 1.25, 0.55)
    cx, cy = 32, 32
    import math

    # 방사상 잎(8장)
    for i in range(8):
        a = i * math.pi / 4
        tip = (cx + 24 * math.cos(a), cy + 24 * math.sin(a))
        mid = (cx + 10 * math.cos(a), cy + 10 * math.sin(a))
        perp = (math.cos(a + math.pi / 2), math.sin(a + math.pi / 2))
        leaf = [
            (cx, cy),
            (mid[0] + 5 * perp[0], mid[1] + 5 * perp[1]),
            tip,
            (mid[0] - 5 * perp[0], mid[1] - 5 * perp[1]),
        ]
        pygame.draw.polygon(surf, dark if i % 2 else base, leaf)
    pygame.draw.circle(surf, light, (cx, cy), 5)  # 중심
    return surf


SPRITES = {
    "deinonychus": deinonychus,
    "psittacosaurus": psittacosaurus,
    "pteranodon": pteranodon,
    "plant": plant,
}

for name, fn in SPRITES.items():
    img = fn()
    pygame.image.save(img, os.path.join(OUT, f"{name}.png"))
    print(f"saved {name}.png")

# 미리보기 시트: 원본 + 4방향 회전
preview = pygame.Surface((S * 5, S * len(SPRITES)), pygame.SRCALPHA)
preview.fill((30, 32, 36))
for row, (name, fn) in enumerate(SPRITES.items()):
    img = fn()
    preview.blit(img, (0, row * S))
    for col, ang in enumerate((0, 90, 180, 270), start=1):
        preview.blit(pygame.transform.rotate(img, ang), (col * S, row * S))
pygame.image.save(
    preview, os.path.join(os.path.dirname(__file__), "..", "_sprite_preview.png")
)
print("saved _sprite_preview.png")
