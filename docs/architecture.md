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

## Initial data flow

```text
Python Simulation
       │
       │ Measurements
       ▼
C++ Controller
       │
       │ Commands
       ▼
C Hardware Abstraction
       │
       │ Equipment state
       ▼
ASP.NET Core API
       │
       │ Status
       ▼
Frontend Dashboard
```

The exact integration mechanism will be selected in a later Architecture
Decision Record.

Possible options include:

- HTTP
- gRPC
- Message queues
- Shared libraries
- Standard input and output streams
- Local sockets

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

The first milestone does not establish cross-language communication.

Each component will initially be developed and tested independently.

This allows the project to establish correct domain behavior before introducing
integration complexity.

A later Architecture Decision Record will evaluate the communication mechanism
between Python, C++, C and ASP.NET Core.

## Error handling

Each component should:

- Validate input at its boundary
- Return meaningful errors
- Avoid silently ignoring failures
- Log failures with useful context
- Avoid exposing internal implementation details unnecessarily

## Testing approach

Each component must support automated testing.

The initial testing strategy includes:

- Python unit tests with pytest
- Static type checking with mypy
- Linting with Ruff
- C++ unit tests in a later milestone
- C unit tests in a later milestone
- .NET unit and integration tests in a later milestone
- Cross-component integration tests after communication is introduced

## Deployment approach

The initial development environment is local.

Later milestones will introduce:

- Docker containers
- Docker Compose
- Linux builds
- GitHub Actions
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