
"""Read HC-SR04 via Telemetrix and print to console (LCD handled on Arduino side)."""
import time
from telemetrix_Barmaja import TelemetrixSync

board = TelemetrixSync()
TRIG, ECHO = 7, 8

try:
    while True:
        try:
            d = board.sonarReadCM(TRIG, ECHO)
            print(f"Distance: {d:.1f} cm")
        except RuntimeError:
            print("Sonar not supported by firmware.")
        time.sleep(0.2)
finally:
    board.shutdown()
