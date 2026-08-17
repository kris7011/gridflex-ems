cmake_minimum_required(VERSION 3.25)

project(
    GridFlexHardware
    VERSION 0.1.0
    DESCRIPTION "C hardware abstraction layer for GridFlex EMS"
    LANGUAGES C
)

include(CTest)

function(gridflex_enable_strict_c_warnings target)
    if(MSVC)
        target_compile_options(
            ${target}
            PRIVATE
                /W4
        )
    else()
        target_compile_options(
            ${target}
            PRIVATE
                -Wall
                -Wextra
                -Wpedantic
        )
    endif()
endfunction()

add_library(
    gridflex_hardware
    STATIC
    src/hardware.c
    src/sensor.c
    src/actuator.c
    src/simulated_sensor.c
    src/simulated_actuator.c
    src/error.c
)

target_include_directories(
    gridflex_hardware
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_compile_features(
    gridflex_hardware
    PUBLIC
        c_std_17
)

set_target_properties(
    gridflex_hardware
    PROPERTIES
        C_EXTENSIONS OFF
)

gridflex_enable_strict_c_warnings(
    gridflex_hardware
)

add_executable(
    gridflex_hardware_cli
    src/main.c
)

target_link_libraries(
    gridflex_hardware_cli
    PRIVATE
        gridflex_hardware
)

set_target_properties(
    gridflex_hardware_cli
    PROPERTIES
        C_EXTENSIONS OFF
)

gridflex_enable_strict_c_warnings(
    gridflex_hardware_cli
)

if(BUILD_TESTING)
    add_executable(
        gridflex_sensor_tests
        tests/sensor_tests.c
    )

    target_link_libraries(
        gridflex_sensor_tests
        PRIVATE
            gridflex_hardware
    )

    set_target_properties(
        gridflex_sensor_tests
        PROPERTIES
            C_EXTENSIONS OFF
    )

    gridflex_enable_strict_c_warnings(
        gridflex_sensor_tests
    )

    add_test(
        NAME gridflex_hardware_sensor_tests
        COMMAND gridflex_sensor_tests
    )

    add_executable(
        gridflex_actuator_tests
        tests/actuator_tests.c
    )

    target_link_libraries(
        gridflex_actuator_tests
        PRIVATE
            gridflex_hardware
    )

    set_target_properties(
        gridflex_actuator_tests
        PROPERTIES
            C_EXTENSIONS OFF
    )

    gridflex_enable_strict_c_warnings(
        gridflex_actuator_tests
    )

    add_test(
        NAME gridflex_hardware_actuator_tests
        COMMAND gridflex_actuator_tests
    )

    add_executable(
        gridflex_simulated_sensor_tests
        tests/simulated_sensor_tests.c
    )

    target_link_libraries(
        gridflex_simulated_sensor_tests
        PRIVATE
            gridflex_hardware
    )

    set_target_properties(
        gridflex_simulated_sensor_tests
        PROPERTIES
            C_EXTENSIONS OFF
    )

    gridflex_enable_strict_c_warnings(
        gridflex_simulated_sensor_tests
    )

    add_test(
        NAME gridflex_hardware_simulated_sensor_tests
        COMMAND gridflex_simulated_sensor_tests
    )

    add_executable(
        gridflex_simulated_actuator_tests
        tests/simulated_actuator_tests.c
    )

    target_link_libraries(
        gridflex_simulated_actuator_tests
        PRIVATE
            gridflex_hardware
    )

    set_target_properties(
        gridflex_simulated_actuator_tests
        PROPERTIES
            C_EXTENSIONS OFF
    )

    gridflex_enable_strict_c_warnings(
        gridflex_simulated_actuator_tests
    )

    add_test(
        NAME gridflex_hardware_simulated_actuator_tests
        COMMAND gridflex_simulated_actuator_tests
    )

    add_executable(
        gridflex_error_tests
        tests/error_tests.c
    )

    target_link_libraries(
        gridflex_error_tests
        PRIVATE
            gridflex_hardware
    )

    set_target_properties(
        gridflex_error_tests
        PROPERTIES
            C_EXTENSIONS OFF
    )

    gridflex_enable_strict_c_warnings(
        gridflex_error_tests
    )

    add_test(
        NAME gridflex_hardware_error_tests
        COMMAND gridflex_error_tests
    )
endif()
