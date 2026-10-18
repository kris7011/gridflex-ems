using System.Diagnostics.Metrics;
using GridFlex.Api.Application.Control;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Microsoft.Extensions.Options;

namespace GridFlex.Api.Infrastructure.Native.Control;

internal static class NativeControllerServiceCollectionExtensions
{
  internal static IServiceCollection AddNativeController(
    this IServiceCollection services)
  {
    ArgumentNullException.ThrowIfNull(services);

    services
      .AddOptions<NativeControllerOptions>()
      .BindConfiguration(
        NativeControllerOptions.SectionName)
      .Validate(
        static options =>
          double.IsFinite(
            options.MaxChargePowerKw) &&
          options.MaxChargePowerKw > 0.0 &&
          double.IsFinite(
            options.MaxDischargePowerKw) &&
          options.MaxDischargePowerKw > 0.0 &&
          double.IsFinite(
            options.MinimumBatterySocKwh) &&
          options.MinimumBatterySocKwh >= 0.0 &&
          double.IsFinite(
            options.MaximumBatterySocKwh) &&
          options.MaximumBatterySocKwh >
            options.MinimumBatterySocKwh,
        "Native controller configuration is invalid.")
      .ValidateOnStart();

    services.TryAddSingleton(TimeProvider.System);
    services.TryAddSingleton<ControlDecisionStatistics>();

    services.AddSingleton(
      static serviceProvider =>
      {
        var options =
          serviceProvider
            .GetRequiredService<
              IOptions<NativeControllerOptions>>()
            .Value;

        var limits =
          new NativeControllerLimits
          {
            MaxChargePowerKw =
              options.MaxChargePowerKw,
            MaxDischargePowerKw =
              options.MaxDischargePowerKw,
            MinimumBatterySocKwh =
              options.MinimumBatterySocKwh,
            MaximumBatterySocKwh =
              options.MaximumBatterySocKwh
          };

        return new NativeControllerGateway(limits);
      });

    // The application sees the native gateway only through the
    // instrumented decorator (metrics, statistics, structured logs).
    services.AddSingleton<IControllerGateway>(
      static serviceProvider =>
        new InstrumentedControllerGateway(
          serviceProvider.GetRequiredService<NativeControllerGateway>(),
          serviceProvider.GetRequiredService<ControlDecisionStatistics>(),
          serviceProvider.GetRequiredService<IMeterFactory>(),
          serviceProvider.GetRequiredService<TimeProvider>(),
          serviceProvider.GetRequiredService<
            ILogger<InstrumentedControllerGateway>>()));

    services.AddSingleton<
      IControllerDiagnostics,
      NativeControllerDiagnostics>();

    services
      .AddHealthChecks()
      .AddCheck<NativeControllerReadinessHealthCheck>(
        "native_controller",
        tags: ["ready"]);

    return services;
  }
}
