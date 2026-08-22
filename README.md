# GridFlex EMS

GridFlex EMS is an independent portfolio and learning project that demonstrates
the incremental development of a modular Energy Management System across
multiple programming languages and technical layers.

The project combines:

- C# and ASP.NET Core for APIs and application coordination
- C++ for deterministic and performance-oriented control logic
- C for hardware-facing abstractions
- Python for simulation and reproducible energy scenarios
- CMake for native build orchestration
- Docker for reproducible Linux runtime packaging
- GitHub Container Registry for versioned container distribution
- GitHub Actions for automated quality and deployment validation
- Linux and Windows for cross-platform development and testing

The current implementation includes a complete HTTP-to-native control path:

```text
HTTP client
    │
    ▼
ASP.NET Core API
    │
    ▼
Application service
    │
    ▼
IControllerGateway
    │
    ▼
NativeControllerGateway
    │
    ▼
LibraryImport
    │
    ▼
Versioned C ABI
    │
    ▼
C++ EnergyController
```

The backend is also packaged as a Linux container image and published
automatically from `main` to GitHub Container Registry.

The project is educational and does not control real electrical equipment.

---

## Quick start with Docker

The fastest way to run the GridFlex backend is through the public container
image published to GitHub Container Registry.

No repository checkout or local .NET, C or C++ toolchain is required.

You only need Docker with Linux container support.

### Pull the image

```bash
docker pull ghcr.io/kris7011/gridflex-ems-backend:latest
```

The package is public, so authentication to GitHub Container Registry is not
required.

### Run the backend

```bash
docker run --rm \
  --name gridflex-api \
  --publish 5080:8080 \
  ghcr.io/kris7011/gridflex-ems-backend:latest
```

The API is then available at:

```text
http://localhost:5080
```

### Verify liveness

```bash
curl http://localhost:5080/health/live
```

Expected response:

```text
Healthy
```

### Verify readiness

```bash
curl http://localhost:5080/health/ready
```

Expected response:

```text
Healthy
```

Readiness includes validation of the native C++ controller dependency.

A successful readiness check therefore verifies that the application can load
and initialize the managed-to-native controller integration.

The published runtime image contains:

- The ASP.NET Core backend
- The native C++ controller shared library
- The managed-to-native interoperability layer
- Required .NET runtime dependencies

The application runs inside the container as a non-root user.

### Container image tags

Images published from `main` receive two tags:

```text
latest
sha-<full-git-commit-sha>
```

`latest` points to the most recently published `main` image and is convenient
for trying the project.

The commit-SHA tag provides a source-traceable link between a container image and
the exact Git revision that produced it.

Container tags remain mutable registry references.

The immutable content identity is the image digest, for example:

```text
sha256:<digest>
```

Example source-traceable image tag:

```bash
docker pull \
  ghcr.io/kris7011/gridflex-ems-backend:sha-<full-git-commit-sha>
```

See the [HTTP API](#http-api) section for the available endpoints and a complete
control-decision example.

---

## Project purpose

GridFlex EMS demonstrates how a larger technical software system can be divided
into components with explicit responsibilities, testable boundaries and
documented architectural decisions.

The project is also used as a structured learning environment for technologies
commonly found in:

- Backend development
- Industrial software
- Embedded systems
- Energy systems
- Native interoperability
- Cloud and DevOps environments

The system is developed incrementally so that each architectural decision and
implementation step can be explained and justified.

---

## Project goals

GridFlex EMS is designed to demonstrate practical experience with:

- C# and ASP.NET Core
- REST APIs
- Application architecture
- Dependency injection
- Native interoperability
- C++20
- C17
- Python
- CMake
- Linux
- Windows
- GitHub Actions
- Docker
- GitHub Container Registry
- Microsoft Azure
- Automated testing
- Static analysis
- Defensive programming
- Performance measurement
- Observability
- Cross-language communication
- Technical documentation
- Architecture Decision Records

---

## System overview

GridFlex EMS models a simplified energy installation containing:

- Solar generation
- Battery Energy Storage System, also known as BESS
- Building consumption
- Electrical grid connection
- Electric vehicle chargers in a later milestone

The system works with energy measurements and determines how the installation
should react.

Example decisions include:

- Charge the battery when generation exceeds consumption
- Discharge the battery when consumption exceeds generation
- Respect configured battery operating limits
- Respect maximum charging and discharging power
- Import energy from the grid when required by later control strategies
- Export surplus energy when required by later control strategies
- Reject invalid or inconsistent measurements
- Report system readiness and dependency failures

---

## Current architecture

```text
┌─────────────────────────────────────────────┐
│             Frontend Dashboard              │
│               Future milestone              │
└──────────────────────┬──────────────────────┘
                       │
                       │ HTTP / JSON
                       ▼
┌─────────────────────────────────────────────┐
│             ASP.NET Core API                │
│                                             │
│  - System status                            │
│  - Control decision endpoint                │
│  - Application coordination                │
│  - Liveness / readiness                     │
│  - Configuration                            │
└──────────────────────┬──────────────────────┘
                       │
                       │ Application boundary
                       ▼
┌─────────────────────────────────────────────┐
│          IControlDecisionService            │
│          IControllerGateway                 │
└──────────────────────┬──────────────────────┘
                       │
                       │ Managed/native boundary
                       ▼
┌─────────────────────────────────────────────┐
│         NativeControllerGateway             │
│                                             │
│  LibraryImport                              │
│  SafeHandle                                 │
│  ABI validation                             │
│  Explicit mapping                           │
└──────────────────────┬──────────────────────┘
                       │
                       │ Versioned C ABI
                       ▼
┌─────────────────────────────────────────────┐
│             C++ Controller                  │
│                                             │
│  - EnergyMeasurement                       │
│  - ControllerLimits                        │
│  - EnergyController                        │
│  - ControlCommand                          │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│        C Hardware Abstraction Layer         │
│                                             │
│  - Sensors                                  │
│  - Actuators                                │
│  - Simulated devices                        │
│  - Error normalization                     │
└─────────────────────────────────────────────┘
```

The Python simulation engine remains independently testable and currently acts
as the simulation and reference-behavior component.

Python-to-backend integration is a later architectural step.

The backend deployment path currently adds another boundary around the running
application:

```text
Git repository
      │
      ▼
Multi-stage Docker build
      │
      ├── C/C++ native build
      │
      ├── CMake runtime installation
      │
      └── ASP.NET Core Linux publish
      │
      ▼
Linux runtime package
      │
      ▼
ASP.NET Core runtime image
      │
      ▼
GitHub Container Registry
```

---

# Component responsibilities

## ASP.NET Core API

The ASP.NET Core backend is responsible for:

- Exposing HTTP APIs
- Providing explicit request and response contracts
- Coordinating application-level use cases
- Exposing system status
- Exposing health checks
- Providing liveness and readiness information
- Managing controller configuration
- Validating startup configuration
- Integrating with the native controller
- Translating application failures into appropriate HTTP responses
- Keeping native implementation details outside the application layer

The current backend implementation includes:

- ASP.NET Core on .NET 10
- Minimal API endpoints
- `IControlDecisionService`
- `ControlDecisionService`
- `IControllerGateway`
- `NativeControllerGateway`
- Strongly typed controller configuration
- Startup configuration validation
- Source-generated `LibraryImport`
- `SafeHandle`-based native lifetime management
- Native ABI version validation
- Explicit managed/native structure mapping
- Liveness health checks
- Native-controller readiness checks
- HTTP-to-C++ controller integration
- Explicit API contracts
- `ProblemDetails` responses for invalid measurements
- xUnit tests
- ASP.NET Core integration tests
- GitHub Actions backend quality validation
- Linux runtime packaging
- Multi-stage Docker packaging
- Non-root container runtime
- Automated container smoke testing
- GitHub Container Registry publication

The managed/native integration decision is documented in:

[ADR 0002: Use a C ABI for .NET to C++ controller interoperability](docs/decisions/0002-use-c-abi-for-dotnet-cpp-interop.md)

---

## Python simulation engine

The Python simulation engine is responsible for:

- Simulating solar generation
- Simulating building consumption
- Simulating battery behavior
- Simulating grid import and export
- Calculating energy balance
- Coordinating battery-first energy management
- Running multi-step simulation timelines
- Creating reproducible scenarios
- Producing immutable measurement snapshots
- Supporting experiments and energy analysis

The detailed Python architecture is documented in:

[Python Simulation Architecture](docs/simulation-architecture.md)

---

## C++ controller

The C++ controller is responsible for:

- Receiving validated energy measurements
- Evaluating operating conditions
- Producing deterministic control decisions
- Applying operating limits
- Producing explicit control commands
- Keeping decision logic separate from hardware I/O
- Providing a native API consumable by the .NET backend
- Demonstrating performance-oriented development

The implementation includes:

- C++20
- CMake
- Reusable controller library
- Controller CLI
- `EnergyMeasurement`
- `ControlCommand`
- `ControlAction`
- `ControllerLimits`
- `EnergyController`
- `HardwareCommandExecutor`
- Defensive validation
- State-of-charge protection
- Charge and discharge power limits
- Native shared-library adapter
- Versioned C ABI
- Catch2 tests
- CTest integration
- Performance microbenchmarks
- Linux GitHub Actions validation
- Windows MSVC builds

---

## C hardware abstraction layer

The C hardware layer represents low-level hardware-facing concepts.

Responsibilities include:

- Generic sensor interfaces
- Generic actuator interfaces
- Driver-style callback functions
- Opaque device contexts
- Explicit status codes
- Simulated devices
- Failure injection
- Hardware error normalization
- C/C++ interoperability

The implementation includes:

- C17
- CMake
- Reusable static library
- Hardware CLI
- Sensor callbacks
- Actuator callbacks
- Simulated sensors
- Simulated actuators
- Failure injection
- Operation counters
- Last-successful-command state
- `GridFlexHardwareError`
- CTest integration
- Linux and Windows validation

---

# HTTP API

## System status

```text
GET /api/system/status
```

Returns basic information about the running API.

Example response:

```json
{
  "service": "GridFlex.Api",
  "status": "healthy",
  "environment": "Development"
}
```

---

## Liveness

```text
GET /health/live
```

Liveness answers:

```text
Is the ASP.NET Core process alive?
```

The endpoint deliberately does not execute native dependency health checks.

A native controller failure should therefore not automatically make the process
appear dead.

---

## Readiness

```text
GET /health/ready
```

Readiness answers:

```text
Is this application instance ready to receive traffic?
```

The native-controller readiness check resolves `IControllerGateway`.

That causes the managed/native integration to verify:

```text
IControllerGateway
        │
        ▼
NativeControllerGateway
        │
        ▼
Native library loading
        │
        ▼
ABI version validation
        │
        ▼
Native controller creation
```

Expected behavior:

```text
Normal operation

/health/live   → 200 Healthy
/health/ready  → 200 Healthy
```

If the native controller cannot be initialized:

```text
Native dependency unavailable

/health/live   → 200 Healthy
/health/ready  → 503 Unhealthy
```

---

## Control decision

```text
POST /api/control/decision
```

Example request:

```json
{
  "stepNumber": 42,
  "elapsedTimeHours": 1.0,
  "intervalHours": 0.25,
  "generatedEnergyKwh": 5.0,
  "consumedEnergyKwh": 2.0,
  "netEnergyKwh": 3.0,
  "batteryStateOfChargeKwh": 10.0,
  "gridImportEnergyKwh": 0.0,
  "gridExportEnergyKwh": 0.0,
  "unresolvedEnergyKwh": 0.0
}
```

Example response:

```json
{
  "sourceStepNumber": 42,
  "action": "ChargeBattery",
  "requestedPowerKw": 10.0
}
```

For this example:

```text
Net surplus:       3.0 kWh
Interval:          0.25 h

Requested power:
3.0 / 0.25 = 12.0 kW

Configured maximum charge power:
10.0 kW

Result:
ChargeBattery
10.0 kW
```

Invalid energy measurements return:

```text
400 Bad Request
```

using `ProblemDetails`.

---

# End-to-end controller flow

A successful HTTP request executes the following path:

```text
HTTP POST
    │
    ▼
JSON deserialization
    │
    ▼
ControlDecisionRequest
    │
    ▼
EnergyMeasurementInput
    │
    ▼
IControlDecisionService
    │
    ▼
ControlDecisionService
    │
    ▼
IControllerGateway
    │
    ▼
NativeControllerGateway
    │
    ▼
LibraryImport
    │
    ▼
C ABI
    │
    ▼
C++ adapter
    │
    ▼
EnergyController
    │
    ▼
ControlDecision
    │
    ▼
ControlDecisionResponse
    │
    ▼
HTTP JSON
```

Native ABI types are never exposed through the HTTP contract.

---

# Managed-to-native interoperability

The .NET backend communicates with the C++ controller through an in-process
native shared library.

The boundary is a small versioned C ABI.

```text
ASP.NET Core
    │
    ▼
ControlDecisionService
    │
    ▼
IControllerGateway
    │
    ▼
NativeControllerGateway
    │
    ▼
LibraryImport
    │
    ▼
C ABI
    │
    ▼
C++ adapter
    │
    ▼
EnergyController
```

The application layer does not know about:

- Native library names
- P/Invoke declarations
- Native handles
- C-compatible structures
- ABI implementation details
- C++ classes

Those concerns remain inside Infrastructure.

---

## Why a C ABI?

Direct C++ ABI interoperability was intentionally avoided because C++ ABI
details may vary between:

- Compilers
- Platforms
- Toolchains

The C ABI provides a small and explicit interoperability contract.

The boundary avoids exposing:

- C++ classes
- C++ references
- C++ exceptions
- Standard-library containers

Instead it uses:

- Primitive values
- Explicit structures
- Numeric status codes
- Opaque handles

This decision is documented in:

[ADR 0002](docs/decisions/0002-use-c-abi-for-dotnet-cpp-interop.md)

---

## Native lifetime management

The native controller is represented in .NET using `SafeHandle`.

Conceptually:

```text
Dependency injection container
        │
        ▼
NativeControllerGateway
        │
        ▼
NativeControllerSafeHandle
        │
        ▼
SafeHandle.Dispose()
        │
        ▼
ReleaseHandle()
        │
        ▼
gridflex_controller_destroy()
        │
        ▼
delete native controller
```

This avoids requiring application code to manually free native resources.

---

# C++ controller model

## Energy measurements

The C++ controller has its own validated `EnergyMeasurement` domain type.

A measurement contains:

- Step number
- Elapsed time
- Interval duration
- Generated energy
- Consumed energy
- Net energy
- Battery state of charge
- Grid import energy
- Grid export energy
- Unresolved energy

Examples of rejected input include:

- Step number equal to zero
- Non-positive intervals
- Negative values where only non-negative values are valid
- NaN
- Infinite values
- Simultaneous grid import and export

The measurement model creates a defensive input boundary:

```text
External data
    │
    ▼
Validated EnergyMeasurement
    │
    ▼
EnergyController
```

---

## Control commands

The controller produces an explicit `ControlCommand`.

Current actions are:

```text
Idle
ChargeBattery
DischargeBattery
ImportFromGrid
ExportToGrid
```

A command contains:

- Source measurement step number
- Strongly typed control action
- Requested power in kW

Example:

```text
Source step:     42
Action:          ChargeBattery
Requested power: 20 kW
```

Direction and magnitude are represented separately instead of using signed
power values.

---

## Measurement-to-command traceability

Every generated command keeps the source measurement step number.

```text
EnergyMeasurement
Step: 42
    │
    ▼
EnergyController
    │
    ▼
ControlCommand
Source step: 42
```

This supports:

- Debugging
- Logging
- Observability
- Integration testing
- Future auditing
- Cross-component correlation

The .NET application service also verifies that the returned source step matches
the input measurement.

---

# Controller decision logic

The current C++ controller uses deterministic battery-oriented rules.

```text
EnergyMeasurement
        │
        ▼
EnergyController
        │
        ├── Balanced → Idle
        │
        ├── Surplus  → ChargeBattery
        │
        └── Deficit  → DischargeBattery
        │
        ▼
ControlCommand
```

A floating-point tolerance prevents tiny numeric residuals around zero from
creating unnecessary commands.

For active decisions:

```text
requested power kW = |net energy kWh| / interval hours
```

Example:

```text
Net energy: 10 kWh
Interval:   0.5 h

Requested power:
10 / 0.5 = 20 kW
```

---

## Controller operating limits

`ControllerLimits` currently contains:

- Maximum charge power
- Maximum discharge power
- Minimum battery state of charge
- Maximum battery state of charge

The limits are configured outside the C++ decision algorithm.

```text
ControllerLimits ─────┐
                      │
                      ▼
                EnergyController
                      ▲
                      │
EnergyMeasurement ────┘
                      │
                      ▼
                ControlCommand
```

For charging, final power is limited by:

```text
requested charge power
configured maximum charge power
remaining battery capacity
```

For discharging, final power is limited by:

```text
requested discharge power
configured maximum discharge power
available energy above the minimum reserve
```

If the battery cannot safely charge or discharge, the controller can return
`Idle`.

---

# Controller-to-hardware integration

`EnergyController` does not perform hardware I/O.

Hardware execution is handled by `HardwareCommandExecutor`.

```text
EnergyMeasurement
        │
        ▼
EnergyController
        │
        ▼
ControlCommand
        │
        ▼
HardwareCommandExecutor
        │
        ├── Battery actuator
        └── Grid actuator
        │
        ▼
C Hardware Abstraction Layer
```

This separates:

```text
What should the system do?
```

from:

```text
How should that action be represented at the hardware boundary?
```

---

## Complete-state actuator mapping

The current mapping is:

| Control action   | Battery actuator | Grid actuator |
| ---------------- | ---------------- | ------------- |
| Idle             | Idle             | Idle          |
| ChargeBattery    | Charge           | Idle          |
| DischargeBattery | Discharge        | Idle          |
| ImportFromGrid   | Idle             | Import        |
| ExportToGrid     | Idle             | Export        |

The non-target actuator is explicitly idled.

This avoids accidentally leaving an earlier device state active when the next
controller command targets another device.

---

## Hardware execution results

`HardwareExecutionResult` keeps separate results for:

- Battery execution
- Grid execution

This makes partial failures visible.

For example:

```text
Battery command: Failed
Grid command:    Succeeded
```

can be distinguished from:

```text
Battery command: Succeeded
Grid command:    Failed
```

---

# C hardware interfaces

## Sensor interface

A generic sensor contains:

- Sensor type
- Read callback
- Opaque callback context

Conceptually:

```text
GridFlexSensor
      │
      ├── type
      ├── read callback
      └── context
```

Example statuses include:

```text
OK
INVALID_ARGUMENT
NOT_CONFIGURED
READ_FAILED
```

---

## Actuator interface

A generic actuator contains:

- Actuator type
- Apply callback
- Opaque callback context
- Explicit actuator command

Conceptually:

```text
GridFlexActuator
      │
      ├── type
      ├── apply callback
      └── context
```

Current actuator types include:

```text
Battery
Grid connection
EV charger
```

Current actuator actions include:

```text
Idle
Charge
Discharge
Import
Export
```

The generic actuator layer validates the request before calling the concrete
device callback.

---

## Simulated hardware

Simulated sensors support:

- Configurable values
- Failure injection
- Read-attempt tracking

Simulated actuators support:

- Failure injection
- Apply-attempt tracking
- Last successful action
- Last successful requested power

Failed operations count as attempts but do not overwrite the last successful
device state.

---

## Hardware error model

The hardware layer normalizes lower-level statuses through:

```text
GridFlexHardwareError
```

The error model identifies:

- Error source
- Hardware operation
- Normalized error code
- Sensor type when relevant
- Actuator type when relevant

Normalized errors include:

```text
NONE
INVALID_ARGUMENT
NOT_CONFIGURED
UNSUPPORTED_OPERATION
OPERATION_FAILED
UNKNOWN_STATUS
```

The C++ hardware executor reuses this common C hardware error model.

---

# Python simulation

The Python simulation provides reproducible energy-system scenarios.

The current high-level flow is:

```text
SimulationScenario
        │
        ▼
SimulationScenarioRunner
        │
        ▼
SimulationTimelineRunner
        │
        ▼
EnergyManagementService
        │
        ├── EnergyBalanceCalculator
        ├── BatteryDispatchService
        └── GridConnection
        │
        ▼
EnergyMeasurementFactory
        │
        ▼
EnergyMeasurement
        │
        ▼
SimulationScenarioResult
```

The architecture separates:

- Configuration from mutable runtime state
- Energy calculations from coordination
- Simulation internals from external measurements
- Timeline execution from individual decisions

---

## Battery model

The battery model supports:

- Total capacity
- Current state of charge
- Available capacity
- Charging
- Discharging
- State-of-charge calculation
- Invalid-state validation

The battery is intentionally mutable because its state changes during a running
simulation.

---

## Solar generation model

Solar generation currently uses:

- Installed capacity
- Irradiance factor
- Performance ratio
- Simulation interval

The model is intentionally deterministic and simplified.

---

## Building consumption model

Building consumption currently uses:

- Base load
- Peak load
- Activity factor
- Simulation interval

---

## Grid connection model

The grid model supports:

- Energy import
- Energy export
- Maximum import power
- Maximum export power
- Grid availability
- Interval-based transfer limits

Power limits use kilowatts.

Transferable energy depends on time:

```text
energy = power × time
```

Example:

```text
50 kW × 0.5 h = 25 kWh
```

---

## Python energy-management strategy

The current simulation strategy is battery-first.

For surplus:

```text
Solar surplus
      │
      ▼
Charge battery
      │
      ▼
Remaining surplus
      │
      ▼
Export to grid
```

For deficit:

```text
Energy deficit
      │
      ▼
Discharge battery
      │
      ▼
Remaining deficit
      │
      ▼
Import from grid
```

The Python implementation acts as simulation and reference behavior.

The C++ controller remains independently implemented and tested.

---

# Default simulation scenario

The current demonstration contains three one-hour steps.

## Step 1

```text
Solar generation:      76.5 kWh
Building consumption:  66.0 kWh
Net energy:            +10.5 kWh

Battery:
40.0 → 50.5 kWh

Grid import:             0.0 kWh
Grid export:             0.0 kWh
```

## Step 2

```text
Solar generation:      25.5 kWh
Building consumption:  78.0 kWh
Net energy:            -52.5 kWh

Battery:
50.5 → 0.0 kWh

Grid import:             2.0 kWh
Grid export:             0.0 kWh
```

## Step 3

```text
Solar generation:     102.0 kWh
Building consumption:  42.0 kWh
Net energy:            +60.0 kWh

Battery:
0.0 → 60.0 kWh

Grid import:             0.0 kWh
Grid export:             0.0 kWh
```

Final summary:

```text
Final battery state of charge: 60.0 kWh
Total grid import:               2.0 kWh
Total grid export:               0.0 kWh
Total unresolved energy:         0.0 kWh
```

---

# Performance measurement

The C++ controller includes a dedicated microbenchmark executable.

It currently measures:

- Surplus decisions
- Deficit decisions
- Balanced decisions
- Total execution time
- Average nanoseconds per decision
- Decisions per second

The benchmark uses:

- `std::chrono::steady_clock`
- Release builds
- 100,000 warmup iterations per case
- 10,000,000 measured iterations per case
- Checksum consumption of results

The benchmark deliberately remains separate from unit tests.

Unit tests answer:

```text
Is the controller behavior correct?
```

The benchmark answers:

```text
How does the controller decision path perform?
```

Representative Windows/MSVC Release measurements from the current development
baseline have been approximately:

```text
Surplus:   23–25 ns/decision
Deficit:   23–24 ns/decision
Balanced:  around 11 ns/decision
```

These are local development-machine microbenchmark results.

They are not:

- Hard real-time guarantees
- Production SLOs
- Portable timing guarantees

---

# Testing strategy

The project uses several levels of automated testing.

## Python

Python testing includes:

- Unit tests
- Scenario tests
- Validation tests
- pytest
- Coverage
- Ruff
- mypy

Current Python baseline:

```text
127 tests passed
100% coverage of tested domain modules
Ruff passed
mypy passed
```

Coverage is used as one quality signal and is not treated as proof that all
possible behavior is correct.

---

## C++

C++ testing includes:

- `EnergyMeasurement` validation
- `ControlCommand` validation
- `ControllerLimits`
- Controller decisions
- State-of-charge boundaries
- Power limits
- Hardware command translation
- Partial hardware failures
- C/C++ integration
- Performance smoke testing

Current C++ Catch2 baseline:

```text
47 Catch2 test cases
148 assertions
0 failures
```

---

## C

Native C tests cover:

- Sensor contracts
- Actuator contracts
- Callback configuration
- Argument validation
- Failure propagation
- Simulated device behavior
- Failure injection
- Error normalization

The C hardware project currently registers five native C test targets through
CTest.

---

## Mixed C/C++

The integrated native controller build validates both the C and C++ layers.

Current baseline:

```text
47 Catch2 test cases
5 native C test targets
52 total CTest tests
148 Catch2 assertions
0 failures
```

---

## .NET backend

The backend test suite currently contains:

```text
29 tests
0 failures
```

Coverage includes:

- Application startup
- System status
- Liveness
- Readiness
- Controller application service behavior
- Native interoperability contracts
- Native ABI layout
- Safe native handles
- Native runtime integration
- `NativeControllerGateway`
- Dependency injection composition
- HTTP control decisions
- Invalid HTTP measurements
- End-to-end HTTP-to-C++ execution

A successful endpoint integration test executes:

```text
HTTP request
    │
    ▼
ASP.NET Core
    │
    ▼
ControlDecisionService
    │
    ▼
NativeControllerGateway
    │
    ▼
C ABI
    │
    ▼
C++ EnergyController
```

---

# Continuous integration

The repository contains separate GitHub Actions workflows for:

- Python quality
- C quality
- C++ quality
- Backend quality
- Backend container validation and publication

## Python Quality

The workflow:

- Installs Python 3.12
- Installs development dependencies
- Runs Ruff
- Runs mypy
- Runs pytest with coverage

---

## C Quality

The workflow:

- Runs on Linux
- Configures the hardware CMake project
- Builds the C library
- Builds the CLI
- Builds native tests
- Runs CTest
- Executes a CLI smoke test

---

## C++ Quality

The workflow:

- Runs on Linux
- Configures the mixed C/C++ controller project
- Enables tests
- Enables benchmark builds
- Builds the controller
- Builds the C hardware dependency
- Runs CTest
- Runs the controller CLI
- Runs the benchmark as a smoke test

---

## Backend Quality

The backend workflow validates the ASP.NET Core and managed/native integration.

It includes:

- .NET restore
- Formatting validation
- Build
- Tests
- Native controller build
- Native runtime installation
- Linux backend runtime packaging
- Packaged application smoke testing
- Liveness validation
- Readiness validation

The native shared library is built and made available to the backend test
environment so end-to-end interoperability can be validated in CI.

The same native runtime is also included in the generated Linux backend runtime
package.

---

## Backend Container

The container workflow validates the complete Docker deployment unit.

For pull requests and pushes to `main`, it:

1. Builds `backend/Dockerfile`
2. Starts the resulting Linux container
3. Waits for `/health/live`
4. Verifies `/health/ready`
5. Verifies that `libgridflex_controller_native.so` exists
6. Verifies that the application is not running as root
7. Cleans up the test container

On pull requests, image publication is deliberately skipped.

After a successful push to `main`, the workflow additionally:

1. Authenticates to GitHub Container Registry with `GITHUB_TOKEN`
2. Builds the publishable image
3. Tags it as `latest`
4. Tags it with the full Git commit SHA
5. Pushes both tags to GHCR

Published image:

```text
ghcr.io/kris7011/gridflex-ems-backend
```

This creates a deployment artifact that can be pulled and run independently of
the repository checkout.

---

# Current quality baseline

```text
Python
127 tests
Ruff passed
mypy passed

C++
47 Catch2 cases
148 assertions

C
5 native CTest targets

Integrated C/C++
52 CTest tests

.NET backend
29 tests

GitHub Actions
Python Quality     passed
C Quality          passed
C++ Quality        passed
Backend Quality    passed
Backend Container  passed

Container deployment
Linux runtime package      passed
Docker build               passed
Container smoke test       passed
Liveness                   passed
Readiness                  passed
Non-root runtime           passed
Native library validation  passed
GHCR publication           passed
Anonymous GHCR pull        passed
```

---

# Repository structure

```text
gridflex-ems/
├── .github/
│   └── workflows/
│       ├── backend-container.yml
│       ├── backend-quality.yml
│       ├── c-quality.yml
│       ├── cpp-quality.yml
│       └── python-quality.yml
│
├── backend/
│   ├── GridFlex.Api/
│   │   ├── Application/
│   │   ├── Contracts/
│   │   ├── Endpoints/
│   │   ├── Infrastructure/
│   │   ├── Services/
│   │   ├── Program.cs
│   │   └── appsettings.json
│   │
│   ├── GridFlex.Api.Tests/
│   ├── scripts/
│   │   └── package-linux-runtime.sh
│   ├── Dockerfile
│   └── GridFlex.slnx
│
├── controller/
│   ├── benchmarks/
│   ├── include/
│   ├── src/
│   ├── tests/
│   └── CMakeLists.txt
│
├── hardware/
│   ├── include/
│   ├── src/
│   ├── tests/
│   └── CMakeLists.txt
│
├── simulation/
│   ├── src/
│   ├── tests/
│   └── pyproject.toml
│
├── docs/
│   ├── decisions/
│   │   ├── 0001-use-multiple-languages.md
│   │   └── 0002-use-c-abi-for-dotnet-cpp-interop.md
│   ├── architecture.md
│   └── simulation-architecture.md
│
├── .clang-format
├── .dockerignore
├── .editorconfig
├── .gitattributes
├── .gitignore
├── global.json
├── LICENSE
└── README.md
```

Build and package output directories are intentionally excluded from version
control.

---

# Engineering principles

## Clear responsibilities

Each component should have a small and understandable responsibility.

---

## Separation of concerns

Simulation, application coordination, controller logic, native
interoperability, hardware access and presentation remain separate.

Deployment packaging is also kept outside the application and controller domain
logic.

---

## Explicit boundaries

Important boundaries use explicit interfaces and contracts.

Examples include:

```text
HTTP
ControlDecisionRequest / ControlDecisionResponse
```

```text
Application
IControlDecisionService
IControllerGateway
```

```text
Managed/native
Versioned C ABI
```

```text
Controller
EnergyMeasurement
ControlCommand
```

```text
Hardware
GridFlexSensor
GridFlexActuator
```

```text
Deployment
CMake install contract
Linux runtime package
Docker image
```

---

## Dependency direction

The application layer depends on abstractions rather than native infrastructure.

For example:

```text
ControlDecisionService
        │
        ▼
IControllerGateway
```

rather than:

```text
ControlDecisionService
        │
        ▼
P/Invoke / C ABI
```

Native details remain in the Infrastructure layer.

---

## Defensive programming

Invalid data should be rejected at boundaries.

Examples include:

- Invalid simulation input
- Invalid C++ measurements
- Invalid control commands
- Invalid controller limits
- Invalid native ABI calls
- Unsupported control actions
- Invalid HTTP measurements

---

## Explicit mapping

Important boundaries use explicit mapping instead of relying on accidental
representation compatibility.

Examples:

```text
HTTP request
    ↓
EnergyMeasurementInput
```

```text
Native action
    ↓
ControlAction
```

```text
ControlAction
    ↓
HTTP action string
```

This keeps contracts independently evolvable.

---

## Testability

Core behavior should remain independently testable.

The project contains:

- Unit tests
- Integration tests
- Native interoperability tests
- HTTP integration tests
- Scenario tests
- CI validation
- Container smoke tests
- Performance benchmarks

---

## Observability

System state and dependency health should be visible.

The backend currently exposes:

```text
/api/system/status
/health/live
/health/ready
```

Liveness and readiness are also used during automated deployment validation.

Logging and metrics will be expanded in later milestones.

---

## Reliability

Failures should be surfaced explicitly instead of being silently ignored.

Examples include:

- Native status codes
- Managed exceptions at infrastructure boundaries
- Readiness failures
- HTTP `ProblemDetails`
- Separate hardware execution results
- Failing CI quality gates
- Failing container smoke tests

---

## Performance awareness

Performance-sensitive controller behavior is benchmarked instead of assumed to
be fast.

---

## Portability

The project currently supports:

```text
Local development
Windows + MSVC + .NET

Continuous integration
Linux + native C/C++ + .NET

Deployment
Linux container + ASP.NET Core runtime + native C++ shared library
```

---

## Documented decisions

Important architectural decisions are recorded using ADRs.

---

# Development workflow

The project uses feature branches and pull requests.

```text
main
  │
  ▼
feature branch
  │
  ▼
small implementation
  │
  ▼
format
  │
  ▼
build
  │
  ▼
tests
  │
  ▼
inspect diff
  │
  ▼
commit
  │
  ▼
push
  │
  ▼
draft pull request
  │
  ▼
GitHub Actions
  │
  ▼
review
  │
  ▼
squash merge
  │
  ▼
main
```

Container publication is deliberately separated from pull-request validation.

```text
Pull request
    │
    ▼
Build + smoke test
    │
    ▼
No publication

main
    │
    ▼
Build + smoke test
    │
    ▼
GHCR publication
```

This keeps the Git history incremental and makes architectural evolution easier
to understand.

---

# Milestones

## Milestone 1: Project foundation - Complete

- [x] Repository structure
- [x] Documentation
- [x] Python package setup
- [x] Battery simulation
- [x] Unit tests
- [x] Linting
- [x] Static type checking
- [x] Continuous integration

---

## Milestone 2: Energy simulation - Complete

- [x] Solar generation model
- [x] Building consumption model
- [x] Grid connection model
- [x] Simulation timeline
- [x] Energy measurements
- [x] Scenario configuration

---

## Milestone 3: Control logic - Complete

- [x] C++ project setup
- [x] Measurement input
- [x] Control commands
- [x] Deterministic control rules
- [x] Controller operating limits
- [x] State-of-charge protection
- [x] Unit-test infrastructure
- [x] Performance benchmarks
- [x] Linux CI

---

## Milestone 4: Hardware abstraction - Complete

- [x] C project setup
- [x] Sensor interfaces
- [x] Actuator interfaces
- [x] Simulated sensors
- [x] Simulated actuators
- [x] Failure injection
- [x] Hardware error normalization
- [x] C++ integration
- [x] Mixed C/C++ build
- [x] Integration testing
- [x] Linux C CI

---

## Milestone 5: Backend API and native integration - Complete

- [x] ASP.NET Core solution
- [x] .NET 10 backend
- [x] System-status endpoint
- [x] Application control boundary
- [x] `IControlDecisionService`
- [x] `IControllerGateway`
- [x] Architecture Decision Record for .NET/C++ integration
- [x] Versioned C ABI
- [x] Native C++ adapter
- [x] Native shared library
- [x] Source-generated `LibraryImport`
- [x] Explicit ABI structures
- [x] Native ABI contract tests
- [x] Runtime native integration tests
- [x] `SafeHandle` resource ownership
- [x] `NativeControllerGateway`
- [x] Strongly typed configuration
- [x] Startup configuration validation
- [x] Dependency injection
- [x] Liveness health check
- [x] Native-controller readiness health check
- [x] HTTP control decision endpoint
- [x] Explicit request and response contracts
- [x] End-to-end HTTP-to-C++ integration tests
- [x] Backend GitHub Actions quality validation

Current backend path:

```text
HTTP
  ↓
ASP.NET Core
  ↓
Application
  ↓
Native gateway
  ↓
C ABI
  ↓
C++
```

---

## Milestone 6: Containers and Linux deployment - Core path complete

The core Linux deployment path is implemented.

Completed:

- [x] Native-library deployment packaging
- [x] CMake runtime installation contract
- [x] Backend Linux runtime packaging
- [x] Framework-dependent Linux publish
- [x] Backend Dockerfile
- [x] Multi-stage native + .NET build
- [x] ASP.NET Core runtime-only final image
- [x] Native shared-library deployment
- [x] Linux-sensitive LF repository rules
- [x] Docker build-context exclusions
- [x] Container liveness validation
- [x] Container readiness validation
- [x] Native-library container validation
- [x] Non-root container runtime
- [x] Reproducible local container startup
- [x] Automated container smoke testing
- [x] GitHub Container Registry publication
- [x] `latest` container tag
- [x] Commit-SHA container tag
- [x] Public anonymous container pull

Possible later deployment improvements include:

- [ ] Docker Compose if multiple runtime services are introduced
- [ ] Environment-specific container configuration
- [ ] Deployment helper scripts
- [ ] Additional container security scanning
- [ ] Build-once / promote-the-tested-artifact workflow

---

## Milestone 7: DevOps and Azure

Current DevOps foundation:

- [x] GitHub Actions foundation
- [x] Python quality workflow
- [x] C quality workflow
- [x] C++ quality workflow
- [x] Backend quality workflow
- [x] Backend container workflow
- [x] Container image creation
- [x] Automated container build
- [x] Container smoke testing
- [x] GitHub Container Registry publication
- [x] Source-traceable commit-SHA image tagging
- [ ] Azure deployment
- [ ] Environment-specific deployment configuration
- [ ] Monitoring
- [ ] Metrics
- [ ] Centralized logs
- [ ] Dependency scanning
- [ ] Container scanning

---

## Milestone 8: Frontend dashboard

Planned features include:

- [ ] System overview
- [ ] Battery status
- [ ] Solar production
- [ ] Building consumption
- [ ] Grid import and export
- [ ] Controller decisions
- [ ] System health
- [ ] Alerts
- [ ] Controller history

---

# Running the project

## Recommended: Docker

For the quickest end-to-end backend startup, use the public image:

```bash
docker pull ghcr.io/kris7011/gridflex-ems-backend:latest
```

```bash
docker run --rm \
  --name gridflex-api \
  --publish 5080:8080 \
  ghcr.io/kris7011/gridflex-ems-backend:latest
```

Then verify:

```bash
curl http://localhost:5080/health/live
curl http://localhost:5080/health/ready
```

Both endpoints should return:

```text
Healthy
```

---

## Python simulation

The Python package is located in:

```text
simulation/
```

Create the development environment:

```powershell
cd simulation

python -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

python -m pip install -e ".[dev]"
```

Run the simulation:

```powershell
gridflex-simulation
```

Run tests:

```powershell
python -m pytest
```

Run coverage:

```powershell
python -m pytest --cov=gridflex_simulation --cov-report=term-missing
```

Run Ruff:

```powershell
python -m ruff check .
```

Run mypy:

```powershell
python -m mypy
```

---

# Building the C hardware layer

On Windows, initialize a Visual Studio Developer PowerShell environment first.

Configure:

```powershell
cmake `
  -S hardware `
  -B hardware/build `
  -DBUILD_TESTING=ON
```

Build Release:

```powershell
cmake `
  --build hardware/build `
  --config Release
```

Run tests:

```powershell
ctest `
  --test-dir hardware/build `
  -C Release `
  --output-on-failure
```

Run the hardware CLI:

```powershell
& ".\hardware\build\Release\gridflex_hardware_cli.exe"
```

---

# Building the C++ controller

On Windows, initialize a Visual Studio Developer PowerShell environment first.

Configure:

```powershell
cmake `
  -S controller `
  -B controller/build `
  -DBUILD_TESTING=ON
```

Build Release:

```powershell
cmake `
  --build controller/build `
  --config Release
```

Run the integrated C/C++ tests:

```powershell
ctest `
  --test-dir controller/build `
  -C Release `
  --output-on-failure
```

Expected native baseline:

```text
52 tests passed
0 tests failed
```

Run the controller CLI:

```powershell
& ".\controller\build\Release\gridflex_controller_cli.exe"
```

---

# Running the C++ benchmark

Configure benchmark builds:

```powershell
cmake `
  -S controller `
  -B controller/build `
  -DBUILD_TESTING=ON `
  -DGRIDFLEX_BUILD_BENCHMARKS=ON
```

Build:

```powershell
cmake `
  --build controller/build `
  --config Release `
  --target gridflex_controller_benchmark
```

Run:

```powershell
& ".\controller\build\Release\gridflex_controller_benchmark.exe"
```

---

# Building the backend

The backend solution is:

```text
backend/GridFlex.slnx
```

Build:

```powershell
dotnet build `
  "backend/GridFlex.slnx" `
  --configuration Release
```

The backend uses the native controller shared library.

For local Windows testing, make the native Release build available through
`PATH`:

```powershell
$env:PATH =
  "$(Resolve-Path 'controller/build/Release');$env:PATH"
```

Verify the DLL:

```powershell
Get-ChildItem `
  "controller/build/Release/gridflex_controller_native.dll"
```

Run backend tests:

```powershell
dotnet test `
  "backend/GridFlex.slnx" `
  --configuration Release `
  --no-build
```

Current expected result:

```text
29 tests passed
0 tests failed
```

---

# Building the Linux backend runtime package

The repository contains:

```text
backend/scripts/package-linux-runtime.sh
```

The packaging script creates a framework-dependent Linux runtime package:

```text
backend/dist/linux-x64/
├── app/
│   ├── GridFlex.Api.dll
│   ├── GridFlex.Api.deps.json
│   ├── GridFlex.Api.runtimeconfig.json
│   ├── appsettings.json
│   └── application dependencies
└── lib/
    └── libgridflex_controller_native.so
```

The package deliberately separates:

```text
managed application runtime
```

from:

```text
native runtime dependency
```

The Docker build reuses this deployment package instead of copying intermediate
CMake or .NET build directories directly into the final image.

---

# Building the Docker image locally

Build from the repository root:

```powershell
docker build `
  --file backend/Dockerfile `
  --tag gridflex-api:local `
  .
```

Run:

```powershell
docker run `
  --detach `
  --name gridflex-api-local `
  --publish 5080:8080 `
  gridflex-api:local
```

Verify:

```powershell
Invoke-WebRequest `
  -UseBasicParsing `
  "http://localhost:5080/health/live"
```

```powershell
Invoke-WebRequest `
  -UseBasicParsing `
  "http://localhost:5080/health/ready"
```

Inspect the runtime user:

```powershell
docker exec gridflex-api-local id
```

The application should run as the non-root `app` user.

Verify the native runtime:

```powershell
docker exec `
  gridflex-api-local `
  test -f /app/lib/libgridflex_controller_native.so
```

Clean up:

```powershell
docker rm --force gridflex-api-local
```

---

# Running the ASP.NET Core API

The API project is:

```text
backend/GridFlex.Api
```

Start it with:

```powershell
dotnet run `
  --project "backend/GridFlex.Api/GridFlex.Api.csproj"
```

The repository also contains:

```text
backend/GridFlex.Api/GridFlex.Api.http
```

with ready-to-run requests for:

```text
GET  /api/system/status
GET  /health/live
GET  /health/ready
POST /api/control/decision
```

---

# Container deployment

The production-style container path currently looks like this:

```text
Source code
    │
    ▼
GitHub Actions
    │
    ▼
Docker multi-stage build
    │
    ├── .NET SDK
    ├── C compiler
    ├── C++ compiler
    └── CMake
    │
    ▼
Native controller build
    │
    ▼
CMake runtime installation
    │
    ▼
Linux backend runtime package
    │
    ▼
ASP.NET Core runtime-only image
    │
    ▼
Container smoke test
    │
    ├── /health/live
    ├── /health/ready
    ├── native .so
    └── non-root user
    │
    ▼
GitHub Container Registry
```

The final runtime image does not contain the .NET SDK, C/C++ compilers or native
build tooling.

This is a deliberate multi-stage-build boundary.

---

## Public container image

The current backend image is:

```text
ghcr.io/kris7011/gridflex-ems-backend
```

Pull the newest `main` build:

```bash
docker pull ghcr.io/kris7011/gridflex-ems-backend:latest
```

The image is publicly readable.

---

## Versioned image references

Each publication creates a tag containing the full Git commit SHA:

```text
sha-<full-git-commit-sha>
```

The commit-SHA tag is intended for source traceability.

Container tags remain mutable registry references.

The immutable content identity is the image digest:

```text
sha256:<digest>
```

This distinction is important:

```text
latest
    → convenient moving tag

sha-<git-commit>
    → source-traceable tag

sha256:<digest>
    → immutable content identity
```

A commit-SHA tag allows a source revision and deployment artifact to be
correlated more clearly than `latest`.

Conceptually:

```text
Git commit
    │
    ▼
container build
    │
    ▼
sha-<git-commit>
```

This is preferable to relying only on `latest` when source traceability matters.

---

# Documentation

Detailed documentation lives under:

```text
docs/
```

Main architecture document:

[GridFlex EMS Architecture](docs/architecture.md)

Python architecture:

[Python Simulation Architecture](docs/simulation-architecture.md)

Architecture decisions:

```text
docs/decisions/
```

Current ADRs include:

- [ADR 0001: Use multiple languages](docs/decisions/0001-use-multiple-languages.md)
- [ADR 0002: Use a C ABI for .NET to C++ controller interoperability](docs/decisions/0002-use-c-abi-for-dotnet-cpp-interop.md)

---

# Technology choices

| Area                    | Technology                      | Responsibility                         | Status      |
| ----------------------- | ------------------------------- | -------------------------------------- | ----------- |
| Backend                 | C# / ASP.NET Core / .NET 10     | APIs and application coordination      | Implemented |
| Application boundary    | C# interfaces                   | Use-case and infrastructure separation | Implemented |
| Native interoperability | `LibraryImport` + C ABI         | .NET-to-C++ integration                | Implemented |
| Controller              | C++20                           | Deterministic control logic            | Implemented |
| Hardware abstraction    | C17                             | Low-level interfaces and simulation    | Implemented |
| Simulation              | Python 3.12                     | Energy models and scenarios            | Implemented |
| Native build            | CMake                           | C and C++ builds                       | Implemented |
| Testing                 | xUnit / Catch2 / CTest / pytest | Automated verification                 | Implemented |
| CI                      | GitHub Actions                  | Automated quality validation           | Implemented |
| Containers              | Docker                          | Reproducible Linux runtime             | Implemented |
| Container registry      | GitHub Container Registry       | Versioned image distribution           | Implemented |
| Cloud                   | Microsoft Azure                 | Deployment and observability           | Planned     |
| Development             | Windows + Linux                 | Cross-platform engineering             | Active      |

Every technology has a defined responsibility.

Technologies are not added simply to increase the number of technologies in the
repository.

---

# Security considerations

The current project runs as an educational development system and does not yet
contain authentication.

Current deployment-oriented security measures include:

- A runtime-only final Docker image
- Separation of build tooling from runtime tooling
- A non-root application user
- Explicit GitHub Actions permissions
- `GITHUB_TOKEN` instead of manually stored registry credentials
- Package publication only from `main`
- Source-traceable commit-SHA image tags

Future work may include:

- Authentication
- Authorization
- Role-based access control
- Secret management
- Secure service communication
- Dependency scanning
- Container scanning
- Audit logging
- Image signing and provenance

Input validation is already applied at multiple application and native
boundaries.

---

# Safety considerations

GridFlex EMS is an educational software simulation.

It must not be used to control:

- Real batteries
- Electrical installations
- Industrial equipment
- Energy infrastructure

The project does not implement:

- Certified electrical safety functions
- Electrical protection systems
- Production battery management protocols
- Real PLC communication
- Production grid synchronization
- Hard real-time guarantees
- Regulatory compliance

The C hardware interfaces and simulated devices exist for learning, software
design and automated testing.

They are not certified device drivers or safety systems.

---

# Out of scope

The current project does not include:

- Control of real electrical equipment
- Certified safety functionality
- Real PLC communication
- Production BMS integration
- Electrical protection
- Grid synchronization
- Regulatory compliance
- Hard real-time operating-system guarantees
- Production industrial deployment

---

# Current development direction

Milestones 1 through 5 are complete.

The core deployment path of Milestone 6 is also implemented:

```text
ASP.NET Core
    │
    ▼
Managed/native gateway
    │
    ▼
Versioned C ABI
    │
    ▼
C++ EnergyController
    │
    ▼
Linux runtime package
    │
    ▼
Docker image
    │
    ▼
Container validation
    │
    ▼
GitHub Container Registry
```

The current system therefore spans:

```text
Simulation
    ↓
Application API
    ↓
Native interoperability
    ↓
Control logic
    ↓
Hardware abstraction
    ↓
Linux deployment packaging
    ↓
Container distribution
```

The next major development areas are expected to include:

- Deployment hardening
- Azure deployment
- Monitoring and metrics
- Centralized logging
- Dependency and container scanning
- Frontend visualization
- Further integration between simulation and backend components

The project will continue to evolve incrementally so that each new capability
has an explicit responsibility, testable boundary and documented reason for
existing.

---

# Disclaimer

GridFlex EMS is an independent educational portfolio project.

It is not based on proprietary software, confidential documentation, internal
architecture or protected information belonging to PowerCon or any other
energy company.

The project represents a simplified and fictional Energy Management System
created solely for learning and portfolio purposes.
