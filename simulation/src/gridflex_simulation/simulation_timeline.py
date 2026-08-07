from collections.abc import Sequence
from dataclasses import dataclass

from gridflex_simulation.battery import Battery
from gridflex_simulation.building import BuildingLoad
from gridflex_simulation.energy_management import (
    EnergyManagementResult,
    EnergyManagementService,
)
from gridflex_simulation.energy_measurement import (
    EnergyMeasurement,
    EnergyMeasurementFactory,
)
from gridflex_simulation.grid import GridConnection
from gridflex_simulation.solar import SolarArray


@dataclass(frozen=True)
class SimulationStep:
    """
    Describes the input conditions for one simulation interval.
    """

    irradiance_factor: float
    activity_factor: float
    interval_hours: float


@dataclass(frozen=True)
class SimulationStepResult:
    """
    Contains the result of one completed simulation interval.
    """

    simulation_step: SimulationStep
    measurement: EnergyMeasurement
    management_result: EnergyManagementResult

    @property
    def step_number(self) -> int:
        """
        Return the chronological step number.
        """

        return self.measurement.step_number

    @property
    def generated_energy_kwh(self) -> float:
        """
        Return solar energy generated during the step.
        """

        return self.measurement.generated_energy_kwh

    @property
    def consumed_energy_kwh(self) -> float:
        """
        Return building energy consumed during the step.
        """

        return self.measurement.consumed_energy_kwh

    @property
    def final_battery_state_of_charge_kwh(self) -> float:
        """
        Return battery state of charge after the step.
        """

        return self.measurement.battery_state_of_charge_kwh


class SimulationTimelineRunner:
    """
    Runs a sequence of simulation steps in chronological order.

    The same battery and grid instances are reused across all steps,
    allowing system state to evolve throughout the timeline.
    """

    @staticmethod
    def run(
        steps: Sequence[SimulationStep],
        battery: Battery,
        solar_array: SolarArray,
        building: BuildingLoad,
        grid: GridConnection,
    ) -> tuple[SimulationStepResult, ...]:
        """
        Run all simulation steps and return their results.
        """

        if not steps:
            raise ValueError("Simulation timeline must contain at least one step.")

        results: list[SimulationStepResult] = []
        elapsed_time_hours = 0.0

        for step_number, simulation_step in enumerate(
            steps,
            start=1,
        ):
            generated_energy_kwh = solar_array.calculate_generated_energy_kwh(
                irradiance_factor=(simulation_step.irradiance_factor),
                interval_hours=(simulation_step.interval_hours),
            )

            consumed_energy_kwh = building.calculate_consumed_energy_kwh(
                activity_factor=(simulation_step.activity_factor),
                interval_hours=(simulation_step.interval_hours),
            )

            management_result = EnergyManagementService.manage(
                battery=battery,
                grid=grid,
                generated_energy_kwh=generated_energy_kwh,
                consumed_energy_kwh=consumed_energy_kwh,
                interval_hours=simulation_step.interval_hours,
            )

            elapsed_time_hours += simulation_step.interval_hours

            measurement = EnergyMeasurementFactory.create(
                step_number=step_number,
                elapsed_time_hours=elapsed_time_hours,
                interval_hours=simulation_step.interval_hours,
                management_result=management_result,
            )

            results.append(
                SimulationStepResult(
                    simulation_step=simulation_step,
                    measurement=measurement,
                    management_result=management_result,
                )
            )

        return tuple(results)
