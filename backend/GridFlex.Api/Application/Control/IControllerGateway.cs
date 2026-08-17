namespace GridFlex.Api.Application.Control;

public interface IControllerGateway
{
  ControlDecision Decide(
    EnergyMeasurementInput measurement);
}
