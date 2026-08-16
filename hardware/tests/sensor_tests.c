#include <stdio.h>

#include "gridflex/hardware/sensor.h"

typedef struct FakeSensorContext
{
    double value;
    int read_count;
} FakeSensorContext;

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

static GridFlexSensorStatus successful_read(
    void *context,
    double *value)
{
    FakeSensorContext *fake_context = context;

    if (fake_context == NULL || value == NULL)
    {
        return GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT;
    }

    ++fake_context->read_count;

    *value = fake_context->value;

    return GRIDFLEX_SENSOR_STATUS_OK;
}

static GridFlexSensorStatus failing_read(
    void *context,
    double *value)
{
    (void)context;
    (void)value;

    return GRIDFLEX_SENSOR_STATUS_READ_FAILED;
}

static void test_successful_sensor_read(void)
{
    FakeSensorContext context = {
        42.5,
        0};

    GridFlexSensor sensor = {
        GRIDFLEX_SENSOR_TYPE_BATTERY_SOC,
        successful_read,
        &context};

    GridFlexSensorReading reading = {
        GRIDFLEX_SENSOR_TYPE_UNKNOWN,
        0.0};

    const GridFlexSensorStatus status =
        gridflex_sensor_read(
            &sensor,
            &reading);

    expect_true(
        status == GRIDFLEX_SENSOR_STATUS_OK,
        "successful sensor read should return OK");

    expect_true(
        reading.type ==
            GRIDFLEX_SENSOR_TYPE_BATTERY_SOC,
        "successful sensor read should preserve sensor type");

    expect_true(
        reading.value == 42.5,
        "successful sensor read should return sensor value");

    expect_true(
        context.read_count == 1,
        "sensor callback should be invoked exactly once");
}

static void test_null_sensor_is_rejected(void)
{
    GridFlexSensorReading reading = {
        GRIDFLEX_SENSOR_TYPE_UNKNOWN,
        0.0};

    const GridFlexSensorStatus status =
        gridflex_sensor_read(
            NULL,
            &reading);

    expect_true(
        status ==
            GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT,
        "null sensor should be rejected");
}

static void test_null_reading_is_rejected(void)
{
    GridFlexSensor sensor = {
        GRIDFLEX_SENSOR_TYPE_BATTERY_SOC,
        successful_read,
        NULL};

    const GridFlexSensorStatus status =
        gridflex_sensor_read(
            &sensor,
            NULL);

    expect_true(
        status ==
            GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT,
        "null reading should be rejected");
}

static void test_unknown_sensor_type_is_rejected(void)
{
    FakeSensorContext context = {
        42.5,
        0};

    GridFlexSensor sensor = {
        GRIDFLEX_SENSOR_TYPE_UNKNOWN,
        successful_read,
        &context};

    GridFlexSensorReading reading = {
        GRIDFLEX_SENSOR_TYPE_TEMPERATURE,
        99.0};

    const GridFlexSensorStatus status =
        gridflex_sensor_read(
            &sensor,
            &reading);

    expect_true(
        status ==
            GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT,
        "unknown sensor type should be rejected");

    expect_true(
        context.read_count == 0,
        "invalid sensor type should not invoke callback");

    expect_true(
        reading.type ==
            GRIDFLEX_SENSOR_TYPE_TEMPERATURE,
        "invalid sensor type should not modify reading type");

    expect_true(
        reading.value == 99.0,
        "invalid sensor type should not modify reading value");
}

static void test_missing_callback_is_rejected(void)
{
    GridFlexSensor sensor = {
        GRIDFLEX_SENSOR_TYPE_BATTERY_SOC,
        NULL,
        NULL};

    GridFlexSensorReading reading = {
        GRIDFLEX_SENSOR_TYPE_UNKNOWN,
        0.0};

    const GridFlexSensorStatus status =
        gridflex_sensor_read(
            &sensor,
            &reading);

    expect_true(
        status ==
            GRIDFLEX_SENSOR_STATUS_NOT_CONFIGURED,
        "sensor without read callback should be rejected");
}

static void test_read_failure_is_propagated(void)
{
    GridFlexSensor sensor = {
        GRIDFLEX_SENSOR_TYPE_GRID_POWER,
        failing_read,
        NULL};

    GridFlexSensorReading reading = {
        GRIDFLEX_SENSOR_TYPE_TEMPERATURE,
        99.0};

    const GridFlexSensorStatus status =
        gridflex_sensor_read(
            &sensor,
            &reading);

    expect_true(
        status ==
            GRIDFLEX_SENSOR_STATUS_READ_FAILED,
        "sensor callback failure should be propagated");

    expect_true(
        reading.type ==
            GRIDFLEX_SENSOR_TYPE_TEMPERATURE,
        "failed read should not modify reading type");

    expect_true(
        reading.value == 99.0,
        "failed read should not modify reading value");
}

int main(void)
{
    test_successful_sensor_read();
    test_null_sensor_is_rejected();
    test_null_reading_is_rejected();
    test_unknown_sensor_type_is_rejected();
    test_missing_callback_is_rejected();
    test_read_failure_is_propagated();

    if (failures != 0)
    {
        fprintf(
            stderr,
            "%d sensor test(s) failed\n",
            failures);

        return 1;
    }

    puts("All C hardware sensor tests passed.");

    return 0;
}
