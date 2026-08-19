using GridFlex.Api.Application.Control;
using GridFlex.Api.Infrastructure.Native.Control;
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
    using var factory = CreateFactory();

    var environment =
      factory.Services
        .GetRequiredService<IHostEnvironment>();

    Assert.Equal(
      "Testing",
      environment.EnvironmentName);

    Assert.Equal(
      "GridFlex.Api",
      environment.ApplicationName);
  }

  [Fact]
  public void ApplicationRegistersNativeControllerGatewayAsSingleton()
  {
    using var factory = CreateFactory();

    var firstGateway =
      factory.Services
        .GetRequiredService<IControllerGateway>();

    var secondGateway =
      factory.Services
        .GetRequiredService<IControllerGateway>();

    Assert.IsType<NativeControllerGateway>(
      firstGateway);

    Assert.Same(
      firstGateway,
      secondGateway);
  }

  [Fact]
  public void ApplicationUsesConfiguredNativeController()
  {
    using var factory = CreateFactory();

    var service =
      factory.Services
        .GetRequiredService<IControlDecisionService>();

    var measurement =
      new EnergyMeasurementInput(
        StepNumber: 50,
        ElapsedTimeHours: 1.0,
        IntervalHours: 0.25,
        GeneratedEnergyKwh: 5.0,
        ConsumedEnergyKwh: 2.0,
        NetEnergyKwh: 3.0,
        BatteryStateOfChargeKwh: 10.0,
        GridImportEnergyKwh: 0.0,
        GridExportEnergyKwh: 0.0,
        UnresolvedEnergyKwh: 0.0);

    var decision =
      service.Decide(measurement);

    Assert.Equal(
      50UL,
      decision.SourceStepNumber);

    Assert.Equal(
      ControlAction.ChargeBattery,
      decision.Action);

    Assert.Equal(
      10.0,
      decision.RequestedPowerKw,
      precision: 10);
  }

  private static WebApplicationFactory<global::Program>
    CreateFactory()
  {
    return new WebApplicationFactory<global::Program>()
      .WithWebHostBuilder(builder =>
        builder.UseEnvironment("Testing"));
  }
}
