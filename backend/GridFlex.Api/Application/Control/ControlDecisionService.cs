namespace GridFlex.Api.Application.Control;

public sealed class ControlDecisionService
  : IControlDecisionService
{
  private readonly IControllerGateway _controllerGateway;

  public ControlDecisionService(
    IControllerGateway controllerGateway)
  {
    ArgumentNullException.ThrowIfNull(controllerGateway);

    _controllerGateway = controllerGateway;
  }

  public ControlDecision Decide(
    EnergyMeasurementInput measurement)
  {
    ArgumentNullException.ThrowIfNull(measurement);

    var decision =
      _controllerGateway.Decide(measurement);

    if (decision is null)
    {
      throw new InvalidOperationException(
        "Controller gateway returned no decision.");
    }

    if (decision.SourceStepNumber != measurement.StepNumber)
    {
      throw new InvalidOperationException(
        "Controller decision source step does not match the measurement step.");
    }

    return decision;
  }
}
