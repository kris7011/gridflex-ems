#ifndef GRIDFLEX_SENSOR_H
#define GRIDFLEX_SENSOR_H

#ifdef __cplusplus
extern "C"
{
#endif

typedef enum GridFlexSensorType
{
    GRIDFLEX_SENSOR_TYPE_UNKNOWN = 0,
    GRIDFLEX_SENSOR_TYPE_BATTERY_SOC = 1,
    GRIDFLEX_SENSOR_TYPE_GRID_POWER = 2,
    GRIDFLEX_SENSOR_TYPE_SOLAR_POWER = 3,
    GRIDFLEX_SENSOR_TYPE_TEMPERATURE = 4
} GridFlexSensorType;

typedef enum GridFlexSensorStatus
{
    GRIDFLEX_SENSOR_STATUS_OK = 0,
    GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT = 1,
    GRIDFLEX_SENSOR_STATUS_NOT_CONFIGURED = 2,
    GRIDFLEX_SENSOR_STATUS_READ_FAILED = 3
} GridFlexSensorStatus;

typedef struct GridFlexSensorReading
{
    GridFlexSensorType type;
    double value;
} GridFlexSensorReading;

typedef GridFlexSensorStatus (*GridFlexSensorReadFunction)(
    void *context,
    double *value);

typedef struct GridFlexSensor
{
    GridFlexSensorType type;
    GridFlexSensorReadFunction read;
    void *context;
} GridFlexSensor;

GridFlexSensorStatus gridflex_sensor_read(
    const GridFlexSensor *sensor,
    GridFlexSensorReading *reading);

#ifdef __cplusplus
}
#endif

#endif
