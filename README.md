# 🔍 MVTool v2.6

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Mac-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-success)
![Threads](https://img.shields.io/badge/Multi--Threaded-Yes-orange)
![GUI](https://img.shields.io/badge/GUI-Tkinter-blueviolet)

![Version](https://img.shields.io/badge/Version-2.6-blue)
![Maintained](https://img.shields.io/badge/Maintained-Yes-brightgreen)
![Made With](https://img.shields.io/badge/Made%20With-Python-blue?logo=python)
![Security](https://img.shields.io/badge/Use-Ethical%20Only-red)
![PRs](https://img.shields.io/badge/PRs-Welcome-brightgreen)
![Contributions](https://img.shields.io/badge/Contributions-Welcome-orange)

---

## 🔍 MVTool v2.6

**Multi-Threaded Port Scanner with CLI & GUI (Python)**

MVTool is a fast, lightweight TCP port scanner built in Python with both Command Line Interface (CLI) and Graphical User Interface (GUI). It supports multi-threaded scanning, banner grabbing, service detection, and version extraction.

---

## 🚀 Features

### ⚡ Core Features

* Multi-threaded TCP port scanning
* Fast scanning using `ThreadPoolExecutor`
* Banner grabbing for service identification
* Service detection (HTTP, SSH, FTP, etc.)
* Version extraction from banners
* Scan summary (open ports, time taken)

### 💻 CLI Features

* Scan specific ports (`-p`)
* Scan port range (`--range`)
* Scan all ports (`--all-port`)
* Adjustable thread count (`--t`)
* Colored terminal output
* Clean summary report

### 🖥️ GUI Features

* Simple and modern interface (Tkinter)
* Start / Stop scan functionality
* Live progress bar with percentage
* Real-time open port display
* Save scan results to file
* Status indicator (Ready / Scanning / Stopped / Completed)

---

## 📦 Installation

### 1. Clone the Repository

```bash id="p7y1ht"
git clone https://github.com/WhiteHatWolf/WHW-tools.git
cd mvtool
```

### 2. Run the Tool

No external dependencies required (uses Python standard library).

---

## 🛠️ Usage

### ▶️ CLI Mode

#### Scan common ports

```bash id="kp5b6q"
python mvtool.py <target_ip>
```

#### Scan specific ports

```bash id="x7kl5y"
python mvtool.py <target_ip> -p 22,80,443
```

#### Scan port range

```bash id="0kttn1"
python mvtool.py <target_ip> --range 1-1000
```

#### Scan all ports

```bash id="o3gq5n"
python mvtool.py <target_ip> --all-port
```

#### Set thread count

```bash id="jv2n3s"
python mvtool.py <target_ip> --range 1-1000 --t 200
```

---

### 🖥️ GUI Mode

```bash id="e6i0he"
python mvtool.py --gui
```

#### GUI Controls

* **Start Scan** → Begin scanning
* **Stop** → Stop scanning safely
* **Save Results** → Export results to `.txt`

---

## 📊 Sample Output

```id="6k5a1v"
[OPEN] Port 22
├─ Service : SSH
├─ Version : OpenSSH_7.6p1 Ubuntu

[OPEN] Port 80
├─ Service : HTTP
├─ Version : Apache/2.4.29 (Ubuntu)

=== SCAN SUMMARY ===
Target : 10.48.145.16
Ports : 1-65535
Open : 3
Time : 43.98s
```

---

## 🧠 How It Works

* Uses TCP connect scan (`socket.connect_ex`)
* Sends probes to grab banners
* Detects service using:

  * Known port mappings
  * Banner content
* Extracts versions using regex

---

## ⚠️ Disclaimer

This tool is intended for:

* Educational purposes
* Ethical hacking practice
* Authorized penetration testing

🚫 **Do NOT use on networks without permission.**

---

## 📌 Future Improvements

* UDP scanning
* OS fingerprinting
* JSON / HTML report export
* CVE lookup integration
* Nmap-like scripting engine

---

## 👨‍💻 Author

**MV**
Cybersecurity Enthusiast | Pentesting | Tool Development

---

## ⭐ Support

If you like this project:

* Star the repo ⭐
* Fork it 🍴
* Contribute improvements 🤝
