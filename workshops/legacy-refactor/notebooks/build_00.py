"""Author 00_setup.ipynb. Run from the repo root, then execute the notebook.

Writes cells only. Outputs come from a real kernel run. See notebooks/README.md.
"""
import nbformat as nbf

nb = nbf.v4.new_notebook()
md = lambda t: nbf.v4.new_markdown_cell(t)
code = lambda t: nbf.v4.new_code_cell(t)

nb.cells = [
md("""\
# 00 — Setup: the build environment is an artifact

**Proves:** claim 1 of [../THESIS.md](../THESIS.md) — rung 1 of the ladder must exist before anything else.
**Skill:** [`legacy-build-container`](../../../skills/legacy-build-container/SKILL.md)
**Needs:** .NET SDK, git, Docker. Network for the first run only.
**Run time:** about 1 minute warm, a few minutes on the first run while images and packages download.
**State:** EXECUTED

---

## What this notebook is for

I did not build a development environment for this workshop. I built the
**skill that builds one**, and this notebook is the proof that the skill works.

That difference is the whole point. A Dockerfile solves one toolchain once. A
skill that writes the right Dockerfile for *your* toolchain solves it again for
the next one.

Two environments are set up here, because the audience has two languages:

| Language | Toolchain | Why this one |
| --- | --- | --- |
| C# | .NET SDK on the host | fo-dicom 4.0.8 builds in about a second. Readable, fast, no CMake. |
| C++ | `gcc:4.9` in a container | A real 2016 compiler. The host has no C++ toolchain at all, which is the normal situation. |

Decisions behind this: [ADR 002](../../../docs/decisions/002-workshop-container-environment.md).
"""),

code("""\
import os, subprocess, shlex, re, time, shutil, json

ROOT = os.path.abspath(os.path.join(os.getcwd(), "..", "..", ".."))
WORKSPACE = os.path.join(ROOT, "tmp", "workshop-workspace")
SPECIMEN = os.path.join(WORKSPACE, "fo-dicom")
SPECIMEN_TAG = "4.0.8"
PROJECT = os.path.join(SPECIMEN, "FO-DICOM.Core", "FO-DICOM.Core.csproj")
CPP_FIXTURE = os.path.abspath(os.path.join(os.getcwd(), "..", "fixtures", "cpp"))
CPP_IMAGE = "gcc:4.9"

def run(cmd, cwd=None, timeout=1800):
    p = subprocess.run(cmd if isinstance(cmd, list) else shlex.split(cmd),
                       cwd=cwd, capture_output=True, text=True,
                       errors="replace", timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")

print("repo root :", ROOT)
print("workspace :", os.path.relpath(WORKSPACE, ROOT), "(gitignored)")
print()
for tool in ("git", "dotnet", "docker"):
    path = shutil.which(tool)
    print("%-8s %s" % (tool, path or "NOT FOUND"))"""),

md("""\
## Step 1 — Which toolchain does the code need?

Read the build files, not the documentation. The build files are current.
"""),

code("""\
if not os.path.isdir(SPECIMEN):
    os.makedirs(WORKSPACE, exist_ok=True)
    print("cloning fo-dicom at tag %s ..." % SPECIMEN_TAG)
    rc, out = run(["git", "clone", "--quiet", "--depth", "1", "--branch",
                   SPECIMEN_TAG,
                   "https://github.com/fo-dicom/fo-dicom.git", "fo-dicom"],
                  cwd=WORKSPACE)
    print("clone exit:", rc)
else:
    print("specimen already present, not re-cloning")

rc, out = run(["git", "describe", "--tags", "--always"], cwd=SPECIMEN)
print("specimen tag :", out.strip())

# What the build files say the project needs.
tfms = set()
for base, dirs, names in os.walk(SPECIMEN):
    dirs[:] = [d for d in dirs if d not in (".git", "obj", "bin")]
    for n in names:
        if n.endswith(".csproj"):
            with open(os.path.join(base, n), encoding="utf-8", errors="replace") as fh:
                for m in re.finditer(r"<TargetFrameworks?>([^<]+)<", fh.read()):
                    tfms.update(t.strip() for t in m.group(1).split(";"))

print()
print("target frameworks found across the clone:")
for t in sorted(tfms):
    print("   ", t)"""),

md("""\
`netstandard1.3` and `net462` date this code to about 2017. That is the
evidence for calling it legacy — not an opinion about its style.

The project we build is `FO-DICOM.Core`, which targets `netstandard2.0`. A
current SDK can build that, so the C# half needs no container.

## Step 2 — Rung 1 for C#: a green build

Measure the build. Build time decides whether the loop in `05_refactoring` is
usable live.
"""),

code("""\
# Build matrix. One entry on purpose: this workshop proves the method, not the
# full configuration space. Every claim of complete recall is limited to the
# entries listed here. Adding a second entry costs one line.
# See ADR 002, decision 7.
MATRIX = ["FO-DICOM.Core/netstandard2.0"]
# MATRIX += ["DICOM/net462", "DICOM/netstandard1.3"]   # the rest of the clone

t0 = time.time()
rc, out = run(["dotnet", "build", PROJECT, "-v", "q", "--nologo", "-t:Rebuild"])
build_s = time.time() - t0

errors = len(re.findall(r": error ", out))
warnings = len(set(re.findall(r": warning (CS\\d+)", out)))

print("build matrix     :", MATRIX)
print("exit code        :", rc)
print("errors           :", errors)
print("distinct warnings:", warnings)
print("build time       : %.1f s" % build_s)
print()
print("Rung 1 exists for C#." if rc == 0 else "BUILD FAILED - fix this first.")"""),

md("""\
## Step 3 — Rung 1 for C++: there is no host toolchain

This is the ordinary situation on a developer laptop, and it is why the skill
exists.
"""),

code("""\
print("g++ on the host :", shutil.which("g++") or "NOT FOUND")
print("cmake on host   :", shutil.which("cmake") or "NOT FOUND")
print()
print("Without a C++ compiler there is no rung 1, so an agent cannot prove that")
print("a change to C++ code is complete. It can only guess. The container")
print("supplies the missing rung.")"""),

md("""\
## Step 4 — The container, pinned by digest

A tag moves. A digest does not. Under IEC 62304 the digest is what makes the
build environment a controlled, recorded fact rather than "whatever was current
that day".

`gcc:4.9` is used instead of an old distribution plus `apt`, which avoids the
trap recorded in the skill: old distributions moved their package servers, so
`apt-get update` returns 404 on images such as `ubuntu:14.04`. An image that
already contains the compiler needs no package server at all.
"""),

code("""\
rc, out = run(["docker", "image", "inspect", CPP_IMAGE, "--format", "{{index .RepoDigests 0}}"])
if rc != 0:
    print("pulling %s ..." % CPP_IMAGE)
    print(run(["docker", "pull", "--quiet", CPP_IMAGE])[1].strip())
    rc, out = run(["docker", "image", "inspect", CPP_IMAGE,
                   "--format", "{{index .RepoDigests 0}}"])
digest = out.strip()

rc, sizes = run(["docker", "image", "inspect", CPP_IMAGE, "--format", "{{.Size}}"])
size_mb = int(sizes.strip()) / (1024 * 1024) if sizes.strip().isdigit() else None

rc, vers = run(["docker", "run", "--rm", CPP_IMAGE, "bash", "-lc",
                "g++ --version | head -1; cat /etc/debian_version; ld --version | head -1"])

print("image   :", CPP_IMAGE)
print("digest  :", digest)
if size_mb:
    print("size    : %.0f MB" % size_mb)
print()
print("inside the container:")
for line in vers.strip().splitlines():
    if line.strip() and "not a tty" not in line:
        print("   ", line.strip())"""),

md("""\
## Step 5 — Prove the C++ oracle works, with the case C# cannot show

In C#, the text search failed by **over**-reporting (see `05_refactoring`). In
C++ it fails by **under**-reporting, and that is the more famous problem: a
macro writes the call, so the call is not in any source file.

The fixture in [`../fixtures/cpp/`](../fixtures/cpp/) is small on purpose. It is
a reproduction of the mechanism, **not** a large code base. DCMTK and VTK show
the same thing at a scale nobody can read, and building DCMTK is a separate
task.

Three paths reach the deprecated function:

1. a direct call,
2. three accessors written by a macro, so their names exist in no file,
3. a template body, checked only where it is instantiated.
"""),

code("""\
mount = CPP_FIXTURE.replace(os.sep, "/")

with open(os.path.join(CPP_FIXTURE, "main.cpp"), encoding="utf-8") as fh:
    main_src = fh.readlines()
with open(os.path.join(CPP_FIXTURE, "legacy_api.h"), encoding="utf-8") as fh:
    hdr_src = fh.readlines()

def real_hits(lines, name):
    \"\"\"Count 'setLegacy' outside comments - the best a text search can do.\"\"\"
    out = []
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith("//"):
            continue
        if name in line:
            out.append((i, s))
    return out

ts = [("legacy_api.h", i, s) for i, s in real_hits(hdr_src, "setLegacy")] + \\
     [("main.cpp", i, s) for i, s in real_hits(main_src, "setLegacy")]

# Of the lines a text search returns, which are actually CALL sites? A
# declaration, a definition, and a macro or template body are not call sites.
def classify(path, line_no, text):
    if "LEGACY_DEPRECATED" in text:
        return "declaration"
    if text.startswith("void Geometry::setLegacy"):
        return "definition"
    if "Set##Name" in text:
        return "macro body"
    if "setFrom" in text:
        return "template body"
    return "CALL SITE"

print("text search for 'setLegacy', comments removed:")
print()
for f, i, s in ts:
    print("    %-14s %s:%d: %s" % (classify(f, i, s), f, i, s))
print()
visible = [t for t in ts if classify(*t) == "CALL SITE"]
print("lines returned         : %d" % len(ts))
print("actual call sites shown: %d   <- all a text search can give you" % len(visible))
print()
print("The macro body is ONE line. It becomes three call sites, and their names")
print("(SetWidth, SetHeight, SetDepth) appear in no file at all.")"""),

code("""\
rc, out = run(["docker", "run", "--rm", "-v", mount + ":/src", "-w", "/src",
               CPP_IMAGE, "g++", "-std=c++03",
               "-Werror=deprecated-declarations", "-c", "main.cpp",
               "-o", "/tmp/main.o"])

# One site per diagnostic. A macro expansion is reported at the macro USE line,
# which is the line a text search can never find.
sites = []
lines = out.splitlines()
for i, line in enumerate(lines):
    m = re.match(r"([\\w./]+):(\\d+):\\d+: error: .*is deprecated", line)
    if not m:
        continue
    where = "%s:%s" % (m.group(1), m.group(2))
    detail = " <- direct call"
    # A macro expansion is reported AFTER the diagnostic, as a note.
    for nxt in lines[i + 1:i + 5]:
        mm = re.match(r"([\\w./]+):(\\d+):\\d+: note: in expansion of macro", nxt)
        if mm:
            detail = " <- written by the macro used at %s:%s" % (mm.group(1), mm.group(2))
            break
    # A template instantiation is reported BEFORE it, as context.
    if detail == " <- direct call":
        for prev in reversed(lines[max(0, i - 4):i]):
            pm = re.match(r"([\\w./]+):(\\d+):\\d+:\\s+required from here", prev)
            if pm:
                detail = " <- template instantiated at %s:%s" % (pm.group(1), pm.group(2))
                break
    sites.append(where + detail)

print("compiler exit code :", rc, "(non-zero on purpose)")
print("deprecated call sites reported : %d" % len(sites))
print()
for s in sites:
    print("   ", s)"""),

md("""\
### What the two lists show

| Method | Lines returned | Call sites it can actually show you |
| --- | --- | --- |
| Text search for `setLegacy` | 5 | **1.** The other four are a declaration, a definition, a macro body and a template body. |
| Compiler, `-Werror=deprecated-declarations` | 5 diagnostics | **5.** The direct call, three macro expansions, and the template instantiation. |

The two totals are both 5 and they mean different things. That is the trap in
one line: a text search returns *lines containing a name*, and a compiler
returns *uses of a function*. Counting the first and reporting it as the second
is the mistake this whole workshop is about.

The three macro-generated call sites are the ones that matter. `SetWidth`,
`SetHeight` and `SetDepth` **appear in no source file** — the preprocessor
writes them. No text search can list them, and no amount of care fixes that.
The compiler lists them, and it names the macro-use line.

This is also where the limits are visible. The template body is checked only
because `main.cpp` instantiates it. Remove that line and the compiler goes
quiet, while the code is still there.
"""),

md("""\
## Step 6 — Prove it works with no network

Both events are in person, and a guest network may not exist or may block
outbound HTTPS. The demo must not need one.

`dotnet build --no-restore` is **not** a proof on its own. It only skips the
restore step, and it still depends on packages already sitting in the global
cache. A warm cache is not an artifact you can carry.

The real proof uses a **local feed with the source list cleared**. If `<clear />`
removes nuget.org and the restore still succeeds, then nothing remote was
needed. That is a statement about the configuration, not about whatever the
network happened to be doing at the time.

Build the feed once on a machine that has already restored online, then carry
`offline-feed/` to the demonstration laptop.
"""),

code("""\
import json, shutil

feed = os.path.join(SPECIMEN, "offline-feed")
os.makedirs(feed, exist_ok=True)
cache = os.path.expanduser("~/.nuget/packages")

with open(os.path.join(SPECIMEN, "FO-DICOM.Core", "obj", "project.assets.json"),
          encoding="utf-8-sig") as fh:
    assets = json.load(fh)

copied, missing = [], []
for key, v in assets.get("libraries", {}).items():
    if v.get("type") != "package":
        continue
    name, _, ver = key.partition("/")
    nupkg = os.path.join(cache, name.lower(), ver,
                         "%s.%s.nupkg" % (name.lower(), ver))
    if os.path.isfile(nupkg):
        shutil.copy2(nupkg, feed)
        copied.append(name)
    else:
        missing.append(key)

size_mb = sum(os.path.getsize(os.path.join(feed, f))
              for f in os.listdir(feed)) / 1048576
print("packages vendored :", len(copied))
print("feed size         : %.1f MB" % size_mb)
print("missing           :", missing or "none")

def write_config(path, with_feed):
    lines = ['<?xml version="1.0" encoding="utf-8"?>',
             "<configuration>",
             "  <packageSources>",
             "    <clear />"]
    if with_feed:
        lines.append('    <add key="offline" value="offline-feed" />')
    lines += ["  </packageSources>", "</configuration>", ""]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(os.linesep.join(lines))
    return path

offline_cfg = write_config(os.path.join(SPECIMEN, "nuget.offline.config"), True)
print("wrote            :", os.path.basename(offline_cfg))"""),

code("""\
cold = os.path.join(WORKSPACE, "offline-test", "packages")
shutil.rmtree(os.path.join(WORKSPACE, "offline-test"), ignore_errors=True)
os.makedirs(cold, exist_ok=True)

rc_ok, out_ok = run(["dotnet", "restore", PROJECT, "--configfile", offline_cfg,
                     "--packages", cold, "--force"], cwd=SPECIMEN)
print("A. restore from the local feed only, into a cold package folder")
print("   exit code :", rc_ok, " <- 0 means nothing remote was needed")
for line in out_ok.splitlines():
    if "Restored" in line:
        print("   restored in:", line.strip().split("(in ")[-1].rstrip(").").strip())

env = dict(os.environ, NUGET_PACKAGES=cold)
t0 = time.time()
p = subprocess.run(["dotnet", "build", PROJECT, "-v", "q", "--nologo",
                    "--no-restore"], cwd=SPECIMEN, capture_output=True,
                   text=True, errors="replace", env=env)
offline_build_s = time.time() - t0
combined = (p.stdout or "") + (p.stderr or "")
print()
print("B. build --no-restore against that cold folder")
print("   exit code  :", p.returncode)
print("   errors     :", len(re.findall(r": error ", combined)))
print("   build time : %.1f s" % offline_build_s)"""),

code("""\
# Negative control. Without it, "A worked" proves nothing - the restore could
# simply have reached the network. Clear every source and offer no feed.
nosrc = write_config(os.path.join(SPECIMEN, "nuget.nosources.config"), False)
cold2 = os.path.join(WORKSPACE, "offline-test", "packages-nosource")
shutil.rmtree(cold2, ignore_errors=True)
os.makedirs(cold2, exist_ok=True)

rc_bad, out_bad = run(["dotnet", "restore", PROJECT, "--configfile", nosrc,
                       "--packages", cold2, "--force"], cwd=SPECIMEN)
nu1101 = [l.strip() for l in out_bad.splitlines() if "NU1101" in l]

print("C. negative control: no feed at all, cold folder")
print("   exit code     :", rc_bad, " <- non-zero is the expected result")
print("   NU1101 errors :", len(nu1101))
for l in nu1101[:3]:
    print("      ", l.split(" : ")[-1][:100])
print()
print("So A did not pass by accident. With no local feed the restore cannot find")
print("a single package. With the local feed it finds every one of them.")"""),

md("""\
## Step 7 — Record the environment

The skill's value is that the next attempt is faster. So a green build adds one
row to
[`verified-environments.md`](../../../skills/legacy-build-container/reference/verified-environments.md),
and a human merges it.

The notebook prints the row. It does not write the file. The record enters the
repository through a pull request, which is what keeps it reviewable — an
artifact that edits itself has no change control, and in a regulated process
that is a defect rather than a feature.
"""),

code("""\
row = {
    "code base": "C++ fixture (workshops/legacy-refactor/fixtures/cpp)",
    "base image": "%s @ %s" % (CPP_IMAGE, digest.split("@")[-1]),
    "compiler": [l.strip() for l in vers.splitlines() if l.strip().startswith("g++")][0],
    "build system": "g++ direct, no CMake (fixture is two files)",
    "flags": "-std=c++03 -Werror=deprecated-declarations",
    "call sites found": len(sites),
    "network needed after image exists": "no",
}
print("append this row after review:")
print()
for k, v in row.items():
    print("  %-34s %s" % (k + ":", v))
print()
print("C# environment, same form:")
print("  %-34s %s" % ("project:", "fo-dicom %s / FO-DICOM.Core" % SPECIMEN_TAG))
print("  %-34s %s" % ("sdk:", run(["dotnet", "--version"])[1].strip()))
print("  %-34s %.1f s" % ("rebuild time:", build_s))
print("  %-34s %s" % ("matrix:", MATRIX))"""),

md("""\
## What this notebook proved

- **Rung 1 exists for both languages.** C# builds on the host in about a
  second. C++ builds in a container with a 2016 compiler, pinned by digest.
- **The host has no C++ toolchain**, which is the normal case and the reason
  the skill exists.
- **The C++ text search under-reports**, and the gap is the macro-generated
  call sites, which exist in no file.
- **The environment is a recorded fact**: image digest, compiler version,
  flags, and build time.

Next: [`05_refactoring`](05_refactoring.ipynb) uses rung 1 to enumerate call
sites in C#. `01_precondition_checks` (planned) will ask which rungs a code
base already has.

Not proved here: that DCMTK builds in this container. That is task B1, and it
is about scale, not about the mechanism.
"""),
]

nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python"},
}

out = "workshops/legacy-refactor/notebooks/00_setup.ipynb"
nbf.write(nb, out)
print("wrote", out, "with", len(nb.cells), "cells (no outputs; execute next)")
