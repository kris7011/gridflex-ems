from gridflex_simulation.battery import Battery
from gridflex_simulation.battery_dispatch import (
    BatteryDispatchAction,
    BatteryDispatchService,
)
from gridflex_simulation.building import BuildingLoad
from gridflex_simulation.energy_balance import (
    EnergyBalanceCalculator,
    EnergyBalanceStatus,
)
from gridflex_simulation.solar import SolarArray


def main() -> None:
    """
    Run an integrated GridFlex EMS simulation example.
    """

    interval_hours = 1.0
    irradiance_factor = 0.75
    activity_factor = 0.60

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

    generated_energy_kwh = (
        solar_array.calculate_generated_energy_kwh(
            irradiance_factor=irradiance_factor,
            interval_hours=interval_hours,
        )
    )

    consumed_energy_kwh = (
        building.calculate_consumed_energy_kwh(
            activity_factor=activity_factor,
            interval_hours=interval_hours,
        )
    )

    balance = EnergyBalanceCalculator.calculate(
        generated_energy_kwh=generated_energy_kwh,
        consumed_energy_kwh=consumed_energy_kwh,
    )

    dispatch_result = BatteryDispatchService.dispatch(
        battery=battery,
        balance=balance,
    )

    print("GridFlex EMS simulation")
    print("-----------------------")

    print()
    print("Inputs")
    print("------")
    print(f"Simulation interval: {interval_hours:.1f} hour")
    print(f"Irradiance factor: {irradiance_factor:.2f}")
    print(f"Building activity factor: {activity_factor:.2f}")

    print()
    print("Energy")
    print("------")
    print(f"Solar generation: {generated_energy_kwh:.1f} kWh")
    print(f"Building consumption: {consumed_energy_kwh:.1f} kWh")

    if balance.status is EnergyBalanceStatus.SURPLUS:
        print(f"Energy surplus: {balance.surplus_energy_kwh:.1f} kWh")
    elif balance.status is EnergyBalanceStatus.DEFICIT:
        print(f"Energy deficit: {balance.deficit_energy_kwh:.1f} kWh")
    else:
        print("Energy generation and consumption are balanced.")

    print()
    print("Battery dispatch")
    print("----------------")
    print(
        f"Action: "
        f"{dispatch_result.action.value}"
    )
    print(
        f"Requested energy: "
        f"{dispatch_result.requested_energy_kwh:.1f} kWh"
    )
    print(
        f"Transferred energy: "
        f"{dispatch_result.transferred_energy_kwh:.1f} kWh"
    )
    print(
        f"Remaining energy: "
        f"{dispatch_result.remaining_energy_kwh:.1f} kWh"
    )
    print(
        f"Initial state of charge: "
        f"{dispatch_result.initial_state_of_charge_kwh:.1f} kWh"
    )
    print(
        f"Final state of charge: "
        f"{dispatch_result.final_state_of_charge_kwh:.1f} kWh"
    )
    print(
        f"Final state of charge: "
        f"{battery.state_of_charge_percentage:.1f}%"
    )

    if dispatch_result.action is BatteryDispatchAction.CHARGE:
        print("The battery absorbed available surplus energy.")
    elif dispatch_result.action is BatteryDispatchAction.DISCHARGE:
        print("The battery supplied energy to reduce the deficit.")
    else:
        print("No battery dispatch was required.")


if __name__ == "__main__":
    main()