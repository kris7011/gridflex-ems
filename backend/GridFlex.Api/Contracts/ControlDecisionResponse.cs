namespace GridFlex.Api.Contracts;

public sealed record ControlDecisionResponse(
  ulong SourceStepNumber,
  string Action,
  double RequestedPowerKw);
