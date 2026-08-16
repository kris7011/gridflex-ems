#include <math.h>
#include <stddef.h>

#include "gridflex/hardware/simulated_sensor.h"

static int gridflex_simulated_sensor_type_is_valid(
    GridFlexSensorType type)
{
    switch (type)
    {
    case GRIDFLEX_SENSOR_TYPE_BATTERY_SOC:
    case GRIDFLEX_SENSOR_TYPE_GRID_POWER:
    case GRIDFLEX_SENSOR_TYPE_SOLAR_POWER:
    case GRIDFLEX_SENSOR_TYPE_TEMPERATURE:
        return 1;

    case GRIDFLEX_SENSOR_TYPE_UNKNOWN:
    default:
        return 0;
    }
}

static GridFlexSensorStatus gridflex_simulated_sensor_read(
    void *context,
    double *value)
{
    GridFlexSimulatedSensor *simulated_sensor = context;

    if (simulated_sensor == NULL || value == NULL)
    {
        return GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT;
    }

    ++simulated_sensor->read_count;

    if (simulated_sensor->read_failure_enabled)
    {
        return GRIDFLEX_SENSOR_STATUS_READ_FAILED;
    }

    *value = simulated_sensor->value;

    return GRIDFLEX_SENSOR_STATUS_OK;
}

GridFlexSensorStatus gridflex_simulated_sensor_init(
    GridFlexSimulatedSensor *simulated_sensor,
    GridFlexSensorType type,
    double initial_value)
{
    if (simulated_sensor == NULL)
    {
        return GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT;
    }

    if (!gridflex_simulated_sensor_type_is_valid(type))
    {
        return GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT;
    }

    if (!isfinite(initial_value))
    {
        return GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT;
    }

    simulated_sensor->type = type;
    simulated_sensor->value = initial_value;
    simulated_sensor->read_failure_enabled = 0;
    simulated_sensor->read_count = 0;

    return GRIDFLEX_SENSOR_STATUS_OK;
}

GridFlexSensor gridflex_simulated_sensor_as_sensor(
    GridFlexSimulatedSensor *simulated_sensor)
{
    GridFlexSensor sensor = {
        GRIDFLEX_SENSOR_TYPE_UNKNOWN,
        NULL,
        NULL};

    if (simulated_sensor == NULL)
    {
        return sensor;
    }

    sensor.type = simulated_sensor->type;
    sensor.read = gridflex_simulated_sensor_read;
    sensor.context = simulated_sensor;

    return sensor;
}

GridFlexSensorStatus gridflex_simulated_sensor_set_value(
    GridFlexSimulatedSensor *simulated_sensor,
    double value)
{
    if (simulated_sensor == NULL)
    {
        return GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT;
    }

    if (!isfinite(value))
    {
        return GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT;
    }

    simulated_sensor->value = value;

    return GRIDFLEX_SENSOR_STATUS_OK;
}

GridFlexSensorStatus gridflex_simulated_sensor_set_read_failure(
    GridFlexSimulatedSensor *simulated_sensor,
    int enabled)
{
    if (simulated_sensor == NULL)
    {
        return GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT;
    }

    simulated_sensor->read_failure_enabled =
        enabled != 0;

    return GRIDFLEX_SENSOR_STATUS_OK;
}
