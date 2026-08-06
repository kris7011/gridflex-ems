import pytest

from gridflex_simulation.battery import Battery


def test_battery_calculates_state_of_charge_percentage() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=40.0,
    )

    assert battery.state_of_charge_percentage == pytest.approx(40.0)


def test_battery_calculates_available_capacity() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=40.0,
    )

    assert battery.available_capacity_kwh == pytest.approx(60.0)


def test_charge_adds_energy_to_battery() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=40.0,
    )

    accepted_energy_kwh = battery.charge(25.0)

    assert accepted_energy_kwh == pytest.approx(25.0)
    assert battery.state_of_charge_kwh == pytest.approx(65.0)


def test_charge_does_not_exceed_battery_capacity() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=90.0,
    )

    accepted_energy_kwh = battery.charge(25.0)

    assert accepted_energy_kwh == pytest.approx(10.0)
    assert battery.state_of_charge_kwh == pytest.approx(100.0)


def test_discharge_removes_energy_from_battery() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=40.0,
    )

    delivered_energy_kwh = battery.discharge(15.0)

    assert delivered_energy_kwh == pytest.approx(15.0)
    assert battery.state_of_charge_kwh == pytest.approx(25.0)


def test_discharge_does_not_make_state_of_charge_negative() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=10.0,
    )

    delivered_energy_kwh = battery.discharge(25.0)

    assert delivered_energy_kwh == pytest.approx(10.0)
    assert battery.state_of_charge_kwh == pytest.approx(0.0)


@pytest.mark.parametrize(
    ("capacity_kwh", "state_of_charge_kwh"),
    [
        (0.0, 0.0),
        (-10.0, 0.0),
        (100.0, -1.0),
        (100.0, 101.0),
    ],
)
def test_battery_rejects_invalid_initial_state(
    capacity_kwh: float,
    state_of_charge_kwh: float,
) -> None:
    with pytest.raises(ValueError):
        Battery(
            capacity_kwh=capacity_kwh,
            state_of_charge_kwh=state_of_charge_kwh,
        )


def test_charge_rejects_negative_energy() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=40.0,
    )

    with pytest.raises(ValueError):
        battery.charge(-1.0)


def test_discharge_rejects_negative_energy() -> None:
    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=40.0,
    )

    with pytest.raises(ValueError):
        battery.discharge(-1.0)