import socket
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, Future
import sys

# --- Port to Service Mapping ---
PORT_SERVICES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
    3306: "MySQL", 3389: "RDP", 8080: "HTTP-Alt", 8443: "HTTPS-Alt",
    5900: "VNC", 139: "NetBIOS", 445: "SMB", 137: "NetBIOS-NS", 138: "NetBIOS-DGM",
    1723: "PPTP", 5432: "PostgreSQL", 6379: "Redis"
}

COMMON_PORTS = list(PORT_SERVICES.keys())
shutdown_event = threading.Event()

# --- TCP Scanner with Description and Banner ---
def scan_tcp_port(ip, port):
    if shutdown_event.is_set():
        return
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((ip, port))

            service = PORT_SERVICES.get(port, "Unknown")
            banner = ""
            try:
                banner = s.recv(1024).decode(errors='ignore').strip()
            except:
                pass

            if banner:
                print(f"[TCP OPEN] Port \033[34m{port}\033[0m \033[37m({service})\033[0m - Banner: {banner}")
            else:
                print(f"[TCP OPEN] Port \033[34m{port}\033[0m \033[37m({service})\033[0m")

    except:
        pass

# --- Main Scanner ---
def main():
    parser = argparse.ArgumentParser(
        description="TCP Port Scanner with Service Names and Banner Grabbing",
        epilog="Example usage:\n"
               " [1] python mvtool.py 10.0.0.1\n"
               " [2] python mvtool.py 10.0.0.1 --all-port\n"
               " [3] python mvtool.py 10.0.0.1 --range 20-1024",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("ip", help="Target IP address")
    parser.add_argument("--all-port", action="store_true", help="Scan all 65535 ports")
    parser.add_argument("--range", help="Scan ports in a specific range (e.g., 20-1000)")
    parser.add_argument("--t", type=int, default=100, metavar="THREADS",
                        help="Number of threads (increase scanning speed) (default: 100)")
    args = parser.parse_args()

    # Determine the ports to scan
    if args.all_port:
        ports = range(1, 65536)
        label = "ALL"
    elif args.range:
        try:
            start, end = map(int, args.range.split('-'))
            if not (1 <= start <= end <= 65535):
                raise ValueError
            ports = range(start, end + 1)
            label = f"ports {start}-{end}"
        except:
            print("[!] Invalid port range format. Use --range START-END (e.g., 20-1000)")
            return
    else:
        ports = COMMON_PORTS
        label = "COMMON"
    print(f"\n\033[33m[+] Scanning {label} ports on {args.ip}\033[0m ....\n")
    print("\033[35m[+][+][+]TCP SCAN ONLY[+][+][+]\033[0m\n")

    executor = ThreadPoolExecutor(max_workers=args.t)
    futures: list[Future] = []

    try:
        for port in ports:
            if shutdown_event.is_set():
                break
            futures.append(executor.submit(scan_tcp_port, args.ip, port))

        for future in futures:
            if shutdown_event.is_set():
                break
            try:
                future.result(timeout=1)
            except Exception:
                pass

    except KeyboardInterrupt:
        print("\n[!] Interrupt detected. Attempting graceful shutdown...")
        shutdown_event.set()
        executor.shutdown(wait=False, cancel_futures=True)
        print("[!] Aborting scan.")

    finally:
        executor.shutdown(wait=True)
        print(f"\n[+] Scan complete for {args.ip}.")

# --- Entry Point ---
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        shutdown_event.set()
        print("\n[!] Force-stopped by user.")
        sys.exit(0)
