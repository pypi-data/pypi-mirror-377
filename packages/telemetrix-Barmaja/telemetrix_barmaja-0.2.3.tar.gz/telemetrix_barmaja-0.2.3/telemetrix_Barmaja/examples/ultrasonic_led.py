
"""LED on if distance < 30 cm using HC-SR04 (TRIG=7, ECHO=8)."""
import time
from telemetrix_Barmaja import TelemetrixSync, OUTPUT, HIGH, LOW

board = TelemetrixSync()
TRIG, ECHO = 7, 8
LED = 13
board.pinMode(LED, OUTPUT)

try:
    while True:
        try:
            d = board.sonarReadCM(TRIG, ECHO)
        except RuntimeError:
            d = 999
        board.digitalWrite(LED, HIGH if d < 30 else LOW)
        time.sleep(0.05)
finally:
    board.digitalWrite(LED, LOW)
    board.shutdown()
