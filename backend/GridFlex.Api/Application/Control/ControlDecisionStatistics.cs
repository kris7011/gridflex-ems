namespace GridFlex.Api.Application.Control;

/// <summary>
/// Thread-safe counters of the decisions made since the process started,
/// exposed through the system status endpoint.
/// </summary>
public sealed class ControlDecisionStatistics
{
  private readonly long[] _decidedByAction =
    new long[Enum.GetValues<ControlAction>().Length];

  private long _rejected;
  private long _failed;
  private long _lastDecisionAtUtcTicks;

  internal void RecordDecided(
    ControlAction action,
    DateTimeOffset at)
  {
    Interlocked.Increment(
      ref _decidedByAction[(int)action]);

    Interlocked.Exchange(
      ref _lastDecisionAtUtcTicks,
      at.UtcTicks);
  }

  internal void RecordRejected()
  {
    Interlocked.Increment(ref _rejected);
  }

  internal void RecordFailed()
  {
    Interlocked.Increment(ref _failed);
  }

  public ControlDecisionStatisticsSnapshot GetSnapshot()
  {
    var byAction =
      Enum.GetValues<ControlAction>()
        .ToDictionary(
          static action => action,
          action => Interlocked.Read(
            ref _decidedByAction[(int)action]));

    var lastTicks =
      Interlocked.Read(ref _lastDecisionAtUtcTicks);

    return new ControlDecisionStatisticsSnapshot(
      Decided: byAction.Values.Sum(),
      DecidedByAction: byAction,
      Rejected: Interlocked.Read(ref _rejected),
      Failed: Interlocked.Read(ref _failed),
      LastDecisionAt:
        lastTicks == 0
          ? null
          : new DateTimeOffset(lastTicks, TimeSpan.Zero));
  }
}

public sealed record ControlDecisionStatisticsSnapshot(
  long Decided,
  IReadOnlyDictionary<ControlAction, long> DecidedByAction,
  long Rejected,
  long Failed,
  DateTimeOffset? LastDecisionAt);
