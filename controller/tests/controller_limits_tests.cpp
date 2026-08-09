#include <catch2/catch_test_macros.hpp>

#include <limits>
#include <stdexcept>

#include "gridflex/controller/controller_limits.hpp"

using gridflex::controller::ControllerLimits;

TEST_CASE("Controller limits preserve valid configuration")
{
    const ControllerLimits limits{
        25.0,
        30.0,
        10.0,
        90.0};

    REQUIRE(limits.max_charge_power_kw() == 25.0);
    REQUIRE(limits.max_discharge_power_kw() == 30.0);
    REQUIRE(limits.minimum_battery_soc_kwh() == 10.0);
    REQUIRE(limits.maximum_battery_soc_kwh() == 90.0);
}

TEST_CASE("Controller limits reject non-positive maximum charge power")
{
    REQUIRE_THROWS_AS(
        (
            ControllerLimits{
                0.0,
                30.0,
                10.0,
                90.0}),
        std::invalid_argument);
}

TEST_CASE("Controller limits reject non-positive maximum discharge power")
{
    REQUIRE_THROWS_AS(
        (
            ControllerLimits{
                25.0,
                -1.0,
                10.0,
                90.0}),
        std::invalid_argument);
}

TEST_CASE("Controller limits reject negative minimum battery state of charge")
{
    REQUIRE_THROWS_AS(
        (
            ControllerLimits{
                25.0,
                30.0,
                -1.0,
                90.0}),
        std::invalid_argument);
}

TEST_CASE("Controller limits reject equal battery state of charge boundaries")
{
    REQUIRE_THROWS_AS(
        (
            ControllerLimits{
                25.0,
                30.0,
                50.0,
                50.0}),
        std::invalid_argument);
}

TEST_CASE("Controller limits reject reversed battery state of charge boundaries")
{
    REQUIRE_THROWS_AS(
        (
            ControllerLimits{
                25.0,
                30.0,
                80.0,
                20.0}),
        std::invalid_argument);
}

TEST_CASE("Controller limits reject non-finite configuration values")
{
    const auto infinity =
        std::numeric_limits<double>::infinity();

    const auto not_a_number =
        std::numeric_limits<double>::quiet_NaN();

    REQUIRE_THROWS_AS(
        (
            ControllerLimits{
                infinity,
                30.0,
                10.0,
                90.0}),
        std::invalid_argument);

    REQUIRE_THROWS_AS(
        (
            ControllerLimits{
                25.0,
                30.0,
                10.0,
                not_a_number}),
        std::invalid_argument);
}
