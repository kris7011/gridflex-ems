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
        simulation_step = result.simulation_step
        management_result = result.management_result
        balance = management_result.balance
        battery_dispatch = management_result.battery_dispatch
        grid_transfer = management_result.grid_transfer

        print()
        print(f"Step {result.step_number}")
        print("------")
        print(f"Irradiance factor: " f"{simulation_step.irradiance_factor:.2f}")
        print(f"Building activity factor: " f"{simulation_step.activity_factor:.2f}")
        print(f"Interval: " f"{simulation_step.interval_hours:.1f} hour")

        print(f"Solar generation: " f"{result.generated_energy_kwh:.1f} kWh")
        print(f"Building consumption: " f"{result.consumed_energy_kwh:.1f} kWh")

        print(f"Energy balance: {balance.status.value}")

        print(f"Battery action: " f"{battery_dispatch.action.value}")
        print(
            f"Battery SOC: "
            f"{battery_dispatch.initial_state_of_charge_kwh:.1f} "
            f"→ "
            f"{battery_dispatch.final_state_of_charge_kwh:.1f} kWh"
        )

        if grid_transfer is None:
            print("Grid transfer: none")
        else:
            print(
                f"Grid transfer: "
                f"{grid_transfer.direction.value} "
                f"{grid_transfer.transferred_energy_kwh:.1f} kWh"
            )

        print(
            f"Unresolved energy: " f"{management_result.unresolved_energy_kwh:.1f} kWh"
        )

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
