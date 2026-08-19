using GridFlex.Api.Application.Control;
using GridFlex.Api.Endpoints;
using GridFlex.Api.Infrastructure.Native.Control;
using GridFlex.Api.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddOpenApi();
builder.Services.AddHealthChecks();

builder.Services.AddSingleton<
  ISystemStatusService,
  SystemStatusService>();

builder.Services.AddSingleton<
  IControlDecisionService,
  ControlDecisionService>();

builder.Services.AddNativeController();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
  app.MapOpenApi();
}

app.UseHttpsRedirection();

app.MapHealthEndpoints();
app.MapSystemStatusEndpoints();

app.Run();

public partial class Program
{
}
