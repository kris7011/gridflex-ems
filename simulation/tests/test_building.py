import pytest

from gridflex_simulation.building import BuildingLoad


def test_building_uses_base_load_when_activity_is_zero() -> None:
    building = BuildingLoad(
        base_load_kw=30.0,
        peak_load_kw=90.0,
    )

    power_demand_kw = building.calculate_power_demand_kw(
        activity_factor=0.0,
    )

    assert power_demand_kw == pytest.approx(30.0)


def test_building_uses_peak_load_when_activity_is_full() -> None:
    building = BuildingLoad(
        base_load_kw=30.0,
        peak_load_kw=90.0,
    )

    power_demand_kw = building.calculate_power_demand_kw(
        activity_factor=1.0,
    )

    assert power_demand_kw == pytest.approx(90.0)


def test_building_calculates_partial_power_demand() -> None:
    building = BuildingLoad(
        base_load_kw=30.0,
        peak_load_kw=90.0,
    )

    power_demand_kw = building.calculate_power_demand_kw(
        activity_factor=0.5,
    )

    assert power_demand_kw == pytest.approx(60.0)


def test_building_calculates_consumed_energy() -> None:
    building = BuildingLoad(
        base_load_kw=30.0,
        peak_load_kw=90.0,
    )

    consumed_energy_kwh = building.calculate_consumed_energy_kwh(
        activity_factor=0.6,
        interval_hours=1.0,
    )

    assert consumed_energy_kwh == pytest.approx(66.0)


def test_consumed_energy_scales_with_interval_duration() -> None:
    building = BuildingLoad(
        base_load_kw=30.0,
        peak_load_kw=90.0,
    )

    consumed_energy_kwh = building.calculate_consumed_energy_kwh(
        activity_factor=0.5,
        interval_hours=2.0,
    )

    assert consumed_energy_kwh == pytest.approx(120.0)


def test_building_allows_zero_base_load() -> None:
    building = BuildingLoad(
        base_load_kw=0.0,
        peak_load_kw=100.0,
    )

    power_demand_kw = building.calculate_power_demand_kw(
        activity_factor=0.0,
    )

    assert power_demand_kw == pytest.approx(0.0)


def test_building_rejects_negative_base_load() -> None:
    with pytest.raises(
        ValueError,
        match="base load",
    ):
        BuildingLoad(
            base_load_kw=-1.0,
            peak_load_kw=90.0,
        )


@pytest.mark.parametrize(
    "peak_load_kw",
    [
        0.0,
        -1.0,
    ],
)
def test_building_rejects_non_positive_peak_load(
    peak_load_kw: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="peak load",
    ):
        BuildingLoad(
            base_load_kw=0.0,
            peak_load_kw=peak_load_kw,
        )


def test_building_rejects_peak_load_lower_than_base_load() -> None:
    with pytest.raises(
        ValueError,
        match="lower than base load",
    ):
        BuildingLoad(
            base_load_kw=100.0,
            peak_load_kw=90.0,
        )


@pytest.mark.parametrize(
    "activity_factor",
    [
        -0.1,
        1.1,
    ],
)
def test_building_rejects_invalid_activity_factor(
    activity_factor: float,
) -> None:
    building = BuildingLoad(
        base_load_kw=30.0,
        peak_load_kw=90.0,
    )

    with pytest.raises(
        ValueError,
        match="Activity factor",
    ):
        building.calculate_power_demand_kw(
            activity_factor=activity_factor,
        )


@pytest.mark.parametrize(
    "interval_hours",
    [
        0.0,
        -1.0,
    ],
)
def test_building_rejects_invalid_consumption_interval(
    interval_hours: float,
) -> None:
    building = BuildingLoad(
        base_load_kw=30.0,
        peak_load_kw=90.0,
    )

    with pytest.raises(
        ValueError,
        match="Consumption interval",
    ):
        building.calculate_consumed_energy_kwh(
            activity_factor=0.5,
            interval_hours=interval_hours,
        )