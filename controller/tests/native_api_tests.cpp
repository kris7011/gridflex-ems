#include "gridflex/controller/native_api.h"

#include <catch2/catch_test_macros.hpp>

#include <cstddef>
#include <cstdint>
#include <type_traits>

TEST_CASE("Native API defines stable ABI scalar types")
{
    STATIC_REQUIRE(
        sizeof(GridFlexControllerStatus) ==
        sizeof(std::int32_t));

    STATIC_REQUIRE(
        sizeof(GridFlexControllerAction) ==
        sizeof(std::int32_t));

    REQUIRE(
        GRIDFLEX_CONTROLLER_ABI_VERSION ==
        1u);

    REQUIRE(
        GRIDFLEX_CONTROLLER_STATUS_OK ==
        0);

    REQUIRE(
        GRIDFLEX_CONTROLLER_STATUS_INVALID_ARGUMENT ==
        1);

    REQUIRE(
        GRIDFLEX_CONTROLLER_STATUS_INVALID_LIMITS ==
        2);

    REQUIRE(
        GRIDFLEX_CONTROLLER_STATUS_INVALID_MEASUREMENT ==
        3);

    REQUIRE(
        GRIDFLEX_CONTROLLER_STATUS_INTERNAL_ERROR ==
        4);
}

TEST_CASE("Native API defines stable controller actions")
{
    REQUIRE(
        GRIDFLEX_CONTROLLER_ACTION_IDLE ==
        0);

    REQUIRE(
        GRIDFLEX_CONTROLLER_ACTION_CHARGE_BATTERY ==
        1);

    REQUIRE(
        GRIDFLEX_CONTROLLER_ACTION_DISCHARGE_BATTERY ==
        2);

    REQUIRE(
        GRIDFLEX_CONTROLLER_ACTION_IMPORT_FROM_GRID ==
        3);

    REQUIRE(
        GRIDFLEX_CONTROLLER_ACTION_EXPORT_TO_GRID ==
        4);
}

TEST_CASE("Native API payloads are suitable for C interoperability")
{
    STATIC_REQUIRE(
        std::is_standard_layout_v<
            GridFlexControllerLimits>);

    STATIC_REQUIRE(
        std::is_trivially_copyable_v<
            GridFlexControllerLimits>);

    STATIC_REQUIRE(
        std::is_standard_layout_v<
            GridFlexControllerMeasurement>);

    STATIC_REQUIRE(
        std::is_trivially_copyable_v<
            GridFlexControllerMeasurement>);

    STATIC_REQUIRE(
        std::is_standard_layout_v<
            GridFlexControllerDecision>);

    STATIC_REQUIRE(
        std::is_trivially_copyable_v<
            GridFlexControllerDecision>);
}

TEST_CASE("Native API controller limits have stable memory layout")
{
    STATIC_REQUIRE(
        sizeof(GridFlexControllerLimits) ==
        32);

    STATIC_REQUIRE(
        offsetof(
            GridFlexControllerLimits,
            max_charge_power_kw) ==
        0);

    STATIC_REQUIRE(
        offsetof(
            GridFlexControllerLimits,
            max_discharge_power_kw) ==
        8);

    STATIC_REQUIRE(
        offsetof(
            GridFlexControllerLimits,
            minimum_battery_soc_kwh) ==
        16);

    STATIC_REQUIRE(
        offsetof(
            GridFlexControllerLimits,
            maximum_battery_soc_kwh) ==
        24);
}

TEST_CASE("Native API measurement has stable memory layout")
{
    STATIC_REQUIRE(
        sizeof(GridFlexControllerMeasurement) ==
        80);

    STATIC_REQUIRE(
        offsetof(
            GridFlexControllerMeasurement,
            step_number) ==
        0);

    STATIC_REQUIRE(
        offsetof(
            GridFlexControllerMeasurement,
            elapsed_time_hours) ==
        8);

    STATIC_REQUIRE(
        offsetof(
            GridFlexControllerMeasurement,
            interval_hours) ==
        16);

    STATIC_REQUIRE(
        offsetof(
            GridFlexControllerMeasurement,
            generated_energy_kwh) ==
        24);

    STATIC_REQUIRE(
        offsetof(
            GridFlexControllerMeasurement,
            consumed_energy_kwh) ==
        32);

    STATIC_REQUIRE(
        offsetof(
            GridFlexControllerMeasurement,
            net_energy_kwh) ==
        40);

    STATIC_REQUIRE(
        offsetof(
            GridFlexControllerMeasurement,
            battery_state_of_charge_kwh) ==
        48);

    STATIC_REQUIRE(
        offsetof(
            GridFlexControllerMeasurement,
            grid_import_energy_kwh) ==
        56);

    STATIC_REQUIRE(
        offsetof(
            GridFlexControllerMeasurement,
            grid_export_energy_kwh) ==
        64);

    STATIC_REQUIRE(
        offsetof(
            GridFlexControllerMeasurement,
            unresolved_energy_kwh) ==
        72);
}

TEST_CASE("Native API decision has stable memory layout")
{
    STATIC_REQUIRE(
        sizeof(GridFlexControllerDecision) ==
        24);

    STATIC_REQUIRE(
        offsetof(
            GridFlexControllerDecision,
            source_step_number) ==
        0);

    STATIC_REQUIRE(
        offsetof(
            GridFlexControllerDecision,
            action) ==
        8);

    STATIC_REQUIRE(
        offsetof(
            GridFlexControllerDecision,
            requested_power_kw) ==
        16);
}
