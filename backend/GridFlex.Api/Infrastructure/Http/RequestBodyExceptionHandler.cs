using System.Text.Json;
using Microsoft.AspNetCore.Diagnostics;
using Microsoft.AspNetCore.Mvc;

namespace GridFlex.Api.Infrastructure.Http;

/// <summary>
/// Turns request bodies that cannot be bound (malformed JSON, missing or
/// unknown properties) into a 400 problem response that names the cause.
/// </summary>
/// <remarks>
/// Without this handler, minimal APIs answer such requests with an empty
/// 400 response outside Development, so a client cannot tell which field
/// was wrong. Every other exception is left to the default handler, which
/// logs it and writes a generic 500 problem response.
/// </remarks>
internal sealed partial class RequestBodyExceptionHandler
  : IExceptionHandler
{
  private readonly IProblemDetailsService _problemDetailsService;
  private readonly ILogger<RequestBodyExceptionHandler> _logger;

  public RequestBodyExceptionHandler(
    IProblemDetailsService problemDetailsService,
    ILogger<RequestBodyExceptionHandler> logger)
  {
    _problemDetailsService = problemDetailsService;
    _logger = logger;
  }

  public async ValueTask<bool> TryHandleAsync(
    HttpContext httpContext,
    Exception exception,
    CancellationToken cancellationToken)
  {
    if (exception is not BadHttpRequestException badRequest)
    {
      return false;
    }

    // The JSON message names the offending property and position, for
    // example "missing required properties including:
    // 'batteryStateOfChargeKwh'". It contains no request values.
    var detail =
      badRequest.InnerException is JsonException jsonException
        ? jsonException.Message
        : badRequest.Message;

    LogRejectedRequestBody(
      _logger,
      httpContext.Request.Path,
      detail);

    httpContext.Response.StatusCode =
      StatusCodes.Status400BadRequest;

    return await _problemDetailsService.TryWriteAsync(
      new ProblemDetailsContext
      {
        HttpContext = httpContext,
        Exception = exception,
        ProblemDetails =
          new ProblemDetails
          {
            Status =
              StatusCodes.Status400BadRequest,
            Title =
              "Invalid request body.",
            Detail =
              detail
          }
      });
  }

  [LoggerMessage(
    Level = LogLevel.Warning,
    Message = "Rejected request body for {Path}: {Detail}")]
  private static partial void LogRejectedRequestBody(
    ILogger logger,
    PathString path,
    string detail);
}
