# RuView — Dashboard mô phỏng cảm biến WiFi CSI

Dashboard web **một file, tự chứa** (không cần cài đặt, không phụ thuộc mạng) minh hoạ trực quan
các khả năng của dự án [ruvnet/RuView](https://github.com/ruvnet/RuView): biến sóng WiFi thành
cảm biến để phát hiện người, đo nhịp thở / nhịp tim, và ước lượng tư thế qua **CSI (Channel State Information)**.

## Cách xem
Mở trực tiếp file trong trình duyệt:
```
ruview-demo/index.html
```
Không cần server, không cần build. Hoạt động offline.

## Có gì trong dashboard
- **Bản đồ nhiệt CSI** — 56 subcarrier × thời gian, cuộn theo thời gian thực
- **Sóng nhịp thở** + BPM (dải 0.1–0.5 Hz, giống `BreathingExtractor`)
- **Sóng nhịp tim** + BPM (dải 0.8–2.0 Hz, giống `HeartRateExtractor`)
- **Phổ tần số phát hiện** (công suất Goertzel theo dải)
- **Ước lượng tư thế (pose)** — khung xương minh hoạ hoạt động
- **KPI**: hiện diện, số người, nhịp thở, nhịp tim, năng lượng chuyển động
- **Điều khiển**: số người, hoạt động (đứng yên / thở / đi lại / té ngã), nhịp thở đặt,
  nhịp tim đặt, nhiễu môi trường, khoảng cách tới router
- Sáng/tối tự động theo hệ thống + nút đổi theme

## Quan trọng — mô phỏng, nhưng thuật toán là thật
Đây **không phải dữ liệu WiFi thật** (dữ liệu thật cần phần cứng ESP32-S3). Tuy nhiên phần
**phát hiện BPM là thuật toán thật**: tín hiệu CSI mô phỏng được đưa qua bộ lọc **Goertzel**
trên đúng dải tần của thư viện (nhịp thở 0.1–0.5 Hz, nhịp tim 0.8–2.0 Hz, lấy mẫu 25 Hz,
cửa sổ 30 s). Vì vậy số BPM hiển thị là **đo được từ tín hiệu**, không phải gán sẵn — kéo
thanh "đặt" và xem giá trị "đo" bám theo. Khi chọn *đi lại / té ngã*, nhiễu chuyển động lấn
át và độ tin cậy giảm, đúng như hành vi thực tế của hệ thống.

## Công nghệ
Vanilla HTML/CSS/JS + Canvas 2D. Không framework, không dependency ngoài. Bảng màu tuân theo
chuẩn data-viz (đã kiểm định độ tương phản & an toàn mù màu). Đã test headless (Chromium) —
không lỗi console, phát hiện BPM khớp giá trị đặt ở cả chế độ sáng và tối.
