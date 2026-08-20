# GridFlex EMS Architecture

## Purpose

GridFlex EMS models a simplified Energy Management System that coordinates
energy generation, consumption, storage and grid interaction.

The system is divided into independently testable components to demonstrate how
multiple programming languages and technical environments can cooperate in one
software solution.

## System context

The Energy Management System receives measurements from simulated energy assets
and determines an appropriate operational action.

Examples include:

- Charging the battery when solar production exceeds consumption
- Discharging the battery during periods of high consumption
- Importing energy from the grid when local production is insufficient
- Exporting energy when production exceeds local consumption and storage capacity
- Reducing charging activity if a component reports a critical temperature
- Rejecting invalid measurements before they reach the controller

## System boundaries

The project models software behavior only.

It does not control real electrical equipment and does not implement certified
safety functionality.

External systems and physical equipment are represented through simulations and
software abstractions.

## Main components

### ASP.NET Core API

Responsibilities:

- Expose system status through HTTP endpoints
- Accept commands from users and external systems
- Coordinate application-level use cases
- Provide health checks
- Provide structured logging
- Expose metrics later in the project
- Manage authentication and authorization in a later milestone

### Python simulation engine

Responsibilities:

- Simulate solar generation
- Simulate building consumption
- Simulate battery behavior
- Simulate grid import and export
- Produce measurement data
- Support reproducible test scenarios
- Support experiments with different operating strategies

The Python simulation milestone is now implemented.

The detailed internal simulation architecture, including energy balance,
battery dispatch, grid handling, timelines, measurements and reproducible
scenario execution, is documented in:

[Python Simulation Architecture](simulation-architecture.md)


### C++ controller

Responsibilities:

- Evaluate incoming measurements
- Make time-sensitive control decisions
- Apply operating limits and safety rules
- Select appropriate energy actions
- Produce control commands
- Demonstrate performance-oriented software development

### C hardware abstraction layer

Responsibilities:

- Provide low-level sensor interfaces
- Provide actuator interfaces
- Simulate communication with physical hardware
- Hide hardware-specific details from the controller
- Represent embedded software concepts
- Report hardware-related errors

## Current controller data flow

The implemented backend-to-controller path is:

```text
HTTP client
       │
       │ JSON request
       ▼
ASP.NET Core API
       │
       │ ControlDecisionRequest
       ▼
ControlDecisionService
       │
       │ EnergyMeasurementInput
       ▼
IControllerGateway
       │
       ▼
NativeControllerGateway
       │
       │ LibraryImport
       ▼
Versioned C ABI
       │
       ▼
C++ EnergyController
       │
       │ ControlCommand
       ▼
C hardware abstraction
```

The .NET application layer does not depend on native implementation details.

`IControllerGateway` forms the application boundary, while
`NativeControllerGateway` owns the infrastructure-specific interoperability.

The managed/native integration uses:

- A native shared library
- A versioned C ABI
- Source-generated `.NET` `LibraryImport`
- Explicit structure and enum mapping
- `SafeHandle` for native lifetime management
- Native ABI compatibility validation
- Managed translation of native error statuses

The architectural decision is documented in:

[ADR 0002: Use a C ABI for .NET to C++ controller interoperability](decisions/0002-use-c-abi-for-dotnet-cpp-interop.md)

Python-to-backend integration remains a later architectural concern.

## Initial battery model

The first implemented domain component is a simplified battery.

The battery contains:

- Total capacity in kilowatt-hours
- Current state of charge in kilowatt-hours
- Available storage capacity
- State of charge as a percentage

The battery supports:

- Charging
- Discharging
- Capacity validation
- State validation

The first battery model does not yet include:

- Charging losses
- Discharging losses
- Temperature
- Degradation
- Maximum charge rate
- Maximum discharge rate
- Minimum reserve level

These concepts will be added incrementally.

## Quality attributes

### Robustness

The system must validate measurements and reject invalid values.

Components should fail in a controlled and understandable way.

### Performance

Control decisions should be predictable and measurable.

Performance-sensitive logic should be benchmarked rather than assumed to be
fast.

### Scalability

Simulation, control and hardware components should be replaceable without
redesigning the entire system.

### Testability

Business rules should be testable without running the complete system.

### Maintainability

Components should have clear responsibilities and limited coupling.

### Observability

Important decisions, state changes and failures should be visible through logs
and metrics.

### Portability

The system should support local Windows development and Linux-based execution.

## Architectural principles

The architecture follows these principles:

- Separation of concerns
- Explicit interfaces
- Dependency direction
- Small testable components
- Defensive validation
- Technology choices based on responsibility
- Incremental delivery
- Documented decisions

## Integration strategy

Cross-language integration is introduced only where a concrete boundary needs
it.

The current .NET-to-C++ controller integration is in-process:

```text
ASP.NET Core
    │
    ▼
Application abstraction
    │
    ▼
Native gateway
    │
    ▼
C ABI
    │
    ▼
C++ controller
```

The application layer depends on `IControllerGateway`, not on native APIs.

This preserves the option to replace the infrastructure implementation later
with another transport such as IPC or a separate service without redesigning
the application use case.

The C++ controller continues to interact with the C hardware abstraction layer
through native C/C++ interfaces.

Python integration remains independent and has not yet been connected directly
to the ASP.NET Core backend.

## Error handling

Each component should:

- Validate input at its boundary
- Return meaningful errors
- Avoid silently ignoring failures
- Log failures with useful context
- Avoid exposing internal implementation details unnecessarily

## Testing approach

Each component supports automated testing.

The current testing strategy includes:

- Python unit tests with pytest
- Python static type checking with mypy
- Python linting with Ruff
- C++ unit and integration tests with Catch2
- C++ test execution through CTest
- Native C tests through CTest
- .NET unit and integration tests with xUnit
- ASP.NET Core application startup tests
- HTTP endpoint integration tests
- Native runtime interoperability tests
- End-to-end HTTP-to-C++ controller testing
- GitHub Actions quality workflows for Python, C, C++ and backend code

## Deployment approach

The project currently supports local Windows development and automated
Linux-based validation through GitHub Actions.

The backend and native controller are currently validated as development and
CI components rather than as a production deployment.

Later milestones will introduce:

- Docker containers
- Docker Compose
- Native-library packaging for deployment
- Azure deployment
- Centralized logs
- Metrics and monitoring

## Security

The initial version runs locally and contains no authentication.

Future milestones may introduce:

- Authentication
- Role-based authorization
- Secret management
- Secure service communication
- Dependency scanning
- Container scanning
- Audit logging

## Safety limitation

GridFlex EMS is an educational simulation.

It must not be used to control real batteries, electrical equipment, industrial
systems or energy infrastructure.

## Out of scope

The first version does not implement:

- Electrical protection systems
- Certified safety functionality
- Real PLC communication
- Production grid synchronization
- Real battery management protocols
- Hard real-time guarantees
- Regulatory compliance