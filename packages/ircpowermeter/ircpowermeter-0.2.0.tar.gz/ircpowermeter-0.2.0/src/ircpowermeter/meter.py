import re
import time
from typing import Optional
import serial  # pyserial

DEFAULT_BAUD = 115200  # CDC-ACM typically ignores this but pyserial wants a value.
DEFAULT_TIMEOUT = 0.5

class MeterError(Exception):
    pass

class ImmersionRCPowerMeter:
    """
    Minimal interface for the ImmersionRC RF Power Meter v2 over USB CDC.

    Known commands (ASCII):
      V  -> firmware version string
      D  -> current average power (dBm)
      E  -> current peak power (dBm)
      F  -> query current frequency (returns MHz)
      F<i> -> set frequency by index (0=first supported, 1=next, ...)

    Source: product manual (USB Interface (CDC) section).
    """
    def __init__(self, device: str = "/dev/ttyACM0", baud: int = DEFAULT_BAUD, timeout: float = DEFAULT_TIMEOUT):
        try:
            self._ser = serial.Serial(device, baudrate=baud, timeout=timeout)
        except Exception as e:
            raise MeterError(f"Failed to open serial device {device}: {e}") from e

    def close(self):
        try:
            self._ser.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    # ---- low-level ----
    def _cmd(self, cmd: str) -> str:
        """Send a command and read a single line response (stripped)."""
        if not cmd.endswith("\n"):
            cmd = cmd + "\n"
        # Clear input buffer to avoid stale lines
        try:
            self._ser.reset_input_buffer()
        except Exception:
            pass

        self._ser.write(cmd.encode("ascii"))
        self._ser.flush()
        line = self._ser.readline()  # reads up to newline or timeout
        if not line:
            # one quick retry
            time.sleep(0.05)
            line = self._ser.readline()
        if not line:
            raise MeterError("No response from meter (timeout).")
        try:
            text = line.decode("utf-8", errors="replace").strip()
        except Exception as e:
            raise MeterError(f"Invalid response bytes: {line!r} ({e})")
        return text

    # ---- high-level ----
    def get_version(self) -> str:
        return self._cmd("V")

    def get_avg_dbm(self) -> float:
        return _parse_dbm(self._cmd("D"))

    def get_peak_dbm(self) -> float:
        return _parse_dbm(self._cmd("E"))

    def get_frequency_mhz(self) -> float:
        # manual: F (no args) = query current freq
        resp = self._cmd("F")
        # Accept "5800" or "5800 MHz" or similar
        m = re.search(r"([-+]?\d+(?:\.\d+)?)", resp)
        if not m:
            raise MeterError(f"Unexpected frequency response: {resp!r}")
        return float(m.group(1))

    def set_frequency_index(self, idx: int) -> str:
        if idx < 0:
            raise ValueError("idx must be >= 0")
        return self._cmd(f"F{idx}")

def _parse_dbm(s: str) -> float:
    """
    Extract the first float from the line. The meter typically returns a number,
    but we accept forms like '-14.23 dBm'.
    """
    m = re.search(r"([-+]?\d+(?:\.\d+)?)", s)
    if not m:
        raise MeterError(f"Unexpected dBm response: {s!r}")
    return float(m.group(1))
