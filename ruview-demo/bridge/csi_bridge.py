#!/usr/bin/env python3
"""
CSI BRIDGE — cầu nối phần cứng ESP32 → dashboard (chế độ "WiFi thật / Live").

Đọc CSI thật từ ESP32 (qua cổng Serial/USB hoặc UDP), tính BIÊN ĐỘ mỗi subcarrier,
rồi phát cho dashboard qua WebSocket dưới dạng JSON:  {"subcarriers":[a0,...]}

--- CÀI ĐẶT ---
    pip install websockets pyserial

--- DÙNG (ESP32 cắm USB, in CSI ra serial theo firmware espressif/esp-csi) ---
    python csi_bridge.py --serial /dev/ttyUSB0 --baud 921600
    # Windows:  python csi_bridge.py --serial COM7 --baud 921600

--- DÙNG (firmware gửi CSI qua UDP, ví dụ RuView sensing-node) ---
    python csi_bridge.py --udp 5005

Sau đó mở dashboard → chọn "WiFi thật (Live CSI)" → URL ws://localhost:8765 → Kết nối.
"""
import argparse, asyncio, json, math, re, socket, sys, time
import websockets

TARGET_FS = 25.0     # Hz — hạ mẫu xuống mức dashboard kỳ vọng
clients = set()

def amps_from_csi_ints(vals):
    """esp-csi xuất mảng CSI xen kẽ [imag, real, imag, real, ...] (int8).
    Biên độ mỗi subcarrier = sqrt(re^2 + im^2)."""
    out = []
    for i in range(0, len(vals) - 1, 2):
        im, re = vals[i], vals[i + 1]
        out.append(math.sqrt(re * re + im * im))
    return out

_bracket = re.compile(r"\[([-0-9,\s]+)\]")

def parse_esp_csi_line(line):
    """Bắt mảng [...] trong dòng CSI_DATA của firmware esp-csi. Trả biên độ/subcarrier."""
    if "CSI_DATA" not in line and "[" not in line:
        return None
    m = _bracket.search(line)
    if not m:
        return None
    try:
        vals = [int(x) for x in m.group(1).replace(",", " ").split()]
    except ValueError:
        return None
    if len(vals) < 8:
        return None
    return amps_from_csi_ints(vals)

async def broadcast(amps):
    if not amps or not clients:
        return
    msg = json.dumps({"subcarriers": [round(a, 3) for a in amps]})
    dead = set()
    for c in list(clients):
        try:
            await c.send(msg)
        except Exception:
            dead.add(c)
    clients.difference_update(dead)

# ---------- nguồn Serial ----------
async def serial_source(port, baud):
    import serial  # pyserial
    loop = asyncio.get_event_loop()
    ser = serial.Serial(port, baud, timeout=0.05)
    print(f"[serial] đọc CSI từ {port} @ {baud}")
    last = 0.0
    while True:
        line = await loop.run_in_executor(None, ser.readline)
        if not line:
            await asyncio.sleep(0)
            continue
        amps = parse_esp_csi_line(line.decode("utf-8", "ignore"))
        now = time.time()
        if amps and (now - last) >= 1.0 / TARGET_FS:   # hạ mẫu
            last = now
            await broadcast(amps)

# ---------- nguồn UDP ----------
async def udp_source(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    sock.bind(("0.0.0.0", port))
    loop = asyncio.get_event_loop()
    print(f"[udp] nghe CSI ở cổng UDP {port}")
    last = 0.0
    while True:
        data, _ = await loop.sock_recvfrom(sock, 4096)
        txt = data.decode("utf-8", "ignore")
        amps = parse_esp_csi_line(txt)
        if amps is None:
            # thử JSON {"subcarriers":[...]} hoặc mảng thuần
            try:
                j = json.loads(txt)
                amps = j.get("subcarriers") if isinstance(j, dict) else j
            except Exception:
                amps = None
        now = time.time()
        if amps and (now - last) >= 1.0 / TARGET_FS:
            last = now
            await broadcast(amps)

async def ws_handler(ws):
    clients.add(ws)
    print(f"[ws] dashboard kết nối ({len(clients)} client)")
    try:
        await ws.wait_closed()
    finally:
        clients.discard(ws)
        print("[ws] dashboard ngắt")

async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--serial", help="cổng serial ESP32, ví dụ /dev/ttyUSB0 hoặc COM7")
    ap.add_argument("--baud", type=int, default=921600)
    ap.add_argument("--udp", type=int, help="nghe CSI qua cổng UDP thay vì serial")
    ap.add_argument("--ws-port", type=int, default=8765)
    a = ap.parse_args()
    if not a.serial and not a.udp:
        sys.exit("Cần --serial <cổng> HOẶC --udp <port>. Xem --help.")

    print(f"[ws] phát cho dashboard tại ws://localhost:{a.ws_port}")
    async with websockets.serve(ws_handler, "0.0.0.0", a.ws_port):
        if a.serial:
            await serial_source(a.serial, a.baud)
        else:
            await udp_source(a.udp)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\ndừng.")
