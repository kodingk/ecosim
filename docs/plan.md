# 구현 플랜 (TODO)

ecosim 구체 콘텐츠 구현 로드맵. 바닥부터 **수직 슬라이스**로 하나씩. 도메인은 [domain.md](domain.md), 엔진 계약은 [../CLAUDE.md](../CLAUDE.md) 참조.

## 현재 상태

- [x] 엔진 베이스 — 2단계 `update`(snapshot→plan→apply), `Entity`/`Behavior`/`Action` 계약, `bisect` 정렬 `entities`, `Simulator.render`
- [x] 생태 도메인 정의 (`domain.md`: 12종 + 보조 생물, 종간/동종간 상호작용)
- [ ] 구체 `Entity`/`Behavior`/`Action` — **여기부터**

## 먼저 정할 설계 결정 (3단계에서 필요)

- [ ] **A. 식물 = `Entity` vs 환경 필드?** — Entity면 일관·재사용(despawn/번식), 개체 수↑(성능). 환경 그리드면 가볍지만 별도 표현.
- [ ] **B. `status()`/`snapshot`이 무엇을 노출?** — 현재 `EntityStatus`는 `loc`·`level`뿐. 사냥·먹기에 상대의 **종류/생사/에너지**가 필요 → `EntityStatus` 확장 + 종 식별 방식(타입? 태그?).

> 1·2단계는 A/B 없이 진행 가능. 3단계 진입 전 확정.

## 빌드 순서

### 1. 생산자 Entity + 스폰 — *창에 첫 렌더*
- [ ] 식물 `Entity` 하위 클래스: `status()`(낮은 `level`), `sprite()`, `behaviors() = []`
- [ ] `main.py`에서 다수 `spawn`
- [ ] 실행 → 식물 렌더 + z-order 육안 확인

### 2. 초식 1종 + Wander + Move — *2단계 틱 라이브 검증*
- [ ] 초식 `Entity`(예: Psittacosaurus)
- [ ] `Wander` `Behavior` → `Move` `Action` 반환 (**시드 RNG**로 방향 — 결정성/재현성)
- [ ] `Move` `Action`: `apply`에서 위치 갱신 + 월드 경계 클램프
- [ ] 실행 → 이동 확인

### 3. 먹기 (초식 → 식물) — *상호작용 시작 (A/B 확정 후)*
- [ ] 에너지(포만) 상태 + 시간 감소(`dt`)
- [ ] `Graze` `Behavior`(스냅샷에서 근처 식물 탐색) + `Eat` `Action`(식물 `despawn`, 에너지 이전)

### 4. 육식 1종 + 사냥 — *포식 + 충돌 해결*
- [ ] 육식 `Entity`(예: Deinonychus)
- [ ] `Hunt` `Behavior`(스냅샷에서 먹이 탐색) + 공격/포식 `Action`
- [ ] **apply 단계 충돌 해결 훅** 구현 (포식자 2 ↔ 먹이 1)

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
