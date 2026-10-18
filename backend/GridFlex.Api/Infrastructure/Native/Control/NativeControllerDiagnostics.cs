using GridFlex.Api.Application.Control;
using Microsoft.Extensions.Options;

namespace GridFlex.Api.Infrastructure.Native.Control;

internal sealed class NativeControllerDiagnostics
  : IControllerDiagnostics
{
  private readonly IServiceProvider _serviceProvider;
  private readonly NativeControllerOptions _options;

  public NativeControllerDiagnostics(
    IServiceProvider serviceProvider,
    IOptions<NativeControllerOptions> options)
  {
    ArgumentNullException.ThrowIfNull(serviceProvider);
    ArgumentNullException.ThrowIfNull(options);

    _serviceProvider = serviceProvider;
    _options = options.Value;
  }

  public ControllerDiagnostics GetDiagnostics()
  {
    var limits =
      new ControllerLimitsInfo(
        _options.MaxChargePowerKw,
        _options.MaxDischargePowerKw,
        _options.MinimumBatterySocKwh,
        _options.MaximumBatterySocKwh);

    try
    {
      // Same check as the readiness probe: the gateway singleton loads
      // the native library, validates the ABI and creates the handle.
      _ = _serviceProvider.GetRequiredService<IControllerGateway>();

      return new ControllerDiagnostics(
        Ready: true,
        AbiVersion: NativeControllerMethods.GetAbiVersion(),
        Limits: limits);
    }
    catch (Exception exception)
      when (exception is InvalidOperationException
              or ArgumentException
              or DllNotFoundException
              or EntryPointNotFoundException
              or BadImageFormatException)
    {
      return new ControllerDiagnostics(
        Ready: false,
        AbiVersion: null,
        Limits: limits);
    }
  }
}
