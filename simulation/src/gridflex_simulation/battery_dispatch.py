from dataclasses import dataclass
from enum import StrEnum

from gridflex_simulation.battery import Battery
from gridflex_simulation.energy_balance import (
    EnergyBalanceResult,
    EnergyBalanceStatus,
)


class BatteryDispatchAction(StrEnum):
    """
    Describes the action requested from the battery.
    """

    CHARGE = "charge"
    DISCHARGE = "discharge"
    IDLE = "idle"


@dataclass(frozen=True)
class BatteryDispatchResult:
    """
    Contains the result of a battery dispatch operation.
    """

    action: BatteryDispatchAction
    requested_energy_kwh: float
    transferred_energy_kwh: float
    remaining_energy_kwh: float
    initial_state_of_charge_kwh: float
    final_state_of_charge_kwh: float

    @property
    def state_of_charge_change_kwh(self) -> float:
        """
        Return the signed change in battery state of charge.

        A positive value represents charging.
        A negative value represents discharging.
        """

        return (
            self.final_state_of_charge_kwh
            - self.initial_state_of_charge_kwh
        )


class BatteryDispatchService:
    """
    Applies an energy balance to a battery.

    Surplus energy is used to charge the battery.
    An energy deficit is supplied by discharging the battery.
    A balanced system leaves the battery unchanged.
    """

    @staticmethod
    def dispatch(
        battery: Battery,
        balance: EnergyBalanceResult,
    ) -> BatteryDispatchResult:
        """
        Dispatch the battery based on the supplied energy balance.
        """

        initial_state_of_charge_kwh = (
            battery.state_of_charge_kwh
        )

        if balance.status is EnergyBalanceStatus.SURPLUS:
            action = BatteryDispatchAction.CHARGE
            requested_energy_kwh = balance.surplus_energy_kwh

            transferred_energy_kwh = battery.charge(
                requested_energy_kwh=requested_energy_kwh,
            )

        elif balance.status is EnergyBalanceStatus.DEFICIT:
            action = BatteryDispatchAction.DISCHARGE
            requested_energy_kwh = balance.deficit_energy_kwh

            transferred_energy_kwh = battery.discharge(
                requested_energy_kwh=requested_energy_kwh,
            )

        else:
            action = BatteryDispatchAction.IDLE
            requested_energy_kwh = 0.0
            transferred_energy_kwh = 0.0

        remaining_energy_kwh = max(
            requested_energy_kwh - transferred_energy_kwh,
            0.0,
        )

        return BatteryDispatchResult(
            action=action,
            requested_energy_kwh=requested_energy_kwh,
            transferred_energy_kwh=transferred_energy_kwh,
            remaining_energy_kwh=remaining_energy_kwh,
            initial_state_of_charge_kwh=initial_state_of_charge_kwh,
            final_state_of_charge_kwh=battery.state_of_charge_kwh,
        )