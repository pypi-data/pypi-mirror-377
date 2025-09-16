
"""Blink the onboard LED on pin 13 (Arduino Uno)."""
import time
from telemetrix_Barmaja import TelemetrixSync, OUTPUT, HIGH, LOW

board = TelemetrixSync()  # auto-detect port; or TelemetrixSync(com_port="COM6")
LED = 13
board.pinMode(LED, OUTPUT)

try:
    while True:
        board.digitalWrite(LED, HIGH); time.sleep(0.5)
        board.digitalWrite(LED, LOW);  time.sleep(0.5)
finally:
    board.shutdown()
