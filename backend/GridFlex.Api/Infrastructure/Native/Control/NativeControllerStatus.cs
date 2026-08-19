namespace GridFlex.Api.Infrastructure.Native.Control;

internal enum NativeControllerStatus : int
{
  Ok = 0,
  InvalidArgument = 1,
  InvalidLimits = 2,
  InvalidMeasurement = 3,
  InternalError = 4
}
