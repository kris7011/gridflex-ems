#include <stddef.h>
#include <stdio.h>

#include "gridflex/hardware/error.h"

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

static void test_sensor_statuses_are_normalized(void)
{
    typedef struct SensorStatusCase
    {
        GridFlexSensorStatus status;
        GridFlexHardwareErrorCode expected_code;
    } SensorStatusCase;

    const SensorStatusCase cases[] = {
        {GRIDFLEX_SENSOR_STATUS_OK,
         GRIDFLEX_HARDWARE_ERROR_NONE},
        {GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT,
         GRIDFLEX_HARDWARE_ERROR_INVALID_ARGUMENT},
        {GRIDFLEX_SENSOR_STATUS_NOT_CONFIGURED,
         GRIDFLEX_HARDWARE_ERROR_NOT_CONFIGURED},
        {GRIDFLEX_SENSOR_STATUS_READ_FAILED,
         GRIDFLEX_HARDWARE_ERROR_OPERATION_FAILED}};

    const size_t case_count =
        sizeof(cases) /
        sizeof(cases[0]);

    size_t index;

    for (index = 0; index < case_count; ++index)
    {
        const GridFlexHardwareError error =
            gridflex_hardware_error_from_sensor_read(
                GRIDFLEX_SENSOR_TYPE_GRID_POWER,
                cases[index].status);

        expect_true(
            error.source ==
                GRIDFLEX_HARDWARE_ERROR_SOURCE_SENSOR,
            "sensor error should preserve sensor source");

        expect_true(
            error.operation ==
                GRIDFLEX_HARDWARE_OPERATION_READ,
            "sensor error should preserve read operation");

        expect_true(
            error.code ==
                cases[index].expected_code,
            "sensor status should map to expected hardware error code");

        expect_true(
            error.sensor_type ==
                GRIDFLEX_SENSOR_TYPE_GRID_POWER,
            "sensor error should preserve sensor type");

        expect_true(
            error.actuator_type ==
                GRIDFLEX_ACTUATOR_TYPE_UNKNOWN,
            "sensor error should not contain an actuator type");
    }
}

static void test_unknown_sensor_status_is_preserved_as_error(void)
{
    const GridFlexHardwareError error =
        gridflex_hardware_error_from_sensor_read(
            GRIDFLEX_SENSOR_TYPE_TEMPERATURE,
            (GridFlexSensorStatus)999);

    expect_true(
        error.code ==
            GRIDFLEX_HARDWARE_ERROR_UNKNOWN_STATUS,
        "unknown sensor status should map to unknown hardware status");

    expect_true(
        gridflex_hardware_error_is_error(error),
        "unknown sensor status should be considered an error");
}

static void test_actuator_statuses_are_normalized(void)
{
    typedef struct ActuatorStatusCase
    {
        GridFlexActuatorStatus status;
        GridFlexHardwareErrorCode expected_code;
    } ActuatorStatusCase;

    const ActuatorStatusCase cases[] = {
        {GRIDFLEX_ACTUATOR_STATUS_OK,
         GRIDFLEX_HARDWARE_ERROR_NONE},
        {GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT,
         GRIDFLEX_HARDWARE_ERROR_INVALID_ARGUMENT},
        {GRIDFLEX_ACTUATOR_STATUS_NOT_CONFIGURED,
         GRIDFLEX_HARDWARE_ERROR_NOT_CONFIGURED},
        {GRIDFLEX_ACTUATOR_STATUS_UNSUPPORTED_ACTION,
         GRIDFLEX_HARDWARE_ERROR_UNSUPPORTED_OPERATION},
        {GRIDFLEX_ACTUATOR_STATUS_APPLY_FAILED,
         GRIDFLEX_HARDWARE_ERROR_OPERATION_FAILED}};

    const size_t case_count =
        sizeof(cases) /
        sizeof(cases[0]);

    size_t index;

    for (index = 0; index < case_count; ++index)
    {
        const GridFlexHardwareError error =
            gridflex_hardware_error_from_actuator_apply(
                GRIDFLEX_ACTUATOR_TYPE_BATTERY,
                cases[index].status);

        expect_true(
            error.source ==
                GRIDFLEX_HARDWARE_ERROR_SOURCE_ACTUATOR,
            "actuator error should preserve actuator source");

        expect_true(
            error.operation ==
                GRIDFLEX_HARDWARE_OPERATION_APPLY,
            "actuator error should preserve apply operation");

        expect_true(
            error.code ==
                cases[index].expected_code,
            "actuator status should map to expected hardware error code");

        expect_true(
            error.sensor_type ==
                GRIDFLEX_SENSOR_TYPE_UNKNOWN,
            "actuator error should not contain a sensor type");

        expect_true(
            error.actuator_type ==
                GRIDFLEX_ACTUATOR_TYPE_BATTERY,
            "actuator error should preserve actuator type");
    }
}

static void test_unknown_actuator_status_is_preserved_as_error(void)
{
    const GridFlexHardwareError error =
        gridflex_hardware_error_from_actuator_apply(
            GRIDFLEX_ACTUATOR_TYPE_EV_CHARGER,
            (GridFlexActuatorStatus)999);

    expect_true(
        error.code ==
            GRIDFLEX_HARDWARE_ERROR_UNKNOWN_STATUS,
        "unknown actuator status should map to unknown hardware status");

    expect_true(
        gridflex_hardware_error_is_error(error),
        "unknown actuator status should be considered an error");
}

static void test_success_status_is_not_an_error(void)
{
    const GridFlexHardwareError sensor_error =
        gridflex_hardware_error_from_sensor_read(
            GRIDFLEX_SENSOR_TYPE_BATTERY_SOC,
            GRIDFLEX_SENSOR_STATUS_OK);

    const GridFlexHardwareError actuator_error =
        gridflex_hardware_error_from_actuator_apply(
            GRIDFLEX_ACTUATOR_TYPE_GRID_CONNECTION,
            GRIDFLEX_ACTUATOR_STATUS_OK);

    expect_true(
        !gridflex_hardware_error_is_error(
            sensor_error),
        "successful sensor status should not be an error");

    expect_true(
        !gridflex_hardware_error_is_error(
            actuator_error),
        "successful actuator status should not be an error");
}

static void test_failure_status_is_an_error(void)
{
    const GridFlexHardwareError sensor_error =
        gridflex_hardware_error_from_sensor_read(
            GRIDFLEX_SENSOR_TYPE_SOLAR_POWER,
            GRIDFLEX_SENSOR_STATUS_READ_FAILED);

    const GridFlexHardwareError actuator_error =
        gridflex_hardware_error_from_actuator_apply(
            GRIDFLEX_ACTUATOR_TYPE_BATTERY,
            GRIDFLEX_ACTUATOR_STATUS_APPLY_FAILED);

    expect_true(
        gridflex_hardware_error_is_error(
            sensor_error),
        "failed sensor read should be considered an error");

    expect_true(
        gridflex_hardware_error_is_error(
            actuator_error),
        "failed actuator apply should be considered an error");
}

int main(void)
{
    test_sensor_statuses_are_normalized();
    test_unknown_sensor_status_is_preserved_as_error();
    test_actuator_statuses_are_normalized();
    test_unknown_actuator_status_is_preserved_as_error();
    test_success_status_is_not_an_error();
    test_failure_status_is_an_error();

    if (failures != 0)
    {
        fprintf(
            stderr,
            "%d hardware error test(s) failed\n",
            failures);

        return 1;
    }

    puts("All C hardware error tests passed.");

    return 0;
}
