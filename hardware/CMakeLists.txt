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
        gridflex_hardware_tests
        tests/sensor_tests.c
    )

    target_link_libraries(
        gridflex_hardware_tests
        PRIVATE
            gridflex_hardware
    )

    set_target_properties(
        gridflex_hardware_tests
        PROPERTIES
            C_EXTENSIONS OFF
    )

    gridflex_enable_strict_c_warnings(
        gridflex_hardware_tests
    )

    add_test(
        NAME gridflex_hardware_sensor_tests
        COMMAND gridflex_hardware_tests
    )
endif()
