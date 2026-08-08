cmake_minimum_required(VERSION 3.25)

project(
    GridFlexController
    VERSION 0.1.0
    DESCRIPTION "C++ energy controller for GridFlex EMS"
    LANGUAGES CXX
)

add_library(
    gridflex_controller
    STATIC
    src/controller.cpp
)

target_include_directories(
    gridflex_controller
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_compile_features(
    gridflex_controller
    PUBLIC
        cxx_std_20
)

add_executable(
    gridflex_controller_cli
    src/main.cpp
)

target_link_libraries(
    gridflex_controller_cli
    PRIVATE
        gridflex_controller
)

set_target_properties(
    gridflex_controller
    gridflex_controller_cli
    PROPERTIES
        CXX_EXTENSIONS OFF
)

if(MSVC)
    target_compile_options(
        gridflex_controller
        PRIVATE
            /W4
            /permissive-
    )

    target_compile_options(
        gridflex_controller_cli
        PRIVATE
            /W4
            /permissive-
    )
else()
    target_compile_options(
        gridflex_controller
        PRIVATE
            -Wall
            -Wextra
            -Wpedantic
    )

    target_compile_options(
        gridflex_controller_cli
        PRIVATE
            -Wall
            -Wextra
            -Wpedantic
    )
endif()