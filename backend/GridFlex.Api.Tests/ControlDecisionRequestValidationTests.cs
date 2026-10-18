using System.Net;
using System.Net.Http.Json;
using System.Text;
using GridFlex.Api.Application.Control;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;

namespace GridFlex.Api.Tests;

/// <summary>
/// The HTTP boundary must reject request bodies that do not describe a
/// complete measurement, instead of deciding on default values.
/// </summary>
public sealed class ControlDecisionRequestValidationTests
{
  private const string ValidBody =
    """
    {
      "stepNumber": 1,
      "elapsedTimeHours": 1.0,
      "intervalHours": 1.0,
      "generatedEnergyKwh": 2.0,
      "consumedEnergyKwh": 6.0,
      "netEnergyKwh": -4.0,
      "batteryStateOfChargeKwh": 15.0,
      "gridImportEnergyKwh": 0.0,
      "gridExportEnergyKwh": 0.0,
      "unresolvedEnergyKwh": 0.0
    }
    """;

  [Fact]
  public async Task ValidBodyIsDecided()
  {
    using var factory = CreateFactory();
    using var client = CreateClient(factory);

    using var response =
      await PostAsync(client, ValidBody);

    Assert.Equal(
      HttpStatusCode.OK,
      response.StatusCode);
  }

  [Fact]
  public async Task MissingPropertyIsRejectedInsteadOfDefaultingToZero()
  {
    using var factory = CreateFactory();
    using var client = CreateClient(factory);

    var body =
      ValidBody.Replace(
        "\"batteryStateOfChargeKwh\": 15.0,",
        string.Empty,
        StringComparison.Ordinal);

    var problem =
      await AssertBadRequestAsync(client, body);

    Assert.Contains(
      "batteryStateOfChargeKwh",
      problem.Detail,
      StringComparison.Ordinal);
  }

  [Fact]
  public async Task MisspelledPropertyIsRejected()
  {
    using var factory = CreateFactory();
    using var client = CreateClient(factory);

    // Before strict binding, this request was answered with 200 and an
    // Idle decision, because the state of charge was bound as 0 kWh.
    var body =
      ValidBody.Replace(
        "\"batteryStateOfChargeKwh\"",
        "\"batterySoc\"",
        StringComparison.Ordinal);

    var problem =
      await AssertBadRequestAsync(client, body);

    Assert.Contains(
      "batterySoc",
      problem.Detail,
      StringComparison.Ordinal);
  }

  [Theory]
  [InlineData("{\"stepNumber\":")]
  [InlineData("not json")]
  [InlineData("{\"stepNumber\": -1}")]
  public async Task MalformedBodyIsRejectedWithProblemDetails(
    string body)
  {
    using var factory = CreateFactory();
    using var client = CreateClient(factory);

    var problem =
      await AssertBadRequestAsync(client, body);

    Assert.False(
      string.IsNullOrWhiteSpace(problem.Detail));
  }

  [Fact]
  public async Task ControllerFailureIsReportedAsProblemDetailsWithoutInternals()
  {
    using var factory =
      CreateFactory(
        services =>
        {
          services.RemoveAll<IControllerGateway>();
          services.AddSingleton<IControllerGateway>(
            new FailingControllerGateway());
        });

    using var client = CreateClient(factory);

    using var response =
      await PostAsync(client, ValidBody);

    Assert.Equal(
      HttpStatusCode.InternalServerError,
      response.StatusCode);

    Assert.Equal(
      "application/problem+json",
      response.Content.Headers.ContentType?.MediaType);

    var content =
      await response.Content.ReadAsStringAsync();

    Assert.DoesNotContain(
      FailingControllerGateway.Message,
      content,
      StringComparison.Ordinal);

    Assert.Contains(
      "traceId",
      content,
      StringComparison.Ordinal);
  }

  private static async Task<ProblemDetails> AssertBadRequestAsync(
    HttpClient client,
    string body)
  {
    using var response =
      await PostAsync(client, body);

    Assert.Equal(
      HttpStatusCode.BadRequest,
      response.StatusCode);

    Assert.Equal(
      "application/problem+json",
      response.Content.Headers.ContentType?.MediaType);

    var problem =
      await response.Content
        .ReadFromJsonAsync<ProblemDetails>();

    Assert.NotNull(problem);
    Assert.Equal(400, problem.Status);
    Assert.Equal("Invalid request body.", problem.Title);

    return problem;
  }

  private static Task<HttpResponseMessage> PostAsync(
    HttpClient client,
    string body)
  {
    return client.PostAsync(
      "/api/control/decision",
      new StringContent(
        body,
        Encoding.UTF8,
        "application/json"));
  }

  private static WebApplicationFactory<global::Program>
    CreateFactory(
      Action<IServiceCollection>? configureServices = null)
  {
    return new WebApplicationFactory<global::Program>()
      .WithWebHostBuilder(
        builder =>
        {
          // Production behaviour: no developer exception page.
          builder.UseEnvironment("Production");

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
        BaseAddress =
          new Uri("https://localhost")
      });
  }

  private sealed class FailingControllerGateway
    : IControllerGateway
  {
    internal const string Message =
      "Native controller decision failed with status 'InternalError'.";

    public ControlDecision Decide(
      EnergyMeasurementInput measurement)
    {
      throw new InvalidOperationException(Message);
    }
  }
}
