# GridFlex EMS

GridFlex EMS is an independent portfolio and learning project that demonstrates
the architecture and development of a modular Energy Management System.

The system simulates and coordinates energy flows between:

* A Battery Energy Storage System, also known as BESS
* Solar power generation
* The electrical grid
* Building energy consumption
* Electric vehicle chargers in a later milestone

The project focuses on software architecture, reliability, performance,
automated testing, observability and communication between components written
in different programming languages.

## Project purpose

The purpose of GridFlex EMS is to demonstrate how a larger technical software
solution can be divided into components with clear responsibilities.

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

The C++ controller will be responsible for:

* Receiving energy measurements
* Evaluating operating conditions
* Making control decisions
* Applying safety and operating limits
* Prioritizing energy sources
* Demonstrating performance-oriented software development
* Producing deterministic and testable control behavior

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
│
├── backend/
│   └── ASP.NET Core API and application services
│
├── controller/
│   └── Performance-oriented controller written in C++
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
│   └── Energy simulation components written in Python
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
          │ Measurements
          ▼
C++ Energy Controller
          │
          │ Control commands
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

## Current status

Milestone 1 and Milestone 2 are implemented.

The current Python simulation supports:

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

The detailed Python architecture is documented in:

[Python Simulation Architecture](docs/simulation-architecture.md)

The next development milestone introduces the C++ energy controller.

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

The current simplified energy-management strategy is battery-first.

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

Invalid measurements and impossible states should be rejected explicitly.

### Explicit interfaces

Communication between components should happen through documented interfaces.

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

### Milestone 3: Control logic

* [ ] Initial energy control rules
* [ ] C++ project setup
* [ ] Measurement input
* [ ] Control commands
* [ ] Safety limits
* [ ] Unit tests
* [ ] Performance benchmarks

### Milestone 4: Hardware abstraction

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
* [ ] Linux builds
* [ ] Development scripts
* [ ] Component networking
* [ ] Environment configuration

### Milestone 7: DevOps and Azure

* [x] Initial GitHub Actions quality checks
* [ ] Automated multi-component builds
* [ ] Automated multi-component tests
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

Current examples include:

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
* Control-command behavior

### Integration tests

Integration tests will verify communication between components.

Examples include:

* Simulation engine to controller
* Controller to hardware abstraction
* ASP.NET Core API to system components

### Performance tests

Performance tests will measure:

* Controller execution time
* Simulation throughput
* Time-sensitive decision behavior

## Current Python quality baseline

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

## Running the automated tests

From the `simulation` directory:

```powershell
python -m pytest
```

Run tests with coverage:

```powershell
python -m pytest --cov=gridflex_simulation --cov-report=term-missing
```

## Running linting

From the `simulation` directory:

```powershell
python -m ruff check .
```

Automatically fix supported Ruff findings:

```powershell
python -m ruff check . --fix
```

## Running static type checking

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

## Next development step

Milestone 2 is complete.

The next milestone introduces the C++ energy controller.

The planned direction is:

```text
Python Simulation
        │
        │ EnergyMeasurement
        ▼
C++ Energy Controller
        │
        │ Control commands
        ▼
C Hardware Abstraction Layer
```

The first C++ development steps will focus on:

- C++ project structure
- CMake
- Headers and source files
- Unit testing
- Measurement input model
- Control command model
- Initial deterministic control rules
- Safety limits
- Performance measurement

The communication mechanism between Python and C++ will be selected separately
and documented through an Architecture Decision Record.

## Disclaimer

GridFlex EMS is an independent educational portfolio project.

It is not based on proprietary software, confidential documentation, internal
architecture or protected information belonging to PowerCon or any other
energy company.

The project represents a simplified and fictional Energy Management System
created solely for learning and portfolio purposes.
