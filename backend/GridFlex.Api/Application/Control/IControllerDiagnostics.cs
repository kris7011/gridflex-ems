namespace GridFlex.Api.Application.Control;

/// <summary>
/// Read-only information about the controller for status reporting.
/// </summary>
public interface IControllerDiagnostics
{
  ControllerDiagnostics GetDiagnostics();
}

/// <param name="Ready">
/// Whether the controller could be initialised; the same condition as the
/// readiness health check.
/// </param>
/// <param name="AbiVersion">
/// The ABI version reported by the loaded native library, or
/// <see langword="null"/> if it could not be loaded.
/// </param>
public sealed record ControllerDiagnostics(
  bool Ready,
  uint? AbiVersion,
  ControllerLimitsInfo Limits);

public sealed record ControllerLimitsInfo(
  double MaxChargePowerKw,
  double MaxDischargePowerKw,
  double MinimumBatterySocKwh,
  double MaximumBatterySocKwh);
