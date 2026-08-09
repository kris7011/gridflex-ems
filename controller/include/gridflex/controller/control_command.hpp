#pragma once

#include <cstdint>

namespace gridflex::controller
{

    enum class ControlAction
    {
        Idle,
        ChargeBattery,
        DischargeBattery,
        ImportFromGrid,
        ExportToGrid
    };

    class ControlCommand final
    {
    public:
        ControlCommand(
            std::uint64_t source_step_number,
            ControlAction action,
            double requested_power_kw);

        [[nodiscard]] std::uint64_t source_step_number() const noexcept;
        [[nodiscard]] ControlAction action() const noexcept;
        [[nodiscard]] double requested_power_kw() const noexcept;
        [[nodiscard]] bool is_idle() const noexcept;

    private:
        std::uint64_t source_step_number_;
        ControlAction action_;
        double requested_power_kw_;
    };

}