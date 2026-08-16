#ifndef GRIDFLEX_HARDWARE_ERROR_H
#define GRIDFLEX_HARDWARE_ERROR_H

#include "gridflex/hardware/actuator.h"
#include "gridflex/hardware/sensor.h"

#ifdef __cplusplus
extern "C"
{
#endif

typedef enum GridFlexHardwareErrorSource
{
    GRIDFLEX_HARDWARE_ERROR_SOURCE_UNKNOWN = 0,
    GRIDFLEX_HARDWARE_ERROR_SOURCE_SENSOR = 1,
    GRIDFLEX_HARDWARE_ERROR_SOURCE_ACTUATOR = 2
} GridFlexHardwareErrorSource;

typedef enum GridFlexHardwareOperation
{
    GRIDFLEX_HARDWARE_OPERATION_UNKNOWN = 0,
    GRIDFLEX_HARDWARE_OPERATION_READ = 1,
    GRIDFLEX_HARDWARE_OPERATION_APPLY = 2
} GridFlexHardwareOperation;

typedef enum GridFlexHardwareErrorCode
{
    GRIDFLEX_HARDWARE_ERROR_NONE = 0,
    GRIDFLEX_HARDWARE_ERROR_INVALID_ARGUMENT = 1,
    GRIDFLEX_HARDWARE_ERROR_NOT_CONFIGURED = 2,
    GRIDFLEX_HARDWARE_ERROR_UNSUPPORTED_OPERATION = 3,
    GRIDFLEX_HARDWARE_ERROR_OPERATION_FAILED = 4,
    GRIDFLEX_HARDWARE_ERROR_UNKNOWN_STATUS = 5
} GridFlexHardwareErrorCode;

typedef struct GridFlexHardwareError
{
    GridFlexHardwareErrorSource source;
    GridFlexHardwareOperation operation;
    GridFlexHardwareErrorCode code;
    GridFlexSensorType sensor_type;
    GridFlexActuatorType actuator_type;
} GridFlexHardwareError;

GridFlexHardwareError gridflex_hardware_error_from_sensor_read(
    GridFlexSensorType sensor_type,
    GridFlexSensorStatus status);

GridFlexHardwareError gridflex_hardware_error_from_actuator_apply(
    GridFlexActuatorType actuator_type,
    GridFlexActuatorStatus status);

int gridflex_hardware_error_is_error(
    GridFlexHardwareError error);

#ifdef __cplusplus
}
#endif

#endif
