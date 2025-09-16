import ctypes
import threading
import ipaddress
import time
import platform
import subprocess
import re
import os
import sys
from tqdm import tqdm
from typing import List, Dict, Optional


class ArpScanner:
    def __init__(self, show_progress: bool = True):
        self.show_progress = show_progress
        self.results = {}
        self.results_lock = threading.Lock()
        self.os_type = platform.system().lower()

    def _get_mac_windows(self, ip: str) -> Optional[str]:
        """Windows SendARP API - 快速高效"""
        try:
            iphlpapi = ctypes.windll.iphlpapi
            inet_addr = ctypes.windll.ws2_32.inet_addr
            SendARP = iphlpapi.SendARP
            dest_ip = inet_addr(ip.encode('utf-8'))
            mac_addr = ctypes.create_string_buffer(6)
            mac_addr_len = ctypes.c_ulong(6)
            res = SendARP(dest_ip, 0, ctypes.byref(mac_addr), ctypes.byref(mac_addr_len))
            if res == 0:
                return ':'.join('%02x' % b for b in mac_addr.raw[:6])
            return None
        except Exception:
            return None

    def _get_mac_scapy(self, ip: str) -> Optional[str]:
        """使用 scapy 直接發送 ARP 封包 - 超快速 (需要 root 權限)"""
        try:
            from scapy.all import ARP, Ether, srp, conf
            conf.verb = 0  # 禁用 scapy 輸出

            # 建立 ARP 封包
            arp = ARP(pdst=ip)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether / arp

            # 發送封包並等待回應
            result = srp(packet, timeout=0.5, verbose=False)[0]

            if result:
                return result[0][1].hwsrc.lower()
            return None
        except ImportError:
            raise ImportError("scapy 未安裝。請執行: pip install scapy")
        except Exception as e:
            raise RuntimeError(f"ARP 掃描失敗 (可能需要 sudo 權限): {e}")

    def _get_mac_linux(self, ip: str) -> Optional[str]:
        """Linux MAC 獲取 - 使用 scapy 直接發送 ARP 封包"""
        return self._get_mac_scapy(ip)


    def _get_mac_macos(self, ip: str) -> Optional[str]:
        """macOS arp 命令"""
        try:
            # 檢查 ARP cache
            result = subprocess.run(['arp', '-n', ip],
                                  capture_output=True, text=True, timeout=0.5)
            if result.returncode == 0:
                mac_match = re.search(r'([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}', result.stdout)
                if mac_match:
                    return mac_match.group(0).replace('-', ':').lower()

            # 觸發 ARP
            subprocess.run(['ping', '-c', '1', '-t', '1', ip],
                         capture_output=True, timeout=1.0)

            # 再次檢查
            result = subprocess.run(['arp', '-n', ip],
                                  capture_output=True, text=True, timeout=0.5)
            if result.returncode == 0:
                mac_match = re.search(r'([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}', result.stdout)
                if mac_match:
                    mac = mac_match.group(0).replace('-', ':').lower()
                    return mac if mac != "00:00:00:00:00:00" else None

        except Exception:
            pass
        return None

    def get_mac(self, ip: str) -> Optional[str]:
        """跨平台 MAC 地址獲取"""
        if self.os_type == 'windows':
            return self._get_mac_windows(ip)
        elif self.os_type == 'linux':
            return self._get_mac_linux(ip)
        elif self.os_type == 'darwin':
            return self._get_mac_macos(ip)
        else:
            # 未知系統，嘗試通用方法
            try:
                result = subprocess.run(['arp', '-n', ip],
                                      capture_output=True, text=True, timeout=1.0)
                if result.returncode == 0:
                    mac_match = re.search(r'([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}', result.stdout)
                    if mac_match:
                        return mac_match.group(0).replace('-', ':').lower()
            except Exception:
                pass
            return None

    def scan_ip(self, ip: str, pbar: Optional[tqdm] = None) -> None:
        mac = self.get_mac(ip)
        if mac and mac != "00:00:00:00:00:00":
            with self.results_lock:
                self.results[ip] = mac
        if pbar:
            pbar.update(1)

    def scan_range(self, start_ip: str, end_ip: str) -> Dict[str, str]:
        self.results.clear()

        # 驗證 IP 地址格式
        try:
            start_addr = ipaddress.IPv4Address(start_ip)
            end_addr = ipaddress.IPv4Address(end_ip)
        except ipaddress.AddressValueError as e:
            raise ValueError(f"無效的 IP 地址格式|Invalid IP address format: {e}")

        if int(start_addr) > int(end_addr):
            raise ValueError("起始 IP 應小於或等於結束 IP|Start IP should be less than or equal to end IP")

        ip_list = [str(ipaddress.IPv4Address(ip)) for ip in range(
            int(start_addr),
            int(end_addr) + 1
        )]

        pbar = tqdm(total=len(ip_list), desc="ARP掃描|ARP Scan", ncols=80) if self.show_progress else None

        threads = []
        for ip in ip_list:
            t = threading.Thread(target=self.scan_ip, args=(ip, pbar))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        if pbar:
            pbar.close()

        return self.results.copy()

    def scan_list(self, ip_list: List[str]) -> Dict[str, str]:
        self.results.clear()
        pbar = tqdm(total=len(ip_list), desc="ARP掃描|ARP Scan", ncols=80) if self.show_progress else None

        threads = []
        for ip in ip_list:
            t = threading.Thread(target=self.scan_ip, args=(ip, pbar))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        if pbar:
            pbar.close()

        return self.results.copy()


def arp_range(start_ip: str, end_ip: str, show_progress: bool = True) -> Dict[str, str]:
    return ArpScanner(show_progress=show_progress).scan_range(start_ip, end_ip)


def arp_list(ip_list: List[str], show_progress: bool = True) -> Dict[str, str]:
    return ArpScanner(show_progress=show_progress).scan_list(ip_list)


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


def check_sudo_permission():
    """檢查是否有 sudo 權限（Linux）"""
    if platform.system().lower() == 'linux':
        if os.geteuid() != 0:
            print("=" * 60)
            print("⚠️  Linux ARP 掃描需要 sudo 權限 | ARP scan requires sudo on Linux")
            print("=" * 60)
            print("\n請使用以下命令執行 | Please run with:")
            print(f"\n  sudo {sys.executable} -m ipscan.sarp")

            # 如果在虛擬環境中，提供更精確的指令
            if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
                print(f"  或 | or")
                print(f"  sudo {sys.executable} {sys.argv[0]}")

            print("\n提示 | Tip: 您也可以給 Python 添加網路權限:")
            print(f"  sudo setcap cap_net_raw+ep {sys.executable}")
            print("  然後可以直接運行 sarp")
            print("=" * 60)
            return False
    return True


def main():
    # Linux 平台檢查 sudo 權限
    if not check_sudo_permission():
        sys.exit(1)

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

    host_results = arp_range(start_ip, end_ip)

    print("正在收集最後的回應...|Collecting final replies...")
    time.sleep(1)

    total_time = time.time() - start_time
    ip_count = int(ipaddress.IPv4Address(end_ip)) - int(ipaddress.IPv4Address(start_ip)) + 1

    print("掃描結束|Scan completed")
    print(f"總共掃描了 {ip_count} 個 IP 地址|Total scanned: {ip_count}")
    print(f"總耗時: {total_time:.2f} 秒|Total time: {total_time:.2f} s")
    print(f"平均每個 IP 耗時: {total_time/ip_count:.4f} 秒|Avg per IP: {total_time/ip_count:.4f} s")

    if host_results:
        print(f"\n📋 在線主機列表 ({len(host_results)} 個)|Online hosts ({len(host_results)}):")
        print("-" * 50)
        for ip in sorted(host_results, key=lambda x: ipaddress.IPv4Address(x)):
            print(f"  {ip:<15} -> {host_results[ip]}")
    else:
        print("\n❌ 沒有發現在線主機|No online hosts found")


if __name__ == '__main__':
    main()