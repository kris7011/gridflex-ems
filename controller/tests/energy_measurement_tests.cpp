#include <catch2/catch_test_macros.hpp>

#include <limits>
#include <stdexcept>

#include "gridflex/controller/energy_measurement.hpp"

namespace
{

    using gridflex::controller::EnergyMeasurement;

    EnergyMeasurement create_valid_measurement()
    {
        return EnergyMeasurement{
            1,
            1.0,
            1.0,
            76.5,
            66.0,
            10.5,
            50.5,
            0.0,
            0.0,
            0.0};
    }

}

TEST_CASE("Energy measurement preserves valid input values")
{
    const auto measurement = create_valid_measurement();

    REQUIRE(measurement.step_number() == 1);
    REQUIRE(measurement.elapsed_time_hours() == 1.0);
    REQUIRE(measurement.interval_hours() == 1.0);
    REQUIRE(measurement.generated_energy_kwh() == 76.5);
    REQUIRE(measurement.consumed_energy_kwh() == 66.0);
    REQUIRE(measurement.net_energy_kwh() == 10.5);
    REQUIRE(measurement.battery_state_of_charge_kwh() == 50.5);
    REQUIRE(measurement.grid_import_energy_kwh() == 0.0);
    REQUIRE(measurement.grid_export_energy_kwh() == 0.0);
    REQUIRE(measurement.unresolved_energy_kwh() == 0.0);
}

TEST_CASE("Energy measurement calculates signed grid import")
{
    const EnergyMeasurement measurement{
        1,
        1.0,
        1.0,
        20.0,
        30.0,
        -10.0,
        40.0,
        10.0,
        0.0,
        0.0};

    REQUIRE(measurement.grid_net_energy_kwh() == 10.0);
}

TEST_CASE("Energy measurement calculates signed grid export")
{
    const EnergyMeasurement measurement{
        1,
        1.0,
        1.0,
        40.0,
        20.0,
        20.0,
        60.0,
        0.0,
        12.0,
        0.0};

    REQUIRE(measurement.grid_net_energy_kwh() == -12.0);
}

TEST_CASE("Energy measurement rejects zero step number")
{
    REQUIRE_THROWS_AS(
        (
            EnergyMeasurement{
                0,
                1.0,
                1.0,
                20.0,
                20.0,
                0.0,
                40.0,
                0.0,
                0.0,
                0.0}),
        std::invalid_argument);
}

TEST_CASE("Energy measurement rejects non-positive interval")
{
    REQUIRE_THROWS_AS(
        (
            EnergyMeasurement{
                1,
                1.0,
                0.0,
                20.0,
                20.0,
                0.0,
                40.0,
                0.0,
                0.0,
                0.0}),
        std::invalid_argument);
}

TEST_CASE("Energy measurement rejects negative energy")
{
    REQUIRE_THROWS_AS(
        (
            EnergyMeasurement{
                1,
                1.0,
                1.0,
                -1.0,
                20.0,
                -21.0,
                40.0,
                0.0,
                0.0,
                0.0}),
        std::invalid_argument);
}

TEST_CASE("Energy measurement rejects non-finite values")
{
    const auto infinity = std::numeric_limits<double>::infinity();

    REQUIRE_THROWS_AS(
        (
            EnergyMeasurement{
                1,
                1.0,
                1.0,
                infinity,
                20.0,
                0.0,
                40.0,
                0.0,
                0.0,
                0.0}),
        std::invalid_argument);
}

TEST_CASE("Energy measurement rejects simultaneous grid import and export")
{
    REQUIRE_THROWS_AS(
        (
            EnergyMeasurement{
                1,
                1.0,
                1.0,
                20.0,
                20.0,
                0.0,
                40.0,
                5.0,
                3.0,
                0.0}),
        std::invalid_argument);
}
TEST_CASE("Energy measurement rejects net energy that contradicts generation and consumption")
{
    REQUIRE_THROWS_AS(
        (
            EnergyMeasurement{
                1,
                1.0,
                1.0,
                5.0,
                2.0,
                -3.0,
                10.0,
                0.0,
                0.0,
                0.0}),
        std::invalid_argument);

    REQUIRE_THROWS_AS(
        (
            EnergyMeasurement{
                1,
                1.0,
                1.0,
                5.0,
                2.0,
                3.01,
                10.0,
                0.0,
                0.0,
                0.0}),
        std::invalid_argument);
}

TEST_CASE("Energy measurement tolerates floating-point rounding in net energy")
{
    // 5.1 - 2.3 is 2.7999999999999998 in binary floating point.
    const EnergyMeasurement rounded{
        1,
        1.0,
        1.0,
        5.1,
        2.3,
        2.8,
        10.0,
        0.0,
        0.0,
        0.0};

    REQUIRE(rounded.net_energy_kwh() == 2.8);

    // The simulation snaps a balance within 1e-9 kWh to exactly zero.
    const EnergyMeasurement snapped{
        1,
        1.0,
        1.0,
        2.0 + 5.0e-10,
        2.0,
        0.0,
        10.0,
        0.0,
        0.0,
        0.0};

    REQUIRE(snapped.net_energy_kwh() == 0.0);
}
