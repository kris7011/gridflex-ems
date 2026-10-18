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

    char message[64] = {0};

    size_t message_length =
        gridflex_controller_last_error_message(
            message,
            sizeof(message));

    (void)limits;
    (void)measurement;
    (void)decision;
    (void)handle;
    (void)status;
    (void)action;
    (void)message_length;

    return 0;
}
