from gridflex_simulation.battery import Battery


def main() -> None:
    """
    Run a small demonstration of the battery simulation.
    """

    battery = Battery(
        capacity_kwh=100.0,
        state_of_charge_kwh=40.0,
    )

    print("GridFlex EMS simulation")
    print("-----------------------")
    print(
        f"Initial state of charge: "
        f"{battery.state_of_charge_percentage:.1f}%"
    )

    accepted_energy_kwh = battery.charge(25.0)

    print(f"Accepted charging energy: {accepted_energy_kwh:.1f} kWh")
    print(
        f"State of charge after charging: "
        f"{battery.state_of_charge_percentage:.1f}%"
    )

    delivered_energy_kwh = battery.discharge(15.0)

    print(f"Delivered energy: {delivered_energy_kwh:.1f} kWh")
    print(
        f"Final state of charge: "
        f"{battery.state_of_charge_percentage:.1f}%"
    )


if __name__ == "__main__":
    main()