# ADR 0001: Use multiple programming languages

## Status

Accepted

## Context

GridFlex EMS is intended to demonstrate software engineering across backend,
simulation, performance-oriented and low-level development.

Using only one programming language would simplify development, building,
testing and deployment.

However, it would not provide practical experience with integration between
different technical environments.

The project must avoid adding technologies without a clear purpose.

## Decision

The project will initially use:

- C# for the HTTP API and application coordination
- Python for energy simulation and data analysis
- C++ for performance-oriented control logic
- C for hardware abstraction and embedded software concepts

Each language must have a clear and documented responsibility.

A language must not be introduced solely to increase the number of technologies
used by the project.

The components will initially be developed independently.

Cross-language communication will be introduced only after the individual
components have stable interfaces and automated tests.

## Consequences

### Positive consequences

- The repository demonstrates integration between multiple technologies
- Each language can be used for tasks suited to its strengths
- The project provides structured learning
- Architectural boundaries must be made explicit
- Components can be developed and tested independently
- The portfolio demonstrates broader technical understanding

### Negative consequences

- Builds and local development become more complex
- Cross-language communication must be designed carefully
- More development tools are required
- More documentation is required
- Continuous integration becomes more complex
- Debugging across process boundaries may be harder

## Alternatives considered

### Use only C#

This would simplify development and make effective use of existing experience.

It was rejected because it would provide less practical learning in Python,
C++ and C.

### Use only Python

This would support rapid development of the simulation and control rules.

It was rejected because Python is less appropriate for demonstrating low-level
hardware abstractions and performance-oriented controller development.

### Use only C++

This would allow simulation, controller and low-level functionality to share
one language.

It was rejected because it would not demonstrate backend API development in
ASP.NET Core or data-oriented simulation work in Python.

### Use C# and Python only

This would provide a simpler multi-language architecture.

It remains a reasonable alternative, but it was rejected because the project
also aims to introduce C++, C and embedded software concepts.