#include "gridflex/controller/native_api.h"

#include "gridflex/controller/control_command.hpp"
#include "gridflex/controller/controller_limits.hpp"
#include "gridflex/controller/energy_controller.hpp"
#include "gridflex/controller/energy_measurement.hpp"

#include <memory>
#include <stdexcept>

using gridflex::controller::ControlAction;
using gridflex::controller::ControlCommand;
using gridflex::controller::ControllerLimits;
using gridflex::controller::EnergyController;
using gridflex::controller::EnergyMeasurement;

struct GridFlexControllerHandle final
{
    explicit GridFlexControllerHandle(
        const ControllerLimits &limits)
        : controller{limits}
    {
    }

    EnergyController controller;
};

namespace
{

[[nodiscard]] bool try_map_control_action(
    const ControlAction action,
    GridFlexControllerAction &native_action) noexcept
{
    switch (action)
    {
    case ControlAction::Idle:
        native_action =
            GRIDFLEX_CONTROLLER_ACTION_IDLE;
        return true;

    case ControlAction::ChargeBattery:
        native_action =
            GRIDFLEX_CONTROLLER_ACTION_CHARGE_BATTERY;
        return true;

    case ControlAction::DischargeBattery:
        native_action =
            GRIDFLEX_CONTROLLER_ACTION_DISCHARGE_BATTERY;
        return true;

    case ControlAction::ImportFromGrid:
        native_action =
            GRIDFLEX_CONTROLLER_ACTION_IMPORT_FROM_GRID;
        return true;

    case ControlAction::ExportToGrid:
        native_action =
            GRIDFLEX_CONTROLLER_ACTION_EXPORT_TO_GRID;
        return true;
    }

    return false;
}

} // namespace

extern "C"
{

GRIDFLEX_CONTROLLER_API uint32_t GRIDFLEX_CONTROLLER_CALL
gridflex_controller_abi_version(void)
{
    return GRIDFLEX_CONTROLLER_ABI_VERSION;
}

GRIDFLEX_CONTROLLER_API GridFlexControllerStatus GRIDFLEX_CONTROLLER_CALL
gridflex_controller_create(
    const GridFlexControllerLimits *limits,
    GridFlexControllerHandle **handle)
{
    if (handle == nullptr)
    {
        return GRIDFLEX_CONTROLLER_STATUS_INVALID_ARGUMENT;
    }

    *handle = nullptr;

    if (limits == nullptr)
    {
        return GRIDFLEX_CONTROLLER_STATUS_INVALID_ARGUMENT;
    }

    try
    {
        const ControllerLimits controller_limits{
            limits->max_charge_power_kw,
            limits->max_discharge_power_kw,
            limits->minimum_battery_soc_kwh,
            limits->maximum_battery_soc_kwh};

        try
        {
            auto controller_handle =
                std::make_unique<GridFlexControllerHandle>(
                    controller_limits);

            *handle = controller_handle.release();

            return GRIDFLEX_CONTROLLER_STATUS_OK;
        }
        catch (...)
        {
            return GRIDFLEX_CONTROLLER_STATUS_INTERNAL_ERROR;
        }
    }
    catch (const std::invalid_argument &)
    {
        return GRIDFLEX_CONTROLLER_STATUS_INVALID_LIMITS;
    }
    catch (...)
    {
        return GRIDFLEX_CONTROLLER_STATUS_INTERNAL_ERROR;
    }
}

GRIDFLEX_CONTROLLER_API void GRIDFLEX_CONTROLLER_CALL
gridflex_controller_destroy(
    GridFlexControllerHandle *handle)
{
    delete handle;
}

GRIDFLEX_CONTROLLER_API GridFlexControllerStatus GRIDFLEX_CONTROLLER_CALL
gridflex_controller_decide(
    GridFlexControllerHandle *handle,
    const GridFlexControllerMeasurement *measurement,
    GridFlexControllerDecision *decision)
{
    if (
        handle == nullptr ||
        measurement == nullptr ||
        decision == nullptr)
    {
        return GRIDFLEX_CONTROLLER_STATUS_INVALID_ARGUMENT;
    }

    try
    {
        const EnergyMeasurement controller_measurement{
            measurement->step_number,
            measurement->elapsed_time_hours,
            measurement->interval_hours,
            measurement->generated_energy_kwh,
            measurement->consumed_energy_kwh,
            measurement->net_energy_kwh,
            measurement->battery_state_of_charge_kwh,
            measurement->grid_import_energy_kwh,
            measurement->grid_export_energy_kwh,
            measurement->unresolved_energy_kwh};

        try
        {
            const ControlCommand command =
                handle->controller.decide(
                    controller_measurement);

            GridFlexControllerAction native_action =
                GRIDFLEX_CONTROLLER_ACTION_IDLE;

            if (!try_map_control_action(
                    command.action(),
                    native_action))
            {
                return GRIDFLEX_CONTROLLER_STATUS_INTERNAL_ERROR;
            }

            const GridFlexControllerDecision native_decision{
                command.source_step_number(),
                native_action,
                command.requested_power_kw()};

            *decision = native_decision;

            return GRIDFLEX_CONTROLLER_STATUS_OK;
        }
        catch (...)
        {
            return GRIDFLEX_CONTROLLER_STATUS_INTERNAL_ERROR;
        }
    }
    catch (const std::invalid_argument &)
    {
        return GRIDFLEX_CONTROLLER_STATUS_INVALID_MEASUREMENT;
    }
    catch (...)
    {
        return GRIDFLEX_CONTROLLER_STATUS_INTERNAL_ERROR;
    }
}
}
