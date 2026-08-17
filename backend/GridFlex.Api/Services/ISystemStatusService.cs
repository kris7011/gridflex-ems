using GridFlex.Api.Contracts;

namespace GridFlex.Api.Services;

public interface ISystemStatusService
{
  SystemStatusResponse GetStatus();
}
