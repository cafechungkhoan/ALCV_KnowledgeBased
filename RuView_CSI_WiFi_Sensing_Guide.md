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

## 8. Build từ source — quy trình ĐÃ KIỂM CHỨNG ✅

> Toàn bộ dự án đã được build & chạy thử thành công trên **Ubuntu 24.04, Rust 1.94 (stable), Python 3.11** ngày 2026-07-08. Kết quả: **17 binary Rust** + **1 Python wheel**, và bộ `verify` của dự án đạt các phase liên quan tới build.

### 8.1. Lấy source (kèm submodule — BẮT BUỘC)
Repo dùng nhiều git submodule (`vendor/*`, `ruv-neural`, `worldgraph`, `rufield`, `rvcsi`, `ruview-swarm`). Thiếu là build fail:
```bash
git clone --recurse-submodules https://github.com/ruvnet/RuView
# hoặc nếu đã clone:
cd RuView && git submodule update --init --recursive
```

### 8.2. Công cụ cần
- **Rust** (repo pin 1.89 qua `rust-toolchain.toml`; stable ≥1.89 chạy tốt — dùng `RUSTUP_TOOLCHAIN=stable` để khỏi tải toolchain riêng)
- **Python 3.10+** và **maturin** (`pip install maturin`)

### 8.3. Thư viện hệ thống (Ubuntu/Debian)
```bash
sudo apt-get update && sudo apt-get install -y --no-install-recommends \
  libgtk-3-dev libwebkit2gtk-4.1-dev libsoup-3.0-dev librsvg2-dev \
  libxdo-dev libayatana-appindicator3-dev \   # crate desktop (Tauri)
  gfortran libopenblas-dev \                   # BLAS cho ndarray-linalg (person-counting)
  libudev-dev make                             # serialport (giao tiếp ESP32)
```

### 8.4. Build Python wheel (deliverable chính, tự chứa)
```bash
cd python
maturin build --release          # → target/wheels/wifi_densepose-2.0.0a1-*.whl
pip install target/wheels/wifi_densepose-2.0.0a1-*.whl
python -c "import wifi_densepose as w; print(w.hello())"   # -> ok
```

### 8.5. Build Rust workspace (17 binary)
```bash
cd v2 && RUSTUP_TOOLCHAIN=stable cargo build --release --workspace
# hoặc: make build-rust
```
Binary xuất ra ở `v2/target/release/`: `wifi-densepose` (CLI), `sensing-server`,
`homecore-server`, `homecore-api-server`, `nvsim-server`, `wifi-densepose-desktop`,
`cog-pose-estimation`, `cog-person-count`, `cog-ha-matter`, `ruview-pointcloud`, `train`…

> **⚠️ Hai chỉnh sửa trong `v2/Cargo.toml` — CHỈ cần khi build trong môi trường CHẶN mạng** (như sandbox này). Máy có internet bình thường thì để nguyên mặc định:
> 1. `ndarray-linalg`: đổi feature `openblas-static` → **`openblas-system`** (dùng `libopenblas-dev` hệ thống thay vì tải + build OpenBLAS từ nguồn).
> 2. `ort` (ONNX Runtime): đổi thành `default-features = false, features = ["load-dynamic"]` (nạp `libonnxruntime.so` lúc chạy thay vì tải binary từ `cdn.pyke.io`). Khi chạy các binary ML, trỏ `ORT_DYLIB_PATH` tới `libonnxruntime.so` (ví dụ lấy từ `pip install onnxruntime`).

### 8.6. Kiểm chứng
```bash
./v2/target/release/wifi-densepose version      # wifi-densepose 0.3.1 (+ MAT 0.3.1)
./v2/target/release/sensing-server --help
pip install numpy scipy                          # cần cho Phase 1 của verify
./verify --quick                                 # trust kill switch (proof pipeline)
```
Kết quả `verify` mong đợi: **Phase 1** (pipeline hash khớp), **Phase 2** (không có random giả),
**Phase 4** (PyO3 compile sạch), **Phase 5** (invariant riêng tư) đều **PASS**. Phase 6 (kiểm
tra crates.io) sẽ FAIL nếu build từ source chưa publish — điều này **bình thường**, không phải lỗi build.

---

## Nguồn tham khảo
- Repo: https://github.com/ruvnet/RuView
- README: https://github.com/ruvnet/RuView/blob/main/README.md
- PyPI: `wifi-densepose` (bản chạy được: `2.0.0a1`), meta-package `ruview`
- Hướng dẫn migration pip: https://github.com/ruvnet/RuView/blob/main/docs/pip-migration.md
