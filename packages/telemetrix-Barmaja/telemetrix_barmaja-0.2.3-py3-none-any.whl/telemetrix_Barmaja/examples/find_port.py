
"""List available serial ports (Windows: COMx)."""
try:
    from serial.tools import list_ports
except Exception:
    raise SystemExit("Install pyserial: pip install pyserial")
for p in list_ports.comports():
    print(f"{p.device}  ->  {p.description}")
