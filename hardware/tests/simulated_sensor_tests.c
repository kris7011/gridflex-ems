#include <math.h>
#include <stddef.h>
#include <stdio.h>

#include "gridflex/hardware/simulated_sensor.h"

static int failures = 0;

static void expect_true(
    int condition,
    const char *message)
{
    if (!condition)
    {
        fprintf(
            stderr,
            "FAIL: %s\n",
            message);

        ++failures;
    }
}

static void test_sensor_can_be_initialized(void)
{
    GridFlexSimulatedSensor simulated_sensor;

    const GridFlexSensorStatus status =
        gridflex_simulated_sensor_init(
            &simulated_sensor,
            GRIDFLEX_SENSOR_TYPE_BATTERY_SOC,
            72.5);

    expect_true(
        status == GRIDFLEX_SENSOR_STATUS_OK,
        "valid simulated sensor should initialize");

    expect_true(
        simulated_sensor.type ==
            GRIDFLEX_SENSOR_TYPE_BATTERY_SOC,
        "initialized sensor should preserve type");

    expect_true(
        simulated_sensor.value == 72.5,
        "initialized sensor should preserve value");

    expect_true(
        simulated_sensor.read_failure_enabled == 0,
        "initialized sensor should not fail reads");

    expect_true(
        simulated_sensor.read_count == 0,
        "initialized sensor should have zero reads");
}

static void test_null_sensor_initialization_is_rejected(void)
{
    const GridFlexSensorStatus status =
        gridflex_simulated_sensor_init(
            NULL,
            GRIDFLEX_SENSOR_TYPE_BATTERY_SOC,
            72.5);

    expect_true(
        status ==
            GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT,
        "null simulated sensor should be rejected");
}

static void test_unknown_sensor_type_is_rejected(void)
{
    GridFlexSimulatedSensor simulated_sensor;

    const GridFlexSensorStatus status =
        gridflex_simulated_sensor_init(
            &simulated_sensor,
            GRIDFLEX_SENSOR_TYPE_UNKNOWN,
            72.5);

    expect_true(
        status ==
            GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT,
        "unknown simulated sensor type should be rejected");
}

static void test_non_finite_initial_values_are_rejected(void)
{
    const double invalid_values[] = {
        NAN,
        INFINITY,
        -INFINITY};

    const size_t value_count =
        sizeof(invalid_values) /
        sizeof(invalid_values[0]);

    size_t index;

    for (index = 0; index < value_count; ++index)
    {
        GridFlexSimulatedSensor simulated_sensor;

        const GridFlexSensorStatus status =
            gridflex_simulated_sensor_init(
                &simulated_sensor,
                GRIDFLEX_SENSOR_TYPE_GRID_POWER,
                invalid_values[index]);

        expect_true(
            status ==
                GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT,
            "non-finite initial value should be rejected");
    }
}

static void test_simulated_sensor_can_be_read_through_generic_interface(void)
{
    GridFlexSimulatedSensor simulated_sensor;

    GridFlexSensorStatus status =
        gridflex_simulated_sensor_init(
            &simulated_sensor,
            GRIDFLEX_SENSOR_TYPE_SOLAR_POWER,
            18.75);

    expect_true(
        status == GRIDFLEX_SENSOR_STATUS_OK,
        "simulated sensor initialization should succeed");

    GridFlexSensor sensor =
        gridflex_simulated_sensor_as_sensor(
            &simulated_sensor);

    GridFlexSensorReading reading = {
        GRIDFLEX_SENSOR_TYPE_UNKNOWN,
        0.0};

    status =
        gridflex_sensor_read(
            &sensor,
            &reading);

    expect_true(
        status == GRIDFLEX_SENSOR_STATUS_OK,
        "generic sensor read should succeed");

    expect_true(
        reading.type ==
            GRIDFLEX_SENSOR_TYPE_SOLAR_POWER,
        "generic reading should preserve simulated sensor type");

    expect_true(
        reading.value == 18.75,
        "generic reading should contain simulated value");

    expect_true(
        simulated_sensor.read_count == 1,
        "successful read should increment read count");
}

static void test_sensor_value_can_change_between_reads(void)
{
    GridFlexSimulatedSensor simulated_sensor;

    GridFlexSensorStatus status =
        gridflex_simulated_sensor_init(
            &simulated_sensor,
            GRIDFLEX_SENSOR_TYPE_TEMPERATURE,
            20.0);

    expect_true(
        status == GRIDFLEX_SENSOR_STATUS_OK,
        "simulated sensor initialization should succeed");

    GridFlexSensor sensor =
        gridflex_simulated_sensor_as_sensor(
            &simulated_sensor);

    GridFlexSensorReading reading = {
        GRIDFLEX_SENSOR_TYPE_UNKNOWN,
        0.0};

    status =
        gridflex_sensor_read(
            &sensor,
            &reading);

    expect_true(
        status == GRIDFLEX_SENSOR_STATUS_OK,
        "first simulated read should succeed");

    expect_true(
        reading.value == 20.0,
        "first read should return initial value");

    status =
        gridflex_simulated_sensor_set_value(
            &simulated_sensor,
            24.5);

    expect_true(
        status == GRIDFLEX_SENSOR_STATUS_OK,
        "updating simulated value should succeed");

    status =
        gridflex_sensor_read(
            &sensor,
            &reading);

    expect_true(
        status == GRIDFLEX_SENSOR_STATUS_OK,
        "second simulated read should succeed");

    expect_true(
        reading.value == 24.5,
        "second read should return updated value");

    expect_true(
        simulated_sensor.read_count == 2,
        "two reads should produce read count of two");
}

static void test_non_finite_updated_values_are_rejected(void)
{
    const double invalid_values[] = {
        NAN,
        INFINITY,
        -INFINITY};

    const size_t value_count =
        sizeof(invalid_values) /
        sizeof(invalid_values[0]);

    GridFlexSimulatedSensor simulated_sensor;

    GridFlexSensorStatus status =
        gridflex_simulated_sensor_init(
            &simulated_sensor,
            GRIDFLEX_SENSOR_TYPE_GRID_POWER,
            10.0);

    expect_true(
        status == GRIDFLEX_SENSOR_STATUS_OK,
        "simulated sensor initialization should succeed");

    size_t index;

    for (index = 0; index < value_count; ++index)
    {
        status =
            gridflex_simulated_sensor_set_value(
                &simulated_sensor,
                invalid_values[index]);

        expect_true(
            status ==
                GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT,
            "non-finite updated value should be rejected");

        expect_true(
            simulated_sensor.value == 10.0,
            "failed value update should preserve previous value");
    }
}

static void test_read_failure_can_be_simulated(void)
{
    GridFlexSimulatedSensor simulated_sensor;

    GridFlexSensorStatus status =
        gridflex_simulated_sensor_init(
            &simulated_sensor,
            GRIDFLEX_SENSOR_TYPE_BATTERY_SOC,
            65.0);

    expect_true(
        status == GRIDFLEX_SENSOR_STATUS_OK,
        "simulated sensor initialization should succeed");

    GridFlexSensor sensor =
        gridflex_simulated_sensor_as_sensor(
            &simulated_sensor);

    status =
        gridflex_simulated_sensor_set_read_failure(
            &simulated_sensor,
            1);

    expect_true(
        status == GRIDFLEX_SENSOR_STATUS_OK,
        "enabling simulated failure should succeed");

    GridFlexSensorReading reading = {
        GRIDFLEX_SENSOR_TYPE_TEMPERATURE,
        99.0};

    status =
        gridflex_sensor_read(
            &sensor,
            &reading);

    expect_true(
        status ==
            GRIDFLEX_SENSOR_STATUS_READ_FAILED,
        "simulated read failure should be propagated");

    expect_true(
        simulated_sensor.read_count == 1,
        "failed read should increment read count");

    expect_true(
        reading.type ==
            GRIDFLEX_SENSOR_TYPE_TEMPERATURE,
        "failed read should preserve existing reading type");

    expect_true(
        reading.value == 99.0,
        "failed read should preserve existing reading value");
}

static void test_sensor_can_recover_after_failure(void)
{
    GridFlexSimulatedSensor simulated_sensor;

    GridFlexSensorStatus status =
        gridflex_simulated_sensor_init(
            &simulated_sensor,
            GRIDFLEX_SENSOR_TYPE_GRID_POWER,
            12.0);

    expect_true(
        status == GRIDFLEX_SENSOR_STATUS_OK,
        "simulated sensor initialization should succeed");

    GridFlexSensor sensor =
        gridflex_simulated_sensor_as_sensor(
            &simulated_sensor);

    status =
        gridflex_simulated_sensor_set_read_failure(
            &simulated_sensor,
            1);

    expect_true(
        status == GRIDFLEX_SENSOR_STATUS_OK,
        "enabling simulated failure should succeed");

    GridFlexSensorReading reading = {
        GRIDFLEX_SENSOR_TYPE_UNKNOWN,
        0.0};

    status =
        gridflex_sensor_read(
            &sensor,
            &reading);

    expect_true(
        status ==
            GRIDFLEX_SENSOR_STATUS_READ_FAILED,
        "read should fail while failure mode is enabled");

    status =
        gridflex_simulated_sensor_set_read_failure(
            &simulated_sensor,
            0);

    expect_true(
        status == GRIDFLEX_SENSOR_STATUS_OK,
        "disabling simulated failure should succeed");

    status =
        gridflex_sensor_read(
            &sensor,
            &reading);

    expect_true(
        status == GRIDFLEX_SENSOR_STATUS_OK,
        "sensor should recover after failure is disabled");

    expect_true(
        reading.value == 12.0,
        "recovered sensor should return current value");

    expect_true(
        simulated_sensor.read_count == 2,
        "failed and successful reads should both be counted");
}

static void test_null_simulated_sensor_view_is_safe(void)
{
    GridFlexSensor sensor =
        gridflex_simulated_sensor_as_sensor(
            NULL);

    GridFlexSensorReading reading = {
        GRIDFLEX_SENSOR_TYPE_UNKNOWN,
        0.0};

    const GridFlexSensorStatus status =
        gridflex_sensor_read(
            &sensor,
            &reading);

    expect_true(
        status ==
            GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT,
        "null simulated sensor view should produce invalid generic sensor");
}

static void test_null_configuration_updates_are_rejected(void)
{
    GridFlexSensorStatus status =
        gridflex_simulated_sensor_set_value(
            NULL,
            10.0);

    expect_true(
        status ==
            GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT,
        "null simulated sensor value update should be rejected");

    status =
        gridflex_simulated_sensor_set_read_failure(
            NULL,
            1);

    expect_true(
        status ==
            GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT,
        "null simulated sensor failure update should be rejected");
}

int main(void)
{
    test_sensor_can_be_initialized();
    test_null_sensor_initialization_is_rejected();
    test_unknown_sensor_type_is_rejected();
    test_non_finite_initial_values_are_rejected();
    test_simulated_sensor_can_be_read_through_generic_interface();
    test_sensor_value_can_change_between_reads();
    test_non_finite_updated_values_are_rejected();
    test_read_failure_can_be_simulated();
    test_sensor_can_recover_after_failure();
    test_null_simulated_sensor_view_is_safe();
    test_null_configuration_updates_are_rejected();

    if (failures != 0)
    {
        fprintf(
            stderr,
            "%d simulated sensor test(s) failed\n",
            failures);

        return 1;
    }

    puts("All C simulated sensor tests passed.");

    return 0;
}
