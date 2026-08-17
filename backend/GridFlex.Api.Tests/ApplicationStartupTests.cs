using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

namespace GridFlex.Api.Tests;

public sealed class ApplicationStartupTests
{
  [Fact]
  public void ApplicationStartsWithExpectedEnvironment()
  {
    using var factory =
      new WebApplicationFactory<global::Program>()
        .WithWebHostBuilder(builder =>
          builder.UseEnvironment("Testing"));

    var environment =
      factory.Services.GetRequiredService<IHostEnvironment>();

    Assert.Equal("Testing", environment.EnvironmentName);
    Assert.Equal("GridFlex.Api", environment.ApplicationName);
  }
}
