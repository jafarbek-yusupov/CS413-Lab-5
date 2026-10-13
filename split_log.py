"""
log line written by the robot:  pw,encoder4,encoder3,t[,battery_V]   (M4 gets power pw, M3 gets -pw)

usage: python split_log.py log/motor_data_240057.txt motor_data [battery_voltage]
The battery argument is only used for logs without the battery column.
"""
import os
import sys

# wheel_id -> (log column of its encoder, sign of the power its motor got relative to pw, ports)
WHEELS = {
    1: (1, +1, "M4 E4"), # theta_l
    2: (2, -1, "M3 E3"), # theta_r, driven with -pw
}
T_COL = 3
BAT_COL = 4

src = sys.argv[1] if len(sys.argv) > 1 else "log/motor_data_240057.txt"
out = sys.argv[2] if len(sys.argv) > 2 else "motor_data"
battery = sys.argv[3] if len(sys.argv) > 3 else "unknown"

runs = []   # [(pw, [row, ...]), ...] in recording order
with open(src) as f:
    for line in f:
        parts = line.strip().split(",")
        if len(parts) not in (4, 5) or not parts[0].lstrip("-").isdigit():
            continue   # header or a half-written line
        row = [int(float(x)) for x in parts[:4]] + parts[4:]
        # a new run starts when pw changes or the time stamp jumps back
        if not runs or row[0] != runs[-1][0] or row[T_COL] < runs[-1][1][-1][T_COL]:
            runs.append((row[0], []))
        runs[-1][1].append(row)

os.makedirs(out, exist_ok=True)
seen = set()
for pw, rows in runs:
    if pw in seen:
        print("warning: pw %d recorded twice, keeping the later run" % pw)
    seen.add(pw)
    run_battery = rows[0][BAT_COL] if len(rows[0]) > BAT_COL else battery
    for wheel_id, (col, sign, ports) in WHEELS.items():
        pwm = sign * pw
        with open(os.path.join(out, "wheel_%d_v_%d.txt" % (wheel_id, pwm)), "w") as f:
            f.write("# wheel_id: %d\n# ports: %s\n# pwm_percent: %d\n# battery_voltage: %s\n"
                    "# format: time_ms angle_deg\n" % (wheel_id, ports, pwm, run_battery))
            for r in rows:
                f.write("%d %d\n" % (r[T_COL], r[col]))
    print("pw %4d: %3d samples, %4d..%4d ms, battery %s V"
          % (pw, len(rows), rows[0][T_COL], rows[-1][T_COL], run_battery))
print("%d runs -> %d files in %s/" % (len(runs), 2 * len(seen), out))
