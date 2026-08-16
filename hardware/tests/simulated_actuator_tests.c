#include <stddef.h>
#include <stdio.h>

#include "gridflex/hardware/simulated_actuator.h"

static int failures = 0;

static void expect_true(
    int condition,
    const char *message)
{
    if (!condition)
    {
        fprintf(
            stderr,
            "FAIL: %s\n",
            message);

        ++failures;
    }
}

static void test_supported_actuator_types_can_be_initialized(void)
{
    const GridFlexActuatorType types[] = {
        GRIDFLEX_ACTUATOR_TYPE_BATTERY,
        GRIDFLEX_ACTUATOR_TYPE_GRID_CONNECTION,
        GRIDFLEX_ACTUATOR_TYPE_EV_CHARGER};

    const size_t type_count =
        sizeof(types) /
        sizeof(types[0]);

    size_t index;

    for (index = 0; index < type_count; ++index)
    {
        GridFlexSimulatedActuator simulated_actuator;

        const GridFlexActuatorStatus status =
            gridflex_simulated_actuator_init(
                &simulated_actuator,
                types[index]);

        expect_true(
            status == GRIDFLEX_ACTUATOR_STATUS_OK,
            "supported simulated actuator type should initialize");

        expect_true(
            simulated_actuator.type == types[index],
            "initialized actuator should preserve type");

        expect_true(
            simulated_actuator.apply_failure_enabled == 0,
            "initialized actuator should not fail applies");

        expect_true(
            simulated_actuator.apply_count == 0,
            "initialized actuator should have zero apply attempts");

        expect_true(
            simulated_actuator.last_action ==
                GRIDFLEX_ACTUATOR_ACTION_UNKNOWN,
            "initialized actuator should have no previous action");

        expect_true(
            simulated_actuator.last_requested_power_kw == 0.0,
            "initialized actuator should have zero previous power");
    }
}

static void test_null_actuator_initialization_is_rejected(void)
{
    const GridFlexActuatorStatus status =
        gridflex_simulated_actuator_init(
            NULL,
            GRIDFLEX_ACTUATOR_TYPE_BATTERY);

    expect_true(
        status ==
            GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT,
        "null simulated actuator should be rejected");
}

static void test_unknown_actuator_type_is_rejected(void)
{
    GridFlexSimulatedActuator simulated_actuator;

    const GridFlexActuatorStatus status =
        gridflex_simulated_actuator_init(
            &simulated_actuator,
            GRIDFLEX_ACTUATOR_TYPE_UNKNOWN);

    expect_true(
        status ==
            GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT,
        "unknown simulated actuator type should be rejected");
}

static void test_battery_command_can_be_applied_through_generic_interface(void)
{
    GridFlexSimulatedActuator simulated_actuator;

    GridFlexActuatorStatus status =
        gridflex_simulated_actuator_init(
            &simulated_actuator,
            GRIDFLEX_ACTUATOR_TYPE_BATTERY);

    expect_true(
        status == GRIDFLEX_ACTUATOR_STATUS_OK,
        "simulated battery initialization should succeed");

    GridFlexActuator actuator =
        gridflex_simulated_actuator_as_actuator(
            &simulated_actuator);

    const GridFlexActuatorCommand command = {
        GRIDFLEX_ACTUATOR_ACTION_CHARGE,
        25.0};

    status =
        gridflex_actuator_apply(
            &actuator,
            &command);

    expect_true(
        status == GRIDFLEX_ACTUATOR_STATUS_OK,
        "generic battery command should succeed");

    expect_true(
        simulated_actuator.apply_count == 1,
        "successful command should increment apply count");

    expect_true(
        simulated_actuator.last_action ==
            GRIDFLEX_ACTUATOR_ACTION_CHARGE,
        "successful command should record action");

    expect_true(
        simulated_actuator.last_requested_power_kw == 25.0,
        "successful command should record requested power");
}

static void test_supported_commands_work_for_each_actuator_type(void)
{
    typedef struct SupportedCommandCase
    {
        GridFlexActuatorType type;
        GridFlexActuatorAction action;
        double requested_power_kw;
    } SupportedCommandCase;

    const SupportedCommandCase cases[] = {
        {GRIDFLEX_ACTUATOR_TYPE_BATTERY,
         GRIDFLEX_ACTUATOR_ACTION_DISCHARGE,
         20.0},
        {GRIDFLEX_ACTUATOR_TYPE_GRID_CONNECTION,
         GRIDFLEX_ACTUATOR_ACTION_EXPORT,
         15.0},
        {GRIDFLEX_ACTUATOR_TYPE_EV_CHARGER,
         GRIDFLEX_ACTUATOR_ACTION_CHARGE,
         7.4}};

    const size_t case_count =
        sizeof(cases) /
        sizeof(cases[0]);

    size_t index;

    for (index = 0; index < case_count; ++index)
    {
        GridFlexSimulatedActuator simulated_actuator;

        GridFlexActuatorStatus status =
            gridflex_simulated_actuator_init(
                &simulated_actuator,
                cases[index].type);

        expect_true(
            status == GRIDFLEX_ACTUATOR_STATUS_OK,
            "simulated actuator initialization should succeed");

        GridFlexActuator actuator =
            gridflex_simulated_actuator_as_actuator(
                &simulated_actuator);

        const GridFlexActuatorCommand command = {
            cases[index].action,
            cases[index].requested_power_kw};

        status =
            gridflex_actuator_apply(
                &actuator,
                &command);

        expect_true(
            status == GRIDFLEX_ACTUATOR_STATUS_OK,
            "supported simulated command should succeed");

        expect_true(
            simulated_actuator.apply_count == 1,
            "supported command should reach simulated driver");

        expect_true(
            simulated_actuator.last_action ==
                cases[index].action,
            "simulated driver should preserve action");

        expect_true(
            simulated_actuator.last_requested_power_kw ==
                cases[index].requested_power_kw,
            "simulated driver should preserve requested power");
    }
}

static void test_idle_command_can_be_applied(void)
{
    GridFlexSimulatedActuator simulated_actuator;

    GridFlexActuatorStatus status =
        gridflex_simulated_actuator_init(
            &simulated_actuator,
            GRIDFLEX_ACTUATOR_TYPE_GRID_CONNECTION);

    expect_true(
        status == GRIDFLEX_ACTUATOR_STATUS_OK,
        "simulated grid actuator initialization should succeed");

    GridFlexActuator actuator =
        gridflex_simulated_actuator_as_actuator(
            &simulated_actuator);

    const GridFlexActuatorCommand command = {
        GRIDFLEX_ACTUATOR_ACTION_IDLE,
        0.0};

    status =
        gridflex_actuator_apply(
            &actuator,
            &command);

    expect_true(
        status == GRIDFLEX_ACTUATOR_STATUS_OK,
        "idle command should succeed");

    expect_true(
        simulated_actuator.last_action ==
            GRIDFLEX_ACTUATOR_ACTION_IDLE,
        "idle command should be recorded");

    expect_true(
        simulated_actuator.last_requested_power_kw == 0.0,
        "idle command should record zero requested power");
}

static void test_successive_commands_update_last_successful_command(void)
{
    GridFlexSimulatedActuator simulated_actuator;

    GridFlexActuatorStatus status =
        gridflex_simulated_actuator_init(
            &simulated_actuator,
            GRIDFLEX_ACTUATOR_TYPE_BATTERY);

    expect_true(
        status == GRIDFLEX_ACTUATOR_STATUS_OK,
        "simulated battery initialization should succeed");

    GridFlexActuator actuator =
        gridflex_simulated_actuator_as_actuator(
            &simulated_actuator);

    const GridFlexActuatorCommand charge_command = {
        GRIDFLEX_ACTUATOR_ACTION_CHARGE,
        30.0};

    status =
        gridflex_actuator_apply(
            &actuator,
            &charge_command);

    expect_true(
        status == GRIDFLEX_ACTUATOR_STATUS_OK,
        "first battery command should succeed");

    const GridFlexActuatorCommand discharge_command = {
        GRIDFLEX_ACTUATOR_ACTION_DISCHARGE,
        12.0};

    status =
        gridflex_actuator_apply(
            &actuator,
            &discharge_command);

    expect_true(
        status == GRIDFLEX_ACTUATOR_STATUS_OK,
        "second battery command should succeed");

    expect_true(
        simulated_actuator.apply_count == 2,
        "two commands should produce two apply attempts");

    expect_true(
        simulated_actuator.last_action ==
            GRIDFLEX_ACTUATOR_ACTION_DISCHARGE,
        "latest successful action should be retained");

    expect_true(
        simulated_actuator.last_requested_power_kw == 12.0,
        "latest successful power should be retained");
}

static void test_apply_failure_can_be_simulated(void)
{
    GridFlexSimulatedActuator simulated_actuator;

    GridFlexActuatorStatus status =
        gridflex_simulated_actuator_init(
            &simulated_actuator,
            GRIDFLEX_ACTUATOR_TYPE_BATTERY);

    expect_true(
        status == GRIDFLEX_ACTUATOR_STATUS_OK,
        "simulated battery initialization should succeed");

    GridFlexActuator actuator =
        gridflex_simulated_actuator_as_actuator(
            &simulated_actuator);

    const GridFlexActuatorCommand successful_command = {
        GRIDFLEX_ACTUATOR_ACTION_CHARGE,
        25.0};

    status =
        gridflex_actuator_apply(
            &actuator,
            &successful_command);

    expect_true(
        status == GRIDFLEX_ACTUATOR_STATUS_OK,
        "initial battery command should succeed");

    status =
        gridflex_simulated_actuator_set_apply_failure(
            &simulated_actuator,
            1);

    expect_true(
        status == GRIDFLEX_ACTUATOR_STATUS_OK,
        "enabling simulated actuator failure should succeed");

    const GridFlexActuatorCommand failing_command = {
        GRIDFLEX_ACTUATOR_ACTION_DISCHARGE,
        10.0};

    status =
        gridflex_actuator_apply(
            &actuator,
            &failing_command);

    expect_true(
        status ==
            GRIDFLEX_ACTUATOR_STATUS_APPLY_FAILED,
        "simulated actuator failure should be propagated");

    expect_true(
        simulated_actuator.apply_count == 2,
        "failed command should still count as an apply attempt");

    expect_true(
        simulated_actuator.last_action ==
            GRIDFLEX_ACTUATOR_ACTION_CHARGE,
        "failed command should preserve last successful action");

    expect_true(
        simulated_actuator.last_requested_power_kw == 25.0,
        "failed command should preserve last successful power");
}

static void test_actuator_can_recover_after_failure(void)
{
    GridFlexSimulatedActuator simulated_actuator;

    GridFlexActuatorStatus status =
        gridflex_simulated_actuator_init(
            &simulated_actuator,
            GRIDFLEX_ACTUATOR_TYPE_GRID_CONNECTION);

    expect_true(
        status == GRIDFLEX_ACTUATOR_STATUS_OK,
        "simulated grid actuator initialization should succeed");

    GridFlexActuator actuator =
        gridflex_simulated_actuator_as_actuator(
            &simulated_actuator);

    status =
        gridflex_simulated_actuator_set_apply_failure(
            &simulated_actuator,
            1);

    expect_true(
        status == GRIDFLEX_ACTUATOR_STATUS_OK,
        "enabling simulated failure should succeed");

    const GridFlexActuatorCommand command = {
        GRIDFLEX_ACTUATOR_ACTION_IMPORT,
        18.0};

    status =
        gridflex_actuator_apply(
            &actuator,
            &command);

    expect_true(
        status ==
            GRIDFLEX_ACTUATOR_STATUS_APPLY_FAILED,
        "command should fail while failure mode is enabled");

    status =
        gridflex_simulated_actuator_set_apply_failure(
            &simulated_actuator,
            0);

    expect_true(
        status == GRIDFLEX_ACTUATOR_STATUS_OK,
        "disabling simulated failure should succeed");

    status =
        gridflex_actuator_apply(
            &actuator,
            &command);

    expect_true(
        status == GRIDFLEX_ACTUATOR_STATUS_OK,
        "actuator should recover after failure is disabled");

    expect_true(
        simulated_actuator.apply_count == 2,
        "failed and successful attempts should both be counted");

    expect_true(
        simulated_actuator.last_action ==
            GRIDFLEX_ACTUATOR_ACTION_IMPORT,
        "recovered command should update last action");

    expect_true(
        simulated_actuator.last_requested_power_kw == 18.0,
        "recovered command should update requested power");
}

static void test_unsupported_command_is_rejected_before_driver(void)
{
    GridFlexSimulatedActuator simulated_actuator;

    GridFlexActuatorStatus status =
        gridflex_simulated_actuator_init(
            &simulated_actuator,
            GRIDFLEX_ACTUATOR_TYPE_BATTERY);

    expect_true(
        status == GRIDFLEX_ACTUATOR_STATUS_OK,
        "simulated battery initialization should succeed");

    GridFlexActuator actuator =
        gridflex_simulated_actuator_as_actuator(
            &simulated_actuator);

    const GridFlexActuatorCommand command = {
        GRIDFLEX_ACTUATOR_ACTION_IMPORT,
        10.0};

    status =
        gridflex_actuator_apply(
            &actuator,
            &command);

    expect_true(
        status ==
            GRIDFLEX_ACTUATOR_STATUS_UNSUPPORTED_ACTION,
        "unsupported battery action should be rejected");

    expect_true(
        simulated_actuator.apply_count == 0,
        "unsupported command should not reach simulated driver");
}

static void test_invalid_power_is_rejected_before_driver(void)
{
    GridFlexSimulatedActuator simulated_actuator;

    GridFlexActuatorStatus status =
        gridflex_simulated_actuator_init(
            &simulated_actuator,
            GRIDFLEX_ACTUATOR_TYPE_EV_CHARGER);

    expect_true(
        status == GRIDFLEX_ACTUATOR_STATUS_OK,
        "simulated EV actuator initialization should succeed");

    GridFlexActuator actuator =
        gridflex_simulated_actuator_as_actuator(
            &simulated_actuator);

    const GridFlexActuatorCommand command = {
        GRIDFLEX_ACTUATOR_ACTION_CHARGE,
        -7.4};

    status =
        gridflex_actuator_apply(
            &actuator,
            &command);

    expect_true(
        status ==
            GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT,
        "negative actuator power should be rejected");

    expect_true(
        simulated_actuator.apply_count == 0,
        "invalid power should not reach simulated driver");
}

static void test_null_simulated_actuator_view_is_safe(void)
{
    GridFlexActuator actuator =
        gridflex_simulated_actuator_as_actuator(
            NULL);

    const GridFlexActuatorCommand command = {
        GRIDFLEX_ACTUATOR_ACTION_IDLE,
        0.0};

    const GridFlexActuatorStatus status =
        gridflex_actuator_apply(
            &actuator,
            &command);

    expect_true(
        status ==
            GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT,
        "null simulated actuator view should produce invalid generic actuator");
}

static void test_null_failure_configuration_is_rejected(void)
{
    const GridFlexActuatorStatus status =
        gridflex_simulated_actuator_set_apply_failure(
            NULL,
            1);

    expect_true(
        status ==
            GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT,
        "null simulated actuator failure update should be rejected");
}

int main(void)
{
    test_supported_actuator_types_can_be_initialized();
    test_null_actuator_initialization_is_rejected();
    test_unknown_actuator_type_is_rejected();
    test_battery_command_can_be_applied_through_generic_interface();
    test_supported_commands_work_for_each_actuator_type();
    test_idle_command_can_be_applied();
    test_successive_commands_update_last_successful_command();
    test_apply_failure_can_be_simulated();
    test_actuator_can_recover_after_failure();
    test_unsupported_command_is_rejected_before_driver();
    test_invalid_power_is_rejected_before_driver();
    test_null_simulated_actuator_view_is_safe();
    test_null_failure_configuration_is_rejected();

    if (failures != 0)
    {
        fprintf(
            stderr,
            "%d simulated actuator test(s) failed\n",
            failures);

        return 1;
    }

    puts("All C simulated actuator tests passed.");

    return 0;
}
