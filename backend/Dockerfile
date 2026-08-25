# syntax=docker/dockerfile:1@sha256:ecfaec9ed6d810b56388c508f4121597bfbba70d41a6dfeee4d8cad5f295fc32

FROM mcr.microsoft.com/dotnet/sdk:10.0-noble@sha256:e1ffd2a92ae84c1291bc1b6887501f8af98e6331e7af6d4c8d37168c5e87a64c AS build

WORKDIR /src

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
    && rm -rf /var/lib/apt/lists/*

COPY global.json ./
COPY hardware ./hardware
COPY controller ./controller
COPY backend ./backend

RUN cmake \
      -S controller \
      -B controller/build \
      -DCMAKE_BUILD_TYPE=Release \
      -DBUILD_TESTING=OFF \
      -DGRIDFLEX_BUILD_BENCHMARKS=OFF \
    && cmake \
      --build controller/build \
      --target gridflex_controller_native \
      --parallel \
    && cmake \
      --install controller/build \
      --prefix controller/package \
      --component runtime

RUN bash backend/scripts/package-linux-runtime.sh

FROM mcr.microsoft.com/dotnet/aspnet:10.0-noble@sha256:a4556ed033fa96f984bb7a8d348851cb2d36b1281dd2420070045f664fbb5f94 AS runtime

WORKDIR /app

COPY --from=build /src/backend/dist/linux-x64/app/ ./
COPY --from=build /src/backend/dist/linux-x64/lib/ ./lib/

ENV ASPNETCORE_HTTP_PORTS=8080
ENV LD_LIBRARY_PATH=/app/lib

EXPOSE 8080

USER app

ENTRYPOINT ["dotnet", "GridFlex.Api.dll"]
