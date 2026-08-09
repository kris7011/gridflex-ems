#include <catch2/catch_test_macros.hpp>

#include <limits>
#include <stdexcept>

#include "gridflex/controller/control_command.hpp"

using gridflex::controller::ControlAction;
using gridflex::controller::ControlCommand;

TEST_CASE("Control command preserves active command values")
{
    const ControlCommand command{
        42,
        ControlAction::ChargeBattery,
        25.0};

    REQUIRE(command.source_step_number() == 42);
    REQUIRE(command.action() == ControlAction::ChargeBattery);
    REQUIRE(command.requested_power_kw() == 25.0);
    REQUIRE_FALSE(command.is_idle());
}

TEST_CASE("Control command supports idle with zero power")
{
    const ControlCommand command{
        7,
        ControlAction::Idle,
        0.0};

    REQUIRE(command.source_step_number() == 7);
    REQUIRE(command.action() == ControlAction::Idle);
    REQUIRE(command.requested_power_kw() == 0.0);
    REQUIRE(command.is_idle());
}

TEST_CASE("Control command rejects zero source step number")
{
    REQUIRE_THROWS_AS(
        (
            ControlCommand{
                0,
                ControlAction::ChargeBattery,
                10.0}),
        std::invalid_argument);
}

TEST_CASE("Control command rejects negative power")
{
    REQUIRE_THROWS_AS(
        (
            ControlCommand{
                1,
                ControlAction::ChargeBattery,
                -10.0}),
        std::invalid_argument);
}

TEST_CASE("Control command rejects non-finite power")
{
    const auto infinity = std::numeric_limits<double>::infinity();

    REQUIRE_THROWS_AS(
        (
            ControlCommand{
                1,
                ControlAction::ChargeBattery,
                infinity}),
        std::invalid_argument);
}

TEST_CASE("Control command rejects idle command with requested power")
{
    REQUIRE_THROWS_AS(
        (
            ControlCommand{
                1,
                ControlAction::Idle,
                10.0}),
        std::invalid_argument);
}

TEST_CASE("Control command rejects active command with zero power")
{
    REQUIRE_THROWS_AS(
        (
            ControlCommand{
                1,
                ControlAction::DischargeBattery,
                0.0}),
        std::invalid_argument);
}