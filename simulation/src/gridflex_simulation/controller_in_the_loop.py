"""
Software-in-the-loop simulation: the Python plant model asks the real
controller what to do.

For every interval, the simulation computes solar generation and building
consumption, sends the measurement (with the battery state of charge at the
start of the interval) to the GridFlex API, and applies the returned decision
to the simulated battery. The remainder goes to the simulated grid. The C++
controller therefore decides, through HTTP, C# and the C ABI, while Python
models the physical installation.

The same scenario is also run with the Python battery-first reference
strategy, so the two can be compared.

Only simulated equipment is involved: decisions are applied to the Python
battery and grid objects, never to real hardware.
"""

import argparse
import math
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from gridflex_simulation.control_api import ControlApiClient, ControlApiError, ControlDecision
from gridflex_simulation.energy_balance import EnergyBalanceCalculator
from gridflex_simulation.energy_measurement import EnergyMeasurement
from gridflex_simulation.scenario import (
    SimulationScenario,
    SimulationScenarioResult,
    SimulationScenarioRunner,
)
from gridflex_simulation.scenario_catalogue import SCENARIOS

# Tolerance for the per-step energy conservation check.
_CONSERVATION_TOLERANCE_KWH = 1e-6


class DecisionProvider(Protocol):
    """
    Anything that decides for a measurement; normally ControlApiClient.
    """

    def decide(self, measurement: EnergyMeasurement) -> ControlDecision: ...


@dataclass(frozen=True)
class LoopStep:
    """
    One interval: what the controller decided and what the plant did.
    """

    step_number: int
    start_time_hours: float
    interval_hours: float
    generated_energy_kwh: float
    consumed_energy_kwh: float
    net_energy_kwh: float
    state_of_charge_before_kwh: float
    decision: ControlDecision
    charged_energy_kwh: float
    discharged_energy_kwh: float
    state_of_charge_after_kwh: float
    grid_import_energy_kwh: float
    grid_export_energy_kwh: float
    curtailed_energy_kwh: float
    unserved_energy_kwh: float


@dataclass(frozen=True)
class LoopResult:
    """
    All intervals of one scenario, with the controller in the loop.
    """

    scenario_name: str
    steps: tuple[LoopStep, ...]

    @property
    def final_state_of_charge_kwh(self) -> float:
        return self.steps[-1].state_of_charge_after_kwh

    @property
    def total_generated_energy_kwh(self) -> float:
        return sum(step.generated_energy_kwh for step in self.steps)

    @property
    def total_consumed_energy_kwh(self) -> float:
        return sum(step.consumed_energy_kwh for step in self.steps)

    @property
    def total_charged_energy_kwh(self) -> float:
        return sum(step.charged_energy_kwh for step in self.steps)

    @property
    def total_discharged_energy_kwh(self) -> float:
        return sum(step.discharged_energy_kwh for step in self.steps)

    @property
    def total_grid_import_energy_kwh(self) -> float:
        return sum(step.grid_import_energy_kwh for step in self.steps)

    @property
    def total_grid_export_energy_kwh(self) -> float:
        return sum(step.grid_export_energy_kwh for step in self.steps)

    @property
    def total_unresolved_energy_kwh(self) -> float:
        return sum(step.curtailed_energy_kwh + step.unserved_energy_kwh for step in self.steps)


@dataclass(frozen=True)
class ScenarioComparison:
    """
    One scenario run twice: with the C++ controller and with the Python
    battery-first reference strategy.
    """

    scenario: SimulationScenario
    controller: LoopResult
    reference: SimulationScenarioResult


class ControllerInTheLoopRunner:
    """
    Runs a scenario with an external controller deciding every interval.
    """

    @staticmethod
    def run(
        scenario: SimulationScenario,
        decision_provider: DecisionProvider,
    ) -> LoopResult:
        battery = scenario.battery.create_battery()
        solar_array = scenario.solar.create_solar_array()
        building = scenario.building.create_building()
        grid = scenario.grid.create_grid()

        steps: list[LoopStep] = []
        elapsed_time_hours = 0.0

        for step_number, simulation_step in enumerate(scenario.steps, start=1):
            interval_hours = simulation_step.interval_hours

            generated_energy_kwh = solar_array.calculate_generated_energy_kwh(
                irradiance_factor=simulation_step.irradiance_factor,
                interval_hours=interval_hours,
            )

            consumed_energy_kwh = building.calculate_consumed_energy_kwh(
                activity_factor=simulation_step.activity_factor,
                interval_hours=interval_hours,
            )

            balance = EnergyBalanceCalculator.calculate(
                generated_energy_kwh=generated_energy_kwh,
                consumed_energy_kwh=consumed_energy_kwh,
            )

            start_time_hours = elapsed_time_hours
            elapsed_time_hours += interval_hours
            state_of_charge_before_kwh = battery.state_of_charge_kwh

            # What the controller sees: this interval's generation and
            # consumption with the state of charge at its start. Nothing has
            # been dispatched yet, so grid and unresolved energy are zero.
            decision = decision_provider.decide(
                EnergyMeasurement(
                    step_number=step_number,
                    elapsed_time_hours=elapsed_time_hours,
                    interval_hours=interval_hours,
                    generated_energy_kwh=generated_energy_kwh,
                    consumed_energy_kwh=consumed_energy_kwh,
                    net_energy_kwh=balance.net_energy_kwh,
                    battery_state_of_charge_kwh=state_of_charge_before_kwh,
                    grid_import_energy_kwh=0.0,
                    grid_export_energy_kwh=0.0,
                    unresolved_energy_kwh=0.0,
                )
            )

            surplus_kwh = balance.surplus_energy_kwh
            deficit_kwh = balance.deficit_energy_kwh
            requested_energy_kwh = max(decision.requested_power_kw, 0.0) * interval_hours
            charged_kwh = 0.0
            discharged_kwh = 0.0

            # The plant applies the decision within what is physically
            # available: only surplus can be stored, only deficit is
            # supplied, and the battery itself is bounded by its capacity.
            if decision.action == "ChargeBattery":
                charged_kwh = battery.charge(min(requested_energy_kwh, surplus_kwh))
                surplus_kwh -= charged_kwh
            elif decision.action == "DischargeBattery":
                discharged_kwh = battery.discharge(min(requested_energy_kwh, deficit_kwh))
                deficit_kwh -= discharged_kwh
            elif decision.action not in ("Idle", "ImportFromGrid", "ExportToGrid"):
                raise ControlApiError(f"Unknown controller action '{decision.action}'.")

            grid_import_kwh = 0.0
            grid_export_kwh = 0.0
            curtailed_kwh = 0.0
            unserved_kwh = 0.0

            if surplus_kwh > 0:
                export = grid.export_energy(
                    requested_energy_kwh=surplus_kwh,
                    interval_hours=interval_hours,
                )
                grid_export_kwh = export.transferred_energy_kwh
                curtailed_kwh = export.remaining_energy_kwh

            if deficit_kwh > 0:
                imported = grid.import_energy(
                    requested_energy_kwh=deficit_kwh,
                    interval_hours=interval_hours,
                )
                grid_import_kwh = imported.transferred_energy_kwh
                unserved_kwh = imported.remaining_energy_kwh

            step = LoopStep(
                step_number=step_number,
                start_time_hours=start_time_hours,
                interval_hours=interval_hours,
                generated_energy_kwh=generated_energy_kwh,
                consumed_energy_kwh=consumed_energy_kwh,
                net_energy_kwh=balance.net_energy_kwh,
                state_of_charge_before_kwh=state_of_charge_before_kwh,
                decision=decision,
                charged_energy_kwh=charged_kwh,
                discharged_energy_kwh=discharged_kwh,
                state_of_charge_after_kwh=battery.state_of_charge_kwh,
                grid_import_energy_kwh=grid_import_kwh,
                grid_export_energy_kwh=grid_export_kwh,
                curtailed_energy_kwh=curtailed_kwh,
                unserved_energy_kwh=unserved_kwh,
            )

            _check_energy_conservation(step)
            steps.append(step)

        return LoopResult(scenario_name=scenario.name, steps=tuple(steps))

    @staticmethod
    def compare(
        scenario: SimulationScenario,
        decision_provider: DecisionProvider,
    ) -> ScenarioComparison:
        return ScenarioComparison(
            scenario=scenario,
            controller=ControllerInTheLoopRunner.run(scenario, decision_provider),
            reference=SimulationScenarioRunner.run(scenario),
        )


def _check_energy_conservation(step: LoopStep) -> None:
    """
    Every kWh is accounted for: sources equal sinks in each interval.
    """

    sources = (
        step.generated_energy_kwh
        + step.discharged_energy_kwh
        + step.grid_import_energy_kwh
        + step.unserved_energy_kwh
    )

    sinks = (
        step.consumed_energy_kwh
        + step.charged_energy_kwh
        + step.grid_export_energy_kwh
        + step.curtailed_energy_kwh
    )

    if not math.isclose(sources, sinks, rel_tol=0.0, abs_tol=_CONSERVATION_TOLERANCE_KWH):
        raise AssertionError(
            f"Energy is not conserved in step {step.step_number}: "
            f"sources {sources:.6f} kWh, sinks {sinks:.6f} kWh."
        )


def format_comparison(comparison: ScenarioComparison) -> str:
    """
    A plain-text table of one scenario for the console.
    """

    controller = comparison.controller
    reference = comparison.reference

    lines = [
        f"Scenario {comparison.scenario.name}: {len(controller.steps)} intervals",
        "",
        " hour   solar   load    net  C++ decision        kW   SoC before->after"
        "   import  export  unresolved",
    ]

    for step in controller.steps:
        unresolved = step.curtailed_energy_kwh + step.unserved_energy_kwh
        lines.append(
            f"{_clock(step.start_time_hours)}  {step.generated_energy_kwh:6.2f} "
            f"{step.consumed_energy_kwh:6.2f} {step.net_energy_kwh:6.2f}  "
            f"{step.decision.action:<17} {step.decision.requested_power_kw:5.2f}  "
            f"{step.state_of_charge_before_kwh:6.2f} -> {step.state_of_charge_after_kwh:5.2f}  "
            f"{step.grid_import_energy_kwh:7.2f} {step.grid_export_energy_kwh:7.2f}"
            f" {unresolved:11.2f}"
        )

    lines += [
        "",
        f"{'Totals (kWh)':<22}{'C++ controller':>16}{'Python reference':>18}",
        _total_line(
            "grid import",
            controller.total_grid_import_energy_kwh,
            reference.total_grid_import_energy_kwh,
        ),
        _total_line(
            "grid export",
            controller.total_grid_export_energy_kwh,
            reference.total_grid_export_energy_kwh,
        ),
        _total_line(
            "unresolved",
            controller.total_unresolved_energy_kwh,
            reference.total_unresolved_energy_kwh,
        ),
        _total_line(
            "final state of charge",
            controller.final_state_of_charge_kwh,
            reference.final_battery_state_of_charge_kwh,
        ),
    ]

    return "\n".join(lines)


def _total_line(label: str, controller: float, reference: float) -> str:
    return f"  {label:<20}{controller:>16.2f}{reference:>18.2f}"


def _clock(hours: float) -> str:
    whole_minutes = round(hours * 60)

    return f"{whole_minutes // 60 % 24:02d}:{whole_minutes % 60:02d}"


def parse_arguments(arguments: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="gridflex-sil",
        description=(
            "Run simulation scenarios with the GridFlex C++ controller in the loop, "
            "through the HTTP API."
        ),
    )

    parser.add_argument(
        "--api-url",
        default="http://localhost:5080",
        help="Base URL of the GridFlex API (default: %(default)s).",
    )

    parser.add_argument(
        "--scenario",
        action="append",
        choices=sorted(SCENARIOS),
        help="Scenario to run; repeat for several. Default: all scenarios.",
    )

    parser.add_argument(
        "--report-dir",
        type=Path,
        help="Write JSON results and an HTML report to this directory.",
    )

    parser.add_argument(
        "--wait-seconds",
        type=float,
        default=30.0,
        help="How long to wait for /health/ready (default: %(default)s).",
    )

    return parser.parse_args(arguments)


def main(arguments: Sequence[str] | None = None) -> int:
    options = parse_arguments(sys.argv[1:] if arguments is None else arguments)
    names = options.scenario or list(SCENARIOS)
    client = ControlApiClient(options.api_url)

    try:
        client.wait_until_ready(options.wait_seconds)

        comparisons = [
            ControllerInTheLoopRunner.compare(SCENARIOS[name](), client) for name in names
        ]
    except ControlApiError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    for comparison in comparisons:
        print(format_comparison(comparison))
        print()

    if options.report_dir is not None:
        # Imported here so the console runner does not depend on it.
        from gridflex_simulation.sil_report import write_report

        report = write_report(
            options.report_dir,
            comparisons,
            api_url=client.base_url,
            api_status=client.get_status(),
        )

        print(f"Report written to {report}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
