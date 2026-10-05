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

**Proves:** claim 1 of [../THESIS.md](../THESIS.md) — step 1 of the ladder must exist before anything else.
**Skill:** [`legacy-build-container`](../../../skills/legacy-build-container/SKILL.md)
**Needs:** git, Docker, and the .NET SDK. Network for the first run only.
**Run time:** 20 seconds warm, measured. The first run takes several minutes, because it pulls two images and restores packages.
**State:** EXECUTED

---

## In short

A team must change a large code base that it did not write. Before anybody
changes one line, somebody must answer one question: **does this code build?**

This notebook is a guided tour of that first step. It visits the evidence for
each claim. You can read it without a computer.

The work is not a build environment. The work is a **skill that builds one**.
A Dockerfile solves one toolchain one time. A skill reads a project it has
never seen, and writes the right Dockerfile for that project.

### What you will see

| | Station | What it answers |
| --- | --- | --- |
| 1 | A real run of the skill | Does the skill work on a project it has not seen? |
| 2 | The code | Which version do we change? |
| 3 | The tool needs | Which toolchain does the code ask for? |
| 4 | The build | Does the code compile, in a container? |
| 5 | The C++ case | What happens when the host has no compiler at all? |
| 6 | The network | Does the demonstration work with no network? |
| 7 | The record | What does the next team start from? |

### Two things to remember

**1. Start from a working environment.** An AI agent writes code quickly. It
cannot prove that the code is correct. A compiler can. So the compiler comes
first, and every later claim depends on it.

**2. Never refactor without a reason.** A refactor costs money and adds risk.
The reason does not have to be a new function. "Nobody understands this code"
is a reason. "There are no tests" is a reason. "The documentation is wrong" is
a reason. But write the reason down first. The five common reasons are in
[../THESIS.md](../THESIS.md).

Decisions behind this notebook: [ADR 002](../../../docs/decisions/002-workshop-container-environment.md).
"""),

md("""\
## The story

A hospital software team uses fo-dicom, an open-source DICOM library. The team
still calls the 1.x interface. That interface now lives in a separate package,
and it is not supported. The team must move to the current interface. One of
the calls that must move also holds a defect.

So the team must find every place that uses the old interface. A text search is
not good enough, because a text search finds names, not calls. The compiler
finds calls. Therefore the team needs a build.

Nobody on the team has built this code. The build files are nine years old.
This is the normal state of legacy code, and it is where the skill starts.

### What the skill looks like in use

You open a terminal in the project. You type one command. No code, and no
Dockerfile, is written by hand.

```text
~/fo-dicom $ claude
> /legacy-build-container

  reads FO-DICOM.Core.csproj      -> netstandard2.0, C# 8
  reads Tests/...csproj           -> net462 as well, so it says so, and leaves it out
  chooses mcr.microsoft.com/dotnet/sdk:8.0, pinned by digest
  builds FO-DICOM.Core in the container   -> 0 errors, 11 warnings
  vendors 22 packages, then proves the build needs no network
  writes build-container/Dockerfile and build-container/BUILD.md
  proposes one row for the skill's memory, and asks a human to merge it
```

Two details matter for a medical product. The image is pinned by **digest**, so
the build environment is a recorded fact and not "whatever was current that
day". And the source is **mounted**, never copied into the image, so patient
data and confidential code never enter an image layer. See
[ADR 003](../../../docs/decisions/003-ai-assistance-network-and-confidentiality.md).

### A note on tools

The skill runs ordinary shell commands: `git`, `docker`, and the project's own
build tool. It needs no MCP server and no special tool. An agent with a shell
runs the steps itself. A person with a terminal runs the same commands and gets
the same result. That is deliberate: a command you cannot run by hand is a
command you cannot check.
"""),

code("""\
import os, subprocess, shlex, re, time, shutil, json

ROOT = os.path.abspath(os.path.join(os.getcwd(), "..", "..", ".."))
EVIDENCE = os.path.join(ROOT, "workshops", "legacy-refactor", "evidence",
                        "legacy-build-container")
FIXTURE_CPP = os.path.abspath(os.path.join(os.getcwd(), "..", "fixtures", "cpp"))

# This notebook creates everything it needs under WORKSPACE. It assumes nothing
# about what is already there. WORKSPACE is gitignored, so it holds no evidence.
WORKSPACE = os.path.join(ROOT, "tmp", "workshop-workspace")
SPECIMEN = os.path.join(WORKSPACE, "fo-dicom")
SPECIMEN_TAG = "4.0.8"
PROJECT_REL = "FO-DICOM.Core/FO-DICOM.Core.csproj"
CPP_IMAGE = "gcc:4.9"
os.makedirs(WORKSPACE, exist_ok=True)

def run(cmd, cwd=None, timeout=1800, env=None):
    p = subprocess.run(cmd if isinstance(cmd, list) else shlex.split(cmd),
                       cwd=cwd, capture_output=True, text=True,
                       errors="replace", timeout=timeout, env=env)
    return p.returncode, (p.stdout or "") + (p.stderr or "")

print("repo root :", ROOT)
print("evidence  :", os.path.relpath(EVIDENCE, ROOT), "(committed)")
print("workspace :", os.path.relpath(WORKSPACE, ROOT), "(gitignored, built by this notebook)")
print()
for tool in ("git", "dotnet", "docker"):
    print("%-8s %s" % (tool, shutil.which(tool) or "NOT FOUND"))"""),

md("""\
## Station 1 — A real run, on a project the skill had not seen

This is the main piece of evidence, and it was not produced by this notebook.

One clone of fo-dicom 4.0.8. The skill installed into that clone. One Claude
Code session started in the clone root, with one prompt: `/legacy-build-container`.
Everything the session produced is kept.

The complete record is in
[`../evidence/legacy-build-container/`](../evidence/legacy-build-container/README.md):
every tool call, every word, the files that were written, and the limits of the
run.
"""),

code("""\
if not os.path.isdir(EVIDENCE):
    print("EVIDENCE MISSING at", EVIDENCE)
else:
    with open(os.path.join(EVIDENCE, "session.jsonl"), encoding="utf-8") as fh:
        events = [json.loads(l) for l in fh if l.strip()]

    calls = [c["name"] for e in events if e.get("type") == "assistant"
             for c in e["message"].get("content", []) if c["type"] == "tool_use"]
    result = [e for e in events if e.get("type") == "result"][0]

    print("the session, as recorded")
    print("   tool calls :", len(calls))
    print("   turns      :", result["num_turns"])
    print("   wall clock : %.0f s" % (result["duration_ms"] / 1000))
    print("   cost       : USD %.2f" % result["total_cost_usd"])
    print()
    print("what it wrote, and what each file is for:")
    for name in sorted(os.listdir(EVIDENCE)):
        size = os.path.getsize(os.path.join(EVIDENCE, name))
        print("   %-24s %7d bytes" % (name, size))"""),

code("""\
# The measured result, quoted from the file the session wrote. Not re-typed.
with open(os.path.join(EVIDENCE, "BUILD.md"), encoding="utf-8") as fh:
    build_md = fh.read()

block = build_md.split("```text", 1)[1].split("```", 1)[0]
print(block.strip())"""),

md("""\
### Read that result twice

The first reading is the obvious one: the code builds, in a container, with no
network.

The second reading is the one that matters. **Every line of that block is a
measurement, and every measurement has a file behind it.** The digest, the
build matrix of one entry, the count of warnings, the negative control. Under
IEC 62304 this block is not a status report. It is the record of a controlled
build environment, and an auditor can repeat it.

The session also stopped at the right place. It proposed one row for the
skill's memory, and it asked a human to merge the row. It did not write the
row itself. An artifact that edits its own evidence has no change control.
"""),

code("""\
# What the session chose, in the file it wrote. The digest is the whole point.
with open(os.path.join(EVIDENCE, "Dockerfile"), encoding="utf-8") as fh:
    for line in fh:
        if line.startswith("FROM") or line.startswith("ENV NUGET"):
            print(line.rstrip())"""),

md("""\
## Station 2 — Get the code first

The order is not a detail. You cannot decide which compiler you need before
you can read the build files. So the code comes first, and every later answer
is read out of it.

The clone is pinned to a tag. A branch moves, and a moving specimen cannot be
cited.
"""),

code("""\
if not os.path.isdir(SPECIMEN):
    print("cloning fo-dicom at tag %s ..." % SPECIMEN_TAG)
    rc, out = run(["git", "clone", "--quiet", "--depth", "1", "--branch",
                   SPECIMEN_TAG,
                   "https://github.com/fo-dicom/fo-dicom.git", "fo-dicom"],
                  cwd=WORKSPACE)
    print("clone exit:", rc)
else:
    print("specimen already present, not re-cloned")

PROJECT = os.path.join(SPECIMEN, *PROJECT_REL.split("/"))
print("tag        :", run(["git", "describe", "--tags", "--always"], cwd=SPECIMEN)[1].strip())
print("last commit:", run(["git", "log", "-1", "--date=short", "--format=%ad %h"], cwd=SPECIMEN)[1].strip())
print("project    :", PROJECT_REL, "exists" if os.path.isfile(PROJECT) else "MISSING")"""),

md("""\
## Station 3 — Ask the build files, not the documentation

The documentation describes an intention. The build files describe the build.
Read the build files.
"""),

code("""\
tfms = set()
for base, dirs, names in os.walk(SPECIMEN):
    dirs[:] = [d for d in dirs if d not in (".git", "obj", "bin", "build-container")]
    for n in names:
        if n.endswith(".csproj"):
            with open(os.path.join(base, n), encoding="utf-8", errors="replace") as fh:
                for m in re.finditer(r"<TargetFrameworks?>([^<]+)<", fh.read()):
                    tfms.update(t.strip() for t in m.group(1).split(";"))

print("target frameworks declared across the clone:")
for t in sorted(tfms):
    print("   ", t)

with open(PROJECT, encoding="utf-8") as fh:
    core = fh.read()
print()
print("the project we build:")
for tag in ("TargetFramework", "LangVersion"):
    m = re.search(r"<%s>([^<]+)<" % tag, core)
    print("   %-16s %s" % (tag + ":", m.group(1) if m else "not set"))"""),

md("""\
`netstandard1.3` and `net462` date this code to about 2017. That is evidence
for the word "legacy", not an opinion about the style of the code.

`FO-DICOM.Core` targets `netstandard2.0` and asks for C# 8. A current SDK
compiles both. So the skill chose the **newest** SDK that builds the target,
and not an old one. An old image costs time and buys nothing here.

The other frameworks are a different matter. `net462` needs the .NET Framework
reference assemblies, and the WinForms tools and the C++/CLI projects need
Windows. They stay out of the build matrix, and the record says so. **Any claim
of complete recall is limited to the entries in the matrix.** That is the
reason to write the matrix down.
"""),

md("""\
## Station 4 — The build. A smoke test on the host, then the container.

Do not install an old toolchain on your laptop. A legacy project needs an old
compiler, and an old compiler on a working laptop is a cost that never ends.
The container holds the toolchain instead.

The host build below is a **smoke test** only. It takes about one second, and
it tells you whether the clone is intact before you spend minutes on an image.
It is not the build you ship, and it is not the build you cite. It works here
only because this project happens to accept a current SDK.
"""),

code("""\
# Build matrix. One entry on purpose: this workshop proves the method, not the
# full configuration space. Every claim of complete recall is limited to the
# entries listed here. Adding a second entry costs one line.
# See ADR 002, decision 7.
MATRIX = ["FO-DICOM.Core/netstandard2.0"]
# MATRIX += ["DICOM/net462", "DICOM/netstandard1.3"]   # the rest of the clone

t0 = time.time()
rc_host, out = run(["dotnet", "build", PROJECT, "-v", "q", "--nologo", "-t:Rebuild"])
host_build_s = time.time() - t0

errors = len(re.findall(r": error ", out))
warnings = len(set(re.findall(r": warning (CS\\d+)", out)))

print("SMOKE TEST, on the host. Not the shipped build.")
print("   build matrix     :", MATRIX)
print("   exit code        :", rc_host)
print("   errors           :", errors)
print("   distinct warnings:", warnings)
print("   build time       : %.1f s" % host_build_s)
print()
print("The clone is intact." if rc_host == 0 else "The clone does not build - fix this first.")"""),

md("""\
Now the real build: the `Dockerfile` that the session wrote, used as written.

This is a check of the evidence, not a new result. The same image, the same
project, the same build matrix. If the committed Dockerfile has drifted from
the record, this cell fails, and the failure is visible.

**One step of cleaning first, and it is not housekeeping.** The smoke test above
used the host SDK, and it left generated files in `FO-DICOM.Core/obj/`. The
container build writes its own generated files to a different folder. The
project then compiles both copies and stops with about 20 errors like this:

```text
error CS0579: Duplicate 'System.Reflection.AssemblyCompanyAttribute' attribute
```

The cause is not the container. The cause is two toolchains in one working
tree. This is the reason the `Dockerfile` redirects the package cache, and the
reason `BUILD.md` redirects the build output. A build you cannot repeat from a
clean tree is not evidence, so the cell cleans the tree first.
"""),

code("""\
# Remove what the host SDK generated. See the note above: two toolchains must
# not share one obj/ folder.
for sub in (("FO-DICOM.Core", "obj"), ("FO-DICOM.Core", "bin"),
            ("build-container", "obj"), ("build-container", "bin")):
    shutil.rmtree(os.path.join(SPECIMEN, *sub), ignore_errors=True)
print("cleaned the generated folders of both toolchains")
print()

img = "fo-dicom-build"
rc_img, out_img = run(["docker", "build", "-q", "-t", img, EVIDENCE])
print("docker build :", "ok" if rc_img == 0 else "FAILED")
print("image id     :", out_img.strip()[:19])

src = SPECIMEN.replace(os.sep, "/")
t0 = time.time()
rc_b, out_b = run(["docker", "run", "--rm", "-v", src + ":/work", "-w", "/work", img,
                   "dotnet", "build", PROJECT_REL, "-c", "Release", "-v", "q", "--nologo",
                   "-p:BaseIntermediateOutputPath=/work/build-container/obj/core/",
                   "-p:BaseOutputPath=/work/build-container/bin/core/"])
container_s = time.time() - t0

c_errors = len(re.findall(r": error ", out_b))
c_warnings = sorted(set(re.findall(r": warning (CS\\d+)", out_b)))
dll = os.path.join(SPECIMEN, "build-container", "bin", "core", "Release",
                   "netstandard2.0", "fo-dicom.core.dll")

print()
print("CONTAINER BUILD, the one that counts")
print("   exit code     :", rc_b)
print("   errors        :", c_errors)
print("   warning codes :", " ".join(c_warnings))
print("   build time    : %.1f s  (host smoke test: %.1f s)" % (container_s, host_build_s))
print("   produced      :", os.path.basename(dll),
      "%d bytes" % os.path.getsize(dll) if os.path.isfile(dll) else "MISSING")
print()
print("Oracle step 1 exists for C#, in a container." if rc_b == 0
      else "CONTAINER BUILD FAILED - the evidence does not reproduce.")"""),

md("""\
### Check it yourself: an interactive terminal in the container

A notebook cell proves that the build works. A **terminal** proves that you can
work in it. Those are two different claims, and the second one is the claim an
engineer in the room will want.

This is Rule 3 of the skill: whoever starts the compiler must run where the
compiler lives. So open a shell inside the container, and keep the source on
the host disk.

#### Start the terminal

The next cell prints this command with the path of your own clone already in
it. Copy that line.

```bash
docker run --rm -it -v "<clone>:/work" -w /work fo-dicom-build bash
```

| Part | Why it is there |
| --- | --- |
| `-it` | keeps a terminal open, instead of running one command and leaving |
| `--rm` | deletes the container when you exit. The image stays, so nothing collects. |
| `-v "<clone>:/work"` | **mounts** the source. The code never enters an image layer. That is what makes a confidential code base safe here. See [ADR 003](../../../docs/decisions/003-ai-assistance-network-and-confidentiality.md). |
| `-w /work` | starts you in the project root, so the paths below stay short |
| `--network none` | optional. Add it for the air-gapped check further down. |

**On Windows in Git Bash, write `MSYS_NO_PATHCONV=1` in front of the command.**
Git Bash otherwise rewrites `-w /work` into a Windows path, and `docker run`
stops with `the working directory 'C:/Program Files/Git/work' is invalid`. In
PowerShell the command needs no prefix.

#### What to type, and what you must see

Measured in this container on 2026-10-05. Your times will differ. Nothing else
should.

```console
root@container:/work# dotnet --version
8.0.425

root@container:/work# git describe --tags --always
4.0.8

root@container:/work# rm -rf FO-DICOM.Core/obj FO-DICOM.Core/bin \
                             build-container/obj build-container/bin

root@container:/work# dotnet restore FO-DICOM.Core/FO-DICOM.Core.csproj \
    -p:BaseIntermediateOutputPath=/work/build-container/obj/core/
  Restored /work/FO-DICOM.Core/FO-DICOM.Core.csproj (in 1.48 sec).

root@container:/work# dotnet build FO-DICOM.Core/FO-DICOM.Core.csproj \
    -c Release --no-restore --nologo \
    -p:BaseIntermediateOutputPath=/work/build-container/obj/core/ \
    -p:BaseOutputPath=/work/build-container/bin/core/
    11 Warning(s)
    0 Error(s)
Time Elapsed 00:00:06.74

root@container:/work# ls -l build-container/bin/core/Release/netstandard2.0/fo-dicom.core.dll
-rw-r--r-- 1 root root 1540096 Oct  5 10:49 .../fo-dicom.core.dll

root@container:/work# exit
```

Three numbers are the whole check: **0 errors**, **11 warnings**, and
**1540096 bytes**. They are the same three numbers as station 1 and station 4.
If all three match, then the environment in your hands is the environment in
the record.

**Do not skip the `rm -rf`.** Without it the build stops with about 20
`error CS0579` lines, for the reason in the note above station 4: the host SDK
and the container SDK each generated an `AssemblyInfo.cs`, and the project
compiles both.

#### The air-gapped variant

Add `--network none` to the `docker run` command. The daemon then gives the
container no network at all. Check that first, so that you know the test is
real.

```console
root@container:/work# getent hosts api.nuget.org
                                      # prints nothing: there is no network

root@container:/work# dotnet restore FO-DICOM.Core/FO-DICOM.Core.csproj \
    --configfile /work/nuget.offline.config \
    -p:BaseIntermediateOutputPath=/work/build-container/obj/core/
  warning NU1603: System.Threading.Tasks.Extensions 4.5.4 depends on
  System.Runtime.CompilerServices.Unsafe (>= 4.5.3) but ... 4.7.1 was resolved.
  Restored /work/FO-DICOM.Core/FO-DICOM.Core.csproj (in 5.04 sec).

root@container:/work# dotnet build ... --no-restore         # the same flags
    21 Warning(s)
    0 Error(s)
```

**Read that carefully, because it is not a clean pass.** The build is green
with no network, and that is the claim. But the warning count moved from 11 to
21, and `NU1603` says that one package was resolved by an approximate match.

The cause is worth a minute in the room. Station 6 builds `offline-feed/` from
the packages that the **host** SDK 10.0.400 resolved. SDK 8.0 in the container
resolves a slightly different set. One package that it wants is not in the
feed, so NuGet takes the nearest version that is.

A vendored feed is therefore evidence **for the SDK that vendored it**, and for
no other SDK. The feed that matches this container is the one that the station
1 session vendored for itself: 22 packages in `build-container/nuget-feed/`,
and that folder is not in this clone. See
[`BUILD.md`](../evidence/legacy-build-container/BUILD.md), section *Reproducing
the vendored feed*.
"""),

code("""\
# The command to paste into a terminal, with this machine's path filled in.
# This cell starts nothing. It only prints.
host_path = SPECIMEN.replace(os.sep, "/")
cmd = 'docker run --rm -it -v "%s:/work" -w /work %s bash' % (host_path, img)

print("Git Bash on Windows:")
print("   MSYS_NO_PATHCONV=1 " + cmd)
print()
print("PowerShell, or a Linux or macOS shell:")
print("   " + cmd)
print()
print("air-gapped variant: add --network none directly after 'run'")
print()
print("image on this machine :", "yes" if rc_img == 0 else "NO - run the cell above first")
print("clone on this machine :", "yes" if os.path.isfile(PROJECT) else "NO")"""),

md("""\
## Station 5 — The case that C# cannot show

The C# half of this workshop is the easy half. The host happens to have a
usable SDK. Most legacy C++ does not give you that.

Two things are different in C++, and both of them matter.
"""),

code("""\
print("g++ on the host   :", shutil.which("g++") or "NOT FOUND")
print("cmake on the host :", shutil.which("cmake") or "NOT FOUND")
print()
print("This is the ordinary state of a developer laptop, and it is the reason")
print("the skill exists. With no compiler there is no oracle step 1. An agent")
print("then cannot prove that a change is complete. It can only guess.")"""),

md("""\
### The container, pinned by digest

`gcc:4.9` carries a 2016 compiler. The image is used instead of an old
distribution plus `apt-get`, which avoids a trap that the skill records: old
distributions moved their package servers, so `apt-get update` returns 404 on
images such as `ubuntu:14.04`. An image that already holds the compiler needs
no package server at all.
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
### The second difference: a text search misses calls that no file contains

In C#, a text search fails because it reports too much. See `05_refactoring`:
62 matches, and 6 real call sites.

In C++ it fails the other way, and that way is worse. A macro writes the call.
The name of the function that is called appears in **no source file**.

The fixture in [`../fixtures/cpp/`](../fixtures/cpp/) is small on purpose. It
reproduces the mechanism. It is not a large code base: DCMTK and VTK show the
same thing at a size nobody can read in a workshop.

Three paths reach the deprecated function:

1. a direct call,
2. three accessors that a macro writes, so their names exist in no file,
3. a template body, which the compiler checks only where it is instantiated.
"""),

code("""\
mount = FIXTURE_CPP.replace(os.sep, "/")

with open(os.path.join(FIXTURE_CPP, "main.cpp"), encoding="utf-8") as fh:
    main_src = fh.readlines()
with open(os.path.join(FIXTURE_CPP, "legacy_api.h"), encoding="utf-8") as fh:
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

| Method | Lines returned | Call sites it can show you |
| --- | --- | --- |
| Text search for `setLegacy` | 5 | **1.** The other four are a declaration, a definition, a macro body and a template body. |
| Compiler, `-Werror=deprecated-declarations` | 5 diagnostics | **5.** The direct call, three macro expansions, and the template instantiation. |

Both totals are 5, and they mean different things. That is the trap in one
line. A text search returns *lines that contain a name*. A compiler returns
*uses of a function*. Counting the first and reporting it as the second is the
mistake that this workshop is about.

The three call sites that a macro writes are the ones that matter. `SetWidth`,
`SetHeight` and `SetDepth` appear in no source file. The preprocessor writes
them. No text search can list them, and more care does not help. The compiler
lists them, and it names the line where the macro is used.

The limits are visible here as well. The compiler checks the template body only
because `main.cpp` instantiates it. Remove that one line, and the compiler goes
quiet while the code is still there.
"""),

md("""\
## Station 6 — Prove that the demonstration needs no network

Both events are in person. A guest network may not exist, or it may block
outbound HTTPS. The demonstration must not need one.

`dotnet build --no-restore` is not a proof on its own. It skips the restore
step, and it still depends on packages that already sit in the global cache. A
warm cache is not an artifact that you can carry in a bag.

The proof uses a **local feed with the source list cleared**. `<clear />`
removes nuget.org. If the restore still succeeds, then nothing remote was
needed. That is a statement about the configuration, and not about whatever the
network happened to be doing at the time.

Build the feed once on a machine that has restored online. Then carry the
folder.
"""),

code("""\
feed = os.path.join(SPECIMEN, "offline-feed")
os.makedirs(feed, exist_ok=True)
cache = os.path.expanduser("~/.nuget/packages")

# Do not assume a previous run left this file here. Restore if it is missing.
assets_path = os.path.join(SPECIMEN, "FO-DICOM.Core", "obj", "project.assets.json")
if not os.path.isfile(assets_path):
    print("no restore graph yet, restoring once ...")
    print("   exit:", run(["dotnet", "restore", PROJECT])[0])

with open(assets_path, encoding="utf-8-sig") as fh:
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
print("wrote             :", os.path.basename(offline_cfg))"""),

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
rc_ob, out_ob = run(["dotnet", "build", PROJECT, "-v", "q", "--nologo",
                     "--no-restore"], cwd=SPECIMEN, env=env)
offline_build_s = time.time() - t0
print()
print("B. build --no-restore against that cold folder")
print("   exit code  :", rc_ob)
print("   errors     :", len(re.findall(r": error ", out_ob)))
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
print("one package. With the local feed it finds every one of them.")"""),

md("""\
The session in station 1 did the same proof inside the container, with
`--network none` on the `docker run` command. That is stronger, because the
daemon enforces it rather than the configuration. Both proofs are in
[`BUILD.md`](../evidence/legacy-build-container/BUILD.md).
"""),

md("""\
## Station 7 — Record the environment, so that the next attempt is faster

A skill that does not learn is a template. The value of this skill is its
memory:
[`verified-environments.md`](../../../skills/legacy-build-container/reference/verified-environments.md).

A green build adds one row. A failure that cost more than 15 minutes adds one
line to the traps table. A human merges both, through a pull request.

The notebook prints the row. It does not write the file. An artifact that edits
its own evidence has no change control, and in a regulated process that is a
defect rather than a feature.
"""),

code("""\
row = {
    "code base": "C++ fixture (workshops/legacy-refactor/fixtures/cpp)",
    "base image": "%s @ %s" % (CPP_IMAGE, digest.split("@")[-1]),
    "compiler": [l.strip() for l in vers.splitlines() if l.strip().startswith("g++")][0],
    "build system": "g++ called directly, no CMake (the fixture is two files)",
    "flags": "-std=c++03 -Werror=deprecated-declarations",
    "call sites found": len(sites),
    "network needed after the image exists": "no",
}
print("C++ fixture, the row this notebook proposes:")
for k, v in row.items():
    print("   %-38s %s" % (k + ":", v))

print()
print("C# in a container, already merged from the station 1 run:")
print("   %-38s %s" % ("project:", "fo-dicom %s / %s" % (SPECIMEN_TAG, PROJECT_REL)))
print("   %-38s %s" % ("container build:", "exit %d, %.1f s" % (rc_b, container_s)))
print("   %-38s %s" % ("host smoke test:", "exit %d, %.1f s" % (rc_host, host_build_s)))
print("   %-38s %s" % ("matrix:", MATRIX))

mem = os.path.join(ROOT, "skills", "legacy-build-container", "reference",
                   "verified-environments.md")
with open(mem, encoding="utf-8") as fh:
    rows = [l.strip("# ").strip() for l in fh if l.startswith("### ")
            and not l.startswith("### <")]
print()
print("rows in the skill's memory today:")
for r in rows:
    print("   ", r)"""),

md("""\
## What this notebook proved

- **The skill works from a cold start.** One session, started in a clone it had
  never seen, read the build files, chose an image, built the code in a
  container, proved the offline claim, and wrote the instructions. The record
  is [`../evidence/legacy-build-container/`](../evidence/legacy-build-container/README.md).
- **Oracle step 1 exists for both languages.** C# builds in a container with
  the SDK pinned by digest. C++ builds in a container with a 2016 compiler,
  also pinned by digest.
- **The host has no C++ toolchain.** That is the normal state, and it is the
  reason the skill exists.
- **A C++ text search misses calls.** The gap is the call sites that a macro
  writes, and they exist in no file.
- **The environment is a recorded fact**: digest, compiler version, flags,
  build matrix, and build time.

## What it did not prove

- **Not a hard case.** fo-dicom accepts a current SDK. The skill exists for the
  case where nothing current works, and that case is shown here only on a small
  C++ fixture. DCMTK at scale is task B1, and it is about size, not about the
  mechanism.
- **Not the "cannot decide" path.** The skill reports what is missing when a
  repository holds no evidence. No run has exercised that report.

## The two things to remember, again

1. **Start from a working environment.** Everything later depends on it.
2. **Never refactor without a reason.** Write the reason down first. Better
   documentation, better understanding and a first test set are valid reasons,
   and they are results of this method rather than costs of it.

Next: [`05_refactoring`](05_refactoring.ipynb) uses oracle step 1 to list every
call site in C#. `01_precondition_checks` (planned) asks which steps of the
ladder a code base already has.
"""),
]

nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python"},
}

out = "workshops/legacy-refactor/notebooks/00_setup.ipynb"
nbf.write(nb, out)
print("wrote", out, "with", len(nb.cells), "cells (no outputs; execute next)")
