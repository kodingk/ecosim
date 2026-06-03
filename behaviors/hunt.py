from typing import TYPE_CHECKING

from actions.consume import Consume
from actions.move import Move
from behavior import Behavior

if TYPE_CHECKING:
    from action import Action
    from dinosaur.base import Dinosaur
    from entity import Entity
    from world import WorldSnapshot


class Hunt(Behavior):
    """
    sight 이내에서 target_classes에 해당하는 가장 가까운 먹이를 쫓는다.

    attack_distance 안에 들면 잡아먹고(`Consume`), 아니면 먹이 쪽으로 이동(`Move`)한다.
    먹이 '종류'는 클래스로 주입(예: [Psittacosaurus])하므로 동족은 쫓지 않는다.

    **추격 스태미나(give-up)** — max_chase초 동안 못 잡으면 지쳐 추격을 포기하고 rest_duration
    초간 쉰다(이때 None을 반환해 배회로 넘어간다). 이 한계가 결정적이다: 포식자(90)가 도주
    피식자(80)보다 빨라 *순수 footrace로는 결국 항상 잡지만*, 스태미나 상한이 피식자에게
    **탈출 창**을 보장해 포식자가 먹이를 절대 0으로 전멸시키지 못하게 한다(구조적 공존).
    실제 포식자의 사냥 성공률이 낮은 것도 이 유한한 추격 지구력 때문이다.

    추격 상태(_chase_time/_rest_time)는 behavior의 사유 메모리라(월드 아님) 갱신해도 2단계
    판단 규약을 어기지 않으며, 자기 이력에만 의존하므로 처리 순서와 무관하다.
    """

    def __init__(
        self,
        actor: "Dinosaur",
        target_classes: list[type["Entity"]],
        sight: float,
        attack_distance: float,
        speed: float,
        gain: float,
        hunt_hunger: float | None = None,
        max_chase: float = 8.0,
        rest_duration: float = 3.0,
    ):
        self._actor = actor
        self._target_classes = tuple(target_classes)
        self._sight = sight
        self._attack_distance = attack_distance
        self._speed = speed
        self._gain = gain
        # 이 에너지 이상이면 사냥하지 않는다(포만). None이면 max_energy(거의 항상 사냥).
        self._hunt_hunger = hunt_hunger
        self._max_chase = max_chase
        self._rest_duration = rest_duration
        self._chase_time = 0.0
        self._rest_time = 0.0

    def plan(self, snapshot: "WorldSnapshot", dt: float) -> "Action | None":
        # 지쳐 쉬는 중이면 사냥하지 않는다.
        if self._rest_time > 0.0:
            self._rest_time -= dt
            return None
        # 포만(Holling 기능반응): 배부르면 사냥을 멈춘다 → 한 번 잡은 포식자는 소화하는 동안
        # 사냥 안 함 → 개체당 포식률이 먹이 밀도와 무관하게 포만으로 상한이 걸린다(안정자).
        satiation = (
            self._hunt_hunger
            if self._hunt_hunger is not None
            else self._actor.max_energy
        )
        if self._actor.energy >= satiation:
            self._chase_time = 0.0
            return None
        prey = next(
            (
                entity
                for entity in snapshot.query_entities_within(self._actor, self._sight)
                if isinstance(entity, self._target_classes)
            ),
            None,
        )
        if prey is None:
            self._chase_time = 0.0  # 사냥감 없음 → 추격 리셋
            return None
        actor_loc = snapshot.statuses[self._actor].loc
        prey_loc = snapshot.statuses[prey].loc
        if actor_loc.distance_to(prey_loc) <= self._attack_distance:
            self._chase_time = 0.0  # 포획 성공 → 리셋
            return Consume(self._actor, prey, self._gain)
        # 추격 중 — 스태미나 소진 체크
        self._chase_time += dt
        if self._chase_time >= self._max_chase:
            self._chase_time = 0.0
            self._rest_time = self._rest_duration  # 지쳐 포기하고 휴식
            return None
        direction = prey_loc - actor_loc
        if direction.length() > 0:
            direction = direction.normalize()
        return Move(self._actor, direction * self._speed * dt)
