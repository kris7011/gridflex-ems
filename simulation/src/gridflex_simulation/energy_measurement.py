import math
from dataclasses import dataclass

from gridflex_simulation.energy_management import (
    EnergyManagementResult,
)
from gridflex_simulation.grid import GridTransferDirection


@dataclass(frozen=True)
class EnergyMeasurement:
    """
    Represents an immutable energy-system measurement snapshot.

    The measurement describes the system after one completed
    simulation interval.
    """

    step_number: int
    elapsed_time_hours: float
    interval_hours: float
    generated_energy_kwh: float
    consumed_energy_kwh: float
    net_energy_kwh: float
    battery_state_of_charge_kwh: float
    grid_import_energy_kwh: float
    grid_export_energy_kwh: float
    unresolved_energy_kwh: float

    def __post_init__(self) -> None:
        """
        Validate the measurement snapshot.
        """

        if self.step_number <= 0:
            raise ValueError("Measurement step number must be greater than zero.")

        self._validate_positive_finite(
            value=self.elapsed_time_hours,
            name="Elapsed time",
        )

        self._validate_positive_finite(
            value=self.interval_hours,
            name="Measurement interval",
        )

        self._validate_non_negative_finite(
            value=self.generated_energy_kwh,
            name="Generated energy",
        )

        self._validate_non_negative_finite(
            value=self.consumed_energy_kwh,
            name="Consumed energy",
        )

        self._validate_non_negative_finite(
            value=self.battery_state_of_charge_kwh,
            name="Battery state of charge",
        )

        self._validate_non_negative_finite(
            value=self.grid_import_energy_kwh,
            name="Grid import energy",
        )

        self._validate_non_negative_finite(
            value=self.grid_export_energy_kwh,
            name="Grid export energy",
        )

        self._validate_non_negative_finite(
            value=self.unresolved_energy_kwh,
            name="Unresolved energy",
        )

        if not math.isfinite(self.net_energy_kwh):
            raise ValueError("Net energy must be a finite number.")

        if self.grid_import_energy_kwh > 0 and self.grid_export_energy_kwh > 0:
            raise ValueError(
                "A measurement cannot contain both grid import "
                "and grid export energy."
            )

    @property
    def grid_net_energy_kwh(self) -> float:
        """
        Return signed grid energy.

        Positive values represent grid import.
        Negative values represent grid export.
        """

        return self.grid_import_energy_kwh - self.grid_export_energy_kwh

    @staticmethod
    def _validate_positive_finite(
        value: float,
        name: str,
    ) -> None:
        """
        Validate a value that must be finite and greater than zero.
        """

        if not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number.")

        if value <= 0:
            raise ValueError(f"{name} must be greater than zero.")

    @staticmethod
    def _validate_non_negative_finite(
        value: float,
        name: str,
    ) -> None:
        """
        Validate a value that must be finite and non-negative.
        """

        if not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number.")

        if value < 0:
            raise ValueError(f"{name} cannot be negative.")


class EnergyMeasurementFactory:
    """
    Converts an internal energy-management result into measurement data.
    """

    @staticmethod
    def create(
        step_number: int,
        elapsed_time_hours: float,
        interval_hours: float,
        management_result: EnergyManagementResult,
    ) -> EnergyMeasurement:
        """
        Create a measurement for one completed simulation interval.
        """

        grid_import_energy_kwh = 0.0
        grid_export_energy_kwh = 0.0

        grid_transfer = management_result.grid_transfer

        if grid_transfer is not None:
            if grid_transfer.direction is GridTransferDirection.IMPORT:
                grid_import_energy_kwh = grid_transfer.transferred_energy_kwh
            else:
                grid_export_energy_kwh = grid_transfer.transferred_energy_kwh

        return EnergyMeasurement(
            step_number=step_number,
            elapsed_time_hours=elapsed_time_hours,
            interval_hours=interval_hours,
            generated_energy_kwh=(management_result.balance.generated_energy_kwh),
            consumed_energy_kwh=(management_result.balance.consumed_energy_kwh),
            net_energy_kwh=(management_result.balance.net_energy_kwh),
            battery_state_of_charge_kwh=(
                management_result.battery_dispatch.final_state_of_charge_kwh
            ),
            grid_import_energy_kwh=grid_import_energy_kwh,
            grid_export_energy_kwh=grid_export_energy_kwh,
            unresolved_energy_kwh=(management_result.unresolved_energy_kwh),
        )
