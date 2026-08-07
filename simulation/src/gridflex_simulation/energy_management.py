import math
from dataclasses import dataclass

from gridflex_simulation.battery import Battery
from gridflex_simulation.battery_dispatch import (
    BatteryDispatchResult,
    BatteryDispatchService,
)
from gridflex_simulation.energy_balance import (
    EnergyBalanceCalculator,
    EnergyBalanceResult,
    EnergyBalanceStatus,
)
from gridflex_simulation.grid import (
    GridConnection,
    GridTransferResult,
)


@dataclass(frozen=True)
class EnergyManagementResult:
    """
    Contains the result of one energy management step.
    """

    balance: EnergyBalanceResult
    battery_dispatch: BatteryDispatchResult
    grid_transfer: GridTransferResult | None

    @property
    def unresolved_energy_kwh(self) -> float:
        """
        Return energy that could not be handled by the battery or grid.

        A value greater than zero means that further system action
        would be required.
        """

        if self.grid_transfer is not None:
            return self.grid_transfer.remaining_energy_kwh

        return self.battery_dispatch.remaining_energy_kwh


class EnergyManagementService:
    """
    Coordinates one simplified energy management step.

    The service first calculates the energy balance, then uses the
    battery, and finally uses the electrical grid for any remaining
    surplus or deficit.
    """

    @staticmethod
    def manage(
        battery: Battery,
        grid: GridConnection,
        generated_energy_kwh: float,
        consumed_energy_kwh: float,
        interval_hours: float,
    ) -> EnergyManagementResult:
        """
        Coordinate energy flow for one simulation interval.
        """

        EnergyManagementService._validate_interval(
            interval_hours=interval_hours,
        )

        balance = EnergyBalanceCalculator.calculate(
            generated_energy_kwh=generated_energy_kwh,
            consumed_energy_kwh=consumed_energy_kwh,
        )

        battery_dispatch = BatteryDispatchService.dispatch(
            battery=battery,
            balance=balance,
        )

        grid_transfer: GridTransferResult | None = None

        if battery_dispatch.remaining_energy_kwh > 0:
            if balance.status is EnergyBalanceStatus.SURPLUS:
                grid_transfer = grid.export_energy(
                    requested_energy_kwh=(battery_dispatch.remaining_energy_kwh),
                    interval_hours=interval_hours,
                )

            elif balance.status is EnergyBalanceStatus.DEFICIT:
                grid_transfer = grid.import_energy(
                    requested_energy_kwh=(battery_dispatch.remaining_energy_kwh),
                    interval_hours=interval_hours,
                )

        return EnergyManagementResult(
            balance=balance,
            battery_dispatch=battery_dispatch,
            grid_transfer=grid_transfer,
        )

    @staticmethod
    def _validate_interval(
        interval_hours: float,
    ) -> None:
        """
        Validate the simulation interval.
        """

        if not math.isfinite(interval_hours):
            raise ValueError("Energy management interval must be a finite number.")

        if interval_hours <= 0:
            raise ValueError("Energy management interval must be greater than zero.")
