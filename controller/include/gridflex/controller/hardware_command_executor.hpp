#pragma once

#include "gridflex/controller/control_command.hpp"
#include "gridflex/hardware/actuator.h"
#include "gridflex/hardware/error.h"

namespace gridflex::controller
{

    class HardwareExecutionResult final
    {
    public:
        HardwareExecutionResult(
            GridFlexHardwareError battery_error,
            GridFlexHardwareError grid_error) noexcept;

        [[nodiscard]] const GridFlexHardwareError &battery_error() const noexcept;
        [[nodiscard]] const GridFlexHardwareError &grid_error() const noexcept;

        [[nodiscard]] bool battery_succeeded() const noexcept;
        [[nodiscard]] bool grid_succeeded() const noexcept;
        [[nodiscard]] bool succeeded() const noexcept;

    private:
        GridFlexHardwareError battery_error_;
        GridFlexHardwareError grid_error_;
    };

    class HardwareCommandExecutor final
    {
    public:
        HardwareCommandExecutor(
            GridFlexActuator battery_actuator,
            GridFlexActuator grid_actuator);

        [[nodiscard]] HardwareExecutionResult execute(
            const ControlCommand &command) const;

    private:
        [[nodiscard]] static GridFlexActuatorCommand create_battery_command(
            const ControlCommand &command);

        [[nodiscard]] static GridFlexActuatorCommand create_grid_command(
            const ControlCommand &command);

        GridFlexActuator battery_actuator_;
        GridFlexActuator grid_actuator_;
    };

}
