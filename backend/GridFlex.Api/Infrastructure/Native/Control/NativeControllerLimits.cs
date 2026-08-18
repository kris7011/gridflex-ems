using System.Runtime.InteropServices;

namespace GridFlex.Api.Infrastructure.Native.Control;

[StructLayout(LayoutKind.Sequential)]
internal struct NativeControllerLimits
{
  internal double MaxChargePowerKw;
  internal double MaxDischargePowerKw;
  internal double MinimumBatterySocKwh;
  internal double MaximumBatterySocKwh;
}
