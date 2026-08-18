#ifndef GRIDFLEX_CONTROLLER_NATIVE_API_H
#define GRIDFLEX_CONTROLLER_NATIVE_API_H

#include <stdint.h>

#if defined(_WIN32)
#if defined(GRIDFLEX_CONTROLLER_NATIVE_EXPORTS)
#define GRIDFLEX_CONTROLLER_API __declspec(dllexport)
#elif defined(GRIDFLEX_CONTROLLER_NATIVE_IMPORTS)
#define GRIDFLEX_CONTROLLER_API __declspec(dllimport)
#else
#define GRIDFLEX_CONTROLLER_API
#endif
#define GRIDFLEX_CONTROLLER_CALL __cdecl
#elif defined(__GNUC__) && __GNUC__ >= 4
#define GRIDFLEX_CONTROLLER_API __attribute__((visibility("default")))
#define GRIDFLEX_CONTROLLER_CALL
#else
#define GRIDFLEX_CONTROLLER_API
#define GRIDFLEX_CONTROLLER_CALL
#endif

#ifdef __cplusplus
extern "C"
{
#endif

#define GRIDFLEX_CONTROLLER_ABI_VERSION 1u

typedef int32_t GridFlexControllerStatus;

enum
{
    GRIDFLEX_CONTROLLER_STATUS_OK = 0,
    GRIDFLEX_CONTROLLER_STATUS_INVALID_ARGUMENT = 1,
    GRIDFLEX_CONTROLLER_STATUS_INVALID_LIMITS = 2,
    GRIDFLEX_CONTROLLER_STATUS_INVALID_MEASUREMENT = 3,
    GRIDFLEX_CONTROLLER_STATUS_INTERNAL_ERROR = 4
};

typedef int32_t GridFlexControllerAction;

enum
{
    GRIDFLEX_CONTROLLER_ACTION_IDLE = 0,
    GRIDFLEX_CONTROLLER_ACTION_CHARGE_BATTERY = 1,
    GRIDFLEX_CONTROLLER_ACTION_DISCHARGE_BATTERY = 2,
    GRIDFLEX_CONTROLLER_ACTION_IMPORT_FROM_GRID = 3,
    GRIDFLEX_CONTROLLER_ACTION_EXPORT_TO_GRID = 4
};

typedef struct GridFlexControllerLimits
{
    double max_charge_power_kw;
    double max_discharge_power_kw;
    double minimum_battery_soc_kwh;
    double maximum_battery_soc_kwh;
} GridFlexControllerLimits;

typedef struct GridFlexControllerMeasurement
{
    uint64_t step_number;
    double elapsed_time_hours;
    double interval_hours;
    double generated_energy_kwh;
    double consumed_energy_kwh;
    double net_energy_kwh;
    double battery_state_of_charge_kwh;
    double grid_import_energy_kwh;
    double grid_export_energy_kwh;
    double unresolved_energy_kwh;
} GridFlexControllerMeasurement;

typedef struct GridFlexControllerDecision
{
    uint64_t source_step_number;
    GridFlexControllerAction action;
    double requested_power_kw;
} GridFlexControllerDecision;

typedef struct GridFlexControllerHandle GridFlexControllerHandle;

GRIDFLEX_CONTROLLER_API uint32_t GRIDFLEX_CONTROLLER_CALL
gridflex_controller_abi_version(void);

GRIDFLEX_CONTROLLER_API GridFlexControllerStatus GRIDFLEX_CONTROLLER_CALL
gridflex_controller_create(
    const GridFlexControllerLimits *limits,
    GridFlexControllerHandle **handle);

GRIDFLEX_CONTROLLER_API void GRIDFLEX_CONTROLLER_CALL
gridflex_controller_destroy(
    GridFlexControllerHandle *handle);

GRIDFLEX_CONTROLLER_API GridFlexControllerStatus GRIDFLEX_CONTROLLER_CALL
gridflex_controller_decide(
    GridFlexControllerHandle *handle,
    const GridFlexControllerMeasurement *measurement,
    GridFlexControllerDecision *decision);

#ifdef __cplusplus
}
#endif

#endif
