#include <catch2/catch_test_macros.hpp>

#include <cstdint>

#include "gridflex/controller/control_command.hpp"
#include "gridflex/controller/energy_controller.hpp"
#include "gridflex/controller/energy_measurement.hpp"

namespace
{

    using gridflex::controller::ControlAction;
    using gridflex::controller::EnergyController;
    using gridflex::controller::EnergyMeasurement;

    EnergyMeasurement create_measurement(
        const std::uint64_t step_number,
        const double interval_hours,
        const double net_energy_kwh)
    {
        const double generated_energy_kwh =
            net_energy_kwh >= 0.0
                ? 50.0 + net_energy_kwh
                : 50.0;

        const double consumed_energy_kwh =
            net_energy_kwh >= 0.0
                ? 50.0
                : 50.0 - net_energy_kwh;

        return EnergyMeasurement{
            step_number,
            1.0,
            interval_hours,
            generated_energy_kwh,
            consumed_energy_kwh,
            net_energy_kwh,
            40.0,
            0.0,
            0.0,
            0.0};
    }

}

TEST_CASE("Energy controller charges battery during energy surplus")
{
    const EnergyController controller;

    const auto measurement =
        create_measurement(
            1,
            1.0,
            10.5);

    const auto command = controller.decide(measurement);

    REQUIRE(command.source_step_number() == 1);
    REQUIRE(command.action() == ControlAction::ChargeBattery);
    REQUIRE(command.requested_power_kw() == 10.5);
    REQUIRE_FALSE(command.is_idle());
}

TEST_CASE("Energy controller discharges battery during energy deficit")
{
    const EnergyController controller;

    const auto measurement =
        create_measurement(
            2,
            1.0,
            -12.0);

    const auto command = controller.decide(measurement);

    REQUIRE(command.source_step_number() == 2);
    REQUIRE(command.action() == ControlAction::DischargeBattery);
    REQUIRE(command.requested_power_kw() == 12.0);
    REQUIRE_FALSE(command.is_idle());
}

TEST_CASE("Energy controller idles when energy is balanced")
{
    const EnergyController controller;

    const auto measurement =
        create_measurement(
            3,
            1.0,
            0.0);

    const auto command = controller.decide(measurement);

    REQUIRE(command.source_step_number() == 3);
    REQUIRE(command.action() == ControlAction::Idle);
    REQUIRE(command.requested_power_kw() == 0.0);
    REQUIRE(command.is_idle());
}

TEST_CASE("Energy controller converts interval energy to requested power")
{
    const EnergyController controller;

    const auto measurement =
        create_measurement(
            4,
            0.5,
            10.0);

    const auto command = controller.decide(measurement);

    REQUIRE(command.action() == ControlAction::ChargeBattery);
    REQUIRE(command.requested_power_kw() == 20.0);
}

TEST_CASE("Energy controller treats tiny positive residual as balanced")
{
    const EnergyController controller;

    const auto measurement =
        create_measurement(
            5,
            1.0,
            0.5e-9);

    const auto command = controller.decide(measurement);

    REQUIRE(command.action() == ControlAction::Idle);
    REQUIRE(command.requested_power_kw() == 0.0);
}

TEST_CASE("Energy controller treats tiny negative residual as balanced")
{
    const EnergyController controller;

    const auto measurement =
        create_measurement(
            6,
            1.0,
            -0.5e-9);

    const auto command = controller.decide(measurement);

    REQUIRE(command.action() == ControlAction::Idle);
    REQUIRE(command.requested_power_kw() == 0.0);
}

TEST_CASE("Energy controller reacts when surplus exceeds balance tolerance")
{
    const EnergyController controller;

    const auto measurement =
        create_measurement(
            42,
            1.0,
            1.1e-9);

    const auto command = controller.decide(measurement);

    REQUIRE(command.source_step_number() == 42);
    REQUIRE(command.action() == ControlAction::ChargeBattery);
    REQUIRE(command.requested_power_kw() == 1.1e-9);
}
