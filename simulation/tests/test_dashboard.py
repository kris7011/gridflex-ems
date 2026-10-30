from dataclasses import dataclass, field
from typing import Any

import pytest

from gridflex_simulation.control_api import ControlApiError, ControlDecision
from gridflex_simulation.controller_in_the_loop import ControllerInTheLoopRunner, LoopStep
from gridflex_simulation.dashboard import (
    ControllerLimits,
    DashboardService,
    RecordingDecisionProvider,
    UnknownScenarioError,
    explain_decision,
    run_to_dict,
)
from gridflex_simulation.energy_measurement import EnergyMeasurement
from gridflex_simulation.scenario import SimulationScenarioRunner
from gridflex_simulation.scenario_catalogue import SCENARIOS, evening_peak, sunny_day
from tests.fake_controller import FakeController

LIMITS = ControllerLimits(
    max_charge_power_kw=10.0,
    max_discharge_power_kw=8.0,
    minimum_state_of_charge_kwh=2.0,
    maximum_state_of_charge_kwh=20.0,
)

STATUS: dict[str, Any] = {
    "status": "healthy",
    "version": "1.0.0",
    "nativeController": {
        "ready": True,
        "abiVersion": 2,
        "limits": {
            "maxChargePowerKw": 10,
            "maxDischargePowerKw": 8,
            "minimumBatterySocKwh": 2,
            "maximumBatterySocKwh": 20,
        },
    },
}


@dataclass
class FakeBackend:
    """
    The API as the dashboard sees it, backed by the C++ stand-in.
    """

    base_url: str = "http://api.test"
    status: dict[str, Any] | None = field(default_factory=lambda: STATUS)
    fail_at_step: int | None = None
    controller: FakeController = field(default_factory=FakeController)

    def decide(self, measurement: EnergyMeasurement) -> ControlDecision:
        if measurement.step_number == self.fail_at_step:
            raise ControlApiError("The control API rejected step 3: Invalid energy measurement.")

        return self.controller.decide(measurement)

    def get_status(self) -> dict[str, Any] | None:
        return self.status


def _step(
    *,
    net: float,
    soc: float,
    action: str,
    power: float,
    interval: float = 1.0,
) -> LoopStep:
    generated = max(net, 0.0) + 1.0
    consumed = generated - net

    return LoopStep(
        step_number=1,
        start_time_hours=0.0,
        interval_hours=interval,
        generated_energy_kwh=generated,
        consumed_energy_kwh=consumed,
        net_energy_kwh=net,
        state_of_charge_before_kwh=soc,
        decision=ControlDecision(1, action, power),
        charged_energy_kwh=0.0,
        discharged_energy_kwh=0.0,
        state_of_charge_after_kwh=soc,
        grid_import_energy_kwh=0.0,
        grid_export_energy_kwh=0.0,
        curtailed_energy_kwh=0.0,
        unserved_energy_kwh=0.0,
    )


class _Ticker:
    """
    A clock that advances 2 ms per reading.
    """

    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        self.now += 0.002
        return self.now


@pytest.mark.parametrize(
    ("net", "soc", "action", "power", "code"),
    [
        (0.0, 10.0, "Idle", 0.0, "balanced"),
        (4.0, 6.0, "ChargeBattery", 4.0, "covers-surplus"),
        (12.0, 6.0, "ChargeBattery", 10.0, "max-charge-power"),
        (5.0, 17.0, "ChargeBattery", 3.0, "soc-maximum"),
        (5.0, 20.0, "Idle", 0.0, "battery-full"),
        (-3.0, 10.0, "DischargeBattery", 3.0, "covers-deficit"),
        (-12.35, 14.3, "DischargeBattery", 8.0, "max-discharge-power"),
        (-7.0, 4.98, "DischargeBattery", 2.98, "soc-minimum"),
        (-5.0, 2.0, "Idle", 0.0, "battery-at-minimum"),
    ],
)
def test_each_decision_is_traced_to_the_limit_that_determined_it(
    net: float, soc: float, action: str, power: float, code: str
) -> None:
    explanation = explain_decision(_step(net=net, soc=soc, action=action, power=power), LIMITS)

    assert explanation.code == code
    assert explanation.text


def test_explanations_use_the_reported_limit_values() -> None:
    explanation = explain_decision(
        _step(net=-12.35, soc=14.3, action="DischargeBattery", power=8.0), LIMITS
    )

    assert "8 kW" in explanation.text


def test_a_half_hour_interval_compares_power_not_energy() -> None:
    # 3 kWh of surplus in 0.5 h is 6 kW: under the 10 kW limit.
    explanation = explain_decision(
        _step(net=3.0, soc=6.0, action="ChargeBattery", power=6.0, interval=0.5), LIMITS
    )

    assert explanation.code == "covers-surplus"


@pytest.mark.parametrize(
    ("action", "power"),
    [
        ("ChargeBattery", 12.0),  # above the reported charge limit
        ("DischargeBattery", 4.0),  # wrong direction for a surplus
        ("Idle", 0.0),  # idle although the battery could store energy
    ],
)
def test_a_decision_that_contradicts_the_reported_limits_is_flagged(
    action: str, power: float
) -> None:
    explanation = explain_decision(_step(net=12.0, soc=6.0, action=action, power=power), LIMITS)

    assert explanation.code == "unexplained"


def test_without_reported_limits_only_balanced_intervals_are_explained() -> None:
    assert explain_decision(_step(net=0.0, soc=5.0, action="Idle", power=0.0), None).code == (
        "balanced"
    )
    assert (
        explain_decision(_step(net=4.0, soc=5.0, action="ChargeBattery", power=4.0), None).code
        == "limits-unknown"
    )


def test_controller_limits_are_read_from_the_system_status() -> None:
    assert ControllerLimits.from_status(STATUS) == LIMITS


@pytest.mark.parametrize(
    "status",
    [
        None,
        {},
        {"nativeController": None},
        {"nativeController": {"limits": "n/a"}},
        {"nativeController": {"limits": {"maxChargePowerKw": 10}}},
        {
            "nativeController": {
                "limits": {**STATUS["nativeController"]["limits"], "maxChargePowerKw": "x"}
            }
        },
    ],
)
def test_missing_or_malformed_limits_are_treated_as_unknown(status: dict[str, Any] | None) -> None:
    assert ControllerLimits.from_status(status) is None


def test_the_recorder_keeps_the_exact_request_and_the_round_trip_time() -> None:
    recorder = RecordingDecisionProvider(FakeBackend(), clock=_Ticker())

    ControllerInTheLoopRunner.run(sunny_day(), recorder)

    assert len(recorder.exchanges) == 24
    request, decision, elapsed_ms = recorder.exchanges[0]
    assert set(request) == {
        "stepNumber",
        "elapsedTimeHours",
        "intervalHours",
        "generatedEnergyKwh",
        "consumedEnergyKwh",
        "netEnergyKwh",
        "batteryStateOfChargeKwh",
        "gridImportEnergyKwh",
        "gridExportEnergyKwh",
        "unresolvedEnergyKwh",
    }
    assert request["stepNumber"] == decision.source_step_number == 1
    assert request["batteryStateOfChargeKwh"] == 6.0
    assert elapsed_ms == pytest.approx(2.0)


def test_list_scenarios_describes_the_whole_catalogue() -> None:
    scenarios = DashboardService(FakeBackend()).list_scenarios()

    assert [scenario["name"] for scenario in scenarios] == list(SCENARIOS)

    outage = next(scenario for scenario in scenarios if scenario["name"] == "grid-outage")
    assert outage["grid"]["available"] is False
    assert outage["intervals"] == 24
    assert outage["summary"].startswith("The grid is unavailable all day")


def test_controller_status_reports_an_unreachable_api() -> None:
    status = DashboardService(FakeBackend(status=None)).controller_status()

    assert status == {"apiUrl": "http://api.test", "reachable": False, "status": None}


@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_every_interval_of_a_run_is_explained_by_the_controller_limits(name: str) -> None:
    run = DashboardService(FakeBackend()).run(name)

    steps = run["controller"]["steps"]
    assert len(steps) == 24
    assert {step["explanation"]["code"] for step in steps}.isdisjoint(
        {"unexplained", "limits-unknown"}
    )


def test_a_run_carries_request_response_and_both_strategies_per_interval() -> None:
    run = DashboardService(FakeBackend(), clock=_Ticker()).run("evening-peak")

    assert run["scenario"] == "evening-peak"
    assert run["apiUrl"] == "http://api.test"
    assert run["apiVersion"] == "1.0.0"
    assert run["abiVersion"] == 2
    assert run["durationMs"] > 0
    assert run["controllerLimits"] == {
        "maxChargePowerKw": 10.0,
        "maxDischargePowerKw": 8.0,
        "minimumStateOfChargeKwh": 2.0,
        "maximumStateOfChargeKwh": 20.0,
    }
    assert run["referenceLimits"]["minimumStateOfChargeKwh"] == 0.0
    assert run["referenceLimits"]["maximumStateOfChargeKwh"] == 20.0
    assert run["referenceLimits"]["maxDischargePowerKw"] is None

    # 18:00 in evening-peak: the 8 kW discharge limit applies.
    peak = run["controller"]["steps"][18]
    assert peak["request"]["stepNumber"] == peak["response"]["sourceStepNumber"] == 19
    assert peak["response"] == {
        "sourceStepNumber": 19,
        "action": "DischargeBattery",
        "requestedPowerKw": 8.0,
    }
    assert peak["explanation"]["code"] == "max-discharge-power"
    assert peak["dischargedEnergyKwh"] == pytest.approx(8.0)
    assert peak["gridImportEnergyKwh"] == pytest.approx(4.35, abs=0.01)
    assert run["reference"]["steps"][18]["dischargedEnergyKwh"] == pytest.approx(12.35, abs=0.01)


def test_reference_totals_match_the_reference_runner() -> None:
    run = DashboardService(FakeBackend()).run("sunny-day")
    expected = SimulationScenarioRunner.run(sunny_day())
    totals = run["reference"]["totals"]

    assert totals["gridImportEnergyKwh"] == pytest.approx(expected.total_grid_import_energy_kwh)
    assert totals["gridExportEnergyKwh"] == pytest.approx(expected.total_grid_export_energy_kwh)
    assert totals["finalStateOfChargeKwh"] == pytest.approx(
        expected.final_battery_state_of_charge_kwh
    )
    assert totals["chargedEnergyKwh"] == pytest.approx(
        sum(step["chargedEnergyKwh"] for step in run["reference"]["steps"])
    )


@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_every_reference_interval_conserves_energy(name: str) -> None:
    run = DashboardService(FakeBackend()).run(name)

    for controller_step, reference_step in zip(
        run["controller"]["steps"], run["reference"]["steps"], strict=True
    ):
        sources = (
            controller_step["generatedEnergyKwh"]
            + reference_step["dischargedEnergyKwh"]
            + reference_step["gridImportEnergyKwh"]
            + reference_step["unservedEnergyKwh"]
        )
        sinks = (
            controller_step["consumedEnergyKwh"]
            + reference_step["chargedEnergyKwh"]
            + reference_step["gridExportEnergyKwh"]
            + reference_step["curtailedEnergyKwh"]
        )

        assert sources == pytest.approx(sinks, abs=1e-6)


def test_the_reference_ignores_the_controller_window() -> None:
    run = DashboardService(FakeBackend()).run("evening-peak")

    lowest_reference = min(step["stateOfChargeAfterKwh"] for step in run["reference"]["steps"])
    lowest_controller = min(
        step["stateOfChargeAfterKwh"] for step in run["controller"]["steps"]
    )

    assert lowest_reference == pytest.approx(0.0)
    assert lowest_controller == pytest.approx(2.0)


def test_a_run_without_status_still_returns_every_interval() -> None:
    run = DashboardService(FakeBackend(status=None)).run("sunny-day")

    assert run["controllerLimits"] is None
    assert run["apiVersion"] is None
    assert len(run["controller"]["steps"]) == 24


def test_unknown_scenarios_are_rejected_before_calling_the_api() -> None:
    backend = FakeBackend()

    with pytest.raises(UnknownScenarioError):
        DashboardService(backend).run("solar-eclipse")

    assert backend.controller.measurements == []


def test_an_api_failure_stops_the_run() -> None:
    with pytest.raises(ControlApiError, match="step 3"):
        DashboardService(FakeBackend(fail_at_step=3)).run("sunny-day")


def test_run_to_dict_requires_one_exchange_per_interval() -> None:
    comparison = ControllerInTheLoopRunner.compare(evening_peak(), FakeController())

    with pytest.raises(ValueError, match="exactly one"):
        run_to_dict(comparison, [], LIMITS)
