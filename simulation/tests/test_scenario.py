import pytest

from gridflex_simulation.scenario import (
    BatteryScenarioConfiguration,
    BuildingScenarioConfiguration,
    GridScenarioConfiguration,
    SimulationScenario,
    SimulationScenarioRunner,
    SolarScenarioConfiguration,
    create_demo_scenario,
)
from gridflex_simulation.simulation_timeline import SimulationStep


def create_test_scenario() -> SimulationScenario:
    return SimulationScenario(
        name="Test scenario",
        battery=BatteryScenarioConfiguration(
            capacity_kwh=100.0,
            initial_state_of_charge_kwh=40.0,
        ),
        solar=SolarScenarioConfiguration(
            installed_capacity_kw=120.0,
            performance_ratio=0.85,
        ),
        building=BuildingScenarioConfiguration(
            base_load_kw=30.0,
            peak_load_kw=90.0,
        ),
        grid=GridScenarioConfiguration(
            max_import_power_kw=50.0,
            max_export_power_kw=50.0,
        ),
        steps=(
            SimulationStep(
                irradiance_factor=0.75,
                activity_factor=0.60,
                interval_hours=1.0,
            ),
        ),
    )


def test_battery_configuration_creates_battery() -> None:
    configuration = BatteryScenarioConfiguration(
        capacity_kwh=100.0,
        initial_state_of_charge_kwh=40.0,
    )

    battery = configuration.create_battery()

    assert battery.capacity_kwh == pytest.approx(100.0)
    assert battery.state_of_charge_kwh == pytest.approx(40.0)


def test_solar_configuration_creates_solar_array() -> None:
    configuration = SolarScenarioConfiguration(
        installed_capacity_kw=120.0,
        performance_ratio=0.85,
    )

    solar_array = configuration.create_solar_array()

    assert solar_array.installed_capacity_kw == pytest.approx(120.0)
    assert solar_array.performance_ratio == pytest.approx(0.85)


def test_building_configuration_creates_building() -> None:
    configuration = BuildingScenarioConfiguration(
        base_load_kw=30.0,
        peak_load_kw=90.0,
    )

    building = configuration.create_building()

    assert building.base_load_kw == pytest.approx(30.0)
    assert building.peak_load_kw == pytest.approx(90.0)


def test_grid_configuration_creates_grid() -> None:
    configuration = GridScenarioConfiguration(
        max_import_power_kw=50.0,
        max_export_power_kw=40.0,
        is_available=False,
    )

    grid = configuration.create_grid()

    assert grid.max_import_power_kw == pytest.approx(50.0)
    assert grid.max_export_power_kw == pytest.approx(40.0)
    assert grid.is_available is False


def test_scenario_rejects_empty_name() -> None:
    scenario = create_test_scenario()

    with pytest.raises(
        ValueError,
        match="Scenario name cannot be empty",
    ):
        SimulationScenario(
            name="   ",
            battery=scenario.battery,
            solar=scenario.solar,
            building=scenario.building,
            grid=scenario.grid,
            steps=scenario.steps,
        )


def test_scenario_rejects_empty_steps() -> None:
    scenario = create_test_scenario()

    with pytest.raises(
        ValueError,
        match="Scenario must contain at least one simulation step",
    ):
        SimulationScenario(
            name="Empty timeline",
            battery=scenario.battery,
            solar=scenario.solar,
            building=scenario.building,
            grid=scenario.grid,
            steps=(),
        )


def test_scenario_runner_executes_configured_scenario() -> None:
    scenario = create_test_scenario()

    result = SimulationScenarioRunner.run(
        scenario=scenario,
    )

    assert result.scenario_name == "Test scenario"
    assert len(result.steps) == 1

    assert result.final_battery_state_of_charge_kwh == pytest.approx(50.5)

    assert result.total_grid_import_energy_kwh == pytest.approx(0.0)

    assert result.total_grid_export_energy_kwh == pytest.approx(0.0)

    assert result.total_unresolved_energy_kwh == pytest.approx(0.0)


def test_scenario_runner_is_reproducible() -> None:
    scenario = create_test_scenario()

    first_result = SimulationScenarioRunner.run(
        scenario=scenario,
    )

    second_result = SimulationScenarioRunner.run(
        scenario=scenario,
    )

    assert first_result.final_battery_state_of_charge_kwh == pytest.approx(
        second_result.final_battery_state_of_charge_kwh
    )

    assert first_result.steps[
        0
    ].measurement.battery_state_of_charge_kwh == pytest.approx(
        second_result.steps[0].measurement.battery_state_of_charge_kwh
    )


def test_demo_scenario_contains_expected_configuration() -> None:
    scenario = create_demo_scenario()

    assert scenario.name == "Three-step solar and load variation"
    assert scenario.battery.capacity_kwh == pytest.approx(100.0)
    assert scenario.battery.initial_state_of_charge_kwh == pytest.approx(40.0)
    assert len(scenario.steps) == 3


def test_demo_scenario_produces_expected_summary() -> None:
    result = SimulationScenarioRunner.run(
        scenario=create_demo_scenario(),
    )

    assert len(result.steps) == 3

    assert result.final_battery_state_of_charge_kwh == pytest.approx(60.0)

    assert result.total_grid_import_energy_kwh == pytest.approx(2.0)

    assert result.total_grid_export_energy_kwh == pytest.approx(0.0)

    assert result.total_unresolved_energy_kwh == pytest.approx(0.0)
