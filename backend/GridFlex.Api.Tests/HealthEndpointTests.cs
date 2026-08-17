using System.Net;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;

namespace GridFlex.Api.Tests;

public sealed class HealthEndpointTests
{
  [Fact]
  public async Task LivenessEndpointReturnsHealthy()
  {
    using var factory =
      new WebApplicationFactory<global::Program>()
        .WithWebHostBuilder(builder =>
          builder.UseEnvironment("Testing"));

    using var client =
      factory.CreateClient(
        new WebApplicationFactoryClientOptions
        {
          BaseAddress = new Uri("https://localhost")
        });

    using var response =
      await client.GetAsync("/health/live");

    Assert.Equal(HttpStatusCode.OK, response.StatusCode);

    var content =
      await response.Content.ReadAsStringAsync();

    Assert.Equal("Healthy", content);
  }
}
