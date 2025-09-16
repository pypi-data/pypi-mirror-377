
"""4x4 keypad lock with a servo on pin 10. Rows:2..5 outputs, Cols:6..9 inputs (pullup)."""
import time
from telemetrix_Barmaja import TelemetrixSync, OUTPUT, INPUT_PULLUP

board = TelemetrixSync()
ROWS = [2,3,4,5]; COLS = [6,7,8,9]
KEYS = [['1','2','3','A'],['4','5','6','B'],['7','8','9','C'],['*','0','#','D']]
SERVO = 10
PASSWORD = "1234"
code = ""

for r in ROWS: board.pinMode(r, OUTPUT); board.digitalWrite(r, 1)
for c in COLS: board.pinMode(c, INPUT_PULLUP)

def scan_key():
    for ri, r in enumerate(ROWS):
        board.digitalWrite(r, 0)
        for ci, c in enumerate(COLS):
            if board.digitalRead(c) == 0:
                board.digitalWrite(r, 1); return KEYS[ri][ci]
        board.digitalWrite(r, 1)
    return None

try:
    while True:
        k = scan_key()
        if k:
            print("Key:", k)
            if k in "0123456789": code += k
            elif k == '#':
                if code == PASSWORD: print("Unlocked!"); board.servoWrite(SERVO, 90)
                else: print("Wrong code"); board.servoWrite(SERVO, 0)
                code = ""
            elif k == '*': code = ""
        time.sleep(0.1)
finally:
    board.shutdown()
