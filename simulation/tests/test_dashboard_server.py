import json
import re
import threading
import urllib.error
import urllib.request
from collections.abc import Iterator
from importlib import resources
from typing import Any

import pytest

from gridflex_simulation.dashboard import DashboardService
from gridflex_simulation.dashboard_server import create_server, parse_arguments
from tests.test_dashboard import FakeBackend


@pytest.fixture
def backend() -> FakeBackend:
    return FakeBackend()


@pytest.fixture
def base_url(backend: FakeBackend) -> Iterator[str]:
    server = create_server(DashboardService(backend), "127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


def _request(
    url: str,
    *,
    method: str = "GET",
    body: bytes | None = None,
    content_type: str | None = "application/json",
) -> tuple[int, dict[str, str], bytes]:
    headers = {"Content-Type": content_type} if content_type else {}
    request = urllib.request.Request(url, data=body, method=method, headers=headers)

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as error:
        return error.code, dict(error.headers), error.read()


def _json(body: bytes) -> Any:
    return json.loads(body.decode("utf-8"))


def test_the_page_is_served_with_a_strict_content_security_policy(base_url: str) -> None:
    status, headers, body = _request(f"{base_url}/")

    assert status == 200
    assert headers["Content-Type"] == "text/html; charset=utf-8"
    assert "default-src 'none'" in headers["Content-Security-Policy"]
    assert "script-src 'self'" in headers["Content-Security-Policy"]
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert b"GridFlex Energy Dashboard" in body


@pytest.mark.parametrize(
    ("path", "content_type"),
    [
        ("/static/dashboard.js", "text/javascript; charset=utf-8"),
        ("/static/dashboard.css", "text/css; charset=utf-8"),
    ],
)
def test_static_assets_are_served_with_their_types(
    base_url: str, path: str, content_type: str
) -> None:
    status, headers, body = _request(f"{base_url}{path}")

    assert status == 200
    assert headers["Content-Type"] == content_type
    assert body


@pytest.mark.parametrize(
    "path",
    ["/static/../dashboard.py", "/static/missing.js", "/dashboard_server.py", "/api/nothing"],
)
def test_only_known_paths_are_served(base_url: str, path: str) -> None:
    status, headers, body = _request(f"{base_url}{path}")

    assert status == 404
    assert headers["Content-Type"] == "application/problem+json"
    assert _json(body)["status"] == 404


def test_scenarios_and_controller_status_are_available_as_json(base_url: str) -> None:
    status, _, body = _request(f"{base_url}/api/scenarios")
    assert status == 200
    assert [scenario["name"] for scenario in _json(body)] == [
        "sunny-day",
        "cloudy-day",
        "evening-peak",
        "grid-outage",
    ]

    status, _, body = _request(f"{base_url}/api/controller")
    assert status == 200
    assert _json(body)["reachable"] is True
    assert _json(body)["status"]["nativeController"]["abiVersion"] == 2


def test_a_run_goes_through_the_controller_for_every_interval(
    base_url: str, backend: FakeBackend
) -> None:
    status, headers, body = _request(
        f"{base_url}/api/runs", method="POST", body=b'{"scenario": "grid-outage"}'
    )

    assert status == 200
    assert headers["Cache-Control"] == "no-store"
    run = _json(body)
    assert run["scenario"] == "grid-outage"
    assert len(run["controller"]["steps"]) == 24
    assert len(backend.controller.measurements) == 24
    assert run["controller"]["totals"]["gridImportEnergyKwh"] == 0.0


def test_get_on_runs_is_not_allowed(base_url: str) -> None:
    status, _, body = _request(f"{base_url}/api/runs")

    assert status == 405
    assert "POST" in _json(body)["detail"]


@pytest.mark.parametrize(
    ("body", "content_type", "expected_status"),
    [
        (b"not json", "application/json", 400),
        (b"[]", "application/json", 400),
        (b'{"scenario": 7}', "application/json", 400),
        (b'{"scenario": ""}', "application/json", 400),
        (b'{"scenario": "sunny-day"}', "text/plain", 415),
        (b'{"scenario": "sunny-day"}', None, 415),
        (b'{"scenario": "' + b"x" * 2000 + b'"}', "application/json", 400),
    ],
)
def test_invalid_run_requests_get_problem_details(
    base_url: str,
    backend: FakeBackend,
    body: bytes,
    content_type: str | None,
    expected_status: int,
) -> None:
    status, headers, response = _request(
        f"{base_url}/api/runs", method="POST", body=body, content_type=content_type
    )

    assert status == expected_status
    assert headers["Content-Type"] == "application/problem+json"
    assert _json(response)["detail"]
    assert backend.controller.measurements == []


def test_an_unknown_scenario_is_not_found(base_url: str) -> None:
    status, _, body = _request(
        f"{base_url}/api/runs", method="POST", body=b'{"scenario": "solar-eclipse"}'
    )

    assert status == 404
    assert "solar-eclipse" in _json(body)["detail"]


def test_an_api_failure_is_reported_as_a_bad_gateway(base_url: str, backend: FakeBackend) -> None:
    backend.fail_at_step = 3

    status, _, body = _request(
        f"{base_url}/api/runs", method="POST", body=b'{"scenario": "sunny-day"}'
    )

    assert status == 502
    assert "step 3" in _json(body)["detail"]


def test_the_server_listens_on_localhost_by_default() -> None:
    options = parse_arguments([])

    assert options.host == "127.0.0.1"
    assert options.port == 8050
    assert options.api_url == "http://localhost:5080"


def _static(name: str) -> str:
    return (
        resources.files("gridflex_simulation")
        .joinpath("dashboard_static")
        .joinpath(name)
        .read_text(encoding="utf-8")
    )


def test_the_page_loads_nothing_from_other_origins() -> None:
    page = _static("index.html")

    assert not re.search(r'(src|href)="(https?:)?//', page)
    assert "<script>" not in page  # no inline scripts: the CSP would block them


def test_the_script_never_parses_server_text_as_html() -> None:
    script = _static("dashboard.js")

    assert "innerHTML" not in script
    assert "insertAdjacentHTML" not in script
    assert "eval(" not in script
