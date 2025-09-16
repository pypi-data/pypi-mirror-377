import threading
import ipaddress
import time
import platform
import subprocess
from tqdm import tqdm
from typing import List, Set, Optional


class PingScanner:
    def __init__(self, timeout: float = 1.0, show_progress: bool = True):
        self.timeout = timeout
        self.show_progress = show_progress
        self.results = set()
        self.results_lock = threading.Lock()
        self.os_type = platform.system().lower()

    def _ping_windows(self, ip_address: str) -> bool:
        """Windows: 使用 ping3 (已完善)"""
        try:
            import ping3
            response_time = ping3.ping(str(ip_address), timeout=self.timeout)
            return response_time is not None and response_time is not False
        except (Exception, ImportError):
            # 如果 ping3 不可用，回退到系統 ping
            return self._ping_system(ip_address)

    def _ping_linux(self, ip_address: str) -> bool:
        """Linux: 使用系統 ping 命令 (無需 sudo)"""
        return self._ping_system(ip_address)

    def _ping_system(self, ip_address: str) -> bool:
        """通用系統 ping 命令"""
        try:
            if self.os_type == 'windows':
                # Windows ping 命令參數
                cmd = ['ping', '-n', '1', '-w', str(int(self.timeout * 1000)), ip_address]
            else:
                # Linux/macOS ping 命令參數
                cmd = ['ping', '-c', '1', '-W', str(int(self.timeout)), ip_address]

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=self.timeout + 1
            )
            return result.returncode == 0
        except Exception:
            return False

    def ping_host(self, ip_address: str, pbar: Optional[tqdm] = None) -> None:
        """跨平台 ping 實現"""
        success = False

        if self.os_type == 'windows':
            success = self._ping_windows(ip_address)
        else:  # Linux, macOS, etc.
            success = self._ping_linux(ip_address)

        if success:
            with self.results_lock:
                self.results.add(ip_address)

        if pbar:
            pbar.update(1)

    def scan_range(self, start_ip: str, end_ip: str) -> Set[str]:
        self.results.clear()

        # 驗證 IP 地址格式
        try:
            start_addr = ipaddress.IPv4Address(start_ip)
            end_addr = ipaddress.IPv4Address(end_ip)
        except ipaddress.AddressValueError as e:
            raise ValueError(f"無效的 IP 地址格式|Invalid IP address format: {e}")

        if int(start_addr) > int(end_addr):
            raise ValueError("起始 IP 應小於或等於結束 IP|Start IP should be less than or equal to end IP")

        ip_addresses = [str(ipaddress.IPv4Address(ip)) for ip in range(
            int(start_addr),
            int(end_addr) + 1
        )]

        pbar = tqdm(total=len(ip_addresses), desc="Ping掃描|Ping Scan", ncols=80) if self.show_progress else None

        threads = []
        for ip_address in ip_addresses:
            t = threading.Thread(target=self.ping_host, args=(ip_address, pbar))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        if pbar:
            pbar.close()

        return self.results.copy()

    def scan_list(self, ip_list: List[str]) -> Set[str]:
        self.results.clear()
        pbar = tqdm(total=len(ip_list), desc="Ping掃描|Ping Scan", ncols=80) if self.show_progress else None

        threads = []
        for ip_address in ip_list:
            t = threading.Thread(target=self.ping_host, args=(ip_address, pbar))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        if pbar:
            pbar.close()

        return self.results.copy()


def ping_range(start_ip: str, end_ip: str, timeout: float = 1.0, show_progress: bool = True) -> Set[str]:
    return PingScanner(timeout=timeout, show_progress=show_progress).scan_range(start_ip, end_ip)


def ping_list(ip_list: List[str], timeout: float = 1.0, show_progress: bool = True) -> Set[str]:
    return PingScanner(timeout=timeout, show_progress=show_progress).scan_list(ip_list)


def validate_ip_address(ip: str) -> bool:
    """驗證 IP 地址格式是否正確"""
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False


def validate_ip_range(start_ip: str, end_ip: str) -> bool:
    """驗證 IP 範圍是否有效"""
    try:
        start = int(ipaddress.IPv4Address(start_ip))
        end = int(ipaddress.IPv4Address(end_ip))
        return start <= end
    except ipaddress.AddressValueError:
        return False


def main():
    start_ip = input('請輸入起始 IP 地址|Start IP: ').strip()
    end_ip = input('請輸入結束 IP 地址|End IP: ').strip()

    # 驗證 IP 地址格式
    if not validate_ip_address(start_ip):
        print('無效的起始 IP 地址格式|Invalid start IP address format')
        print('範例|Example: 192.168.1.1')
        return

    if not validate_ip_address(end_ip):
        print('無效的結束 IP 地址格式|Invalid end IP address format')
        print('範例|Example: 192.168.1.254')
        return

    # 驗證 IP 範圍
    if not validate_ip_range(start_ip, end_ip):
        print('無效的 IP 範圍，起始 IP 應小於或等於結束 IP|Invalid IP range, start IP should be less than or equal to end IP')
        return

    start_time = time.time()
    print(f"開始掃描從 {start_ip} 到 {end_ip} 的 IP 地址...|Starting scan from {start_ip} to {end_ip}...")

    online_hosts = ping_range(start_ip, end_ip)

    total_time = time.time() - start_time
    ip_count = int(ipaddress.IPv4Address(end_ip)) - int(ipaddress.IPv4Address(start_ip)) + 1

    print("掃描結束|Scan completed")
    print(f"總共掃描了 {ip_count} 個 IP 地址|Total scanned: {ip_count}")
    print(f"總耗時: {total_time:.2f} 秒|Total time: {total_time:.2f} s")
    print(f"平均每個 IP 耗時: {total_time/ip_count:.4f} 秒|Avg per IP: {total_time/ip_count:.4f} s")

    if online_hosts:
        print(f"\n📋 在線主機列表 ({len(online_hosts)} 個)|Online hosts ({len(online_hosts)}):")
        print("-" * 50)
        for ip in sorted(online_hosts, key=lambda x: ipaddress.IPv4Address(x)):
            print(f"  {ip}")
    else:
        print("\n❌ 沒有發現在線主機|No online hosts found")


if __name__ == '__main__':
    main()