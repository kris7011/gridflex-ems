#include "gridflex/controller/energy_controller.hpp"

#include <algorithm>
#include <cmath>

namespace
{

    constexpr double energy_balance_tolerance_kwh = 1.0e-9;

}

namespace gridflex::controller
{

    EnergyController::EnergyController(
        const ControllerLimits &limits)
        : limits_{limits}
    {
    }

    ControlCommand EnergyController::decide(
        const EnergyMeasurement &measurement) const
    {
        const double net_energy_kwh =
            measurement.net_energy_kwh();

        if (std::abs(net_energy_kwh) <= energy_balance_tolerance_kwh)
        {
            return create_idle_command(measurement);
        }

        if (net_energy_kwh > 0.0)
        {
            return decide_surplus(measurement);
        }

        return decide_deficit(measurement);
    }

    ControlCommand EnergyController::decide_surplus(
        const EnergyMeasurement &measurement) const
    {
        const double requested_power_kw =
            measurement.net_energy_kwh() /
            measurement.interval_hours();

        const double available_charge_energy_kwh =
            std::max(
                0.0,
                limits_.maximum_battery_soc_kwh() -
                    measurement.battery_state_of_charge_kwh());

        const double soc_limited_power_kw =
            available_charge_energy_kwh /
            measurement.interval_hours();

        const double allowed_power_kw =
            std::min(
                {requested_power_kw,
                 limits_.max_charge_power_kw(),
                 soc_limited_power_kw});

        if (allowed_power_kw <= 0.0)
        {
            return create_idle_command(measurement);
        }

        return ControlCommand{
            measurement.step_number(),
            ControlAction::ChargeBattery,
            allowed_power_kw};
    }

    ControlCommand EnergyController::decide_deficit(
        const EnergyMeasurement &measurement) const
    {
        const double requested_power_kw =
            std::abs(measurement.net_energy_kwh()) /
            measurement.interval_hours();

        const double available_discharge_energy_kwh =
            std::max(
                0.0,
                measurement.battery_state_of_charge_kwh() -
                    limits_.minimum_battery_soc_kwh());

        const double soc_limited_power_kw =
            available_discharge_energy_kwh /
            measurement.interval_hours();

        const double allowed_power_kw =
            std::min(
                {requested_power_kw,
                 limits_.max_discharge_power_kw(),
                 soc_limited_power_kw});

        if (allowed_power_kw <= 0.0)
        {
            return create_idle_command(measurement);
        }

        return ControlCommand{
            measurement.step_number(),
            ControlAction::DischargeBattery,
            allowed_power_kw};
    }

    ControlCommand EnergyController::create_idle_command(
        const EnergyMeasurement &measurement) const
    {
        return ControlCommand{
            measurement.step_number(),
            ControlAction::Idle,
            0.0};
    }

}
