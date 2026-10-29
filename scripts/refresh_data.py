"""Làm mới dữ liệu dashboard (chạy bởi GitHub Actions lúc 12:00 giờ Việt Nam).

Trạng thái hiện tại: KHUNG chạy được, CHƯA có connector.
- Ghép ca, chia GMV theo ca, tạo kind, ghi data/*.json: đã viết và có test (--selftest).
- Lấy lịch Google Sheet, danh sách phiên và GMV theo thời gian của TikTok/Shopee: xem connectors.py,
  mỗi hàm đang ném NotConfigured. Khi chưa cấu hình, script thoát với mã 0 và KHÔNG đụng vào data/.

Cách dùng:
    python scripts/refresh_data.py            # chạy thật (cần connector)
    python scripts/refresh_data.py --selftest # chạy thử với dữ liệu giả, ghi vào thư mục tạm
"""
import json
import os
import statistics
import sys
import tempfile
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))
from slot_allocation import allocate, clip_to_live, resolve_overlaps  # noqa: E402

ICT = timezone(timedelta(hours=7))
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SALE_KIND = "Ngày sale lớn"
NORMAL_KIND = "Ngày thường"


def fm(ts):
    d = datetime.fromtimestamp(ts, ICT)
    return d.strftime("%H:%M")


def build_day(platform, channel_id, date, schedule, lives):
    """schedule: [(host, start_ts, end_ts)] theo thứ tự dòng; lives: [{start,end,official_gmv,confirmed_gmv,series}].
    Trả (session_row, slot_rows)."""
    st = min(l["start"] for l in lives)
    en = max(l["end"] for l in lives)
    gmv = sum(l["official_gmv"] for l in lives)
    sess = {"id": channel_id, "date": date, "start": fm(st), "end": fm(en), "hours": round((en - st) / 3600, 2),
            "gmv": round(gmv), "kind": NORMAL_KIND, "lives": len(lives)}
    if platform == "shopee":
        sess["gmv_confirmed"] = round(sum(l.get("confirmed_gmv", 0) for l in lives))
    rows = []
    if schedule:
        segs = clip_to_live(resolve_overlaps(schedule), st, en)
        for s, r in zip(segs, allocate(segs, lives)):
            if r["seconds"] < 600:  # bỏ ca live dưới 10 phút
                continue
            rows.append({"id": channel_id, "date": date, "host": s.host, "start": fm(s.start), "end": fm(s.end),
                         "hours": round(r["hours"], 2), "plan_hours": round((s.end - s.start) / 3600, 2),
                         "gmv": round(r["gmv"])})
    return sess, rows


def assign_kind(platform, sessions):
    """TikTok: phiên từ 1 tỷ. Shopee: từ 3 lần trung vị GMV phiên của từng ID."""
    if platform == "tiktok":
        for s in sessions:
            s["kind"] = SALE_KIND if s["gmv"] >= 1e9 else NORMAL_KIND
        return
    by = {}
    for s in sessions:
        by.setdefault(s["id"], []).append(s["gmv"])
    med = {k: statistics.median(v) for k, v in by.items()}
    for s in sessions:
        s["kind"] = SALE_KIND if s["gmv"] >= 3 * med[s["id"]] else NORMAL_KIND


def write_outputs(out_dir, platform, sessions, slots):
    assign_kind(platform, sessions)
    sessions.sort(key=lambda s: (s["id"], s["date"]))
    slots.sort(key=lambda o: (o["id"], o["date"], o["start"]))
    suffix = "" if platform == "tiktok" else "_shopee"
    for name, rows in (("sessions", sessions), ("slots", slots)):
        with open(os.path.join(out_dir, f"{name}{suffix}.json"), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, separators=(",", ":"))


def write_meta(out_dir, first_date, last_date):
    meta = {"updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "range": f"{first_date[8:]}/{first_date[5:7]}–{last_date[8:]}/{last_date[5:7]}/{last_date[:4]}"}
    with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)


def selftest():
    H = 3600
    base = datetime(2026, 8, 1, tzinfo=ICT).timestamp()
    sched = [("A", base + 9 * H, base + 18 * H), ("B", base + 13 * H, base + 15 * H), ("C", base + 15 * H, base + 17 * H)]
    series = [(base + h * H, base + (h + 1) * H, 10.0 + h) for h in range(9, 17)]
    lives = [{"start": base + 9 * H, "end": base + 17 * H, "official_gmv": 1000.0, "series": series}]
    sess, rows = build_day("tiktok", "@demo", "2026-08-01", sched, lives)
    assert abs(sum(r["gmv"] for r in rows) - 1000) <= 2, rows
    assert [r["host"] for r in rows] == ["A", "B", "C"], rows
    with tempfile.TemporaryDirectory() as d:
        write_outputs(d, "tiktok", [sess], rows)
        write_meta(d, "2026-08-01", "2026-08-01")
        assert json.load(open(os.path.join(d, "sessions.json")))[0]["id"] == "@demo"
    print("selftest OK")


def main():
    if "--selftest" in sys.argv:
        return selftest()
    from connectors import NotConfigured, load_all  # noqa: E402
    try:
        result = load_all()  # {"tiktok": {...}, "shopee": {...}} theo mô tả trong connectors.py
    except NotConfigured as e:
        print(f"[skip] Connector chưa cấu hình: {e}. Giữ nguyên data/ hiện có.")
        return
    first, last = None, None
    for platform, payload in result.items():
        sessions, slots = [], []
        for (cid, date), day in payload.items():
            s, r = build_day(platform, cid, date, day["schedule"], day["lives"])
            sessions.append(s)
            slots += r
            first = date if first is None or date < first else first
            last = date if last is None or date > last else last
        write_outputs(DATA_DIR, platform, sessions, slots)
    write_meta(DATA_DIR, first, last)
    print("Đã cập nhật data/")


if __name__ == "__main__":
    main()
