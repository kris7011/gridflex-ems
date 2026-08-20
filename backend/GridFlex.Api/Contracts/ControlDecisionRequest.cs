namespace GridFlex.Api.Contracts;

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
