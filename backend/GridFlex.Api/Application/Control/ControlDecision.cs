namespace GridFlex.Api.Application.Control;

public sealed record ControlDecision(
  ulong SourceStepNumber,
  ControlAction Action,
  double RequestedPowerKw);
