"""Nguồn dữ liệu. CHƯA CẤU HÌNH: mọi hàm đang ném NotConfigured.

load_all() phải trả:
{
  "tiktok": { (channel_id, "YYYY-MM-DD"): {"schedule": [(host, start_ts, end_ts), ...], "lives": [LIVE, ...]} },
  "shopee": { ... cùng dạng ... }
}
LIVE = {"start": ts, "end": ts, "official_gmv": VND, "confirmed_gmv": VND (chỉ Shopee), "series": [(t0, t1, value), ...]}

Gợi ý nguồn (cần bạn cấp quyền, mình chưa kiểm chứng):
- Lịch: Google Sheets API (service account được share quyền xem file lịch), tab "Ecom Host Livestream", cột ID/CHANNEL/DATE/START/END/Host_Name.
- TikTok: TikTok Shop Partner/Affiliate API chính thức (OAuth app). series = GMV theo mốc 15 phút.
- Shopee: Shopee Open Platform (hoặc xuất dữ liệu Seller Centre). series = doanh số đơn đã đặt theo phút.
Xem docs/DATA_REFRESH.md.
"""
import os


class NotConfigured(Exception):
    pass


def _need(*names):
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        raise NotConfigured("thiếu biến môi trường " + ", ".join(missing))


def fetch_schedule():
    _need("GOOGLE_SA_JSON", "SHEET_ID")
    raise NotConfigured("fetch_schedule chưa được viết")


def fetch_tiktok():
    _need("TIKTOK_APP_KEY", "TIKTOK_APP_SECRET", "TIKTOK_REFRESH_TOKEN")
    raise NotConfigured("fetch_tiktok chưa được viết")


def fetch_shopee():
    _need("SHOPEE_PARTNER_ID", "SHOPEE_PARTNER_KEY", "SHOPEE_REFRESH_TOKENS")
    raise NotConfigured("fetch_shopee chưa được viết")


def load_all():
    fetch_schedule()
    return {"tiktok": fetch_tiktok(), "shopee": fetch_shopee()}
