# Triển khai và phân quyền

Dữ liệu gồm GMV và tên host nên **không dùng GitHub Pages** (site công khai cho ai có link, kể cả khi repo private).
Dùng **Cloudflare Pages** (lấy code từ repo private) và **Cloudflare Access** (chặn đăng nhập theo email).

## Email được cấp quyền

- vy.nguyen@hannaholala.com
- tu.bui@hannaholala.com
- lanh.do@hannaholala.com
- vy.le@hannaholala.com
- hrteam@hannaholala.com

Hiện cả 5 người cùng một quyền (xem tất cả tab). Muốn chia quyền, tạo thêm policy theo mục "Chia quyền" bên dưới.

## Bước 1: Cloudflare Pages

1. Đăng nhập Cloudflare (tạo tài khoản miễn phí nếu chưa có) → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**.
2. Cài Cloudflare Pages GitHub App cho tài khoản `vynguyen-HO`, chỉ chọn repo `host-performance-dashboard`.
3. Cấu hình build: Framework preset **None**, Build command để trống, Build output directory `/` (hoặc để trống).
4. Deploy. Bạn nhận link dạng `https://host-performance-dashboard.pages.dev`.

## Bước 2: Cloudflare Access (Zero Trust)

1. **Zero Trust** → **Access** → **Applications** → **Add an application** → **Self-hosted**.
2. Application domain: `host-performance-dashboard.pages.dev`. Thêm một domain nữa: `*.host-performance-dashboard.pages.dev` (các bản preview của Pages có địa chỉ riêng và sẽ không được bảo vệ nếu thiếu dòng này).
3. Identity providers: chọn **One-time PIN** (mã gửi qua email, không cần cấu hình Google). Có thể thêm Google nếu công ty dùng Google Workspace.
4. Tạo policy **Allow** với Include → **Emails**, dán 5 email ở trên.
5. Lưu. Kiểm tra bằng cửa sổ ẩn danh: người ngoài danh sách không nhận được mã.

Gói miễn phí của Zero Trust cho tối đa 50 người dùng. Gói có thể thay đổi, kiểm tra trên trang giá của Cloudflare.

## Thêm hoặc bớt người

Zero Trust → Access → Applications → chọn ứng dụng → Policies → sửa danh sách email. Có hiệu lực ngay, và người bị bớt mất quyền khi phiên hết hạn (chỉnh Session duration trong ứng dụng, ví dụ 8 giờ).

## Chia quyền (tùy chọn)

Access phân quyền theo đường dẫn, không theo tab trong trang. Cách làm: tách các trang chi tiết thành đường dẫn riêng (ví dụ `/detail/`) rồi tạo thêm một ứng dụng Access cho đường dẫn đó với danh sách email hẹp hơn. Cần chỉnh lại `index.html`, báo mình nếu muốn làm.

## Chặn lộ dữ liệu

- Repo luôn để **private**. Không dán link raw.githubusercontent.com ra ngoài.
- `index.html` có `noindex` để công cụ tìm kiếm không lập chỉ mục.
