from dataclasses import dataclass


@dataclass
class Battery:
    """
    Represents a simplified battery energy storage system.

    The first version models capacity and state of charge only.
    More advanced behavior, such as charging losses, temperature
    and degradation, will be added later.
    """

    capacity_kwh: float
    state_of_charge_kwh: float

    def __post_init__(self) -> None:
        """
        Validate the initial battery state after the dataclass
        has generated its constructor.
        """

        if self.capacity_kwh <= 0:
            raise ValueError("Battery capacity must be greater than zero.")

        if self.state_of_charge_kwh < 0:
            raise ValueError("State of charge cannot be negative.")

        if self.state_of_charge_kwh > self.capacity_kwh:
            raise ValueError(
                "State of charge cannot exceed the battery capacity."
            )

    @property
    def state_of_charge_percentage(self) -> float:
        """
        Return the current state of charge as a percentage.
        """

        return self.state_of_charge_kwh / self.capacity_kwh * 100

    @property
    def available_capacity_kwh(self) -> float:
        """
        Return the amount of energy that can still be stored.
        """

        return self.capacity_kwh - self.state_of_charge_kwh

    def charge(self, requested_energy_kwh: float) -> float:
        """
        Charge the battery and return the amount of energy accepted.

        The battery cannot be charged beyond its total capacity.
        """

        if requested_energy_kwh < 0:
            raise ValueError("Requested charging energy cannot be negative.")

        accepted_energy_kwh = min(
            requested_energy_kwh,
            self.available_capacity_kwh,
        )

        self.state_of_charge_kwh += accepted_energy_kwh

        return accepted_energy_kwh

    def discharge(self, requested_energy_kwh: float) -> float:
        """
        Discharge the battery and return the amount of energy delivered.

        The battery cannot deliver more energy than it currently stores.
        """

        if requested_energy_kwh < 0:
            raise ValueError("Requested discharging energy cannot be negative.")

        delivered_energy_kwh = min(
            requested_energy_kwh,
            self.state_of_charge_kwh,
        )

        self.state_of_charge_kwh -= delivered_energy_kwh

        return delivered_energy_kwh