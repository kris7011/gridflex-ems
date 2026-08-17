namespace GridFlex.Api.Application.Control;

public sealed record EnergyMeasurementInput(
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
