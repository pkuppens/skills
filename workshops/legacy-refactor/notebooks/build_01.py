"""Author 01_build_warnings.ipynb. Run from the repo root, then execute the notebook.

Writes cells only. Outputs come from a real kernel run. See notebooks/README.md.
"""
import nbformat as nbf

nb = nbf.v4.new_notebook()
md = lambda t: nbf.v4.new_markdown_cell(t)
code = lambda t: nbf.v4.new_code_cell(t)

nb.cells = [
md("""\
# 01 — The build is green, and it is not clean

**Proves:** claims 1 and 2 of [../CLAIMS.md](../CLAIMS.md) — the slow part is proof, and the compiler is what provides it.
**Skill:** [`call-site-exhaustiveness`](../../../skills/call-site-exhaustiveness/SKILL.md)
**Needs:** git and Docker. The image from [`00_setup`](00_setup.ipynb). Network for the first run only.
**Run time:** about 3 minutes warm, measured. Eight container builds.
**State:** EXECUTED

---

## In short

[`00_setup`](00_setup.ipynb) ended with a green build that printed **11
warnings**. That is the most common state of real legacy code: it compiles,
nobody is proud of it, and every team argues about the same question.

> Do we fix the warnings? Which ones? And how do we know we fixed all of them?

This notebook is the answer, on a real library, as a runbook you can repeat.

### What you will see

| | Station | What it answers |
| --- | --- | --- |
| 1 | The eleven | What exactly is the compiler complaining about? |
| 2 | The triage | Which of these matter, and which are noise? |
| 3 | The branch | Where does the work go, so it can be reviewed? |
| 4 | The cheap one | Fix the warning that cannot break anything. |
| 5 | The obsolete API | Let the compiler find every call site, then watch three fix attempts fail. |
| 6 | The stop | Two warnings change behaviour. We stop, and say why. |
| 7 | The ratchet | How to stop the eleven from becoming twelve. |

### One thing to remember

**A warning is a question, not a defect.** Eleven warnings are eleven
questions, and they do not have the same answer. Two of these eleven hide a
real defect. One hides nothing. Three must stay exactly as they are, and this
notebook shows the compiler proving it.
"""),

code("""\
import os, subprocess, shlex, re, time, shutil, json

ROOT = os.path.abspath(os.path.join(os.getcwd(), "..", "..", ".."))
EVIDENCE = os.path.join(ROOT, "workshops", "legacy-refactor", "evidence",
                        "legacy-build-container")
WORKSPACE = os.path.join(ROOT, "tmp", "workshop-workspace")
SPECIMEN = os.path.join(WORKSPACE, "fo-dicom")
SPECIMEN_TAG = "4.0.8"
PROJECT_REL = "FO-DICOM.Core/FO-DICOM.Core.csproj"
BRANCH = "feature/fix-build-warnings"
IMAGE = "fo-dicom-build"
os.makedirs(WORKSPACE, exist_ok=True)

def run(cmd, cwd=None, timeout=1800):
    p = subprocess.run(cmd if isinstance(cmd, list) else shlex.split(cmd),
                       cwd=cwd, capture_output=True, text=True,
                       errors="replace", timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")

def git(*args):
    return run(["git"] + list(args), cwd=SPECIMEN)

# This notebook stands alone: it clones the specimen and builds the image if
# they are absent, exactly as 00_setup does. It assumes nothing in tmp/.
if not os.path.isdir(SPECIMEN):
    print("cloning fo-dicom at tag %s ..." % SPECIMEN_TAG)
    print("clone exit:", run(["git", "clone", "--quiet", "--depth", "1",
                              "--branch", SPECIMEN_TAG,
                              "https://github.com/fo-dicom/fo-dicom.git",
                              "fo-dicom"], cwd=WORKSPACE)[0])

rc, _ = run(["docker", "image", "inspect", IMAGE])
if rc != 0:
    print("building the image from the committed Dockerfile ...")
    print("build exit:", run(["docker", "build", "-q", "-t", IMAGE, EVIDENCE])[0])

# Start from the tag, every time. A previous run of this notebook leaves the
# clone on the feature branch with the fixes applied, and station 1 must show
# the state of the released code, not the state of the last run. Station 3
# recreates the branch from the tag, so nothing is lost by resetting here.
git("reset", "-q", "--hard")
git("checkout", "-q", "--detach", SPECIMEN_TAG)

print("specimen :", os.path.relpath(SPECIMEN, ROOT))
print("tag      :", git("describe", "--tags", "--always")[1].strip())
print("head     :", git("log", "-1", "--format=%h %s")[1].strip()[:60])
print("image    :", IMAGE, "present")"""),

code("""\
SRC = SPECIMEN.replace(os.sep, "/")
DIAG = re.compile(r"/work/(\\S+?)\\((\\d+),\\d+\\): (warning|error) (CS\\d+): (.*?)(?: \\[/work|$)")

def build(extra=(), label=""):
    \"\"\"Build FO-DICOM.Core in the container. Return the parsed diagnostics.

    Always cleans the generated folders of both toolchains first: a host build
    and a container build cannot share one obj/. See 00_setup, station 4.
    \"\"\"
    for sub in (("FO-DICOM.Core", "obj"), ("FO-DICOM.Core", "bin"),
                ("build-container", "obj"), ("build-container", "bin")):
        shutil.rmtree(os.path.join(SPECIMEN, *sub), ignore_errors=True)
    # NuGetAudit=false: with no network the package audit cannot reach
    # nuget.org and adds eleven NU1900 warnings that say nothing about this
    # code. Switching it off makes the warning list the compiler's own, and
    # makes the counts below identical with and without a network - which
    # matters, because this notebook has to run in a room with no guest wifi.
    cmd = ["docker", "run", "--rm", "-v", SRC + ":/work", "-w", "/work", IMAGE,
           "dotnet", "build", PROJECT_REL, "-c", "Release", "--nologo",
           "-p:NuGetAudit=false",
           "-p:BaseIntermediateOutputPath=/work/build-container/obj/core/",
           "-p:BaseOutputPath=/work/build-container/bin/core/"] + list(extra)
    t0 = time.time()
    rc, out = run(cmd)
    diags = []
    for path, line, kind, codex, msg in set(DIAG.findall(out)):
        diags.append({"file": path.split("/")[-1], "path": path,
                      "line": int(line), "kind": kind, "code": codex,
                      "msg": msg.strip()})
    diags.sort(key=lambda d: (d["code"], d["file"], d["line"]))
    res = {"rc": rc, "seconds": time.time() - t0, "diags": diags,
           "warnings": [d for d in diags if d["kind"] == "warning"],
           "errors": [d for d in diags if d["kind"] == "error"]}
    if label:
        print("%-34s exit %d | %d errors | %d warnings | %.1f s"
              % (label, rc, len(res["errors"]), len(res["warnings"]), res["seconds"]))
    return res

def show(diags, indent="   "):
    for d in diags:
        print("%s%-7s %-24s %-5d %s" % (indent, d["code"], d["file"], d["line"],
                                        d["msg"][:72]))

base = build(label="the build, at tag %s" % SPECIMEN_TAG)
print()
print("This is where 00_setup stopped: green, and not clean.")"""),

md("""\
## Station 1 — What are the eleven?

Eleven lines of build output are not eleven problems. The first act of
engineering is to group them, because the group decides the decision.
"""),

code("""\
from collections import Counter

by_code = Counter(d["code"] for d in base["warnings"])
print("warnings by code:")
for codex, n in sorted(by_code.items()):
    msgs = sorted({d["msg"] for d in base["warnings"] if d["code"] == codex})
    note = "" if len(msgs) == 1 else "   (%d different members)" % len(msgs)
    print("   %-7s x%-3d %s%s" % (codex, n, msgs[0][:58], note))
print()
print("all eleven, with file and line:")
show(base["warnings"])"""),

md("""\
## Station 2 — The triage

Four groups. The difference between them is not the warning code. It is
**what happens to the behaviour of the library if you fix it**.

| | Group | Warnings | What it really is |
| --- | --- | --- | --- |
| A | Obsolete API | 6 × `CS0618` on `AsyncManualResetEvent`, 1 on `DicomQueryRetrieveLevel.Worklist` | A **refactor**. Behaviour must not change. |
| B | Missing `GetHashCode` | `CS0659` + `CS0661` in `DicomStatus` | A **defect**. Two equal statuses both survive in a `HashSet`. |
| C | Sign-extended operand | `CS0675` in `DicomTag.GetHashCode` | A **hazard**. Today's values stay in range, so nothing is broken yet. |
| D | Malformed pragma | `CS1696` in `DicomService` | **Nothing.** A comment that is not a comment. |

Read the source of B, C and D. Three screens, and the decision is obvious once
you have seen them.
"""),

code("""\
def find_line(rel, needle):
    \"\"\"Line number of the first line containing needle. Fails loudly if absent.\"\"\"
    with open(os.path.join(SPECIMEN, *rel.split("/")), encoding="utf-8-sig") as fh:
        for n, line in enumerate(fh, 1):
            if needle in line:
                return n
    raise AssertionError("%s: %r not found" % (rel, needle))

def quote(rel, first, last, title):
    with open(os.path.join(SPECIMEN, *rel.split("/")), encoding="utf-8-sig") as fh:
        lines = fh.readlines()
    print("--- %s  (%s:%d-%d)" % (title, rel.split("/")[-1], first, last))
    for n in range(first, last + 1):
        print("%5d | %s" % (n, lines[n - 1].rstrip()))
    print()

quote("FO-DICOM.Core/Network/DicomStatus.cs", 149, 157, "B: operator == compares by Code, with a mask")
quote("FO-DICOM.Core/Network/DicomStatus.cs", 184, 187, "B: Equals delegates to it - and there is no GetHashCode")
quote("FO-DICOM.Core/DicomTag.cs", 166, 175, "C: the hash, with the sign-extended operand")
d_line = find_line("FO-DICOM.Core/Network/DicomService.cs", "#pragma warning disable 4014")
quote("FO-DICOM.Core/Network/DicomService.cs", d_line - 2, d_line + 2,
      "D: the prose after the pragma number")"""),

md("""\
### The decision, with a reason for each

This is the table that matters. Note that it is a **choice**, not a default: a
team with a release next Friday would decide group C differently, and would be
right.

| Group | Decision for this session | Reason |
| --- | --- | --- |
| **D** | Fix now. | One line. It cannot change behaviour. Start with the free one. |
| **A** | Fix now, with the compiler proving completeness. | An obsolete API is debt with a deadline. The compiler can list every use, so the work is bounded and checkable. |
| **B** | **Not in this notebook.** Fix under test, in `02_test_driven_development`. | It is a defect. The fix changes a hash value, which is observable. A fix with no failing test first is a guess. |
| **C** | **Not in this notebook.** Fix under test, in `02_test_driven_development`. | Nothing is broken today, so the test must prove that nothing changes. That needs the boundary values, and those need a test runner. |

Groups B and C both change what the code *does*. That is the line this notebook
will not cross, and station 6 explains why it cannot cross it yet.
"""),

md("""\
## Station 3 — The branch, before the first edit

The clone sits on a detached tag. Work in that state cannot be reviewed,
cherry-picked, or sent upstream.

So: one branch, from the tag, and **one commit per group**. The commit history
then *is* the triage, and a reviewer can read the decisions without reading the
diff.
"""),

code("""\
# -B resets the branch to the tag, so re-running this notebook gives the same
# result rather than stacking commits on the previous run.
print(git("checkout", "-q", "-B", BRANCH, SPECIMEN_TAG)[1].strip() or "branch ready")
print("branch :", git("rev-parse", "--abbrev-ref", "HEAD")[1].strip())
print("base   :", git("describe", "--tags", "--always")[1].strip())

def commit(message, *paths):
    git("add", *paths)
    rc, out = git("commit", "-q", "-m", message)
    sha = git("rev-parse", "--short", "HEAD")[1].strip()
    print("   commit %s  %s" % (sha, message))
    return sha

def edit(rel, pairs):
    \"\"\"Apply exact replacements. Assert the count, so a silent miss is loud.\"\"\"
    path = os.path.join(SPECIMEN, *rel.split("/"))
    with open(path, encoding="utf-8-sig") as fh:
        s = fh.read()
    for old, new, expected in pairs:
        found = s.count(old)
        assert found == expected, "%s: expected %d of %r, found %d" % (
            rel, expected, old[:48], found)
        s = s.replace(old, new)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(s)
    return rel

# Untracked files from 00_setup's offline work live in this clone. They are not
# ours to commit, so the status check below ignores untracked files and proves
# that nothing tracked moved.
print()
print("tracked changes before any edit:",
      git("status", "--short", "--untracked-files=no")[1].strip() or "none")"""),

md("""\
## Station 4 — Group D: the free one

`#pragma warning disable 4014 This call should not be awaited because ...`

The prose after the warning number is not a comment, and the compiler says so.
The fix is to make it one. Zero risk, one line, and it removes 1 of the 11.

Always take the free one first. It shortens the list you have to think about.
"""),

code("""\
edit("FO-DICOM.Core/Network/DicomService.cs", [(
    "#pragma warning disable 4014 This call should not be awaited because it can only complete when the pending queue is empty\\n",
    "                        // This call must not be awaited: it completes only when the\\n"
    "                        // pending queue is empty.\\n"
    "#pragma warning disable 4014\\n",
    1)])

after_d = build(label="after group D")
print()
print("warnings: %d -> %d" % (len(base["warnings"]), len(after_d["warnings"])))
assert not any(d["code"] == "CS1696" for d in after_d["warnings"])
commit("fix: CS1696, the prose after the pragma number is not a comment",
       "FO-DICOM.Core/Network/DicomService.cs")"""),

md("""\
## Station 5 — Group A: the obsolete API

Seven warnings, two different obsolete members. This is the group where the
method of this whole workshop earns its keep.

### First, make the compiler produce the list

Do not search for the name. Promote the warning to an error and let the build
stop at every use. The list is then complete **because of the method**, not
because somebody was careful. That is
[`call-site-exhaustiveness`](../../../skills/call-site-exhaustiveness/SKILL.md),
and [`01a_find_obsolete_call_sites`](01a_find_obsolete_call_sites.ipynb) measures it against a text search
on this exact target: 62 text matches, 8 in files that are built, 6 real call
sites.
"""),

code("""\
enumerated = build(extra=["-warnaserror:CS0618"], label="-warnaserror:CS0618")
print()
print("every use of an obsolete member, listed by the compiler:")
show(enumerated["errors"])
print()
print("Two members, not one:")
for member in ("AsyncManualResetEvent", "Worklist"):
    n = sum(1 for d in enumerated["errors"] if member in d["msg"])
    print("   %-24s %d call sites" % (member, n))"""),

md("""\
### Then read the deprecation message properly

```csharp
[Obsolete("Use the AsyncEx library instead")] // Or Dicom.Network.Client.Tasks.AsyncManualResetEvent
                                              // if you're a Fellow Oak DICOM contributor
public sealed class AsyncManualResetEvent : AsyncManualResetEvent<object>
```

The message says to take a dependency on a third-party library. The comment
beside it names a replacement **already in this repository** — and we are the
contributor. So the fix needs no new package, no network, and no offline-feed
work.

`FellowOakDicom.Network.Client.Tasks.AsyncManualResetEvent` has the same shape:
`ctor(bool)`, `WaitAsync()`, `Set()`, `Reset()`. Every one of the six sites uses
only those.

**Two classes with the same name, one obsolete and one not.** This is the trap
that `01a_find_obsolete_call_sites` records from the other direction: a text search cannot
tell them apart, and the compiler can.

### Attempt 1 — a `using` alias at the top of the file

The obvious move. It is also wrong, and the interesting part is *how* it is
wrong.
"""),

code("""\
ALIAS = "using AsyncManualResetEvent = FellowOakDicom.Network.Client.Tasks.AsyncManualResetEvent;\\n"
A_FILES = ["FO-DICOM.Core/Network/DicomServer.cs", "FO-DICOM.Core/Network/DicomService.cs"]

for rel in A_FILES:
    edit(rel, [("using System.Threading.Tasks;\\n",
                "using System.Threading.Tasks;\\n" + ALIAS, 1)])
print("alias added above the namespace in both files")

attempt1 = build(label="attempt 1: alias at file scope")
cs0618 = [d for d in attempt1["warnings"] if d["code"] == "CS0618"]
print()
print("CS0618 before : %d" % sum(1 for d in base["warnings"] if d["code"] == "CS0618"))
print("CS0618 after  : %d   <- unchanged" % len(cs0618))
print()
print("The edit changed the files. It did not change the result. A text search")
print("would have reported this fix as done.")"""),

md("""\
**Why it does nothing.** C# resolves a simple name by walking out from the
innermost namespace. Inside `namespace FellowOakDicom.Network`, a type that is
a *member of that namespace* is found before a using-alias declared at file
scope, which sits further out. The obsolete class is a member of that
namespace, so it keeps winning.

This is the notebook's smallest and best lesson: **the oracle also judges your
fix.** Without the warning count, attempt 1 ships.

### Attempt 2 — move the alias inside the namespace
"""),

code("""\
for rel in A_FILES:
    edit(rel, [("using System.Threading.Tasks;\\n" + ALIAS,
                "using System.Threading.Tasks;\\n", 1),
               ("namespace FellowOakDicom.Network\\n{\\n",
                "namespace FellowOakDicom.Network\\n{\\n    " + ALIAS, 1)])
print("alias moved inside the namespace in both files")

attempt2 = build(label="attempt 2: alias inside namespace")
print()
show(attempt2["errors"])
print()
print("Rejected, and precisely: an alias may not shadow a type declared in the")
print("same namespace. The language closes this door on purpose.")"""),

md("""\
### Attempt 3 — qualify the type at each site

No alias. Name the replacement at each of the six places the compiler listed.
More typing, and it is honest: the reader of the diff sees which type is used.
"""),

code("""\
for rel in A_FILES:
    edit(rel, [("namespace FellowOakDicom.Network\\n{\\n    " + ALIAS,
                "namespace FellowOakDicom.Network\\n{\\n", 1)])

edit("FO-DICOM.Core/Network/DicomServer.cs", [
    ("private readonly AsyncManualResetEvent _hasServicesFlag;",
     "private readonly Client.Tasks.AsyncManualResetEvent _hasServicesFlag;", 1),
    ("private readonly AsyncManualResetEvent _hasNonMaxServicesFlag;",
     "private readonly Client.Tasks.AsyncManualResetEvent _hasNonMaxServicesFlag;", 1),
    ("_hasServicesFlag = new AsyncManualResetEvent(false);",
     "_hasServicesFlag = new Client.Tasks.AsyncManualResetEvent(false);", 1),
    ("_hasNonMaxServicesFlag = new AsyncManualResetEvent(true);",
     "_hasNonMaxServicesFlag = new Client.Tasks.AsyncManualResetEvent(true);", 1)])

edit("FO-DICOM.Core/Network/DicomService.cs", [
    ("protected readonly AsyncManualResetEvent _isDisconnectedFlag;",
     "protected readonly Client.Tasks.AsyncManualResetEvent _isDisconnectedFlag;", 1),
    ("_isDisconnectedFlag = new AsyncManualResetEvent();",
     "_isDisconnectedFlag = new Client.Tasks.AsyncManualResetEvent();", 1)])
print("all 6 sites qualified")

attempt3 = build(label="attempt 3: qualified at each site")
print()
show(attempt3["errors"])
print()
print("4 of the 6 sites are fine. 2 are not, and the reason is the public API:")
print("the replacement is internal, and _isDisconnectedFlag is protected on a")
print("public class. CS0052 is the compiler refusing to leak an internal type.")"""),

md("""\
### Two side lessons from that output

**A red build hides warnings.** Count the warnings in attempt 3: fewer than
before, and nothing was fixed. With an error present the compiler never reaches
the stage that reports `CS0675`. So **triage warnings only on a green build**,
or the list you are working from is not the list.

**The complete list was not a uniform job.** The compiler gave six sites, and
it was right. Then it told us that two of the six are a different kind of
change. Completeness and uniformity are different properties, and only the
first one comes free.

### So group A splits into three decisions

| Sites | Where | Decision | Reason |
| --- | --- | --- | --- |
| 4 | `DicomServer`, private fields | **Swap.** | Internal to the class. The compiler verifies it. |
| 2 | `DicomService`, protected field | **Keep, and suppress with the reason.** | Swapping is `CS0052`. Removing the field from the public surface is a breaking change, so it belongs in a major version, not in a warning cleanup. |
| 1 | `DicomCFindRequest`, a `switch` case | **Keep, and suppress with the reason.** | `Worklist` is still a public enum value that callers can pass. Delete the case and those calls fall to `default:` and throw. That is a behaviour change. |

A suppression at the narrowest scope, with the reason written next to it, is a
decision. A global `NoWarn` is hiding. The difference is whether a reviewer can
disagree with you.
"""),

code("""\
# Revert the two sites that CS0052 rejected, and suppress them with the reason.
edit("FO-DICOM.Core/Network/DicomService.cs", [
    ("        protected readonly Client.Tasks.AsyncManualResetEvent _isDisconnectedFlag;",
     "        // CS0618 kept on purpose. The in-repo replacement\\n"
     "        // Client.Tasks.AsyncManualResetEvent is internal, and this field is protected\\n"
     "        // on a public class, so swapping it is CS0052. Removing the field from the\\n"
     "        // public surface is a breaking change and belongs in a major version.\\n"
     "#pragma warning disable 618\\n"
     "        protected readonly AsyncManualResetEvent _isDisconnectedFlag;\\n"
     "#pragma warning restore 618", 1),
    ("            _isDisconnectedFlag = new Client.Tasks.AsyncManualResetEvent();",
     "#pragma warning disable 618 // see the field declaration\\n"
     "            _isDisconnectedFlag = new AsyncManualResetEvent();\\n"
     "#pragma warning restore 618", 1)])

edit("FO-DICOM.Core/Network/DicomCFindRequest.cs", [
    ("                case DicomQueryRetrieveLevel.Worklist:",
     "                // CS0618 kept on purpose. Worklist is obsolete, but it is a public\\n"
     "                // enum value that callers can still pass. Removing this case sends\\n"
     "                // those calls to default: and throws, which is a behaviour change.\\n"
     "#pragma warning disable 618\\n"
     "                case DicomQueryRetrieveLevel.Worklist:\\n"
     "#pragma warning restore 618", 1)])

after_a = build(label="after group A")
print()
print("warnings: %d -> %d -> %d" % (len(base["warnings"]),
                                    len(after_d["warnings"]),
                                    len(after_a["warnings"])))
print()
show(after_a["warnings"])
assert after_a["rc"] == 0 and not any(d["code"] == "CS0618" for d in after_a["warnings"])
commit("refactor: CS0618, use the in-repo AsyncManualResetEvent where the API allows",
       "FO-DICOM.Core/Network/DicomServer.cs",
       "FO-DICOM.Core/Network/DicomService.cs",
       "FO-DICOM.Core/Network/DicomCFindRequest.cs")"""),

md("""\
## Station 6 — The stop

Three warnings are left, and they are groups B and C. This notebook stops here,
on purpose.

Both change what the library *does*. B changes a hash value. C changes a
computation. To change either one safely, somebody has to be able to answer the
question "did the behaviour change?" — and that is a test, not a compiler.

So: does this code base have tests?
"""),

code("""\
with open(os.path.join(SPECIMEN, "Tests", "FO-DICOM.Tests",
                       "FO-DICOM.Tests.csproj"), encoding="utf-8-sig") as fh:
    tests_csproj = fh.read()
suite_tfms = re.search(r"<TargetFrameworks?>([^<]+)<", tests_csproj).group(1)

n_test_files = sum(1 for b, _, ns in os.walk(os.path.join(SPECIMEN, "Tests"))
                   for n in ns if n.endswith(".cs"))
rc, sdk = run(["docker", "run", "--rm", IMAGE, "dotnet", "--version"])

print("test files in the clone     :", n_test_files)
print("the suite targets           :", suite_tfms)
print("the SDK in our container    :", sdk.strip())
print()
print("Those two lines do not intersect. net462 needs Windows or Mono, and the")
print("netcoreapp versions are out of support and not in this SDK.")
print()
print("So the library has tests, and it has no usable test oracle. That is the")
print("subject of 02, and it is the reason these three warnings stay open.")
print()
print("still open, handed to 02:")
show(after_a["warnings"])"""),

md("""\
## Station 7 — The ratchet

Fixing warnings once is housekeeping. Making them impossible is engineering.

`TreatWarningsAsErrors` turns the next new warning into a failed build, so the
eleven cannot quietly become twelve. It cannot go on yet — three warnings are
still open — and the cell below proves that rather than claiming it.

It goes on in the last commit of `02_test_driven_development`, when
the count reaches zero.
"""),

code("""\
ratchet = build(extra=["-warnaserror"], label="-warnaserror, today")
print()
print("exit code      :", ratchet["rc"], "<- the ratchet is premature, as expected")
print("would-be errors:", len(ratchet["errors"]))
show(ratchet["errors"])
print()
print("This is the gate for 02: when this build is green, the project setting")
print("goes in and the gate stays shut.")"""),

md("""\
## What a reviewer receives

Small, readable, and one commit per decision.
"""),

code("""\
print(git("log", "--oneline", "%s..HEAD" % SPECIMEN_TAG)[1].strip())
print()
print(git("diff", "--stat", "%s..HEAD" % SPECIMEN_TAG)[1].strip())
print()
print("tracked changes left uncommitted:",
      git("status", "--short", "--untracked-files=no")[1].strip() or "none")
print("branch:", git("rev-parse", "--abbrev-ref", "HEAD")[1].strip())"""),

md("""\
## What this notebook proved

- **Eleven warnings were four decisions**, and the difference between them was
  not the warning code. It was whether the fix changes behaviour.
- **The compiler produced the complete list of obsolete uses**, and
  `01a_find_obsolete_call_sites` measures that against a text search: 62 matches against 6
  call sites.
- **The oracle judged the fix, three times.** The file-scope alias changed the
  source and nothing else, the namespace-scope alias was rejected outright, and
  the qualified type revealed that two of the six sites are a public API
  change. None of that is visible to a text search.
- **Three warnings were kept on purpose**, each with the reason next to the
  code, because removing them would change behaviour or break the public
  surface.
- **The work is a reviewable branch**, one commit per decision, cherry-pickable
  into a pull request later.

## What it did not prove

- **Nothing about behaviour.** Not one test ran in this notebook. The build is
  green, and green is not proof — that is claim 4, and it is `02`'s job.
- **Nothing about the rest of the library.** The build matrix is still the one
  entry from `00_setup`: `FO-DICOM.Core/netstandard2.0`.

## The question to remember

Not "are there warnings?" but **"which of these change behaviour, and what do I
have that can tell?"**

Next: `02_test_driven_development` (not written yet) answers
the three that are left — one defect with a failing test first, and one
hazard where no test may fail at all.
"""),
]

nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python"},
}

out = "workshops/legacy-refactor/notebooks/01_build_warnings.ipynb"
nbf.write(nb, out)
print("wrote", out, "with", len(nb.cells), "cells (no outputs; execute next)")
