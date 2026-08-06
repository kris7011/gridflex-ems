import pytest

from gridflex_simulation.solar import SolarArray


def test_solar_array_calculates_output_power_at_full_irradiance() -> None:
    solar_array = SolarArray(
        installed_capacity_kw=100.0,
        performance_ratio=0.85,
    )

    output_power_kw = solar_array.calculate_output_power_kw(
        irradiance_factor=1.0,
    )

    assert output_power_kw == pytest.approx(85.0)


def test_solar_array_calculates_output_power_at_partial_irradiance() -> None:
    solar_array = SolarArray(
        installed_capacity_kw=100.0,
        performance_ratio=0.85,
    )

    output_power_kw = solar_array.calculate_output_power_kw(
        irradiance_factor=0.5,
    )

    assert output_power_kw == pytest.approx(42.5)


def test_solar_array_produces_no_power_without_irradiance() -> None:
    solar_array = SolarArray(
        installed_capacity_kw=100.0,
        performance_ratio=0.85,
    )

    output_power_kw = solar_array.calculate_output_power_kw(
        irradiance_factor=0.0,
    )

    assert output_power_kw == pytest.approx(0.0)


def test_solar_array_calculates_generated_energy() -> None:
    solar_array = SolarArray(
        installed_capacity_kw=100.0,
        performance_ratio=0.85,
    )

    generated_energy_kwh = solar_array.calculate_generated_energy_kwh(
        irradiance_factor=0.8,
        interval_hours=1.0,
    )

    assert generated_energy_kwh == pytest.approx(68.0)


def test_generated_energy_scales_with_interval_duration() -> None:
    solar_array = SolarArray(
        installed_capacity_kw=100.0,
        performance_ratio=0.85,
    )

    generated_energy_kwh = solar_array.calculate_generated_energy_kwh(
        irradiance_factor=1.0,
        interval_hours=2.0,
    )

    assert generated_energy_kwh == pytest.approx(170.0)


@pytest.mark.parametrize(
    "installed_capacity_kw",
    [
        0.0,
        -1.0,
    ],
)
def test_solar_array_rejects_invalid_installed_capacity(
    installed_capacity_kw: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="Installed solar capacity",
    ):
        SolarArray(
            installed_capacity_kw=installed_capacity_kw,
        )


@pytest.mark.parametrize(
    "performance_ratio",
    [
        0.0,
        -0.1,
        1.1,
    ],
)
def test_solar_array_rejects_invalid_performance_ratio(
    performance_ratio: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="Performance ratio",
    ):
        SolarArray(
            installed_capacity_kw=100.0,
            performance_ratio=performance_ratio,
        )


@pytest.mark.parametrize(
    "irradiance_factor",
    [
        -0.1,
        1.1,
    ],
)
def test_solar_array_rejects_invalid_irradiance_factor(
    irradiance_factor: float,
) -> None:
    solar_array = SolarArray(
        installed_capacity_kw=100.0,
    )

    with pytest.raises(
        ValueError,
        match="Irradiance factor",
    ):
        solar_array.calculate_output_power_kw(
            irradiance_factor=irradiance_factor,
        )


@pytest.mark.parametrize(
    "interval_hours",
    [
        0.0,
        -1.0,
    ],
)
def test_solar_array_rejects_invalid_interval(
    interval_hours: float,
) -> None:
    solar_array = SolarArray(
        installed_capacity_kw=100.0,
    )

    with pytest.raises(
        ValueError,
        match="Simulation interval",
    ):
        solar_array.calculate_generated_energy_kwh(
            irradiance_factor=0.8,
            interval_hours=interval_hours,
        )