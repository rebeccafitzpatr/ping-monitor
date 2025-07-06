# High-Frequency Ping Monitor (Windows)

A real-time, terminal-based Python tool that pings multiple hosts every 100ms, showing:

-   **Latency (ms)** — ping response time
-   **Jitter** — average latency variation
-   **Packet Loss (%)** — % of failed pings
---

## Features

- High-frequency, multi-host pinging (100ms interval)
- Multi-threaded for concurrency
- Real-time terminal dashboard using `rich`
- Optional CSV logging with `--log` flag
- Fully working on Windows (optimized for Windows Terminal / VS Code Terminal)

## Requirements

- Python 3.8 or higher
- Works best on Windows Terminal or VS Code Terminal

### Run the app:

```bash
# Install dependencies in virtual environment
python -m venv venv
venv\Scripts\activate
pip install rich plotext

# Run the live terminal monitor only

python monitor.py
