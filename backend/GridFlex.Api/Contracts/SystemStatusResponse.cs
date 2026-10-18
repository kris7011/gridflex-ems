namespace GridFlex.Api.Contracts;

/// <param name="Status">
/// "healthy" when the native controller is ready, otherwise "degraded".
/// </param>
public sealed record SystemStatusResponse(
  string Service,
  string Status,
  string Environment,
  string Version,
  DateTimeOffset StartedAt,
  long UptimeSeconds,
  NativeControllerStatusResponse NativeController,
  ControlDecisionStatisticsResponse Decisions);

public sealed record NativeControllerStatusResponse(
  bool Ready,
  uint? AbiVersion,
  ControllerLimitsResponse Limits);

public sealed record ControllerLimitsResponse(
  double MaxChargePowerKw,
  double MaxDischargePowerKw,
  double MinimumBatterySocKwh,
  double MaximumBatterySocKwh);

/// <summary>Decision counters since the process started.</summary>
public sealed record ControlDecisionStatisticsResponse(
  long Decided,
  IReadOnlyDictionary<string, long> DecidedByAction,
  long Rejected,
  long Failed,
  DateTimeOffset? LastDecisionAt);
