using System.Diagnostics;
using System.Diagnostics.Metrics;

namespace GridFlex.Api.Application.Control;

/// <summary>
/// Decorates a controller gateway with metrics, statistics and
/// structured logs for every decision, without the gateway or the
/// application service knowing about observability.
/// </summary>
/// <remarks>
/// Instruments of the <c>GridFlex.Api.Control</c> meter:
/// <list type="bullet">
/// <item><c>gridflex.control.decisions</c>: counter, tagged with
/// <c>outcome</c> (decided, rejected, failed) and, for decided requests,
/// <c>action</c>.</item>
/// <item><c>gridflex.control.decision.duration</c>: histogram in
/// milliseconds of the call into the controller, tagged with
/// <c>outcome</c>.</item>
/// </list>
/// </remarks>
public sealed partial class InstrumentedControllerGateway
  : IControllerGateway
{
  public const string MeterName = "GridFlex.Api.Control";

  private readonly IControllerGateway _inner;
  private readonly ControlDecisionStatistics _statistics;
  private readonly TimeProvider _timeProvider;
  private readonly ILogger<InstrumentedControllerGateway> _logger;
  private readonly Counter<long> _decisions;
  private readonly Histogram<double> _duration;

  public InstrumentedControllerGateway(
    IControllerGateway inner,
    ControlDecisionStatistics statistics,
    IMeterFactory meterFactory,
    TimeProvider timeProvider,
    ILogger<InstrumentedControllerGateway> logger)
  {
    ArgumentNullException.ThrowIfNull(inner);
    ArgumentNullException.ThrowIfNull(statistics);
    ArgumentNullException.ThrowIfNull(meterFactory);
    ArgumentNullException.ThrowIfNull(timeProvider);
    ArgumentNullException.ThrowIfNull(logger);

    _inner = inner;
    _statistics = statistics;
    _timeProvider = timeProvider;
    _logger = logger;

    var meter =
      meterFactory.Create(MeterName);

    _decisions =
      meter.CreateCounter<long>(
        "gridflex.control.decisions",
        unit: "{decision}",
        description:
          "Control decision requests handled by the controller.");

    _duration =
      meter.CreateHistogram<double>(
        "gridflex.control.decision.duration",
        unit: "ms",
        description:
          "Duration of the call into the controller.");
  }

  public ControlDecision Decide(
    EnergyMeasurementInput measurement)
  {
    ArgumentNullException.ThrowIfNull(measurement);

    var startedAt =
      _timeProvider.GetTimestamp();

    try
    {
      var decision =
        _inner.Decide(measurement);

      var elapsed =
        _timeProvider.GetElapsedTime(startedAt);

      Record(
        "decided",
        elapsed,
        new KeyValuePair<string, object?>(
          "action",
          decision.Action.ToString()));

      _statistics.RecordDecided(
        decision.Action,
        _timeProvider.GetUtcNow());

      LogDecided(
        _logger,
        measurement.StepNumber,
        decision.Action,
        decision.RequestedPowerKw,
        elapsed.TotalMilliseconds);

      return decision;
    }
    catch (ArgumentException exception)
    {
      // The endpoint answers these with 400.
      Record(
        "rejected",
        _timeProvider.GetElapsedTime(startedAt));

      _statistics.RecordRejected();

      LogRejected(
        _logger,
        measurement.StepNumber,
        exception is MeasurementRejectedException rejection
          ? rejection.Reason
          : exception.Message);

      throw;
    }
    catch (Exception exception)
    {
      Record(
        "failed",
        _timeProvider.GetElapsedTime(startedAt));

      _statistics.RecordFailed();

      LogFailed(
        _logger,
        exception,
        measurement.StepNumber);

      throw;
    }
  }

  private void Record(
    string outcome,
    TimeSpan elapsed,
    params ReadOnlySpan<KeyValuePair<string, object?>> extraTags)
  {
    var tags =
      new TagList
      {
        { "outcome", outcome }
      };

    foreach (var tag in extraTags)
    {
      tags.Add(tag);
    }

    _decisions.Add(1, tags);

    _duration.Record(
      elapsed.TotalMilliseconds,
      new KeyValuePair<string, object?>("outcome", outcome));
  }

  [LoggerMessage(
    Level = LogLevel.Information,
    Message =
      "Decided step {StepNumber}: {Action} at {RequestedPowerKw} kW " +
      "in {DurationMs:0.000} ms")]
  private static partial void LogDecided(
    ILogger logger,
    ulong stepNumber,
    ControlAction action,
    double requestedPowerKw,
    double durationMs);

  [LoggerMessage(
    Level = LogLevel.Warning,
    Message = "Rejected measurement for step {StepNumber}: {Reason}")]
  private static partial void LogRejected(
    ILogger logger,
    ulong stepNumber,
    string reason);

  [LoggerMessage(
    Level = LogLevel.Error,
    Message = "Controller failed for step {StepNumber}")]
  private static partial void LogFailed(
    ILogger logger,
    Exception exception,
    ulong stepNumber);
}
