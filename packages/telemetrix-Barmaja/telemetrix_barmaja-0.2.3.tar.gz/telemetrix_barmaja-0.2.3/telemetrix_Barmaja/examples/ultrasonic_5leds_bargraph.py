
"""Display distance on 5 LEDs (pins 2..6)."""
import time
from telemetrix_Barmaja import TelemetrixSync, OUTPUT

board = TelemetrixSync()
TRIG, ECHO = 7, 8
LEDS = [2,3,4,5,6]
for p in LEDS: board.pinMode(p, OUTPUT)

def show_level(n):
    for i,p in enumerate(LEDS):
        board.digitalWrite(p, 1 if i < n else 0)

try:
    while True:
        try:
            d = board.sonarReadCM(TRIG, ECHO)
        except RuntimeError:
            d = 200
        lvl = 5 if d<=10 else 4 if d<=30 else 3 if d<=50 else 2 if d<=75 else 1 if d<=100 else 0
        show_level(lvl)
        time.sleep(0.05)
finally:
    show_level(0)
    board.shutdown()
