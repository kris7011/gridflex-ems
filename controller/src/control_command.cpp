#include "gridflex/controller/control_command.hpp"

#include <cmath>
#include <stdexcept>

namespace gridflex::controller
{

    ControlCommand::ControlCommand(
        const std::uint64_t source_step_number,
        const ControlAction action,
        const double requested_power_kw)
        : source_step_number_{source_step_number},
          action_{action},
          requested_power_kw_{requested_power_kw}
    {
        if (source_step_number_ == 0)
        {
            throw std::invalid_argument(
                "Control command source step number must be greater than zero.");
        }

        if (!std::isfinite(requested_power_kw_))
        {
            throw std::invalid_argument(
                "Requested control power must be a finite number.");
        }

        if (requested_power_kw_ < 0.0)
        {
            throw std::invalid_argument(
                "Requested control power cannot be negative.");
        }

        if (
            action_ == ControlAction::Idle &&
            requested_power_kw_ != 0.0)
        {
            throw std::invalid_argument(
                "An idle control command must request zero power.");
        }

        if (
            action_ != ControlAction::Idle &&
            requested_power_kw_ == 0.0)
        {
            throw std::invalid_argument(
                "An active control command must request power greater than zero.");
        }
    }

    std::uint64_t ControlCommand::source_step_number() const noexcept
    {
        return source_step_number_;
    }

    ControlAction ControlCommand::action() const noexcept
    {
        return action_;
    }

    double ControlCommand::requested_power_kw() const noexcept
    {
        return requested_power_kw_;
    }

    bool ControlCommand::is_idle() const noexcept
    {
        return action_ == ControlAction::Idle;
    }

}