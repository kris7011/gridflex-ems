using System.Diagnostics.Metrics;
using GridFlex.Api.Application.Control;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging.Abstractions;

namespace GridFlex.Api.Tests;

public sealed class InstrumentedControllerGatewayTests
  : IDisposable
{
  private readonly ServiceProvider _services =
    new ServiceCollection()
      .AddMetrics()
      .BuildServiceProvider();

  private readonly ControlDecisionStatistics _statistics = new();

  private readonly List<RecordedMeasurement> _recorded = [];

  private readonly MeterListener _listener = new();

  public InstrumentedControllerGatewayTests()
  {
    var meterFactory =
      _services.GetRequiredService<IMeterFactory>();

    // Only this test's meter: other tests create meters with the same
    // name through their own factories.
    _listener.InstrumentPublished =
      (instrument, listener) =>
      {
        if (instrument.Meter.Name ==
              InstrumentedControllerGateway.MeterName &&
            ReferenceEquals(
              instrument.Meter.Scope,
              meterFactory))
        {
          listener.EnableMeasurementEvents(instrument);
        }
      };

    _listener.SetMeasurementEventCallback<long>(
      (instrument, value, tags, _) =>
        Record(instrument, value, tags));

    _listener.SetMeasurementEventCallback<double>(
      (instrument, value, tags, _) =>
        Record(instrument, value, tags));

    _listener.Start();
  }

  public void Dispose()
  {
    _listener.Dispose();
    _services.Dispose();
  }

  [Fact]
  public void SuccessfulDecisionIsCountedTimedAndAddedToStatistics()
  {
    var gateway =
      CreateGateway(
        _ => new ControlDecision(
          SourceStepNumber: 7,
          Action: ControlAction.ChargeBattery,
          RequestedPowerKw: 4.0));

    var decision =
      gateway.Decide(CreateMeasurement());

    Assert.Equal(ControlAction.ChargeBattery, decision.Action);

    var counted =
      Assert.Single(
        _recorded,
        static measurement =>
          measurement.Instrument == "gridflex.control.decisions");

    Assert.Equal(1.0, counted.Value);
    Assert.Equal("decided", counted.Tags["outcome"]);
    Assert.Equal("ChargeBattery", counted.Tags["action"]);

    var timed =
      Assert.Single(
        _recorded,
        static measurement =>
          measurement.Instrument ==
            "gridflex.control.decision.duration");

    Assert.True(timed.Value >= 0.0);
    Assert.Equal("decided", timed.Tags["outcome"]);

    var snapshot =
      _statistics.GetSnapshot();

    Assert.Equal(1, snapshot.Decided);
    Assert.Equal(1, snapshot.DecidedByAction[ControlAction.ChargeBattery]);
    Assert.NotNull(snapshot.LastDecisionAt);
  }

  [Fact]
  public void RejectedMeasurementIsCountedAndRethrown()
  {
    var gateway =
      CreateGateway(
        _ => throw new MeasurementRejectedException(
          "Measurement interval must be greater than zero.",
          "measurement"));

    Assert.Throws<MeasurementRejectedException>(
      () => gateway.Decide(CreateMeasurement()));

    var counted =
      Assert.Single(
        _recorded,
        static measurement =>
          measurement.Instrument == "gridflex.control.decisions");

    Assert.Equal("rejected", counted.Tags["outcome"]);
    Assert.False(counted.Tags.ContainsKey("action"));

    var snapshot =
      _statistics.GetSnapshot();

    Assert.Equal(0, snapshot.Decided);
    Assert.Equal(1, snapshot.Rejected);
    Assert.Null(snapshot.LastDecisionAt);
  }

  [Fact]
  public void ControllerFailureIsCountedAndRethrown()
  {
    var gateway =
      CreateGateway(
        _ => throw new InvalidOperationException(
          "Native controller decision failed."));

    Assert.Throws<InvalidOperationException>(
      () => gateway.Decide(CreateMeasurement()));

    var counted =
      Assert.Single(
        _recorded,
        static measurement =>
          measurement.Instrument == "gridflex.control.decisions");

    Assert.Equal("failed", counted.Tags["outcome"]);
    Assert.Equal(1, _statistics.GetSnapshot().Failed);
  }

  private InstrumentedControllerGateway CreateGateway(
    Func<EnergyMeasurementInput, ControlDecision> decide)
  {
    return new InstrumentedControllerGateway(
      new DelegatingControllerGateway(decide),
      _statistics,
      _services.GetRequiredService<IMeterFactory>(),
      TimeProvider.System,
      NullLogger<InstrumentedControllerGateway>.Instance);
  }

  private void Record(
    Instrument instrument,
    double value,
    ReadOnlySpan<KeyValuePair<string, object?>> tags)
  {
    var tagValues =
      new Dictionary<string, string?>();

    foreach (var tag in tags)
    {
      tagValues[tag.Key] = tag.Value?.ToString();
    }

    lock (_recorded)
    {
      _recorded.Add(
        new RecordedMeasurement(
          instrument.Name,
          value,
          tagValues));
    }
  }

  private static EnergyMeasurementInput CreateMeasurement()
  {
    return new EnergyMeasurementInput(
      StepNumber: 7,
      ElapsedTimeHours: 1.0,
      IntervalHours: 1.0,
      GeneratedEnergyKwh: 6.0,
      ConsumedEnergyKwh: 2.0,
      NetEnergyKwh: 4.0,
      BatteryStateOfChargeKwh: 10.0,
      GridImportEnergyKwh: 0.0,
      GridExportEnergyKwh: 0.0,
      UnresolvedEnergyKwh: 0.0);
  }

  private sealed record RecordedMeasurement(
    string Instrument,
    double Value,
    IReadOnlyDictionary<string, string?> Tags);

  private sealed class DelegatingControllerGateway(
    Func<EnergyMeasurementInput, ControlDecision> decide)
    : IControllerGateway
  {
    public ControlDecision Decide(
      EnergyMeasurementInput measurement)
    {
      return decide(measurement);
    }
  }
}
