import pytest

from gridflex_simulation.scenario import SimulationScenarioRunner
from gridflex_simulation.scenario_catalogue import SCENARIOS, solar_irradiance


@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_scenarios_are_named_24_hour_days(name: str) -> None:
    scenario = SCENARIOS[name]()

    assert scenario.name == name
    assert len(scenario.steps) == 24
    assert all(step.interval_hours == 1.0 for step in scenario.steps)


@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_scenarios_run_with_the_python_reference_strategy(name: str) -> None:
    result = SimulationScenarioRunner.run(SCENARIOS[name]())

    assert len(result.steps) == 24


def test_irradiance_is_zero_at_night_and_peaks_around_midday() -> None:
    assert solar_irradiance(0) == 0.0
    assert solar_irradiance(5) == 0.0
    assert solar_irradiance(19) == 0.0
    assert solar_irradiance(12) == max(solar_irradiance(hour) for hour in range(24))
    assert solar_irradiance(12, peak_factor=0.3) == pytest.approx(
        0.3 * solar_irradiance(12),
        abs=1e-3,
    )


def test_irradiance_rejects_hours_outside_a_day() -> None:
    with pytest.raises(ValueError):
        solar_irradiance(24)


def test_grid_outage_has_no_grid() -> None:
    assert SCENARIOS["grid-outage"]().grid.is_available is False
