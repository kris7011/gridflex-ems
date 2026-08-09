#pragma once

#include <cstdint>

namespace gridflex::controller
{

    class EnergyMeasurement final
    {
    public:
        EnergyMeasurement(
            std::uint64_t step_number,
            double elapsed_time_hours,
            double interval_hours,
            double generated_energy_kwh,
            double consumed_energy_kwh,
            double net_energy_kwh,
            double battery_state_of_charge_kwh,
            double grid_import_energy_kwh,
            double grid_export_energy_kwh,
            double unresolved_energy_kwh);

        [[nodiscard]] std::uint64_t step_number() const noexcept;
        [[nodiscard]] double elapsed_time_hours() const noexcept;
        [[nodiscard]] double interval_hours() const noexcept;
        [[nodiscard]] double generated_energy_kwh() const noexcept;
        [[nodiscard]] double consumed_energy_kwh() const noexcept;
        [[nodiscard]] double net_energy_kwh() const noexcept;
        [[nodiscard]] double battery_state_of_charge_kwh() const noexcept;
        [[nodiscard]] double grid_import_energy_kwh() const noexcept;
        [[nodiscard]] double grid_export_energy_kwh() const noexcept;
        [[nodiscard]] double unresolved_energy_kwh() const noexcept;

        [[nodiscard]] double grid_net_energy_kwh() const noexcept;

    private:
        std::uint64_t step_number_;
        double elapsed_time_hours_;
        double interval_hours_;
        double generated_energy_kwh_;
        double consumed_energy_kwh_;
        double net_energy_kwh_;
        double battery_state_of_charge_kwh_;
        double grid_import_energy_kwh_;
        double grid_export_energy_kwh_;
        double unresolved_energy_kwh_;
    };

}