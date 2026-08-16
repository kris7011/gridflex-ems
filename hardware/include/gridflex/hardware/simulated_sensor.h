#ifndef GRIDFLEX_SIMULATED_SENSOR_H
#define GRIDFLEX_SIMULATED_SENSOR_H

#include "gridflex/hardware/sensor.h"

#ifdef __cplusplus
extern "C"
{
#endif

typedef struct GridFlexSimulatedSensor
{
    GridFlexSensorType type;
    double value;
    int read_failure_enabled;
    unsigned int read_count;
} GridFlexSimulatedSensor;

GridFlexSensorStatus gridflex_simulated_sensor_init(
    GridFlexSimulatedSensor *simulated_sensor,
    GridFlexSensorType type,
    double initial_value);

GridFlexSensor gridflex_simulated_sensor_as_sensor(
    GridFlexSimulatedSensor *simulated_sensor);

GridFlexSensorStatus gridflex_simulated_sensor_set_value(
    GridFlexSimulatedSensor *simulated_sensor,
    double value);

GridFlexSensorStatus gridflex_simulated_sensor_set_read_failure(
    GridFlexSimulatedSensor *simulated_sensor,
    int enabled);

#ifdef __cplusplus
}
#endif

#endif
