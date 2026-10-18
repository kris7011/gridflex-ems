"""
Named 24-hour scenarios for demonstrating how the controller reacts.

The installation is sized like a house so that the backend's default
controller limits matter (10 kW charge, 8 kW discharge, state of charge
between 2 and 20 kWh): a 12 kW solar array, a building that draws 0.8 to
7 kW, and a 20 kWh battery.
"""

import math
from collections.abc import Callable

from gridflex_simulation.scenario import (
    BatteryScenarioConfiguration,
    BuildingScenarioConfiguration,
    GridScenarioConfiguration,
    SimulationScenario,
    SolarScenarioConfiguration,
)
from gridflex_simulation.simulation_timeline import SimulationStep

HOURS_PER_DAY = 24

# Relative building activity per hour: low at night, a morning peak and a
# larger evening peak.
_ACTIVITY_BY_HOUR: tuple[float, ...] = (
    0.05,
    0.05,
    0.05,
    0.05,
    0.05,
    0.1,
    0.4,
    0.7,
    0.5,
    0.2,
    0.2,
    0.2,
    0.25,
    0.2,
    0.2,
    0.2,
    0.3,
    0.6,
    0.9,
    1.0,
    0.8,
    0.5,
    0.3,
    0.1,
)

_SUNRISE_HOUR = 6
_SUNSET_HOUR = 19


def solar_irradiance(hour: int, peak_factor: float = 1.0) -> float:
    """
    Return a normalised irradiance for the hour that starts at ``hour``.

    The curve is a half sine between sunrise and sunset, evaluated at the
    middle of the hour and rounded so scenarios stay easy to read.
    """

    if not 0 <= hour < HOURS_PER_DAY:
        raise ValueError("Hour must be between 0 and 23.")

    if not _SUNRISE_HOUR <= hour < _SUNSET_HOUR:
        return 0.0

    daylight_hours = _SUNSET_HOUR - _SUNRISE_HOUR
    position = (hour + 0.5 - _SUNRISE_HOUR) / daylight_hours

    return round(peak_factor * math.sin(math.pi * position), 3)


def _day(peak_irradiance: float = 1.0) -> tuple[SimulationStep, ...]:
    return tuple(
        SimulationStep(
            irradiance_factor=solar_irradiance(hour, peak_irradiance),
            activity_factor=_ACTIVITY_BY_HOUR[hour],
            interval_hours=1.0,
        )
        for hour in range(HOURS_PER_DAY)
    )


_SOLAR = SolarScenarioConfiguration(
    installed_capacity_kw=12.0,
    performance_ratio=0.85,
)

_BUILDING = BuildingScenarioConfiguration(
    base_load_kw=0.8,
    peak_load_kw=7.0,
)

_GRID = GridScenarioConfiguration(
    max_import_power_kw=17.0,
    max_export_power_kw=17.0,
)


def sunny_day() -> SimulationScenario:
    """
    Midday surplus charges the battery; the evening peak discharges it.
    """

    return SimulationScenario(
        name="sunny-day",
        battery=BatteryScenarioConfiguration(
            capacity_kwh=20.0,
            initial_state_of_charge_kwh=6.0,
        ),
        solar=_SOLAR,
        building=_BUILDING,
        grid=_GRID,
        steps=_day(),
    )


def cloudy_day() -> SimulationScenario:
    """
    Little surplus to store, so most of the evening load comes from the grid.
    """

    return SimulationScenario(
        name="cloudy-day",
        battery=BatteryScenarioConfiguration(
            capacity_kwh=20.0,
            initial_state_of_charge_kwh=6.0,
        ),
        solar=_SOLAR,
        building=_BUILDING,
        grid=_GRID,
        steps=_day(peak_irradiance=0.3),
    )


def evening_peak() -> SimulationScenario:
    """
    A full battery meets an evening load above the 8 kW discharge limit.
    """

    return SimulationScenario(
        name="evening-peak",
        battery=BatteryScenarioConfiguration(
            capacity_kwh=20.0,
            initial_state_of_charge_kwh=20.0,
        ),
        solar=_SOLAR,
        building=BuildingScenarioConfiguration(
            base_load_kw=0.8,
            peak_load_kw=15.0,
        ),
        grid=_GRID,
        steps=_day(),
    )


def grid_outage() -> SimulationScenario:
    """
    The grid is unavailable all day: surplus beyond the battery is lost and
    deficits beyond the battery remain unserved.
    """

    return SimulationScenario(
        name="grid-outage",
        battery=BatteryScenarioConfiguration(
            capacity_kwh=20.0,
            initial_state_of_charge_kwh=6.0,
        ),
        solar=_SOLAR,
        building=_BUILDING,
        grid=GridScenarioConfiguration(
            max_import_power_kw=17.0,
            max_export_power_kw=17.0,
            is_available=False,
        ),
        steps=_day(),
    )


SCENARIOS: dict[str, Callable[[], SimulationScenario]] = {
    "sunny-day": sunny_day,
    "cloudy-day": cloudy_day,
    "evening-peak": evening_peak,
    "grid-outage": grid_outage,
}
