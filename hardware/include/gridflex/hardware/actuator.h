#ifndef GRIDFLEX_ACTUATOR_H
#define GRIDFLEX_ACTUATOR_H

#ifdef __cplusplus
extern "C"
{
#endif

typedef enum GridFlexActuatorType
{
    GRIDFLEX_ACTUATOR_TYPE_UNKNOWN = 0,
    GRIDFLEX_ACTUATOR_TYPE_BATTERY = 1,
    GRIDFLEX_ACTUATOR_TYPE_GRID_CONNECTION = 2,
    GRIDFLEX_ACTUATOR_TYPE_EV_CHARGER = 3
} GridFlexActuatorType;

typedef enum GridFlexActuatorAction
{
    GRIDFLEX_ACTUATOR_ACTION_UNKNOWN = 0,
    GRIDFLEX_ACTUATOR_ACTION_IDLE = 1,
    GRIDFLEX_ACTUATOR_ACTION_CHARGE = 2,
    GRIDFLEX_ACTUATOR_ACTION_DISCHARGE = 3,
    GRIDFLEX_ACTUATOR_ACTION_IMPORT = 4,
    GRIDFLEX_ACTUATOR_ACTION_EXPORT = 5
} GridFlexActuatorAction;

typedef enum GridFlexActuatorStatus
{
    GRIDFLEX_ACTUATOR_STATUS_OK = 0,
    GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT = 1,
    GRIDFLEX_ACTUATOR_STATUS_NOT_CONFIGURED = 2,
    GRIDFLEX_ACTUATOR_STATUS_UNSUPPORTED_ACTION = 3,
    GRIDFLEX_ACTUATOR_STATUS_APPLY_FAILED = 4
} GridFlexActuatorStatus;

typedef struct GridFlexActuatorCommand
{
    GridFlexActuatorAction action;
    double requested_power_kw;
} GridFlexActuatorCommand;

typedef GridFlexActuatorStatus (*GridFlexActuatorApplyFunction)(
    void *context,
    const GridFlexActuatorCommand *command);

typedef struct GridFlexActuator
{
    GridFlexActuatorType type;
    GridFlexActuatorApplyFunction apply;
    void *context;
} GridFlexActuator;

GridFlexActuatorStatus gridflex_actuator_apply(
    const GridFlexActuator *actuator,
    const GridFlexActuatorCommand *command);

#ifdef __cplusplus
}
#endif

#endif
