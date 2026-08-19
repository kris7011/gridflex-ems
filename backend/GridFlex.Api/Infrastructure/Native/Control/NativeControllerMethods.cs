using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace GridFlex.Api.Infrastructure.Native.Control;

internal static partial class NativeControllerMethods
{
  internal const string LibraryName =
    "gridflex_controller_native";

  internal const uint ExpectedAbiVersion = 1;

  [LibraryImport(
    LibraryName,
    EntryPoint = "gridflex_controller_abi_version")]
  [UnmanagedCallConv(
    CallConvs = [typeof(CallConvCdecl)])]
  internal static partial uint GetAbiVersion();

  [LibraryImport(
    LibraryName,
    EntryPoint = "gridflex_controller_create")]
  [UnmanagedCallConv(
    CallConvs = [typeof(CallConvCdecl)])]
  internal static partial NativeControllerStatus Create(
    in NativeControllerLimits limits,
    out NativeControllerSafeHandle handle);

  [LibraryImport(
    LibraryName,
    EntryPoint = "gridflex_controller_destroy")]
  [UnmanagedCallConv(
    CallConvs = [typeof(CallConvCdecl)])]
  internal static partial void Destroy(
    nint handle);

  [LibraryImport(
    LibraryName,
    EntryPoint = "gridflex_controller_decide")]
  [UnmanagedCallConv(
    CallConvs = [typeof(CallConvCdecl)])]
  internal static partial NativeControllerStatus Decide(
    NativeControllerSafeHandle handle,
    in NativeControllerMeasurement measurement,
    out NativeControllerDecision decision);
}
