namespace GridFlex.Api.Application.Control;

/// <summary>
/// The controller refused to decide because the measurement violates one
/// of its rules, for example a non-positive interval or a net energy that
/// contradicts generation and consumption.
/// </summary>
public sealed class MeasurementRejectedException
  : ArgumentException
{
  public MeasurementRejectedException(
    string reason,
    string? paramName)
    : base(reason, paramName)
  {
    Reason = reason;
  }

  /// <summary>
  /// The violated rule, without the parameter-name suffix that
  /// <see cref="ArgumentException.Message"/> appends. Safe to return to
  /// clients: it never contains measurement values.
  /// </summary>
  public string Reason
  {
    get;
  }
}
