import math

import pytest

from gridflex_simulation.battery import Battery
from gridflex_simulation.energy_management import (
    EnergyManagementService,
)
from gridflex_simulation.energy_measurement import (
    EnergyMeasurement,
    EnergyMeasurementFactory,
)
from gridflex_simulation.grid import GridConnection


def create_measurement(
    *,
    step_number: int = 1,
    elapsed_time_hours: float = 1.0,
    interval_hours: float = 1.0,
    generated_energy_kwh: float = 50.0,
    consumed_energy_kwh: float = 40.0,
    net_energy_kwh: float = 10.0,
    battery_state_of_charge_kwh: float = 50.0,
    grid_import_energy_kwh: float = 0.0,
    grid_export_energy_kwh: float = 0.0,
    unresolved_energy_kwh: float = 0.0,
) -> EnergyMeasurement:
    return EnergyMeasurement(
        step_number=step_number,
        elapsed_time_hours=elapsed_time_hours,
        interval_hours=interval_hours,
        generated_energy_kwh=generated_energy_kwh,
        consumed_energy_kwh=consumed_energy_kwh,
        net_energy_kwh=net_energy_kwh,
        battery_state_of_charge_kwh=(battery_state_of_charge_kwh),
        grid_import_energy_kwh=grid_import_energy_kwh,
        grid_export_energy_kwh=grid_export_energy_kwh,
        unresolved_energy_kwh=unresolved_energy_kwh,
    )


def create_grid() -> GridConnection:
    return GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=50.0,
    )


def test_factory_creates_measurement_without_grid_transfer() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=40.0,
    )

    management_result = EnergyManagementService.manage(
        battery=battery,
        grid=create_grid(),
        generated_energy_kwh=76.5,
        consumed_energy_kwh=66.0,
        interval_hours=1.0,
    )

    measurement = EnergyMeasurementFactory.create(
        step_number=1,
        elapsed_time_hours=1.0,
        interval_hours=1.0,
        management_result=management_result,
    )

    assert measurement.step_number == 1
    assert measurement.elapsed_time_hours == pytest.approx(1.0)
    assert measurement.interval_hours == pytest.approx(1.0)
    assert measurement.generated_energy_kwh == pytest.approx(76.5)
    assert measurement.consumed_energy_kwh == pytest.approx(66.0)
    assert measurement.net_energy_kwh == pytest.approx(10.5)
    assert measurement.battery_state_of_charge_kwh == pytest.approx(50.5)
    assert measurement.grid_import_energy_kwh == pytest.approx(0.0)
    assert measurement.grid_export_energy_kwh == pytest.approx(0.0)
    assert measurement.grid_net_energy_kwh == pytest.approx(0.0)
    assert measurement.unresolved_energy_kwh == pytest.approx(0.0)


def test_factory_records_grid_import() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=0.0,
    )

    management_result = EnergyManagementService.manage(
        battery=battery,
        grid=create_grid(),
        generated_energy_kwh=30.0,
        consumed_energy_kwh=60.0,
        interval_hours=1.0,
    )

    measurement = EnergyMeasurementFactory.create(
        step_number=1,
        elapsed_time_hours=1.0,
        interval_hours=1.0,
        management_result=management_result,
    )

    assert measurement.grid_import_energy_kwh == pytest.approx(30.0)
    assert measurement.grid_export_energy_kwh == pytest.approx(0.0)
    assert measurement.grid_net_energy_kwh == pytest.approx(30.0)


def test_factory_records_grid_export() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=100.0,
    )

    management_result = EnergyManagementService.manage(
        battery=battery,
        grid=create_grid(),
        generated_energy_kwh=80.0,
        consumed_energy_kwh=60.0,
        interval_hours=1.0,
    )

    measurement = EnergyMeasurementFactory.create(
        step_number=1,
        elapsed_time_hours=1.0,
        interval_hours=1.0,
        management_result=management_result,
    )

    assert measurement.grid_import_energy_kwh == pytest.approx(0.0)
    assert measurement.grid_export_energy_kwh == pytest.approx(20.0)
    assert measurement.grid_net_energy_kwh == pytest.approx(-20.0)


@pytest.mark.parametrize(
    "step_number",
    [
        0,
        -1,
    ],
)
def test_measurement_rejects_invalid_step_number(
    step_number: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="Measurement step number must be greater than zero",
    ):
        create_measurement(
            step_number=step_number,
        )


def test_measurement_rejects_non_finite_elapsed_time() -> None:
    with pytest.raises(
        ValueError,
        match="Elapsed time must be a finite number",
    ):
        create_measurement(
            elapsed_time_hours=math.inf,
        )


def test_measurement_rejects_non_positive_elapsed_time() -> None:
    with pytest.raises(
        ValueError,
        match="Elapsed time must be greater than zero",
    ):
        create_measurement(
            elapsed_time_hours=0.0,
        )


def test_measurement_rejects_non_finite_interval() -> None:
    with pytest.raises(
        ValueError,
        match="Measurement interval must be a finite number",
    ):
        create_measurement(
            interval_hours=math.nan,
        )


def test_measurement_rejects_non_positive_interval() -> None:
    with pytest.raises(
        ValueError,
        match="Measurement interval must be greater than zero",
    ):
        create_measurement(
            interval_hours=-1.0,
        )


def test_measurement_rejects_negative_energy_value() -> None:
    with pytest.raises(
        ValueError,
        match="Generated energy cannot be negative",
    ):
        create_measurement(
            generated_energy_kwh=-1.0,
        )


def test_measurement_rejects_non_finite_energy_value() -> None:
    with pytest.raises(
        ValueError,
        match="Consumed energy must be a finite number",
    ):
        create_measurement(
            consumed_energy_kwh=math.inf,
        )


def test_measurement_rejects_non_finite_net_energy() -> None:
    with pytest.raises(
        ValueError,
        match="Net energy must be a finite number",
    ):
        create_measurement(
            net_energy_kwh=math.nan,
        )


def test_measurement_rejects_simultaneous_grid_import_and_export() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "A measurement cannot contain both grid import " "and grid export energy"
        ),
    ):
        create_measurement(
            grid_import_energy_kwh=10.0,
            grid_export_energy_kwh=5.0,
        )
