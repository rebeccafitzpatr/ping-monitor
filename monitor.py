import subprocess
import platform
import re
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.table import Table

# --------------------------
# Host stats tracking
# --------------------------
class HostStats:
    def __init__(self, host, history_len=50):
        self.host = host
        self.latencies = deque(maxlen=history_len)
        self.total_pings = 0
        self.failed_pings = 0

    def record(self, latency):
        self.total_pings += 1
        if latency is None:
            self.failed_pings += 1
        else:
            self.latencies.append(latency)

    def jitter(self):
        if len(self.latencies) < 2:
            return 0
        diffs = [abs(self.latencies[i] - self.latencies[i - 1]) for i in range(1, len(self.latencies))]
        return sum(diffs) / len(diffs)

    def loss_rate(self):
        return 100 * self.failed_pings / self.total_pings if self.total_pings > 0 else 0

    def last_latency(self):
        return self.latencies[-1] if self.latencies else None

# --------------------------
# Windows-friendly ping
# --------------------------
def ping_host(host):
    try:
        output = subprocess.check_output(["ping", "-n", "1", "-w", "100", host], universal_newlines=True)
        match = re.search(r"time[=<](\d+\.?\d*)", output)
        return float(match.group(1)) if match else None
    except subprocess.CalledProcessError:
        return None

# --------------------------
# Monitor and print
# --------------------------
console = Console()
hosts = ["8.8.8.8", "1.1.1.1", "cloudflare.com", "ec2.ap-southeast-2.amazonaws.com", "208.67.222.222"]
stats = {host: HostStats(host) for host in hosts}

def display_stats():
    table = Table(title="🏓 High-Frequency Ping Monitor (Windows)")
    table.add_column("Host")
    table.add_column("Latency (ms)")
    table.add_column("Jitter")
    table.add_column("Loss %")

    for host, stat in stats.items():
        latency = f"{stat.last_latency():.2f}" if stat.last_latency() is not None else "Timeout"
        table.add_row(
            host,
            latency,
            f"{stat.jitter():.2f}",
            f"{stat.loss_rate():.1f}%"
        )
    console.clear()
    console.print(table)

def monitor_loop():
    with ThreadPoolExecutor(max_workers=len(hosts)) as executor:
        while True:
            futures = {executor.submit(ping_host, host): host for host in hosts}
            for future in futures:
                host = futures[future]
                latency = future.result()
                stats[host].record(latency)
            display_stats()
            time.sleep(0.1)  # 100ms between rounds

if __name__ == "__main__":
    try:
        monitor_loop()
    except KeyboardInterrupt:
        print("Stopped by user.")
