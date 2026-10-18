# Software in the loop: the simulation drives the real controller

Version 1.0 kept the Python simulation and the backend apart. This step connects
them without duplicating any control logic. In a software-in-the-loop (SIL) run:

- the **Python plant model** simulates solar generation, building consumption,
  the battery and the grid connection;
- the **real controller** decides what to do in every interval, through the
  whole production path:

```text
Python plant model ──HTTP──▶ ASP.NET Core API ──▶ C# gateway ──C ABI──▶ C++ EnergyController
        ▲                                                                   │
        └──────────────── decision applied to the simulated battery ◀───────┘
```

Decisions are applied only to Python objects (`Battery`, `GridConnection`).
No electrical equipment is involved.

## One interval

1. Compute this interval's generation and consumption from the scenario.
2. Send `POST /api/control/decision` with those values and the battery's state
   of charge **at the start** of the interval. Grid and unresolved energy are 0
   because nothing has been dispatched yet.
3. Apply the decision within physical limits: only surplus can be stored, only
   deficit is supplied, and the battery is bounded by its capacity.
4. Send the remainder to the grid within its power limits. Whatever the grid
   cannot take or supply is recorded as unresolved: curtailed surplus or
   unserved load.
5. Check that energy is conserved:
   `generated + discharged + imported + unserved = consumed + charged + exported + curtailed`.

The same scenario then runs with the Python battery-first strategy as a
reference. That strategy has no power limits and an operating window from
0 kWh to the full capacity.

## Scenarios

`gridflex_simulation.scenario_catalogue` defines four 24-hour days for a
house-sized installation: 12 kW solar, a building load of 0.8 to 7 kW and a
20 kWh battery. At this size, the backend's default controller limits matter:
10 kW charge, 8 kW discharge, and a state of charge between 2 and 20 kWh.

| Scenario | What it shows |
|---|---|
| `sunny-day` | The battery charges from the midday surplus until it is full, then the surplus is exported. The evening peak discharges the battery down to the 2 kWh minimum |
| `cloudy-day` | There is little surplus to store, so most of the evening load is imported |
| `evening-peak` | A full battery meets a 15 kW evening load. Discharge is capped at **8 kW**, and the rest is imported |
| `grid-outage` | No grid: surplus beyond the battery is curtailed, and deficit beyond the battery is unserved |

## Run it

```bash
# Backend: the published image, or a local build (see README)
docker run --rm -p 5080:8080 ghcr.io/kris7011/gridflex-ems-backend:latest

cd simulation
python -m pip install -e .
gridflex-sil --api-url http://localhost:5080 --report-dir ../sil-report
```

Options: `--scenario <name>` (repeatable; all scenarios by default), and
`--wait-seconds` (how long to wait for `/health/ready`).

The command prints a table per scenario and writes:

- `sil-report/<scenario>.json`: every interval with the measurement, the
  decision and the resulting energy flows, plus totals for both strategies;
- `sil-report/index.html`: a self-contained, read-only report with no scripts
  and no external resources. For each scenario it shows energy per hour, the
  state of charge for the C++ controller and the reference, the grid exchange,
  totals, and a table of all decisions. When the API reports its controller
  limits, the state-of-charge chart shades the controller's operating window.

The CI workflow **Software in the Loop**
([`.github/workflows/software-in-the-loop.yml`](../.github/workflows/software-in-the-loop.yml))
builds the backend image, runs all scenarios against it, and uploads the
report as the `software-in-the-loop-report` artifact.

## Example: `evening-peak`

This output was produced locally against the API on `main`, with the native
controller built with MSVC:

```text
Scenario evening-peak: 24 intervals

 hour   solar   load    net  C++ decision        kW   SoC before->after   import  export  unresolved
00:00    0.00   1.51  -1.51  DischargeBattery   1.51   20.00 -> 18.49     0.00    0.00        0.00
01:00    0.00   1.51  -1.51  DischargeBattery   1.51   18.49 -> 16.98     0.00    0.00        0.00
02:00    0.00   1.51  -1.51  DischargeBattery   1.51   16.98 -> 15.47     0.00    0.00        0.00
03:00    0.00   1.51  -1.51  DischargeBattery   1.51   15.47 -> 13.96     0.00    0.00        0.00
04:00    0.00   1.51  -1.51  DischargeBattery   1.51   13.96 -> 12.45     0.00    0.00        0.00
05:00    0.00   2.22  -2.22  DischargeBattery   2.22   12.45 -> 10.23     0.00    0.00        0.00
06:00    1.23   6.48  -5.25  DischargeBattery   5.25   10.23 ->  4.98     0.00    0.00        0.00
07:00    3.62  10.74  -7.12  DischargeBattery   2.98    4.98 ->  2.00     4.13    0.00        0.00
08:00    5.79   7.90  -2.11  Idle               0.00    2.00 ->  2.00     2.11    0.00        0.00
09:00    7.64   3.64   4.00  ChargeBattery      4.00    2.00 ->  6.00     0.00    0.00        0.00
10:00    9.03   3.64   5.39  ChargeBattery      5.39    6.00 -> 11.39     0.00    0.00        0.00
11:00    9.90   3.64   6.26  ChargeBattery      6.26   11.39 -> 17.65     0.00    0.00        0.00
12:00   10.20   4.35   5.85  ChargeBattery      2.35   17.65 -> 20.00     0.00    3.50        0.00
13:00    9.90   3.64   6.26  Idle               0.00   20.00 -> 20.00     0.00    6.26        0.00
14:00    9.03   3.64   5.39  Idle               0.00   20.00 -> 20.00     0.00    5.39        0.00
15:00    7.64   3.64   4.00  Idle               0.00   20.00 -> 20.00     0.00    4.00        0.00
16:00    5.79   5.06   0.73  Idle               0.00   20.00 -> 20.00     0.00    0.73        0.00
17:00    3.62   9.32  -5.70  DischargeBattery   5.70   20.00 -> 14.30     0.00    0.00        0.00
18:00    1.23  13.58 -12.35  DischargeBattery   8.00   14.30 ->  6.30     4.35    0.00        0.00
19:00    0.00  15.00 -15.00  DischargeBattery   4.30    6.30 ->  2.00    10.70    0.00        0.00
20:00    0.00  12.16 -12.16  Idle               0.00    2.00 ->  2.00    12.16    0.00        0.00
21:00    0.00   7.90  -7.90  Idle               0.00    2.00 ->  2.00     7.90    0.00        0.00
22:00    0.00   5.06  -5.06  Idle               0.00    2.00 ->  2.00     5.06    0.00        0.00
23:00    0.00   2.22  -2.22  Idle               0.00    2.00 ->  2.00     2.22    0.00        0.00

Totals (kWh)            C++ controller  Python reference
  grid import                    48.63             44.63
  grid export                    19.89             17.89
  unresolved                      0.00              0.00
  final state of charge            2.00              0.00
```

Read row 18:00: the deficit is 12.35 kWh, but the controller discharges only
8 kW. That is its configured maximum. The remaining 4.35 kWh is imported. The
controller then stops at the 2 kWh minimum state of charge, while the Python
reference empties the battery to 0 kWh. The reference therefore ends with less
grid import, but it also ignores the operating limits that protect the battery.

## Tests

- `tests/test_controller_in_the_loop.py` runs every scenario with a stand-in
  that mirrors `EnergyController::decide`. It checks:
  - what the controller sees before dispatch;
  - energy conservation;
  - the controller window and power limits;
  - that a decision can never store more than the surplus;
  - grid-outage behaviour;
  - that an unknown action stops the run;
  - the CLI end to end against a local HTTP server.
- `tests/test_control_api.py` covers:
  - the JSON contract;
  - problem-details errors;
  - unusable responses;
  - readiness polling;
  - real HTTP with `http.server`.
- `tests/test_sil_report.py` checks that the report is self-contained and
  escaped, has tooltips, a table row per decision, and JSON output.

The package still has no runtime dependencies: the HTTP client uses
`urllib`.
