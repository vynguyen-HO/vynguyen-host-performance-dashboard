"""Chia GMV của một phiên live cho từng ca host.

Logic giống bản đã dùng để dựng dashboard:
1. resolve_overlaps: ô HOST trong lịch đôi khi ghi host dài rồi các host chen vào bên dưới.
   Dòng ghi SAU cắt phần trùng của dòng ghi TRƯỚC.
2. clip_to_live: ca đầu bắt đầu khi phiên lên sóng; ca cuối kéo tới giờ tắt nếu lệch dưới 30 phút.
3. allocate: GMV ca = tổng GMV các mốc thời gian nằm trong ca (chia theo phần thời gian chồng lấn),
   rồi nâng tỷ lệ để tổng các ca khớp GMV chính thức của phiên.

Thời gian tính bằng giây (epoch). series là list (t_start, t_end, value).
"""
from dataclasses import dataclass


@dataclass
class Slot:
    host: str
    start: float
    end: float


def resolve_overlaps(slots):
    """slots theo đúng thứ tự dòng trong ô HOST. Dòng sau ưu tiên hơn dòng trước."""
    segs = []
    for host, a, b in slots:
        out = []
        for s in segs:
            if s.end <= a or s.start >= b:
                out.append(s)
            else:
                if s.start < a:
                    out.append(Slot(s.host, s.start, a))
                if s.end > b:
                    out.append(Slot(s.host, b, s.end))
        out.append(Slot(host, a, b))
        segs = out
    return sorted(segs, key=lambda s: s.start)


def clip_to_live(slots, live_start, live_end, tolerance=1800):
    if not slots:
        return slots
    slots = [Slot(s.host, s.start, s.end) for s in slots]
    slots[0].start = min(slots[0].start, live_start)
    if abs(slots[-1].end - live_end) < tolerance:
        slots[-1].end = max(slots[-1].end, live_end)
    return slots


def _overlap(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))


def allocate(slots, lives):
    """lives: list dict {start, end, official_gmv, series:[(t0,t1,value)]}.
    Trả về list dict {host, start, end, hours, gmv} theo thứ tự ca (đã nâng tỷ lệ)."""
    res = [{"host": s.host, "start": s.start, "end": s.end, "seconds": 0.0, "gmv": 0.0} for s in slots]
    for lv in lives:
        total = sum(v for _, _, v in lv["series"])
        scale = lv["official_gmv"] / total if total > 0 else 0.0
        for i, s in enumerate(slots):
            a, b = max(s.start, lv["start"]), min(s.end, lv["end"])
            if b <= a:
                continue
            res[i]["seconds"] += b - a
            g = 0.0
            for t0, t1, v in lv["series"]:
                o = _overlap(t0, t1, a, b)
                if o > 0:
                    g += v * o / (t1 - t0)
            res[i]["gmv"] += g * scale
    for r in res:
        r["hours"] = r["seconds"] / 3600.0
    return res
