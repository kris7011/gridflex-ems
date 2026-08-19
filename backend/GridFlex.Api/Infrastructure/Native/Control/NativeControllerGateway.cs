using GridFlex.Api.Application.Control;

namespace GridFlex.Api.Infrastructure.Native.Control;

internal sealed class NativeControllerGateway
  : IControllerGateway, IDisposable
{
  private readonly NativeControllerSafeHandle _handle;

  internal NativeControllerGateway(
    NativeControllerLimits limits)
  {
    var actualAbiVersion =
      NativeControllerMethods.GetAbiVersion();

    if (actualAbiVersion !=
        NativeControllerMethods.ExpectedAbiVersion)
    {
      throw new InvalidOperationException(
        $"Native controller ABI version {actualAbiVersion} " +
        $"does not match expected version " +
        $"{NativeControllerMethods.ExpectedAbiVersion}.");
    }

    var status =
      NativeControllerMethods.Create(
        in limits,
        out var handle);

    if (status != NativeControllerStatus.Ok)
    {
      handle?.Dispose();

      if (status == NativeControllerStatus.InvalidLimits)
      {
        throw new ArgumentException(
          "Native controller rejected the configured limits.",
          nameof(limits));
      }

      throw new InvalidOperationException(
        $"Native controller creation failed with status " +
        $"'{status}'.");
    }

    if (handle is null || handle.IsInvalid)
    {
      handle?.Dispose();

      throw new InvalidOperationException(
        "Native controller creation returned an invalid handle.");
    }

    _handle = handle;
  }

  public ControlDecision Decide(
    EnergyMeasurementInput measurement)
  {
    ArgumentNullException.ThrowIfNull(measurement);

    if (_handle.IsClosed)
    {
      throw new ObjectDisposedException(
        nameof(NativeControllerGateway));
    }

    var nativeMeasurement =
      new NativeControllerMeasurement
      {
        StepNumber = measurement.StepNumber,
        ElapsedTimeHours = measurement.ElapsedTimeHours,
        IntervalHours = measurement.IntervalHours,
        GeneratedEnergyKwh = measurement.GeneratedEnergyKwh,
        ConsumedEnergyKwh = measurement.ConsumedEnergyKwh,
        NetEnergyKwh = measurement.NetEnergyKwh,
        BatteryStateOfChargeKwh =
          measurement.BatteryStateOfChargeKwh,
        GridImportEnergyKwh =
          measurement.GridImportEnergyKwh,
        GridExportEnergyKwh =
          measurement.GridExportEnergyKwh,
        UnresolvedEnergyKwh =
          measurement.UnresolvedEnergyKwh
      };

    var status =
      NativeControllerMethods.Decide(
        _handle,
        in nativeMeasurement,
        out var nativeDecision);

    if (status != NativeControllerStatus.Ok)
    {
      if (status ==
          NativeControllerStatus.InvalidMeasurement)
      {
        throw new ArgumentException(
          "Native controller rejected the measurement.",
          nameof(measurement));
      }

      throw new InvalidOperationException(
        $"Native controller decision failed with status " +
        $"'{status}'.");
    }

    return new ControlDecision(
      SourceStepNumber: nativeDecision.SourceStepNumber,
      Action: MapAction(nativeDecision.Action),
      RequestedPowerKw: nativeDecision.RequestedPowerKw);
  }

  public void Dispose()
  {
    _handle.Dispose();
  }

  private static ControlAction MapAction(
    NativeControlAction action)
  {
    return action switch
    {
      NativeControlAction.Idle =>
        ControlAction.Idle,

      NativeControlAction.ChargeBattery =>
        ControlAction.ChargeBattery,

      NativeControlAction.DischargeBattery =>
        ControlAction.DischargeBattery,

      NativeControlAction.ImportFromGrid =>
        ControlAction.ImportFromGrid,

      NativeControlAction.ExportToGrid =>
        ControlAction.ExportToGrid,

      _ => throw new InvalidOperationException(
        $"Native controller returned unsupported control action " +
        $"'{(int)action}'.")
    };
  }
}
