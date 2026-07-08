# Cắm WiFi thật vào dashboard — Hướng dẫn từng bước

Dashboard có 2 nguồn dữ liệu:
- **🧪 Mô phỏng** — chạy ngay, không cần gì (để xem/demo).
- **📶 WiFi thật (Live CSI)** — nhận dữ liệu CSI thật từ ESP32 qua WebSocket.

Để chạy **WiFi thật**, bạn cần 1 con **ESP32** (khoảng 80–200k VNĐ) và làm theo 4 bước dưới.

---

## Bạn cần mua gì
| Món | Giá tham khảo | Ghi chú |
|---|---|---|
| **ESP32-S3** (hoặc ESP32-C6 / ESP32 DevKit) | ~80–200k VNĐ | Bo mạch có WiFi + cổng USB. Mua ở Shopee/Lazada/hshop.vn |
| Cáp USB-C (hoặc micro-USB tuỳ bo) | có sẵn | để cắm vào máy tính |

> Chỉ cần **1 con** là chạy được (dùng chính router WiFi nhà bạn làm nguồn phát sóng).
> Có 2 con thì tách hẳn máy phát / máy thu, tín hiệu ổn định hơn.

---

## Bước 1 — Cài công cụ trên máy tính
```bash
# Cài Python 3.10+ rồi:
pip install esptool websockets pyserial
```

## Bước 2 — Nạp firmware CSI cho ESP32
Dùng firmware CSI chính thức của Espressif (đơn giản, đã in sẵn CSI ra cổng USB):
```bash
git clone https://github.com/espressif/esp-csi
cd esp-csi/examples/get-started/csi_recv
# Cài ESP-IDF theo hướng dẫn của repo, rồi:
idf.py set-target esp32s3      # đổi theo bo của bạn: esp32 / esp32s3 / esp32c6
idf.py flash monitor           # nạp + xem CSI in ra
```
Khi chạy `monitor`, bạn sẽ thấy các dòng bắt đầu bằng `CSI_DATA,...,[ ... ]` cuộn liên tục → **firmware OK**. Nhấn `Ctrl+]` để thoát monitor (nhường cổng cho bridge ở bước 3).

> **Không muốn cài ESP-IDF?** Có thể dùng firmware RuView ở `firmware/` trong repo gốc
> [ruvnet/RuView](https://github.com/ruvnet/RuView) — nó gửi CSI qua **UDP**; khi đó chạy bridge
> ở Bước 3 bằng `--udp 5005` thay vì `--serial`.

## Bước 3 — Chạy bridge (ESP32 → dashboard)
Bridge nằm sẵn trong `ruview-demo/bridge/csi_bridge.py`:
```bash
cd ruview-demo/bridge

# ESP32 cắm USB (đường phổ biến nhất):
python csi_bridge.py --serial /dev/ttyUSB0 --baud 921600
#   Windows: --serial COM7   |   macOS: --serial /dev/tty.usbserial-XXXX

# hoặc nếu firmware gửi UDP:
python csi_bridge.py --udp 5005
```
Thấy dòng `[ws] phát cho dashboard tại ws://localhost:8765` là bridge đã chạy.

> Tìm tên cổng serial: Linux `ls /dev/ttyUSB* /dev/ttyACM*` · Windows xem Device Manager (COMx) · macOS `ls /dev/tty.*`

## Bước 4 — Nối dashboard với dữ liệu thật
1. Mở dashboard (**mở file `ruview-demo/index.html` trên MÁY đang chạy bridge** — xem lưu ý bên dưới).
2. Bấm **📶 WiFi thật (Live CSI)**.
3. URL để mặc định `ws://localhost:8765` → bấm **Kết nối**.
4. Trạng thái chuyển **"đã kết nối"** (xanh) → bản đồ nhiệt, sóng nhịp thở/tim và BPM giờ là **dữ liệu WiFi thật**.

Thử: ngồi yên trước ESP32 vài giây → nhịp thở/nhịp tim hiện lên; đứng dậy đi lại → năng lượng chuyển động tăng vọt.

---

## ⚠️ Lưu ý quan trọng về "mở dashboard online vs. local"
- Trang **deploy online (https://…)** **không** kết nối được `ws://localhost` (trình duyệt chặn mixed-content).
- Vì vậy khi dùng **WiFi thật**, hãy mở **bản local** của dashboard (mở trực tiếp file `index.html`,
  hoặc `python -m http.server` trong thư mục `ruview-demo/` rồi vào `http://localhost:8000`).
- Bản deploy online phù hợp để **xem/demo (chế độ Mô phỏng)** và chia sẻ link cho người khác.
- Muốn dùng bản online với hardware: cho bridge chạy **wss://** (chứng chỉ TLS) hoặc mở bằng `http://localhost` — cùng máy với bridge.

## Định dạng dữ liệu (nếu bạn tự viết firmware/bridge)
Dashboard nhận mỗi frame là JSON:
```json
{"subcarriers": [20.1, 19.8, 21.3, ...]}   // biên độ mỗi subcarrier, ~25 frame/giây
```
Cũng chấp nhận mảng số thuần `[...]` hoặc CSV `"20.1, 19.8, ..."`. Dashboard tự trừ baseline
(EMA) để ra residual, rồi lọc Goertzel dải 0.1–0.5 Hz (thở) và 0.8–2.0 Hz (tim).

## Gặp lỗi?
| Triệu chứng | Cách xử lý |
|---|---|
| `wsStat` báo đỏ "lỗi kết nối" | Bridge chưa chạy, sai URL, hoặc đang mở bản online (dùng bản local) |
| Bridge không thấy CSI | Sai cổng serial/baud; hoặc `monitor` của idf còn chiếm cổng (thoát nó) |
| BPM không lên | Ngồi gần ESP32 (1–3 m), giữ yên 30 s để cửa sổ nhịp thở hội tụ |
| `Permission denied` cổng serial (Linux) | `sudo usermod -aG dialout $USER` rồi đăng nhập lại |
