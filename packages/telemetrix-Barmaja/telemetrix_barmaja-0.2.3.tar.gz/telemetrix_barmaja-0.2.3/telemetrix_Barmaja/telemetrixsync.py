"""
telemetrix_Barmaja.telemetrixsync
- Works with telemetrix==1.43
- Arduino-style API with robust fallbacks (no tmx import needed)
- Features:
  * pinMode / digitalWrite / digitalRead
  * analogRead (with callback fallback)
  * analogWrite (bridges pwm/analog variants)
  * Servo (if firmware enabled)
  * Ultrasonic HC-SR04 helpers
  * DHT11/DHT22 helpers
  * I2C begin/read/write helpers
"""

import time
import threading

try:
    from telemetrix import telemetrix
except Exception as e:
    raise RuntimeError("telemetrix package is required. Try: pip install telemetrix==1.43") from e

# Arduino-like constants
HIGH, LOW = 1, 0
OUTPUT, INPUT, INPUT_PULLUP = 1, 0, 2
A0, A1, A2, A3, A4, A5 = 0, 1, 2, 3, 4, 5

_ctx = None


class _Ctx:
    def __init__(self, com_port=None, **kwargs):
        # Open Telemetrix board (auto-detect if com_port is None)
        self.board = telemetrix.Telemetrix() if com_port is None else telemetrix.Telemetrix(com_port=com_port, **kwargs)

        # Detect method variants across Telemetrix versions
        self._set_pwm    = self._detect(["set_pin_mode_pwm_output", "set_pin_mode_analog_output"])
        self._pwm_write  = self._detect(["pwm_write", "analog_write"])
        self._set_dout   = self._detect(["set_pin_mode_digital_output", "set_pin_mode_output"])
        self._set_din    = self._detect(["set_pin_mode_digital_input"])
        self._set_din_pu = getattr(self.board, "set_pin_mode_digital_input_pullup", None)
        self._set_ain    = self._detect(["set_pin_mode_analog_input"])
        self._digital_read = getattr(self.board, "digital_read", None)
        self._analog_read  = getattr(self.board, "analog_read", None)
        self._set_servo    = getattr(self.board, "set_pin_mode_servo", None)
        self._servo_write  = getattr(self.board, "servo_write", None)
        self._set_sonar    = getattr(self.board, "set_pin_mode_sonar", None)
        self._sonar_read   = getattr(self.board, "sonar_read", None)
        # I2C (depends on firmware)
        self._i2c_begin = getattr(self.board, "i2c_begin", None)
        self._i2c_read  = getattr(self.board, "i2c_read",  None)
        self._i2c_write = getattr(self.board, "i2c_write", None)

        self._sonar_inited = set()
        self._sonar_cache = {}   # trig_pin -> last distance (cm, int)
        self._sonar_cbs = {}     # keep callbacks alive
        

        # State
        self._dout = set()
        self._din = {}         # pin -> "in"/"in_pu"
        self._ain = set()
        self._pwm_inited = set()
        self._servo_inited = set()
        self._sonar_inited = set()
        self._t0 = int(time.time() * 1000)

        # Caches & locks (for callback fallbacks)
        self._lock = threading.Lock()
        self._analog_cache = {}
        self._digital_cache = {}

        # DHT cache: pin -> {"t": float|None, "h": float|None, "ts": float}
        self._dht_cache = {}
        self._dht_cbs = {}          # <— keep DHT callbacks alive


        # I2C read cache: (port, addr, reg) -> bytes
        self._i2c_cache = {}
        

        # track which I2C ports we already started
        self._i2c_started = set()

    # ---------- helpers ----------
    def _detect(self, names):
        for n in names:
            if hasattr(self.board, n):
                return getattr(self.board, n)
        def _missing(*_args, **_kwargs):
            raise RuntimeError(f"Telemetrix method missing; tried {names}")
        return _missing

    # ---------- pin mode & IO ----------
    def pinMode(self, pin, mode):
        if mode == OUTPUT:
            self._set_dout(pin); self._dout.add(pin)
        elif mode == INPUT:
            try:
                if self._digital_read is None:
                    self._set_din(pin, callback=self._on_digital)
                else:
                    self._set_din(pin)
            except TypeError:
                self._set_din(pin)
            self._din[pin] = "in"
        elif mode == INPUT_PULLUP:
            if self._set_din_pu:
                try:
                    if self._digital_read is None:
                        self._set_din_pu(pin, callback=self._on_digital)
                    else:
                        self._set_din_pu(pin)
                except TypeError:
                    self._set_din_pu(pin)
            else:
                try:
                    if self._digital_read is None:
                        self._set_din(pin, callback=self._on_digital)
                    else:
                        self._set_din(pin)
                except TypeError:
                    self._set_din(pin)
            self._din[pin] = "in_pu"
        else:
            raise ValueError("pinMode: use OUTPUT, INPUT, or INPUT_PULLUP")

    def digitalWrite(self, pin, value):
        if pin not in self._dout:
            self._set_dout(pin); self._dout.add(pin)
        self.board.digital_write(pin, 1 if value else 0)

    def digitalRead(self, pin, timeout_ms=100):
        # direct path
        if self._digital_read:
            if pin not in self._din:
                self._set_din(pin); self._din[pin] = "in"
            return 1 if self._digital_read(pin) else 0

        # fallback: wait for cached value via callback
        if pin not in self._din:
            try:
                self._set_din(pin, callback=self._on_digital)
            except TypeError:
                self._set_din(pin)
            self._din[pin] = "in"

        end = time.time() + timeout_ms / 1000.0
        while time.time() < end:
            with self._lock:
                if pin in self._digital_cache:
                    return 1 if self._digital_cache[pin] else 0
            time.sleep(0.005)
        return 0

    def analogRead(self, apin, timeout_ms=120):
        # direct path
        if self._analog_read:
            if apin not in self._ain:
                self._set_ain(apin); self._ain.add(apin)
            v = self._analog_read(apin)
            return 0 if v is None else int(v)

        # fallback with callback
        if apin not in self._ain:
            try:
                self._set_ain(apin, callback=self._on_analog)
            except TypeError:
                self._set_ain(apin)
            self._ain.add(apin)

        end = time.time() + (timeout_ms / 1000.0)
        while time.time() < end:
            with self._lock:
                if apin in self._analog_cache:
                    return int(self._analog_cache[apin])
            time.sleep(0.005)
        return 0

    def analogWrite(self, pin, val):
        if pin not in self._pwm_inited:
            self._set_pwm(pin); self._pwm_inited.add(pin)
        self._pwm_write(pin, int(val))

    def delay(self, ms): time.sleep(ms / 1000.0)
    def millis(self): return int(time.time() * 1000) - self._t0

    # ---------- callback parsers ----------
    def _on_analog(self, data):
        try:
            if isinstance(data, (list, tuple)) and len(data) >= 3:
                pin, val = int(data[1]), int(data[2])
            elif isinstance(data, dict):
                pin, val = int(data.get("pin")), int(data.get("value"))
            else:
                return
            with self._lock:
                self._analog_cache[pin] = val
        except Exception:
            pass

    def _on_digital(self, data):
        try:
            if isinstance(data, (list, tuple)) and len(data) >= 3:
                pin, val = int(data[1]), 1 if data[2] else 0
            elif isinstance(data, dict):
                pin, val = int(data.get("pin")), 1 if data.get("value") else 0
            else:
                return
            with self._lock:
                self._digital_cache[pin] = val
        except Exception:
            pass

    # ---------- Servo ----------
    def servoWrite(self, pin, angle):
        if self._set_servo is None or self._servo_write is None:
            raise RuntimeError("Servo not supported by this Telemetrix firmware/version.")
        if pin not in self._servo_inited:
            try:
                self._set_servo(pin)
            except TypeError:
                self._set_servo(pin, 544, 2400)  # min/max pulse fallback
            self._servo_inited.add(pin)
        self._servo_write(pin, int(angle))

    # ---------- Ultrasonic ----------
    def _sonar_cb_factory(self, trig_pin_expected: int):
        def _cb(msg):
            try:
                # Variant B (your firmware): [11, trig, distance_mm, timestamp]
                if isinstance(msg, (list, tuple)) and len(msg) >= 4 and int(msg[0]) == 11:
                    trig = int(msg[1])
                    if trig == int(trig_pin_expected):
                        dist_mm = int(msg[2])
                        dist_cm = dist_mm #/ 10.0  # Convert mm -> cm

                        # ✅ Store distance in the cache so sonarReadCM() works
                        with self._lock:
                            self._sonar_cache[trig] = dist_cm

                        # Debug line (optional)
                        # print("RAW SONAR:", msg)
            except Exception:
                pass
        return _cb


    def sonarBegin(self, trig_pin, echo_pin):
        if self._set_sonar is None:
            raise RuntimeError("Sonar not supported by this Telemetrix firmware/version.")
        key = (trig_pin, echo_pin)
        if key in self._sonar_inited:
            return

        cb = self._sonar_cb_factory(trig_pin)
        self._sonar_cbs[key] = cb  # keep strong ref (prevents GC)

        # Try multiple Telemetrix client signatures in order
        ok = False
        try:
            self._set_sonar(trig_pin, echo_pin, callback=cb); ok = True
        except TypeError:
            try:
                self._set_sonar(trig_pin, echo_pin, cb=cb); ok = True
            except TypeError:
                try:
                    self._set_sonar(trig_pin, echo_pin, cb); ok = True  # positional
                except TypeError:
                    pass

        # If none accepted a callback, still set sonar so firmware streams reports
        if not ok:
            self._set_sonar(trig_pin, echo_pin)

        # Ensure firmware-side reporting is on
        if hasattr(self.board, "sonar_enable"):
            try: self.board.sonar_enable()
            except: pass
        if hasattr(self.board, "enable_all_reports"):
            try: self.board.enable_all_reports()
            except: pass

        self._sonar_inited.add(key)


    def sonarReadCM(self, trig_pin, echo_pin):
        """
        If sonar_read() exists, use it. Otherwise return last cached report.
        Raises RuntimeError if nothing has been cached yet.
        """
        # fast path if available on some builds
        if self._sonar_read is not None:
            key = (trig_pin, echo_pin)
            if key not in self._sonar_inited:
                self.sonarBegin(trig_pin, echo_pin)
            return self._sonar_read(trig_pin, echo_pin)

        # callback-based path
        key = (trig_pin, echo_pin)
        if key not in self._sonar_inited:
            self.sonarBegin(trig_pin, echo_pin)

        with self._lock:
            if trig_pin in self._sonar_cache:
                return self._sonar_cache[trig_pin]

        # No report has arrived yet
        raise RuntimeError("No sonar reading available yet (waiting for first report).")


    def sonarDisableReports(self):
        if hasattr(self.board, "sonar_disable"):
            self.board.sonar_disable()

    def sonarEnableReports(self):
        if hasattr(self.board, "sonar_enable"):
            self.board.sonar_enable()

    # ---------- DHT (11/22) ----------
    def _dht_callback_factory(self, pin):
        """
        Parse DHT sensor messages and **always store as (temperature, humidity)**.
        """
        import time as _time

        def _cb(msg):
            #print(msg
            try:
                # --- Canonical Telemetrix DHT format ---
                # [len, 12, subtype(0 OK), pin, dht_type,
                #  hum_sign, temp_sign, hum_int, hum_frac, temp_int, temp_frac]
                if isinstance(msg, (list, tuple)) and len(msg) >= 11 and int(msg[1]) == 12:
                    if int(msg[2]) != 0:
                        # Error reading
                        with self._lock:
                            self._dht_cache[pin] = {"t": None, "h": None, "ts": _time.time()}
                        return

                    hum = int(msg[7]) + int(msg[8]) / 100.0
                    if int(msg[5]) == 1:  # negative humidity (rare)
                        hum = -hum

                    temp = int(msg[9]) + int(msg[10]) / 100.0
                    if int(msg[6]) == 1:  # negative temp
                        temp = -temp

                    # ✅ Store as temp, hum
                    with self._lock:
                        self._dht_cache[pin] = {"t": temp, "h": hum, "ts": _time.time()}
                    return

                # --- Compact float list (your raw example) ---
                # [12, ?, pin, dht_type, humidity, temperature, timestamp]
                if isinstance(msg, (list, tuple)) and len(msg) >= 6 and int(msg[0]) == 12:
                    hum = float(msg[4])
                    temp = float(msg[5])

                    # optional sanity swap in case a fork flips them
                    if not (0.0 <= hum <= 100.0) and (-40.0 <= hum <= 85.0) and (0.0 <= temp <= 100.0):
                        temp, hum = hum, temp

                    with self._lock:
                        self._dht_cache[pin] = {"t": temp, "h": hum, "ts": _time.time()}
                    return


                # --- Dictionary style (rare older builds) ---
                # {"type":12, "pin":N, "h":xx.xx, "t":yy.yy, "ok":True/0}
                if isinstance(msg, dict) and int(msg.get("type", -1)) == 12:
                    ok = msg.get("ok", 0)
                    if ok in (True, 0):
                        temperature = float(msg.get("t", float("nan")))
                        humidity = float(msg.get("h", float("nan")))
                        with self._lock:
                            self._dht_cache[pin] = {"t": temperature, "h": humidity, "ts": _time.time()}
                    else:
                        with self._lock:
                            self._dht_cache[pin] = {"t": None, "h": None, "ts": _time.time()}
                    return

            except Exception:
                # Ignore corrupted or partial frames
                pass

        return _cb





    def dhtBegin(self, pin, dht_type=11):
        cb = self._dht_callback_factory(pin)
        self._dht_cbs[pin] = cb  # strong ref so callback isn't GC'ed

        # accept both Telemetrix signatures
        try:
            self.board.set_pin_mode_dht(pin, dht_type=dht_type, callback=cb)
        except TypeError:
            self.board.set_pin_mode_dht(pin, cb, dht_type)

        # ensure firmware-side reports are flowing
        if hasattr(self.board, "enable_all_reports"):
            try: self.board.enable_all_reports()
            except: pass

        with self._lock:
            self._dht_cache.setdefault(pin, {"t": None, "h": None, "ts": 0.0})




    def dhtLast(self, pin):
        """
        Return (tempC, humidity) last sample for 'pin', or (None, None) if not yet sampled.
        """
        d = self._dht_cache.get(pin)
        return (None, None) if not d else (d["t"], d["h"])
    # ---------- I2C ----------

    def _ensure_i2c(self, i2c_port: int = 0):
        """Ensure I2C is begun on this port (safe to call multiple times)."""
        if i2c_port in self._i2c_started:
            return
        if self._i2c_begin is None:
            # some builds auto-begin I2C
            self._i2c_started.add(i2c_port)
            return
        try:
            self._i2c_begin(i2c_port)   # newer Telemetrix
        except TypeError:
            self._i2c_begin()           # older Telemetrix (no args)
        self._i2c_started.add(i2c_port)

    def i2cBegin(self, i2c_port: int = 0):
        self._ensure_i2c(i2c_port)

    def i2cWrite(self, address: int, data, *, i2c_port: int = 0):
        """Write bytes to I2C device address."""
        if self._i2c_write is None:
            raise RuntimeError("This Telemetrix build lacks i2c_write().")
        # normalize payload
        if isinstance(data, (bytes, bytearray)):
            payload = list(data)
        else:
            payload = [int(x) & 0xFF for x in data]
        # make sure I2C is begun
        self._ensure_i2c(i2c_port)
        # call Telemetrix (new sig first, then old)
        try:
            self._i2c_write(address, payload, i2c_port=i2c_port)
        except TypeError:
            self._i2c_write(address, payload)

    def _i2c_cb_factory(self, port, addr, reg):
        def _cb(msg):
            # [len, 10(I2C_READ_REPORT), port, nbytes, address, register, data...]
            try:
                if isinstance(msg, (list, tuple)) and len(msg) >= 6 and int(msg[1]) == 10:
                    p = int(msg[2]); n = int(msg[3])
                    a = int(msg[4]); r = int(msg[5])
                    data = bytes(int(x) & 0xFF for x in msg[6:6 + n])
                    with self._lock:
                        self._i2c_cache[(p, a, r)] = data
            except Exception:
                pass
        return _cb

    def i2cRead(self, address: int, register: int, nbytes: int,
                *, stop: bool = True, i2c_port: int = 0, write_register: bool = True,
                timeout_ms: int = 200):
        if not self._i2c_read:
            raise RuntimeError("This Telemetrix build lacks i2c_read()")

        cb = self._i2c_cb_factory(i2c_port, address, register)
        try:
            # keyword sig
            self._i2c_read(address, register, nbytes, stop, i2c_port, write_register, callback=cb)
        except TypeError:
            # positional sig
            self._i2c_read(address, register, nbytes, stop, i2c_port, write_register, cb)

        end = time.time() + timeout_ms / 1000.0
        while time.time() < end:
            with self._lock:
                key = (i2c_port, address, register)
                if key in self._i2c_cache:
                    return self._i2c_cache.pop(key)
            time.sleep(0.005)
        return b""



    # ---------- lifecycle ----------
    def shutdown(self):
        try:
            self.board.shutdown()
        except Exception:
            pass


# ---- module-level singleton API ----
def begin(com_port=None, **kwargs):
    global _ctx
    if _ctx is None:
        _ctx = _Ctx(com_port=com_port, **kwargs)
    return _ctx

def _need():
    if _ctx is None:
        raise RuntimeError("Call TelemetrixSync(...) (or begin(com_port=...)) first.")
    return _ctx

def pinMode(pin, mode):        _need().pinMode(pin, mode)
def digitalWrite(pin, val):    _need().digitalWrite(pin, val)
def digitalRead(pin):          return _need().digitalRead(pin)
def analogRead(apin):          return _need().analogRead(apin)
def analogWrite(pin, val):     _need().analogWrite(pin, val)
def delay(ms):                 _need().delay(ms)
def millis():                  return _need().millis()
def servoWrite(pin, angle):    _need().servoWrite(pin, angle)

def sonarBegin(trig, echo):    _need().sonarBegin(trig, echo)
def sonarReadCM(trig, echo):   return _need().sonarReadCM(trig, echo)
def sonarEnableReports():      _need().sonarEnableReports()
def sonarDisableReports():     _need().sonarDisableReports()

def dhtBegin(pin, dht_type=11):  _need().dhtBegin(pin, dht_type)
def dhtLast(pin):                return _need().dhtLast(pin)


def i2cRead(address, register, nbytes, **kw):  return _need().i2cRead(address, register, nbytes, **kw)
def i2cBegin(i2c_port=0): _need().i2cBegin(i2c_port)
def i2cWrite(address, data, **kw): _need().i2cWrite(address, data, **kw)

def shutdown():                _need().shutdown()
