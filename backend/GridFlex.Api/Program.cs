using GridFlex.Api.Endpoints;
using GridFlex.Api.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddOpenApi();

builder.Services.AddSingleton<
  ISystemStatusService,
  SystemStatusService>();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
  app.MapOpenApi();
}

app.UseHttpsRedirection();

app.MapSystemStatusEndpoints();

app.Run();

public partial class Program
{
}
