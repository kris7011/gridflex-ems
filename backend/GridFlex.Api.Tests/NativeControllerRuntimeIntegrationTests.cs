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
}
