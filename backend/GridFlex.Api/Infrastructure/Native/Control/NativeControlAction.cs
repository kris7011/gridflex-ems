namespace GridFlex.Api.Infrastructure.Native.Control;

internal enum NativeControlAction : int
{
  Idle = 0,
  ChargeBattery = 1,
  DischargeBattery = 2,
  ImportFromGrid = 3,
  ExportToGrid = 4
}
