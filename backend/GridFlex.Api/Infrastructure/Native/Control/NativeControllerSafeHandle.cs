using Microsoft.Win32.SafeHandles;

namespace GridFlex.Api.Infrastructure.Native.Control;

internal sealed class NativeControllerSafeHandle
  : SafeHandleZeroOrMinusOneIsInvalid
{
  public NativeControllerSafeHandle()
    : base(ownsHandle: true)
  {
  }

  protected override bool ReleaseHandle()
  {
    NativeControllerMethods.Destroy(handle);

    return true;
  }
}
