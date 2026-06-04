class SpatialGrid:
    """
    균일 격자 공간 해시 — 위치 기반 이웃 후보를 평균 O(1)로 좁힌다.

    엔티티를 cell_size 격자 칸에 담고, nearby(loc, radius)로 그 반경에 닿을 *가능성*이 있는
    후보만 돌려준다(격자 단위 과대추정 — 반경 내 항목은 빠짐없이 포함하되 약간 더 줄 수 있다).
    정확한 거리 필터는 호출자(WorldSnapshot)가 한다.

    종·엔티티에 의존하지 않는 일반 자료구조다(임의 객체 + 위치). distance 이내 항목이
    누락되지 않도록 span = floor(radius/cell)+1 칸까지 살핀다.
    """

    def __init__(self, cell_size: float):
        self._cs = cell_size
        self._cells: dict[tuple[int, int], list] = {}

    def _cell(self, loc) -> tuple[int, int]:
        cs = self._cs
        return (int(loc[0] // cs), int(loc[1] // cs))

    def insert(self, item, loc) -> None:
        self._cells.setdefault(self._cell(loc), []).append(item)

    def nearby(self, loc, radius: float) -> list:
        """loc 기준 radius 안일 *가능성*이 있는 후보들. 반경 내 항목은 빠짐없이 포함된다."""
        cs = self._cs
        cx, cy = self._cell(loc)
        span = int(radius // cs) + 1  # 반경에 닿는 칸을 모두 덮는다(누락 없음)
        cells = self._cells
        out: list = []
        for gx in range(cx - span, cx + span + 1):
            for gy in range(cy - span, cy + span + 1):
                bucket = cells.get((gx, gy))
                if bucket:
                    out.extend(bucket)
        return out
