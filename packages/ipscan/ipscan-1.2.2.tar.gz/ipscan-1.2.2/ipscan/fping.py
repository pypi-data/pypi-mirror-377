import time
import platform
import subprocess


def _ping_windows(target: str, timeout_s: float = 1.0) -> tuple:
    """Windows: 優先使用 ping3，回退到系統 ping"""
    try:
        import ping3
        rtt = ping3.ping(target, timeout=timeout_s)
        if rtt is not None and rtt is not False:
            return True, rtt
        return False, None
    except (Exception, ImportError):
        # ping3 不可用，使用系統 ping
        return _ping_system_windows(target, timeout_s)


def _ping_system_windows(target: str, timeout_s: float = 1.0) -> tuple:
    """Windows 系統 ping 命令"""
    try:
        result = subprocess.run(
            ['ping', '-n', '1', '-w', str(int(timeout_s * 1000)), target],
            capture_output=True,
            text=True,
            timeout=timeout_s + 1
        )

        if result.returncode == 0:
            # 嘗試解析 RTT (Windows ping 輸出格式)
            lines = result.stdout.split('\n')
            for line in lines:
                if 'time=' in line.lower() or '時間=' in line:
                    try:
                        # 提取時間值 (例如: "time=24ms" 或 "時間=24ms")
                        time_part = line.split('time=')[-1].split('時間=')[-1]
                        rtt_str = time_part.split('ms')[0].strip()
                        rtt_ms = float(rtt_str)
                        return True, rtt_ms / 1000.0  # 轉換為秒
                    except:
                        pass
            return True, None  # 成功但無法解析 RTT
        return False, None
    except Exception:
        return False, None


def _ping_linux(target: str, timeout_s: float = 1.0) -> tuple:
    """Linux: 使用系統 ping 命令"""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', str(int(timeout_s)), target],
            capture_output=True,
            text=True,
            timeout=timeout_s + 1
        )

        if result.returncode == 0:
            # 嘗試解析 RTT (Linux ping 輸出格式)
            lines = result.stdout.split('\n')
            for line in lines:
                if 'time=' in line:
                    try:
                        # 提取時間值 (例如: "time=24.5 ms")
                        time_part = line.split('time=')[1]
                        rtt_str = time_part.split(' ')[0].strip()
                        rtt_ms = float(rtt_str)
                        return True, rtt_ms / 1000.0  # 轉換為秒
                    except:
                        pass
            return True, None  # 成功但無法解析 RTT
        return False, None
    except Exception:
        return False, None


def cross_platform_ping(target: str, timeout_s: float = 1.0) -> tuple:
    """跨平台 ping 實現"""
    os_type = platform.system().lower()

    if os_type == 'windows':
        return _ping_windows(target, timeout_s)
    else:  # Linux, macOS, etc.
        return _ping_linux(target, timeout_s)


def main():
    target = input('請輸入目標 IP 位址|Enter target IP: ').strip()
    if not target:
        print('目標 IP 不可為空|Target IP cannot be empty')
        return

    try:
        interval_ms_str = input('請輸入 ping 間隔(ms)|Enter ping interval (ms): ').strip()
        interval_ms = int(interval_ms_str)
    except Exception:
        print('輸入無效，使用 100ms|Invalid input, using 100ms')
        interval_ms = 100

    if interval_ms < 1:
        print('最小間隔為 1ms，已自動調整|Minimum interval is 1ms; adjusted to 1ms')
        interval_ms = 1

    os_name = platform.system()
    print(f"檢測到系統: {os_name}|Detected OS: {os_name}")
    print(f"開始對 {target} 進行高速連續 Ping（Ctrl+C 結束）|Starting high-speed continuous ping to {target} (Ctrl+C to stop)")

    timeout_s = 1.0
    interval_s = interval_ms / 1000.0

    sent = 0
    received = 0
    try:
        while True:
            start = time.perf_counter()
            sent += 1

            success, rtt = cross_platform_ping(target, timeout_s)

            if success and rtt is not None:
                received += 1
                print(f"回應: {rtt*1000:.2f} ms|Reply: {rtt*1000:.2f} ms")
            elif success:
                received += 1
                print("回應: OK (無法解析時間)|Reply: OK (time not parsed)")
            else:
                print("逾時|Timeout")

            elapsed = time.perf_counter() - start
            sleep_left = interval_s - elapsed
            if sleep_left > 0:
                time.sleep(sleep_left)
    except KeyboardInterrupt:
        loss = 0.0 if sent == 0 else (sent - received) * 100.0 / sent
        print("\n統計|Statistics")
        print(f"已發送: {sent} | Sent: {sent}")
        print(f"已接收: {received} | Received: {received}")
        print(f"遺失率: {loss:.1f}% | Packet Loss: {loss:.1f}%")


if __name__ == '__main__':
    main()