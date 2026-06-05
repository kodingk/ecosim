import random
from typing import TYPE_CHECKING

import pygame

import sprites
from actions.age import Age
from actions.drain_energy import DrainEnergy
from actions.drain_water import DrainWater
from entity import Entity, EntityStatus

if TYPE_CHECKING:
    from action import Action
    from behavior import Behavior
    from world import WorldSnapshot


class Dinosaur(Entity):
    """
    공룡 베이스. 가변 위치(loc)·에너지·나이(age)를 소유한다.

    생활사(life history)를 나이로 모델링한다 — 미성숙 개체(age < maturity_age)는 번식하지
    못하고 작게 그려지며, 노쇠기(age ≥ senescence_age)에 들면 매 틱 확률적으로 죽는다(Age).
    이 둘이 출생/사망에 지연·기저사망률을 더해 개체수 과폭발을 인위적 캡 없이 감쇠한다.

    구체 종은 color/size/level/speed와 생활사 파라미터를 바꾸고 behaviors()를 구현한다.
    """

    color: tuple[int, int, int] = (200, 200, 200)
    size: int = 14
    level: int = 1  # 식물(0) 위에 그려진다
    sprite_name: str = "psittacosaurus"  # assets/sprites/{sprite_name}.png
    max_energy: float = 100.0
    drain_rate: float = 5.0  # 에너지/초
    # 생활사 — 나이 기반
    maturity_age: float = 15.0  # 이 나이 이상이어야 번식 가능(미성숙은 작게 렌더)
    senescence_age: float = 120.0  # 이 나이부터 노화사(확률적) 시작
    mortality_rate: float = 0.02  # 노쇠기 진입 후 초당 사망 확률(hazard)
    # 수분(목마름) — 에너지의 쌍둥이 드라이브. 완만하게(물 풍부·빠른 회복) 둬 탈수가 대량
    # 사망이 아니라 '물 찾기 행동'을 유발하게 한다. 0이 되면 탈수 스트레스로 에너지만 깎인다.
    max_water: float = 100.0
    drain_water_rate: float = 1.8  # 수분/초 감소(≈55초에 고갈)
    thirst_threshold: float = 45.0  # 이 미만이면 물을 찾아 나선다(SeekWater)
    drink_rate: float = 70.0  # 물가에서 수분/초 회복(빠른 보충)
    drink_distance: float = 52.0  # 이 거리 안의 물을 마실 수 있다(Drink)
    water_sight: float = 220.0  # 이 반경의 물을 감지(SeekWater)
    dehydration_stress: float = 3.0  # 수분 0일 때 추가 에너지/초(완만)
    # 낮·밤 — 완만. 주행성 기본(activity=daylight). 비활동기엔 Rest로 휴면 + 대사 절감.
    rest_metabolism: float = 0.5  # 완전 휴식 시 에너지 drain 배율(밤=0.5배로 보존)
    night_thirst: float = 0.4  # 한밤 갈증 배율(밤엔 기온 낮아 덜 마름)
    rest_threshold: float = 0.35  # activity가 이 미만이면 Rest가 휴면시킨다

    def __init__(self, loc: pygame.Vector2, rng: random.Random | None = None):
        self.loc = pygame.Vector2(loc)
        self.velocity = pygame.Vector2(
            0, 0
        )  # 직전 틱 이동 변위(set_location이 갱신). boids 정렬용.
        self.energy = self.max_energy / 2  # 절반에서 시작(처음엔 배고픔)
        self.water = self.max_water  # 수분 가득(수화 상태로 시작)
        self.age = 0.0
        self.last_breed_age = -1.0e9  # 마지막 번식 시점(나이). 번식 쿨다운 계산용.
        self._rng = rng or random.Random()  # 노화사 판정용 전용 스트림(순서 독립)

    def behaviors(self) -> list["Behavior"]:
        return []

    def activity(self, daylight: float) -> float:
        """현재 빛에서의 활동도 [0,1] (1=완전 활동, 0=완전 휴식). 주행성 기본 — 종이
        오버라이드한다(예: 포식자는 상시 활동 cathemeral → 밤에도 사냥)."""
        return daylight

    def passive_actions(self, dt: float, snapshot: "WorldSnapshot") -> list["Action"]:
        # 대사 휴식: 쉴수록(activity 낮음) 에너지 drain 절감. 기온: 한낮일수록 갈증↑.
        act = self.activity(snapshot.daylight)
        metabolism = self.rest_metabolism + (1.0 - self.rest_metabolism) * act
        thirst = self.night_thirst + (1.0 - self.night_thirst) * snapshot.daylight
        return [
            # 수분 먼저: 탈수 스트레스가 같은 틱 DrainEnergy의 사망 판정에 반영되도록.
            DrainWater(
                self, self.drain_water_rate * thirst * dt, self.dehydration_stress * dt
            ),
            DrainEnergy(self, self.drain_rate * metabolism * dt),
            Age(self, dt, self.senescence_age, self.mortality_rate, self._rng),
        ]

    @property
    def status(self) -> EntityStatus:
        return EntityStatus(
            loc=pygame.Vector2(self.loc),
            level=self.level,
            velocity=pygame.Vector2(self.velocity),
        )

    @status.setter
    def status(self, value: EntityStatus) -> None:
        self.loc = value.loc
        self.level = value.level

    def sprite(self) -> pygame.Surface:
        # 에셋 스프라이트를 나이 비례 크기로, velocity 방향으로 회전해 그린다.
        if self.maturity_age > 0:
            frac = min(1.0, 0.4 + 0.6 * (self.age / self.maturity_age))
        else:
            frac = 1.0
        px = int(self.size * frac * 2.9)
        if self.velocity.length_squared() > 0.01:
            angle = -self.velocity.as_polar()[1]
        else:
            angle = 0.0
        return sprites.sprite(self.sprite_name, px, angle)

    @classmethod
    def gen(cls, world_size: tuple[int, int], rng: random.Random) -> "Dinosaur":
        # 월드 안 임의 위치에 전용 rng를 들려 생성한다. 구체 종은 __init__(loc, rng)을
        # 공유하므로 Psittacosaurus·Deinonychus가 그대로 상속한다(중복 제거).
        loc = pygame.Vector2(
            rng.uniform(0, world_size[0]), rng.uniform(0, world_size[1])
        )
        return cls(loc, rng)
