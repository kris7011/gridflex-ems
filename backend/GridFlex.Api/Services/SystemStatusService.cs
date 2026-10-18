using System.Diagnostics;
using System.Reflection;
using GridFlex.Api.Application.Control;
using GridFlex.Api.Contracts;
using Microsoft.Extensions.Hosting;

namespace GridFlex.Api.Services;

public sealed class SystemStatusService : ISystemStatusService
{
  private const string ServiceName = "GridFlex.Api";
  private const string HealthyStatus = "healthy";
  private const string DegradedStatus = "degraded";

  private static readonly string Version =
    typeof(SystemStatusService).Assembly
      .GetCustomAttribute<AssemblyInformationalVersionAttribute>()
      ?.InformationalVersion ??
    "unknown";

  private readonly IHostEnvironment _environment;
  private readonly IControllerDiagnostics _controllerDiagnostics;
  private readonly ControlDecisionStatistics _statistics;
  private readonly TimeProvider _timeProvider;
  private readonly DateTimeOffset _startedAt;

  public SystemStatusService(
    IHostEnvironment environment,
    IControllerDiagnostics controllerDiagnostics,
    ControlDecisionStatistics statistics,
    TimeProvider timeProvider)
  {
    ArgumentNullException.ThrowIfNull(environment);
    ArgumentNullException.ThrowIfNull(controllerDiagnostics);
    ArgumentNullException.ThrowIfNull(statistics);
    ArgumentNullException.ThrowIfNull(timeProvider);

    _environment = environment;
    _controllerDiagnostics = controllerDiagnostics;
    _statistics = statistics;
    _timeProvider = timeProvider;

    using var process = Process.GetCurrentProcess();

    _startedAt =
      new DateTimeOffset(
        process.StartTime.ToUniversalTime(),
        TimeSpan.Zero);
  }

  public SystemStatusResponse GetStatus()
  {
    var controller =
      _controllerDiagnostics.GetDiagnostics();

    var decisions =
      _statistics.GetSnapshot();

    var uptime =
      _timeProvider.GetUtcNow() - _startedAt;

    return new SystemStatusResponse(
      Service: ServiceName,
      // Previously always "healthy", even when the native controller
      // could not be loaded and readiness answered 503.
      Status:
        controller.Ready
          ? HealthyStatus
          : DegradedStatus,
      Environment: _environment.EnvironmentName,
      Version: Version,
      StartedAt: _startedAt,
      UptimeSeconds: Math.Max(0, (long)uptime.TotalSeconds),
      NativeController:
        new NativeControllerStatusResponse(
          Ready: controller.Ready,
          AbiVersion: controller.AbiVersion,
          Limits:
            new ControllerLimitsResponse(
              controller.Limits.MaxChargePowerKw,
              controller.Limits.MaxDischargePowerKw,
              controller.Limits.MinimumBatterySocKwh,
              controller.Limits.MaximumBatterySocKwh)),
      Decisions:
        new ControlDecisionStatisticsResponse(
          Decided: decisions.Decided,
          DecidedByAction:
            decisions.DecidedByAction.ToDictionary(
              static entry => entry.Key.ToString(),
              static entry => entry.Value),
          Rejected: decisions.Rejected,
          Failed: decisions.Failed,
          LastDecisionAt: decisions.LastDecisionAt));
  }
}
