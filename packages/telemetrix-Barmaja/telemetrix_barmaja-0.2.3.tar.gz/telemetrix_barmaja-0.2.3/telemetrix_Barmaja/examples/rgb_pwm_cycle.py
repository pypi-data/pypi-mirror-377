
"""Cycle an RGB LED using PWM pins 9,10,11."""
import time
from telemetrix_Barmaja import TelemetrixSync, OUTPUT

board = TelemetrixSync()
R, G, B = 9, 10, 11
for p in (R, G, B): board.pinMode(p, OUTPUT)

def set_rgb(r,g,b):
    board.analogWrite(R, r); board.analogWrite(G, g); board.analogWrite(B, b)

try:
    while True:
        for v in range(0,256,5): set_rgb(v,0,0); time.sleep(0.01)
        for v in range(0,256,5): set_rgb(255,v,0); time.sleep(0.01)
        for v in range(0,256,5): set_rgb(255,255,v); time.sleep(0.01)
finally:
    set_rgb(0,0,0)
    board.shutdown()
