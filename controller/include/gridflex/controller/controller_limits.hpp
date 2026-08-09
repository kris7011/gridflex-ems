#pragma once

namespace gridflex::controller
{

    class ControllerLimits final
    {
    public:
        ControllerLimits(
            double max_charge_power_kw,
            double max_discharge_power_kw,
            double minimum_battery_soc_kwh,
            double maximum_battery_soc_kwh);

        [[nodiscard]] double max_charge_power_kw() const noexcept;
        [[nodiscard]] double max_discharge_power_kw() const noexcept;
        [[nodiscard]] double minimum_battery_soc_kwh() const noexcept;
        [[nodiscard]] double maximum_battery_soc_kwh() const noexcept;

    private:
        double max_charge_power_kw_;
        double max_discharge_power_kw_;
        double minimum_battery_soc_kwh_;
        double maximum_battery_soc_kwh_;
    };

}
