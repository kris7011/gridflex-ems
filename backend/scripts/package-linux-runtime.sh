#!/usr/bin/env bash

set -euo pipefail

script_directory="$(
    cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
    pwd
)"

repository_root="$(
    cd -- "${script_directory}/../.."
    pwd
)"

native_runtime_path="${repository_root}/controller/package/lib/libgridflex_controller_native.so"

output_root="${repository_root}/backend/dist/linux-x64"
application_output="${output_root}/app"
native_output="${output_root}/lib"

if [[ ! -f "${native_runtime_path}" ]]; then
    echo "Native controller runtime was not found:" >&2
    echo "${native_runtime_path}" >&2
    echo >&2
    echo "Build and install the native runtime before creating the backend package." >&2
    exit 1
fi

rm -rf "${output_root}"

mkdir -p "${application_output}"
mkdir -p "${native_output}"

dotnet publish \
    "${repository_root}/backend/GridFlex.Api/GridFlex.Api.csproj" \
    --configuration Release \
    --runtime linux-x64 \
    --self-contained false \
    --output "${application_output}"

cp \
    "${native_runtime_path}" \
    "${native_output}/libgridflex_controller_native.so"

if [[ ! -f "${application_output}/GridFlex.Api.dll" ]]; then
    echo "Published GridFlex.Api.dll was not found." >&2
    exit 1
fi

if [[ ! -f "${native_output}/libgridflex_controller_native.so" ]]; then
    echo "Packaged native controller runtime was not found." >&2
    exit 1
fi

echo "GridFlex Linux backend runtime package created:"
echo "${output_root}"
echo
echo "Application:"
echo "${application_output}"
echo
echo "Native runtime:"
echo "${native_output}/libgridflex_controller_native.so"
