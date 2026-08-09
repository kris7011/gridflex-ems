# GridFlex EMS

GridFlex EMS is an independent portfolio and learning project that demonstrates
the architecture and incremental development of a modular Energy Management
System.

The system simulates and coordinates energy flows between:

* A Battery Energy Storage System, also known as BESS
* Solar power generation
* The electrical grid
* Building energy consumption
* Electric vehicle chargers in a later milestone

The project focuses on software architecture, reliability, performance,
automated testing, observability, defensive programming and communication
between components written in different programming languages.

## Project purpose

The purpose of GridFlex EMS is to demonstrate how a larger technical software
solution can be divided into components with clear responsibilities and explicit
interfaces.

The project is also used as a structured learning environment for technologies
commonly used in industrial, embedded and energy-related software development.

The system will gradually include components written in:

* C#
* Python
* C++
* C

The project is developed incrementally so that each architectural decision,
implementation step and technology choice can be explained and justified.

## Project goals

GridFlex EMS is designed to demonstrate practical experience with:

* C# and ASP.NET Core
* Python
* C++
* C
* Linux
* Docker
* GitHub Actions
* Microsoft Azure
* REST APIs
* Software architecture
* Automated testing
* Static code analysis
* Observability
* Performance measurement
* Cross-language communication
* Defensive programming
* Technical documentation

## System overview

GridFlex EMS models a simplified energy installation.

The installation contains:

* A solar power source
* A battery storage system
* A connection to the electrical grid
* A building with varying energy consumption
* One or more electric vehicle chargers in a later milestone

The system receives or produces measurements from these energy assets and
determines how energy should be distributed.

Examples of system decisions include:

* Charging the battery when solar production exceeds local consumption
* Discharging the battery when local consumption exceeds solar production
* Importing energy from the electrical grid when local energy is insufficient
* Exporting surplus energy when the battery is fully charged
* Reducing energy usage when system limits are reached
* Stopping battery activity if unsafe operating conditions are detected

## Planned architecture

```text
┌─────────────────────────────────────────────┐
│              Frontend Dashboard             │
└──────────────────────┬──────────────────────┘
                       │
                       │ HTTP
                       ▼
┌─────────────────────────────────────────────┐
│             ASP.NET Core API                │
│                                             │
│  - System status                            │
│  - Commands                                 │
│  - Application coordination                │
│  - Logging and observability                │
└──────────────────────┬──────────────────────┘
                       │
                       │ Application messages
                       ▼
┌─────────────────────────────────────────────┐
│         Energy Management Components        │
│                                             │
│  Python Simulation Engine                   │
│  C++ Real-Time Controller                   │
│  C Hardware Abstraction Layer               │
└─────────────────────────────────────────────┘
```

## Component responsibilities

### ASP.NET Core API

The ASP.NET Core API will be responsible for:

* Exposing system status through REST endpoints
* Receiving commands from users or external systems
* Coordinating application-level use cases
* Exposing health checks
* Providing structured logging
* Exposing metrics later in the project
* Supporting authentication and authorization in a later milestone

### Python simulation engine

The Python simulation engine is responsible for:

* Simulating solar power generation
* Simulating building energy consumption
* Simulating battery behavior
* Simulating grid import and export
* Calculating energy balance
* Coordinating simplified battery-first energy management
* Running multi-step simulation timelines
* Creating reproducible operating scenarios
* Producing immutable measurement data
* Supporting experiments and energy analysis
* Testing energy behavior before controller integration

The detailed Python simulation architecture is documented in:

[Python Simulation Architecture](docs/simulation-architecture.md)

### C++ controller

The C++ controller is being developed to:

* Receive validated energy measurements
* Evaluate operating conditions
* Make deterministic control decisions
* Produce explicit control commands
* Apply safety and operating limits
* Prioritize energy sources in later controller strategies
* Demonstrate performance-oriented software development
* Provide independently testable control behavior

The current C++ implementation includes:

* A CMake-based C++20 project
* A reusable static controller library
* A small controller CLI executable
* An explicit `EnergyMeasurement` input model
* Defensive validation of measurement invariants
* Immutable-by-interface measurement state
* An explicit `ControlCommand` output model
* Strongly typed `ControlAction` values
* Defensive validation of command invariants
* Source-step metadata for measurement-to-command traceability
* Deterministic surplus, deficit and balanced-energy control rules
* Conversion from interval energy in kWh to requested power in kW
* A floating-point balance tolerance around zero
* Validated `ControllerLimits` configuration
* Configurable maximum charge and discharge power
* Configurable minimum and maximum battery state-of-charge boundaries
* Charge limiting based on remaining battery capacity
* Discharge limiting based on minimum battery reserve
* A dedicated controller microbenchmark executable
* Optional benchmark builds through CMake
* Release-oriented benchmark measurements
* Surplus, deficit and balanced-decision benchmark cases
* Benchmark result consumption through a checksum
* Linux benchmark smoke-test execution through GitHub Actions
* 35 Catch2 unit tests
* CTest integration
* Windows Debug and Release builds using MSVC
* Linux builds through GitHub Actions
* Automated C++ build, test and smoke-test validation

### C hardware abstraction layer

The C hardware abstraction layer will be responsible for:

* Representing low-level sensors
* Representing actuators
* Providing driver-like interfaces
* Hiding hardware-specific details from the controller
* Simulating communication with physical equipment
* Introducing embedded software concepts

## Repository structure

```text
gridflex-ems/
├── .github/
│   └── workflows/
│       ├── cpp-quality.yml
│       └── python-quality.yml
│
├── backend/
│   └── ASP.NET Core API and application services
│
├── controller/
│   ├── benchmarks/
│   │   └── energy_controller_benchmark.cpp
│   ├── include/
│   │   └── gridflex/
│   │       └── controller/
│   ├── src/
│   ├── tests/
│   └── CMakeLists.txt
│
├── docker/
│   └── Dockerfiles and container configuration
│
├── docs/
│   ├── decisions/
│   │   └── Architecture Decision Records
│   ├── architecture.md
│   └── simulation-architecture.md
│
├── hardware/
│   └── Hardware abstraction components written in C
│
├── scripts/
│   └── Development, build and automation scripts
│
├── simulation/
│   ├── src/
│   ├── tests/
│   └── pyproject.toml
│
├── .editorconfig
├── .gitignore
├── LICENSE
└── README.md
```

## Initial data flow

The planned cross-language data flow is:

```text
Python Simulation Engine
          │
          │ EnergyMeasurement
          ▼
C++ Energy Controller
          │
          │ ControlCommand
          ▼
C Hardware Abstraction Layer
          │
          │ Equipment state
          ▼
ASP.NET Core API
          │
          │ System status
          ▼
Frontend Dashboard
```

The exact communication mechanism between the components will be selected and
documented in a later Architecture Decision Record.

Possible communication mechanisms include:

* HTTP
* gRPC
* Message queues
* Shared libraries
* Standard input and output streams
* Local sockets

The transport mechanism is intentionally kept separate from the domain
contracts.

The Python simulation and C++ controller can therefore evolve around explicit
measurement and command models before a specific communication technology is
selected.

## Current status

Milestone 1, Milestone 2 and Milestone 3 are complete.

Milestone 4 is the next planned development milestone.

The Python simulation supports:

* Battery charging and discharging
* Solar energy generation
* Building energy consumption
* Energy balance calculation
* Battery-first energy dispatch
* Grid import and export
* Configurable grid transfer limits
* Grid availability scenarios
* Multi-step simulation timelines
* Stateful battery behavior across simulation steps
* Immutable energy measurement snapshots
* Reproducible scenario configuration and execution
* Defensive input validation
* Automated unit tests
* Static type checking
* Linting
* Test coverage
* GitHub Actions quality checks

The C++ controller currently supports:

* C++20 project configuration through CMake
* A reusable controller library
* A CLI executable
* Explicit energy measurement input
* Defensive measurement validation
* Signed grid import/export measurement calculation
* Explicit control-command output modelling
* Strongly typed controller actions
* Defensive control-command validation
* Source-step metadata on generated control commands
* Deterministic surplus, deficit and balanced-energy decisions
* Requested-power calculation from interval energy
* Floating-point tolerance for near-zero energy balances
* Validated controller operating-limit configuration
* Maximum battery charge-power limiting
* Maximum battery discharge-power limiting
* Minimum battery state-of-charge protection
* Maximum battery state-of-charge protection
* SOC-aware charge and discharge limiting
* A dedicated performance benchmark executable
* Release-oriented controller microbenchmarks
* Surplus, deficit and balanced-decision benchmark cases
* Benchmark timing through `std::chrono::steady_clock`
* Benchmark warmup and repeated measured iterations
* Automated unit testing with Catch2
* 35 discovered C++ tests through CTest
* Debug and Release builds with MSVC on Windows
* Automated Linux builds, tests and benchmark smoke testing through GitHub Actions

The detailed Python architecture is documented in:

[Python Simulation Architecture](docs/simulation-architecture.md)

## Current Python simulation flow

The Python simulation currently follows this high-level flow:

```text
SimulationScenario
        │
        │ configuration
        ▼
SimulationScenarioRunner
        │
        │ creates fresh runtime components
        ▼
SimulationTimelineRunner
        │
        │ executes chronological intervals
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

The design separates:

* Configuration from mutable runtime state
* Energy calculations from coordination
* Internal simulation results from external measurement data
* Timeline execution from individual energy-management decisions

## Battery model

The current battery model supports:

* Total capacity measured in kilowatt-hours
* Current state of charge
* Available storage capacity
* Charging
* Discharging
* State-of-charge calculation
* Validation of invalid battery states

The battery is intentionally mutable because its state of charge changes during
a running simulation.

Later versions may include:

* Charging efficiency
* Discharging efficiency
* Maximum charging power
* Maximum discharging power
* Battery temperature
* Battery degradation
* Minimum and maximum state-of-charge limits
* Emergency shutdown behavior

## Solar generation model

The solar model calculates energy generation based on:

* Installed capacity
* Irradiance factor
* Performance ratio
* Simulation interval

The model is intentionally simplified and deterministic.

It provides predictable energy values that can be used when testing later
control strategies.

## Building consumption model

The building model calculates consumption based on:

* Base load
* Peak load
* Activity factor
* Simulation interval

This allows scenarios to represent changing building demand over time.

## Energy balance

The energy balance component compares generated and consumed energy.

The result is classified as:

* Surplus
* Deficit
* Balanced

The calculator is stateless.

It determines the energy situation but does not decide how the system should
respond.

## Battery dispatch

The battery dispatch service applies surplus or deficit energy to the battery.

It records:

* Requested energy
* Actually transferred energy
* Remaining energy
* Initial battery state of charge
* Final battery state of charge

This makes battery constraints and state changes explicit.

## Grid connection model

The grid model supports:

* Importing energy
* Exporting energy
* Maximum import power
* Maximum export power
* Grid availability
* Transfer limits based on simulation interval

Power limits are configured in kilowatts.

The amount of transferable energy depends on both power and time:

```text
energy = power × time
```

For example:

```text
50 kW × 0.5 hours = 25 kWh
```

## Energy management

The current simplified Python energy-management strategy is battery-first.

For surplus energy:

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

For an energy deficit:

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

This coordination is implemented separately from the individual battery and
grid models.

The Python strategy currently acts as the simulation and reference behavior.

The C++ controller is developed separately so that control decisions can be
implemented, tested and measured independently.

## Simulation timeline

The simulation timeline executes multiple energy intervals in chronological
order.

A simulation step currently contains:

* Irradiance factor
* Building activity factor
* Interval duration

The same battery runtime instance is reused throughout one timeline.

This allows state of charge to evolve between steps.

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

## Energy measurements

The simulation produces immutable measurement snapshots after each interval.

A measurement currently contains:

* Step number
* Elapsed simulation time
* Interval duration
* Generated energy
* Consumed energy
* Net energy
* Battery state of charge
* Grid import energy
* Grid export energy
* Unresolved energy

The measurement model creates an explicit boundary between internal simulation
behavior and data intended for other components.

The planned direction is:

```text
Python internal simulation
          │
          ▼
EnergyMeasurement
          │
          ├── C++ controller
          ├── ASP.NET Core API
          ├── Logging
          ├── Metrics
          └── Analysis
```

The exact serialization format and transport mechanism have not yet been
selected.

## C++ measurement input

The C++ controller contains its own `EnergyMeasurement` domain type.

The C++ type represents the controller-side measurement contract rather than
depending directly on Python runtime objects.

The current measurement contains:

* Step number
* Elapsed time
* Interval duration
* Generated energy
* Consumed energy
* Net energy
* Battery state of charge
* Grid import energy
* Grid export energy
* Unresolved energy

The measurement validates its invariants during construction.

Examples of rejected input include:

* Step number equal to zero
* Non-positive time intervals
* Negative energy values where only non-negative values are valid
* NaN or infinite numeric values
* Simultaneous positive grid import and grid export

The model also exposes signed grid energy:

```text
grid net energy = grid import - grid export
```

Examples:

```text
Import 10 kWh, export 0 kWh  → +10 kWh
Import 0 kWh, export 8 kWh   →  -8 kWh
```

The C++ measurement state is private and exposed through const accessors.

This means that once a valid measurement has been constructed, callers cannot
directly mutate its fields into an invalid state.

The measurement model therefore establishes the validated input boundary for
the controller:

```text
External measurement data
          │
          ▼
Validated EnergyMeasurement
          │
          ▼
C++ controller
```

## C++ control commands

The C++ controller contains an explicit `ControlCommand` output model.

A control command represents an action that the controller can request after
evaluating an energy measurement.

The currently defined actions are:

* Idle
* Charge battery
* Discharge battery
* Import from grid
* Export to grid

These actions are represented by the strongly typed C++ `ControlAction`
enumeration.

A control command contains:

* The source measurement step number
* A strongly typed control action
* Requested power measured in kilowatts

The command direction and requested power magnitude are represented separately.

For example:

```text
Action:          ChargeBattery
Requested power: 25 kW
```

rather than representing the same decision using signed power such as:

```text
+25 kW
```

or:

```text
-25 kW
```

Keeping action and magnitude separate makes controller intent explicit and
avoids requiring downstream components to interpret the sign of a numeric
value.

### Strongly typed control actions

Control actions are represented through a C++ `enum class` instead of strings.

Conceptually:

```text
ControlAction
├── Idle
├── ChargeBattery
├── DischargeBattery
├── ImportFromGrid
└── ExportToGrid
```

This provides:

* A restricted set of valid actions
* Compile-time type checking
* No string-based magic values
* Clearer controller interfaces
* Better editor and compiler assistance
* Safer refactoring

### Control-command validation

The `ControlCommand` model validates its invariants during construction.

Examples of rejected commands include:

* Source step number equal to zero
* Negative requested power
* NaN requested power
* Infinite requested power
* Idle commands requesting non-zero power
* Active commands requesting zero power

An idle command is explicitly represented as:

```text
Action:          Idle
Requested power: 0 kW
```

An active command must request power greater than zero.

For example:

```text
Action:          DischargeBattery
Requested power: 20 kW
```

is valid.

The following is not:

```text
Action:          DischargeBattery
Requested power: 0 kW
```

### Measurement-to-command traceability

Each command stores the source step number of the measurement used to create the
command.

For example:

```text
EnergyMeasurement
Step number: 42
      │
      ▼
EnergyController
      │
      ▼
ControlCommand
Source step:     42
Action:          ChargeBattery
Requested power: 25 kW
```

The source-step metadata provides explicit traceability between controller input
and output.

It can support:

* Debugging
* Structured logging
* Observability
* Audit trails
* Integration testing
* Cross-component correlation

The deterministic controller rules preserve the measurement step number when
creating the resulting command.

### Controller domain boundary

The controller has both an explicit validated input model and an explicit
validated output model:

```text
EnergyMeasurement
        │
        │ validated input
        ▼
┌──────────────────┐
│ EnergyController │
└──────────────────┘
        │
        │ deterministic decision
        ▼
ControlCommand
        │
        │ validated output
        ▼
Downstream component
```

This keeps input modelling, output modelling, decision logic and operating
constraints as separate responsibilities.

The controller can therefore operate on already valid measurements and produce
commands that already satisfy command invariants.

## Scenario configuration

Simulation scenarios define reproducible initial conditions.

A scenario contains:

* Scenario name
* Battery configuration
* Solar configuration
* Building configuration
* Grid configuration
* Timeline steps

Scenario configuration objects are immutable.

Fresh runtime components are created whenever a scenario is executed.

This prevents mutable state from one simulation run from leaking into another.

```text
SimulationScenario
        │
        ├── Run 1 → fresh runtime components
        │
        └── Run 2 → fresh runtime components
```

This allows identical scenarios to produce deterministic results when the
underlying models and control strategy remain unchanged.

## Default demonstration scenario

The current demonstration contains three one-hour steps.

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

Scenario summary:

```text
Final battery state of charge: 60.0 kWh
Total grid import:               2.0 kWh
Total grid export:               0.0 kWh
Total unresolved energy:         0.0 kWh
```

## Engineering principles

GridFlex EMS follows these engineering principles.

### Clear responsibilities

Each component and class should have a clear and limited responsibility.

### Incremental development

The system is developed through small, understandable and testable changes.

### Testability

Business rules and control decisions should be testable without requiring the
entire system to run.

### Defensive validation

Invalid measurements, invalid commands and impossible states should be rejected
explicitly.

### Explicit interfaces

Communication between components should happen through documented interfaces.

Input and output contracts should remain explicit rather than relying on
implicit assumptions between components.

### Observability

Important system decisions, errors and state changes should be visible through
logs and metrics.

### Reliability

Components should handle invalid input, unavailable dependencies and unexpected
conditions in a controlled manner.

### Performance awareness

Performance-sensitive functionality should be measured rather than assumed.

### Documented decisions

Important architectural decisions should be documented through Architecture
Decision Records.

### Separation of concerns

Simulation, control logic, hardware access, API communication and presentation
should not be mixed together.

### Portability

Core components should avoid unnecessary platform-specific assumptions.

The C++ controller is currently validated using MSVC on Windows and through
Linux-based GitHub Actions.

## Quality attributes

The project places particular focus on the following quality attributes.

### Robustness

The system should continue operating safely when it receives invalid or
unexpected input.

### Maintainability

The source code should be readable, modular and easy to change.

### Testability

Core behavior should be covered by automated tests.

### Performance

Time-sensitive control logic should have predictable and measurable execution
time.

### Scalability

Individual components should be replaceable or extendable without requiring a
complete redesign.

### Portability

The project should be runnable on Windows during development and Linux through
containers or native tooling.

### Observability

The system should provide enough information to understand its current state
and diagnose failures.

## Development approach

The project is developed using an incremental, sprint-inspired workflow.

Each development step should include:

* A clearly defined goal
* A small implementation scope
* Automated tests
* Documentation
* A meaningful Git commit
* An explanation of technical decisions

The Git history is intended to show how the architecture and implementation
evolve over time.

The project uses feature branches and pull requests for incremental changes.

The current development flow is:

```text
Feature branch
      │
      ▼
Implementation
      │
      ▼
Local build and tests
      │
      ▼
Commit and push
      │
      ▼
Pull request
      │
      ▼
GitHub Actions
      │
      ▼
Squash merge
      │
      ▼
Main
```

Quality checks run locally and through GitHub Actions before changes are merged
into the main branch.

## Planned milestones

### Milestone 1: Project foundation — Complete

* [x] Repository structure
* [x] Documentation
* [x] Python package setup
* [x] Battery simulation
* [x] Unit tests
* [x] Linting
* [x] Static type checking
* [x] Continuous integration

### Milestone 2: Energy simulation — Complete

* [x] Solar generation model
* [x] Building consumption model
* [x] Grid connection model
* [x] Simulation timeline
* [x] Energy measurements
* [x] Scenario configuration

### Milestone 3: Control logic — Complete

* [x] Initial energy control rules
* [x] C++ project setup
* [x] Measurement input
* [x] Control commands
* [x] Safety limits
* [x] Initial controller unit-test infrastructure
* [x] Performance benchmarks

Milestone 3 completion status:

```text
C++ project foundation       Complete
Measurement input            Complete
Control commands             Complete
C++ test infrastructure      Complete
Linux C++ CI                 Complete
Initial control rules        Complete
Safety limits                Complete
Performance benchmarks       Complete
```

### Milestone 4: Hardware abstraction — Next

* [ ] C project setup
* [ ] Sensor interfaces
* [ ] Actuator interfaces
* [ ] Simulated hardware devices
* [ ] Error handling
* [ ] Controller integration

### Milestone 5: Backend API

* [ ] ASP.NET Core solution
* [ ] REST endpoints
* [ ] Application services
* [ ] Health checks
* [ ] Structured logging
* [ ] Integration with simulation and controller components

### Milestone 6: Containers and Linux

* [ ] Dockerfiles
* [ ] Docker Compose
* [x] Initial Linux C++ builds through GitHub Actions
* [ ] Development scripts
* [ ] Component networking
* [ ] Environment configuration

### Milestone 7: DevOps and Azure

* [x] Initial GitHub Actions quality checks
* [x] Python automated build and test workflow
* [x] Initial C++ automated build and test workflow
* [ ] Automated multi-component builds
* [ ] Extended code-quality checks
* [ ] Container image creation
* [ ] Azure deployment
* [ ] Monitoring and telemetry

### Milestone 8: Frontend dashboard

* [ ] System overview
* [ ] Battery status
* [ ] Solar production
* [ ] Building consumption
* [ ] Grid import and export
* [ ] Controller decisions
* [ ] Alerts and system health

## Testing strategy

The project uses several types of testing.

### Unit tests

Unit tests verify individual classes and functions in isolation.

Current Python examples include:

* Battery charging behavior
* Battery discharging behavior
* Solar generation
* Building consumption
* Energy balance calculations
* Battery dispatch
* Grid transfer limits
* Energy management behavior
* Measurement validation
* Timeline behavior
* Scenario reproducibility

Current C++ examples include:

* Valid energy measurement construction
* Measurement value preservation
* Signed grid import calculation
* Signed grid export calculation
* Rejection of invalid measurement step numbers
* Rejection of non-positive measurement intervals
* Rejection of negative energy values
* Rejection of non-finite measurement values
* Rejection of simultaneous grid import and export
* Valid active control commands
* Explicit idle control commands
* Rejection of invalid command source steps
* Rejection of negative command power
* Rejection of non-finite command power
* Rejection of idle commands with requested power
* Rejection of active commands with zero requested power
* Valid controller operating-limit configuration
* Rejection of invalid controller operating limits
* Surplus-to-charge controller decisions
* Deficit-to-discharge controller decisions
* Balanced-energy idle decisions
* Interval-energy to requested-power conversion
* Floating-point balance tolerance
* Maximum charge-power limiting
* Maximum discharge-power limiting
* Maximum battery state-of-charge protection
* Minimum battery state-of-charge protection
* Charge limiting by remaining battery capacity
* Discharge limiting by minimum battery reserve

### Scenario tests

Scenario tests verify complete energy situations.

Examples include:

* High solar production and low consumption
* Low solar production and high consumption
* Fully charged battery
* Empty battery
* Grid connection failure
* Grid transfer limits

Later scenarios may include:

* Battery overheating
* Safety shutdown
* Load shedding
* Cross-component control-command behavior

### Integration tests

Integration tests will verify communication between components.

Examples include:

* Simulation engine to controller
* Controller to hardware abstraction
* ASP.NET Core API to system components

### Performance benchmarks

The C++ controller includes a dedicated microbenchmark executable.

The benchmark currently measures:

* Surplus controller decisions
* Deficit controller decisions
* Balanced controller decisions
* Total measured execution time
* Average nanoseconds per decision
* Decisions per second

The benchmark uses:

* `std::chrono::steady_clock`
* A Release build
* 100,000 warmup iterations per case
* 10,000,000 measured iterations per case
* Result consumption through a checksum

The checksum keeps the controller output observable and reduces the risk of the
compiler removing the work being measured as unused.

The benchmark deliberately remains separate from the unit tests.

Unit tests answer:

```text
Is the controller behavior correct?
```

The benchmark answers:

```text
How does the current controller decision path perform?
```

The benchmark is executed in Linux CI as a smoke test, but CI does not enforce
performance thresholds.

Shared CI runners can differ in:

* CPU hardware
* Virtualization
* Current system load
* Compiler environment
* Power-management behavior

Performance values from CI are therefore not treated as stable acceptance
criteria.

## Current quality baseline

### Python

At the completion of Milestone 2:

```text
127 tests passed
100% coverage of the tested Python domain modules
Ruff passed
mypy passed
GitHub Actions passed
```

Test coverage is used as one quality signal.

A coverage percentage of 100% does not by itself guarantee that every possible
behavior is correct.

Tests are expected to verify meaningful domain rules, boundaries and edge cases.

### C++

The current C++ correctness baseline includes:

```text
35 C++ tests passed
8 EnergyMeasurement tests
7 ControlCommand tests
7 ControllerLimits tests
13 EnergyController tests
Debug build passed with MSVC
Release build passed with MSVC
CTest passed
Linux GitHub Actions build passed
Linux GitHub Actions tests passed
Controller CLI smoke test passed
Controller benchmark smoke test passed
```

The C++ quality baseline covers:

* Domain contracts
* Defensive validation
* Deterministic controller decisions
* Battery operating constraints
* Windows and Linux builds
* Unit-test execution
* CLI linkage and execution
* Benchmark compilation and execution

### C++ performance baseline

Representative local Windows/MSVC Release microbenchmark measurements were:

```text
Surplus decision:   approximately 23–25 ns/decision
Deficit decision:   approximately 23–24 ns/decision
Balanced decision:  approximately 11 ns/decision
```

Across five longer local benchmark runs, representative median measurements were
approximately:

```text
Surplus decision:   24.29 ns/decision
Deficit decision:   23.03 ns/decision
Balanced decision:  11.05 ns/decision
```

These measurements are development-machine microbenchmark results.

They are not real-time guarantees, production service-level objectives or
portable performance guarantees.

The measured loop also includes minimal checksum work used to consume the
generated `ControlCommand` and keep the result observable to the optimizer.

The purpose of the baseline is to make controller performance measurable before
additional controller complexity is introduced.

## Continuous integration

The repository currently contains separate quality workflows for Python and C++.

### Python Quality

The Python workflow:

* Installs Python 3.12
* Installs the simulation package and development dependencies
* Runs Ruff
* Runs mypy
* Runs pytest with coverage

### C++ Quality

The C++ workflow:

* Runs on Ubuntu
* Displays CMake and compiler versions
* Configures the controller as a Release build
* Enables C++ testing
* Enables C++ benchmark builds
* Builds the controller
* Builds the benchmark executable
* Runs CTest
* Executes the controller CLI as a smoke test
* Executes the controller benchmark as a smoke test

This gives the C++ component validation on both:

```text
Local development:
Windows + MSVC

Continuous integration:
Linux + C++ toolchain
```

Performance timings from the shared Linux CI runner are not used as pass/fail
thresholds.

## C++ build structure

The controller is built as a reusable static library:

```text
control_command.cpp
controller.cpp
controller_limits.cpp
energy_controller.cpp
energy_measurement.cpp
        │
        ▼
gridflex_controller
```

Multiple executables consume the same library:

```text
                        gridflex_controller
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
gridflex_controller_cli   controller tests   controller benchmark
```

The concrete targets are:

```text
gridflex_controller
        │
        ├──────────────► gridflex_controller_cli
        │
        ├──────────────► gridflex_controller_tests
        │
        └──────────────► gridflex_controller_benchmark
```

This keeps reusable controller logic and domain models separate from:

* CLI entry points
* Correctness tests
* Performance measurement infrastructure

The benchmark does not reimplement controller behavior.

It links against the same `gridflex_controller` library used by the other C++
executables.

## C++ testing infrastructure

The C++ component uses:

* Catch2 as the unit-test framework
* CTest as the CMake-integrated test runner

Catch2 provides the test API, including test cases and assertions.

CTest provides test discovery and execution at the build-system level.

The relationship is:

```text
C++ test source
      │
      ▼
Catch2
      │
      ▼
gridflex_controller_tests
      │
      ▼
CTest
      │
      ▼
Pass / fail result
```

The same CTest integration is used locally and through GitHub Actions.

The current test executable includes tests for:

```text
EnergyMeasurement
        │
        ├── validation
        ├── value preservation
        └── grid-net calculation

ControlCommand
        │
        ├── validation
        ├── idle behavior
        └── active-command behavior

ControllerLimits
        │
        ├── valid configuration
        └── invalid-boundary rejection

EnergyController
        │
        ├── deterministic decisions
        ├── requested-power calculation
        ├── balance tolerance
        ├── charge and discharge power limits
        └── state-of-charge protection
```

## C++ benchmark infrastructure

The controller benchmark is built as a separate executable:

```text
energy_controller_benchmark.cpp
              │
              ▼
gridflex_controller_benchmark
              │
              │ links against
              ▼
gridflex_controller
```

Benchmark builds are controlled through the CMake option:

```text
GRIDFLEX_BUILD_BENCHMARKS
```

The default value is:

```text
OFF
```

This means normal users of the controller do not have to build performance
tooling.

Benchmark development enables it explicitly:

```text
-DGRIDFLEX_BUILD_BENCHMARKS=ON
```

The benchmark currently executes three decision paths:

```text
EnergyMeasurement
        │
        ▼
EnergyController::decide()
        │
        ├── Surplus  → ChargeBattery
        ├── Deficit  → DischargeBattery
        └── Balanced → Idle
        │
        ▼
ControlCommand
```

Measurement objects and controller configuration are constructed before the
timed loop.

The timed loop therefore focuses on the controller decision path rather than
measurement construction and validation.

Each case performs:

```text
100,000 warmup iterations
          │
          ▼
10,000,000 measured iterations
          │
          ▼
elapsed time
          │
          ├── nanoseconds per decision
          └── decisions per second
```

The benchmark consumes each produced command through a checksum.

Conceptually:

```text
EnergyController::decide()
          │
          ▼
ControlCommand
          │
          ▼
checksum
```

The checksum has no energy-domain meaning.

Its purpose is to make benchmark output observable so that compiler
optimization cannot trivially discard unused controller results.

## Security considerations

The current version runs as a local simulation and does not control physical
equipment.

Later security work may include:

* Authentication
* Authorization
* Input validation at service boundaries
* Secret management
* Secure service communication
* Dependency scanning
* Container scanning
* Audit logging

## Safety considerations

GridFlex EMS is an educational software simulation.

It must not be used to control real batteries, electrical installations,
industrial equipment or energy infrastructure.

The project does not implement certified electrical safety functionality,
protection systems or production-ready control logic.

Safety-related controller behavior in the project remains educational and
simulated.

## Out of scope

The current GridFlex EMS project does not include:

* Control of real electrical equipment
* Certified safety functionality
* Real PLC communication
* Production battery management protocols
* Electrical protection systems
* Grid synchronization
* Regulatory compliance
* Real-time operating system guarantees
* Production deployment to industrial installations

## Technology choices

The planned technology responsibilities are:

| Area                    | Technology          | Purpose                               |
| ----------------------- | ------------------- | ------------------------------------- |
| Backend                 | C# and ASP.NET Core | APIs and application coordination     |
| Simulation              | Python              | Energy models and scenario simulation |
| Controller              | C++                 | Performance-oriented control logic    |
| Hardware abstraction    | C                   | Low-level and embedded concepts       |
| Containers              | Docker              | Reproducible runtime environments     |
| CI/CD                   | GitHub Actions      | Automated builds and tests            |
| Cloud                   | Microsoft Azure     | Deployment and observability          |
| Development environment | Windows and Linux   | Cross-platform development            |

Each technology must have a clear responsibility.

A technology will not be added only to increase the number of technologies in
the repository.

## Documentation

Technical documentation is stored in the `docs` directory.

The main architecture document is:

[GridFlex EMS Architecture](docs/architecture.md)

The detailed Python simulation architecture is:

[Python Simulation Architecture](docs/simulation-architecture.md)

Important architectural decisions are stored as Architecture Decision Records
in:

```text
docs/decisions/
```

Each Architecture Decision Record documents:

* The technical context
* The selected decision
* Alternatives considered
* Positive consequences
* Negative consequences

## Running the Python simulation

The Python simulation package is located in:

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

Run the demonstration scenario:

```powershell
gridflex-simulation
```

## Running the Python tests

From the `simulation` directory:

```powershell
python -m pytest
```

Run tests with coverage:

```powershell
python -m pytest --cov=gridflex_simulation --cov-report=term-missing
```

## Running Python linting

From the `simulation` directory:

```powershell
python -m ruff check .
```

Automatically fix supported Ruff findings:

```powershell
python -m ruff check . --fix
```

## Running Python static type checking

From the `simulation` directory:

```powershell
python -m mypy
```

## Running the complete Python quality check

From the `simulation` directory:

```powershell
python -m ruff check .
python -m mypy
python -m pytest --cov=gridflex_simulation --cov-report=term-missing
```

## Building the C++ controller

The C++ controller is located in:

```text
controller/
```

On Windows, initialize a Visual Studio Developer PowerShell environment before
building.

Configure the project with tests enabled:

```powershell
cmake `
  -S controller `
  -B controller/build `
  -DBUILD_TESTING=ON
```

Build the Debug configuration:

```powershell
cmake `
  --build controller/build `
  --config Debug
```

Build the Release configuration:

```powershell
cmake `
  --build controller/build `
  --config Release
```

## Running the C++ tests

Run the Debug tests:

```powershell
ctest `
  --test-dir controller/build `
  -C Debug `
  --output-on-failure
```

Run the Release tests:

```powershell
ctest `
  --test-dir controller/build `
  -C Release `
  --output-on-failure
```

The current expected result is:

```text
100% tests passed
0 tests failed out of 35
```

## Running the C++ controller CLI

After building the Release configuration on Windows:

```powershell
& ".\controller\build\Release\gridflex_controller_cli.exe"
```

Current output:

```text
GridFlex EMS C++ Controller
```

The CLI is intentionally small.

Its purpose at the current stage is to verify that the reusable controller
library can be linked into and consumed by an executable.

Additional controller behavior and integration will continue to be developed
incrementally behind the library interface.

## Running the C++ controller benchmark

Configure the controller with benchmark builds enabled:

```powershell
cmake `
  -S controller `
  -B controller/build `
  -DBUILD_TESTING=ON `
  -DGRIDFLEX_BUILD_BENCHMARKS=ON
```

Build the Release benchmark:

```powershell
cmake `
  --build controller/build `
  --config Release `
  --target gridflex_controller_benchmark
```

Run the benchmark on Windows:

```powershell
& ".\controller\build\Release\gridflex_controller_benchmark.exe"
```

The benchmark currently reports:

```text
Total measured time
Average nanoseconds per decision
Decisions per second
Checksum
```

for:

```text
Surplus decision
Deficit decision
Balanced decision
```

The current configuration uses:

```text
Warmup iterations per case:   100,000
Measured iterations per case: 10,000,000
```

The benchmark should be run using a Release build.

Debug builds are intended for debugging and correctness work and are not used as
the controller performance baseline.

Performance results should be interpreted as measurements from the machine and
compiler configuration on which they were produced.

They are not portable timing guarantees.

## Current controller architecture

The controller has explicit models on both sides of its domain boundary and a
validated operating-limit configuration.

```text
                  ControllerLimits
                        │
                        │ configuration
                        ▼
                  ┌──────────────┐
                  │              │
EnergyMeasurement ─────► EnergyController
                  │              │
                  └──────┬───────┘
                         │
                         │ deterministic decision
                         ▼
                  ControlCommand
```

`EnergyMeasurement` describes what the controller knows about the current
energy situation.

`ControllerLimits` describes the operating boundaries the controller must
respect.

`ControlCommand` describes what the controller is allowed to request.

Separating these responsibilities means that:

* Measurement validation is independent of decision logic
* Command validation is independent of decision logic
* Operating-limit validation is independent of individual measurements
* Controller rules can operate on already valid input
* Controller decisions can be constrained by validated configuration
* Downstream components can receive already valid commands
* Each responsibility can be tested independently

## C++ controller decision logic

The C++ `EnergyController` transforms a validated `EnergyMeasurement` into a
validated `ControlCommand`.

The controller currently implements deterministic battery-first control rules.

At a high level:

```text
EnergyMeasurement
        │
        ▼
EnergyController
        │
        ├── Balanced energy → Idle
        ├── Energy surplus  → ChargeBattery
        └── Energy deficit  → DischargeBattery
        │
        ▼
ControlCommand
```

The controller uses a small floating-point tolerance around zero so that tiny
numeric residuals do not result in unnecessary battery commands.

For an active command, interval energy is converted to requested power using:

```text
requested power kW = |net energy kWh| / interval hours
```

For example:

```text
Net energy: 10 kWh
Interval:   0.5 hours

Requested power:
10 kWh / 0.5 h = 20 kW
```

### Controller operating limits

The controller receives its operating boundaries through a validated
`ControllerLimits` object.

The current configuration contains:

* Maximum charge power
* Maximum discharge power
* Minimum battery state of charge
* Maximum battery state of charge

These values are provided to the controller instead of being hardcoded into the
decision logic.

Conceptually:

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

For battery charging, the final command power is the minimum of:

```text
Requested charge power
Configured maximum charge power
Power allowed by remaining battery capacity
```

For example:

```text
Requested charge power:        50 kW
Maximum charge power:          25 kW
Remaining SOC allows:          10 kW

Final ChargeBattery command:   10 kW
```

The same principle applies when discharging.

The final discharge power is the minimum of:

```text
Requested discharge power
Configured maximum discharge power
Power available above the minimum battery reserve
```

If the battery is already at its maximum state of charge, further charging is
prevented and the controller returns an `Idle` command.

If the battery is already at its minimum state of charge, further discharging
is prevented in the same way.

This separates controller intent from operating constraints:

```text
Energy condition
      │
      ▼
Desired controller action
      │
      ▼
Power and SOC constraints
      │
      ▼
Allowed ControlCommand
```

Grid fallback behavior is intentionally not part of the current controller
logic yet.

For example, if a deficit remains when the battery reaches its minimum state of
charge, the controller currently returns `Idle` rather than automatically
creating an `ImportFromGrid` command.

Grid prioritization and fallback behavior will be introduced separately so that
battery control, operating constraints and grid strategy remain independently
testable.

## C++ controller performance measurement

Performance measurement was introduced after the initial deterministic
controller behavior and operating limits were established.

This sequence makes it possible to benchmark a known controller baseline before
additional strategy and integration complexity is introduced.

The current benchmark flow is:

```text
Validated EnergyMeasurement
          │
          ▼
EnergyController::decide()
          │
          ▼
ControlCommand
          │
          ▼
Minimal checksum consumption
          │
          ▼
Timing result
```

Three control paths are measured independently:

```text
Surplus
   │
   ▼
ChargeBattery

Deficit
   │
   ▼
DischargeBattery

Balanced
   │
   ▼
Idle
```

Balanced decisions currently take a shorter logical path through the controller
than active charge or discharge decisions.

The benchmark therefore makes both controller performance and differences
between decision paths visible.

The benchmark baseline is intended to support comparisons as future controller
behavior is added.

## Next development step

Milestone 3 is complete.

Completed C++ controller work:

```text
C++ project structure             Complete
CMake configuration               Complete
Static controller library         Complete
Controller CLI                    Complete
Windows MSVC build                Complete
Linux CI build                    Complete
EnergyMeasurement input           Complete
Measurement validation            Complete
ControlCommand output             Complete
Control command validation        Complete
Initial deterministic rules       Complete
Controller operating limits       Complete
Battery SOC protection            Complete
Catch2 integration                Complete
CTest integration                  Complete
C++ CI test execution              Complete
Benchmark infrastructure          Complete
Release benchmark build           Complete
Surplus benchmark                  Complete
Deficit benchmark                  Complete
Balanced benchmark                 Complete
Linux benchmark smoke test         Complete
```

The next development milestone is:

```text
Milestone 4: Hardware abstraction
```

The next implementation sequence is planned as:

```text
C project setup
      │
      ▼
Sensor interfaces
      │
      ▼
Actuator interfaces
      │
      ▼
Simulated hardware devices
      │
      ▼
Error handling
      │
      ▼
Controller integration
```

This introduces a separate low-level boundary beneath the C++ controller:

```text
EnergyMeasurement
      │
      ▼
C++ EnergyController
      │
      │ ControlCommand
      ▼
C Hardware Abstraction Layer
      │
      ├── Sensor interfaces
      ├── Actuator interfaces
      └── Simulated devices
```

The purpose of the C hardware abstraction layer is not to add another language
for its own sake.

It introduces a component with a different technical responsibility:

```text
Python
Simulation and reference behavior

C++
Deterministic and performance-oriented control logic

C
Low-level hardware-facing interfaces
```

The communication mechanism between the larger Python, C++, C and future C#
components will be selected separately and documented through an Architecture
Decision Record.

## Disclaimer

GridFlex EMS is an independent educational portfolio project.

It is not based on proprietary software, confidential documentation, internal
architecture or protected information belonging to PowerCon or any other
energy company.

The project represents a simplified and fictional Energy Management System
created solely for learning and portfolio purposes.
