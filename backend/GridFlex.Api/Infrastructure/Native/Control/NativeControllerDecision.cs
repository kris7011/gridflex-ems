using System.Runtime.InteropServices;

namespace GridFlex.Api.Infrastructure.Native.Control;

[StructLayout(LayoutKind.Sequential)]
internal struct NativeControllerDecision
{
  internal ulong SourceStepNumber;
  internal NativeControlAction Action;
  internal double RequestedPowerKw;
}
