import math
from dataclasses import dataclass
from enum import StrEnum

BALANCE_TOLERANCE_KWH = 1e-9


class EnergyBalanceStatus(StrEnum):
    """
    Describes the relationship between generated and consumed energy.
    """

    SURPLUS = "surplus"
    DEFICIT = "deficit"
    BALANCED = "balanced"


@dataclass(frozen=True)
class EnergyBalanceResult:
    """
    Contains the result of an energy balance calculation.
    """

    generated_energy_kwh: float
    consumed_energy_kwh: float
    net_energy_kwh: float
    status: EnergyBalanceStatus

    @property
    def surplus_energy_kwh(self) -> float:
        """
        Return available surplus energy.

        A deficit or balanced result has no surplus.
        """

        return max(self.net_energy_kwh, 0.0)

    @property
    def deficit_energy_kwh(self) -> float:
        """
        Return the amount of missing energy.

        A surplus or balanced result has no deficit.
        """

        return max(-self.net_energy_kwh, 0.0)


class EnergyBalanceCalculator:
    """
    Calculates the balance between generated and consumed energy.
    """

    @staticmethod
    def calculate(
        generated_energy_kwh: float,
        consumed_energy_kwh: float,
    ) -> EnergyBalanceResult:
        """
        Calculate the net energy balance.

        A positive result represents surplus energy.
        A negative result represents an energy deficit.
        A result sufficiently close to zero is considered balanced.
        """

        EnergyBalanceCalculator._validate_energy_value(
            value=generated_energy_kwh,
            name="Generated energy",
        )

        EnergyBalanceCalculator._validate_energy_value(
            value=consumed_energy_kwh,
            name="Consumed energy",
        )

        net_energy_kwh = (
            generated_energy_kwh - consumed_energy_kwh
        )

        if math.isclose(
            net_energy_kwh,
            0.0,
            rel_tol=0.0,
            abs_tol=BALANCE_TOLERANCE_KWH,
        ):
            net_energy_kwh = 0.0
            status = EnergyBalanceStatus.BALANCED
        elif net_energy_kwh > 0:
            status = EnergyBalanceStatus.SURPLUS
        else:
            status = EnergyBalanceStatus.DEFICIT

        return EnergyBalanceResult(
            generated_energy_kwh=generated_energy_kwh,
            consumed_energy_kwh=consumed_energy_kwh,
            net_energy_kwh=net_energy_kwh,
            status=status,
        )

    @staticmethod
    def _validate_energy_value(
        value: float,
        name: str,
    ) -> None:
        """
        Validate that an energy value is finite and non-negative.
        """

        if not math.isfinite(value):
            raise ValueError(
                f"{name} must be a finite number."
            )

        if value < 0:
            raise ValueError(
                f"{name} cannot be negative."
            )