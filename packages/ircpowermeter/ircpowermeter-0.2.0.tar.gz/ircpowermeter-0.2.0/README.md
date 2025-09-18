# ircpowermeter

Tiny Python interface + CLI for the **ImmersionRC RF Power Meter v2** over USB (CDC-ACM).

## Commands the device understands

- `V` → firmware version
- `D` → current **average** power (dBm)
- `E` → current **peak** power (dBm)
- `F` → query current frequency (MHz)
- `F<idx>` → set frequency by index (0 = first supported)

(From the official manual, "USB Interface (CDC)" section.)  

## Examples

```bash
irc-rfpm               # prints avg dBm once
irc-rfpm --peak        # prints peak dBm once
irc-rfpm --json        # {"dbm": -12.45, "mode":"avg"}
irc-rfpm --freq        # prints current MHz
irc-rfpm --set-freq-index 3
irc-rfpm --stream 0.25 # 4 Hz streaming
