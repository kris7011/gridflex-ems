using GridFlex.Api.Application.Control;
using GridFlex.Api.Endpoints;
using GridFlex.Api.Infrastructure.Http;
using GridFlex.Api.Infrastructure.Native.Control;
using GridFlex.Api.Services;
using Microsoft.AspNetCore.Routing;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddOpenApi();
builder.Services.AddHealthChecks();

// Every error response, including 500s and failed body binding, is an
// RFC 9457 problem document with a trace identifier.
builder.Services.AddProblemDetails();
builder.Services.AddExceptionHandler<RequestBodyExceptionHandler>();

// Surface body-binding failures as exceptions in every environment, so
// RequestBodyExceptionHandler can explain them instead of the default
// empty 400 response.
builder.Services.Configure<RouteHandlerOptions>(
  static options => options.ThrowOnBadRequest = true);

// Constructor parameters of request records are required properties: a
// missing value is an error, not 0.
builder.Services.ConfigureHttpJsonOptions(
  static options =>
    options.SerializerOptions.RespectRequiredConstructorParameters = true);

builder.Services.AddSingleton<
  ISystemStatusService,
  SystemStatusService>();

builder.Services.AddSingleton<
  IControlDecisionService,
  ControlDecisionService>();

builder.Services.AddNativeController();

var app = builder.Build();

app.UseExceptionHandler();
app.UseStatusCodePages();

if (app.Environment.IsDevelopment())
{
  app.MapOpenApi();
}

app.UseHttpsRedirection();

app.MapHealthEndpoints();
app.MapSystemStatusEndpoints();
app.MapControlDecisionEndpoints();

app.Run();

public partial class Program
{
}
