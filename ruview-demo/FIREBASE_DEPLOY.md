# Deploy dashboard lên Firebase Hosting

Đã chuẩn bị sẵn: `firebase.json` (trỏ publish vào `ruview-demo/`) và `.firebaserc` ở gốc repo.
Bạn chỉ cần đăng nhập Google + chọn project của mình (bước này **bắt buộc bạn tự làm** vì là tài khoản của bạn).

## Cách nhanh nhất (3 lệnh)
```bash
# 1) Cài CLI (nếu máy chưa có)
npm install -g firebase-tools

# 2) Đăng nhập Google (mở trình duyệt)
firebase login

# 3) Deploy — thay YOUR_PROJECT_ID bằng project Firebase của bạn
firebase deploy --only hosting --project YOUR_PROJECT_ID
```
Xong, Firebase in ra URL dạng `https://YOUR_PROJECT_ID.web.app`.

## Chưa có project Firebase?
1. Vào https://console.firebase.google.com → **Add project** (đặt tên tuỳ ý, tắt Analytics cho nhanh).
2. Lấy **Project ID** (dạng chữ thường, ví dụ `ruview-csi-demo`).
3. Dùng ID đó ở lệnh deploy phía trên. (Không cần bật gói trả phí — Hosting có bậc miễn phí.)

## Deploy không cần trình duyệt (máy chủ/CI)
```bash
# trên máy có trình duyệt, tạo token 1 lần:
firebase login:ci          # in ra 1 token dài
# rồi trên máy bất kỳ:
FIREBASE_TOKEN=<token> firebase deploy --only hosting --project YOUR_PROJECT_ID
```
> ⚠️ Token là bí mật — đừng dán vào chat hay commit lên Git.

## Cấu hình đã set sẵn (không cần chỉnh)
`firebase.json`:
- `public: "ruview-demo"` → phục vụ thẳng thư mục dashboard
- bỏ qua `bridge/**` và `*.md` (không đưa script Python / tài liệu lên hosting)

## Lưu ý dùng WiFi thật
Giống bản online khác: trang `https://…web.app` **không** kết nối được `ws://localhost` (mixed-content).
Muốn cắm ESP32 thật, mở **bản local** của dashboard (xem `HARDWARE_SETUP.md`). Bản Firebase để xem/demo (Mô phỏng) và chia sẻ.
