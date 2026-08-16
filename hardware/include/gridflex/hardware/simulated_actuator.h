#ifndef GRIDFLEX_SIMULATED_ACTUATOR_H
#define GRIDFLEX_SIMULATED_ACTUATOR_H

#include "gridflex/hardware/actuator.h"

#ifdef __cplusplus
extern "C"
{
#endif

typedef struct GridFlexSimulatedActuator
{
    GridFlexActuatorType type;
    int apply_failure_enabled;
    unsigned int apply_count;
    GridFlexActuatorAction last_action;
    double last_requested_power_kw;
} GridFlexSimulatedActuator;

GridFlexActuatorStatus gridflex_simulated_actuator_init(
    GridFlexSimulatedActuator *simulated_actuator,
    GridFlexActuatorType type);

GridFlexActuator gridflex_simulated_actuator_as_actuator(
    GridFlexSimulatedActuator *simulated_actuator);

GridFlexActuatorStatus gridflex_simulated_actuator_set_apply_failure(
    GridFlexSimulatedActuator *simulated_actuator,
    int enabled);

#ifdef __cplusplus
}
#endif

#endif
