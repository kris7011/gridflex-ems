using GridFlex.Api.Application.Control;

namespace GridFlex.Api.Tests;

public sealed class ControlDecisionServiceTests
{
  [Fact]
  public void DecideDelegatesMeasurementToControllerGateway()
  {
    var measurement = CreateMeasurement(stepNumber: 42);

    var expectedDecision =
      new ControlDecision(
        SourceStepNumber: 42,
        Action: ControlAction.ChargeBattery,
        RequestedPowerKw: 12.5);

    var gateway =
      new RecordingControllerGateway(expectedDecision);

    var service =
      new ControlDecisionService(gateway);

    var actualDecision =
      service.Decide(measurement);

    Assert.Same(measurement, gateway.LastMeasurement);
    Assert.Equal(1, gateway.DecideCallCount);
    Assert.Equal(expectedDecision, actualDecision);
  }

  [Fact]
  public void DecideRejectsMissingControllerDecision()
  {
    var measurement = CreateMeasurement(stepNumber: 42);

    var gateway =
      new RecordingControllerGateway(decision: null);

    var service =
      new ControlDecisionService(gateway);

    var exception =
      Assert.Throws<InvalidOperationException>(
        () => service.Decide(measurement));

    Assert.Equal(
      "Controller gateway returned no decision.",
      exception.Message);

    Assert.Equal(1, gateway.DecideCallCount);
  }

  [Fact]
  public void DecideRejectsDecisionForDifferentMeasurementStep()
  {
    var measurement = CreateMeasurement(stepNumber: 42);

    var mismatchedDecision =
      new ControlDecision(
        SourceStepNumber: 41,
        Action: ControlAction.Idle,
        RequestedPowerKw: 0.0);

    var gateway =
      new RecordingControllerGateway(mismatchedDecision);

    var service =
      new ControlDecisionService(gateway);

    var exception =
      Assert.Throws<InvalidOperationException>(
        () => service.Decide(measurement));

    Assert.Equal(
      "Controller decision source step does not match the measurement step.",
      exception.Message);
  }

  [Fact]
  public void ConstructorRejectsNullControllerGateway()
  {
    Assert.Throws<ArgumentNullException>(
      () => new ControlDecisionService(null!));
  }

  [Fact]
  public void DecideRejectsNullMeasurement()
  {
    var gateway =
      new RecordingControllerGateway(
        new ControlDecision(
          SourceStepNumber: 1,
          Action: ControlAction.Idle,
          RequestedPowerKw: 0.0));

    var service =
      new ControlDecisionService(gateway);

    Assert.Throws<ArgumentNullException>(
      () => service.Decide(null!));

    Assert.Equal(0, gateway.DecideCallCount);
  }

  private static EnergyMeasurementInput CreateMeasurement(
    ulong stepNumber)
  {
    return new EnergyMeasurementInput(
      StepNumber: stepNumber,
      ElapsedTimeHours: 1.0,
      IntervalHours: 0.25,
      GeneratedEnergyKwh: 5.0,
      ConsumedEnergyKwh: 2.0,
      NetEnergyKwh: 3.0,
      BatteryStateOfChargeKwh: 10.0,
      GridImportEnergyKwh: 0.0,
      GridExportEnergyKwh: 0.0,
      UnresolvedEnergyKwh: 0.0);
  }

  private sealed class RecordingControllerGateway
    : IControllerGateway
  {
    private readonly ControlDecision? _decision;

    public RecordingControllerGateway(
      ControlDecision? decision)
    {
      _decision = decision;
    }

    public EnergyMeasurementInput? LastMeasurement
    {
      get;
      private set;
    }

    public int DecideCallCount
    {
      get;
      private set;
    }

    public ControlDecision Decide(
      EnergyMeasurementInput measurement)
    {
      LastMeasurement = measurement;
      DecideCallCount++;

      return _decision!;
    }
  }
}
