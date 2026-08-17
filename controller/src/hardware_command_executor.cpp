#include "gridflex/controller/hardware_command_executor.hpp"

#include <stdexcept>

namespace gridflex::controller
{

HardwareExecutionResult::HardwareExecutionResult(
    const GridFlexHardwareError battery_error,
    const GridFlexHardwareError grid_error) noexcept
    : battery_error_{battery_error},
      grid_error_{grid_error}
{
}

const GridFlexHardwareError &
HardwareExecutionResult::battery_error() const noexcept
{
    return battery_error_;
}

const GridFlexHardwareError &
HardwareExecutionResult::grid_error() const noexcept
{
    return grid_error_;
}

bool HardwareExecutionResult::battery_succeeded() const noexcept
{
    return gridflex_hardware_error_is_error(
               battery_error_) == 0;
}

bool HardwareExecutionResult::grid_succeeded() const noexcept
{
    return gridflex_hardware_error_is_error(
               grid_error_) == 0;
}

bool HardwareExecutionResult::succeeded() const noexcept
{
    return battery_succeeded() &&
           grid_succeeded();
}

HardwareCommandExecutor::HardwareCommandExecutor(
    const GridFlexActuator battery_actuator,
    const GridFlexActuator grid_actuator)
    : battery_actuator_{battery_actuator},
      grid_actuator_{grid_actuator}
{
    if (
        battery_actuator_.type !=
        GRIDFLEX_ACTUATOR_TYPE_BATTERY)
    {
        throw std::invalid_argument(
            "Hardware command executor requires a battery actuator.");
    }

    if (
        grid_actuator_.type !=
        GRIDFLEX_ACTUATOR_TYPE_GRID_CONNECTION)
    {
        throw std::invalid_argument(
            "Hardware command executor requires a grid connection actuator.");
    }
}

HardwareExecutionResult HardwareCommandExecutor::execute(
    const ControlCommand &command) const
{
    const GridFlexActuatorCommand battery_command =
        create_battery_command(command);

    const GridFlexActuatorCommand grid_command =
        create_grid_command(command);

    const GridFlexActuatorStatus battery_status =
        gridflex_actuator_apply(
            &battery_actuator_,
            &battery_command);

    const GridFlexActuatorStatus grid_status =
        gridflex_actuator_apply(
            &grid_actuator_,
            &grid_command);

    return HardwareExecutionResult{
        gridflex_hardware_error_from_actuator_apply(
            battery_actuator_.type,
            battery_status),
        gridflex_hardware_error_from_actuator_apply(
            grid_actuator_.type,
            grid_status)};
}

GridFlexActuatorCommand
HardwareCommandExecutor::create_battery_command(
    const ControlCommand &command)
{
    switch (command.action())
    {
    case ControlAction::Idle:
        return GridFlexActuatorCommand{
            GRIDFLEX_ACTUATOR_ACTION_IDLE,
            0.0};

    case ControlAction::ChargeBattery:
        return GridFlexActuatorCommand{
            GRIDFLEX_ACTUATOR_ACTION_CHARGE,
            command.requested_power_kw()};

    case ControlAction::DischargeBattery:
        return GridFlexActuatorCommand{
            GRIDFLEX_ACTUATOR_ACTION_DISCHARGE,
            command.requested_power_kw()};

    case ControlAction::ImportFromGrid:
    case ControlAction::ExportToGrid:
        return GridFlexActuatorCommand{
            GRIDFLEX_ACTUATOR_ACTION_IDLE,
            0.0};

    default:
        throw std::invalid_argument(
            "Unsupported control action.");
    }
}

GridFlexActuatorCommand
HardwareCommandExecutor::create_grid_command(
    const ControlCommand &command)
{
    switch (command.action())
    {
    case ControlAction::Idle:
    case ControlAction::ChargeBattery:
    case ControlAction::DischargeBattery:
        return GridFlexActuatorCommand{
            GRIDFLEX_ACTUATOR_ACTION_IDLE,
            0.0};

    case ControlAction::ImportFromGrid:
        return GridFlexActuatorCommand{
            GRIDFLEX_ACTUATOR_ACTION_IMPORT,
            command.requested_power_kw()};

    case ControlAction::ExportToGrid:
        return GridFlexActuatorCommand{
            GRIDFLEX_ACTUATOR_ACTION_EXPORT,
            command.requested_power_kw()};

    default:
        throw std::invalid_argument(
            "Unsupported control action.");
    }
}

} // namespace gridflex::controller
