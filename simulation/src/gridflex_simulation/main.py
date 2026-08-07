from gridflex_simulation.scenario import (
    SimulationScenarioRunner,
    create_demo_scenario,
)


def main() -> None:
    """
    Run the default GridFlex EMS demonstration scenario.
    """

    scenario = create_demo_scenario()

    result = SimulationScenarioRunner.run(
        scenario=scenario,
    )

    print("GridFlex EMS scenario simulation")
    print("--------------------------------")
    print(f"Scenario: {result.scenario_name}")

    for step_result in result.steps:
        measurement = step_result.measurement
        battery_dispatch = step_result.management_result.battery_dispatch

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

        print(f"Unresolved energy: " f"{measurement.unresolved_energy_kwh:.1f} kWh")

    print()
    print("Scenario summary")
    print("----------------")
    print(
        f"Final battery state of charge: "
        f"{result.final_battery_state_of_charge_kwh:.1f} kWh"
    )
    print(f"Total grid import: " f"{result.total_grid_import_energy_kwh:.1f} kWh")
    print(f"Total grid export: " f"{result.total_grid_export_energy_kwh:.1f} kWh")
    print(f"Total unresolved energy: " f"{result.total_unresolved_energy_kwh:.1f} kWh")


if __name__ == "__main__":
    main()
