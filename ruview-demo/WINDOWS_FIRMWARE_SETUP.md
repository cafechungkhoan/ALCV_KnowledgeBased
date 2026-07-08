# Nạp firmware CSI cho ESP32-S3 trên Windows — từng bước

Mục tiêu: biến con ESP32-S3-DevKitC-1 "trắng" thành thiết bị đo CSI, in dữ liệu ra cổng USB
để `csi_bridge.py` đọc và đẩy vào dashboard.

> Làm 1 lần ~30–60 phút. Cần: board ESP32-S3-DevKitC-1 + **cáp USB-C truyền dữ liệu** (không phải cáp chỉ sạc).

---

## Bước 0 — Cắm đúng cổng USB
ESP32-S3-DevKitC-1 có **2 cổng USB-C**: một cái ghi **UART**, một cái ghi **USB**.
👉 Cắm vào cổng **UART** (dùng chip CP2102 để nạp + xem dữ liệu). Đây là cổng dùng cho mọi bước dưới.

## Bước 1 — Cài ESP-IDF (bộ công cụ của Espressif)
1. Vào https://dl.espressif.com/dl/esp-idf/ → tải **ESP-IDF Windows Installer** (Offline, bản v5.2 trở lên).
2. Chạy file cài. Cứ **Next** hết (nó tự cài Python, Git, trình biên dịch). Chọn cài bản ESP-IDF mới nhất.
3. Cài xong sẽ có shortcut trong Start Menu: **"ESP-IDF 5.x PowerShell"** (hoặc "ESP-IDF CMD").
   👉 **Từ giờ mọi lệnh idf.py phải gõ trong cửa sổ này** (không dùng CMD/PowerShell thường).

## Bước 2 — Driver USB + tìm cổng COM
1. Cắm ESP32 vào máy (cổng UART).
2. Mở **Device Manager** (bấm Start, gõ "Device Manager") → mục **Ports (COM & LPT)**.
3. Tìm dòng kiểu **"Silicon Labs CP210x ... (COM5)"** → nhớ số **COMx** (vd COM5).
   - Nếu không thấy / báo dấu chấm than vàng: cài driver **CP210x VCP** của Silicon Labs:
     https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers → tải bản Windows → cài → rút ra cắm lại.
   - (Một số bo dùng chip CH340 → cài driver CH340 thay vì CP210x.)

## Bước 3 — Tải mã firmware esp-csi
Mở **"ESP-IDF PowerShell"** (ở Bước 1) rồi gõ:
```powershell
cd %USERPROFILE%\Desktop
git clone https://github.com/espressif/esp-csi
cd esp-csi\examples\get-started\csi_recv
```

## Bước 4 — Chọn chip + khai báo WiFi
```powershell
idf.py set-target esp32s3
idf.py menuconfig
```
- Cửa sổ xanh hiện ra. Tìm mục có **SSID** và **Password** (thường trong **"Example Configuration"**
  hoặc **"Example Connection Configuration"**).
- Điền **tên WiFi nhà bạn** (SSID) và **mật khẩu**.
- Bấm **S** để lưu → **Enter** → **Q** để thoát.
> Dùng WiFi 2.4GHz (ESP32 không vào băng 5GHz). Tên/mật khẩu gõ chính xác.

## Bước 5 — Build + nạp + xem dữ liệu (thay COM5 bằng cổng của bạn)
```powershell
idf.py -p COM5 flash monitor
```
- Lần đầu build hơi lâu (vài phút). Nạp xong nó tự mở "monitor".
- **Thành công** khi thấy các dòng cuộn liên tục bắt đầu bằng:
  ```
  CSI_DATA,STA,...,[ 12 -3 5 7 ... ]
  ```
  👉 Đó là dữ liệu CSI thật! Firmware OK.
- Nhấn **Ctrl + ]** để thoát monitor (nhường cổng cho bridge ở Bước 7).

> Chưa thấy CSI_DATA mà chỉ thấy log WiFi? Cần có "lưu lượng mạng" để sinh CSI: mở CMD thường, gõ
> `ping <IP-của-ESP32> -t` (IP hiện trong log khi ESP32 vào WiFi). Có ping là CSI_DATA chạy.

## Bước 6 — Nếu nạp lỗi "Failed to connect"
- Giữ nút **BOOT** trên bo, bấm nhả **RST** (RESET) 1 cái, rồi thả **BOOT** → chạy lại lệnh flash.
- Kiểm tra đúng cổng COM (Bước 2) và đã cắm cổng **UART**.

## Bước 7 — Chuyển sang chạy bridge → dashboard
Đã thấy CSI_DATA và đã thoát monitor. Mở **PowerShell/CMD thường** (không phải ESP-IDF):
```powershell
pip install websockets pyserial
cd <thư-mục-repo>\ALCV_KnowledgeBased\ruview-demo\bridge
python csi_bridge.py --serial COM5 --baud 921600
```
Thấy `[ws] phát cho dashboard tại ws://localhost:8765` là OK.

Rồi mở dashboard **bản local** (cửa sổ khác):
```powershell
cd <thư-mục-repo>\ALCV_KnowledgeBased\ruview-demo
python -m http.server 8000
```
Vào trình duyệt `http://localhost:8000` → **📶 WiFi thật (Live CSI)** → `ws://localhost:8765` → **Kết nối**.
Ngồi yên trước ESP32 vài giây → nhịp thở/nhịp tim hiện lên = **dữ liệu WiFi THẬT**. 🎉

---

## Lỗi hay gặp trên Windows
| Lỗi | Cách xử lý |
|---|---|
| `idf.py` không nhận | Đang dùng CMD thường. Phải mở "ESP-IDF PowerShell" từ Start Menu. |
| Không thấy cổng COM | Cắm cổng UART; cài driver CP210x (Bước 2); đổi cáp (dùng cáp truyền dữ liệu). |
| `Failed to connect to ESP32` | Giữ BOOT + nhấn RST (Bước 6); đóng monitor/bridge đang chiếm cổng. |
| Thấy log nhưng không có CSI_DATA | Ping ESP32 để tạo lưu lượng (cuối Bước 5); kiểm tra WiFi 2.4GHz đúng mật khẩu. |
| Bridge báo cổng bận | Đóng cửa sổ ESP-IDF monitor (Ctrl+]) trước khi chạy bridge. |
| Trang online (netlify) không nối được | Dùng bản LOCAL `http://localhost:8000`, không dùng link https. |
