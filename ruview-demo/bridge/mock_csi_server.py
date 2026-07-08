#!/usr/bin/env python3
"""
Mock CSI WebSocket server — phát khung CSI mô phỏng để TEST dashboard ở chế độ Live
mà chưa cần phần cứng ESP32. Đây KHÔNG phải dữ liệu thật; dùng để kiểm tra đường
truyền WebSocket → dashboard hoạt động. Bridge thật xem `csi_bridge.py`.

Chạy:
    pip install websockets
    python mock_csi_server.py            # ws://localhost:8765
Rồi mở dashboard → "WiFi thật (Live)" → Kết nối.
"""
import asyncio, json, math, time, argparse
import websockets

NSUB = 56
FS   = 25.0          # Hz — khớp giả định của dashboard

async def stream(ws, br_bpm, hr_bpm):
    t0 = time.time()
    i = 0
    while True:
        t = i / FS
        fbr, fhr = br_bpm / 60.0, hr_bpm / 60.0
        br = 1.0 * math.sin(2 * math.pi * fbr * t)
        hr = 0.28 * math.sin(2 * math.pi * fhr * t)
        frame = []
        for k in range(NSUB):
            ph = (k * 0.17) % (2 * math.pi)
            noise = 0.15 * (2 * ((i * 7 + k * 13) % 97) / 97 - 1)
            frame.append(round(20.0 + br * math.cos(ph) + hr + noise, 4))
        await ws.send(json.dumps({"subcarriers": frame}))
        i += 1
        # giữ nhịp ~FS Hz theo thời gian thực
        await asyncio.sleep(max(0, (i / FS) - (time.time() - t0)))

async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--breathing", type=float, default=15.0)
    ap.add_argument("--heart", type=float, default=72.0)
    a = ap.parse_args()

    async def handler(ws):
        print("client connected")
        try:
            await stream(ws, a.breathing, a.heart)
        except websockets.ConnectionClosed:
            print("client disconnected")

    print(f"Mock CSI server ws://{a.host}:{a.port}  (breathing={a.breathing} heart={a.heart} BPM)")
    async with websockets.serve(handler, a.host, a.port):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
