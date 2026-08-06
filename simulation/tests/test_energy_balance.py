import math

import pytest

from gridflex_simulation.energy_balance import (
    EnergyBalanceCalculator,
    EnergyBalanceStatus,
)


def test_energy_balance_calculates_surplus() -> None:
    result = EnergyBalanceCalculator.calculate(
        generated_energy_kwh=76.5,
        consumed_energy_kwh=66.0,
    )

    assert result.net_energy_kwh == pytest.approx(10.5)
    assert result.status is EnergyBalanceStatus.SURPLUS
    assert result.surplus_energy_kwh == pytest.approx(10.5)
    assert result.deficit_energy_kwh == pytest.approx(0.0)


def test_energy_balance_calculates_deficit() -> None:
    result = EnergyBalanceCalculator.calculate(
        generated_energy_kwh=40.0,
        consumed_energy_kwh=66.0,
    )

    assert result.net_energy_kwh == pytest.approx(-26.0)
    assert result.status is EnergyBalanceStatus.DEFICIT
    assert result.surplus_energy_kwh == pytest.approx(0.0)
    assert result.deficit_energy_kwh == pytest.approx(26.0)


def test_energy_balance_identifies_balanced_energy() -> None:
    result = EnergyBalanceCalculator.calculate(
        generated_energy_kwh=50.0,
        consumed_energy_kwh=50.0,
    )

    assert result.net_energy_kwh == pytest.approx(0.0)
    assert result.status is EnergyBalanceStatus.BALANCED
    assert result.surplus_energy_kwh == pytest.approx(0.0)
    assert result.deficit_energy_kwh == pytest.approx(0.0)


def test_energy_balance_handles_floating_point_rounding() -> None:
    result = EnergyBalanceCalculator.calculate(
        generated_energy_kwh=0.3,
        consumed_energy_kwh=0.1 + 0.2,
    )

    assert result.net_energy_kwh == pytest.approx(0.0)
    assert result.status is EnergyBalanceStatus.BALANCED


def test_energy_balance_preserves_input_values() -> None:
    result = EnergyBalanceCalculator.calculate(
        generated_energy_kwh=80.0,
        consumed_energy_kwh=60.0,
    )

    assert result.generated_energy_kwh == pytest.approx(80.0)
    assert result.consumed_energy_kwh == pytest.approx(60.0)


@pytest.mark.parametrize(
    "generated_energy_kwh",
    [
        -0.1,
        -10.0,
    ],
)
def test_energy_balance_rejects_negative_generation(
    generated_energy_kwh: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="Generated energy cannot be negative",
    ):
        EnergyBalanceCalculator.calculate(
            generated_energy_kwh=generated_energy_kwh,
            consumed_energy_kwh=10.0,
        )


@pytest.mark.parametrize(
    "consumed_energy_kwh",
    [
        -0.1,
        -10.0,
    ],
)
def test_energy_balance_rejects_negative_consumption(
    consumed_energy_kwh: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="Consumed energy cannot be negative",
    ):
        EnergyBalanceCalculator.calculate(
            generated_energy_kwh=10.0,
            consumed_energy_kwh=consumed_energy_kwh,
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        math.inf,
        -math.inf,
        math.nan,
    ],
)
def test_energy_balance_rejects_non_finite_generation(
    invalid_value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="Generated energy must be a finite number",
    ):
        EnergyBalanceCalculator.calculate(
            generated_energy_kwh=invalid_value,
            consumed_energy_kwh=10.0,
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        math.inf,
        -math.inf,
        math.nan,
    ],
)
def test_energy_balance_rejects_non_finite_consumption(
    invalid_value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="Consumed energy must be a finite number",
    ):
        EnergyBalanceCalculator.calculate(
            generated_energy_kwh=10.0,
            consumed_energy_kwh=invalid_value,
        )