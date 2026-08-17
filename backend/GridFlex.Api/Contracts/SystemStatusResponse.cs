namespace GridFlex.Api.Contracts;

public sealed record SystemStatusResponse(
  string Service,
  string Status,
  string Environment);
