using GridFlex.Api.Application.Control;
using GridFlex.Api.Infrastructure.Native.Control;

namespace GridFlex.Api.Tests;

public sealed class NativeControllerGatewayIntegrationTests
{
  [Fact]
  public void DecideMapsSurplusMeasurementToChargeDecision()
  {
    using var gateway =
      new NativeControllerGateway(CreateValidLimits());

    var measurement =
      CreateMeasurement(
        stepNumber: 42,
        generatedEnergyKwh: 5.0,
        consumedEnergyKwh: 2.0,
        netEnergyKwh: 3.0);

    var decision =
      gateway.Decide(measurement);

    Assert.Equal(42UL, decision.SourceStepNumber);
    Assert.Equal(
      ControlAction.ChargeBattery,
      decision.Action);
    Assert.Equal(
      10.0,
      decision.RequestedPowerKw,
      precision: 10);
  }

  [Fact]
  public void DecideMapsDeficitMeasurementToDischargeDecision()
  {
    using var gateway =
      new NativeControllerGateway(CreateValidLimits());

    var measurement =
      CreateMeasurement(
        stepNumber: 43,
        generatedEnergyKwh: 1.0,
        consumedEnergyKwh: 3.0,
        netEnergyKwh: -2.0);

    var decision =
      gateway.Decide(measurement);

    Assert.Equal(43UL, decision.SourceStepNumber);
    Assert.Equal(
      ControlAction.DischargeBattery,
      decision.Action);
    Assert.Equal(
      8.0,
      decision.RequestedPowerKw,
      precision: 10);
  }

  [Fact]
  public void DecideMapsBalancedMeasurementToIdleDecision()
  {
    using var gateway =
      new NativeControllerGateway(CreateValidLimits());

    var measurement =
      CreateMeasurement(
        stepNumber: 44,
        generatedEnergyKwh: 2.0,
        consumedEnergyKwh: 2.0,
        netEnergyKwh: 0.0);

    var decision =
      gateway.Decide(measurement);

    Assert.Equal(44UL, decision.SourceStepNumber);
    Assert.Equal(
      ControlAction.Idle,
      decision.Action);
    Assert.Equal(
      0.0,
      decision.RequestedPowerKw,
      precision: 10);
  }

  [Fact]
  public void ConstructorRejectsInvalidNativeLimits()
  {
    var invalidLimits =
      new NativeControllerLimits
      {
        MaxChargePowerKw = 0.0,
        MaxDischargePowerKw = 8.0,
        MinimumBatterySocKwh = 2.0,
        MaximumBatterySocKwh = 20.0
      };

    var exception =
      Assert.Throws<ArgumentException>(
        () => new NativeControllerGateway(
          invalidLimits));

    Assert.Equal(
      "limits",
      exception.ParamName);
  }

  [Fact]
  public void DecideRejectsInvalidMeasurement()
  {
    using var gateway =
      new NativeControllerGateway(CreateValidLimits());

    var measurement =
      CreateMeasurement(
        stepNumber: 0,
        generatedEnergyKwh: 5.0,
        consumedEnergyKwh: 2.0,
        netEnergyKwh: 3.0);

    var exception =
      Assert.Throws<ArgumentException>(
        () => gateway.Decide(measurement));

    Assert.Equal(
      "measurement",
      exception.ParamName);
  }

  [Fact]
  public void DecideRejectsCallsAfterDisposal()
  {
    var gateway =
      new NativeControllerGateway(CreateValidLimits());

    gateway.Dispose();

    var measurement =
      CreateMeasurement(
        stepNumber: 45,
        generatedEnergyKwh: 5.0,
        consumedEnergyKwh: 2.0,
        netEnergyKwh: 3.0);

    Assert.Throws<ObjectDisposedException>(
      () => gateway.Decide(measurement));
  }

  [Fact]
  public void DecideRejectsNullMeasurement()
  {
    using var gateway =
      new NativeControllerGateway(CreateValidLimits());

    Assert.Throws<ArgumentNullException>(
      () => gateway.Decide(null!));
  }

  private static NativeControllerLimits CreateValidLimits()
  {
    return new NativeControllerLimits
    {
      MaxChargePowerKw = 10.0,
      MaxDischargePowerKw = 8.0,
      MinimumBatterySocKwh = 2.0,
      MaximumBatterySocKwh = 20.0
    };
  }

  private static EnergyMeasurementInput CreateMeasurement(
    ulong stepNumber,
    double generatedEnergyKwh,
    double consumedEnergyKwh,
    double netEnergyKwh)
  {
    return new EnergyMeasurementInput(
      StepNumber: stepNumber,
      ElapsedTimeHours: 1.0,
      IntervalHours: 0.25,
      GeneratedEnergyKwh: generatedEnergyKwh,
      ConsumedEnergyKwh: consumedEnergyKwh,
      NetEnergyKwh: netEnergyKwh,
      BatteryStateOfChargeKwh: 10.0,
      GridImportEnergyKwh: 0.0,
      GridExportEnergyKwh: 0.0,
      UnresolvedEnergyKwh: 0.0);
  }
}
