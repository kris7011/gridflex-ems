from gridflex_simulation.battery import Battery
from gridflex_simulation.building import BuildingLoad
from gridflex_simulation.grid import GridConnection
from gridflex_simulation.simulation_timeline import (
    SimulationStep,
    SimulationTimelineRunner,
)
from gridflex_simulation.solar import SolarArray


def main() -> None:
    """
    Run a multi-step GridFlex EMS simulation.
    """

    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=40.0,
    )

    solar_array = SolarArray(
        installed_capacity_kw=120.0,
        performance_ratio=0.85,
    )

    building = BuildingLoad(
        base_load_kw=30.0,
        peak_load_kw=90.0,
    )

    grid = GridConnection(
        max_import_power_kw=50.0,
        max_export_power_kw=50.0,
    )

    steps = (
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
    )

    results = SimulationTimelineRunner.run(
        steps=steps,
        battery=battery,
        solar_array=solar_array,
        building=building,
        grid=grid,
    )

    print("GridFlex EMS timeline simulation")
    print("--------------------------------")

    for result in results:
        measurement = result.measurement
        management_result = result.management_result
        battery_dispatch = management_result.battery_dispatch

        print()
        print(f"Step {measurement.step_number}")
        print("------")

        print(f"Elapsed time: " f"{measurement.elapsed_time_hours:.1f} hours")
        print(f"Interval: " f"{measurement.interval_hours:.1f} hour")

        print(f"Solar generation: " f"{measurement.generated_energy_kwh:.1f} kWh")
        print(f"Building consumption: " f"{measurement.consumed_energy_kwh:.1f} kWh")
        print(f"Net energy: " f"{measurement.net_energy_kwh:.1f} kWh")

        print(f"Battery action: " f"{battery_dispatch.action.value}")
        print(
            f"Battery state of charge: "
            f"{measurement.battery_state_of_charge_kwh:.1f} kWh"
        )

        print(f"Grid import: " f"{measurement.grid_import_energy_kwh:.1f} kWh")
        print(f"Grid export: " f"{measurement.grid_export_energy_kwh:.1f} kWh")
        print(f"Grid net energy: " f"{measurement.grid_net_energy_kwh:.1f} kWh")

        print(f"Unresolved energy: " f"{measurement.unresolved_energy_kwh:.1f} kWh")

    print()
    print("Final system state")
    print("------------------")
    print(f"Battery state of charge: " f"{battery.state_of_charge_kwh:.1f} kWh")
    print(
        f"Battery state of charge percentage: "
        f"{battery.state_of_charge_percentage:.1f}%"
    )


if __name__ == "__main__":
    main()
