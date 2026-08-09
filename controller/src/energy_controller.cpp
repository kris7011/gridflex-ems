#include "gridflex/controller/energy_controller.hpp"

#include <cmath>

namespace
{

    constexpr double energy_balance_tolerance_kwh = 1.0e-9;

}

namespace gridflex::controller
{

    ControlCommand EnergyController::decide(
        const EnergyMeasurement &measurement) const
    {
        const double net_energy_kwh = measurement.net_energy_kwh();

        if (std::abs(net_energy_kwh) <= energy_balance_tolerance_kwh)
        {
            return ControlCommand{
                measurement.step_number(),
                ControlAction::Idle,
                0.0};
        }

        const double requested_power_kw =
            std::abs(net_energy_kwh) / measurement.interval_hours();

        const auto action =
            net_energy_kwh > 0.0
                ? ControlAction::ChargeBattery
                : ControlAction::DischargeBattery;

        return ControlCommand{
            measurement.step_number(),
            action,
            requested_power_kw};
    }

}
