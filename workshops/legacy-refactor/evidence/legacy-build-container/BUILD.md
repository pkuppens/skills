# Build container — fo-dicom 4.0.8

A reproducible, offline-capable build of `FO-DICOM.Core` in a container.
The build is [oracle step 1](../.claude/skills/legacy-build-container/SKILL.md):
without it, no change to this code base can be proved complete.

## Result

```text
Base image:   mcr.microsoft.com/dotnet/sdk:8.0@sha256:78235e09001f52b6592c458ac010775ebac6725422e80cd0c1650590f67b2743
Image size:   867 MB
Compiler:     .NET SDK 8.0.425, Roslyn (C# 8 requested by the project)
Build system: dotnet build / MSBuild, from the SDK image
Index:        Roslyn, in the SDK. No compile_commands.json applies.
Target built: FO-DICOM.Core -> fo-dicom.core.dll, netstandard2.0, 1540096 bytes
Build matrix: ["FO-DICOM.Core/netstandard2.0"]
Build time:   image 0.9 s (no layers beyond FROM); restore 5.7 s online,
              5.3 s offline from the vendored feed; build 7.1 s. 32 cores.
Network:      not needed after the image exists and the feed is vendored. Proved
              with --network none and a negative control; see "Offline" below.
Warnings:     0 errors, 11 warnings, 5 distinct codes:
              CS0618, CS0659, CS0661, CS0675, CS1696
```

## Which toolchain, and why

| Evidence | File | Conclusion |
| --- | --- | --- |
| `<TargetFramework>netstandard2.0</TargetFramework>` | `FO-DICOM.Core/FO-DICOM.Core.csproj:4` | SDK-style project, any modern .NET SDK can target it |
| `<LangVersion>8.0</LangVersion>` | `FO-DICOM.Core/FO-DICOM.Core.csproj:19` | C# 8, so an SDK of 3.1 or newer |
| `Project Sdk="Microsoft.NET.Sdk"` | same file, line 1 | `dotnet build`, not `msbuild` on a `.sln` |
| `netcoreapp2.1;net462;netcoreapp3.1` | `Tests/FO-DICOM.Tests/FO-DICOM.Tests.csproj` | the **oldest** requirement in the repo, and out of this matrix — see below |
| 51 further `.csproj` + 12 `.vcxproj` | `git ls-files` | Android, iOS, Unity, Hololens, WinForms tools, and a C++/CLI native codec. None on the path to the core library. |

So: the **newest** SDK that still builds the target was preferred, per Step 3 of
the skill. .NET SDK 8.0 is the current LTS and compiles `netstandard2.0` with
C# 8 directly. Nothing older is needed, and nothing older is cheaper.

### What is deliberately not built

`net462` needs the .NET Framework reference assemblies; `netcoreapp2.1` and
`netcoreapp3.1` are out of support and their targeting packs are not in the
SDK 8.0 image. The WinForms tools (`Tools/DICOM Dump`) and the C++/CLI
`Native/Desktop/*.vcxproj` need Windows. Building any of those means a Windows
container or Mono, and none of it is on the path to `FO-DICOM.Core`.

**Therefore any claim of complete recall from this build is limited to the one
matrix entry above.** That is the point of writing the matrix down.

## Prerequisites

A shell, `git`, and Docker with Linux containers. Network for the first image
pull and the first `dotnet restore` only.

## Commands

Set `R` to this repository's root, then paste the rest.

```bash
R="$(git rev-parse --show-toplevel)"
```

**On Windows in Git Bash, prefix every `docker` command with
`MSYS_NO_PATHCONV=1`** (or `export` it once). Git Bash otherwise rewrites
`-w /work` into a Windows path and `docker run` fails with
`the working directory 'C:/Program Files/Git/work' is invalid`.

### 1. Build the image

```bash
docker build -t fo-dicom-build "$R/build-container"
```

### 2. Restore, once, with a network

Writes the package cache to `build-container/.nuget-cache/`, inside the mounted
tree, so it survives the container.

```bash
docker run --rm -v "$R:/work" -w /work fo-dicom-build \
  dotnet restore FO-DICOM.Core/FO-DICOM.Core.csproj \
    -p:BaseIntermediateOutputPath=/work/build-container/obj/core/
```

### 3. Build

`--network none` is not decoration. It is the assertion that this step needs no
network, checked by the daemon.

```bash
docker run --rm --network none -v "$R:/work" -w /work fo-dicom-build \
  dotnet build FO-DICOM.Core/FO-DICOM.Core.csproj -c Release --no-restore \
    -p:BaseIntermediateOutputPath=/work/build-container/obj/core/ \
    -p:BaseOutputPath=/work/build-container/bin/core/
```

Expected: `0 Error(s)`, `11 Warning(s)`.

### 4. Smoke test

```bash
ls -l "$R/build-container/bin/core/Release/netstandard2.0/fo-dicom.core.dll"
```

### Interactive shell, for an agent or a person

Rule 3: the agent must run where the compiler runs.

```bash
docker run --rm -it -v "$R:/work" -w /work fo-dicom-build bash
```

The source is **mounted, never copied** (Rule 4). The image never contains the
code, which matters when the code is confidential.

## Why the build outputs are redirected

`BaseIntermediateOutputPath` and `BaseOutputPath` point into
`build-container/`. Without that, a container build and a host build share
`FO-DICOM.Core/obj/`, and the two SDKs overwrite each other's
`project.assets.json`. The symptom is a restore that looks fine and a build
that fails on a package the other SDK resolved differently.

`NUGET_PACKAGES` is set in the `Dockerfile` for the same reason.

## Offline

`build-container/nuget-feed/` holds 22 `.nupkg` files, 11 MB — the full
transitive closure of `FO-DICOM.Core`. `nuget.offline.config` declares that
folder as the only source, with `<clear />` ahead of it, so nuget.org is gone
rather than merely unreachable.

Restore from the feed with a cold cache and no network:

```bash
rm -rf "$R/build-container/.nuget-cache" "$R/build-container/obj"
docker run --rm --network none -v "$R:/work" -w /work fo-dicom-build \
  dotnet restore FO-DICOM.Core/FO-DICOM.Core.csproj \
    --configfile /work/build-container/nuget.offline.config \
    -p:BaseIntermediateOutputPath=/work/build-container/obj/core/
```

Measured: `Restored ... (in 5.31 sec)`, then step 3 builds green.

### Negative control

A pass proves nothing unless the same setup fails without the feed. Run it:

```bash
rm -rf "$R/build-container/.nuget-cache" "$R/build-container/obj"
docker run --rm --network none -v "$R:/work" -w /work fo-dicom-build bash -lc \
  'printf "%s\n" "<configuration><packageSources><clear /></packageSources></configuration>" > /tmp/empty.config
   dotnet restore FO-DICOM.Core/FO-DICOM.Core.csproj --configfile /tmp/empty.config \
     -p:BaseIntermediateOutputPath=/work/build-container/obj/core/'
```

Measured: exit 1, six `error NU1100` lines. Re-run step 3's offline restore
afterwards to get back to a green tree.

### Fully air-gapped transfer

```bash
docker save -o fo-dicom-build.tar fo-dicom-build   # 867 MB
# on the target: docker load -i fo-dicom-build.tar
```

With the image loaded and `build-container/nuget-feed/` present, nothing in the
procedure above touches a network.

## Reproducing the vendored feed

If a `PackageReference` changes, regenerate the feed with a network once:

```bash
docker run --rm -v "$R:/work" -w /work fo-dicom-build bash -lc '
  rm -rf /work/build-container/nuget-feed && mkdir -p /work/build-container/nuget-feed /tmp/pkgcache
  dotnet restore FO-DICOM.Core/FO-DICOM.Core.csproj \
    -p:RestorePackagesPath=/tmp/pkgcache \
    -p:BaseIntermediateOutputPath=/work/build-container/obj/core/
  find /tmp/pkgcache -name "*.nupkg" -not -name "*.symbols.nupkg" \
    -exec cp {} /work/build-container/nuget-feed/ \;'
```

Then re-run the offline restore and the negative control. A feed that was not
checked against the negative control is not evidence.

## Files in this directory

| File | Purpose |
| --- | --- |
| `Dockerfile` | the environment, base image pinned by digest |
| `BUILD.md` | this file |
| `nuget.offline.config` | `<clear />` plus the local feed |
| `nuget-feed/` | 22 vendored `.nupkg` files, 11 MB |
| `.gitignore` | ignores `obj/`, `bin/`, `.nuget-cache/` |

Nothing outside `build-container/` was modified. The project belongs to
somebody else.
