
"""Map LDR (A0) to LED PWM (pin 5)."""
"""GND--Resistor-A0-LDR--5V"""
import time
from telemetrix_Barmaja import TelemetrixSync, OUTPUT, A0

board = TelemetrixSync()
LED_PWM = 5
board.pinMode(LED_PWM, OUTPUT)


while True:
    raw = board.analogRead(A0)          # 0..1023
    pwm = int(255-(raw / 1023) * 255)         # 0..255
    board.analogWrite(LED_PWM, pwm)
    time.sleep(0.04)
    print("A0 =", raw)
    print("pwm =", pwm)


