
"""Sweep a servo on pin 9 (requires servo support in firmware)."""
import time
from telemetrix_Barmaja import TelemetrixSync

board = TelemetrixSync()
SERVO_PIN = 9

try:
    while True:
        for angle in range(0,181,3):
            board.servoWrite(SERVO_PIN, angle); time.sleep(0.02)
        for angle in range(180,-1,-3):
            board.servoWrite(SERVO_PIN, angle); time.sleep(0.02)
finally:
    board.shutdown()
