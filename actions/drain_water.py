from typing import TYPE_CHECKING

from action import Action

if TYPE_CHECKING:
    from dinosaur.base import Dinosaur
    from world import World


class DrainWater(Action):
    """
    매 틱 수분(water)을 소모한다. DrainEnergy(에너지)의 쌍둥이 수동 행동이다.

    물은 직접 죽이지 않는다(완만한 설계) — 수분이 0이 되면 **탈수 스트레스**로 에너지를
    stress만큼 추가 소모시킬 뿐이고, 실제 사망은 기존 에너지 고갈 경로(DrainEnergy)가
    처리한다. 즉 탈수는 굶주림을 가속하는 음성 압력이지 별도의 대량 사망 벡터가 아니다 →
    어렵게 맞춘 개체수 균형을 깨지 않으면서도 '목마름'이 생존에 의미를 갖게 한다.
    """

    def __init__(self, actor: "Dinosaur", amount: float, stress: float):
        self._actor = actor
        self._amount = amount
        self._stress = stress

    def apply(self, world: "World") -> None:
        self._actor.water = max(0.0, self._actor.water - self._amount)
        if self._actor.water <= 0.0:
            # 탈수: 에너지를 추가 소모(사망 판정은 같은 틱 DrainEnergy가 한다).
            self._actor.energy = max(0.0, self._actor.energy - self._stress)
