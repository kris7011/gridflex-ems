#include "gridflex/controller/controller_limits.hpp"

#include <cmath>
#include <stdexcept>

namespace gridflex::controller
{

    ControllerLimits::ControllerLimits(
        const double max_charge_power_kw,
        const double max_discharge_power_kw,
        const double minimum_battery_soc_kwh,
        const double maximum_battery_soc_kwh)
        : max_charge_power_kw_{max_charge_power_kw},
          max_discharge_power_kw_{max_discharge_power_kw},
          minimum_battery_soc_kwh_{minimum_battery_soc_kwh},
          maximum_battery_soc_kwh_{maximum_battery_soc_kwh}
    {
        if (
            !std::isfinite(max_charge_power_kw_) ||
            max_charge_power_kw_ <= 0.0)
        {
            throw std::invalid_argument(
                "Maximum charge power must be finite and greater than zero.");
        }

        if (
            !std::isfinite(max_discharge_power_kw_) ||
            max_discharge_power_kw_ <= 0.0)
        {
            throw std::invalid_argument(
                "Maximum discharge power must be finite and greater than zero.");
        }

        if (
            !std::isfinite(minimum_battery_soc_kwh_) ||
            minimum_battery_soc_kwh_ < 0.0)
        {
            throw std::invalid_argument(
                "Minimum battery state of charge must be finite and non-negative.");
        }

        if (!std::isfinite(maximum_battery_soc_kwh_))
        {
            throw std::invalid_argument(
                "Maximum battery state of charge must be finite.");
        }

        if (maximum_battery_soc_kwh_ <= minimum_battery_soc_kwh_)
        {
            throw std::invalid_argument(
                "Maximum battery state of charge must be greater than the minimum.");
        }
    }

    double ControllerLimits::max_charge_power_kw() const noexcept
    {
        return max_charge_power_kw_;
    }

    double ControllerLimits::max_discharge_power_kw() const noexcept
    {
        return max_discharge_power_kw_;
    }

    double ControllerLimits::minimum_battery_soc_kwh() const noexcept
    {
        return minimum_battery_soc_kwh_;
    }

    double ControllerLimits::maximum_battery_soc_kwh() const noexcept
    {
        return maximum_battery_soc_kwh_;
    }

}
