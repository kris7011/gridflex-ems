using System.Runtime.InteropServices;
using GridFlex.Api.Infrastructure.Native.Control;

namespace GridFlex.Api.Tests;

public sealed class NativeControllerInteropContractTests
{
  [Fact]
  public void StatusValuesMatchNativeAbi()
  {
    Assert.Equal(
      typeof(int),
      Enum.GetUnderlyingType(
        typeof(NativeControllerStatus)));

    Assert.Equal(
      0,
      (int)NativeControllerStatus.Ok);

    Assert.Equal(
      1,
      (int)NativeControllerStatus.InvalidArgument);

    Assert.Equal(
      2,
      (int)NativeControllerStatus.InvalidLimits);

    Assert.Equal(
      3,
      (int)NativeControllerStatus.InvalidMeasurement);

    Assert.Equal(
      4,
      (int)NativeControllerStatus.InternalError);
  }

  [Fact]
  public void ActionValuesMatchNativeAbi()
  {
    Assert.Equal(
      typeof(int),
      Enum.GetUnderlyingType(
        typeof(NativeControlAction)));

    Assert.Equal(
      0,
      (int)NativeControlAction.Idle);

    Assert.Equal(
      1,
      (int)NativeControlAction.ChargeBattery);

    Assert.Equal(
      2,
      (int)NativeControlAction.DischargeBattery);

    Assert.Equal(
      3,
      (int)NativeControlAction.ImportFromGrid);

    Assert.Equal(
      4,
      (int)NativeControlAction.ExportToGrid);
  }

  [Fact]
  public void ControllerLimitsLayoutMatchesNativeAbi()
  {
    Assert.Equal(
      32,
      Marshal.SizeOf<NativeControllerLimits>());

    Assert.Equal(
      0L,
      OffsetOf<NativeControllerLimits>(
        nameof(
          NativeControllerLimits.MaxChargePowerKw)));

    Assert.Equal(
      8L,
      OffsetOf<NativeControllerLimits>(
        nameof(
          NativeControllerLimits.MaxDischargePowerKw)));

    Assert.Equal(
      16L,
      OffsetOf<NativeControllerLimits>(
        nameof(
          NativeControllerLimits.MinimumBatterySocKwh)));

    Assert.Equal(
      24L,
      OffsetOf<NativeControllerLimits>(
        nameof(
          NativeControllerLimits.MaximumBatterySocKwh)));
  }

  [Fact]
  public void ControllerMeasurementLayoutMatchesNativeAbi()
  {
    Assert.Equal(
      80,
      Marshal.SizeOf<NativeControllerMeasurement>());

    Assert.Equal(
      0L,
      OffsetOf<NativeControllerMeasurement>(
        nameof(
          NativeControllerMeasurement.StepNumber)));

    Assert.Equal(
      8L,
      OffsetOf<NativeControllerMeasurement>(
        nameof(
          NativeControllerMeasurement.ElapsedTimeHours)));

    Assert.Equal(
      16L,
      OffsetOf<NativeControllerMeasurement>(
        nameof(
          NativeControllerMeasurement.IntervalHours)));

    Assert.Equal(
      24L,
      OffsetOf<NativeControllerMeasurement>(
        nameof(
          NativeControllerMeasurement.GeneratedEnergyKwh)));

    Assert.Equal(
      32L,
      OffsetOf<NativeControllerMeasurement>(
        nameof(
          NativeControllerMeasurement.ConsumedEnergyKwh)));

    Assert.Equal(
      40L,
      OffsetOf<NativeControllerMeasurement>(
        nameof(
          NativeControllerMeasurement.NetEnergyKwh)));

    Assert.Equal(
      48L,
      OffsetOf<NativeControllerMeasurement>(
        nameof(
          NativeControllerMeasurement.BatteryStateOfChargeKwh)));

    Assert.Equal(
      56L,
      OffsetOf<NativeControllerMeasurement>(
        nameof(
          NativeControllerMeasurement.GridImportEnergyKwh)));

    Assert.Equal(
      64L,
      OffsetOf<NativeControllerMeasurement>(
        nameof(
          NativeControllerMeasurement.GridExportEnergyKwh)));

    Assert.Equal(
      72L,
      OffsetOf<NativeControllerMeasurement>(
        nameof(
          NativeControllerMeasurement.UnresolvedEnergyKwh)));
  }

  [Fact]
  public void ControllerDecisionLayoutMatchesNativeAbi()
  {
    Assert.Equal(
      24,
      Marshal.SizeOf<NativeControllerDecision>());

    Assert.Equal(
      0L,
      OffsetOf<NativeControllerDecision>(
        nameof(
          NativeControllerDecision.SourceStepNumber)));

    Assert.Equal(
      8L,
      OffsetOf<NativeControllerDecision>(
        nameof(
          NativeControllerDecision.Action)));

    Assert.Equal(
      16L,
      OffsetOf<NativeControllerDecision>(
        nameof(
          NativeControllerDecision.RequestedPowerKw)));
  }

  [Fact]
  public void NativeMethodMetadataMatchesAbiVersionOne()
  {
    Assert.Equal(
      "gridflex_controller_native",
      NativeControllerMethods.LibraryName);

    Assert.Equal(
      1u,
      NativeControllerMethods.ExpectedAbiVersion);
  }

  private static long OffsetOf<T>(
    string fieldName)
    where T : struct
  {
    return Marshal
      .OffsetOf<T>(fieldName)
      .ToInt64();
  }
}
