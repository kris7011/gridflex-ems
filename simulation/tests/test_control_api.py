import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest

from gridflex_simulation.control_api import (
    ControlApiClient,
    ControlApiError,
    measurement_to_request,
)
from gridflex_simulation.energy_measurement import EnergyMeasurement


def create_measurement(step_number: int = 3) -> EnergyMeasurement:
    return EnergyMeasurement(
        step_number=step_number,
        elapsed_time_hours=3.0,
        interval_hours=1.0,
        generated_energy_kwh=6.0,
        consumed_energy_kwh=2.0,
        net_energy_kwh=4.0,
        battery_state_of_charge_kwh=10.0,
        grid_import_energy_kwh=0.0,
        grid_export_energy_kwh=0.0,
        unresolved_energy_kwh=0.0,
    )


class RecordingTransport:
    def __init__(self, status: int, payload: Any) -> None:
        self.status = status
        self.body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.requests: list[tuple[str, str, bytes | None]] = []

    def __call__(self, method: str, url: str, body: bytes | None) -> tuple[int, bytes]:
        self.requests.append((method, url, body))
        return self.status, self.body


def test_measurement_uses_every_field_of_the_api_contract() -> None:
    assert measurement_to_request(create_measurement()) == {
        "stepNumber": 3,
        "elapsedTimeHours": 3.0,
        "intervalHours": 1.0,
        "generatedEnergyKwh": 6.0,
        "consumedEnergyKwh": 2.0,
        "netEnergyKwh": 4.0,
        "batteryStateOfChargeKwh": 10.0,
        "gridImportEnergyKwh": 0.0,
        "gridExportEnergyKwh": 0.0,
        "unresolvedEnergyKwh": 0.0,
    }


def test_decide_posts_the_measurement_and_maps_the_decision() -> None:
    transport = RecordingTransport(
        200,
        {"sourceStepNumber": 3, "action": "ChargeBattery", "requestedPowerKw": 4.0},
    )

    client = ControlApiClient("http://api.test/", transport=transport)
    decision = client.decide(create_measurement())

    assert decision.action == "ChargeBattery"
    assert decision.requested_power_kw == 4.0

    method, url, body = transport.requests[0]
    assert method == "POST"
    assert url == "http://api.test/api/control/decision"
    assert body is not None
    assert json.loads(body)["batteryStateOfChargeKwh"] == 10.0


def test_decide_reports_the_problem_detail_of_a_rejection() -> None:
    transport = RecordingTransport(
        400,
        {
            "title": "Invalid energy measurement.",
            "status": 400,
            "detail": "Measurement interval must be greater than zero.",
        },
    )

    with pytest.raises(ControlApiError, match="Measurement interval") as raised:
        ControlApiClient("http://api.test", transport=transport).decide(create_measurement())

    assert raised.value.status == 400
    assert raised.value.detail == "Measurement interval must be greater than zero."


@pytest.mark.parametrize(
    "payload",
    [
        b"not json",
        {"action": "ChargeBattery"},
        {"sourceStepNumber": 99, "action": "Idle", "requestedPowerKw": 0.0},
    ],
)
def test_decide_rejects_unusable_responses(payload: Any) -> None:
    client = ControlApiClient("http://api.test", transport=RecordingTransport(200, payload))

    with pytest.raises(ControlApiError):
        client.decide(create_measurement())


def test_client_requires_an_http_url() -> None:
    with pytest.raises(ValueError, match="http"):
        ControlApiClient("ftp://api.test")


def test_wait_until_ready_polls_until_the_api_is_ready() -> None:
    statuses = iter([503, 503, 200])
    sleeps: list[float] = []

    def transport(method: str, url: str, body: bytes | None) -> tuple[int, bytes]:
        assert url.endswith("/health/ready")
        return next(statuses), b"Healthy"

    ControlApiClient("http://api.test", transport=transport).wait_until_ready(
        10.0,
        sleep=sleeps.append,
        clock=lambda: 0.0,
    )

    assert sleeps == [1.0, 1.0]


def test_wait_until_ready_gives_up_after_the_timeout() -> None:
    times = iter([0.0, 5.0, 11.0])

    def transport(method: str, url: str, body: bytes | None) -> tuple[int, bytes]:
        return 503, b"Unhealthy"

    with pytest.raises(ControlApiError, match="not ready within 10 s"):
        ControlApiClient("http://api.test", transport=transport).wait_until_ready(
            10.0,
            sleep=lambda _: None,
            clock=lambda: next(times),
        )


class _DecisionHandler(BaseHTTPRequestHandler):
    received: list[dict[str, Any]] = []

    def do_POST(self) -> None:  # noqa: N802 - name required by BaseHTTPRequestHandler
        length = int(self.headers["Content-Length"])
        request = json.loads(self.rfile.read(length))
        self.received.append({"contentType": self.headers["Content-Type"], **request})

        body = json.dumps(
            {
                "sourceStepNumber": request["stepNumber"],
                "action": "Idle",
                "requestedPowerKw": 0.0,
            }
        ).encode()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        pass


@pytest.fixture
def local_api() -> Iterator[str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _DecisionHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


def test_decide_works_over_real_http(local_api: str) -> None:
    decision = ControlApiClient(local_api).decide(create_measurement(step_number=5))

    assert decision.source_step_number == 5
    assert _DecisionHandler.received[-1]["contentType"] == "application/json"
    assert _DecisionHandler.received[-1]["stepNumber"] == 5


def test_unreachable_api_raises_a_control_api_error() -> None:
    # Port 9 (discard) is not served on the loopback interface.
    client = ControlApiClient("http://127.0.0.1:9", timeout_seconds=1.0)

    with pytest.raises(ControlApiError, match="Could not reach"):
        client.decide(create_measurement())

    assert client.get_status() is None
