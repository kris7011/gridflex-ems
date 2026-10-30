"""
Application layer of the interactive energy dashboard.

The dashboard runs the same software-in-the-loop path as ``gridflex-sil``:
the Python plant model sends every interval to the GridFlex API, the API
forwards it through the C ABI to the C++ controller, and the decision is
applied to the simulated battery and grid. This module turns one such run
into the JSON document the browser plays back:

- every interval with the exact request sent to the API, the decision that
  came back, the round-trip time and the energy flows that resulted;
- the Python battery-first reference for the same interval;
- an explanation of which limit determined each decision, derived from the
  limits the API reports. The explanation is computed here for display; it
  never changes what the controller decided.

It has no HTTP code, so it can be tested with a stand-in controller.
"""

import inspect
import math
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Protocol

from gridflex_simulation.control_api import ControlDecision, measurement_to_request
from gridflex_simulation.controller_in_the_loop import (
    ControllerInTheLoopRunner,
    LoopStep,
    ScenarioComparison,
)
from gridflex_simulation.energy_balance import EnergyBalanceStatus
from gridflex_simulation.energy_measurement import EnergyMeasurement
from gridflex_simulation.scenario import SimulationScenario
from gridflex_simulation.scenario_catalogue import SCENARIOS
from gridflex_simulation.sil_report import loop_totals
from gridflex_simulation.simulation_timeline import SimulationStepResult

# Power values from the API are doubles; a decision "matches" a limit when it
# is within this distance of it.
_MATCH_TOLERANCE_KW = 1e-6

# Net energy at or below this is balanced, as in EnergyController::decide.
_BALANCED_TOLERANCE_KWH = 1e-9


class ControllerBackend(Protocol):
    """
    The API as the dashboard uses it; normally ControlApiClient.
    """

    base_url: str

    def decide(self, measurement: EnergyMeasurement) -> ControlDecision: ...

    def get_status(self) -> dict[str, Any] | None: ...


class UnknownScenarioError(LookupError):
    """
    The requested scenario is not in the catalogue.
    """


@dataclass(frozen=True)
class ControllerLimits:
    """
    The operating limits the C++ controller reports through the API.
    """

    max_charge_power_kw: float
    max_discharge_power_kw: float
    minimum_state_of_charge_kwh: float
    maximum_state_of_charge_kwh: float

    @staticmethod
    def from_status(status: dict[str, Any] | None) -> "ControllerLimits | None":
        controller = (status or {}).get("nativeController")
        limits = controller.get("limits") if isinstance(controller, dict) else None

        if not isinstance(limits, dict):
            return None

        try:
            return ControllerLimits(
                max_charge_power_kw=float(limits["maxChargePowerKw"]),
                max_discharge_power_kw=float(limits["maxDischargePowerKw"]),
                minimum_state_of_charge_kwh=float(limits["minimumBatterySocKwh"]),
                maximum_state_of_charge_kwh=float(limits["maximumBatterySocKwh"]),
            )
        except (KeyError, TypeError, ValueError):
            return None


@dataclass(frozen=True)
class DecisionExplanation:
    """
    Which constraint determined a decision, in words.

    ``code`` is stable for the browser and tests; ``text`` is for people.
    """

    code: str
    text: str


@dataclass(frozen=True)
class _Candidate:
    code: str
    power_kw: float
    text: str


def explain_decision(step: LoopStep, limits: ControllerLimits | None) -> DecisionExplanation:
    """
    Explain a decision by comparing it with the candidates the controller
    takes the minimum of: the power that covers the whole surplus or deficit,
    the power limit, and the power that reaches the state-of-charge limit.
    """

    action = step.decision.action
    power = step.decision.requested_power_kw
    interval = step.interval_hours
    soc = step.state_of_charge_before_kwh
    net = step.net_energy_kwh

    if abs(net) <= _BALANCED_TOLERANCE_KWH:
        return DecisionExplanation(
            "balanced",
            "Generation equals consumption, so there is nothing to store or supply.",
        )

    if limits is None:
        return DecisionExplanation(
            "limits-unknown",
            "The API did not report the controller limits, so the decision cannot be "
            "traced to a limit.",
        )

    surplus = net > 0
    candidates = (
        [
            _Candidate(
                "covers-surplus",
                net / interval,
                f"Stores the whole surplus of {net:.2f} kWh.",
            ),
            _Candidate(
                "max-charge-power",
                limits.max_charge_power_kw,
                f"Capped at the controller's maximum charge power of "
                f"{limits.max_charge_power_kw:g} kW; the rest of the surplus goes to the grid.",
            ),
            _Candidate(
                "soc-maximum",
                max(0.0, limits.maximum_state_of_charge_kwh - soc) / interval,
                f"Charges only up to the controller's maximum state of charge of "
                f"{limits.maximum_state_of_charge_kwh:g} kWh.",
            ),
        ]
        if surplus
        else [
            _Candidate(
                "covers-deficit",
                -net / interval,
                f"Supplies the whole deficit of {-net:.2f} kWh.",
            ),
            _Candidate(
                "max-discharge-power",
                limits.max_discharge_power_kw,
                f"Capped at the controller's maximum discharge power of "
                f"{limits.max_discharge_power_kw:g} kW; the rest is imported.",
            ),
            _Candidate(
                "soc-minimum",
                max(0.0, soc - limits.minimum_state_of_charge_kwh) / interval,
                f"Discharges only down to the controller's minimum state of charge of "
                f"{limits.minimum_state_of_charge_kwh:g} kWh.",
            ),
        ]
    )

    expected_action = "ChargeBattery" if surplus else "DischargeBattery"
    binding = min(candidates, key=lambda candidate: candidate.power_kw)

    if action == "Idle" and binding.power_kw <= _MATCH_TOLERANCE_KW:
        if surplus:
            return DecisionExplanation(
                "battery-full",
                f"The battery is at the controller's maximum state of charge of "
                f"{limits.maximum_state_of_charge_kwh:g} kWh, so the surplus goes to the grid.",
            )

        return DecisionExplanation(
            "battery-at-minimum",
            f"The battery is at the controller's minimum state of charge of "
            f"{limits.minimum_state_of_charge_kwh:g} kWh, so the deficit is imported.",
        )

    if action == expected_action and math.isclose(
        power, binding.power_kw, rel_tol=0.0, abs_tol=_MATCH_TOLERANCE_KW
    ):
        return DecisionExplanation(binding.code, binding.text)

    return DecisionExplanation(
        "unexplained",
        f"{action} at {power:.2f} kW does not follow from the reported limits "
        f"(expected {expected_action} at {binding.power_kw:.2f} kW).",
    )


@dataclass
class RecordingDecisionProvider:
    """
    Passes every measurement to the backend and records what was sent,
    what came back and how long the round trip took.
    """

    backend: ControllerBackend
    clock: Callable[[], float] = time.perf_counter
    exchanges: list[tuple[dict[str, float | int], ControlDecision, float]] = field(
        default_factory=list
    )

    def decide(self, measurement: EnergyMeasurement) -> ControlDecision:
        request = measurement_to_request(measurement)
        started = self.clock()
        decision = self.backend.decide(measurement)
        elapsed_ms = (self.clock() - started) * 1000.0

        self.exchanges.append((request, decision, elapsed_ms))

        return decision


def describe_scenario(name: str, scenario: SimulationScenario, summary: str) -> dict[str, Any]:
    """
    What the browser shows before a scenario has run.
    """

    return {
        "name": name,
        "summary": summary,
        "intervals": len(scenario.steps),
        "intervalHours": scenario.steps[0].interval_hours,
        "battery": {
            "capacityKwh": scenario.battery.capacity_kwh,
            "initialStateOfChargeKwh": scenario.battery.initial_state_of_charge_kwh,
        },
        "solar": {"installedCapacityKw": scenario.solar.installed_capacity_kw},
        "building": {
            "baseLoadKw": scenario.building.base_load_kw,
            "peakLoadKw": scenario.building.peak_load_kw,
        },
        "grid": {
            "available": scenario.grid.is_available,
            "maxImportPowerKw": scenario.grid.max_import_power_kw,
            "maxExportPowerKw": scenario.grid.max_export_power_kw,
        },
    }


def reference_step_to_dict(step: SimulationStepResult) -> dict[str, Any]:
    """
    One interval of the Python battery-first reference strategy.
    """

    result = step.management_result
    dispatch = result.battery_dispatch
    surplus = result.balance.status is EnergyBalanceStatus.SURPLUS
    charged = dispatch.transferred_energy_kwh if surplus else 0.0
    discharged = 0.0 if surplus else dispatch.transferred_energy_kwh
    unresolved = result.unresolved_energy_kwh

    return {
        "stepNumber": step.step_number,
        "stateOfChargeBeforeKwh": dispatch.initial_state_of_charge_kwh,
        "stateOfChargeAfterKwh": step.measurement.battery_state_of_charge_kwh,
        "chargedEnergyKwh": charged,
        "dischargedEnergyKwh": discharged,
        "gridImportEnergyKwh": step.measurement.grid_import_energy_kwh,
        "gridExportEnergyKwh": step.measurement.grid_export_energy_kwh,
        "curtailedEnergyKwh": unresolved if surplus else 0.0,
        "unservedEnergyKwh": 0.0 if surplus else unresolved,
    }


def run_to_dict(
    comparison: ScenarioComparison,
    exchanges: list[tuple[dict[str, float | int], ControlDecision, float]],
    limits: ControllerLimits | None,
) -> dict[str, Any]:
    """
    The document the browser plays back for one run.
    """

    controller = comparison.controller
    reference = comparison.reference

    if len(exchanges) != len(controller.steps):
        raise ValueError("Every interval must have exactly one recorded API exchange.")

    reference_steps = [reference_step_to_dict(step) for step in reference.steps]
    steps = []

    for step, (request, decision, elapsed_ms) in zip(controller.steps, exchanges, strict=True):
        explanation = explain_decision(step, limits)
        steps.append(
            {
                "stepNumber": step.step_number,
                "startTimeHours": step.start_time_hours,
                "intervalHours": step.interval_hours,
                "generatedEnergyKwh": step.generated_energy_kwh,
                "consumedEnergyKwh": step.consumed_energy_kwh,
                "netEnergyKwh": step.net_energy_kwh,
                "stateOfChargeBeforeKwh": step.state_of_charge_before_kwh,
                "stateOfChargeAfterKwh": step.state_of_charge_after_kwh,
                "chargedEnergyKwh": step.charged_energy_kwh,
                "dischargedEnergyKwh": step.discharged_energy_kwh,
                "gridImportEnergyKwh": step.grid_import_energy_kwh,
                "gridExportEnergyKwh": step.grid_export_energy_kwh,
                "curtailedEnergyKwh": step.curtailed_energy_kwh,
                "unservedEnergyKwh": step.unserved_energy_kwh,
                "request": request,
                "response": {
                    "sourceStepNumber": decision.source_step_number,
                    "action": decision.action,
                    "requestedPowerKw": decision.requested_power_kw,
                },
                "roundTripMs": elapsed_ms,
                "explanation": {"code": explanation.code, "text": explanation.text},
            }
        )

    return {
        "scenario": comparison.scenario.name,
        "controllerLimits": None
        if limits is None
        else {
            "maxChargePowerKw": limits.max_charge_power_kw,
            "maxDischargePowerKw": limits.max_discharge_power_kw,
            "minimumStateOfChargeKwh": limits.minimum_state_of_charge_kwh,
            "maximumStateOfChargeKwh": limits.maximum_state_of_charge_kwh,
        },
        "referenceLimits": {
            "maxChargePowerKw": None,
            "maxDischargePowerKw": None,
            "minimumStateOfChargeKwh": 0.0,
            "maximumStateOfChargeKwh": comparison.scenario.battery.capacity_kwh,
        },
        "controller": {"totals": loop_totals(controller), "steps": steps},
        "reference": {
            "totals": {
                "chargedEnergyKwh": sum(step["chargedEnergyKwh"] for step in reference_steps),
                "dischargedEnergyKwh": sum(
                    step["dischargedEnergyKwh"] for step in reference_steps
                ),
                "gridImportEnergyKwh": reference.total_grid_import_energy_kwh,
                "gridExportEnergyKwh": reference.total_grid_export_energy_kwh,
                "unresolvedEnergyKwh": reference.total_unresolved_energy_kwh,
                "finalStateOfChargeKwh": reference.final_battery_state_of_charge_kwh,
            },
            "steps": reference_steps,
        },
    }


class DashboardService:
    """
    Lists scenarios, reports the controller status and runs scenarios with
    the controller in the loop.
    """

    def __init__(
        self,
        backend: ControllerBackend,
        scenarios: dict[str, Callable[[], SimulationScenario]] | None = None,
        clock: Callable[[], float] = time.perf_counter,
    ) -> None:
        self._backend = backend
        self._scenarios = SCENARIOS if scenarios is None else scenarios
        self._clock = clock

    def list_scenarios(self) -> list[dict[str, Any]]:
        return [
            describe_scenario(name, factory(), _summary(factory))
            for name, factory in self._scenarios.items()
        ]

    def controller_status(self) -> dict[str, Any]:
        status = self._backend.get_status()

        return {
            "apiUrl": self._backend.base_url,
            "reachable": status is not None,
            "status": status,
        }

    def run(self, name: str) -> dict[str, Any]:
        """
        Run one scenario against the API; ControlApiError propagates when the
        API cannot be reached or rejects a measurement.
        """

        factory = self._scenarios.get(name)

        if factory is None:
            raise UnknownScenarioError(name)

        status = self._backend.get_status()
        recorder = RecordingDecisionProvider(self._backend, clock=self._clock)
        started = self._clock()
        comparison = ControllerInTheLoopRunner.compare(factory(), recorder)
        elapsed_ms = (self._clock() - started) * 1000.0

        run = run_to_dict(comparison, recorder.exchanges, ControllerLimits.from_status(status))
        run["apiUrl"] = self._backend.base_url
        run["apiVersion"] = (status or {}).get("version")
        run["abiVersion"] = ((status or {}).get("nativeController") or {}).get("abiVersion")
        run["durationMs"] = elapsed_ms

        return run


def _summary(factory: Callable[[], SimulationScenario]) -> str:
    return inspect.cleandoc(factory.__doc__ or "").replace("\n", " ")
