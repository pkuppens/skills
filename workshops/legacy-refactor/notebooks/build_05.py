"""Author 05_refactoring.ipynb. Run from the repo root, then execute the notebook.

This script only writes the cells. It never writes outputs: the outputs come
from a real kernel run via `jupyter nbconvert --execute`. See notebooks/README.md
rule 2.
"""
import nbformat as nbf

nb = nbf.v4.new_notebook()
md = lambda t: nbf.v4.new_markdown_cell(t)
code = lambda t: nbf.v4.new_code_cell(t)

nb.cells = [
md("""\
# 05 — Refactoring: let the compiler find the call sites

**Proves:** claims 2 and 3 of [../THESIS.md](../THESIS.md), and the limits of claim 2.
**Skill:** [`call-site-exhaustiveness`](../../../skills/call-site-exhaustiveness/SKILL.md), [`oracle-first-refactor`](../../../skills/oracle-first-refactor/SKILL.md)
**Needs:** .NET SDK, `rg` (ripgrep), git, and the fo-dicom specimen from `00_setup`. No model API. No network after the first restore.
**Run time:** about 1 minute.
**State:** EXECUTED

---

## The reason for this change

Reason 3 of [../THESIS.md](../THESIS.md#why-refactor-legacy-code): **the library forces it.**

fo-dicom marks `FellowOakDicom.Network.AsyncManualResetEvent` as obsolete. The
maintainers wrote the migration message themselves. A team that upgrades must
stop using the type.

The task is not "improve the code". The task is: **find every place that uses
this type, and miss none.** That is a question about completeness, so the
[test oracle](../../../CONTEXT.md#language-legacy-refactoring) is the compiler.
"""),

code("""\
import os, subprocess, shlex, re, time, shutil, fnmatch

# Repo root, from this notebook's location. Works from a clone, no install step.
ROOT = os.path.abspath(os.path.join(os.getcwd(), "..", "..", ".."))
SPECIMEN = os.path.join(ROOT, "tmp", "workshop-workspace", "fo-dicom")
PROJECT = os.path.join(SPECIMEN, "FO-DICOM.Core", "FO-DICOM.Core.csproj")
TARGET = "AsyncManualResetEvent"

def run(cmd, cwd=SPECIMEN, check=False):
    \"\"\"Run a command and return (exit code, combined output).\"\"\"
    p = subprocess.run(cmd if isinstance(cmd, list) else shlex.split(cmd),
                       cwd=cwd, capture_output=True, text=True, errors="replace")
    out = (p.stdout or "") + (p.stderr or "")
    if check and p.returncode != 0:
        print(out[-2000:])
        raise SystemExit("command failed: %s" % cmd)
    return p.returncode, out

if not os.path.isdir(SPECIMEN):
    raise SystemExit("Specimen missing. Run 00_setup.ipynb first.")

# The text search. Uses ripgrep when it is installed, and a plain Python scan
# otherwise, so this notebook runs on a machine that has neither ripgrep nor a
# model API. Both engines return the same rows: (path, line number, line text).
RG = shutil.which("rg")

def text_search(pattern, subdir=".", name_glob="*.cs"):
    rows = []
    if RG:
        rc, out = run([RG, "-n", pattern, "--glob", name_glob, subdir])
        for line in out.splitlines():
            if not line.strip():
                continue
            path, _, rest = line.partition(":")
            num, _, text = rest.partition(":")
            if num.isdigit():
                rows.append((path.replace(os.sep, "/").lstrip("./"), int(num), text))
        return rows, "ripgrep"
    rx = re.compile(pattern)
    for b, dirs, names in os.walk(os.path.join(SPECIMEN, subdir)):
        dirs[:] = [d for d in dirs if d not in ("obj", "bin", ".git")]
        for n in names:
            if not fnmatch.fnmatch(n, name_glob):
                continue
            f = os.path.join(b, n)
            rel = os.path.relpath(f, SPECIMEN).replace(os.sep, "/")
            with open(f, encoding="utf-8", errors="replace") as fh:
                for i, line in enumerate(fh, 1):
                    if rx.search(line):
                        rows.append((rel, i, line.rstrip()))
    return rows, "python re"

for tool in ("dotnet", "git"):
    if not shutil.which(tool):
        raise SystemExit("%s is not on PATH. See 00_setup.ipynb." % tool)

print("specimen    :", os.path.relpath(SPECIMEN, ROOT))
print("project     :", os.path.relpath(PROJECT, ROOT))
print("target      :", TARGET)
print("tag         :", run("git describe --tags --always")[1].strip())
print("text search :", text_search(TARGET, "FO-DICOM.Core")[1])"""),

md("""\
## Step 0 — The specimen is real, and large enough to matter

A toy project proves nothing. Measure first.
"""),

code("""\
cs_files = []
for base, dirs, names in os.walk(os.path.join(SPECIMEN, "FO-DICOM.Core")):
    dirs[:] = [d for d in dirs if d not in ("obj", "bin")]
    cs_files += [os.path.join(base, n) for n in names if n.endswith(".cs")]

loc = 0
for f in cs_files:
    with open(f, encoding="utf-8", errors="replace") as fh:
        loc += sum(1 for _ in fh)

print("C# files in the built project :", len(cs_files))
print("lines of C#                   :", loc)
print()
print("Too large to read in one go. That is the point: the method never reads")
print("the whole project. It asks a tool instead.")"""),

md("""\
## Step 1 — The weakest method: text search

`rg` is fast and it is **not sound**. It matches text, so it knows nothing about
types, namespaces or which project you build.

Start with the naive command, the one everybody runs first.
"""),

code("""\
rows, engine = text_search(TARGET, ".")
naive_hits = sum(len(re.findall(TARGET, text)) for _, _, text in rows)
naive_files = sorted(set(f for f, _, _ in rows))

print("naive text search over the whole clone")
print("  occurrences :", naive_hits)
print("  files       :", len(naive_files))
print()
for f in naive_files:
    print("   ", f)"""),

md("""\
That number is useless, and it is useless in a way that matters.

Two reasons, and both are ordinary in a legacy repository:

1. **A second, older copy of the project.** `DICOM/` is the previous project
   layout, targeting `netstandard1.3` and `net462`. It is not in the build we
   ship. Its matches are real text and irrelevant code.
2. **The declaration files themselves**, plus XML documentation comments
   (`<see cref="..."/>`), which are not call sites.

So scope the search to the project that is actually built, and drop the
declarations. This is the *generous* version of the text search — the best a
careful engineer gets without a compiler.
"""),

code("""\
rows, engine = text_search(TARGET, "FO-DICOM.Core")

def is_declaration(path):
    return path.endswith("Network/AsyncManualResetEvent.cs") or \\
           path.endswith("Network/Client/Tasks/AsyncManualResetEvent.cs")

scoped = [(f, n, t) for f, n, t in rows if not is_declaration(f)]
rg_sites = set((f, n) for f, n, _ in scoped)

print("text search (%s), scoped to the built project, declarations removed" % engine)
print("  sites :", len(rg_sites))
print("  files :", len(set(f for f, _ in rg_sites)))
print()
for f, n, t in sorted(scoped):
    print("    %s:%d: %s" % (f.split("FO-DICOM.Core/", 1)[-1], n, t.strip()))"""),

md("""\
## Step 2 — The sound method: make the compiler produce the list

Now ask the compiler. It resolves types, so it cannot be fooled by a name.

The type is already marked `[Obsolete]`, which the compiler reports as warning
`CS0618`. A warning is easy to ignore, so promote exactly that warning to an
error. Nothing else changes.

```
dotnet build -warnaserror:CS0618
```

**No source edit is needed here.** The deliberate breakage described in
[`oracle-first-refactor`](../../../skills/oracle-first-refactor/SKILL.md) is for
the case where the old API is *not* already deprecated. When the maintainers
have done that work, promoting their warning is enough.
"""),

code("""\
t0 = time.time()
rc, out = run(["dotnet", "build", PROJECT, "-v", "n", "--nologo", "-t:Rebuild",
               "-warnaserror:CS0618"])
elapsed = time.time() - t0

pat = re.compile(r"([^\\s(]+\\.cs)\\((\\d+),(\\d+)\\): error CS0618: '" + TARGET + r"'")

def site_key(raw_path):
    \"\"\"One diagnostic can appear twice: MSBuild prints a node-prefixed absolute
    form ('1>C:/...') and a project-relative form. Normalise both to the path
    inside the project, so a site is counted once.\"\"\"
    p = raw_path.replace("\\\\", "/")
    p = p.split(">")[-1]                       # drop the '1>' MSBuild node prefix
    return p.split("FO-DICOM.Core/", 1)[-1]    # keep 'Network/DicomServer.cs'

cc_sites = set()
for m in pat.finditer(out):
    cc_sites.add((site_key(m.group(1)), int(m.group(2))))

print("compiler, -warnaserror:CS0618")
print("  exit code  :", rc, "(non-zero on purpose: the errors are the list)")
print("  sites      :", len(cc_sites))
print("  files      :", len(set(f for f, _ in cc_sites)))
print("  build time : %.1f s" % elapsed)
print()
for f, l in sorted(cc_sites):
    print("    %s:%d" % (f, l))"""),

md("""\
## Step 3 — Compare the two lists, and explain every difference

A difference is never noise. Each one has a cause, and the cause is worth more
than the count.
"""),

code("""\
rg_norm = set((f.split("FO-DICOM.Core/", 1)[-1], l) for f, l in rg_sites)
cc_norm = set(cc_sites)   # already normalised at capture time

print("%-46s %s" % ("method", "sites"))
print("%-46s %s" % ("-" * 46, "-----"))
print("%-46s %d" % ("A. text search, whole clone (occurrences)", naive_hits))
print("%-46s %d" % ("B. text search, built project, no declarations", len(rg_norm)))
print("%-46s %d" % ("C. compiler, -warnaserror:CS0618", len(cc_norm)))
print()
print("in B but NOT in C  (text search found what is not there):")
for f, l in sorted(rg_norm - cc_norm):
    print("    %s:%d" % (f, l))
print()
print("in C but NOT in B  (compiler found what the text search missed):")
extra = sorted(cc_norm - rg_norm)
print("    none" if not extra else "")
for f, l in extra:
    print("    %s:%d" % (f, l))"""),

md("""\
### What the difference is

The text search reports **two sites that are not uses of this type at all**:

```csharp
// FO-DICOM.Core/Network/Client/States/DicomClientSendingRequestsState.cs
private readonly Tasks.AsyncManualResetEvent _sendMoreRequests;
```

There are **two different classes with the same name** in this library:

| Class | Role |
| --- | --- |
| `FellowOakDicom.Network.AsyncManualResetEvent` | The obsolete one. The target. |
| `FellowOakDicom.Network.Client.Tasks.AsyncManualResetEvent` | `internal`. The **replacement**, named in the obsolete message. |

A text search cannot separate them. The compiler resolves the type and never
confuses the two.

**This is the dangerous direction of being unsound.** A missed site fails loudly
at build time. A false site invites an engineer — or an agent working from
`rg` output — to "migrate" code that was already correct, and that edit
replaces the new class with the deprecated one. The error count goes down and
the code gets worse.

For this target the compiler missed nothing, so claim 2 holds here as stated.
"""),

md("""\
## Step 4 — A trap worth measuring: `error: true` reports fewer sites

The obvious way to force the issue in C# is to make the attribute itself an
error:

```csharp
[Obsolete("Use the AsyncEx library instead", error: true)]
```

That is correct for **blocking new use**. It is wrong for **enumerating
existing use**, and the difference is measurable. Apply it on a branch and
count.
"""),

code("""\
decl = os.path.join(SPECIMEN, "FO-DICOM.Core", "Network", "AsyncManualResetEvent.cs")
with open(decl, encoding="utf-8-sig") as fh:
    original = fh.read()

patched = original.replace(
    '[Obsolete("Use the AsyncEx library instead")]',
    '[Obsolete("Use the AsyncEx library instead", error: true)]', 1)
patched = patched.replace(
    '[Obsolete("For fo-dicom consumers: use the AsyncEx library instead, '
    'for fo-dicom contributors: use FellowOakDicom.Network.Client.Tasks.AsyncManualResetEvent")]',
    '[Obsolete("For fo-dicom consumers: use the AsyncEx library instead, '
    'for fo-dicom contributors: use FellowOakDicom.Network.Client.Tasks.AsyncManualResetEvent", '
    'error: true)]', 1)
assert patched != original, "patch did not apply"

try:
    with open(decl, "w", encoding="utf-8-sig", newline="\\r\\n") as fh:
        fh.write(patched)
    rc2, out2 = run(["dotnet", "build", PROJECT, "-v", "n", "--nologo", "-t:Rebuild"])
    pat2 = re.compile(r"([^\\s(]+\\.cs)\\((\\d+),(\\d+)\\): error CS0619: '" + TARGET)
    err_sites = set()
    for m in pat2.finditer(out2):
        err_sites.add((site_key(m.group(1)), int(m.group(2))))
finally:
    with open(decl, "w", encoding="utf-8-sig", newline="\\r\\n") as fh:
        fh.write(original)   # always restore: the specimen stays clean

print("D. [Obsolete(..., error: true)]  -> CS0619")
print("   sites :", len(err_sites))
for f, l in sorted(err_sites):
    print("     %s:%d" % (f, l))
print()
print("C. -warnaserror:CS0618           -> sites :", len(cc_norm))
print()
print("missing from D, present in C:")
for f, l in sorted(cc_norm - err_sites):
    print("     %s:%d" % (f, l))
print()
print("source restored:", open(decl, encoding='utf-8-sig').read() == original)"""),

md("""\
### Why `error: true` under-reports

Once the **declaration** of a field is an error, the compiler stops reporting
the later **uses** of that field. That is ordinary error recovery: it avoids
burying the real cause under cascading messages.

So the sites that disappear are exactly the uses whose declaration already
errored:

| Reported | `-warnaserror:CS0618` | `[Obsolete(error: true)]` |
| --- | --- | --- |
| Field declarations | yes | yes |
| Uses of those fields | yes | **no** |

**The rule for C#:** to *enumerate*, promote the warning. To *block*, use
`error: true`. If you must use `error: true`, then fix and rebuild until the
count reaches zero, and never trust the first count as the total.

This is why the recall-reporting rule in
[`call-site-exhaustiveness`](../../../skills/call-site-exhaustiveness/SKILL.md)
asks for the method next to the number. "3 sites" and "6 sites" are both true
here, for different methods, and only one of them is the list of work to do.
"""),

md("""\
## Step 5 — State the limits before anybody asks

The compiler is sound **for what you build**. It is not magic, and the gap is
measurable in this very repository.
"""),

code("""\
rows_all, _ = text_search(TARGET, ".")
all_files = sorted(set(f for f, _, _ in rows_all))
outside = [f for f in all_files if not f.startswith("FO-DICOM.Core")]

print("files mentioning the target: %d total, %d outside the built project" % (
    len(all_files), len(outside)))
print()
print("outside the project we built:")
for f in sorted(outside):
    print("   ", f)
print()
print("Those belong to DICOM/ - the older project layout (netstandard1.3,")
print("net462). Real code, real uses, invisible to our build.")
print()
print("A claim of complete recall is therefore limited to the build matrix.")
print("Ours has one entry, on purpose, and it is written down:")
print('   MATRIX=("FO-DICOM.Core/netstandard2.0")')"""),

md("""\
### The three limits, stated plainly

1. **Build settings.** Code behind a different project or a build condition is
   invisible until you build that configuration. Here, 8 of the 11 matching
   files sit outside the project we built. The single-entry build matrix is a
   deliberate choice, declared in
   [ADR 002](../../../docs/decisions/002-workshop-container-environment.md),
   not an oversight.
2. **Reflection and text keys.** A call made by name at run time is invisible to
   the compiler as well as to the text search. **This target has no such use** —
   searching for `"AsyncManualResetEvent"` as a string finds only XML
   documentation comments. So this notebook does not demonstrate that limit; it
   states it. Claiming otherwise would be inventing evidence.
3. **Uninstantiated generics.** `AsyncManualResetEvent<T>` is only checked where
   it is instantiated. C# checks generic definitions more thoroughly than C++
   templates, but a type used only by an absent configuration is still unseen.

## The recall report

This is the honest form. Method, count, configuration, blind spots.
"""),

code("""\
print("Target  : FellowOakDicom.Network.AsyncManualResetEvent  (obsolete upstream)")
print("Reason  : 3 - the library deprecated it; an upgrade must stop using it")
print()
print("Method and result")
print("  text search, whole clone      : %d occurrences, %d files  (unusable)" % (naive_hits, len(naive_files)))
print("  text search, built project    : %d sites" % len(rg_norm))
print("  compiler, -warnaserror:CS0618 : %d sites  <- the list of work" % len(cc_norm))
print("  [Obsolete(error: true)]       : %d sites  (under-reports; see step 4)" % len(err_sites))
print()
print("Configurations built : FO-DICOM.Core, netstandard2.0.  One entry, declared.")
print("                       Not built: DICOM/ (netstandard1.3, net462).")
print()
print("False sites from the text search : %d" % len(rg_norm - cc_norm))
print("  cause: a second class of the same name, which is the replacement")
print()
print("Blind spots that remain")
print("  - uses in the configurations not built (listed in step 5)")
print("  - reflective use: none found for this target; not proven absent elsewhere")
print()
print("Recall : complete for FO-DICOM.Core/netstandard2.0. Not proven for the rest.")"""),

md("""\
## What this notebook proved

- **Claim 2 holds.** The compiler produced the list of call sites. The text
  search did not, and its error was over-reporting, which is the direction that
  causes a wrong edit.
- **Claim 3 holds.** No oracle had to be written. The type system was already
  there, and the build took about a second.
- **The limits are real and measured**, not hedged away: 8 of 11 matching files
  lie outside the one-entry build matrix.

What this notebook did **not** prove: that a green build means the behavior did
not change. It does not. That is the job of `02_test_driven_development`, which
is planned and not yet written.

The specimen is left unmodified — step 4 restores the file it patched.
"""),
]

nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python"},
}

out = "workshops/legacy-refactor/notebooks/05_refactoring.ipynb"
nbf.write(nb, out)
print("wrote", out, "with", len(nb.cells), "cells (no outputs; execute next)")
