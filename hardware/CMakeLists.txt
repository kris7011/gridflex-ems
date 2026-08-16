cmake_minimum_required(VERSION 3.25)

project(
    GridFlexHardware
    VERSION 0.1.0
    DESCRIPTION "C hardware abstraction layer for GridFlex EMS"
    LANGUAGES C
)

add_library(
    gridflex_hardware
    STATIC
    src/hardware.c
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
    gridflex_hardware
    gridflex_hardware_cli
    PROPERTIES
        C_EXTENSIONS OFF
)

if(MSVC)
    target_compile_options(
        gridflex_hardware
        PRIVATE
            /W4
    )

    target_compile_options(
        gridflex_hardware_cli
        PRIVATE
            /W4
    )
else()
    target_compile_options(
        gridflex_hardware
        PRIVATE
            -Wall
            -Wextra
            -Wpedantic
    )

    target_compile_options(
        gridflex_hardware_cli
        PRIVATE
            -Wall
            -Wextra
            -Wpedantic
    )
endif()
