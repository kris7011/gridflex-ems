using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Diagnostics.HealthChecks;
using Microsoft.AspNetCore.Routing;

namespace GridFlex.Api.Endpoints;

public static class HealthEndpoints
{
  public static IEndpointConventionBuilder MapHealthEndpoints(
    this IEndpointRouteBuilder endpoints)
  {
    endpoints.MapHealthChecks(
      "/health/ready",
      new HealthCheckOptions
      {
        Predicate =
          healthCheck =>
            healthCheck.Tags.Contains("ready")
      });

    return endpoints.MapHealthChecks(
      "/health/live",
      new HealthCheckOptions
      {
        Predicate = _ => false
      });
  }
}
