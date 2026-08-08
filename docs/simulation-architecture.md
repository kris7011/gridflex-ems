# Python Simulation Architecture

## Purpose

The Python simulation engine models the energy behavior of a simplified
Energy Management System.

The simulation is responsible for:

- Solar energy generation
- Building energy consumption
- Battery state and energy transfer
- Grid import and export
- Energy balance calculation
- Energy management coordination
- Multi-step simulation timelines
- Energy measurement generation
- Reproducible scenario execution

The simulation does not control real electrical equipment.

Its purpose is to provide deterministic and testable energy behavior that can
later supply measurements to the C++ controller.

## Current architecture

The simulation is divided into small components with explicit responsibilities.

```text
SimulationScenario
        │
        │ configuration
        ▼
SimulationScenarioRunner
        │
        │ creates fresh runtime components
        ▼
┌──────────────────────────────────────┐
│ Battery                              │
│ SolarArray                           │
│ BuildingLoad                         │
│ GridConnection                       │
└──────────────────┬───────────────────┘
                   │
                   ▼
        SimulationTimelineRunner
                   │
                   │ one interval at a time
                   ▼
          EnergyManagementService
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
EnergyBalance   Battery     Grid
 Calculator     Dispatch   Connection
               Service
        │          │          │
        └──────────┴──────────┘
                   │
                   ▼
         EnergyManagementResult
                   │
                   ▼
        EnergyMeasurementFactory
                   │
                   ▼
           EnergyMeasurement
                   │
                   ▼
        SimulationStepResult
                   │
                   ▼
       SimulationScenarioResult
```

## Domain models

### Battery

`Battery` represents mutable battery state.

It contains:

- Total capacity in kilowatt-hours
- Current state of charge
- Available storage capacity
- State-of-charge percentage

The battery supports:

- Charging
- Discharging
- Capacity limiting
- State validation

Unlike most result and configuration objects, the battery is intentionally
mutable because its state of charge changes during a simulation.

### SolarArray

`SolarArray` models simplified solar production.

Solar generation depends on:

- Installed capacity
- Irradiance factor
- Performance ratio
- Simulation interval

The model converts power into generated energy for the requested interval.

### BuildingLoad

`BuildingLoad` models simplified building energy consumption.

Consumption depends on:

- Base load
- Peak load
- Activity factor
- Simulation interval

The activity factor represents how heavily the building is being used during
the current interval.

### GridConnection

`GridConnection` models the electrical grid boundary.

It supports:

- Grid import
- Grid export
- Maximum import power
- Maximum export power
- Grid availability
- Interval-based transfer limits

Grid power limits are configured in kilowatts.

The amount of energy that can be transferred during an interval is calculated
as:

```text
energy = power × time
```

For example:

```text
50 kW × 0.5 h = 25 kWh
```

## Energy balance

`EnergyBalanceCalculator` calculates the relationship between generated and
consumed energy.

The result can be:

- Surplus
- Deficit
- Balanced

The calculator is stateless and has no side effects.

It answers the question:

> What is the current energy situation?

It does not decide how the system should respond.

## Battery dispatch

`BatteryDispatchService` applies an energy surplus or deficit to the battery.

For surplus energy:

```text
surplus
   ↓
battery charge
```

For deficit energy:

```text
deficit
   ↓
battery discharge
```

The dispatch result separates:

- Requested energy
- Transferred energy
- Remaining energy
- Initial battery state of charge
- Final battery state of charge

This makes physical constraints explicit and makes state transitions easy to
inspect and test.

## Energy management

`EnergyManagementService` coordinates one energy-management interval.

The current strategy is:

```text
generation and consumption
          │
          ▼
     energy balance
          │
          ▼
        battery
          │
          ▼
 remaining surplus or deficit
          │
          ▼
          grid
```

A surplus is first offered to the battery.

If the battery cannot accept the complete surplus, the remaining energy is
exported to the grid.

A deficit is first supplied by the battery.

If the battery cannot supply the complete deficit, the remaining energy is
imported from the grid.

This coordination is intentionally separated from the individual battery and
grid models.

## Simulation timeline

`SimulationTimelineRunner` executes multiple simulation intervals in
chronological order.

Each `SimulationStep` defines:

- Irradiance factor
- Building activity factor
- Interval duration

The same runtime battery is reused between timeline steps.

This means battery state evolves over time.

Example:

```text
Step 1
Battery: 40.0 → 50.5 kWh
              │
              ▼
Step 2
Battery: 50.5 → 0.0 kWh
              │
              ▼
Step 3
Battery: 0.0 → 60.0 kWh
```

The timeline runner controls when individual simulation intervals are executed.

It does not contain the energy-management strategy itself.

That responsibility remains inside `EnergyManagementService`.

## Energy measurements

`EnergyMeasurement` represents an immutable snapshot of observable energy data
after a completed simulation interval.

Measurements currently contain:

- Step number
- Elapsed simulation time
- Interval duration
- Generated energy
- Consumed energy
- Net energy
- Battery state of charge
- Grid import
- Grid export
- Unresolved energy

`EnergyMeasurementFactory` maps internal simulation results into measurement
objects.

This creates a boundary between internal simulation implementation and data
that can later be consumed by other components.

```text
Internal simulation objects
          │
          ▼
EnergyMeasurementFactory
          │
          ▼
EnergyMeasurement
          │
          ├── C++ controller
          ├── ASP.NET Core API
          ├── logging
          ├── metrics
          └── analysis
```

The exact cross-language serialization and transport format has not yet been
selected.

## Scenario configuration

`SimulationScenario` defines the initial conditions for a reproducible
simulation.

A scenario contains:

- Scenario name
- Battery configuration
- Solar configuration
- Building configuration
- Grid configuration
- Timeline steps

Configuration objects are immutable.

Runtime components are created from those configuration objects when the
scenario starts.

Example:

```text
BatteryScenarioConfiguration
        │
        │ create
        ▼
     Battery
        │
        │ mutable during run
        ▼
40.0 → 50.5 → 0.0 → 60.0 kWh
```

## Reproducibility

`SimulationScenarioRunner` creates new runtime component instances every time a
scenario is executed.

This prevents mutable state from one simulation run from affecting another.

Therefore:

```text
Scenario A
   │
   ├── Run 1 → fresh Battery
   │
   └── Run 2 → fresh Battery
```

The same scenario configuration should produce the same deterministic result
when the underlying models and strategy are unchanged.

## Configuration versus runtime state

A deliberate distinction exists between configuration and runtime state.

### Immutable configuration

Examples:

- `BatteryScenarioConfiguration`
- `SolarScenarioConfiguration`
- `BuildingScenarioConfiguration`
- `GridScenarioConfiguration`
- `SimulationScenario`

These objects describe what should be created.

They do not represent changing equipment state.

### Mutable runtime state

The primary mutable runtime object is:

- `Battery`

Its state changes as energy is charged and discharged.

### Immutable results

Examples include:

- `EnergyBalanceResult`
- `BatteryDispatchResult`
- `GridTransferResult`
- `EnergyManagementResult`
- `EnergyMeasurement`
- `SimulationStepResult`
- `SimulationScenarioResult`

Results represent completed calculations or state transitions and should not be
modified afterwards.

## Current simulation flow

The default demonstration scenario currently behaves as follows.

### Step 1

```text
Solar generation:      76.5 kWh
Building consumption:  66.0 kWh
Net energy:            +10.5 kWh

Battery:
40.0 → 50.5 kWh

Grid import:             0.0 kWh
Grid export:             0.0 kWh
```

### Step 2

```text
Solar generation:      25.5 kWh
Building consumption:  78.0 kWh
Net energy:            -52.5 kWh

Battery:
50.5 → 0.0 kWh

Grid import:             2.0 kWh
Grid export:             0.0 kWh
```

### Step 3

```text
Solar generation:     102.0 kWh
Building consumption:  42.0 kWh
Net energy:            +60.0 kWh

Battery:
0.0 → 60.0 kWh

Grid import:             0.0 kWh
Grid export:             0.0 kWh
```

Final scenario result:

```text
Battery state of charge: 60.0 kWh
Total grid import:        2.0 kWh
Total grid export:        0.0 kWh
Unresolved energy:        0.0 kWh
```

## Testing

The simulation is covered by automated tests using pytest.

The current quality pipeline includes:

- pytest
- pytest-cov
- Ruff
- mypy
- GitHub Actions

At the completion of Milestone 2:

```text
127 tests passed
100% coverage of the tested Python domain modules
Ruff passed
mypy passed
```

Coverage is used as one signal of test completeness.

A coverage value of 100% does not by itself prove that all possible behavior is
correct.

Tests are still expected to verify meaningful domain behavior, boundaries and
edge cases.

## Milestone 2 status

Milestone 2: Energy simulation is complete.

Implemented capabilities:

- Solar generation model
- Building consumption model
- Grid connection model
- Simulation timeline
- Energy measurements
- Scenario configuration

The next milestone introduces the C++ energy controller.

## Next architecture step

Milestone 3 will introduce a C++ controller responsible for evaluating
measurement input and producing control decisions.

The planned direction is:

```text
Python Simulation
        │
        │ Energy measurements
        ▼
C++ Energy Controller
        │
        │ Control commands
        ▼
Future hardware abstraction
```

The first C++ work should establish:

- C++ project structure
- Build tooling
- Unit-test framework
- Measurement input model
- Initial control command model
- Deterministic control rules

The communication mechanism between Python and C++ will be selected separately
and documented through an Architecture Decision Record.
