using System.Text.Json.Serialization;

namespace GridFlex.Api.Contracts;

/// <summary>
/// One energy measurement for which the controller decides an action.
/// </summary>
/// <remarks>
/// Every property is required, and unknown properties are rejected. A
/// property that is missing or misspelled would otherwise be bound as 0
/// and silently produce a decision for a different measurement (for
/// example, a battery state of charge of 0 kWh).
/// </remarks>
[JsonUnmappedMemberHandling(JsonUnmappedMemberHandling.Disallow)]
public sealed record ControlDecisionRequest(
  ulong StepNumber,
  double ElapsedTimeHours,
  double IntervalHours,
  double GeneratedEnergyKwh,
  double ConsumedEnergyKwh,
  double NetEnergyKwh,
  double BatteryStateOfChargeKwh,
  double GridImportEnergyKwh,
  double GridExportEnergyKwh,
  double UnresolvedEnergyKwh);
