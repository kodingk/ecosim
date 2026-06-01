# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

백악기(Cretaceous) 생태계 시뮬레이터. pygame 기반의 entity–behavior 시뮬레이션 엔진이며, 현재 코어 골격만 잡혀 있고 렌더링·스폰·구체 개체는 아직 미구현 상태다. 코드 주석/독스트링은 한국어로 작성되어 있다.

## Commands

의존성은 `requirements.txt`/`pyproject.toml` 없이 `.venv`에만 설치되어 있다 (Python 3.13, pygame 2.6.1만 존재). 새 패키지는 `.venv/bin/pip install`로 넣고, 추적이 필요하면 직접 매니페스트를 만들어야 한다.

```bash
source .venv/bin/activate     # 또는 아래 명령에 .venv/bin/ 접두사 사용
python main.py                # 시뮬레이터 실행 (반드시 repo 루트에서 — 아래 import 규칙 참고)
ruff check .                  # 린트 (ruff 0.12.10, Homebrew 전역 설치 — venv에는 없음)
ruff format .                 # 포매팅
```

테스트 프레임워크는 설정되어 있지 않다 (pytest 미설치, 테스트 디렉터리 없음). 변경 검증의 유일한 자동 수단은 `ruff`와 `python main.py` 실행이다.

## Architecture

핵심은 **entity–behavior 분리(strategy 패턴)**다. 개체는 데이터 + 우선순위가 매겨진 behavior 목록일 뿐이고, 실제 동작 로직은 behavior가 `World`를 대상으로 수행한다. 전체 흐름을 이해하려면 `simulator.py` → `world.py` → `entity.py` → `behavior.py`를 함께 읽어야 한다.

**틱 파이프라인** — `main.py`가 `Simulator().run()`을 호출하면 60 FPS 루프가 돌며 매 프레임:
1. `dt = clock.tick(60) / 1000` (초 단위)
2. `World.update(dt)` 호출
3. 화면을 검게 채우고 `flip()` (개체 스프라이트는 그리지 않음 — 아래 미구현 항목 참고)

**우선순위 short-circuit** — `World.update`의 동작 규약이 가장 중요하다:
```python
for entity in self.entities:          # entities는 매 틱 dict 키의 스냅샷 리스트 (순회 중 map 변경 안전)
    for behavior in entity.behaviors():   # behaviors()는 우선순위 내림차순
        if behavior.act(self, dt):        # 처음 True를 반환한 behavior가 틱을 "소비"하고 break
            break
```
즉 `act`는 자신이 동작을 수행했으면 `True`(이하 우선순위 behavior 차단), 양보하려면 `False`를 반환한다. `behaviors()`는 반드시 높은 우선순위부터 정렬해 반환해야 한다.

**Behavior의 엔티티 바인딩** — `Behavior.act(self, world, dt)`는 **소유 엔티티를 인자로 받지 않는다**. 따라서 구체 behavior는 생성 시점에 자신의 엔티티 참조(및 필요한 상태)를 캡처해야 하며, 위치는 `world.entity_location_map`을 통해 읽고 쓴다. 이것이 behavior 확장의 핵심 계약이다.

**World = 공간 저장소** — `World`는 `entity_location_map: dict[Entity, pygame.Vector2]`로 개체의 위치를 보관하는 권위 있는 저장소다. `Entity`는 `id()` 기반 해시(`__hash__`)를 쓰므로 dict 키로 안전하게 쓰이고 동일 객체끼리만 같다. `spawn(entity, location)`으로 추가, `entities` 프로퍼티는 읽기 전용 스냅샷.

**Entity 계약** — `Entity`(ABC)를 상속하는 모든 개체는 세 메서드를 구현한다: `behaviors()`(우선순위 내림차순 리스트), `status() -> EntityStatus(loc, level)`, `sprite() -> pygame.Surface`. 새 생물은 `dinosaur/` 아래에 `Entity` 하위 클래스로 추가한다 (`dinosaur/base.py`의 `Dinosaur` 스텁이 시작점).

**Import 규칙** — 모든 모듈이 평면적(top-level) import를 쓴다 (`from entity import Entity`). 따라서 **항상 repo 루트에서 실행**해야 경로가 해석되며, `dinosaur/`에는 `__init__.py`가 없어 암묵적 namespace 패키지로 동작한다.

## 미구현 / 주의 (좋은 베이스를 잡으려면 먼저 채울 부분)

- **렌더링 미연결**: `Simulator.run`은 화면을 검게 칠하고 flip만 한다. `Entity.sprite()`는 어디서도 blit되지 않으므로, `entity_location_map`의 위치에 스프라이트를 그리는 로직이 필요하다.
- **스폰 없음**: `World.__init__`은 빈 map으로 시작하고 `spawn()`을 호출하는 곳이 없다. 현재는 빈 세계가 돈다.
- **위치 source-of-truth 이중화**: 권위 있는 위치는 `World.entity_location_map`(업데이트 루프·렌더링이 사용)지만 `EntityStatus`도 별도의 `loc`를 들고 있다. behavior 구현 시 둘을 동기화하거나 어느 쪽이 정본인지 명확히 정해야 한다.
- **구체 클래스 스텁**: `Dinosaur` 및 모든 구체 behavior는 아직 비어 있다.
