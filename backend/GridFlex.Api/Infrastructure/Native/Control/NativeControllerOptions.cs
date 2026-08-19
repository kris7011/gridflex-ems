namespace GridFlex.Api.Infrastructure.Native.Control;

internal sealed class NativeControllerOptions
{
  internal const string SectionName =
    "NativeController";

  public double MaxChargePowerKw
  {
    get;
    set;
  }

  public double MaxDischargePowerKw
  {
    get;
    set;
  }

  public double MinimumBatterySocKwh
  {
    get;
    set;
  }

  public double MaximumBatterySocKwh
  {
    get;
    set;
  }
}
