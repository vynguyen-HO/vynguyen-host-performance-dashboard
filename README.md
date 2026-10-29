# Host performance dashboard (TikTok & Shopee)

Dashboard tĩnh: tab **Tổng quan**, **TikTok**, **Shopee**. GMV chia theo ca của từng host.
Dữ liệu nằm trong `data/*.json`, trang `index.html` tự tải các file này.

## Cấu trúc

| Đường dẫn | Việc |
|---|---|
| `index.html` | Dashboard (d3 tải từ cdnjs, pin 7.9.0) |
| `data/` | `sessions.json`, `slots.json` (TikTok), `sessions_shopee.json`, `slots_shopee.json` (Shopee), `meta.json` |
| `scripts/slot_allocation.py` | Chia GMV phiên cho từng ca (có test) |
| `scripts/refresh_data.py`, `scripts/connectors.py` | Làm mới dữ liệu. **Connector chưa cấu hình**, xem `docs/DATA_REFRESH.md` |
| `.github/workflows/refresh-data.yml` | Cron 12:00 giờ Việt Nam (`0 5 * * *` UTC) |
| `docs/ACCESS.md` | Triển khai và phân quyền bằng Cloudflare Pages + Access |

## Trạng thái hiện tại

- Dữ liệu seed: 01/08–28/10/2026, 4 kênh TikTok và 3 shop Shopee (hannahteam1, 2, 3).
- Cron đã đặt lịch, nhưng bước lấy dữ liệu **chưa chạy thật** vì chưa có connector và key. Hiện nó chỉ chạy test rồi bỏ qua.
- Muốn cập nhật ngay: thay 4 file JSON trong `data/` (xem `docs/DATA_REFRESH.md`, cách C).

## Triển khai nhanh

1. Làm theo `docs/ACCESS.md` (Cloudflare Pages + Access). **Không bật GitHub Pages**, vì Pages không có phân quyền và site sẽ công khai.
2. Upload 4 file JSON dữ liệu vào `data/` nếu chưa có.
3. Mở link Pages, đăng nhập bằng email được cấp quyền.

## Chạy test local

```
cd scripts && python -m unittest test_slot_allocation
python scripts/refresh_data.py --selftest
```
