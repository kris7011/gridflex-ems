using System.Net;
using System.Net.Http.Json;
using GridFlex.Api.Contracts;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Testing;

namespace GridFlex.Api.Tests;

public sealed class ControlDecisionEndpointTests
{
  [Fact]
  public async Task PostDecisionReturnsNativeControllerDecision()
  {
    using var factory = CreateFactory();
    using var client = CreateClient(factory);

    var request =
      CreateValidRequest();

    using var response =
      await client.PostAsJsonAsync(
        "/api/control/decision",
        request);

    Assert.Equal(
      HttpStatusCode.OK,
      response.StatusCode);

    var decision =
      await response.Content
        .ReadFromJsonAsync<ControlDecisionResponse>();

    Assert.NotNull(decision);

    Assert.Equal(
      42UL,
      decision.SourceStepNumber);

    Assert.Equal(
      "ChargeBattery",
      decision.Action);

    Assert.Equal(
      10.0,
      decision.RequestedPowerKw,
      precision: 10);
  }

  [Fact]
  public async Task PostDecisionReturnsBadRequestForInvalidMeasurement()
  {
    using var factory = CreateFactory();
    using var client = CreateClient(factory);

    var request =
      CreateValidRequest() with
      {
        StepNumber = 0
      };

    using var response =
      await client.PostAsJsonAsync(
        "/api/control/decision",
        request);

    Assert.Equal(
      HttpStatusCode.BadRequest,
      response.StatusCode);

    var problem =
      await response.Content
        .ReadFromJsonAsync<ProblemDetails>();

    Assert.NotNull(problem);

    Assert.Equal(
      400,
      problem.Status);

    Assert.Equal(
      "Invalid energy measurement.",
      problem.Title);
  }

  private static ControlDecisionRequest
    CreateValidRequest()
  {
    return new ControlDecisionRequest(
      StepNumber: 42,
      ElapsedTimeHours: 1.0,
      IntervalHours: 0.25,
      GeneratedEnergyKwh: 5.0,
      ConsumedEnergyKwh: 2.0,
      NetEnergyKwh: 3.0,
      BatteryStateOfChargeKwh: 10.0,
      GridImportEnergyKwh: 0.0,
      GridExportEnergyKwh: 0.0,
      UnresolvedEnergyKwh: 0.0);
  }

  private static WebApplicationFactory<global::Program>
    CreateFactory()
  {
    return new WebApplicationFactory<global::Program>()
      .WithWebHostBuilder(
        builder =>
          builder.UseEnvironment("Testing"));
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
