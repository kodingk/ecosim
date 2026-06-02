# 구현 플랜 (TODO)

ecosim 구체 콘텐츠 구현 로드맵. 바닥부터 **수직 슬라이스**로 하나씩. 도메인은 [domain.md](domain.md), 엔진 계약은 [../CLAUDE.md](../CLAUDE.md) 참조.

## 현재 상태

- [x] 엔진 베이스 — 2단계 `update`(snapshot→plan→apply), `Entity`/`Behavior`/`Action` 계약, `bisect` 정렬 `entities`, `Simulator.render`
- [x] 생태 도메인 정의 (`domain.md`: 12종 + 보조 생물, 종간/동종간 상호작용)
- [ ] 구체 `Entity`/`Behavior`/`Action` — **진행 중**: 1·2단계 완료, 3단계부터

## 먼저 정할 설계 결정 (3단계에서 필요)

- [x] **A. 식물 = `Entity`** — 웬만하면 전부 Entity로 통일. UI/통계 패널도 Entity 지향(추후): `level`=HUD z-order, `plan(snapshot)`=통계 집계. ⚠️ model↔view 경계·screen좌표는 **패널 만들 때** 정리(생태 World 말고 Simulator 오버레이 권장).
- [x] **B. 종 식별 = 클래스 주입 + `isinstance`** (`kind` 태그 X) — behavior에 `target_classes` 주입, `WorldSnapshot.query_entities_within`로 근처 탐색. `EntityStatus`는 `loc`·`level` 유지(자기 에너지는 엔티티 내부; 먹이의 생사/에너지 노출은 필요 시 4단계).

## 빌드 순서

### 1. 생산자 Entity + 스폰 — *창에 첫 렌더* ✅
- [x] 식물 `Entity` 하위 클래스 — `plant/base.py` (`Plant`: 낮은 `level`, `behaviors()=[]`)
- [x] `main.py`에서 다수 `spawn` (시드 고정 40개)
- [x] 식물 렌더 + z-order (헤드리스 픽셀 단언으로 검증)

### 2. 초식 1종 + Wander + Move — *2단계 틱 라이브 검증* ✅
- [x] 초식 `Entity` — `dinosaur/base.py`(`Dinosaur` 베이스) + `dinosaur/psittacosaurus.py` (level 1)
- [x] `Wander` `Behavior`(`behaviors/`) → `Move` `Action` (엔티티 전용 시드 RNG — 순서 독립)
- [x] `Move` `Action`(`actions/`): `apply`에서 위치 갱신 + 경계 클램프 (`World.size` 추가)
- [x] 이동·클램프·결정성·z-order 검증

### 3. 먹기 (초식 → 식물) — *상호작용 시작* ✅
- [x] `Dinosaur.energy`(포만) — 절반에서 시작, 포만이면 안 먹음 (시간 소진은 5단계로)
- [x] `Eat` `Behavior`(`target_classes` 주입 + isinstance) + `Consume` `Action`(식물 `despawn` + 에너지↑)
- [x] `WorldSnapshot.query_entities_within`(근처 탐색, 가까운 순) + 식물 1 : 초식 2 충돌 가드

### 4. 육식 1종 + 사냥 — *포식 + 충돌 해결* ✅
- [x] 육식 `Entity` — `dinosaur/deinonychus.py` (level 2, 빠름; `target_classes=[Psittacosaurus]`)
- [x] `Hunt` `Behavior`(추격+사냥) — 기존 `Move`(seek)·`Consume`(kill) 재사용
- [x] **apply 단계 충돌 해결 훅** — `Action.claim()`/`contest_key()` + `World._resolve`, **가까운 포식자 우선**

### 5. 죽음·번식 — *개체군 동역학 / 사이클 닫기*
- [ ] 에너지 0 / 노화 → `Die` `Action`(despawn)
- [ ] 번식 조건 → `Reproduce` `Action`(자식 `spawn`), r/K 전략 반영
- [ ] 생산자↔초식↔육식 진동 관찰

## 가로지르는 원칙

- **결정성**: 무작위(Wander·tie-break)는 **시드 RNG**로 — 순서 독립·재현성 유지
- **`level` = 렌더 z-order** (익룡 위 / 식물·소형 아래). 트로픽 단계 아님
- **합성 군집**: 비동소 종을 동시 스폰하지 말 것 (domain §7.7 대역 매핑)
- **풀 없음**: 지표 먹이는 양치류·속새·저성 속씨식물
- **검증**: `ruff` + `SDL_VIDEODRIVER=dummy` 헤드리스 한두 틱 단언 (GUI 무한 루프 회피)
