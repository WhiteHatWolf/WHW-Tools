# WHW-Tools
A fast, multithreaded TCP port scanner with service detection and banner grabbing — written in Python.

# mvtool - Multithreaded TCP Port Scanner

`mvtool` is a fast and lightweight TCP port scanner written in Python. 
It supports scanning common ports, custom port ranges, or the full 1–65535 port range. 
With built-in service name mapping and optional banner grabbing, it's a useful tool for penetration testers, sysadmins, or anyone needing quick visibility into open ports on a host.

Key features include:
- ✅ Multithreaded scanning for high speed
- ✅ Supports full range, custom range, or common ports
- ✅ Banner grabbing from open services (when available)
- ✅ Service name resolution (e.g., port 22 → SSH)
