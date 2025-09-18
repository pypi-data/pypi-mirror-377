import argparse
import json
import sys
from .meter import ImmersionRCPowerMeter, MeterError

def main():
    p = argparse.ArgumentParser(description="Query ImmersionRC RF Power Meter v2 over USB CDC.")
    p.add_argument("-d","--device", default="/dev/ttyACM0", help="Serial device (default: /dev/ttyACM0)")
    m = p.add_mutually_exclusive_group()
    m.add_argument("--avg", action="store_true", help="Read average power (dBm) [default]")
    m.add_argument("--peak", action="store_true", help="Read peak power (dBm)")
    p.add_argument("--version", action="store_true", help="Print meter firmware version and exit")
    p.add_argument("--freq", action="store_true", help="Query current frequency (MHz) and exit")
    p.add_argument("--set-freq-index", type=int, help="Set frequency by index (0=first supported)")
    p.add_argument("--json", action="store_true", help="Output JSON (for scripting)")
    p.add_argument("--stream", type=float, metavar="SECS", help="Continuous readings every N seconds")
    args = p.parse_args()

    try:
        with ImmersionRCPowerMeter(device=args.device) as meter:
            if args.version:
                v = meter.get_version()
                return _out({"version": v} if args.json else v, args.json)

            if args.set_freq_index is not None:
                r = meter.set_frequency_index(args.set_freq_index)
                # Many firmwares echo or respond with new freq: just print whatever we get.
                return _out({"response": r} if args.json else r, args.json)

            if args.freq:
                f = meter.get_frequency_mhz()
                return _out({"mhz": f}, True) if args.json else _out(f"{f} MHz", False)

            read_fn = meter.get_peak_dbm if args.peak else meter.get_avg_dbm

            if args.stream:
                import time
                period = max(0.01, args.stream)
                while True:
                    val = read_fn()
                    if args.json:
                        sys.stdout.write(json.dumps({"dbm": val, "mode": "peak" if args.peak else "avg"}) + "\n")
                    else:
                        sys.stdout.write(f"{val:.2f} dBm\n")
                    sys.stdout.flush()
                    time.sleep(period)
            else:
                val = read_fn()
                return _out({"dbm": val, "mode": "peak" if args.peak else "avg"}, True) if args.json else _out(f"{val:.2f}", False)

    except MeterError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)

def _out(x, as_json: bool):
    if as_json:
        print(json.dumps(x))
    else:
        print(x)
