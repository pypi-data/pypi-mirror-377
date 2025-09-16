
"""Turn LED on in the dark using LDR on A0."""
"""GND--Resistor-A0-LDR--5V"""
import time
from telemetrix_Barmaja import TelemetrixSync, OUTPUT, HIGH, LOW, A0

board = TelemetrixSync()
LED = 13
THRESH = 600  # adjust to your room
board.pinMode(LED, OUTPUT)

try:
    while True:
        val = board.analogRead(A0)  # 0..1023
        board.digitalWrite(LED, HIGH if val < THRESH else LOW)
        time.sleep(0.05)
        print("input =" ,val)
finally:
    board.digitalWrite(LED, LOW)
    board.shutdown()
