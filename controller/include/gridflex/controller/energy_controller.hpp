#pragma once

#include "gridflex/controller/control_command.hpp"
#include "gridflex/controller/controller_limits.hpp"
#include "gridflex/controller/energy_measurement.hpp"

namespace gridflex::controller
{

    class EnergyController final
    {
    public:
        explicit EnergyController(const ControllerLimits &limits);

        [[nodiscard]] ControlCommand decide(
            const EnergyMeasurement &measurement) const;

    private:
        [[nodiscard]] ControlCommand decide_surplus(
            const EnergyMeasurement &measurement) const;

        [[nodiscard]] ControlCommand decide_deficit(
            const EnergyMeasurement &measurement) const;

        [[nodiscard]] ControlCommand create_idle_command(
            const EnergyMeasurement &measurement) const;

        ControllerLimits limits_;
    };

}
