using GridFlex.Api.Services;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;

namespace GridFlex.Api.Endpoints;

public static class SystemStatusEndpoints
{
  public static RouteGroupBuilder MapSystemStatusEndpoints(
    this IEndpointRouteBuilder endpoints)
  {
    var group = endpoints
      .MapGroup("/api/system")
      .WithTags("System");

    group
      .MapGet(
        "/status",
        (ISystemStatusService statusService) =>
          TypedResults.Ok(statusService.GetStatus()))
      .WithName("GetSystemStatus");

    return group;
  }
}
