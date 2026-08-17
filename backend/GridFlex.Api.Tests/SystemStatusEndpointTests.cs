using System.Net;
using System.Net.Http.Json;
using GridFlex.Api.Contracts;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;

namespace GridFlex.Api.Tests;

public sealed class SystemStatusEndpointTests
{
  [Fact]
  public async Task GetSystemStatusReturnsHealthyApiStatus()
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
      await client.GetAsync("/api/system/status");

    Assert.Equal(HttpStatusCode.OK, response.StatusCode);

    var status =
      await response.Content
        .ReadFromJsonAsync<SystemStatusResponse>();

    Assert.NotNull(status);
    Assert.Equal("GridFlex.Api", status.Service);
    Assert.Equal("healthy", status.Status);
    Assert.Equal("Testing", status.Environment);
  }
}
