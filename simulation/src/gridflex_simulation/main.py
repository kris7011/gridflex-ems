from gridflex_simulation.battery import Battery
from gridflex_simulation.solar import SolarArray


def main() -> None:
    """
    Run a small demonstration of the GridFlex EMS simulation components.
    """

    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=40.0,
    )

    solar_array = SolarArray(
        installed_capacity_kw=120.0,
        performance_ratio=0.85,
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
    interval_hours = 1.0

    output_power_kw = solar_array.calculate_output_power_kw(
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
        f"{output_power_kw:.1f} kW"
    )
    print(
        f"Generated energy: "
        f"{generated_energy_kwh:.1f} kWh"
    )


if __name__ == "__main__":
    main()