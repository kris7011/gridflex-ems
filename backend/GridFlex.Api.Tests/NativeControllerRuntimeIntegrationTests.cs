using GridFlex.Api.Infrastructure.Native.Control;

namespace GridFlex.Api.Tests;

public sealed class NativeControllerRuntimeIntegrationTests
{
  [Fact]
  public void GetAbiVersionLoadsNativeLibraryAndReturnsExpectedVersion()
  {
    var actualAbiVersion =
      NativeControllerMethods.GetAbiVersion();

    Assert.Equal(
      NativeControllerMethods.ExpectedAbiVersion,
      actualAbiVersion);
  }

  [Fact]
  public void CreateAndDisposeControllerOwnsNativeHandle()
  {
    var limits =
      new NativeControllerLimits
      {
        MaxChargePowerKw = 10.0,
        MaxDischargePowerKw = 10.0,
        MinimumBatterySocKwh = 2.0,
        MaximumBatterySocKwh = 20.0
      };

    var status =
      NativeControllerMethods.Create(
        in limits,
        out var handle);

    Assert.Equal(
      NativeControllerStatus.Ok,
      status);

    Assert.False(handle.IsInvalid);

    using (handle)
    {
      Assert.False(handle.IsClosed);
    }

    Assert.True(handle.IsClosed);
  }
}
