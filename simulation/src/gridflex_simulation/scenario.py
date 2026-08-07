from dataclasses import dataclass

from gridflex_simulation.battery import Battery
from gridflex_simulation.building import BuildingLoad
from gridflex_simulation.grid import GridConnection
from gridflex_simulation.simulation_timeline import (
    SimulationStep,
    SimulationStepResult,
    SimulationTimelineRunner,
)
from gridflex_simulation.solar import SolarArray


@dataclass(frozen=True)
class BatteryScenarioConfiguration:
    """
    Defines the battery settings used when a scenario starts.
    """

    capacity_kwh: float
    initial_state_of_charge_kwh: float

    def create_battery(self) -> Battery:
        """
        Create a fresh battery from the scenario configuration.
        """

        return Battery(
            capacity_kwh=self.capacity_kwh,
            state_of_charge_kwh=self.initial_state_of_charge_kwh,
        )


@dataclass(frozen=True)
class SolarScenarioConfiguration:
    """
    Defines the solar installation used by a scenario.
    """

    installed_capacity_kw: float
    performance_ratio: float

    def create_solar_array(self) -> SolarArray:
        """
        Create a solar array from the scenario configuration.
        """

        return SolarArray(
            installed_capacity_kw=self.installed_capacity_kw,
            performance_ratio=self.performance_ratio,
        )


@dataclass(frozen=True)
class BuildingScenarioConfiguration:
    """
    Defines the building load used by a scenario.
    """

    base_load_kw: float
    peak_load_kw: float

    def create_building(self) -> BuildingLoad:
        """
        Create a building load from the scenario configuration.
        """

        return BuildingLoad(
            base_load_kw=self.base_load_kw,
            peak_load_kw=self.peak_load_kw,
        )


@dataclass(frozen=True)
class GridScenarioConfiguration:
    """
    Defines the electrical grid connection used by a scenario.
    """

    max_import_power_kw: float
    max_export_power_kw: float
    is_available: bool = True

    def create_grid(self) -> GridConnection:
        """
        Create a grid connection from the scenario configuration.
        """

        return GridConnection(
            max_import_power_kw=self.max_import_power_kw,
            max_export_power_kw=self.max_export_power_kw,
            is_available=self.is_available,
        )


@dataclass(frozen=True)
class SimulationScenario:
    """
    Describes a complete reproducible simulation scenario.

    A scenario contains system configuration together with the
    chronological operating conditions that should be simulated.
    """

    name: str
    battery: BatteryScenarioConfiguration
    solar: SolarScenarioConfiguration
    building: BuildingScenarioConfiguration
    grid: GridScenarioConfiguration
    steps: tuple[SimulationStep, ...]

    def __post_init__(self) -> None:
        """
        Validate basic scenario-level invariants.
        """

        if not self.name.strip():
            raise ValueError("Scenario name cannot be empty.")

        if not self.steps:
            raise ValueError("Scenario must contain at least one simulation step.")


@dataclass(frozen=True)
class SimulationScenarioResult:
    """
    Contains the completed result of a simulation scenario.
    """

    scenario_name: str
    steps: tuple[SimulationStepResult, ...]

    @property
    def final_battery_state_of_charge_kwh(self) -> float:
        """
        Return battery state of charge at the end of the scenario.
        """

        return self.steps[-1].measurement.battery_state_of_charge_kwh

    @property
    def total_grid_import_energy_kwh(self) -> float:
        """
        Return total energy imported from the grid.
        """

        return sum(step.measurement.grid_import_energy_kwh for step in self.steps)

    @property
    def total_grid_export_energy_kwh(self) -> float:
        """
        Return total energy exported to the grid.
        """

        return sum(step.measurement.grid_export_energy_kwh for step in self.steps)

    @property
    def total_unresolved_energy_kwh(self) -> float:
        """
        Return total unresolved energy across the scenario.
        """

        return sum(step.measurement.unresolved_energy_kwh for step in self.steps)


class SimulationScenarioRunner:
    """
    Creates fresh system components and executes a scenario.

    Creating new component instances for every run makes scenarios
    reproducible and prevents state from one run leaking into another.
    """

    @staticmethod
    def run(
        scenario: SimulationScenario,
    ) -> SimulationScenarioResult:
        """
        Run the supplied scenario from its configured initial state.
        """

        battery = scenario.battery.create_battery()
        solar_array = scenario.solar.create_solar_array()
        building = scenario.building.create_building()
        grid = scenario.grid.create_grid()

        results = SimulationTimelineRunner.run(
            steps=scenario.steps,
            battery=battery,
            solar_array=solar_array,
            building=building,
            grid=grid,
        )

        return SimulationScenarioResult(
            scenario_name=scenario.name,
            steps=results,
        )


def create_demo_scenario() -> SimulationScenario:
    """
    Create the default demonstration scenario.
    """

    return SimulationScenario(
        name="Three-step solar and load variation",
        battery=BatteryScenarioConfiguration(
            capacity_kwh=100.0,
            initial_state_of_charge_kwh=40.0,
        ),
        solar=SolarScenarioConfiguration(
            installed_capacity_kw=120.0,
            performance_ratio=0.85,
        ),
        building=BuildingScenarioConfiguration(
            base_load_kw=30.0,
            peak_load_kw=90.0,
        ),
        grid=GridScenarioConfiguration(
            max_import_power_kw=50.0,
            max_export_power_kw=50.0,
        ),
        steps=(
            SimulationStep(
                irradiance_factor=0.75,
                activity_factor=0.60,
                interval_hours=1.0,
            ),
            SimulationStep(
                irradiance_factor=0.25,
                activity_factor=0.80,
                interval_hours=1.0,
            ),
            SimulationStep(
                irradiance_factor=1.00,
                activity_factor=0.20,
                interval_hours=1.0,
            ),
        ),
    )
