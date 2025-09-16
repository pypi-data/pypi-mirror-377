
"""Fade an LED with PWM on a PWM-capable pin (e.g., 5)."""
import time
from telemetrix_Barmaja import TelemetrixSync, OUTPUT

board = TelemetrixSync()
LED_PWM = 5   # PWM pin (~ symbol)
board.pinMode(LED_PWM, OUTPUT)

try:
    while True:
        for v in range(0, 256, 5):
            board.analogWrite(LED_PWM, v); time.sleep(0.02)
        for v in range(255, -1, -5):
            board.analogWrite(LED_PWM, v); time.sleep(0.02)
finally:
    board.analogWrite(LED_PWM, 0)
    board.shutdown()
