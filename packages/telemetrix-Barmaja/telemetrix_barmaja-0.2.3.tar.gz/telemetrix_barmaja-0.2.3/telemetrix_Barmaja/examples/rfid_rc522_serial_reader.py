
"""RC522 serial bridge: Arduino sketch prints UID lines; Python reads and prints."""
import serial
ser = serial.Serial('COM6', 9600, timeout=1)  # set to your RC522 sketch COM
try:
    while True:
        line = ser.readline().decode(errors='ignore').strip()
        if line: print(line)
finally:
    ser.close()
