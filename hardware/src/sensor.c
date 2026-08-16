#include <stddef.h>

#include "gridflex/hardware/sensor.h"

static int gridflex_sensor_type_is_valid(
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

GridFlexSensorStatus gridflex_sensor_read(
    const GridFlexSensor *sensor,
    GridFlexSensorReading *reading)
{
    double value;
    GridFlexSensorStatus status;

    if (sensor == NULL || reading == NULL)
    {
        return GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT;
    }

    if (!gridflex_sensor_type_is_valid(sensor->type))
    {
        return GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT;
    }

    if (sensor->read == NULL)
    {
        return GRIDFLEX_SENSOR_STATUS_NOT_CONFIGURED;
    }

    value = 0.0;

    status = sensor->read(
        sensor->context,
        &value);

    if (status != GRIDFLEX_SENSOR_STATUS_OK)
    {
        return status;
    }

    reading->type = sensor->type;
    reading->value = value;

    return GRIDFLEX_SENSOR_STATUS_OK;
}
