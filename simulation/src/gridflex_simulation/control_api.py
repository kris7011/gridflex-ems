"""
HTTP client for the GridFlex control API.

The client sends simulated measurements to ``POST /api/control/decision``,
where the ASP.NET Core backend forwards them through the C ABI to the C++
controller. It uses only the standard library, so the simulation package
keeps having no runtime dependencies.
"""

import json
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from gridflex_simulation.energy_measurement import EnergyMeasurement

# (method, url, body) -> (status code, response body)
Transport = Callable[[str, str, bytes | None], tuple[int, bytes]]


@dataclass(frozen=True)
class ControlDecision:
    """
    A decision returned by the controller for one measurement.
    """

    source_step_number: int
    action: str
    requested_power_kw: float


class ControlApiError(Exception):
    """
    The API could not be reached or did not return a decision.
    """

    def __init__(
        self,
        message: str,
        *,
        status: int | None = None,
        detail: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.detail = detail


def urllib_transport(timeout_seconds: float) -> Transport:
    """
    Create a transport that performs real HTTP requests.
    """

    def send(method: str, url: str, body: bytes | None) -> tuple[int, bytes]:
        request = urllib.request.Request(
            url,
            data=body,
            method=method,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                return int(response.status), bytes(response.read())
        except urllib.error.HTTPError as error:
            return int(error.code), bytes(error.read())
        except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
            raise ControlApiError(f"Could not reach {url}: {error}") from error

    return send


def measurement_to_request(measurement: EnergyMeasurement) -> dict[str, float | int]:
    """
    Map a measurement to the JSON contract of the decision endpoint.
    """

    return {
        "stepNumber": measurement.step_number,
        "elapsedTimeHours": measurement.elapsed_time_hours,
        "intervalHours": measurement.interval_hours,
        "generatedEnergyKwh": measurement.generated_energy_kwh,
        "consumedEnergyKwh": measurement.consumed_energy_kwh,
        "netEnergyKwh": measurement.net_energy_kwh,
        "batteryStateOfChargeKwh": measurement.battery_state_of_charge_kwh,
        "gridImportEnergyKwh": measurement.grid_import_energy_kwh,
        "gridExportEnergyKwh": measurement.grid_export_energy_kwh,
        "unresolvedEnergyKwh": measurement.unresolved_energy_kwh,
    }


class ControlApiClient:
    """
    Requests control decisions from a running GridFlex backend.
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout_seconds: float = 5.0,
        transport: Transport | None = None,
    ) -> None:
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("The API URL must start with http:// or https://.")

        self.base_url = base_url.rstrip("/")
        self._transport = transport or urllib_transport(timeout_seconds)

    def decide(self, measurement: EnergyMeasurement) -> ControlDecision:
        """
        Ask the controller what to do for one measurement.
        """

        status, body = self._transport(
            "POST",
            f"{self.base_url}/api/control/decision",
            json.dumps(measurement_to_request(measurement)).encode("utf-8"),
        )

        payload = _parse_json(body)

        if status != 200:
            detail = _string_field(payload, "detail")
            title = _string_field(payload, "title") or f"HTTP {status}"

            raise ControlApiError(
                f"The control API rejected step {measurement.step_number}: "
                f"{title}" + (f" {detail}" if detail else ""),
                status=status,
                detail=detail,
            )

        try:
            decision = ControlDecision(
                source_step_number=int(payload["sourceStepNumber"]),
                action=str(payload["action"]),
                requested_power_kw=float(payload["requestedPowerKw"]),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise ControlApiError(
                "The control API returned an unexpected decision payload."
            ) from error

        if decision.source_step_number != measurement.step_number:
            raise ControlApiError(
                f"The decision is for step {decision.source_step_number}, "
                f"not step {measurement.step_number}."
            )

        return decision

    def get_status(self) -> dict[str, Any] | None:
        """
        Return the API's system status, or None if it is not available.
        """

        try:
            status, body = self._transport("GET", f"{self.base_url}/api/system/status", None)
        except ControlApiError:
            return None

        payload = _parse_json(body)

        return payload if status == 200 and payload else None

    def wait_until_ready(
        self,
        timeout_seconds: float,
        *,
        poll_interval_seconds: float = 1.0,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """
        Wait until ``/health/ready`` reports the native controller as ready.
        """

        deadline = clock() + timeout_seconds
        last_problem = "no response"

        while True:
            try:
                status, _ = self._transport("GET", f"{self.base_url}/health/ready", None)

                if status == 200:
                    return

                last_problem = f"HTTP {status}"
            except ControlApiError as error:
                last_problem = str(error)

            if clock() >= deadline:
                raise ControlApiError(
                    f"The API at {self.base_url} was not ready within "
                    f"{timeout_seconds:g} s ({last_problem})."
                )

            sleep(poll_interval_seconds)


def _parse_json(body: bytes) -> dict[str, Any]:
    try:
        value = json.loads(body.decode("utf-8")) if body else {}
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}

    return value if isinstance(value, dict) else {}


def _string_field(payload: dict[str, Any], name: str) -> str | None:
    value = payload.get(name)

    return value if isinstance(value, str) and value else None
