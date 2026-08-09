#include "gridflex/controller/energy_measurement.hpp"

#include <cmath>
#include <stdexcept>
#include <string>
#include <string_view>

namespace
{

    void validate_positive_finite(
        const double value,
        const std::string_view name)
    {
        if (!std::isfinite(value))
        {
            throw std::invalid_argument(
                std::string{name} + " must be a finite number.");
        }

        if (value <= 0.0)
        {
            throw std::invalid_argument(
                std::string{name} + " must be greater than zero.");
        }
    }

    void validate_non_negative_finite(
        const double value,
        const std::string_view name)
    {
        if (!std::isfinite(value))
        {
            throw std::invalid_argument(
                std::string{name} + " must be a finite number.");
        }

        if (value < 0.0)
        {
            throw std::invalid_argument(
                std::string{name} + " cannot be negative.");
        }
    }

}

namespace gridflex::controller
{

    EnergyMeasurement::EnergyMeasurement(
        const std::uint64_t step_number,
        const double elapsed_time_hours,
        const double interval_hours,
        const double generated_energy_kwh,
        const double consumed_energy_kwh,
        const double net_energy_kwh,
        const double battery_state_of_charge_kwh,
        const double grid_import_energy_kwh,
        const double grid_export_energy_kwh,
        const double unresolved_energy_kwh)
        : step_number_{step_number},
          elapsed_time_hours_{elapsed_time_hours},
          interval_hours_{interval_hours},
          generated_energy_kwh_{generated_energy_kwh},
          consumed_energy_kwh_{consumed_energy_kwh},
          net_energy_kwh_{net_energy_kwh},
          battery_state_of_charge_kwh_{battery_state_of_charge_kwh},
          grid_import_energy_kwh_{grid_import_energy_kwh},
          grid_export_energy_kwh_{grid_export_energy_kwh},
          unresolved_energy_kwh_{unresolved_energy_kwh}
    {
        if (step_number_ == 0)
        {
            throw std::invalid_argument(
                "Measurement step number must be greater than zero.");
        }

        validate_positive_finite(
            elapsed_time_hours_,
            "Elapsed time");

        validate_positive_finite(
            interval_hours_,
            "Measurement interval");

        validate_non_negative_finite(
            generated_energy_kwh_,
            "Generated energy");

        validate_non_negative_finite(
            consumed_energy_kwh_,
            "Consumed energy");

        if (!std::isfinite(net_energy_kwh_))
        {
            throw std::invalid_argument(
                "Net energy must be a finite number.");
        }

        validate_non_negative_finite(
            battery_state_of_charge_kwh_,
            "Battery state of charge");

        validate_non_negative_finite(
            grid_import_energy_kwh_,
            "Grid import energy");

        validate_non_negative_finite(
            grid_export_energy_kwh_,
            "Grid export energy");

        validate_non_negative_finite(
            unresolved_energy_kwh_,
            "Unresolved energy");

        if (
            grid_import_energy_kwh_ > 0.0 &&
            grid_export_energy_kwh_ > 0.0)
        {
            throw std::invalid_argument(
                "A measurement cannot contain both grid import "
                "and grid export energy.");
        }
    }

    std::uint64_t EnergyMeasurement::step_number() const noexcept
    {
        return step_number_;
    }

    double EnergyMeasurement::elapsed_time_hours() const noexcept
    {
        return elapsed_time_hours_;
    }

    double EnergyMeasurement::interval_hours() const noexcept
    {
        return interval_hours_;
    }

    double EnergyMeasurement::generated_energy_kwh() const noexcept
    {
        return generated_energy_kwh_;
    }

    double EnergyMeasurement::consumed_energy_kwh() const noexcept
    {
        return consumed_energy_kwh_;
    }

    double EnergyMeasurement::net_energy_kwh() const noexcept
    {
        return net_energy_kwh_;
    }

    double EnergyMeasurement::battery_state_of_charge_kwh() const noexcept
    {
        return battery_state_of_charge_kwh_;
    }

    double EnergyMeasurement::grid_import_energy_kwh() const noexcept
    {
        return grid_import_energy_kwh_;
    }

    double EnergyMeasurement::grid_export_energy_kwh() const noexcept
    {
        return grid_export_energy_kwh_;
    }

    double EnergyMeasurement::unresolved_energy_kwh() const noexcept
    {
        return unresolved_energy_kwh_;
    }

    double EnergyMeasurement::grid_net_energy_kwh() const noexcept
    {
        return grid_import_energy_kwh_ - grid_export_energy_kwh_;
    }

}
