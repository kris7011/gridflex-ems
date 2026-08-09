cmake_minimum_required(VERSION 3.25)

project(
    GridFlexController
    VERSION 0.1.0
    DESCRIPTION "C++ energy controller for GridFlex EMS"
    LANGUAGES CXX
)

include(CTest)

add_library(
    gridflex_controller
    STATIC
    src/control_command.cpp
    src/controller.cpp
    src/energy_controller.cpp
    src/energy_measurement.cpp
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

if(BUILD_TESTING)
    include(FetchContent)

    FetchContent_Declare(
        Catch2
        GIT_REPOSITORY https://github.com/catchorg/Catch2.git
        GIT_TAG v3.15.3
        GIT_SHALLOW TRUE
    )

    FetchContent_MakeAvailable(Catch2)

    add_executable(
        gridflex_controller_tests
        tests/control_command_tests.cpp
        tests/energy_controller_tests.cpp
        tests/energy_measurement_tests.cpp
    )

    target_link_libraries(
        gridflex_controller_tests
        PRIVATE
            gridflex_controller
            Catch2::Catch2WithMain
    )

    set_target_properties(
        gridflex_controller_tests
        PROPERTIES
            CXX_EXTENSIONS OFF
    )

    if(MSVC)
        target_compile_options(
            gridflex_controller_tests
            PRIVATE
                /W4
                /permissive-
        )
    else()
        target_compile_options(
            gridflex_controller_tests
            PRIVATE
                -Wall
                -Wextra
                -Wpedantic
        )
    endif()

    list(
        APPEND CMAKE_MODULE_PATH
        ${catch2_SOURCE_DIR}/extras
    )

    include(Catch)

    catch_discover_tests(
        gridflex_controller_tests
    )
endif()