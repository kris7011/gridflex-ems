"""
Local web server for the interactive energy dashboard.

``gridflex-dashboard`` serves a single page and a small JSON API:

- ``GET /api/scenarios``: the scenario catalogue;
- ``GET /api/controller``: the GridFlex API's system status and limits;
- ``POST /api/runs`` with ``{"scenario": "<name>"}``: runs the scenario with
  the C++ controller in the loop and returns every interval.

The browser never calls the GridFlex API directly; this server is the
Python plant model, so the decisions still travel through HTTP, ASP.NET
Core, the C ABI and the C++ controller. It uses only the standard library
and listens on 127.0.0.1 by default.
"""

import argparse
import json
import sys
from collections.abc import Sequence
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from typing import Any

from gridflex_simulation.control_api import ControlApiClient, ControlApiError
from gridflex_simulation.dashboard import DashboardService, UnknownScenarioError

_MAX_BODY_BYTES = 1024

# The only files the server hands out, by URL path.
_STATIC_FILES: dict[str, tuple[str, str]] = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/static/dashboard.css": ("dashboard.css", "text/css; charset=utf-8"),
    "/static/dashboard.js": ("dashboard.js", "text/javascript; charset=utf-8"),
}

_SECURITY_HEADERS: dict[str, str] = {
    "Content-Security-Policy": (
        "default-src 'none'; script-src 'self'; style-src 'self'; "
        "connect-src 'self'; img-src 'self' data:; base-uri 'none'; "
        "form-action 'none'; frame-ancestors 'none'"
    ),
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
}


def _read_static(name: str) -> bytes:
    return (
        resources.files("gridflex_simulation")
        .joinpath("dashboard_static")
        .joinpath(name)
        .read_bytes()
    )


def create_handler(service: DashboardService) -> type[BaseHTTPRequestHandler]:
    """
    A request handler class bound to one dashboard service.
    """

    class DashboardRequestHandler(BaseHTTPRequestHandler):
        server_version = "GridFlexDashboard"
        sys_version = ""

        def do_GET(self) -> None:  # noqa: N802 (http.server naming)
            path = self.path.split("?", 1)[0]

            if path in _STATIC_FILES:
                name, content_type = _STATIC_FILES[path]
                self._send(HTTPStatus.OK, _read_static(name), content_type)
            elif path == "/api/scenarios":
                self._send_json(HTTPStatus.OK, service.list_scenarios())
            elif path == "/api/controller":
                self._send_json(HTTPStatus.OK, service.controller_status())
            elif path == "/api/runs":
                self._send_problem(HTTPStatus.METHOD_NOT_ALLOWED, "Use POST to start a run.")
            else:
                self._send_problem(HTTPStatus.NOT_FOUND, f"No resource at {path}.")

        def do_POST(self) -> None:  # noqa: N802 (http.server naming)
            if self.path.split("?", 1)[0] != "/api/runs":
                self._send_problem(HTTPStatus.NOT_FOUND, f"No resource at {self.path}.")
                return

            scenario = self._read_scenario_name()

            if scenario is None:
                return

            try:
                run = service.run(scenario)
            except UnknownScenarioError:
                self._send_problem(HTTPStatus.NOT_FOUND, f"Unknown scenario '{scenario}'.")
            except ControlApiError as error:
                # The GridFlex API is the upstream: unreachable, not ready or
                # rejecting a measurement.
                self._send_problem(HTTPStatus.BAD_GATEWAY, str(error))
            else:
                self._send_json(HTTPStatus.OK, run)

        def _read_scenario_name(self) -> str | None:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                length = -1

            if length < 0 or length > _MAX_BODY_BYTES:
                self._send_problem(
                    HTTPStatus.BAD_REQUEST,
                    f"The request body must be at most {_MAX_BODY_BYTES} bytes.",
                )
                return None

            content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip()

            if content_type != "application/json":
                self._send_problem(
                    HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "The request body must be JSON."
                )
                return None

            try:
                body = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                body = None

            scenario = body.get("scenario") if isinstance(body, dict) else None

            if not isinstance(scenario, str) or not scenario:
                self._send_problem(
                    HTTPStatus.BAD_REQUEST,
                    'The body must be a JSON object such as {"scenario": "sunny-day"}.',
                )
                return None

            return scenario

        def _send_json(self, status: HTTPStatus, payload: Any) -> None:
            self._send(status, json.dumps(payload).encode("utf-8"), "application/json")

        def _send_problem(self, status: HTTPStatus, detail: str) -> None:
            problem = {"title": status.phrase, "status": int(status), "detail": detail}
            self._send(
                status,
                json.dumps(problem).encode("utf-8"),
                "application/problem+json",
            )

        def _send(self, status: HTTPStatus, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")

            for name, value in _SECURITY_HEADERS.items():
                self.send_header(name, value)

            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            sys.stderr.write(f"dashboard: {format % args}\n")

    return DashboardRequestHandler


def create_server(service: DashboardService, host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), create_handler(service))


def parse_arguments(arguments: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="gridflex-dashboard",
        description=(
            "Serve an interactive dashboard that runs simulation scenarios with the "
            "GridFlex C++ controller in the loop."
        ),
    )

    parser.add_argument(
        "--api-url",
        default="http://localhost:5080",
        help="Base URL of the GridFlex API (default: %(default)s).",
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Interface to listen on (default: %(default)s).",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8050,
        help="Port to listen on (default: %(default)s).",
    )

    return parser.parse_args(arguments)


def main(arguments: Sequence[str] | None = None) -> int:
    options = parse_arguments(sys.argv[1:] if arguments is None else arguments)
    service = DashboardService(ControlApiClient(options.api_url, timeout_seconds=10.0))
    server = create_server(service, options.host, options.port)
    host, port = server.server_address[:2]

    print(f"GridFlex dashboard on http://{host!s}:{port} (API {options.api_url})", flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
