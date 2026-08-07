import math
from dataclasses import dataclass
from enum import StrEnum


class GridTransferDirection(StrEnum):
    """
    Describes the direction of an electrical grid energy transfer.
    """

    IMPORT = "import"
    EXPORT = "export"


@dataclass(frozen=True)
class GridTransferResult:
    """
    Contains the result of an electrical grid transfer.
    """

    direction: GridTransferDirection
    requested_energy_kwh: float
    transferred_energy_kwh: float
    remaining_energy_kwh: float


@dataclass(frozen=True)
class GridConnection:
    """
    Represents a simplified electrical grid connection.

    Import and export capacity are configured as power limits in kilowatts.
    The amount of energy that can be transferred depends on both the power
    limit and the duration of the simulation interval.
    """

    max_import_power_kw: float
    max_export_power_kw: float
    is_available: bool = True

    def __post_init__(self) -> None:
        """
        Validate the grid connection configuration.
        """

        self._validate_power_limit(
            value=self.max_import_power_kw,
            name="Maximum import power",
        )

        self._validate_power_limit(
            value=self.max_export_power_kw,
            name="Maximum export power",
        )

    def import_energy(
        self,
        requested_energy_kwh: float,
        interval_hours: float,
    ) -> GridTransferResult:
        """
        Import energy from the electrical grid.
        """

        return self._transfer_energy(
            direction=GridTransferDirection.IMPORT,
            requested_energy_kwh=requested_energy_kwh,
            interval_hours=interval_hours,
            max_power_kw=self.max_import_power_kw,
        )

    def export_energy(
        self,
        requested_energy_kwh: float,
        interval_hours: float,
    ) -> GridTransferResult:
        """
        Export energy to the electrical grid.
        """

        return self._transfer_energy(
            direction=GridTransferDirection.EXPORT,
            requested_energy_kwh=requested_energy_kwh,
            interval_hours=interval_hours,
            max_power_kw=self.max_export_power_kw,
        )

    def _transfer_energy(
        self,
        direction: GridTransferDirection,
        requested_energy_kwh: float,
        interval_hours: float,
        max_power_kw: float,
    ) -> GridTransferResult:
        """
        Transfer energy while respecting availability and power limits.
        """

        self._validate_requested_energy(requested_energy_kwh)
        self._validate_interval(interval_hours)

        maximum_transfer_energy_kwh = (
            max_power_kw * interval_hours
        )

        if self.is_available:
            transferred_energy_kwh = min(
                requested_energy_kwh,
                maximum_transfer_energy_kwh,
            )
        else:
            transferred_energy_kwh = 0.0

        remaining_energy_kwh = max(
            requested_energy_kwh - transferred_energy_kwh,
            0.0,
        )

        return GridTransferResult(
            direction=direction,
            requested_energy_kwh=requested_energy_kwh,
            transferred_energy_kwh=transferred_energy_kwh,
            remaining_energy_kwh=remaining_energy_kwh,
        )

    @staticmethod
    def _validate_power_limit(
        value: float,
        name: str,
    ) -> None:
        """
        Validate a configured grid power limit.
        """

        if not math.isfinite(value):
            raise ValueError(
                f"{name} must be a finite number."
            )

        if value < 0:
            raise ValueError(
                f"{name} cannot be negative."
            )

    @staticmethod
    def _validate_requested_energy(
        requested_energy_kwh: float,
    ) -> None:
        """
        Validate a requested grid energy transfer.
        """

        if not math.isfinite(requested_energy_kwh):
            raise ValueError(
                "Requested grid energy must be a finite number."
            )

        if requested_energy_kwh < 0:
            raise ValueError(
                "Requested grid energy cannot be negative."
            )

    @staticmethod
    def _validate_interval(
        interval_hours: float,
    ) -> None:
        """
        Validate the duration of the transfer interval.
        """

        if not math.isfinite(interval_hours):
            raise ValueError(
                "Grid interval must be a finite number."
            )

        if interval_hours <= 0:
            raise ValueError(
                "Grid interval must be greater than zero."
            )