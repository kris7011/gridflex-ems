#include <catch2/catch_test_macros.hpp>

#include <stdexcept>

#include "gridflex/controller/control_command.hpp"
#include "gridflex/controller/controller_limits.hpp"
#include "gridflex/controller/energy_controller.hpp"
#include "gridflex/controller/energy_measurement.hpp"
#include "gridflex/controller/hardware_command_executor.hpp"
#include "gridflex/hardware/simulated_actuator.h"

namespace
{

using gridflex::controller::ControlAction;
using gridflex::controller::ControlCommand;
using gridflex::controller::ControllerLimits;
using gridflex::controller::EnergyController;
using gridflex::controller::EnergyMeasurement;
using gridflex::controller::HardwareCommandExecutor;

class ActuatorFixture final
{
  public:
    ActuatorFixture()
    {
        const GridFlexActuatorStatus battery_status =
            gridflex_simulated_actuator_init(
                &battery_state,
                GRIDFLEX_ACTUATOR_TYPE_BATTERY);

        if (battery_status != GRIDFLEX_ACTUATOR_STATUS_OK)
        {
            throw std::runtime_error(
                "Failed to initialize simulated battery actuator.");
        }

        const GridFlexActuatorStatus grid_status =
            gridflex_simulated_actuator_init(
                &grid_state,
                GRIDFLEX_ACTUATOR_TYPE_GRID_CONNECTION);

        if (grid_status != GRIDFLEX_ACTUATOR_STATUS_OK)
        {
            throw std::runtime_error(
                "Failed to initialize simulated grid actuator.");
        }

        battery =
            gridflex_simulated_actuator_as_actuator(
                &battery_state);

        grid =
            gridflex_simulated_actuator_as_actuator(
                &grid_state);
    }

    ActuatorFixture(
        const ActuatorFixture &) = delete;

    ActuatorFixture &operator=(
        const ActuatorFixture &) = delete;

    GridFlexSimulatedActuator battery_state{};
    GridFlexSimulatedActuator grid_state{};

    GridFlexActuator battery{};
    GridFlexActuator grid{};
};

} // namespace

TEST_CASE("Hardware executor routes battery charge and idles grid")
{
    ActuatorFixture fixture;

    const HardwareCommandExecutor executor{
        fixture.battery,
        fixture.grid};

    const ControlCommand command{
        1,
        ControlAction::ChargeBattery,
        25.0};

    const auto result =
        executor.execute(command);

    REQUIRE(result.succeeded());
    REQUIRE(result.battery_succeeded());
    REQUIRE(result.grid_succeeded());

    REQUIRE(fixture.battery_state.apply_count == 1);
    REQUIRE(
        fixture.battery_state.last_action ==
        GRIDFLEX_ACTUATOR_ACTION_CHARGE);
    REQUIRE(
        fixture.battery_state.last_requested_power_kw ==
        25.0);

    REQUIRE(fixture.grid_state.apply_count == 1);
    REQUIRE(
        fixture.grid_state.last_action ==
        GRIDFLEX_ACTUATOR_ACTION_IDLE);
    REQUIRE(
        fixture.grid_state.last_requested_power_kw ==
        0.0);
}

TEST_CASE("Hardware executor routes battery discharge and idles grid")
{
    ActuatorFixture fixture;

    const HardwareCommandExecutor executor{
        fixture.battery,
        fixture.grid};

    const ControlCommand command{
        2,
        ControlAction::DischargeBattery,
        18.0};

    const auto result =
        executor.execute(command);

    REQUIRE(result.succeeded());

    REQUIRE(
        fixture.battery_state.last_action ==
        GRIDFLEX_ACTUATOR_ACTION_DISCHARGE);
    REQUIRE(
        fixture.battery_state.last_requested_power_kw ==
        18.0);

    REQUIRE(
        fixture.grid_state.last_action ==
        GRIDFLEX_ACTUATOR_ACTION_IDLE);
    REQUIRE(
        fixture.grid_state.last_requested_power_kw ==
        0.0);
}

TEST_CASE("Hardware executor routes grid import and idles battery")
{
    ActuatorFixture fixture;

    const HardwareCommandExecutor executor{
        fixture.battery,
        fixture.grid};

    const ControlCommand command{
        3,
        ControlAction::ImportFromGrid,
        30.0};

    const auto result =
        executor.execute(command);

    REQUIRE(result.succeeded());

    REQUIRE(
        fixture.battery_state.last_action ==
        GRIDFLEX_ACTUATOR_ACTION_IDLE);
    REQUIRE(
        fixture.battery_state.last_requested_power_kw ==
        0.0);

    REQUIRE(
        fixture.grid_state.last_action ==
        GRIDFLEX_ACTUATOR_ACTION_IMPORT);
    REQUIRE(
        fixture.grid_state.last_requested_power_kw ==
        30.0);
}

TEST_CASE("Hardware executor routes grid export and idles battery")
{
    ActuatorFixture fixture;

    const HardwareCommandExecutor executor{
        fixture.battery,
        fixture.grid};

    const ControlCommand command{
        4,
        ControlAction::ExportToGrid,
        12.5};

    const auto result =
        executor.execute(command);

    REQUIRE(result.succeeded());

    REQUIRE(
        fixture.battery_state.last_action ==
        GRIDFLEX_ACTUATOR_ACTION_IDLE);

    REQUIRE(
        fixture.grid_state.last_action ==
        GRIDFLEX_ACTUATOR_ACTION_EXPORT);
    REQUIRE(
        fixture.grid_state.last_requested_power_kw ==
        12.5);
}

TEST_CASE("Hardware executor idles both actuators")
{
    ActuatorFixture fixture;

    const HardwareCommandExecutor executor{
        fixture.battery,
        fixture.grid};

    const ControlCommand command{
        5,
        ControlAction::Idle,
        0.0};

    const auto result =
        executor.execute(command);

    REQUIRE(result.succeeded());

    REQUIRE(
        fixture.battery_state.last_action ==
        GRIDFLEX_ACTUATOR_ACTION_IDLE);

    REQUIRE(
        fixture.grid_state.last_action ==
        GRIDFLEX_ACTUATOR_ACTION_IDLE);

    REQUIRE(
        fixture.battery_state.last_requested_power_kw ==
        0.0);

    REQUIRE(
        fixture.grid_state.last_requested_power_kw ==
        0.0);
}

TEST_CASE("Hardware executor clears previous actuator state when command target changes")
{
    ActuatorFixture fixture;

    const HardwareCommandExecutor executor{
        fixture.battery,
        fixture.grid};

    const ControlCommand charge_command{
        6,
        ControlAction::ChargeBattery,
        20.0};

    const auto charge_result =
        executor.execute(charge_command);

    REQUIRE(charge_result.succeeded());

    REQUIRE(
        fixture.battery_state.last_action ==
        GRIDFLEX_ACTUATOR_ACTION_CHARGE);

    REQUIRE(
        fixture.battery_state.last_requested_power_kw ==
        20.0);

    REQUIRE(
        fixture.grid_state.last_action ==
        GRIDFLEX_ACTUATOR_ACTION_IDLE);

    const ControlCommand import_command{
        7,
        ControlAction::ImportFromGrid,
        15.0};

    const auto import_result =
        executor.execute(import_command);

    REQUIRE(import_result.succeeded());

    REQUIRE(
        fixture.battery_state.last_action ==
        GRIDFLEX_ACTUATOR_ACTION_IDLE);

    REQUIRE(
        fixture.battery_state.last_requested_power_kw ==
        0.0);

    REQUIRE(
        fixture.grid_state.last_action ==
        GRIDFLEX_ACTUATOR_ACTION_IMPORT);

    REQUIRE(
        fixture.grid_state.last_requested_power_kw ==
        15.0);

    REQUIRE(fixture.battery_state.apply_count == 2);
    REQUIRE(fixture.grid_state.apply_count == 2);
}

TEST_CASE("Energy controller decision executes through C hardware abstraction")
{
    ActuatorFixture fixture;

    const EnergyController controller{
        ControllerLimits{
            25.0,
            30.0,
            10.0,
            90.0}};

    const EnergyMeasurement measurement{
        10,
        1.0,
        1.0,
        60.0,
        50.0,
        10.0,
        40.0,
        0.0,
        0.0,
        0.0};

    const auto command =
        controller.decide(measurement);

    REQUIRE(
        command.action() ==
        ControlAction::ChargeBattery);

    REQUIRE(
        command.requested_power_kw() ==
        10.0);

    const HardwareCommandExecutor executor{
        fixture.battery,
        fixture.grid};

    const auto result =
        executor.execute(command);

    REQUIRE(result.succeeded());

    REQUIRE(
        fixture.battery_state.last_action ==
        GRIDFLEX_ACTUATOR_ACTION_CHARGE);

    REQUIRE(
        fixture.battery_state.last_requested_power_kw ==
        10.0);

    REQUIRE(
        fixture.grid_state.last_action ==
        GRIDFLEX_ACTUATOR_ACTION_IDLE);

    REQUIRE(
        fixture.grid_state.last_requested_power_kw ==
        0.0);
}

TEST_CASE("Hardware executor reports battery failure while still applying grid command")
{
    ActuatorFixture fixture;

    REQUIRE(
        gridflex_simulated_actuator_set_apply_failure(
            &fixture.battery_state,
            1) ==
        GRIDFLEX_ACTUATOR_STATUS_OK);

    const HardwareCommandExecutor executor{
        fixture.battery,
        fixture.grid};

    const ControlCommand command{
        6,
        ControlAction::ChargeBattery,
        20.0};

    const auto result =
        executor.execute(command);

    REQUIRE_FALSE(result.succeeded());
    REQUIRE_FALSE(result.battery_succeeded());
    REQUIRE(result.grid_succeeded());

    REQUIRE(
        result.battery_error().code ==
        GRIDFLEX_HARDWARE_ERROR_OPERATION_FAILED);

    REQUIRE(
        result.grid_error().code ==
        GRIDFLEX_HARDWARE_ERROR_NONE);

    REQUIRE(fixture.battery_state.apply_count == 1);
    REQUIRE(fixture.grid_state.apply_count == 1);

    REQUIRE(
        fixture.battery_state.last_action ==
        GRIDFLEX_ACTUATOR_ACTION_UNKNOWN);

    REQUIRE(
        fixture.grid_state.last_action ==
        GRIDFLEX_ACTUATOR_ACTION_IDLE);
}

TEST_CASE("Hardware executor reports grid failure while preserving battery result")
{
    ActuatorFixture fixture;

    REQUIRE(
        gridflex_simulated_actuator_set_apply_failure(
            &fixture.grid_state,
            1) ==
        GRIDFLEX_ACTUATOR_STATUS_OK);

    const HardwareCommandExecutor executor{
        fixture.battery,
        fixture.grid};

    const ControlCommand command{
        7,
        ControlAction::ImportFromGrid,
        15.0};

    const auto result =
        executor.execute(command);

    REQUIRE_FALSE(result.succeeded());
    REQUIRE(result.battery_succeeded());
    REQUIRE_FALSE(result.grid_succeeded());

    REQUIRE(
        result.battery_error().code ==
        GRIDFLEX_HARDWARE_ERROR_NONE);

    REQUIRE(
        result.grid_error().code ==
        GRIDFLEX_HARDWARE_ERROR_OPERATION_FAILED);

    REQUIRE(fixture.battery_state.apply_count == 1);
    REQUIRE(fixture.grid_state.apply_count == 1);

    REQUIRE(
        fixture.battery_state.last_action ==
        GRIDFLEX_ACTUATOR_ACTION_IDLE);

    REQUIRE(
        fixture.grid_state.last_action ==
        GRIDFLEX_ACTUATOR_ACTION_UNKNOWN);
}

TEST_CASE("Hardware executor rejects actuators with incorrect roles")
{
    ActuatorFixture fixture;

    REQUIRE_THROWS_AS(
        (HardwareCommandExecutor{
            fixture.grid,
            fixture.battery}),
        std::invalid_argument);
}

TEST_CASE("Hardware executor reports unconfigured actuator")
{
    ActuatorFixture fixture;

    const GridFlexActuator unconfigured_battery{
        GRIDFLEX_ACTUATOR_TYPE_BATTERY,
        nullptr,
        nullptr};

    const HardwareCommandExecutor executor{
        unconfigured_battery,
        fixture.grid};

    const ControlCommand command{
        8,
        ControlAction::ChargeBattery,
        10.0};

    const auto result =
        executor.execute(command);

    REQUIRE_FALSE(result.succeeded());

    REQUIRE(
        result.battery_error().code ==
        GRIDFLEX_HARDWARE_ERROR_NOT_CONFIGURED);

    REQUIRE(result.grid_succeeded());

    REQUIRE(fixture.grid_state.apply_count == 1);
}

TEST_CASE("Hardware executor rejects unknown control action before hardware access")
{
    ActuatorFixture fixture;

    const HardwareCommandExecutor executor{
        fixture.battery,
        fixture.grid};

    const ControlCommand command{
        9,
        static_cast<ControlAction>(999),
        10.0};

    REQUIRE_THROWS_AS(
        executor.execute(command),
        std::invalid_argument);

    REQUIRE(fixture.battery_state.apply_count == 0);
    REQUIRE(fixture.grid_state.apply_count == 0);
}
