using System.Net;
using System.Net.Http.Json;
using GridFlex.Api.Application.Control;
using GridFlex.Api.Contracts;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;

namespace GridFlex.Api.Tests;

public sealed class SystemStatusEndpointTests
{
  [Fact]
  public async Task GetSystemStatusReturnsHealthyApiStatus()
  {
    using var factory = CreateFactory();
    using var client = CreateClient(factory);

    var status =
      await GetStatusAsync(client);

    Assert.Equal("GridFlex.Api", status.Service);
    Assert.Equal("healthy", status.Status);
    Assert.Equal("Testing", status.Environment);
    Assert.False(string.IsNullOrWhiteSpace(status.Version));
    Assert.True(status.UptimeSeconds >= 0);
  }

  [Fact]
  public async Task GetSystemStatusDescribesTheLoadedNativeController()
  {
    using var factory = CreateFactory();
    using var client = CreateClient(factory);

    var controller =
      (await GetStatusAsync(client)).NativeController;

    Assert.True(controller.Ready);
    Assert.Equal(2u, controller.AbiVersion);

    // From appsettings.json.
    Assert.Equal(
      new ControllerLimitsResponse(
        MaxChargePowerKw: 10.0,
        MaxDischargePowerKw: 8.0,
        MinimumBatterySocKwh: 2.0,
        MaximumBatterySocKwh: 20.0),
      controller.Limits);
  }

  [Fact]
  public async Task GetSystemStatusCountsDecisionsByOutcomeAndAction()
  {
    using var factory = CreateFactory();
    using var client = CreateClient(factory);

    var before =
      (await GetStatusAsync(client)).Decisions;

    Assert.Equal(0, before.Decided);
    Assert.Null(before.LastDecisionAt);

    using var charged =
      await client.PostAsJsonAsync(
        "/api/control/decision",
        CreateRequest(netEnergyKwh: 3.0, stepNumber: 1));

    using var rejected =
      await client.PostAsJsonAsync(
        "/api/control/decision",
        CreateRequest(netEnergyKwh: 3.0, stepNumber: 0));

    Assert.Equal(HttpStatusCode.OK, charged.StatusCode);
    Assert.Equal(HttpStatusCode.BadRequest, rejected.StatusCode);

    var after =
      (await GetStatusAsync(client)).Decisions;

    Assert.Equal(1, after.Decided);
    Assert.Equal(1, after.DecidedByAction["ChargeBattery"]);
    Assert.Equal(0, after.DecidedByAction["DischargeBattery"]);
    Assert.Equal(1, after.Rejected);
    Assert.Equal(0, after.Failed);
    Assert.NotNull(after.LastDecisionAt);
  }

  [Fact]
  public async Task GetSystemStatusReportsDegradedWhenTheNativeControllerIsUnavailable()
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

    var status =
      await GetStatusAsync(client);

    // Before, this endpoint reported "healthy" while /health/ready
    // answered 503.
    Assert.Equal("degraded", status.Status);
    Assert.False(status.NativeController.Ready);
    Assert.Null(status.NativeController.AbiVersion);
  }

  private static async Task<SystemStatusResponse> GetStatusAsync(
    HttpClient client)
  {
    using var response =
      await client.GetAsync("/api/system/status");

    Assert.Equal(HttpStatusCode.OK, response.StatusCode);

    var status =
      await response.Content
        .ReadFromJsonAsync<SystemStatusResponse>();

    Assert.NotNull(status);

    return status;
  }

  private static ControlDecisionRequest CreateRequest(
    double netEnergyKwh,
    ulong stepNumber)
  {
    return new ControlDecisionRequest(
      StepNumber: stepNumber,
      ElapsedTimeHours: 1.0,
      IntervalHours: 1.0,
      GeneratedEnergyKwh: 2.0 + Math.Max(netEnergyKwh, 0.0),
      ConsumedEnergyKwh: 2.0 + Math.Max(-netEnergyKwh, 0.0),
      NetEnergyKwh: netEnergyKwh,
      BatteryStateOfChargeKwh: 10.0,
      GridImportEnergyKwh: 0.0,
      GridExportEnergyKwh: 0.0,
      UnresolvedEnergyKwh: 0.0);
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
            builder.ConfigureTestServices(configureServices);
          }
        });
  }

  private static HttpClient CreateClient(
    WebApplicationFactory<global::Program> factory)
  {
    return factory.CreateClient(
      new WebApplicationFactoryClientOptions
      {
        BaseAddress = new Uri("https://localhost")
      });
  }
}
