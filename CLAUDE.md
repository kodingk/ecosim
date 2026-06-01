# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

백악기(Cretaceous) 생태계 시뮬레이터. pygame 기반의 entity–behavior–action 시뮬레이션 엔진이며, 현재 **엔진 골격**까지 구현되어 있고 구체 개체/행동/액션과 스폰은 아직 없다. 코드 주석/독스트링은 한국어다.

## Commands

의존성은 `requirements.txt`/`pyproject.toml` 없이 `.venv`에만 설치되어 있다 (Python 3.13, pygame 2.6.1만). 새 패키지는 `.venv/bin/pip install`로 넣는다.

```bash
source .venv/bin/activate     # 또는 아래 명령에 .venv/bin/ 접두사 사용
python main.py                # 시뮬레이터 실행 (반드시 repo 루트에서 — 평면 import)
ruff check .                  # 린트 (ruff 0.12.10, Homebrew 전역 설치 — venv에는 없음)
ruff format .                 # 포매팅
```

테스트 프레임워크는 없다 (pytest 미설치). 변경 검증은 `ruff` + `python main.py`. GUI 무한 루프라 자동 확인이 필요하면 `SDL_VIDEODRIVER=dummy`로 `World`/`Simulator`를 직접 한두 틱 돌려 상태를 단언하는 헤드리스 방식을 쓴다.

## Architecture

한 문장 요약: **엔티티는 자기 상태의 정본이고, 행동은 2단계(판단→적용)로 처리되어 순서 독립이며, 렌더링은 Simulator만 담당한다.** 전체 그림은 `world.py`(update 2단계)·`entity.py`·`behavior.py`·`action.py`·`simulator.py`(render)를 함께 읽어야 잡힌다.

### 2단계 틱 (가장 중요)
`Simulator.run`의 60 FPS 루프가 매 프레임 `World.update(dt)` → `Simulator.render()`를 호출한다. `World.update`는 두 단계다:

1. **판단(plan)** — `World.snapshot()`이 모든 엔티티의 `status()`를 떠 읽기 전용 `WorldSnapshot`을 만든다. 각 엔티티의 `behaviors()`(우선순위 내림차순)가 `plan(snapshot, dt)`를 호출하고, **첫 번째로 non-None `Action`을 반환한 behavior가 채택**된다(엔티티당 틱당 1액션). 이 단계는 **월드를 변경하지 않고** 동일 스냅샷만 읽으므로 **엔티티 처리 순서에 결과가 좌우되지 않는다.**
2. **적용(apply)** — 수집된 `Action`들의 `apply(world)`가 호출되어 실제 상태를 변경한다.

> 설계 이유: 즉시-변경 순차 루프는 결과가 우연한 순회 순서·선점 이득에 묶인다. 판단을 스냅샷 기반으로 떼어 그 결합을 끊었다. **충돌 해결**(예: 포식자 2 vs 먹이 1)은 apply 단계에 들어갈 **의도된 훅**이며 아직 미구현 — apply는 현재 수집 순서대로 도는데 독립적 액션엔 무관하지만, 충돌이 생기면 여기서 명시적으로 해결해야 한다.

### 상태의 정본 = 엔티티
각 엔티티가 자기 위치·레벨을 소유하고 `status() -> EntityStatus(loc, level)`로 보고한다. **`World`는 위치를 저장하지 않는다.** `status()`는 스냅샷으로 한 틱 보관되므로 **매번 새 값(loc 복사본)** 을 반환해야 한다 — 반환 객체를 in-place로 변형하면 스냅샷이 오염된다.

### 책임 분리 (SRP)
- **`World` = 모델**: 엔티티 보유 + `update`(시뮬레이션 진행). pygame을 import하지 않는다. 내부는 level 오름차순으로 유지되는 리스트(`bisect.insort`로 삽입) + `entities`(정렬 없이 추출만, 읽기 전용) / `spawn`(insort)·`despawn`(O(n) 제거) / `snapshot`.
- **`Simulator` = 오케스트레이션 + 표현**: 루프·화면 소유, `render()`가 월드 상태를 읽어 그린다. **렌더링은 여기 있다 (World가 아님).**

### `level`은 우선순위가 아니라 렌더 레이어
`level`이 클수록 **나중에 그려져 위에** 표시된다(예: 나는 익룡이 지상 개체 위로). `World.entities`는 **level 오름차순으로 유지되는 리스트**(spawn 때 `bisect.insort`로 제자리 삽입)라 정렬 없이 그대로 추출해 반환하고(동률은 `counter`로 tie-break — `Entity`끼리 비교 안 되게), `Simulator.render()`는 그 순서대로 그리기만 한다. 처리/포식 우선순위가 **아니며** update 순서는 level과 무관하다(update는 2단계라 순서 독립). 참고 ①: level은 사실상 렌더 전용 속성이라 이 정렬을 `World`에 둔 것은 약한 결합 — 의도된 선택. 참고 ②: level은 **spawn 시 정렬 키로 고정**되므로, 런타임에 level이 바뀌면 `despawn` 후 재`spawn`해야 순서가 유지된다.

### 확장 지점
- **새 생물**: `Entity` 하위 클래스 (`dinosaur/base.py`의 `Dinosaur` 스텁이 출발점). `behaviors()`·`status()`·`sprite()` 구현.
- **새 행동**: `Behavior` 하위 클래스. `plan`은 소유 엔티티 인자를 받지 않으므로 **생성 시 엔티티 참조를 캡처**하고, 월드 상태는 `snapshot`으로만 읽으며, 변경은 직접 하지 말고 `Action`으로 반환한다.
- **새 효과**: `Action` 하위 클래스, `apply(world)`에서 변경.

### Import 규칙
평면 top-level import라 **항상 repo 루트에서 실행**해야 한다. `dinosaur/`는 `__init__.py`가 없는 암묵적 namespace 패키지. 순환을 피하려고 `behavior.py`·`action.py`는 `World`·`WorldSnapshot`·`Action`을 `TYPE_CHECKING`에서만 import하고 문자열 어노테이션을 쓴다. 런타임 그래프: `simulator → world → {entity → behavior, action}`.

## 미구현 (베이스만 잡혀 있음 — 구체 콘텐츠는 의도적으로 보류)
- 구체 `Entity`/`Behavior`/`Action` 없음 (`Dinosaur`는 빈 스텁). `spawn()` 호출부도 없어 빈 세계가 돈다 — 실행하면 제목만 있는 검은 창.
- apply 단계의 충돌 해결 미구현 (위의 훅).
- 렌더링은 단색 배경 + 스프라이트 blit뿐 (카메라/스케일/에셋 로딩 없음).
