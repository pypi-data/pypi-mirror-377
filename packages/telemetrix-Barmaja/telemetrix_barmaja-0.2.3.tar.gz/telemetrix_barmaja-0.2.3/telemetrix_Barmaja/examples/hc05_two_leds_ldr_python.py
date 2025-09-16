
"""HC-05 serial: 'r' toggle RED, 'g' toggle GREEN, 'q' -> reply with LDR value from A0."""
import time, serial
from telemetrix_Barmaja import TelemetrixSync, OUTPUT, HIGH, LOW, A0

bt = serial.Serial('COM7', 9600, timeout=0.1)
board = TelemetrixSync()
RED, GREEN = 12, 13
board.pinMode(RED, OUTPUT); board.pinMode(GREEN, OUTPUT)
stateR, stateG = LOW, LOW

try:
    while True:
        ch = bt.read(1).decode(errors='ignore')
        if not ch:
            time.sleep(0.02); continue
        if ch == 'r':
            stateR = HIGH if stateR==LOW else LOW; board.digitalWrite(RED, stateR)
        elif ch == 'g':
            stateG = HIGH if stateG==LOW else LOW; board.digitalWrite(GREEN, stateG)
        elif ch == 'q':
            val = board.analogRead(A0)
            bt.write(f"LDR:{val}\n".encode())
finally:
    board.digitalWrite(RED, LOW); board.digitalWrite(GREEN, LOW)
    board.shutdown(); bt.close()
