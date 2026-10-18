# ADR 0003: Report native error details through the C ABI

## Status

Accepted

## Context

ADR 0002 established a small C ABI between the .NET backend and the C++
controller. Failures cross that boundary as numeric status codes only.

The C++ domain model already knows exactly why it rejects an input. For
example, `EnergyMeasurement` throws `std::invalid_argument` with messages such
as "Measurement interval must be greater than zero.". The adapter in
`native_api.cpp` mapped every such exception to
`GRIDFLEX_CONTROLLER_STATUS_INVALID_MEASUREMENT` and discarded the message.

As a result, the HTTP API could only answer:

```text
400 Invalid energy measurement.
detail: Native controller rejected the measurement. (Parameter 'measurement')
```

A client could not tell which of the ten measurement values was wrong. ADR 0002
already listed "interoperability failures require careful diagnostics" as a
negative consequence.

Exceptions must not cross the ABI. Status codes must stay stable, and the
existing functions and structures must not change.

## Decision

The ABI exposes the reason for the last failure through an additional
function, following the pattern of `errno`, `GetLastError` and
`sqlite3_errmsg`:

```c
size_t gridflex_controller_last_error_message(
    char *buffer,
    size_t buffer_size);
```

- `gridflex_controller_create` and `gridflex_controller_decide` clear the
  message when they start and set it when they fail.
- The state is `thread_local`, so concurrent callers never see each other's
  errors and no locking is needed.
- The caller provides the buffer. The function copies at most
  `buffer_size - 1` bytes plus a NUL terminator and returns the full length,
  so a caller can query the length with `(NULL, 0)` and retry with a larger
  buffer. No memory is allocated across the boundary, so there is no ownership
  question.
- Messages describe the violated rule and never contain measurement values.

The ABI version increases from 1 to 2. Version 1 functions and structures are
unchanged, so this is an additive change. The managed side requires version 2,
because it calls the new function, and its existing version check rejects an
older library at startup.

On the managed side, `NativeControllerMethods.ReadLastErrorMessage` reads the
message synchronously, right after the failed call, on the same operating
system thread. `NativeControllerGateway` throws a
`MeasurementRejectedException` carrying the reason, and the endpoint returns
the reason as the problem `detail`.

The same change adds a missing domain rule: net energy must equal generated
minus consumed energy, within a small floating-point tolerance. Before this
rule, the controller accepted a measurement that reported a 3 kWh surplus as a
3 kWh deficit, and discharged the battery. The Python `EnergyMeasurement`
enforces the identical rule and tolerance, so the simulation and the
controller accept exactly the same measurements.

## Consequences

### Positive

- Clients receive actionable errors, for example
  `detail: Net energy must equal generated energy minus consumed energy.`
- Native failures that reach the logs as `500` responses include the native
  reason.
- No exceptions, heap ownership or C++ types cross the boundary.
- The change is additive. Existing status codes and payload layouts are
  unchanged and covered by the layout contract tests.

### Negative

- The managed adapter and the native library must both be at version 2.
  The startup check enforces this.
- Thread-local state requires the reason to be read on the same thread as the
  failed call. This holds for the synchronous gateway. An asynchronous design
  would need an explicit error out-parameter instead.
- Error messages become part of the observable API. Tests assert them, so
  rewording a message is a visible change.

## Alternatives considered

### An error structure as an out-parameter of every function

This is explicit and has no thread-local state, but it changes every existing
signature and therefore breaks version 1 consumers. It remains the better
option if the ABI is ever redesigned.

### Additional status codes, one per rule

These are stable and machine-readable, but they couple the ABI to every
validation rule. Adding a rule would then require an ABI change.

### Duplicate the validation in C#

This would produce field-level errors without native changes. It was rejected
because it creates a second source of truth for the controller's rules, which
ADR 0002 explicitly avoids.
