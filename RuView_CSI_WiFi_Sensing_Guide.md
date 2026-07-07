# RuView — Cảm biến con người bằng sóng WiFi (CSI) — Hướng dẫn cài đặt & tìm hiểu

> Biến sóng WiFi sẵn có trong nhà thành "radar": phát hiện người, đếm người, đo **nhịp thở / nhịp tim** không tiếp xúc, nhận diện tư thế — xuyên tường, trong bóng tối, **không cần camera hay thiết bị đeo**.

- **Repo gốc:** https://github.com/ruvnet/RuView (tác giả: rUv, giấy phép MIT)
- **Tài liệu này đã được kiểm chứng thực tế** (cài + chạy thử) ngày 2026-07-07, không phải chép nguyên văn từ quảng cáo.

---

## 1. RuView là gì?

Mọi router WiFi liên tục phát sóng vô tuyến khắp phòng. Khi có người **di chuyển, thở, hoặc thậm chí ngồi yên**, họ làm nhiễu các sóng đó theo cách đo lường được. RuView đọc thông tin nhiễu này — gọi là **CSI (Channel State Information)** — từ chip **ESP32 giá rẻ (~$6–9)** và suy ra:

| Khả năng | Mô tả |
|---|---|
| 👤 Hiện diện & đếm người | Phát hiện có người, số người, ra/vào phòng |
| ❤️ Dấu hiệu sinh tồn | Đo **nhịp thở (6–30 BPM)** và **nhịp tim (40–120 BPM)** không tiếp xúc |
| 🚶 Nhận diện hoạt động | Đi, ngồi, cử chỉ, **té ngã** |
| 🕴️ Ước lượng tư thế (pose) | Ước lượng khung xương người từ tín hiệu WiFi |
| 🛏️ Giám sát giấc ngủ | Theo dõi ban đêm, sàng lọc ngưng thở (nghiên cứu) |

**Lõi kỹ thuật:** viết bằng **Rust** + binding Python (PyO3). Tích hợp Home Assistant (MQTT), Apple Home, Google Home, Alexa, Matter.

---

## 2. ⚠️ Lưu ý QUAN TRỌNG về tên package (dễ cài sai)

Reel/quảng cáo thường ghi `pip install ruview` — **lệnh này sẽ báo lỗi**. Trạng thái thật trên PyPI (đã kiểm tra):

| Lệnh trong quảng cáo | Thực tế |
|---|---|
| `pip install ruview` | ❌ Không tìm thấy (chỉ có bản alpha, cần cờ `--pre`) |
| `pip install wifi-densepose` | ⚠️ Cài được **v1.99.0 nhưng đây chỉ là "stub"** — khi `import` sẽ báo lỗi yêu cầu cài v2.0.0 |
| `pip install wifi-densepose==2.0.0` | ❌ **Bản 2.0.0 stable CHƯA phát hành** (dù chính stub trỏ tới nó) |
| `pip install wifi-densepose==2.0.0a1` | ✅ **Đây mới là bản chạy được** (alpha, lõi Rust thật) |

👉 **Kết luận:** dự án đang ở **giai đoạn alpha**. Muốn dùng thư viện Python thật, phải cài bản tiền phát hành (pre-release).

---

## 3. Cài đặt

### Yêu cầu môi trường
- Python **3.10+** (cho thư viện Python) — hoặc Docker (cho bản demo)
- Có **trình biên dịch** nếu máy bạn chưa có sẵn wheel (bản alpha build từ Rust). Đa số Linux/macOS/Windows phổ biến đã có wheel dựng sẵn.
- Phần cứng **ESP32-S3** (~$9) hoặc **ESP32-C6** (~$6–10) — **chỉ cần khi muốn thu tín hiệu CSI thật**.

### Cách 1 — Thư viện Python (nên dùng để lập trình) ✅ đã kiểm chứng
```bash
# Tạo môi trường ảo cho gọn
python3 -m venv rv-env
source rv-env/bin/activate        # Windows: rv-env\Scripts\activate

# BẮT BUỘC cài bản alpha (pre-release):
pip install --pre wifi-densepose
# hoặc chỉ định rõ:
pip install wifi-densepose==2.0.0a1
```

Kiểm tra cài đặt thành công:
```bash
python -c "import wifi_densepose as w; print(w.hello())"   # In ra: ok
```

### Cách 2 — Docker demo (KHÔNG cần phần cứng, để xem giao diện heatmap)
```bash
docker pull ruvnet/wifi-densepose:latest
docker run -p 3000:3000 ruvnet/wifi-densepose:latest
# Mở trình duyệt: http://localhost:3000
```
> Lưu ý: image này do dự án cung cấp; nếu pull lỗi/không tồn tại thì dùng Cách 1 hoặc clone repo (Cách 4).

### Cách 3 — Nạp firmware cho ESP32-S3 (khi ĐÃ có phần cứng)
```bash
python -m esptool --chip esp32s3 --port COM9 --baud 460800 \
  write_flash 0x0 bootloader.bin 0x8000 partition-table.bin \
  0xf000 ota_data_initial.bin 0x20000 esp32-csi-node.bin

python firmware/esp32-csi-node/provision.py --port COM9 \
  --ssid "TenWiFi" --password "matkhau" --target-ip 192.168.1.20
```

### Cách 4 — Clone toàn bộ repo (xem mã nguồn, script Node.js)
```bash
git clone https://github.com/ruvnet/RuView
cd RuView
# Các script xử lý tín hiệu (cần Cognitum Seed / phần cứng):
node scripts/rf-scan.js --port 5006
node scripts/snn-csi-processor.js --port 5006
node scripts/mincut-person-counter.js --port 5006
```

---

## 4. Ví dụ chạy được — Đo nhịp thở từ tín hiệu CSI ✅ đã kiểm chứng

Đoạn dưới lấy từ chính docstring của thư viện và **đã chạy thật** (mô phỏng nhịp thở 15 BPM → thư viện phát hiện đúng 15.0 BPM):

```python
import math
import wifi_densepose as w

# 56 subcarrier, lấy mẫu 100 Hz, cửa sổ 30 giây (mặc định cho ESP32)
br = w.BreathingExtractor.esp32_default()
# hoặc: w.BreathingExtractor(n_subcarriers=56, sample_rate=100.0, window_secs=30.0)

fs, bpm = 100.0, 15.0          # mô phỏng nhịp thở 15 lần/phút
f = bpm / 60.0
est = None
for i in range(3000):          # 30 giây x 100 Hz
    t = i / fs
    frame = [0.02 * math.sin(2 * math.pi * f * t) for _ in range(56)]
    # Trong thực tế: 'residuals' là dữ liệu đã tiền xử lý từ ESP32
    est = br.extract(residuals=frame, weights=[])   # weights=[] = trọng số bằng nhau

if est is not None:
    print(est.value_bpm, est.confidence, est.status)
# Kết quả mẫu: 15.0  0.291  Unreliable
#   -> value_bpm chính xác; confidence thấp vì đây là sóng sin thuần,
#      dữ liệu CSI thật từ ESP32 sẽ cho độ tin cậy cao hơn.
```

Các class/API chính có sẵn: `BreathingExtractor`, `HeartRateExtractor`, `PoseEstimate`,
`PersonPose`, `Keypoint`, `VitalEstimate`, `VitalReading`, `VitalStatus`, `BoundingBox`.

- `HeartRateExtractor`: đo nhịp tim 40–120 BPM (bandpass 0.8–2.0 Hz + autocorrelation).
- `BreathingExtractor`: đo nhịp thở 6–30 BPM (bandpass 0.1–0.5 Hz + zero-crossing).

---

## 5. Phần cứng cần mua (nếu muốn dùng thật)

| Mức | Thiết bị | Chi phí | Khả năng |
|---|---|---|---|
| Tối thiểu | Router WiFi hiện có | $0 | Chỉ RSSI, rất hạn chế |
| **Khuyến nghị** | **ESP32-S3 / ESP32-C6** | **$6–10 / node** | CSI đầy đủ (pose, vital signs) |
| Đầy đủ | ESP32 + Cognitum Seed | ~$140 | Thêm bộ nhớ bền vững, AI, chạy hoàn toàn tại edge |

> Đặt tối thiểu **2 node** (1 phát, 1 thu) để có CSI tốt; nhiều node → độ phủ và độ chính xác cao hơn.

---

## 6. Lộ trình đề xuất

1. **Bắt đầu không cần mua gì:** cài Cách 1 (`pip install --pre wifi-densepose`) và chạy ví dụ ở Mục 4 để hiểu API.
2. **Xem giao diện trực quan:** thử Docker demo (Cách 2).
3. **Làm thật:** mua 2× ESP32-S3, nạp firmware (Cách 3), đưa dữ liệu CSI vào các Extractor.
4. **Tích hợp nhà thông minh:** nối qua MQTT → Home Assistant.

---

## 7. Cảnh báo & lưu ý thực tế

- ⚠️ **Dự án đang ở giai đoạn alpha** — API có thể đổi, tài liệu/link migration đôi chỗ chưa khớp (ví dụ trỏ tới v2.0.0 chưa tồn tại). Không nên dùng cho sản phẩm production ngay.
- 🔒 **Quyền riêng tư:** cảm biến xuyên tường + đo sinh trắc học → cân nhắc pháp lý và sự đồng thuận khi triển khai nơi có người khác.
- 🩺 Kết quả nhịp tim/nhịp thở mang tính **tham khảo/nghiên cứu**, không thay thế thiết bị y tế.

---

## Nguồn tham khảo
- Repo: https://github.com/ruvnet/RuView
- README: https://github.com/ruvnet/RuView/blob/main/README.md
- PyPI: `wifi-densepose` (bản chạy được: `2.0.0a1`), meta-package `ruview`
- Hướng dẫn migration pip: https://github.com/ruvnet/RuView/blob/main/docs/pip-migration.md
