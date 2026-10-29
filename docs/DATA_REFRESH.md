# Cập nhật dữ liệu hằng ngày

Cron trong `.github/workflows/refresh-data.yml` chạy 12:00 trưa giờ Việt Nam mỗi ngày. Bước lấy dữ liệu cần connector, hiện **chưa có**.

## Vì sao chưa chạy được thật

Dữ liệu TikTok Partner Center và Shopee Seller Centre lúc dựng dashboard được lấy qua trình duyệt đã đăng nhập. GitHub Actions chạy trên máy chủ không có phiên đăng nhập đó. Lưu mật khẩu hoặc cookie đăng nhập vào secrets không nên làm (hết hạn, 2FA, rủi ro vi phạm điều khoản).

## Ba cách

**A. API chính thức (nên dùng để chạy tự động hoàn toàn)**
- TikTok: đăng ký app trên TikTok Shop Partner/Affiliate, xin quyền đọc dữ liệu live, lấy `APP_KEY`, `APP_SECRET`, `REFRESH_TOKEN`.
- Shopee: đăng ký Shopee Open Platform, ủy quyền từng shop (hannahteam1, 2, 3), lấy `PARTNER_ID`, `PARTNER_KEY`, refresh token của từng shop.
- Lịch: tạo service account Google, share quyền xem file lịch cho email của service account, lưu JSON vào secret `GOOGLE_SA_JSON`, id file vào `SHEET_ID`.
- Thêm các secret trong repo → Settings → Secrets and variables → Actions, rồi viết các hàm trong `scripts/connectors.py` (mô tả đầu ra ở đầu file). Phần ghép ca và chia GMV đã có sẵn và có test.

**B. Tác vụ định kỳ trên máy có Chrome đã đăng nhập**
Một tác vụ chạy 12:00 mỗi ngày trên máy của bạn lấy dữ liệu như cách đã làm khi dựng dashboard, ghi vào `data/` rồi push lên repo. Cần máy bật và các tài khoản đang đăng nhập. Tính năng đặt lịch của Claude bạn kiểm tra tại https://support.claude.com.

**C. Thủ công**
GitHub → repo → thư mục `data` → **Add file** → **Upload files**, kéo 4 file JSON mới vào, Commit. Cloudflare Pages tự cập nhật sau vài phút.

## Định dạng file

Giống `data/*.json` hiện có. `sessions*.json`: `id, date, start, end, hours, gmv, kind, lives` (Shopee thêm `gmv_confirmed`). `slots*.json`: `id, date, host, start, end, hours, plan_hours, gmv`. `meta.json`: `updated_at` (UTC ISO), `range`.
