#include <math.h>
#include <stddef.h>

#include "gridflex/hardware/actuator.h"

static int gridflex_actuator_type_is_valid(
    GridFlexActuatorType type)
{
    switch (type)
    {
    case GRIDFLEX_ACTUATOR_TYPE_BATTERY:
    case GRIDFLEX_ACTUATOR_TYPE_GRID_CONNECTION:
    case GRIDFLEX_ACTUATOR_TYPE_EV_CHARGER:
        return 1;

    case GRIDFLEX_ACTUATOR_TYPE_UNKNOWN:
    default:
        return 0;
    }
}

static int gridflex_actuator_action_is_valid(
    GridFlexActuatorAction action)
{
    switch (action)
    {
    case GRIDFLEX_ACTUATOR_ACTION_IDLE:
    case GRIDFLEX_ACTUATOR_ACTION_CHARGE:
    case GRIDFLEX_ACTUATOR_ACTION_DISCHARGE:
    case GRIDFLEX_ACTUATOR_ACTION_IMPORT:
    case GRIDFLEX_ACTUATOR_ACTION_EXPORT:
        return 1;

    case GRIDFLEX_ACTUATOR_ACTION_UNKNOWN:
    default:
        return 0;
    }
}

static int gridflex_actuator_action_is_supported(
    GridFlexActuatorType type,
    GridFlexActuatorAction action)
{
    if (action == GRIDFLEX_ACTUATOR_ACTION_IDLE)
    {
        return 1;
    }

    switch (type)
    {
    case GRIDFLEX_ACTUATOR_TYPE_BATTERY:
        return action == GRIDFLEX_ACTUATOR_ACTION_CHARGE ||
               action == GRIDFLEX_ACTUATOR_ACTION_DISCHARGE;

    case GRIDFLEX_ACTUATOR_TYPE_GRID_CONNECTION:
        return action == GRIDFLEX_ACTUATOR_ACTION_IMPORT ||
               action == GRIDFLEX_ACTUATOR_ACTION_EXPORT;

    case GRIDFLEX_ACTUATOR_TYPE_EV_CHARGER:
        return action == GRIDFLEX_ACTUATOR_ACTION_CHARGE;

    case GRIDFLEX_ACTUATOR_TYPE_UNKNOWN:
    default:
        return 0;
    }
}

static int gridflex_actuator_power_is_valid(
    const GridFlexActuatorCommand *command)
{
    if (!isfinite(command->requested_power_kw))
    {
        return 0;
    }

    if (command->action == GRIDFLEX_ACTUATOR_ACTION_IDLE)
    {
        return command->requested_power_kw == 0.0;
    }

    return command->requested_power_kw > 0.0;
}

GridFlexActuatorStatus gridflex_actuator_apply(
    const GridFlexActuator *actuator,
    const GridFlexActuatorCommand *command)
{
    if (actuator == NULL || command == NULL)
    {
        return GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT;
    }

    if (!gridflex_actuator_type_is_valid(actuator->type))
    {
        return GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT;
    }

    if (!gridflex_actuator_action_is_valid(command->action))
    {
        return GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT;
    }

    if (!gridflex_actuator_action_is_supported(
            actuator->type,
            command->action))
    {
        return GRIDFLEX_ACTUATOR_STATUS_UNSUPPORTED_ACTION;
    }

    if (!gridflex_actuator_power_is_valid(command))
    {
        return GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT;
    }

    if (actuator->apply == NULL)
    {
        return GRIDFLEX_ACTUATOR_STATUS_NOT_CONFIGURED;
    }

    return actuator->apply(
        actuator->context,
        command);
}
