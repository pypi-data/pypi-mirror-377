from telemetrix_Barmaja import TelemetrixSync, OUTPUT
import time

b = TelemetrixSync(com_port="COM8")
b.dhtBegin(2, dht_type=11)       # D2, DHT11
b.pinMode(5, OUTPUT)             # PWM fan/LED

while True:
    #t, h = b.dhtLast(PIN)  # actually returns (humidity, temperature)

    t, h = b.dhtLast(2)
    if t is not None:
        t = max(20, min(40, t))
        pwm = int((t - 20)/20 * 255)
        b.analogWrite(5, pwm)
        print(f"T={t:.1f}C  H={h:.1f}%  PWM={pwm}")
    time.sleep(0.2)
