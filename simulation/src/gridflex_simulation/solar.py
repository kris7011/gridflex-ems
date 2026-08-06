from dataclasses import dataclass


@dataclass(frozen=True)
class SolarArray:
    """
    Represents a simplified solar power installation.

    The model uses installed capacity, a normalized irradiance factor
    and a performance ratio to calculate output power and generated energy.
    """

    installed_capacity_kw: float
    performance_ratio: float = 0.85

    def __post_init__(self) -> None:
        """
        Validate the solar array configuration after initialization.
        """

        if self.installed_capacity_kw <= 0:
            raise ValueError(
                "Installed solar capacity must be greater than zero."
            )

        if not 0 < self.performance_ratio <= 1:
            raise ValueError(
                "Performance ratio must be greater than zero "
                "and less than or equal to one."
            )

    def calculate_output_power_kw(
        self,
        irradiance_factor: float,
    ) -> float:
        """
        Calculate the current solar output power in kilowatts.

        The irradiance factor is normalized:

        - 0.0 means no available sunlight
        - 0.5 means half of the reference sunlight
        - 1.0 means full reference sunlight
        """

        self._validate_irradiance_factor(irradiance_factor)

        return (
            self.installed_capacity_kw
            * irradiance_factor
            * self.performance_ratio
        )

    def calculate_generated_energy_kwh(
        self,
        irradiance_factor: float,
        interval_hours: float,
    ) -> float:
        """
        Calculate generated energy during a time interval.

        Energy in kilowatt-hours is calculated as output power in
        kilowatts multiplied by the duration in hours.
        """

        if interval_hours <= 0:
            raise ValueError(
                "Simulation interval must be greater than zero."
            )

        output_power_kw = self.calculate_output_power_kw(
            irradiance_factor=irradiance_factor,
        )

        return output_power_kw * interval_hours

    @staticmethod
    def _validate_irradiance_factor(
        irradiance_factor: float,
    ) -> None:
        """
        Validate that the normalized irradiance factor is between zero and one.
        """

        if not 0 <= irradiance_factor <= 1:
            raise ValueError(
                "Irradiance factor must be between zero and one."
            )