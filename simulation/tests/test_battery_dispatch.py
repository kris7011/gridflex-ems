import pytest

from gridflex_simulation.battery import Battery
from gridflex_simulation.battery_dispatch import (
    BatteryDispatchAction,
    BatteryDispatchService,
)
from gridflex_simulation.energy_balance import (
    EnergyBalanceCalculator,
)


def test_dispatch_charges_battery_with_surplus_energy() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=40.0,
    )

    balance = EnergyBalanceCalculator.calculate(
        generated_energy_kwh=76.5,
        consumed_energy_kwh=66.0,
    )

    result = BatteryDispatchService.dispatch(
        battery=battery,
        balance=balance,
    )

    assert result.action is BatteryDispatchAction.CHARGE
    assert result.requested_energy_kwh == pytest.approx(10.5)
    assert result.transferred_energy_kwh == pytest.approx(10.5)
    assert result.remaining_energy_kwh == pytest.approx(0.0)
    assert result.initial_state_of_charge_kwh == pytest.approx(40.0)
    assert result.final_state_of_charge_kwh == pytest.approx(50.5)
    assert result.state_of_charge_change_kwh == pytest.approx(10.5)
    assert battery.state_of_charge_kwh == pytest.approx(50.5)


def test_dispatch_limits_charging_to_available_capacity() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=95.0,
    )

    balance = EnergyBalanceCalculator.calculate(
        generated_energy_kwh=80.0,
        consumed_energy_kwh=60.0,
    )

    result = BatteryDispatchService.dispatch(
        battery=battery,
        balance=balance,
    )

    assert result.action is BatteryDispatchAction.CHARGE
    assert result.requested_energy_kwh == pytest.approx(20.0)
    assert result.transferred_energy_kwh == pytest.approx(5.0)
    assert result.remaining_energy_kwh == pytest.approx(15.0)
    assert result.final_state_of_charge_kwh == pytest.approx(100.0)
    assert battery.state_of_charge_kwh == pytest.approx(100.0)


def test_dispatch_cannot_charge_a_full_battery() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=100.0,
    )

    balance = EnergyBalanceCalculator.calculate(
        generated_energy_kwh=70.0,
        consumed_energy_kwh=50.0,
    )

    result = BatteryDispatchService.dispatch(
        battery=battery,
        balance=balance,
    )

    assert result.action is BatteryDispatchAction.CHARGE
    assert result.transferred_energy_kwh == pytest.approx(0.0)
    assert result.remaining_energy_kwh == pytest.approx(20.0)
    assert result.final_state_of_charge_kwh == pytest.approx(100.0)


def test_dispatch_discharges_battery_for_energy_deficit() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=40.0,
    )

    balance = EnergyBalanceCalculator.calculate(
        generated_energy_kwh=40.0,
        consumed_energy_kwh=66.0,
    )

    result = BatteryDispatchService.dispatch(
        battery=battery,
        balance=balance,
    )

    assert result.action is BatteryDispatchAction.DISCHARGE
    assert result.requested_energy_kwh == pytest.approx(26.0)
    assert result.transferred_energy_kwh == pytest.approx(26.0)
    assert result.remaining_energy_kwh == pytest.approx(0.0)
    assert result.initial_state_of_charge_kwh == pytest.approx(40.0)
    assert result.final_state_of_charge_kwh == pytest.approx(14.0)
    assert result.state_of_charge_change_kwh == pytest.approx(-26.0)
    assert battery.state_of_charge_kwh == pytest.approx(14.0)


def test_dispatch_limits_discharge_to_available_energy() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=10.0,
    )

    balance = EnergyBalanceCalculator.calculate(
        generated_energy_kwh=30.0,
        consumed_energy_kwh=60.0,
    )

    result = BatteryDispatchService.dispatch(
        battery=battery,
        balance=balance,
    )

    assert result.action is BatteryDispatchAction.DISCHARGE
    assert result.requested_energy_kwh == pytest.approx(30.0)
    assert result.transferred_energy_kwh == pytest.approx(10.0)
    assert result.remaining_energy_kwh == pytest.approx(20.0)
    assert result.final_state_of_charge_kwh == pytest.approx(0.0)
    assert battery.state_of_charge_kwh == pytest.approx(0.0)


def test_dispatch_cannot_discharge_an_empty_battery() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=0.0,
    )

    balance = EnergyBalanceCalculator.calculate(
        generated_energy_kwh=20.0,
        consumed_energy_kwh=50.0,
    )

    result = BatteryDispatchService.dispatch(
        battery=battery,
        balance=balance,
    )

    assert result.action is BatteryDispatchAction.DISCHARGE
    assert result.transferred_energy_kwh == pytest.approx(0.0)
    assert result.remaining_energy_kwh == pytest.approx(30.0)
    assert result.final_state_of_charge_kwh == pytest.approx(0.0)


def test_dispatch_keeps_battery_idle_when_energy_is_balanced() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=40.0,
    )

    balance = EnergyBalanceCalculator.calculate(
        generated_energy_kwh=50.0,
        consumed_energy_kwh=50.0,
    )

    result = BatteryDispatchService.dispatch(
        battery=battery,
        balance=balance,
    )

    assert result.action is BatteryDispatchAction.IDLE
    assert result.requested_energy_kwh == pytest.approx(0.0)
    assert result.transferred_energy_kwh == pytest.approx(0.0)
    assert result.remaining_energy_kwh == pytest.approx(0.0)
    assert result.initial_state_of_charge_kwh == pytest.approx(40.0)
    assert result.final_state_of_charge_kwh == pytest.approx(40.0)
    assert result.state_of_charge_change_kwh == pytest.approx(0.0)
    assert battery.state_of_charge_kwh == pytest.approx(40.0)