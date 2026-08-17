namespace GridFlex.Api.Application.Control;

public interface IControlDecisionService
{
  ControlDecision Decide(
    EnergyMeasurementInput measurement);
}
