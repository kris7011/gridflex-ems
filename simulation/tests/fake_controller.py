"""
A stand-in for the C++ controller with the backend's default limits.

It mirrors EnergyController::decide so the loop can be tested without the
backend; the CI workflow runs the same scenarios against the real API.
"""

from dataclasses import dataclass, field

from gridflex_simulation.control_api import ControlDecision
from gridflex_simulation.energy_measurement import EnergyMeasurement


@dataclass
class FakeController:
    max_charge_power_kw: float = 10.0
    max_discharge_power_kw: float = 8.0
    minimum_state_of_charge_kwh: float = 2.0
    maximum_state_of_charge_kwh: float = 20.0
    measurements: list[EnergyMeasurement] = field(default_factory=list)

    def decide(self, measurement: EnergyMeasurement) -> ControlDecision:
        self.measurements.append(measurement)

        net = measurement.net_energy_kwh
        interval = measurement.interval_hours
        soc = measurement.battery_state_of_charge_kwh

        if abs(net) <= 1e-9:
            return ControlDecision(measurement.step_number, "Idle", 0.0)

        if net > 0:
            power = min(
                net / interval,
                self.max_charge_power_kw,
                max(0.0, self.maximum_state_of_charge_kwh - soc) / interval,
            )
            action = "ChargeBattery"
        else:
            power = min(
                -net / interval,
                self.max_discharge_power_kw,
                max(0.0, soc - self.minimum_state_of_charge_kwh) / interval,
            )
            action = "DischargeBattery"

        if power <= 0:
            return ControlDecision(measurement.step_number, "Idle", 0.0)

        return ControlDecision(measurement.step_number, action, power)
