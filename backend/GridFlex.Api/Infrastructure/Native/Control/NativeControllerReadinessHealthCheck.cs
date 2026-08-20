using GridFlex.Api.Application.Control;
using Microsoft.Extensions.Diagnostics.HealthChecks;

namespace GridFlex.Api.Infrastructure.Native.Control;

internal sealed class NativeControllerReadinessHealthCheck
  : IHealthCheck
{
  private readonly IServiceProvider _serviceProvider;

  public NativeControllerReadinessHealthCheck(
    IServiceProvider serviceProvider)
  {
    _serviceProvider =
      serviceProvider ??
      throw new ArgumentNullException(
        nameof(serviceProvider));
  }

  public Task<HealthCheckResult> CheckHealthAsync(
    HealthCheckContext context,
    CancellationToken cancellationToken = default)
  {
    cancellationToken.ThrowIfCancellationRequested();

    _ =
      _serviceProvider
        .GetRequiredService<IControllerGateway>();

    return Task.FromResult(
      HealthCheckResult.Healthy(
        "Native controller is ready."));
  }
}
