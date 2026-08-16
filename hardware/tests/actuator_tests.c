#include <math.h>
#include <stddef.h>
#include <stdio.h>

#include "gridflex/hardware/actuator.h"

typedef struct FakeActuatorContext
{
    int apply_count;
    GridFlexActuatorAction last_action;
    double last_power_kw;
} FakeActuatorContext;

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

static GridFlexActuatorStatus successful_apply(
    void *context,
    const GridFlexActuatorCommand *command)
{
    FakeActuatorContext *fake_context = context;

    if (fake_context == NULL || command == NULL)
    {
        return GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT;
    }

    ++fake_context->apply_count;
    fake_context->last_action = command->action;
    fake_context->last_power_kw = command->requested_power_kw;

    return GRIDFLEX_ACTUATOR_STATUS_OK;
}

static GridFlexActuatorStatus failing_apply(
    void *context,
    const GridFlexActuatorCommand *command)
{
    (void)context;
    (void)command;

    return GRIDFLEX_ACTUATOR_STATUS_APPLY_FAILED;
}

static void test_supported_actions_are_applied(void)
{
    typedef struct SupportedActionCase
    {
        GridFlexActuatorType type;
        GridFlexActuatorAction action;
        double requested_power_kw;
    } SupportedActionCase;

    const SupportedActionCase cases[] = {
        {GRIDFLEX_ACTUATOR_TYPE_BATTERY,
         GRIDFLEX_ACTUATOR_ACTION_IDLE,
         0.0},
        {GRIDFLEX_ACTUATOR_TYPE_BATTERY,
         GRIDFLEX_ACTUATOR_ACTION_CHARGE,
         25.0},
        {GRIDFLEX_ACTUATOR_TYPE_BATTERY,
         GRIDFLEX_ACTUATOR_ACTION_DISCHARGE,
         25.0},
        {GRIDFLEX_ACTUATOR_TYPE_GRID_CONNECTION,
         GRIDFLEX_ACTUATOR_ACTION_IDLE,
         0.0},
        {GRIDFLEX_ACTUATOR_TYPE_GRID_CONNECTION,
         GRIDFLEX_ACTUATOR_ACTION_IMPORT,
         15.0},
        {GRIDFLEX_ACTUATOR_TYPE_GRID_CONNECTION,
         GRIDFLEX_ACTUATOR_ACTION_EXPORT,
         15.0},
        {GRIDFLEX_ACTUATOR_TYPE_EV_CHARGER,
         GRIDFLEX_ACTUATOR_ACTION_IDLE,
         0.0},
        {GRIDFLEX_ACTUATOR_TYPE_EV_CHARGER,
         GRIDFLEX_ACTUATOR_ACTION_CHARGE,
         7.4}};

    const size_t case_count =
        sizeof(cases) / sizeof(cases[0]);

    size_t index;

    for (index = 0; index < case_count; ++index)
    {
        FakeActuatorContext context = {
            0,
            GRIDFLEX_ACTUATOR_ACTION_UNKNOWN,
            0.0};

        GridFlexActuator actuator = {
            cases[index].type,
            successful_apply,
            &context};

        GridFlexActuatorCommand command = {
            cases[index].action,
            cases[index].requested_power_kw};

        const GridFlexActuatorStatus status =
            gridflex_actuator_apply(
                &actuator,
                &command);

        expect_true(
            status == GRIDFLEX_ACTUATOR_STATUS_OK,
            "supported actuator action should return OK");

        expect_true(
            context.apply_count == 1,
            "supported actuator action should invoke callback exactly once");

        expect_true(
            context.last_action ==
                cases[index].action,
            "callback should receive expected actuator action");

        expect_true(
            context.last_power_kw ==
                cases[index].requested_power_kw,
            "callback should receive expected requested power");
    }
}

static void test_null_actuator_is_rejected(void)
{
    GridFlexActuatorCommand command = {
        GRIDFLEX_ACTUATOR_ACTION_IDLE,
        0.0};

    const GridFlexActuatorStatus status =
        gridflex_actuator_apply(
            NULL,
            &command);

    expect_true(
        status ==
            GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT,
        "null actuator should be rejected");
}

static void test_null_command_is_rejected(void)
{
    GridFlexActuator actuator = {
        GRIDFLEX_ACTUATOR_TYPE_BATTERY,
        successful_apply,
        NULL};

    const GridFlexActuatorStatus status =
        gridflex_actuator_apply(
            &actuator,
            NULL);

    expect_true(
        status ==
            GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT,
        "null command should be rejected");
}

static void test_unknown_actuator_type_is_rejected(void)
{
    FakeActuatorContext context = {
        0,
        GRIDFLEX_ACTUATOR_ACTION_UNKNOWN,
        0.0};

    GridFlexActuator actuator = {
        GRIDFLEX_ACTUATOR_TYPE_UNKNOWN,
        successful_apply,
        &context};

    GridFlexActuatorCommand command = {
        GRIDFLEX_ACTUATOR_ACTION_IDLE,
        0.0};

    const GridFlexActuatorStatus status =
        gridflex_actuator_apply(
            &actuator,
            &command);

    expect_true(
        status ==
            GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT,
        "unknown actuator type should be rejected");

    expect_true(
        context.apply_count == 0,
        "invalid actuator type should not invoke callback");
}

static void test_unknown_action_is_rejected(void)
{
    FakeActuatorContext context = {
        0,
        GRIDFLEX_ACTUATOR_ACTION_UNKNOWN,
        0.0};

    GridFlexActuator actuator = {
        GRIDFLEX_ACTUATOR_TYPE_BATTERY,
        successful_apply,
        &context};

    GridFlexActuatorCommand command = {
        GRIDFLEX_ACTUATOR_ACTION_UNKNOWN,
        0.0};

    const GridFlexActuatorStatus status =
        gridflex_actuator_apply(
            &actuator,
            &command);

    expect_true(
        status ==
            GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT,
        "unknown actuator action should be rejected");

    expect_true(
        context.apply_count == 0,
        "invalid actuator action should not invoke callback");
}

static void test_unsupported_action_is_rejected(void)
{
    FakeActuatorContext context = {
        0,
        GRIDFLEX_ACTUATOR_ACTION_UNKNOWN,
        0.0};

    GridFlexActuator actuator = {
        GRIDFLEX_ACTUATOR_TYPE_BATTERY,
        successful_apply,
        &context};

    GridFlexActuatorCommand command = {
        GRIDFLEX_ACTUATOR_ACTION_IMPORT,
        10.0};

    const GridFlexActuatorStatus status =
        gridflex_actuator_apply(
            &actuator,
            &command);

    expect_true(
        status ==
            GRIDFLEX_ACTUATOR_STATUS_UNSUPPORTED_ACTION,
        "battery import action should be rejected");

    expect_true(
        context.apply_count == 0,
        "unsupported action should not invoke callback");
}

static void test_negative_power_is_rejected(void)
{
    FakeActuatorContext context = {
        0,
        GRIDFLEX_ACTUATOR_ACTION_UNKNOWN,
        0.0};

    GridFlexActuator actuator = {
        GRIDFLEX_ACTUATOR_TYPE_BATTERY,
        successful_apply,
        &context};

    GridFlexActuatorCommand command = {
        GRIDFLEX_ACTUATOR_ACTION_CHARGE,
        -5.0};

    const GridFlexActuatorStatus status =
        gridflex_actuator_apply(
            &actuator,
            &command);

    expect_true(
        status ==
            GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT,
        "negative actuator power should be rejected");

    expect_true(
        context.apply_count == 0,
        "invalid power should not invoke callback");
}

static void test_nan_power_is_rejected(void)
{
    FakeActuatorContext context = {
        0,
        GRIDFLEX_ACTUATOR_ACTION_UNKNOWN,
        0.0};

    GridFlexActuator actuator = {
        GRIDFLEX_ACTUATOR_TYPE_BATTERY,
        successful_apply,
        &context};

    GridFlexActuatorCommand command = {
        GRIDFLEX_ACTUATOR_ACTION_CHARGE,
        NAN};

    const GridFlexActuatorStatus status =
        gridflex_actuator_apply(
            &actuator,
            &command);

    expect_true(
        status ==
            GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT,
        "NaN actuator power should be rejected");

    expect_true(
        context.apply_count == 0,
        "NaN power should not invoke callback");
}

static void test_infinite_power_is_rejected(void)
{
    FakeActuatorContext context = {
        0,
        GRIDFLEX_ACTUATOR_ACTION_UNKNOWN,
        0.0};

    GridFlexActuator actuator = {
        GRIDFLEX_ACTUATOR_TYPE_GRID_CONNECTION,
        successful_apply,
        &context};

    GridFlexActuatorCommand command = {
        GRIDFLEX_ACTUATOR_ACTION_EXPORT,
        INFINITY};

    const GridFlexActuatorStatus status =
        gridflex_actuator_apply(
            &actuator,
            &command);

    expect_true(
        status ==
            GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT,
        "infinite actuator power should be rejected");

    expect_true(
        context.apply_count == 0,
        "infinite power should not invoke callback");
}

static void test_zero_power_for_active_action_is_rejected(void)
{
    FakeActuatorContext context = {
        0,
        GRIDFLEX_ACTUATOR_ACTION_UNKNOWN,
        0.0};

    GridFlexActuator actuator = {
        GRIDFLEX_ACTUATOR_TYPE_BATTERY,
        successful_apply,
        &context};

    GridFlexActuatorCommand command = {
        GRIDFLEX_ACTUATOR_ACTION_DISCHARGE,
        0.0};

    const GridFlexActuatorStatus status =
        gridflex_actuator_apply(
            &actuator,
            &command);

    expect_true(
        status ==
            GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT,
        "active actuator action should require positive power");

    expect_true(
        context.apply_count == 0,
        "zero active power should not invoke callback");
}

static void test_nonzero_idle_power_is_rejected(void)
{
    FakeActuatorContext context = {
        0,
        GRIDFLEX_ACTUATOR_ACTION_UNKNOWN,
        0.0};

    GridFlexActuator actuator = {
        GRIDFLEX_ACTUATOR_TYPE_BATTERY,
        successful_apply,
        &context};

    GridFlexActuatorCommand command = {
        GRIDFLEX_ACTUATOR_ACTION_IDLE,
        5.0};

    const GridFlexActuatorStatus status =
        gridflex_actuator_apply(
            &actuator,
            &command);

    expect_true(
        status ==
            GRIDFLEX_ACTUATOR_STATUS_INVALID_ARGUMENT,
        "idle action should require zero power");

    expect_true(
        context.apply_count == 0,
        "invalid idle power should not invoke callback");
}

static void test_missing_callback_is_rejected(void)
{
    GridFlexActuator actuator = {
        GRIDFLEX_ACTUATOR_TYPE_BATTERY,
        NULL,
        NULL};

    GridFlexActuatorCommand command = {
        GRIDFLEX_ACTUATOR_ACTION_IDLE,
        0.0};

    const GridFlexActuatorStatus status =
        gridflex_actuator_apply(
            &actuator,
            &command);

    expect_true(
        status ==
            GRIDFLEX_ACTUATOR_STATUS_NOT_CONFIGURED,
        "actuator without callback should be rejected");
}

static void test_apply_failure_is_propagated(void)
{
    GridFlexActuator actuator = {
        GRIDFLEX_ACTUATOR_TYPE_GRID_CONNECTION,
        failing_apply,
        NULL};

    GridFlexActuatorCommand command = {
        GRIDFLEX_ACTUATOR_ACTION_EXPORT,
        15.0};

    const GridFlexActuatorStatus status =
        gridflex_actuator_apply(
            &actuator,
            &command);

    expect_true(
        status ==
            GRIDFLEX_ACTUATOR_STATUS_APPLY_FAILED,
        "actuator callback failure should be propagated");
}

int main(void)
{
    test_supported_actions_are_applied();
    test_null_actuator_is_rejected();
    test_null_command_is_rejected();
    test_unknown_actuator_type_is_rejected();
    test_unknown_action_is_rejected();
    test_unsupported_action_is_rejected();
    test_negative_power_is_rejected();
    test_nan_power_is_rejected();
    test_infinite_power_is_rejected();
    test_zero_power_for_active_action_is_rejected();
    test_nonzero_idle_power_is_rejected();
    test_missing_callback_is_rejected();
    test_apply_failure_is_propagated();

    if (failures != 0)
    {
        fprintf(
            stderr,
            "%d actuator test(s) failed\n",
            failures);

        return 1;
    }

    puts("All C hardware actuator tests passed.");

    return 0;
}
