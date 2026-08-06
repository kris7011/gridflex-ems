from gridflex_simulation.battery import Battery
from gridflex_simulation.building import BuildingLoad
from gridflex_simulation.solar import SolarArray


def main() -> None:
    """
    Run a demonstration of the GridFlex EMS simulation components.
    """

    interval_hours = 1.0

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

    print("GridFlex EMS simulation")
    print("-----------------------")

    print()
    print("Battery")
    print("-------")
    print(
        f"Initial state of charge: "
        f"{battery.state_of_charge_percentage:.1f}%"
    )

    accepted_energy_kwh = battery.charge(25.0)

    print(
        f"Accepted charging energy: "
        f"{accepted_energy_kwh:.1f} kWh"
    )
    print(
        f"State of charge after charging: "
        f"{battery.state_of_charge_percentage:.1f}%"
    )

    delivered_energy_kwh = battery.discharge(15.0)

    print(
        f"Delivered energy: "
        f"{delivered_energy_kwh:.1f} kWh"
    )
    print(
        f"Final state of charge: "
        f"{battery.state_of_charge_percentage:.1f}%"
    )

    print()
    print("Solar generation")
    print("----------------")

    irradiance_factor = 0.75

    solar_output_power_kw = solar_array.calculate_output_power_kw(
        irradiance_factor=irradiance_factor,
    )

    generated_energy_kwh = solar_array.calculate_generated_energy_kwh(
        irradiance_factor=irradiance_factor,
        interval_hours=interval_hours,
    )

    print(
        f"Installed capacity: "
        f"{solar_array.installed_capacity_kw:.1f} kW"
    )
    print(
        f"Irradiance factor: "
        f"{irradiance_factor:.2f}"
    )
    print(
        f"Current output power: "
        f"{solar_output_power_kw:.1f} kW"
    )
    print(
        f"Generated energy: "
        f"{generated_energy_kwh:.1f} kWh"
    )

    print()
    print("Building consumption")
    print("--------------------")

    activity_factor = 0.60

    building_power_demand_kw = building.calculate_power_demand_kw(
        activity_factor=activity_factor,
    )

    consumed_energy_kwh = building.calculate_consumed_energy_kwh(
        activity_factor=activity_factor,
        interval_hours=interval_hours,
    )

    print(
        f"Base load: "
        f"{building.base_load_kw:.1f} kW"
    )
    print(
        f"Peak load: "
        f"{building.peak_load_kw:.1f} kW"
    )
    print(
        f"Activity factor: "
        f"{activity_factor:.2f}"
    )
    print(
        f"Current power demand: "
        f"{building_power_demand_kw:.1f} kW"
    )
    print(
        f"Consumed energy: "
        f"{consumed_energy_kwh:.1f} kWh"
    )

    print()
    print("Energy balance")
    print("--------------")

    net_energy_kwh = (
        generated_energy_kwh - consumed_energy_kwh
    )

    if net_energy_kwh >= 0:
        print(
            f"Energy surplus: "
            f"{net_energy_kwh:.1f} kWh"
        )
    else:
        print(
            f"Energy deficit: "
            f"{abs(net_energy_kwh):.1f} kWh"
        )


if __name__ == "__main__":
    main()