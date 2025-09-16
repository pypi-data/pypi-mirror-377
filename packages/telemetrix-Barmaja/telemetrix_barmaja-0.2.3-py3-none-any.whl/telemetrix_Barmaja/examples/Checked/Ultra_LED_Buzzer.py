import time
from telemetrix_Barmaja import TelemetrixSync, OUTPUT, HIGH, LOW

board = TelemetrixSync()

TRIG, ECHO = 7, 8
LED, BUZZ = 13, 12

board.pinMode(LED, OUTPUT)
board.pinMode(BUZZ, OUTPUT)

# Initialize sonar
board.sonarBegin(TRIG, ECHO)
board.sonarEnableReports()  # <-- Enable firmware reporting

try:
    while True:
        try:
            d = board.sonarReadCM(TRIG, ECHO)
            print(f"Distance: {d} cm")
        except RuntimeError:
            print("Waiting for first sonar data...")
            d = 999

        # LED logic
        board.digitalWrite(LED, HIGH if d < 30 else LOW)

        # Buzzer logic
        gap = max(0.03, min(0.6, d / 150.0))
        board.digitalWrite(BUZZ, HIGH)
        time.sleep(0.04)
        board.digitalWrite(BUZZ, LOW)
        time.sleep(gap)

finally:
    board.digitalWrite(LED, LOW)
    board.digitalWrite(BUZZ, LOW)
    board.shutdown()
