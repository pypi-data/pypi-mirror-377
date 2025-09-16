
"""PN532 serial bridge: Arduino sketch prints UIDs at 115200 baud."""
import serial
ser = serial.Serial('COM6', 115200, timeout=1)
try:
    while True:
        line = ser.readline().decode(errors='ignore').strip()
        if line: print(line)
finally:
    ser.close()
