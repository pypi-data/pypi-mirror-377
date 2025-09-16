
"""LM35 controls fan speed via PWM (or LED)."""
import time
from telemetrix_Barmaja import TelemetrixSync, OUTPUT, A0

board = TelemetrixSync()
FAN_PWM = 5
board.pinMode(FAN_PWM, OUTPUT)

MIN_C, MAX_C = 20.0, 40.0

def clamp(x, lo, hi): return lo if x < lo else hi if x > hi else x
def tempC_from_adc(adc): return (adc * 5.0 / 1023.0) * 100.0

try:
    while True:
        adc = board.analogRead(A0)
        tC = tempC_from_adc(adc)
        frac = (clamp(tC, MIN_C, MAX_C) - MIN_C) / (MAX_C - MIN_C)
        pwm = int(frac * 255)
        board.analogWrite(FAN_PWM, pwm)
        print(f"ADC={adc:4d} Temp={tC:5.1f}°C PWM={pwm:3d}")
        time.sleep(0.25)
finally:
    board.analogWrite(FAN_PWM, 0)
    board.shutdown()
