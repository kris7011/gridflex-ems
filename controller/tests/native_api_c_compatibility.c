#include "gridflex/controller/native_api.h"

int gridflex_controller_native_api_c_compatibility(void)
{
    GridFlexControllerLimits limits = {0};
    GridFlexControllerMeasurement measurement = {0};
    GridFlexControllerDecision decision = {0};

    GridFlexControllerHandle *handle = 0;

    GridFlexControllerStatus status =
        GRIDFLEX_CONTROLLER_STATUS_OK;

    GridFlexControllerAction action =
        GRIDFLEX_CONTROLLER_ACTION_IDLE;

    (void)limits;
    (void)measurement;
    (void)decision;
    (void)handle;
    (void)status;
    (void)action;

    return 0;
}
