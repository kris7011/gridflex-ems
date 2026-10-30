# GridFlex EMS: project walkthrough

A developer-level tour of what exists in this repository, how the parts fit
together, and how to explain them. It documents only implemented behaviour;
planned work is labelled as such.

## 1. System overview

GridFlex EMS is a **simulated** energy management system for a house-sized
installation: solar panels, a battery, a building load and a grid connection.
A C++ controller decides every interval whether the battery should charge,
discharge or stay idle. The project demonstrates how such a system is split
into languages and layers with explicit boundaries. It controls no real
equipment.

| Status | Capability |
|---|---|
| Implemented, tested | Python plant model and scenarios; C hardware abstraction (simulated sensors/actuators); C++ controller; versioned C ABI; ASP.NET Core API with health checks and status; Linux container on GHCR; software-in-the-loop runner and HTML report; **interactive energy dashboard** |
| Implemented, checked manually | Dashboard charts, playback and keyboard controls in a browser (Edge, light/dark, 390 px) |
| Future | Azure deployment, live monitoring, alerts, persisted run history, EV charging |

## 2. Architecture and structure

```text
simulation/   Python: plant model, scenarios, SIL runner, report, dashboard
backend/      ASP.NET Core API (.NET 10) + xUnit tests
controller/   C++20 controller, C ABI (native_api.h), Catch2 tests, benchmark
hardware/     C17 hardware abstraction with simulated devices
docs/         architecture, ADRs, SIL and dashboard docs, this walkthrough
```

Runtime path of one decision:

```text
HTTP JSON ─▶ ControlDecisionEndpoints ─▶ IControlDecisionService
          ─▶ InstrumentedControllerGateway ─▶ NativeControllerGateway (LibraryImport, SafeHandle)
          ─▶ gridflex_controller_decide (C ABI) ─▶ EnergyController::decide (C++)
```

The Python simulation is a **client** of that path, not part of the backend.
`ControllerInTheLoopRunner` (`simulation/src/gridflex_simulation/controller_in_the_loop.py`)
sends each interval to `POST /api/control/decision` and applies the answer to
Python `Battery` and `GridConnection` objects.

The dashboard adds two thin layers on top of the runner:

- `dashboard.py`: `DashboardService` (list, status, run), `RecordingDecisionProvider`
  (records request, response and round-trip time), `explain_decision`
  (which limit determined a decision) and `run_to_dict` (the JSON document);
- `dashboard_server.py`: a standard-library HTTP server with three JSON
  endpoints and an allow-list of static files;
- `dashboard_static/`: HTML, CSS and an ES module that draws SVG charts.

## 3. Technologies

C# / ASP.NET Core Minimal APIs on .NET 10, C++20, C17, CMake, Python 3.12
(standard library only at runtime; pytest, Ruff and mypy in development),
plain JavaScript and SVG for the dashboard, Docker, GitHub Actions and GitHub
Container Registry.

## 4. Authentication and authorization

None. The API and the dashboard are local demonstration services. The
dashboard binds to `127.0.0.1` by default and the API is meant to run locally
or in a container on a trusted network. Defensive measures that do exist:
strict request contracts (unknown or missing JSON properties are rejected),
problem-details errors, a 1 KB body limit and allow-listed paths in the
dashboard server, and a Content-Security-Policy that blocks inline and
third-party scripts.

## 5. Persistence

No database. Scenarios are code (`scenario_catalogue.py`), controller limits
are configuration (`NativeController` options), and runs are computed on
request. `gridflex-sil --report-dir` writes JSON and HTML files; the dashboard
keeps a run only in the browser until the next run. There is therefore no
backup or restore procedure to maintain.

## 6. Core workflows

**Single decision.** `POST /api/control/decision` with a measurement returns
`{sourceStepNumber, action, requestedPowerKw}`. Inconsistent measurements
(for example a net energy that contradicts generation minus consumption) are
rejected by the C++ layer and returned as 400 problem details with the reason
(ADR 0003).

**Software-in-the-loop run.** For each of 24 intervals the runner computes
generation and consumption, asks the API, applies the decision within
physical limits, sends the remainder to the grid, and checks energy
conservation. The same scenario runs with the Python battery-first reference
for comparison.

**Dashboard run.**

1. The browser posts `{"scenario": "evening-peak"}` to `/api/runs`.
2. `DashboardService.run` reads `/api/system/status` (controller limits),
   wraps the API client in `RecordingDecisionProvider`, and calls
   `ControllerInTheLoopRunner.compare`.
3. `run_to_dict` combines every interval with its recorded request/response,
   the reference interval and `explain_decision`'s explanation.
4. The browser renders the charts once and then only moves a cursor and
   refreshes the inspector during playback.

**Decision explanation.** The controller takes the minimum of three powers
(cover the whole surplus/deficit, the power limit, reach the state-of-charge
limit). `explain_decision` recomputes them from the reported limits and names
the one that matches the returned power; a mismatch is labelled
`unexplained` rather than guessed.

## 7. Testing

| Layer | What runs | Where |
|---|---|---|
| Python | 239 pytest tests, Ruff, mypy (strict), coverage | Python Quality workflow |
| C / C++ | Catch2 and C tests via CTest, plus the C-compatibility check of `native_api.h` | C Quality and C++ Quality workflows |
| .NET | 45 xUnit tests, including integration tests against the real native library | Backend Quality workflow |
| Container | Build, smoke test, liveness/readiness, publish | Backend Container workflow |
| End to end | All scenarios through the real container with `gridflex-sil`, then every scenario through the dashboard, failing on any unexplained interval | Software in the Loop workflow |

Dashboard-specific tests are in `simulation/tests/test_dashboard.py` and
`test_dashboard_server.py` (see [dashboard.md](dashboard.md#tests)). They use
`FakeController`, which mirrors `EnergyController::decide`; the workflow then
proves the same behaviour against the real controller. Browser interaction is
not automated.

## 8. Local development and deployment

See the README sections *Running the project* and *Building the backend*, and
[dashboard.md](dashboard.md#run-it-locally) for the dashboard. Short version:

```bash
docker run --rm -p 5080:8080 ghcr.io/kris7011/gridflex-ems-backend:latest
cd simulation && python -m pip install -e ".[dev]"
gridflex-dashboard --api-url http://localhost:5080   # http://127.0.0.1:8050
```

Without Docker on Windows, build `gridflex_controller_native` with MSVC and
CMake, put `controller/package/bin` on `PATH`, and `dotnet run` the API.
Everything runs locally without paid services; deployment is a container
image on GHCR.

## 9. Backup and restore

Not applicable: the system stores no data. Reports written by `gridflex-sil`
are reproducible from the scenario code.

## 10. Design decisions

- **Multiple languages, one responsibility each** (ADR 0001).
- **C ABI between .NET and C++** rather than C++/CLI or a separate service
  (ADR 0002): portable across Windows and Linux, versioned, testable from C.
- **Error details across the ABI** (ADR 0003).
- **Dashboard served by the Python package, not a SPA calling the API
  directly.** The plant model already lives in Python; putting it in the
  browser would duplicate it in JavaScript. Trade-off: the dashboard needs
  the Python package running as well as the API.
- **No front-end framework or build step.** One page, a few hundred lines of
  JavaScript, no runtime dependencies and a strict CSP. Trade-off: no
  component model or automated UI tests; a React/Vite app would be the better
  choice if the dashboard grew into live monitoring with many views.
- **Explanations derived in Python instead of a new ABI field.** It avoids a
  C ABI version bump for display-only information. Trade-off: the explanation
  mirrors the controller's rule; if the rule changes, the explanation must
  follow, and the `unexplained` code plus the CI check make a divergence
  visible instead of silent.

## 11. Known limitations

- Simulation only; no live telemetry, alerts or stored history.
- No authentication on the API or the dashboard.
- Runs are synchronous; long scenarios would need streaming.
- The reference strategy is intentionally simple (no power limits, full
  window) and is a baseline, not an optimum.

## 12. Interview preparation: the interactive dashboard

**Non-technical.** "You choose a day, for example a sunny day or a power cut.
The program simulates the house hour by hour, and for every hour it asks the
real control software what the battery should do. You can then replay the day
and see, for each hour, what was decided and why, and how a simpler strategy
would have done it."

**Developer.** "The dashboard is a small Python HTTP server in the simulation
package. A run reuses `ControllerInTheLoopRunner`, wrapped in a recording
decision provider, so every interval goes over HTTP to ASP.NET Core and
through `LibraryImport` and the C ABI to the C++ controller. The server
returns one JSON document with the request, response, applied energy flows,
the reference strategy and an explanation per interval. The page draws SVG
charts and replays that document."

**Senior / architectural.** "I kept a single source of truth for each
concern: plant physics in Python, decisions in C++, limits in backend
configuration exposed through the status endpoint. The dashboard adds no
control logic; it records and explains. The explanation is derived, so I made
the failure mode explicit with an `unexplained` code and a CI check against
the real container, rather than an untested reason string. I chose no
framework and no new dependencies because the scope is one page."

**Questions and example answers**

1. *Why not let the browser call the ASP.NET API directly?*
   Because the plant model (solar, load, battery, grid) is in Python; the
   browser would need a second implementation of it. Here the browser only
   displays results, and the decisions still travel the production path.
2. *How do you know the explanation is correct?*
   Unit tests cover each code and the failure codes, and the Software in the
   Loop workflow runs every scenario against the real controller and fails on
   any `unexplained` interval. It recomputes the controller's three
   candidates from the limits the API reports, so a backend with other limits
   is explained with its own values.
3. *Why does the Python reference import less energy than the C++
   controller?* It has no power limits and may empty the battery to 0 kWh,
   whereas the controller keeps 2–20 kWh and caps discharge at 8 kW. The
   difference is the cost of protecting the battery, which the page states.
4. *What security measures does a local dashboard need?* It binds to
   localhost, serves only allow-listed files, limits and validates request
   bodies, returns problem details, and sends a CSP that forbids inline and
   third-party scripts; the JavaScript only inserts text with `textContent`.
5. *What would you change for live monitoring?* Persist measurements and
   decisions (time-series storage), stream updates (SSE or SignalR), add
   alerts and authentication, and probably move to a component framework
   with automated UI tests.

**Hands-on exercise.** Change `MaxDischargePowerKw` in
`backend/GridFlex.Api/appsettings.json` from 8 to 5, restart the API, and run
`evening-peak` in the dashboard (or start a second instance with the
environment variable `NativeController__MaxDischargePowerKw=5`). Predict
first, then check: more intervals show `max-discharge-power` (4 instead of
1 when this was tried), the explanation text says 5 kW, and no interval is
`unexplained`, which shows the explanation follows the reported limits rather
than hard-coded values. Then explain the surprise: total grid import stays at
48.63 kWh, because the battery still delivers the same 18 kWh between 20 and
2 kWh; the lower cap only spreads that discharge over more evening hours.

## 13. Ownership note

The dashboard was implemented with AI assistance (Claude Code) on the
owner's specification, building on the owner's existing simulation, API and
controller. Verification done for this feature: the unit and HTTP tests
above, a local run against the API with an MSVC-built controller (all four
scenarios, no unexplained interval), manual browser checks in Edge, and the
CI workflows on the pull request and on `main`.
