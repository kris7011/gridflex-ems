import math

import pytest

from gridflex_simulation.grid import (
    GridConnection,
    GridTransferDirection,
)


def test_grid_imports_requested_energy_within_limit() -> None:
    grid = GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=40.0,
    )

    result = grid.import_energy(
        requested_energy_kwh=20.0,
        interval_hours=1.0,
    )

    assert result.direction is GridTransferDirection.IMPORT
    assert result.requested_energy_kwh == pytest.approx(20.0)
    assert result.transferred_energy_kwh == pytest.approx(20.0)
    assert result.remaining_energy_kwh == pytest.approx(0.0)


def test_grid_limits_import_using_power_limit() -> None:
    grid = GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=40.0,
    )

    result = grid.import_energy(
        requested_energy_kwh=40.0,
        interval_hours=0.5,
    )

    assert result.transferred_energy_kwh == pytest.approx(25.0)
    assert result.remaining_energy_kwh == pytest.approx(15.0)


def test_grid_exports_requested_energy_within_limit() -> None:
    grid = GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=40.0,
    )

    result = grid.export_energy(
        requested_energy_kwh=30.0,
        interval_hours=1.0,
    )

    assert result.direction is GridTransferDirection.EXPORT
    assert result.requested_energy_kwh == pytest.approx(30.0)
    assert result.transferred_energy_kwh == pytest.approx(30.0)
    assert result.remaining_energy_kwh == pytest.approx(0.0)


def test_grid_limits_export_using_power_limit() -> None:
    grid = GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=20.0,
    )

    result = grid.export_energy(
        requested_energy_kwh=30.0,
        interval_hours=1.0,
    )

    assert result.transferred_energy_kwh == pytest.approx(20.0)
    assert result.remaining_energy_kwh == pytest.approx(10.0)


def test_unavailable_grid_cannot_import_energy() -> None:
    grid = GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=40.0,
        is_available=False,
    )

    result = grid.import_energy(
        requested_energy_kwh=20.0,
        interval_hours=1.0,
    )

    assert result.transferred_energy_kwh == pytest.approx(0.0)
    assert result.remaining_energy_kwh == pytest.approx(20.0)


def test_unavailable_grid_cannot_export_energy() -> None:
    grid = GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=40.0,
        is_available=False,
    )

    result = grid.export_energy(
        requested_energy_kwh=20.0,
        interval_hours=1.0,
    )

    assert result.transferred_energy_kwh == pytest.approx(0.0)
    assert result.remaining_energy_kwh == pytest.approx(20.0)


def test_grid_handles_zero_requested_energy() -> None:
    grid = GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=40.0,
    )

    result = grid.import_energy(
        requested_energy_kwh=0.0,
        interval_hours=1.0,
    )

    assert result.transferred_energy_kwh == pytest.approx(0.0)
    assert result.remaining_energy_kwh == pytest.approx(0.0)


@pytest.mark.parametrize(
    "requested_energy_kwh",
    [
        -0.1,
        -10.0,
    ],
)
def test_grid_rejects_negative_requested_energy(
    requested_energy_kwh: float,
) -> None:
    grid = GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=40.0,
    )

    with pytest.raises(
        ValueError,
        match="Requested grid energy cannot be negative",
    ):
        grid.import_energy(
            requested_energy_kwh=requested_energy_kwh,
            interval_hours=1.0,
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        math.inf,
        -math.inf,
        math.nan,
    ],
)
def test_grid_rejects_non_finite_requested_energy(
    invalid_value: float,
) -> None:
    grid = GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=40.0,
    )

    with pytest.raises(
        ValueError,
        match="Requested grid energy must be a finite number",
    ):
        grid.import_energy(
            requested_energy_kwh=invalid_value,
            interval_hours=1.0,
        )


@pytest.mark.parametrize(
    "interval_hours",
    [
        0.0,
        -1.0,
    ],
)
def test_grid_rejects_non_positive_interval(
    interval_hours: float,
) -> None:
    grid = GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=40.0,
    )

    with pytest.raises(
        ValueError,
        match="Grid interval must be greater than zero",
    ):
        grid.import_energy(
            requested_energy_kwh=10.0,
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
def test_grid_rejects_non_finite_interval(
    invalid_value: float,
) -> None:
    grid = GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=40.0,
    )

    with pytest.raises(
        ValueError,
        match="Grid interval must be a finite number",
    ):
        grid.import_energy(
            requested_energy_kwh=10.0,
            interval_hours=invalid_value,
        )


@pytest.mark.parametrize(
    "max_import_power_kw",
    [
        -0.1,
        -10.0,
    ],
)
def test_grid_rejects_negative_import_power_limit(
    max_import_power_kw: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="Maximum import power cannot be negative",
    ):
        GridConnection(
            max_import_power_kw=max_import_power_kw,
            max_export_power_kw=40.0,
        )


@pytest.mark.parametrize(
    "max_export_power_kw",
    [
        -0.1,
        -10.0,
    ],
)
def test_grid_rejects_negative_export_power_limit(
    max_export_power_kw: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="Maximum export power cannot be negative",
    ):
        GridConnection(
            max_import_power_kw=50.0,
            max_export_power_kw=max_export_power_kw,
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        math.inf,
        -math.inf,
        math.nan,
    ],
)
def test_grid_rejects_non_finite_import_power_limit(
    invalid_value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="Maximum import power must be a finite number",
    ):
        GridConnection(
            max_import_power_kw=invalid_value,
            max_export_power_kw=40.0,
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        math.inf,
        -math.inf,
        math.nan,
    ],
)
def test_grid_rejects_non_finite_export_power_limit(
    invalid_value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="Maximum export power must be a finite number",
    ):
        GridConnection(
            max_import_power_kw=50.0,
            max_export_power_kw=invalid_value,
        )
