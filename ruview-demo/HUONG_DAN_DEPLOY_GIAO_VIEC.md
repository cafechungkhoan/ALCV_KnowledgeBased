# Hướng dẫn deploy dashboard RuView lên Firebase — Bản giao việc

> **Mục tiêu:** đưa dashboard (thư mục `ruview-demo/`) lên mạng, ra một đường link công khai dạng
> `https://<ten-project>.web.app` để ai cũng mở xem được.
>
> **Người thực hiện cần:** biết mở Terminal/CMD và copy-paste lệnh. Không cần biết lập trình.
> **Thời gian:** ~10–15 phút. **Chi phí:** miễn phí.

Tài khoản/thông tin cần chuẩn bị trước:
- 1 tài khoản **Google** (để đăng nhập Firebase).
- Quyền truy cập repo Git: `cafechungkhoan/ALCV_KnowledgeBased`, nhánh `claude/csi-ruview-library-vfzfwn`.

---

## PHẦN A — Cài công cụ (làm 1 lần)

### A1. Cài Node.js (kèm npm)
- Vào https://nodejs.org → tải bản **LTS** → cài như phần mềm bình thường.
- Kiểm tra: mở **Terminal** (macOS/Linux) hoặc **Command Prompt / PowerShell** (Windows), gõ:
  ```bash
  node -v
  npm -v
  ```
  Thấy 2 dòng số phiên bản (vd `v20.x` và `10.x`) là OK.

### A2. Cài Firebase CLI
```bash
npm install -g firebase-tools
```
Kiểm tra:
```bash
firebase --version
```
Thấy số phiên bản (vd `13.x` hoặc `15.x`) là OK.
> Windows nếu báo lỗi quyền: mở **PowerShell (Run as Administrator)** rồi chạy lại.

---

## PHẦN B — Tạo project Firebase (làm 1 lần)

1. Vào https://console.firebase.google.com (đăng nhập bằng tài khoản Google).
2. Bấm **Add project** (Thêm dự án).
3. Đặt tên, ví dụ `ruview-csi-demo` → **Continue**.
4. Trang hỏi Google Analytics → **tắt** (gạt off) cho nhanh → **Create project**.
5. Đợi tạo xong → **Continue**.
6. **Ghi lại Project ID**: bấm ⚙️ (Project settings) ở góc trên trái → xem dòng **Project ID**
   (chữ thường, ví dụ `ruview-csi-demo`). **Sẽ dùng ở Phần D.**

> Không cần thêm thẻ tín dụng. Firebase Hosting có bậc miễn phí.

---

## PHẦN C — Lấy mã nguồn về máy

Mở Terminal/CMD, chạy (thay đường dẫn nếu muốn để chỗ khác):
```bash
git clone https://github.com/cafechungkhoan/ALCV_KnowledgeBased
cd ALCV_KnowledgeBased
git checkout claude/csi-ruview-library-vfzfwn
```
> Nếu repo là **private**, cần đăng nhập Git (GitHub) khi clone. Có thể tải ZIP từ GitHub nếu không quen git:
> vào trang repo → nút **Code → Download ZIP** → giải nén → mở Terminal trong thư mục đó.

Kiểm tra đang đúng thư mục: chạy `ls` (Windows: `dir`) phải thấy các file `firebase.json`, `.firebaserc`, và thư mục `ruview-demo`.

---

## PHẦN D — Deploy lên Firebase

Vẫn ở trong thư mục `ALCV_KnowledgeBased`, chạy 2 lệnh:

### D1. Đăng nhập Google
```bash
firebase login
```
- Trình duyệt tự mở → chọn tài khoản Google (cùng tài khoản đã tạo project ở Phần B) → **Allow**.
- Terminal báo `Success! Logged in as <email>` là xong.
> Máy chủ không có trình duyệt? Dùng `firebase login --no-localhost` và làm theo hướng dẫn dán mã.

### D2. Deploy (thay `TEN-PROJECT-ID` bằng Project ID ghi ở bước B6)
```bash
firebase deploy --only hosting --project TEN-PROJECT-ID
```

Kết thúc, Terminal in ra dòng:
```
✔  Hosting URL: https://TEN-PROJECT-ID.web.app
```
**Đó là link cần lấy.** Mở thử trên trình duyệt — dashboard hiện lên là **THÀNH CÔNG**. ✅

Gửi lại đường link `https://TEN-PROJECT-ID.web.app` cho người giao việc.

---

## PHẦN E — Kiểm tra & xử lý lỗi thường gặp

| Báo lỗi / hiện tượng | Cách xử lý |
|---|---|
| `firebase: command not found` | Chưa cài CLI hoặc chưa mở lại Terminal. Chạy lại Phần A2, mở Terminal mới. |
| `Failed to authenticate` | Chưa `firebase login`, hoặc login sai tài khoản. Chạy `firebase logout` rồi `firebase login` lại. |
| `Project TEN-PROJECT-ID not found` | Sai Project ID (phải chữ thường, đúng ID ở bước B6), hoặc tài khoản login khác chủ project. |
| Deploy xong nhưng trang trắng | Chạy sai thư mục. Phải chạy lệnh deploy ở thư mục **gốc** repo (nơi có `firebase.json`), không phải trong `ruview-demo`. |
| `Permission denied` (npm, Windows) | Mở PowerShell **Run as Administrator** rồi cài lại. |
| Muốn đổi nội dung rồi deploy lại | Sửa file trong `ruview-demo/` → chạy lại lệnh D2. |

---

## (TUỲ CHỌN) PHẦN F — Chạy dữ liệu WiFi THẬT bằng ESP32
Trang deploy online chỉ chạy chế độ **Mô phỏng**. Muốn dùng **WiFi thật** cần phần cứng ESP32 và
chạy bản dashboard cục bộ — xem hướng dẫn riêng trong `ruview-demo/HARDWARE_SETUP.md`.

---

### Tóm tắt cực gọn (cho người đã quen)
```bash
npm install -g firebase-tools
git clone https://github.com/cafechungkhoan/ALCV_KnowledgeBased && cd ALCV_KnowledgeBased
git checkout claude/csi-ruview-library-vfzfwn
firebase login
firebase deploy --only hosting --project TEN-PROJECT-ID   # tạo project ở console.firebase.google.com trước
```
Lấy link `https://TEN-PROJECT-ID.web.app`.
