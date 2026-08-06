# GridFlex EMS

GridFlex EMS is an independent portfolio and learning project that demonstrates
the architecture and development of a modular Energy Management System.

The system simulates and coordinates energy flows between:

- A Battery Energy Storage System, also known as BESS
- Solar power generation
- The electrical grid
- Building energy consumption
- Electric vehicle chargers

The project focuses on software architecture, reliability, performance,
automated testing, observability and communication between components written
in different programming languages.

## Project purpose

The purpose of GridFlex EMS is to demonstrate how a larger technical software
solution can be divided into components with clear responsibilities.

The project is also used as a structured learning environment for technologies
commonly used in industrial, embedded and energy-related software development.

The system will gradually include components written in:

- C#
- Python
- C++
- C

The project is developed incrementally so that each architectural decision,
implementation step and technology choice can be explained and justified.

## Project goals

GridFlex EMS is designed to demonstrate practical experience with:

- C# and ASP.NET Core
- Python
- C++
- C
- Linux
- Docker
- GitHub Actions
- Microsoft Azure
- REST APIs
- Software architecture
- Automated testing
- Static code analysis
- Observability
- Performance measurement
- Cross-language communication
- Defensive programming
- Technical documentation

## System overview

GridFlex EMS models a simplified energy installation.

The installation contains:

- A solar power source
- A battery storage system
- A connection to the electrical grid
- A building with varying energy consumption
- One or more electric vehicle chargers

The system receives measurements from these energy assets and determines how
energy should be distributed.

Examples of system decisions include:

- Charging the battery when solar production exceeds local consumption
- Discharging the battery when local consumption exceeds solar production
- Importing energy from the electrical grid when local energy is insufficient
- Exporting surplus energy when the battery is fully charged
- Reducing energy usage when system limits are reached
- Stopping battery activity if unsafe operating conditions are detected

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
│  - Application coordination                 │
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

- Exposing system status through REST endpoints
- Receiving commands from users or external systems
- Coordinating application-level use cases
- Exposing health checks
- Providing structured logging
- Exposing metrics later in the project
- Supporting authentication and authorization in a later milestone

### Python simulation engine

The Python simulation engine will be responsible for:

- Simulating solar power generation
- Simulating building energy consumption
- Simulating battery behavior
- Creating reproducible operating scenarios
- Producing measurement data
- Supporting experiments and energy analysis
- Testing control strategies before they are used by the controller

### C++ controller

The C++ controller will be responsible for:

- Receiving energy measurements
- Evaluating operating conditions
- Making control decisions
- Applying safety and operating limits
- Prioritizing energy sources
- Demonstrating performance-oriented software development
- Producing deterministic and testable control behavior

### C hardware abstraction layer

The C hardware abstraction layer will be responsible for:

- Representing low-level sensors
- Representing actuators
- Providing driver-like interfaces
- Hiding hardware-specific details from the controller
- Simulating communication with physical equipment
- Introducing embedded software concepts

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
│   ├── Architecture documentation
│   └── Architecture Decision Records
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

The first planned data flow is:

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

- HTTP
- gRPC
- Message queues
- Shared libraries
- Standard input and output streams
- Local sockets

## Current status

GridFlex EMS is under active development.

The first milestone focuses on:

1. Establishing a professional repository structure
2. Documenting the initial architecture
3. Creating the Python simulation package
4. Implementing a simplified battery model
5. Adding automated tests
6. Adding linting and static type checking
7. Creating a continuous integration pipeline

## Initial simulation scope

The first simulation component models a simplified battery.

The battery initially supports:

- Total capacity measured in kilowatt-hours
- Current state of charge
- Available storage capacity
- Charging
- Discharging
- State-of-charge calculation
- Validation of invalid battery states

Later versions may include:

- Charging efficiency
- Discharging efficiency
- Maximum charging power
- Maximum discharging power
- Battery temperature
- Battery degradation
- Minimum and maximum state-of-charge limits
- Emergency shutdown behavior

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

- A clearly defined goal
- A small implementation scope
- Automated tests
- Documentation
- A meaningful Git commit
- An explanation of technical decisions

The Git history is intended to show how the architecture and implementation
evolve over time.

## Planned milestones

### Milestone 1: Project foundation

- Repository structure
- Documentation
- Python package setup
- Battery simulation
- Unit tests
- Linting
- Static type checking
- Continuous integration

### Milestone 2: Energy simulation

- Solar generation model
- Building consumption model
- Grid connection model
- Simulation timeline
- Energy measurements
- Scenario configuration

### Milestone 3: Control logic

- Initial energy control rules
- C++ project setup
- Measurement input
- Control commands
- Safety limits
- Unit tests
- Performance benchmarks

### Milestone 4: Hardware abstraction

- C project setup
- Sensor interfaces
- Actuator interfaces
- Simulated hardware devices
- Error handling
- Controller integration

### Milestone 5: Backend API

- ASP.NET Core solution
- REST endpoints
- Application services
- Health checks
- Structured logging
- Integration with simulation and controller components

### Milestone 6: Containers and Linux

- Dockerfiles
- Docker Compose
- Linux builds
- Development scripts
- Component networking
- Environment configuration

### Milestone 7: DevOps and Azure

- GitHub Actions
- Automated builds
- Automated tests
- Code-quality checks
- Container image creation
- Azure deployment
- Monitoring and telemetry

### Milestone 8: Frontend dashboard

- System overview
- Battery status
- Solar production
- Building consumption
- Grid import and export
- Controller decisions
- Alerts and system health

## Testing strategy

The project will use several types of testing.

### Unit tests

Unit tests verify individual classes and functions in isolation.

Examples include:

- Battery charging behavior
- Battery discharging behavior
- Input validation
- Energy calculation rules

### Integration tests

Integration tests will verify communication between components.

Examples include:

- Simulation engine to controller
- Controller to hardware abstraction
- ASP.NET Core API to system components

### Scenario tests

Scenario tests will verify complete energy situations.

Examples include:

- High solar production and low consumption
- Low solar production and high consumption
- Fully charged battery
- Empty battery
- Grid connection failure
- Battery overheating

### Performance tests

Performance tests will measure controller execution time and simulation
throughput.

## Security considerations

The first version runs as a local simulation and does not control physical
equipment.

Later security work may include:

- Authentication
- Authorization
- Input validation
- Secret management
- Secure service communication
- Dependency scanning
- Container scanning
- Audit logging

## Safety considerations

GridFlex EMS is an educational software simulation.

It must not be used to control real batteries, electrical installations,
industrial equipment or energy infrastructure.

The project does not implement certified electrical safety functionality,
protection systems or production-ready control logic.

## Out of scope

The initial versions of GridFlex EMS do not include:

- Control of real electrical equipment
- Certified safety functionality
- Real PLC communication
- Production battery management protocols
- Electrical protection systems
- Grid synchronization
- Regulatory compliance
- Real-time operating system guarantees
- Production deployment to industrial installations

## Technology choices

The initial technology choices are:

| Area | Technology | Purpose |
|---|---|---|
| Backend | C# and ASP.NET Core | APIs and application coordination |
| Simulation | Python | Energy models and scenario simulation |
| Controller | C++ | Performance-oriented control logic |
| Hardware abstraction | C | Low-level and embedded concepts |
| Containers | Docker | Reproducible runtime environments |
| CI/CD | GitHub Actions | Automated builds and tests |
| Cloud | Microsoft Azure | Deployment and observability |
| Development environment | Windows and Linux | Cross-platform development |

Each technology must have a clear responsibility.

A technology will not be added only to increase the number of technologies in
the repository.

## Documentation

Technical documentation is stored in the `docs` directory.

Important architectural decisions are stored as Architecture Decision Records
in:

```text
docs/decisions/
```

Each Architecture Decision Record documents:

- The technical context
- The selected decision
- Alternatives considered
- Positive consequences
- Negative consequences

## Running the project

The complete system cannot be started yet because the project is being built
incrementally.

The Python simulation package can be installed from the `simulation`
directory.

```powershell
cd simulation
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Run the simulation:

```powershell
gridflex-simulation
```

Run the automated tests:

```powershell
pytest
```

Run linting:

```powershell
ruff check .
```

Run static type checking:

```powershell
mypy
```

Run test coverage:

```powershell
pytest --cov=gridflex_simulation --cov-report=term-missing
```

## Disclaimer

GridFlex EMS is an independent educational portfolio project.

It is not based on proprietary software, confidential documentation, internal
architecture or protected information belonging to PowerCon or any other
energy company.

The project represents a simplified and fictional energy management system
created solely for learning and portfolio purposes.