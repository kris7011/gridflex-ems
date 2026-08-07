import math

import pytest

from gridflex_simulation.battery import Battery
from gridflex_simulation.battery_dispatch import (
    BatteryDispatchAction,
)
from gridflex_simulation.energy_balance import (
    EnergyBalanceStatus,
)
from gridflex_simulation.energy_management import (
    EnergyManagementService,
)
from gridflex_simulation.grid import (
    GridConnection,
    GridTransferDirection,
)


def test_management_uses_battery_before_grid_for_surplus() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=40.0,
    )

    grid = GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=50.0,
    )

    result = EnergyManagementService.manage(
        battery=battery,
        grid=grid,
        generated_energy_kwh=76.5,
        consumed_energy_kwh=66.0,
        interval_hours=1.0,
    )

    assert result.balance.status is EnergyBalanceStatus.SURPLUS
    assert result.battery_dispatch.action is BatteryDispatchAction.CHARGE
    assert result.battery_dispatch.transferred_energy_kwh == pytest.approx(10.5)
    assert result.grid_transfer is None
    assert result.unresolved_energy_kwh == pytest.approx(0.0)
    assert battery.state_of_charge_kwh == pytest.approx(50.5)


def test_management_exports_surplus_remaining_after_battery() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=95.0,
    )

    grid = GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=50.0,
    )

    result = EnergyManagementService.manage(
        battery=battery,
        grid=grid,
        generated_energy_kwh=76.5,
        consumed_energy_kwh=66.0,
        interval_hours=1.0,
    )

    assert result.battery_dispatch.transferred_energy_kwh == pytest.approx(5.0)

    assert result.grid_transfer is not None
    assert result.grid_transfer.direction is GridTransferDirection.EXPORT
    assert result.grid_transfer.transferred_energy_kwh == pytest.approx(5.5)
    assert result.unresolved_energy_kwh == pytest.approx(0.0)


def test_management_uses_battery_before_grid_for_deficit() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=40.0,
    )

    grid = GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=50.0,
    )

    result = EnergyManagementService.manage(
        battery=battery,
        grid=grid,
        generated_energy_kwh=40.0,
        consumed_energy_kwh=66.0,
        interval_hours=1.0,
    )

    assert result.balance.status is EnergyBalanceStatus.DEFICIT
    assert result.battery_dispatch.action is BatteryDispatchAction.DISCHARGE
    assert result.battery_dispatch.transferred_energy_kwh == pytest.approx(26.0)
    assert result.grid_transfer is None
    assert result.unresolved_energy_kwh == pytest.approx(0.0)
    assert battery.state_of_charge_kwh == pytest.approx(14.0)


def test_management_imports_deficit_remaining_after_battery() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=10.0,
    )

    grid = GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=50.0,
    )

    result = EnergyManagementService.manage(
        battery=battery,
        grid=grid,
        generated_energy_kwh=40.0,
        consumed_energy_kwh=66.0,
        interval_hours=1.0,
    )

    assert result.battery_dispatch.transferred_energy_kwh == pytest.approx(10.0)

    assert result.grid_transfer is not None
    assert result.grid_transfer.direction is GridTransferDirection.IMPORT
    assert result.grid_transfer.requested_energy_kwh == pytest.approx(16.0)
    assert result.grid_transfer.transferred_energy_kwh == pytest.approx(16.0)
    assert result.unresolved_energy_kwh == pytest.approx(0.0)


def test_management_reports_energy_remaining_after_grid_limit() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=0.0,
    )

    grid = GridConnection(
        max_import_power_kw=10.0,
        max_export_power_kw=50.0,
    )

    result = EnergyManagementService.manage(
        battery=battery,
        grid=grid,
        generated_energy_kwh=30.0,
        consumed_energy_kwh=60.0,
        interval_hours=1.0,
    )

    assert result.grid_transfer is not None
    assert result.grid_transfer.direction is GridTransferDirection.IMPORT
    assert result.grid_transfer.requested_energy_kwh == pytest.approx(30.0)
    assert result.grid_transfer.transferred_energy_kwh == pytest.approx(10.0)
    assert result.unresolved_energy_kwh == pytest.approx(20.0)


def test_management_keeps_system_idle_when_energy_is_balanced() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=40.0,
    )

    grid = GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=50.0,
    )

    result = EnergyManagementService.manage(
        battery=battery,
        grid=grid,
        generated_energy_kwh=50.0,
        consumed_energy_kwh=50.0,
        interval_hours=1.0,
    )

    assert result.balance.status is EnergyBalanceStatus.BALANCED
    assert result.battery_dispatch.action is BatteryDispatchAction.IDLE
    assert result.grid_transfer is None
    assert result.unresolved_energy_kwh == pytest.approx(0.0)
    assert battery.state_of_charge_kwh == pytest.approx(40.0)


@pytest.mark.parametrize(
    "interval_hours",
    [
        0.0,
        -1.0,
    ],
)
def test_management_rejects_non_positive_interval(
    interval_hours: float,
) -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=40.0,
    )

    grid = GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=50.0,
    )

    with pytest.raises(
        ValueError,
        match="Energy management interval must be greater than zero",
    ):
        EnergyManagementService.manage(
            battery=battery,
            grid=grid,
            generated_energy_kwh=50.0,
            consumed_energy_kwh=50.0,
            interval_hours=interval_hours,
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        math.inf,
        -math.inf,
        math.nan,
    ],
)
def test_management_rejects_non_finite_interval(
    invalid_value: float,
) -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=40.0,
    )

    grid = GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=50.0,
    )

    with pytest.raises(
        ValueError,
        match="Energy management interval must be a finite number",
    ):
        EnergyManagementService.manage(
            battery=battery,
            grid=grid,
            generated_energy_kwh=50.0,
            consumed_energy_kwh=50.0,
            interval_hours=invalid_value,
        )
