# Build container for fo-dicom 4.0.8 (tag), commit de4c382, 2021-09-10.
#
# Pinned by digest, not by tag: a tag moves, a digest does not (Rule 5).
# mcr.microsoft.com/dotnet/sdk:8.0 as pulled on 2026-10-05.
FROM mcr.microsoft.com/dotnet/sdk:8.0@sha256:78235e09001f52b6592c458ac010775ebac6725422e80cd0c1650590f67b2743

# No apt-get. The SDK image already holds the compiler (Roslyn), MSBuild and
# NuGet, so no package server is involved and the archived-mirror trap cannot
# happen. The C# oracle needs no separate language server either: Roslyn ships
# inside the SDK, so there is no compile_commands.json step.

ENV DOTNET_CLI_TELEMETRY_OPTOUT=1
ENV DOTNET_NOLOGO=1
ENV DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1

# The package cache and every build output live under build-container/, inside
# the mounted tree. Two consequences, both wanted:
#   - a container build never fights a host SDK over the project's obj/ and bin/
#   - the restored packages survive the container, so the second build is offline
ENV NUGET_PACKAGES=/work/build-container/.nuget-cache

WORKDIR /work
