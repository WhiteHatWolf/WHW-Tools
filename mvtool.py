import socket
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor
import sys
import time
import re

# GUI
import tkinter as tk
from tkinter import ttk, filedialog

TOOL_NAME = "MVTool v2.6"

PORT_SERVICES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
    3306: "MySQL", 3389: "RDP", 8080: "HTTP-Alt", 8443: "HTTPS-Alt",
    5900: "VNC", 139: "NetBIOS", 445: "SMB",
    1723: "PPTP", 5432: "PostgreSQL", 6379: "Redis"
}

COMMON_PORTS = list(PORT_SERVICES.keys())
shutdown_event = threading.Event()
stop_flag = False
open_ports = []
executor_global = None
is_scanning = False


# ================= DETECTION =================
def detect_service(port, banner):
    b = banner.lower()
    if "http" in b: return "HTTP"
    if "ssh" in b: return "SSH"
    if "ftp" in b: return "FTP"
    if "smtp" in b: return "SMTP"
    if "mysql" in b: return "MySQL"
    return PORT_SERVICES.get(port, "Unknown")

def extract_version(service, banner):
    if not banner:
        return ""

    if service == "HTTP":
        for line in banner.split("\n"):
            if "server:" in line.lower():
                return line.split(":", 1)[1].strip()

    if service == "SSH":
        match = re.search(r"SSH-\d\.\d-(.*)", banner)
        if match:
            return match.group(1)

    if service == "FTP":
        match = re.search(r"\((.*?)\)", banner)
        if match:
            return match.group(1)

    return ""

def grab_banner(sock, port):
    try:
        if port in [80, 8080, 8000]:
            sock.sendall(b"GET / HTTP/1.1\r\nHost: test\r\n\r\n")
        else:
            sock.sendall(b"\r\n")
        return sock.recv(4096).decode(errors="ignore").strip()
    except:
        return ""


# ================= CLI =================
def scan_tcp_port(ip, port, open_list=None):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)

            if s.connect_ex((ip, port)) == 0:
                banner = grab_banner(s, port)
                service = detect_service(port, banner)
                version = extract_version(service, banner)

                print(f"\n[OPEN] Port {port}")
                print(f" ├─ Service : {service}")
                if version:
                    print(f" ├─ Version : {version}")
                if banner:
                    print(f" ├─ Banner  : {banner.splitlines()[0][:100]}")

                if open_list is not None:
                    open_list.append(port)
    except:
        pass

def run_cli(args):
    print(f"""\033[36m
███╗   ███╗██╗   ██╗████████╗ ██████╗  ██████╗ ██╗
████╗ ████║██║   ██║╚══██╔══╝██╔═══██╗██╔═══██╗██║
██╔████╔██║██║   ██║   ██║   ██║   ██║██║   ██║██║
██║╚██╔╝██║╚██╗ ██╔╝   ██║   ██║   ██║██║   ██║██║
██║ ╚═╝ ██║ ╚████╔╝    ██║   ╚██████╔╝╚██████╔╝███████╗
╚═╝     ╚═╝  ╚═══╝     ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝

        \033[32m{TOOL_NAME}\033[0m
\033[0m""")

    if args.p:
        ports = [int(p) for p in args.p.split(",")]
        label = args.p
    elif args.all_port:
        ports = list(range(1, 65536))
        label = "ALL"
    elif args.range:
        start, end = map(int, args.range.split("-"))
        ports = list(range(start, end + 1))
        label = f"{start}-{end}"
    else:
        ports = COMMON_PORTS
        label = "COMMON"

    print(f"\033[33m[+] Scanning {label} ports on {args.ip}\033[0m\n")

    open_list = []
    start_time = time.time()

    executor = ThreadPoolExecutor(max_workers=args.t)

    for port in ports:
        executor.submit(scan_tcp_port, args.ip, port, open_list)

    executor.shutdown(wait=True)

    elapsed = round(time.time() - start_time, 2)

    print("\n\033[35m=== SCAN SUMMARY ===\033[0m")
    print(f"\033[36mTarget :\033[0m {args.ip}")
    print(f"\033[36mPorts  :\033[0m {label}")
    print(f"\033[36mOpen   :\033[0m {len(open_list)}")
    print(f"\033[36mTime   :\033[0m {elapsed}s\n")


# ================= GUI =================
def scan_gui_port(ip, port, update):
    global stop_flag

    if stop_flag:
        update(None)
        return

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.5)

            if s.connect_ex((ip, port)) == 0:
                banner = grab_banner(s, port)
                service = detect_service(port, banner)
                version = extract_version(service, banner)

                result = f"\n[OPEN] Port {port}\n"
                result += f" ├─ Service : {service}\n"

                if version:
                    result += f" ├─ Version : {version}\n"

                if banner:
                    result += f" ├─ Banner  : {banner.splitlines()[0][:100]}\n"

                update(result)
                return
    except:
        pass

    update("")


def launch_gui():
    global stop_flag, open_ports

    root = tk.Tk()
    root.title(TOOL_NAME)
    root.geometry("920x680")
    root.configure(bg="#0f172a")

    fg = "#e2e8f0"
    accent = "#22c55e"
    entry_bg = "#1e293b"

    header = tk.Frame(root, bg="#020617", height=50)
    header.pack(fill="x")

    tk.Label(header, text=TOOL_NAME,
             bg="#020617", fg=accent,
             font=("Consolas", 16, "bold")).pack(side="left", padx=15)

    status_var = tk.StringVar(value="Ready")
    tk.Label(header, textvariable=status_var,
             bg="#020617", fg="#94a3b8").pack(side="right", padx=15)

    frame = tk.Frame(root, bg="#0f172a")
    frame.pack(pady=10)

    tk.Label(frame, text="IP", bg="#0f172a", fg=fg).grid(row=0, column=0, padx=5)
    ip_entry = tk.Entry(frame, bg=entry_bg, fg=fg, insertbackground=accent)
    ip_entry.grid(row=0, column=1, padx=5)

    tk.Label(frame, text="Start Port", bg="#0f172a", fg=fg).grid(row=0, column=2, padx=5)
    start_entry = tk.Entry(frame, bg=entry_bg, fg=fg, insertbackground=accent)
    start_entry.grid(row=0, column=3, padx=5)

    tk.Label(frame, text="End Port", bg="#0f172a", fg=fg).grid(row=0, column=4, padx=5)
    end_entry = tk.Entry(frame, bg=entry_bg, fg=fg, insertbackground=accent)
    end_entry.grid(row=0, column=5, padx=5)

    result_box = tk.Text(root, bg="#020617", fg=accent,
                         insertbackground=accent, font=("Consolas", 10))
    result_box.pack(expand=True, fill="both", padx=10, pady=5)

    progress = ttk.Progressbar(root, length=600)
    progress.pack(pady=5)

    percent_label = tk.Label(root, text="0%", bg="#0f172a", fg=fg)
    percent_label.pack()

    def styled_button(parent, text, cmd, bg_color, hover_color):
        btn = tk.Button(parent, text=text, command=cmd,
                        bg=bg_color, fg="black",
                        activebackground=hover_color,
                        relief="flat", padx=12, pady=5,
                        font=("Consolas", 10, "bold"))

        def on_enter(e):
            btn.config(bg=hover_color)

        def on_leave(e):
            btn.config(bg=bg_color)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

    def save_results():
        file = filedialog.asksaveasfilename(defaultextension=".txt")
        if file:
            with open(file, "w") as f:
                f.write(result_box.get(1.0, tk.END))

    def stop_scan():
        global stop_flag, executor_global, is_scanning

        if not is_scanning:
            return

        stop_flag = True
        is_scanning = False

        if executor_global:
            executor_global.shutdown(wait=False, cancel_futures=True)

        status_var.set("Stopped")

    def start_scan():
        global stop_flag, open_ports, executor_global, is_scanning

        if is_scanning:
            return

        ip = ip_entry.get()
        start = int(start_entry.get())
        end = int(end_entry.get())

        stop_flag = False
        is_scanning = True
        open_ports = []

        result_box.delete(1.0, tk.END)
        status_var.set("Scanning...")

        result_box.insert(
            tk.END,
            f"[+] Starting scan on {ip} (Ports {start}-{end})\n\n"
        )

        total = end - start + 1
        progress["maximum"] = total
        progress["value"] = 0

        start_time = time.time()

        def update(res):
            root.after(0, lambda: safe_update(res))

        def safe_update(res):
            if not is_scanning:
                return

            progress["value"] += 1
            percent = int((progress["value"] / total) * 100)
            percent_label.config(text=f"{percent}%")

            if res:
                result_box.insert(tk.END, res)
                result_box.see(tk.END)

                if "[OPEN]" in res:
                    open_ports.append(res)

        def run():
            global executor_global, is_scanning

            executor_global = ThreadPoolExecutor(max_workers=200)

            for p in range(start, end + 1):
                if stop_flag:
                    break
                executor_global.submit(scan_gui_port, ip, p, update)

            executor_global.shutdown(wait=True)

            elapsed = round(time.time() - start_time, 2)

            def finish():
                global is_scanning
                is_scanning = False

                status_var.set("Completed" if not stop_flag else "Stopped")

                summary = f"\n=== SCAN SUMMARY ===\n"
                summary += f"Target : {ip}\n"
                summary += f"Ports  : {start}-{end}\n"
                summary += f"Open   : {len(open_ports)}\n"
                summary += f"Time   : {elapsed}s\n"

                result_box.insert(tk.END, summary)

            root.after(0, finish)

        threading.Thread(target=run, daemon=True).start()

    btn_frame = tk.Frame(root, bg="#0f172a")
    btn_frame.pack(pady=10)

    styled_button(btn_frame, "Start Scan", start_scan, "#22c55e", "#16a34a").grid(row=0, column=0, padx=10)
    styled_button(btn_frame, "Stop", stop_scan, "#ef4444", "#dc2626").grid(row=0, column=1, padx=10)
    styled_button(btn_frame, "Save Results", save_results, "#38bdf8", "#0ea5e9").grid(row=0, column=2, padx=10)

    root.mainloop()


# ================= MAIN =================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", nargs="?", help="Target IP")
    parser.add_argument("--range")
    parser.add_argument("--all-port", action="store_true")
    parser.add_argument("-p")
    parser.add_argument("--t", type=int, default=100)
    parser.add_argument("--gui", action="store_true")

    args = parser.parse_args()

    if args.gui:
        launch_gui()
    else:
        if not args.ip:
            print("Provide IP")
            sys.exit(1)
        run_cli(args)


if __name__ == "__main__":
    main()
