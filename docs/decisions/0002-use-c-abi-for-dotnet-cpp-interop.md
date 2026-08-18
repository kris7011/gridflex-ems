# ADR 0002: Use a C ABI for .NET to C++ controller interoperability

## Status

Accepted

## Context

GridFlex EMS now has independently tested components for:

- ASP.NET Core application coordination in C#
- performance-oriented control logic in C++
- hardware abstraction in C
- simulation and data-oriented functionality in Python

The C# backend defines an application boundary through `IControllerGateway`.

The existing C++ controller exposes domain concepts such as:

- `EnergyMeasurement`
- `ControlAction`
- `ControlCommand`
- `EnergyController`

The next architectural step is to allow the .NET backend to invoke the C++
controller without coupling the application layer directly to C++ implementation
details.

Several integration approaches are possible:

- direct native interoperability
- process-based IPC
- HTTP between components
- platform-specific C++/.NET bridging

The integration must preserve the existing application boundary and should
remain suitable for both Windows and Linux development.

The controller decision path is expected to be small and performance-sensitive,
so unnecessary network or process boundaries should be avoided unless they
provide a clear architectural benefit.

## Decision

The .NET backend will communicate with the C++ controller through a small,
explicit C-compatible ABI.

The C++ controller implementation will remain internally object-oriented.

A native adapter layer will expose a limited set of functions using C linkage.

Conceptually:

```text
ASP.NET Core
    |
    v
ControlDecisionService
    |
    v
IControllerGateway
    |
    v
NativeControllerGateway
    |
    v
.NET native interoperability
    |
    v
C ABI
    |
    v
C++ adapter
    |
    v
EnergyController
```

The C ABI will act as the boundary between managed and native code.

C++ classes, references, exceptions and standard-library types will not be
exposed directly across this boundary.

The exported interface should use simple interoperability-friendly values and
structures.

The .NET implementation will use source-generated P/Invoke through
`LibraryImport` where practical.

The concrete native implementation will be hidden behind
`IControllerGateway`.

The application service must therefore remain unaware of:

- native library names
- native library loading
- P/Invoke declarations
- marshalling
- C-compatible structures
- C++ implementation details

Native integration failures must be translated at the gateway boundary into
meaningful managed failures rather than leaking native implementation details
into the application layer.

## Consequences

### Positive consequences

- The C# application layer remains independent of the native transport
- The existing `IControllerGateway` boundary can be preserved
- The C++ controller can remain internally object-oriented
- The interoperability surface is explicit and intentionally small
- C++ ABI differences are kept behind a C-compatible interface
- Controller calls remain in-process
- No HTTP server is required for the controller
- No additional controller process is required
- The architecture remains suitable for incremental Windows and Linux support
- Native interoperability can be tested separately from application logic

### Negative consequences

- Native library build and deployment become part of the backend runtime setup
- Managed and native structures must be kept compatible
- Interoperability failures require careful diagnostics
- Native crashes can affect the hosting .NET process
- Library loading differs between operating systems
- Debugging across the managed/native boundary is more complex than debugging
  either component independently
- Version compatibility between the managed adapter and native library must be
  managed explicitly

## Alternatives considered

### Direct C++ ABI interoperability

The .NET backend could attempt to interact directly with exported C++ classes
or compiler-specific C++ symbols.

This was rejected because C++ ABI details vary between compilers and platforms.

The application should depend on an explicit interoperability contract rather
than compiler-specific C++ implementation details.

### HTTP between .NET and C++

The controller could run as a separate HTTP service.

This would provide strong process isolation and make the language boundary
explicit.

It was rejected for the initial implementation because it would introduce:

- another process
- another server
- serialization
- networking configuration
- service lifecycle management

for a local controller decision operation that does not currently require a
distributed architecture.

The existing `IControllerGateway` means this option can still be introduced in
the future without changing the application use case.

### Child process or IPC

The .NET backend could communicate with a dedicated controller process through
pipes, sockets or another IPC mechanism.

This would improve process isolation.

It was rejected for the initial implementation because it would add process
management, message framing and IPC lifecycle concerns before they are needed.

It remains a future option if native fault isolation becomes more important
than the simplicity of in-process calls.

### C++/CLI

A C++/CLI bridge could provide a managed wrapper around the C++ controller.

This was rejected because GridFlex aims to preserve straightforward
cross-platform development and avoid making the controller integration depend
on a Windows-oriented bridging technology.

### Reimplement the controller in C#

The controller logic could be duplicated in the backend.

This was rejected because the C++ controller already represents the
performance-oriented controller component of the project.

Duplicating the logic would create multiple sources of truth and undermine the
purpose of the language boundary.

## Follow-up work

The implementation should be introduced incrementally.

Expected future steps are:

1. Define the minimal C ABI contract
2. Implement a C++ adapter around `EnergyController`
3. Build the adapter as a native shared library
4. Add managed `LibraryImport` declarations
5. Implement `NativeControllerGateway`
6. Add native integration tests
7. Register the gateway through dependency injection
8. Add an HTTP control endpoint only after the native integration is stable
9. Add controller readiness checks when the native dependency becomes part of
   the running API
