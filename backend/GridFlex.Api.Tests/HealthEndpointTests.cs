using System.Net;
using GridFlex.Api.Application.Control;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;

namespace GridFlex.Api.Tests;

public sealed class HealthEndpointTests
{
  [Fact]
  public async Task LivenessEndpointReturnsHealthy()
  {
    using var factory = CreateFactory();
    using var client = CreateClient(factory);

    using var response =
      await client.GetAsync("/health/live");

    Assert.Equal(
      HttpStatusCode.OK,
      response.StatusCode);

    var content =
      await response.Content.ReadAsStringAsync();

    Assert.Equal(
      "Healthy",
      content);
  }

  [Fact]
  public async Task ReadinessEndpointReturnsHealthy()
  {
    using var factory = CreateFactory();
    using var client = CreateClient(factory);

    using var response =
      await client.GetAsync("/health/ready");

    Assert.Equal(
      HttpStatusCode.OK,
      response.StatusCode);

    var content =
      await response.Content.ReadAsStringAsync();

    Assert.Equal(
      "Healthy",
      content);
  }

  [Fact]
  public async Task NativeControllerFailureAffectsReadinessButNotLiveness()
  {
    using var factory =
      CreateFactory(
        services =>
        {
          services.RemoveAll<IControllerGateway>();

          services.AddSingleton<IControllerGateway>(
            static _ =>
              throw new InvalidOperationException(
                "Native controller is unavailable."));
        });

    using var client = CreateClient(factory);

    using var readinessResponse =
      await client.GetAsync("/health/ready");

    Assert.Equal(
      HttpStatusCode.ServiceUnavailable,
      readinessResponse.StatusCode);

    var readinessContent =
      await readinessResponse.Content
        .ReadAsStringAsync();

    Assert.Equal(
      "Unhealthy",
      readinessContent);

    using var livenessResponse =
      await client.GetAsync("/health/live");

    Assert.Equal(
      HttpStatusCode.OK,
      livenessResponse.StatusCode);

    var livenessContent =
      await livenessResponse.Content
        .ReadAsStringAsync();

    Assert.Equal(
      "Healthy",
      livenessContent);
  }

  private static WebApplicationFactory<global::Program>
    CreateFactory(
      Action<IServiceCollection>? configureServices = null)
  {
    return new WebApplicationFactory<global::Program>()
      .WithWebHostBuilder(
        builder =>
        {
          builder.UseEnvironment("Testing");

          if (configureServices is not null)
          {
            builder.ConfigureServices(
              configureServices);
          }
        });
  }

  private static HttpClient CreateClient(
    WebApplicationFactory<global::Program> factory)
  {
    return factory.CreateClient(
      new WebApplicationFactoryClientOptions
      {
        BaseAddress =
          new Uri("https://localhost")
      });
  }
}
