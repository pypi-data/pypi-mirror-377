
"""Buzzer beeps faster when object is closer (HC-SR04)."""
import time
from telemetrix_Barmaja import TelemetrixSync, OUTPUT

board = TelemetrixSync()
TRIG, ECHO = 7, 8
BUZZ = 12
board.pinMode(BUZZ, OUTPUT)

try:
    while True:
        try:
            d = board.sonarReadCM(TRIG, ECHO)
        except RuntimeError:
            d = 1000
        gap = max(0.03, min(0.6, d/150.0))
        board.digitalWrite(BUZZ, 1); time.sleep(0.01)
        board.digitalWrite(BUZZ, 0); time.sleep(gap)
finally:
    board.digitalWrite(BUZZ, 0)
    board.shutdown()
