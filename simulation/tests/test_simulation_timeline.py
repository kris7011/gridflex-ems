import pytest

from gridflex_simulation.battery import Battery
from gridflex_simulation.building import BuildingLoad
from gridflex_simulation.energy_balance import (
    EnergyBalanceStatus,
)
from gridflex_simulation.grid import (
    GridConnection,
    GridTransferDirection,
)
from gridflex_simulation.simulation_timeline import (
    SimulationStep,
    SimulationTimelineRunner,
)
from gridflex_simulation.solar import SolarArray


def create_solar_array() -> SolarArray:
    return SolarArray(
        installed_capacity_kw=120.0,
        performance_ratio=0.85,
    )


def create_building() -> BuildingLoad:
    return BuildingLoad(
        base_load_kw=30.0,
        peak_load_kw=90.0,
    )


def create_grid(
    is_available: bool = True,
) -> GridConnection:
    return GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=50.0,
        is_available=is_available,
    )


def test_timeline_runs_steps_in_order_and_preserves_battery_state() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=40.0,
    )

    steps = (
        SimulationStep(
            irradiance_factor=0.75,
            activity_factor=0.60,
            interval_hours=1.0,
        ),
        SimulationStep(
            irradiance_factor=0.25,
            activity_factor=0.80,
            interval_hours=1.0,
        ),
        SimulationStep(
            irradiance_factor=1.00,
            activity_factor=0.20,
            interval_hours=1.0,
        ),
    )

    results = SimulationTimelineRunner.run(
        steps=steps,
        battery=battery,
        solar_array=create_solar_array(),
        building=create_building(),
        grid=create_grid(),
    )

    assert len(results) == 3

    first_result = results[0]
    second_result = results[1]
    third_result = results[2]

    assert first_result.step_number == 1
    assert second_result.step_number == 2
    assert third_result.step_number == 3

    assert first_result.measurement.elapsed_time_hours == pytest.approx(1.0)
    assert second_result.measurement.elapsed_time_hours == pytest.approx(2.0)
    assert third_result.measurement.elapsed_time_hours == pytest.approx(3.0)

    assert first_result.generated_energy_kwh == pytest.approx(76.5)
    assert first_result.consumed_energy_kwh == pytest.approx(66.0)

    assert first_result.management_result.balance.status is EnergyBalanceStatus.SURPLUS
    assert first_result.final_battery_state_of_charge_kwh == pytest.approx(50.5)

    assert second_result.generated_energy_kwh == pytest.approx(25.5)
    assert second_result.consumed_energy_kwh == pytest.approx(78.0)

    assert second_result.management_result.balance.status is EnergyBalanceStatus.DEFICIT

    assert (
        second_result.management_result.battery_dispatch.initial_state_of_charge_kwh
        == pytest.approx(50.5)
    )

    assert second_result.final_battery_state_of_charge_kwh == pytest.approx(0.0)

    assert second_result.management_result.grid_transfer is not None

    assert (
        second_result.management_result.grid_transfer.direction
        is GridTransferDirection.IMPORT
    )

    assert (
        second_result.management_result.grid_transfer.transferred_energy_kwh
        == pytest.approx(2.0)
    )

    assert third_result.generated_energy_kwh == pytest.approx(102.0)
    assert third_result.consumed_energy_kwh == pytest.approx(42.0)

    assert third_result.management_result.balance.status is EnergyBalanceStatus.SURPLUS

    assert (
        third_result.management_result.battery_dispatch.initial_state_of_charge_kwh
        == pytest.approx(0.0)
    )

    assert third_result.final_battery_state_of_charge_kwh == pytest.approx(60.0)

    assert battery.state_of_charge_kwh == pytest.approx(60.0)


def test_timeline_exports_energy_when_battery_becomes_full() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=95.0,
    )

    steps = (
        SimulationStep(
            irradiance_factor=0.75,
            activity_factor=0.60,
            interval_hours=1.0,
        ),
    )

    results = SimulationTimelineRunner.run(
        steps=steps,
        battery=battery,
        solar_array=create_solar_array(),
        building=create_building(),
        grid=create_grid(),
    )

    result = results[0]

    assert result.final_battery_state_of_charge_kwh == pytest.approx(100.0)

    assert result.management_result.grid_transfer is not None

    assert (
        result.management_result.grid_transfer.direction is GridTransferDirection.EXPORT
    )

    assert (
        result.management_result.grid_transfer.transferred_energy_kwh
        == pytest.approx(5.5)
    )


def test_timeline_reports_unresolved_energy_when_grid_is_unavailable() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=0.0,
    )

    steps = (
        SimulationStep(
            irradiance_factor=0.0,
            activity_factor=0.0,
            interval_hours=1.0,
        ),
    )

    results = SimulationTimelineRunner.run(
        steps=steps,
        battery=battery,
        solar_array=create_solar_array(),
        building=create_building(),
        grid=create_grid(
            is_available=False,
        ),
    )

    result = results[0]

    assert result.management_result.balance.status is EnergyBalanceStatus.DEFICIT

    assert result.management_result.grid_transfer is not None

    assert (
        result.management_result.grid_transfer.transferred_energy_kwh
        == pytest.approx(0.0)
    )

    assert result.management_result.unresolved_energy_kwh == pytest.approx(30.0)


def test_timeline_rejects_empty_step_sequence() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=40.0,
    )

    with pytest.raises(
        ValueError,
        match="Simulation timeline must contain at least one step",
    ):
        SimulationTimelineRunner.run(
            steps=(),
            battery=battery,
            solar_array=create_solar_array(),
            building=create_building(),
            grid=create_grid(),
        )
