
"""LM35 -> buzzer ON/OFF above threshold."""
import time
from telemetrix_Barmaja import TelemetrixSync, OUTPUT, HIGH, LOW, A0

board = TelemetrixSync()
BUZZ = 12
THRESH_C = 35.0
board.pinMode(BUZZ, OUTPUT)

def tempC_from_adc(adc): return (adc * 5.0 / 1023.0) * 100.0

try:
    while True:
        tC = tempC_from_adc(board.analogRead(A0))
        board.digitalWrite(BUZZ, HIGH if tC >= THRESH_C else LOW)
        print(f"Temp={tC:5.1f}°C  Alarm={'ON' if tC>=THRESH_C else 'OFF'}")
        time.sleep(0.25)
finally:
    board.digitalWrite(BUZZ, LOW)
    board.shutdown()
