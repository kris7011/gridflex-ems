import json
import threading
from collections.abc import Iterator
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest

from gridflex_simulation.control_api import ControlApiError, ControlDecision
from gridflex_simulation.controller_in_the_loop import (
    ControllerInTheLoopRunner,
    LoopStep,
    format_comparison,
    main,
)
from gridflex_simulation.energy_measurement import EnergyMeasurement
from gridflex_simulation.scenario_catalogue import SCENARIOS, grid_outage, sunny_day
from tests.fake_controller import FakeController


def test_the_controller_sees_each_interval_before_dispatch() -> None:
    controller = FakeController()

    result = ControllerInTheLoopRunner.run(sunny_day(), controller)

    assert len(controller.measurements) == 24

    for step, measurement in zip(result.steps, controller.measurements, strict=True):
        assert measurement.step_number == step.step_number
        assert measurement.battery_state_of_charge_kwh == step.state_of_charge_before_kwh
        assert measurement.grid_import_energy_kwh == 0.0
        assert measurement.grid_export_energy_kwh == 0.0
        assert measurement.net_energy_kwh == pytest.approx(
            measurement.generated_energy_kwh - measurement.consumed_energy_kwh
        )


@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_every_kilowatt_hour_is_accounted_for(name: str) -> None:
    result = ControllerInTheLoopRunner.run(SCENARIOS[name](), FakeController())

    for step in result.steps:
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

        assert sources == pytest.approx(sinks, abs=1e-9)


@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_the_battery_stays_within_the_controller_window(name: str) -> None:
    scenario = SCENARIOS[name]()
    result = ControllerInTheLoopRunner.run(scenario, FakeController())

    for step in result.steps:
        if step.charged_energy_kwh > 0:
            assert step.state_of_charge_after_kwh <= 20.0 + 1e-9
            assert step.charged_energy_kwh <= 10.0 * step.interval_hours + 1e-9

        if step.discharged_energy_kwh > 0:
            assert step.state_of_charge_after_kwh >= 2.0 - 1e-9
            assert step.discharged_energy_kwh <= 8.0 * step.interval_hours + 1e-9


def test_sunny_day_charges_at_midday_and_discharges_in_the_evening() -> None:
    result = ControllerInTheLoopRunner.run(sunny_day(), FakeController())
    actions = {step.step_number - 1: step.decision.action for step in result.steps}

    assert actions[10] == "ChargeBattery"
    # Full battery at noon: the surplus is exported instead.
    assert actions[12] == "Idle"
    assert result.steps[12].grid_export_energy_kwh > 0
    assert actions[19] == "DischargeBattery"
    assert max(step.state_of_charge_after_kwh for step in result.steps) == pytest.approx(20.0)


def test_grid_outage_leaves_energy_unresolved_but_never_uses_the_grid() -> None:
    result = ControllerInTheLoopRunner.run(grid_outage(), FakeController())

    assert result.total_grid_import_energy_kwh == 0.0
    assert result.total_grid_export_energy_kwh == 0.0
    assert result.total_unresolved_energy_kwh > 0.0


def test_a_decision_cannot_store_more_than_the_surplus() -> None:
    class Greedy:
        def decide(self, measurement: EnergyMeasurement) -> ControlDecision:
            return ControlDecision(measurement.step_number, "ChargeBattery", 1_000.0)

    result = ControllerInTheLoopRunner.run(sunny_day(), Greedy())

    for step in result.steps:
        assert step.charged_energy_kwh <= max(step.net_energy_kwh, 0.0) + 1e-9


def test_an_unknown_action_stops_the_run() -> None:
    class Confused:
        def decide(self, measurement: EnergyMeasurement) -> ControlDecision:
            return ControlDecision(measurement.step_number, "OpenTheValve", 1.0)

    with pytest.raises(ControlApiError, match="OpenTheValve"):
        ControllerInTheLoopRunner.run(sunny_day(), Confused())


def test_comparison_includes_the_python_reference_run() -> None:
    comparison = ControllerInTheLoopRunner.compare(sunny_day(), FakeController())

    assert len(comparison.reference.steps) == len(comparison.controller.steps)

    # The reference may discharge to 0 kWh; the controller stops at 2 kWh.
    assert min(
        step.measurement.battery_state_of_charge_kwh for step in comparison.reference.steps
    ) < min(step.state_of_charge_after_kwh for step in comparison.controller.steps)

    text = format_comparison(comparison)
    assert "Scenario sunny-day: 24 intervals" in text
    assert "Python reference" in text


def test_conservation_check_detects_lost_energy() -> None:
    from gridflex_simulation.controller_in_the_loop import _check_energy_conservation

    step = ControllerInTheLoopRunner.run(sunny_day(), FakeController()).steps[12]
    broken: LoopStep = replace(step, grid_export_energy_kwh=step.grid_export_energy_kwh + 1.0)

    with pytest.raises(AssertionError, match="not conserved"):
        _check_energy_conservation(broken)


class _ControllerApi(BaseHTTPRequestHandler):
    """
    Serves the decision and health endpoints with the fake controller.
    """

    controller = FakeController()

    def do_GET(self) -> None:  # noqa: N802 - name required by BaseHTTPRequestHandler
        if self.path == "/health/ready":
            self._respond(200, b"Healthy")
        else:
            self._respond(404, b"")

    def do_POST(self) -> None:  # noqa: N802
        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        measurement = EnergyMeasurement(
            step_number=request["stepNumber"],
            elapsed_time_hours=request["elapsedTimeHours"],
            interval_hours=request["intervalHours"],
            generated_energy_kwh=request["generatedEnergyKwh"],
            consumed_energy_kwh=request["consumedEnergyKwh"],
            net_energy_kwh=request["netEnergyKwh"],
            battery_state_of_charge_kwh=request["batteryStateOfChargeKwh"],
            grid_import_energy_kwh=request["gridImportEnergyKwh"],
            grid_export_energy_kwh=request["gridExportEnergyKwh"],
            unresolved_energy_kwh=request["unresolvedEnergyKwh"],
        )
        decision = self.controller.decide(measurement)

        self._respond(
            200,
            json.dumps(
                {
                    "sourceStepNumber": decision.source_step_number,
                    "action": decision.action,
                    "requestedPowerKw": decision.requested_power_kw,
                }
            ).encode(),
        )

    def _respond(self, status: int, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        pass


@pytest.fixture
def controller_api() -> Iterator[str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _ControllerApi)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


def test_main_runs_scenarios_over_http_and_writes_a_report(
    controller_api: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(
        [
            "--api-url",
            controller_api,
            "--scenario",
            "sunny-day",
            "--scenario",
            "grid-outage",
            "--report-dir",
            str(tmp_path),
            "--wait-seconds",
            "5",
        ]
    )

    assert exit_code == 0
    assert "Scenario sunny-day" in capsys.readouterr().out

    result = json.loads((tmp_path / "sunny-day.json").read_text(encoding="utf-8"))
    assert len(result["controller"]["steps"]) == 24
    assert (tmp_path / "grid-outage.json").exists()
    assert "<svg" in (tmp_path / "index.html").read_text(encoding="utf-8")


def test_main_fails_when_the_api_is_not_reachable(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["--api-url", "http://127.0.0.1:9", "--wait-seconds", "0"])

    assert exit_code == 1
    assert "not ready" in capsys.readouterr().err
