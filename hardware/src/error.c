#include "gridflex/hardware/error.h"

static GridFlexHardwareErrorCode gridflex_sensor_status_to_error_code(
    GridFlexSensorStatus status)
{
    switch (status)
    {
    case GRIDFLEX_SENSOR_STATUS_OK:
        return GRIDFLEX_HARDWARE_ERROR_NONE;

    case GRIDFLEX_SENSOR_STATUS_INVALID_ARGUMENT:
        return GRIDFLEX_HARDWARE_ERROR_INVALID_ARGUMENT;

    case GRIDFLEX_SENSOR_STATUS_NOT_CONFIGURED:
        return GRIDFLEX_HARDWARE_ERROR_NOT_CONFIGURED;

    case GRIDFLEX_SENSOR_STATUS_READ_FAILED:
        return GRIDFLEX_HARDWARE_ERROR_OPERATION_FAILED;

    default:
        return GRIDFLEX_HARDWARE_ERROR_UNKNOWN_STATUS;
    }
}

static GridFlexHardwareErrorCode gridflex_actuator_status_to_error_code(
    GridFlexActuatorStatus status)
{
    switch (status)
    {
    case GRIDFLEX_ACTUATOR_STATUS_OK:
        return GRIDFLEX_HARDWARE_ERROR_NONE;

    case GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT:
        return GRIDFLEX_HARDWARE_ERROR_INVALID_ARGUMENT;

    case GRIDFLEX_ACTUATOR_STATUS_NOT_CONFIGURED:
        return GRIDFLEX_HARDWARE_ERROR_NOT_CONFIGURED;

    case GRIDFLEX_ACTUATOR_STATUS_UNSUPPORTED_ACTION:
        return GRIDFLEX_HARDWARE_ERROR_UNSUPPORTED_OPERATION;

    case GRIDFLEX_ACTUATOR_STATUS_APPLY_FAILED:
        return GRIDFLEX_HARDWARE_ERROR_OPERATION_FAILED;

    default:
        return GRIDFLEX_HARDWARE_ERROR_UNKNOWN_STATUS;
    }
}

GridFlexHardwareError gridflex_hardware_error_from_sensor_read(
    GridFlexSensorType sensor_type,
    GridFlexSensorStatus status)
{
    GridFlexHardwareError error = {
        GRIDFLEX_HARDWARE_ERROR_SOURCE_SENSOR,
        GRIDFLEX_HARDWARE_OPERATION_READ,
        gridflex_sensor_status_to_error_code(status),
        sensor_type,
        GRIDFLEX_ACTUATOR_TYPE_UNKNOWN};

    return error;
}

GridFlexHardwareError gridflex_hardware_error_from_actuator_apply(
    GridFlexActuatorType actuator_type,
    GridFlexActuatorStatus status)
{
    GridFlexHardwareError error = {
        GRIDFLEX_HARDWARE_ERROR_SOURCE_ACTUATOR,
        GRIDFLEX_HARDWARE_OPERATION_APPLY,
        gridflex_actuator_status_to_error_code(status),
        GRIDFLEX_SENSOR_TYPE_UNKNOWN,
        actuator_type};

    return error;
}

int gridflex_hardware_error_is_error(
    GridFlexHardwareError error)
{
    return error.code !=
           GRIDFLEX_HARDWARE_ERROR_NONE;
}
