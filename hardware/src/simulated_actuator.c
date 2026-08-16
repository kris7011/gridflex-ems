#include <stddef.h>

#include "gridflex/hardware/simulated_actuator.h"

static int gridflex_simulated_actuator_type_is_valid(
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

static GridFlexActuatorStatus gridflex_simulated_actuator_apply(
    void *context,
    const GridFlexActuatorCommand *command)
{
    GridFlexSimulatedActuator *simulated_actuator = context;

    if (simulated_actuator == NULL || command == NULL)
    {
        return GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT;
    }

    ++simulated_actuator->apply_count;

    if (simulated_actuator->apply_failure_enabled)
    {
        return GRIDFLEX_ACTUATOR_STATUS_APPLY_FAILED;
    }

    simulated_actuator->last_action =
        command->action;

    simulated_actuator->last_requested_power_kw =
        command->requested_power_kw;

    return GRIDFLEX_ACTUATOR_STATUS_OK;
}

GridFlexActuatorStatus gridflex_simulated_actuator_init(
    GridFlexSimulatedActuator *simulated_actuator,
    GridFlexActuatorType type)
{
    if (simulated_actuator == NULL)
    {
        return GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT;
    }

    if (!gridflex_simulated_actuator_type_is_valid(type))
    {
        return GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT;
    }

    simulated_actuator->type = type;
    simulated_actuator->apply_failure_enabled = 0;
    simulated_actuator->apply_count = 0;
    simulated_actuator->last_action =
        GRIDFLEX_ACTUATOR_ACTION_UNKNOWN;
    simulated_actuator->last_requested_power_kw = 0.0;

    return GRIDFLEX_ACTUATOR_STATUS_OK;
}

GridFlexActuator gridflex_simulated_actuator_as_actuator(
    GridFlexSimulatedActuator *simulated_actuator)
{
    GridFlexActuator actuator = {
        GRIDFLEX_ACTUATOR_TYPE_UNKNOWN,
        NULL,
        NULL};

    if (simulated_actuator == NULL)
    {
        return actuator;
    }

    actuator.type = simulated_actuator->type;
    actuator.apply = gridflex_simulated_actuator_apply;
    actuator.context = simulated_actuator;

    return actuator;
}

GridFlexActuatorStatus gridflex_simulated_actuator_set_apply_failure(
    GridFlexSimulatedActuator *simulated_actuator,
    int enabled)
{
    if (simulated_actuator == NULL)
    {
        return GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT;
    }

    simulated_actuator->apply_failure_enabled =
        enabled != 0;

    return GRIDFLEX_ACTUATOR_STATUS_OK;
}
