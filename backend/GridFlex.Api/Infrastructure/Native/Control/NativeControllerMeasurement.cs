using System.Runtime.InteropServices;

namespace GridFlex.Api.Infrastructure.Native.Control;

[StructLayout(LayoutKind.Sequential)]
internal struct NativeControllerMeasurement
{
  internal ulong StepNumber;
  internal double ElapsedTimeHours;
  internal double IntervalHours;
  internal double GeneratedEnergyKwh;
  internal double ConsumedEnergyKwh;
  internal double NetEnergyKwh;
  internal double BatteryStateOfChargeKwh;
  internal double GridImportEnergyKwh;
  internal double GridExportEnergyKwh;
  internal double UnresolvedEnergyKwh;
}
