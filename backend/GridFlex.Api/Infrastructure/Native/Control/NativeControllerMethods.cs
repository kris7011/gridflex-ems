using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Text;

namespace GridFlex.Api.Infrastructure.Native.Control;

internal static partial class NativeControllerMethods
{
  internal const string LibraryName =
    "gridflex_controller_native";

  /// <summary>
  /// Version 2 adds <c>gridflex_controller_last_error_message</c>; the
  /// version 1 functions and structures are unchanged.
  /// </summary>
  internal const uint ExpectedAbiVersion = 2;

  // Covers every message the controller produces today without a heap
  // allocation; longer messages are read in a second call.
  private const int LastErrorStackBufferSize = 256;

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

  [LibraryImport(
    LibraryName,
    EntryPoint = "gridflex_controller_last_error_message")]
  [UnmanagedCallConv(
    CallConvs = [typeof(CallConvCdecl)])]
  internal static unsafe partial nuint GetLastErrorMessage(
    byte* buffer,
    nuint bufferSize);

  /// <summary>
  /// Reads why the previous <see cref="Create"/> or <see cref="Decide"/>
  /// call failed, or returns <see langword="null"/> if it succeeded.
  /// </summary>
  /// <remarks>
  /// The native state is thread-local. Calling this synchronously right
  /// after the failed call is safe because a managed thread does not
  /// change its operating-system thread between two synchronous calls.
  /// </remarks>
  internal static unsafe string? ReadLastErrorMessage()
  {
    Span<byte> stackBuffer =
      stackalloc byte[LastErrorStackBufferSize];

    nuint length;

    fixed (byte* pointer = stackBuffer)
    {
      length =
        GetLastErrorMessage(
          pointer,
          (nuint)stackBuffer.Length);
    }

    if (length == 0)
    {
      return null;
    }

    if (length < (nuint)stackBuffer.Length)
    {
      return Encoding.UTF8.GetString(
        stackBuffer[..(int)length]);
    }

    var heapBuffer =
      new byte[checked((int)length + 1)];

    fixed (byte* pointer = heapBuffer)
    {
      length =
        GetLastErrorMessage(
          pointer,
          (nuint)heapBuffer.Length);
    }

    return Encoding.UTF8.GetString(
      heapBuffer,
      0,
      (int)Math.Min(length, (nuint)(heapBuffer.Length - 1)));
  }
}
