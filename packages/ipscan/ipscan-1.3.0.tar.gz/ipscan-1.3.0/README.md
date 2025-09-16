<p align="center">
    <img src="https://raw.githubusercontent.com/Wing9897/ipscan/main/assets/banner.svg" alt="ipscan banner" width="100%" />
</p>

<div align="center">

# ipscan

Fast IP scanner — multithreaded Ping and ARP scanning (Windows, Linux, macOS)

[![PyPI version](https://img.shields.io/pypi/v/ipscan?logo=pypi&label=PyPI)](https://pypi.org/project/ipscan/)
![Python](https://img.shields.io/pypi/pyversions/ipscan?logo=python)
![OS](https://img.shields.io/badge/OS-Windows%20%7C%20Linux%20%7C%20macOS-blue)
![License](https://img.shields.io/github/license/Wing9897/ipscan?color=success)

Language:
[English](README.md) · [繁體中文](README.zh-TW.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Italiano](README.it.md) · [Español](README.es.md) · [Português BR](README.pt-BR.md) · [Русский](README.ru.md)

</div>

---

## Table of contents

- Quick start
- Features
- CLI tools
- Python API
- Performance notes
- Requirements
- Contributing

---

## Quick start

Install from PyPI:

```bash
pip install ipscan
```

**Windows users**: Install optional Windows-optimized ping support:
```bash
pip install "ipscan[windows]"
```

**Note**: Linux ARP scanning requires sudo privileges for optimal performance.

### CLI

```bash
fping           # High-speed continuous ping (interactive)
sping           # Simple range ping scan
sarp            # ARP range scan
```

### Python API

Ping scan:

```python
from ipscan import ping_range, PingScanner

online_hosts = ping_range("192.168.1.1", "192.168.1.254")

scanner = PingScanner(timeout=1.0)
results = scanner.scan_range("10.0.0.1", "10.0.0.100")
```

ARP scan:

```python
from ipscan import arp_range, ArpScanner

host_info = arp_range("192.168.1.1", "192.168.1.254")
for ip, mac in host_info.items():
        print(f"{ip} -> {mac}")

scanner = ArpScanner()
results = scanner.scan_range("10.0.0.1", "10.0.0.100")
```

## Features

- **Cross-platform**: Windows, Linux, macOS support with automatic OS detection
- **Multithreaded scanning**: High-speed concurrent operations
- **Smart implementations**: Platform-optimized for best performance
  - Windows: Native SendARP API + ping3 library
  - Linux: Direct scapy ARP packets + system ping
  - macOS: System arp + ping commands
- **Simple API**: Unified interface across all platforms
- **Progress tracking**: Real-time progress bars and clean output

## Platform Details

| Feature | Windows | Linux | macOS |
|---------|---------|-------|-------|
| **Ping scanning** | ping3 library | system ping | system ping |
| **ARP scanning** | SendARP API | scapy packets | arp command |
| **Permissions** | No special permissions | sudo for ARP | No special permissions |
| **Performance** | Optimized | Optimized | Good |

## Usage Examples

### Linux ARP scanning (requires sudo)
```bash
sudo sarp
# Enter IP range when prompted
```

### High-speed continuous ping
```bash
fping
# Enter target IP and interval
```

### Range ping scanning
```bash
sping
# Enter start and end IP addresses
```

## Requirements

- **Python 3.7+**
- **Cross-platform support**: Windows, Linux, macOS
- **Dependencies**:
  - `tqdm` (progress bars)
  - `scapy` (ARP packet generation)
  - `ping3` (Windows optimization, optional)

## Contributing

Issues and PRs are welcome. If you like this project, consider starring it.

---

<div align="center">
Made with ❤️ for network tinkerers.
</div>
