
# telemetrix_Barmaja (v0.2.1)

Arduino IDE-style **class API** on top of telemetrix (tested with v1.43). Examples are packaged in the wheel at `telemetrix_Barmaja/examples/`.

```python
import time
from telemetrix_Barmaja import TelemetrixSync, OUTPUT, HIGH, LOW

board = TelemetrixSync()  # auto-detect; or TelemetrixSync(com_port="COM6")
board.pinMode(13, OUTPUT)
try:
    while True:
        board.digitalWrite(13, HIGH); time.sleep(0.5)
        board.digitalWrite(13, LOW);  time.sleep(0.5)
finally:
    board.shutdown()
```
