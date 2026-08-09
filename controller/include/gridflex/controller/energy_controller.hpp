#pragma once

#include "gridflex/controller/control_command.hpp"
#include "gridflex/controller/energy_measurement.hpp"

namespace gridflex::controller
{

    class EnergyController final
    {
    public:
        [[nodiscard]] ControlCommand decide(
            const EnergyMeasurement &measurement) const;
    };

}
