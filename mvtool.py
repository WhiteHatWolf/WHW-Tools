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
    root.geometry("1000x900")
    root.configure(bg="#0a0e27")
    root.resizable(True, True)

    # Color Scheme
    bg_dark = "#0a0e27"
    bg_card = "#151b3d"
    bg_header = "#0d1128"
    fg_primary = "#e2e8f0"
    fg_secondary = "#94a3b8"
    accent_green = "#00ff9f"
    accent_cyan = "#00d4ff"
    btn_green = "#00ff9f"
    btn_green_hover = "#00cc7f"
    btn_red = "#ff4757"
    btn_red_hover = "#ee2f3d"
    btn_blue = "#38bdf8"
    btn_blue_hover = "#0ea5e9"
    entry_bg = "#1e2849"
    border_color = "#2d3561"

    # ============= STYLED BUTTON FUNCTION =============
    def styled_button(parent, text, cmd, bg_color, hover_color, width=15):
        btn = tk.Button(
            parent,
            text=text,
            command=cmd,
            bg=bg_color,
            fg="#0a0e27",
            activebackground=hover_color,
            activeforeground="#0a0e27",
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=10,
            font=("Segoe UI", 11, "bold"),
            cursor="hand2",
            width=width
        )

        def on_enter(e):
            btn.config(bg=hover_color)

        def on_leave(e):
            btn.config(bg=bg_color)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

    # ============= HEADER =============
    header = tk.Frame(root, bg=bg_header, height=70)
    header.pack(fill="x")
    header.pack_propagate(False)

    title_label = tk.Label(
        header,
        text="⚡ " + TOOL_NAME + " ⚡",
        bg=bg_header,
        fg=accent_green,
        font=("Consolas", 20, "bold")
    )
    title_label.pack(side="left", padx=25, pady=15)

    status_var = tk.StringVar(value="● Ready")
    status_label = tk.Label(
        header,
        textvariable=status_var,
        bg=bg_header,
        fg=fg_secondary,
        font=("Segoe UI", 12)
    )
    status_label.pack(side="right", padx=25, pady=15)

    # ============= INPUT CARD =============
    input_card = tk.Frame(root, bg=bg_card, highlightbackground=border_color, highlightthickness=2)
    input_card.pack(pady=20, padx=30, fill="x")

    input_inner = tk.Frame(input_card, bg=bg_card)
    input_inner.pack(pady=20, padx=20)

    # Target IP
    ip_frame = tk.Frame(input_inner, bg=bg_card)
    ip_frame.grid(row=0, column=0, padx=15, pady=10, sticky="w")

    tk.Label(
        ip_frame,
        text="Target IP",
        bg=bg_card,
        fg=accent_cyan,
        font=("Segoe UI", 11, "bold")
    ).pack(anchor="w")

    ip_entry = tk.Entry(
        ip_frame,
        bg=entry_bg,
        fg=fg_primary,
        insertbackground=accent_green,
        relief="flat",
        font=("Consolas", 11),
        width=20,
        highlightbackground=border_color,
        highlightthickness=1
    )
    ip_entry.pack(pady=(5, 0), ipady=6)
    ip_entry.insert(0, "127.0.0.1")

    # Start Port
    start_frame = tk.Frame(input_inner, bg=bg_card)
    start_frame.grid(row=0, column=1, padx=15, pady=10, sticky="w")

    tk.Label(
        start_frame,
        text="Start Port",
        bg=bg_card,
        fg=accent_cyan,
        font=("Segoe UI", 11, "bold")
    ).pack(anchor="w")

    start_entry = tk.Entry(
        start_frame,
        bg=entry_bg,
        fg=fg_primary,
        insertbackground=accent_green,
        relief="flat",
        font=("Consolas", 11),
        width=12,
        highlightbackground=border_color,
        highlightthickness=1
    )
    start_entry.pack(pady=(5, 0), ipady=6)
    start_entry.insert(0, "1")

    # End Port
    end_frame = tk.Frame(input_inner, bg=bg_card)
    end_frame.grid(row=0, column=2, padx=15, pady=10, sticky="w")

    tk.Label(
        end_frame,
        text="End Port",
        bg=bg_card,
        fg=accent_cyan,
        font=("Segoe UI", 11, "bold")
    ).pack(anchor="w")

    end_entry = tk.Entry(
        end_frame,
        bg=entry_bg,
        fg=fg_primary,
        insertbackground=accent_green,
        relief="flat",
        font=("Consolas", 11),
        width=12,
        highlightbackground=border_color,
        highlightthickness=1
    )
    end_entry.pack(pady=(5, 0), ipady=6)
    end_entry.insert(0, "1000")

    # ============= OUTPUT CARD =============
    output_card = tk.Frame(root, bg=bg_card, highlightbackground=border_color, highlightthickness=2)
    output_card.pack(pady=(0, 20), padx=30, fill="both", expand=True)

    output_label = tk.Label(
        output_card,
        text="Scan Output",
        bg=bg_card,
        fg=accent_cyan,
        font=("Segoe UI", 12, "bold")
    )
    output_label.pack(anchor="w", padx=20, pady=(15, 5))

    # Scrollable Text Box
    text_frame = tk.Frame(output_card, bg=bg_card)
    text_frame.pack(padx=20, pady=(0, 15), fill="both", expand=True)

    result_box = tk.Text(
        text_frame,
        bg=bg_header,
        fg=fg_primary,
        insertbackground=accent_green,
        font=("Consolas", 10),
        relief="flat",
        wrap="word",
        highlightbackground=border_color,
        highlightthickness=1
    )
    result_box.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(text_frame, command=result_box.yview)
    scrollbar.pack(side="right", fill="y")
    result_box.config(yscrollcommand=scrollbar.set)

    # Configure text tags for colored output
    result_box.tag_config("open", foreground=accent_green, font=("Consolas", 10, "bold"))
    result_box.tag_config("info", foreground=accent_cyan)
    result_box.tag_config("service", foreground="#fbbf24")
    result_box.tag_config("summary", foreground="#a78bfa", font=("Consolas", 11, "bold"))

    # ============= PROGRESS & STATUS BAR =============
    progress_frame = tk.Frame(root, bg=bg_dark)
    progress_frame.pack(pady=(0, 10), padx=30, fill="x")

    # Style for progress bar
    style = ttk.Style()
    style.theme_use('default')
    style.configure(
        "Custom.Horizontal.TProgressbar",
        background=accent_green,
        troughcolor=bg_card,
        bordercolor=border_color,
        lightcolor=accent_green,
        darkcolor=accent_green
    )

    progress = ttk.Progressbar(
        progress_frame,
        length=800,
        mode='determinate',
        style="Custom.Horizontal.TProgressbar"
    )
    progress.pack(pady=(0, 8))

    # Info bar: Progress % | Elapsed Time | Open Ports
    info_bar = tk.Frame(progress_frame, bg=bg_dark)
    info_bar.pack(fill="x")

    percent_label = tk.Label(
        info_bar,
        text="Progress: 0%",
        bg=bg_dark,
        fg=fg_secondary,
        font=("Segoe UI", 10)
    )
    percent_label.pack(side="left", padx=10)

    time_label = tk.Label(
        info_bar,
        text="Elapsed: 0.0s",
        bg=bg_dark,
        fg=fg_secondary,
        font=("Segoe UI", 10)
    )
    time_label.pack(side="left", padx=10)

    open_count_label = tk.Label(
        info_bar,
        text="Open Ports: 0",
        bg=bg_dark,
        fg=accent_green,
        font=("Segoe UI", 10, "bold")
    )
    open_count_label.pack(side="right", padx=10)

    # ============= BUTTON FUNCTIONS =============
    def save_results():
        file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
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

        status_var.set("● Stopped")
        start_btn.config(state="normal")
        stop_btn.config(state="disabled")

    def start_scan():
        global stop_flag, open_ports, executor_global, is_scanning

        if is_scanning:
            return

        try:
            ip = ip_entry.get().strip()
            start = int(start_entry.get())
            end = int(end_entry.get())

            if not ip or start < 1 or end > 65535 or start > end:
                result_box.delete(1.0, tk.END)
                result_box.insert(tk.END, "[ERROR] Invalid input values!\n", "info")
                return

        except ValueError:
            result_box.delete(1.0, tk.END)
            result_box.insert(tk.END, "[ERROR] Ports must be numbers!\n", "info")
            return

        stop_flag = False
        is_scanning = True
        open_ports = []

        result_box.delete(1.0, tk.END)
        status_var.set("● Scanning...")

        result_box.insert(tk.END, f"[+] Starting scan on ", "info")
        result_box.insert(tk.END, f"{ip}", "open")
        result_box.insert(tk.END, f" (Ports {start}-{end})\n\n", "info")

        total = end - start + 1
        progress["maximum"] = total
        progress["value"] = 0
        percent_label.config(text="Progress: 0%")
        time_label.config(text="Elapsed: 0.0s")
        open_count_label.config(text="Open Ports: 0")

        start_btn.config(state="disabled")
        stop_btn.config(state="normal")

        start_time = time.time()

        def update_time():
            if is_scanning:
                elapsed = round(time.time() - start_time, 1)
                time_label.config(text=f"Elapsed: {elapsed}s")
                root.after(100, update_time)

        update_time()

        def update(res):
            root.after(0, lambda: safe_update(res))

        def safe_update(res):
            if res is None:
                return

            progress["value"] += 1
            percent = int((progress["value"] / total) * 100)
            percent_label.config(text=f"Progress: {percent}%")

            if res:
                # Parse and colorize output
                lines = res.split("\n")
                for line in lines:
                    if "[OPEN]" in line:
                        result_box.insert(tk.END, line + "\n", "open")
                        open_ports.append(res)
                        open_count_label.config(text=f"Open Ports: {len(open_ports)}")
                    elif "Service" in line or "Version" in line or "Banner" in line:
                        result_box.insert(tk.END, line + "\n", "service")
                    else:
                        result_box.insert(tk.END, line + "\n")

                result_box.see(tk.END)

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

                status_var.set("● Completed" if not stop_flag else "● Stopped")

                result_box.insert(tk.END, "\n")
                result_box.insert(tk.END, "=== SCAN SUMMARY ===\n", "summary")
                result_box.insert(tk.END, f"Target : {ip}\n", "info")
                result_box.insert(tk.END, f"Ports  : {start}-{end}\n", "info")
                result_box.insert(tk.END, f"Open   : {len(open_ports)}\n", "open")
                result_box.insert(tk.END, f"Time   : {elapsed}s\n", "info")

                start_btn.config(state="normal")
                stop_btn.config(state="disabled")

            root.after(0, finish)

        threading.Thread(target=run, daemon=True).start()

    # ============= BUTTONS =============
    btn_frame = tk.Frame(root, bg=bg_dark)
    btn_frame.pack(pady=(0, 20))

    start_btn = styled_button(btn_frame, "▶ Start Scan", start_scan, btn_green, btn_green_hover)
    start_btn.grid(row=0, column=0, padx=10)

    stop_btn = styled_button(btn_frame, "■ Stop", stop_scan, btn_red, btn_red_hover)
    stop_btn.grid(row=0, column=1, padx=10)
    stop_btn.config(state="disabled")

    save_btn = styled_button(btn_frame, "💾 Save Results", save_results, btn_blue, btn_blue_hover)
    save_btn.grid(row=0, column=2, padx=10)

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
