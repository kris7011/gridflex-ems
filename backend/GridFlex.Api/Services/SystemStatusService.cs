using GridFlex.Api.Contracts;
using Microsoft.Extensions.Hosting;

namespace GridFlex.Api.Services;

public sealed class SystemStatusService : ISystemStatusService
{
  private const string ServiceName = "GridFlex.Api";
  private const string HealthyStatus = "healthy";

  private readonly IHostEnvironment _environment;

  public SystemStatusService(IHostEnvironment environment)
  {
    ArgumentNullException.ThrowIfNull(environment);

    _environment = environment;
  }

  public SystemStatusResponse GetStatus()
  {
    return new SystemStatusResponse(
      ServiceName,
      HealthyStatus,
      _environment.EnvironmentName);
  }
}
