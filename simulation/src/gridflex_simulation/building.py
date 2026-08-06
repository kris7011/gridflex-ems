from dataclasses import dataclass


@dataclass(frozen=True)
class BuildingLoad:
    """
    Represents a simplified building electrical load.

    The model calculates current power demand between a configured
    base load and peak load using a normalized activity factor.
    """

    base_load_kw: float
    peak_load_kw: float

    def __post_init__(self) -> None:
        """
        Validate the building load configuration after initialization.
        """

        if self.base_load_kw < 0:
            raise ValueError(
                "Building base load cannot be negative."
            )

        if self.peak_load_kw <= 0:
            raise ValueError(
                "Building peak load must be greater than zero."
            )

        if self.peak_load_kw < self.base_load_kw:
            raise ValueError(
                "Building peak load cannot be lower than base load."
            )

    def calculate_power_demand_kw(
        self,
        activity_factor: float,
    ) -> float:
        """
        Calculate the current electrical power demand in kilowatts.

        The activity factor is normalized:

        - 0.0 represents base-load operation
        - 0.5 represents medium activity
        - 1.0 represents peak-load operation
        """

        self._validate_activity_factor(activity_factor)

        variable_load_range_kw = (
            self.peak_load_kw - self.base_load_kw
        )

        return (
            self.base_load_kw
            + variable_load_range_kw * activity_factor
        )

    def calculate_consumed_energy_kwh(
        self,
        activity_factor: float,
        interval_hours: float,
    ) -> float:
        """
        Calculate consumed electrical energy during a time interval.

        Energy in kilowatt-hours is calculated as power demand in
        kilowatts multiplied by the duration in hours.
        """

        if interval_hours <= 0:
            raise ValueError(
                "Consumption interval must be greater than zero."
            )

        power_demand_kw = self.calculate_power_demand_kw(
            activity_factor=activity_factor,
        )

        return power_demand_kw * interval_hours

    @staticmethod
    def _validate_activity_factor(
        activity_factor: float,
    ) -> None:
        """
        Validate that the normalized activity factor is between zero and one.
        """

        if not 0 <= activity_factor <= 1:
            raise ValueError(
                "Activity factor must be between zero and one."
            )