using GridFlex.Api.Application.Control;
using GridFlex.Api.Contracts;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.AspNetCore.Routing;

namespace GridFlex.Api.Endpoints;

public static class ControlDecisionEndpoints
{
  public static RouteGroupBuilder MapControlDecisionEndpoints(
    this IEndpointRouteBuilder endpoints)
  {
    var group =
      endpoints
        .MapGroup("/api/control")
        .WithTags("Control");

    group
      .MapPost(
        "/decision",
        Decide)
      .WithName("CreateControlDecision");

    return group;
  }

  private static Results<
    Ok<ControlDecisionResponse>,
    ProblemHttpResult> Decide(
    ControlDecisionRequest request,
    IControlDecisionService decisionService)
  {
    try
    {
      var measurement =
        new EnergyMeasurementInput(
          StepNumber: request.StepNumber,
          ElapsedTimeHours: request.ElapsedTimeHours,
          IntervalHours: request.IntervalHours,
          GeneratedEnergyKwh:
            request.GeneratedEnergyKwh,
          ConsumedEnergyKwh:
            request.ConsumedEnergyKwh,
          NetEnergyKwh:
            request.NetEnergyKwh,
          BatteryStateOfChargeKwh:
            request.BatteryStateOfChargeKwh,
          GridImportEnergyKwh:
            request.GridImportEnergyKwh,
          GridExportEnergyKwh:
            request.GridExportEnergyKwh,
          UnresolvedEnergyKwh:
            request.UnresolvedEnergyKwh);

      var decision =
        decisionService.Decide(measurement);

      var response =
        new ControlDecisionResponse(
          SourceStepNumber:
            decision.SourceStepNumber,
          Action:
            MapAction(decision.Action),
          RequestedPowerKw:
            decision.RequestedPowerKw);

      return TypedResults.Ok(response);
    }
    catch (ArgumentException exception)
    {
      // Written through the problem details service, like every other
      // error response, so it carries the trace identifier.
      return TypedResults.Problem(
        statusCode:
          StatusCodes.Status400BadRequest,
        title:
          "Invalid energy measurement.",
        detail:
          exception.Message);
    }
  }

  private static string MapAction(
    ControlAction action)
  {
    return action switch
    {
      ControlAction.Idle =>
        "Idle",

      ControlAction.ChargeBattery =>
        "ChargeBattery",

      ControlAction.DischargeBattery =>
        "DischargeBattery",

      ControlAction.ImportFromGrid =>
        "ImportFromGrid",

      ControlAction.ExportToGrid =>
        "ExportToGrid",

      _ => throw new InvalidOperationException(
        $"Unsupported control action '{(int)action}'.")
    };
  }
}
