#include <chrono>
#include <cstddef>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <string_view>

#include "gridflex/controller/control_command.hpp"
#include "gridflex/controller/controller_limits.hpp"
#include "gridflex/controller/energy_controller.hpp"
#include "gridflex/controller/energy_measurement.hpp"

namespace
{

    using gridflex::controller::ControlCommand;
    using gridflex::controller::ControllerLimits;
    using gridflex::controller::EnergyController;
    using gridflex::controller::EnergyMeasurement;

    constexpr std::size_t warmup_iterations = 100'000;
    constexpr std::size_t benchmark_iterations = 10'000'000;

    struct BenchmarkResult final
    {
        std::string_view name;
        double elapsed_seconds;
        double nanoseconds_per_decision;
        double decisions_per_second;
        double checksum;
    };

    [[nodiscard]] double command_checksum(
        const ControlCommand &command) noexcept
    {
        return static_cast<double>(command.source_step_number()) +
               static_cast<double>(command.action()) +
               command.requested_power_kw();
    }

    [[nodiscard]] BenchmarkResult run_benchmark(
        const std::string_view name,
        const EnergyController &controller,
        const EnergyMeasurement &measurement)
    {
        double checksum = 0.0;

        for (std::size_t iteration = 0;
             iteration < warmup_iterations;
             ++iteration)
        {
            const auto command =
                controller.decide(measurement);

            checksum += command_checksum(command);
        }

        const auto start =
            std::chrono::steady_clock::now();

        for (std::size_t iteration = 0;
             iteration < benchmark_iterations;
             ++iteration)
        {
            const auto command =
                controller.decide(measurement);

            checksum += command_checksum(command);
        }

        const auto end =
            std::chrono::steady_clock::now();

        const std::chrono::duration<double> elapsed =
            end - start;

        const double elapsed_seconds =
            elapsed.count();

        const double nanoseconds_per_decision =
            std::chrono::duration<double, std::nano>(
                end - start)
                .count() /
            static_cast<double>(benchmark_iterations);

        const double decisions_per_second =
            static_cast<double>(benchmark_iterations) /
            elapsed_seconds;

        return BenchmarkResult{
            name,
            elapsed_seconds,
            nanoseconds_per_decision,
            decisions_per_second,
            checksum};
    }

    void print_result(
        const BenchmarkResult &result)
    {
        std::cout
            << result.name << '\n'
            << "  Total measured time: "
            << std::fixed
            << std::setprecision(6)
            << result.elapsed_seconds
            << " s\n"
            << "  Average time:        "
            << std::setprecision(2)
            << result.nanoseconds_per_decision
            << " ns/decision\n"
            << "  Throughput:          "
            << std::setprecision(2)
            << result.decisions_per_second
            << " decisions/s\n"
            << "  Checksum:            "
            << std::setprecision(2)
            << result.checksum
            << "\n\n";
    }

}

int main()
{
    const ControllerLimits limits{
        25.0,
        30.0,
        10.0,
        90.0};

    const EnergyController controller{
        limits};

    const EnergyMeasurement surplus_measurement{
        1,
        1.0,
        0.25,
        35.0,
        30.0,
        5.0,
        50.0,
        0.0,
        0.0,
        0.0};

    const EnergyMeasurement deficit_measurement{
        2,
        1.0,
        0.25,
        30.0,
        35.0,
        -5.0,
        50.0,
        0.0,
        0.0,
        0.0};

    const EnergyMeasurement balanced_measurement{
        3,
        1.0,
        0.25,
        30.0,
        30.0,
        0.0,
        50.0,
        0.0,
        0.0,
        0.0};

    std::cout
        << "GridFlex EMS C++ Controller Benchmark\n\n"
        << "Warmup iterations per case: "
        << warmup_iterations
        << '\n'
        << "Measured iterations per case: "
        << benchmark_iterations
        << "\n\n";

    const auto surplus_result =
        run_benchmark(
            "Surplus decision",
            controller,
            surplus_measurement);

    const auto deficit_result =
        run_benchmark(
            "Deficit decision",
            controller,
            deficit_measurement);

    const auto balanced_result =
        run_benchmark(
            "Balanced decision",
            controller,
            balanced_measurement);

    print_result(surplus_result);
    print_result(deficit_result);
    print_result(balanced_result);

    return 0;
}
