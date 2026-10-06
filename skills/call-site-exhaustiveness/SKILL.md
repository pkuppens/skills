---
name: call-site-exhaustiveness
description: >
  Answer one question honestly: did I find every call site? Ranks the search
  methods by soundness, and makes the agent report the method, the count, and
  the blind spots. Use before any rename, signature change, API removal, or
  impact analysis in a code base that is too large to read, and whenever an
  agent is about to claim that a refactor is complete.
---

# Call-site exhaustiveness

**Invoke:** `/call-site-exhaustiveness`
**Use when:** you must change or remove a member, and you must know every place
that uses it.
**Status:** exercised on fo-dicom 4.0.8 (76 kLOC, 313 files), twice.
[`01a_find_obsolete_call_sites.ipynb`](../../workshops/legacy-refactor/notebooks/01a_find_obsolete_call_sites.ipynb)
measured 62 text-search occurrences, 8 scoped text-search sites, and 6 true
call sites, with the 2 extra caused by a second class of the same name.
[`01_build_warnings.ipynb`](../../workshops/legacy-refactor/notebooks/01_build_warnings.ipynb)
then applied the fix to those 6 sites and had **three attempts rejected by the
compiler** — the traps below came from that run.

Terms used here — [test oracle, sound, recall, call site](../../CONTEXT.md#language-legacy-refactoring) — have one
definition for this library. Read it before you use them in a report.

**The failure that this skill prevents:** an agent runs one text search, finds
some call sites, fixes those, and reports the refactor as complete. The missed
sites then fail at run time, or they fail in a configuration that nobody built.

---

## The method ladder

Three methods. Each method is more sound than the method above it.

| Step | Method | Sound? | Covers |
| --- | --- | --- | --- |
| 1 | Text search (`rg`, `grep`) | No, in both directions | Only text that matches |
| 2 | Semantic index (LSP, serena, codegraph) | Within the index | The configuration that the index was built for |
| 3 | The compiler | Yes | The configurations that you build |

**Only the compiler can claim completeness.** Use the technique in
[`oracle-first-refactor`](../oracle-first-refactor/SKILL.md) to make the
compiler produce the list.

Use step 1 to form a first idea. Use step 2 to see how much code the change
touches, before you choose an approach. Use step 3 to prove that the work is
complete.

---

## Why a text search gives a wrong answer

### C++

| Case | Example | Why the search fails |
| --- | --- | --- |
| Macro-generated call | `vtkSetMacro(Spacing, double);` generates `SetSpacing`. | The name `SetSpacing` is in no source file. |
| Template instantiation | `template <class T> void f(T t) { t.release(); }` | `release` is called for each `T`, and no line names the type. |
| Build condition | `#ifdef WITH_OPENSSL` ... `oldApi();` | The line exists but is not compiled. The search finds it; the build does not. |
| Argument-dependent lookup | `swap(a, b);` resolves to a function in the type's namespace. | No qualified name appears. |
| Type alias | `typedef OFString MyStr;` then `MyStr s;` | A search for `OFString` misses `MyStr`. |

### C#

| Case | Example | Why the search fails |
| --- | --- | --- |
| Reflection | `type.GetMethod("Load").Invoke(obj, args);` | The name is a string. The compiler also cannot see it. |
| String-keyed registration | `services.AddSingleton("dicomReader", ...)` | The key is data, not code. |
| Serialization contract | A property name in JSON or XML that maps by name. | The contract lives outside the code. |
| Generated designer file | `Form1.Designer.cs` calls a property that a tool wrote. | The call is real, but the file is generated and often ignored by a search filter. |
| Partial class | The member is in `A.part1.cs`, the call is in `A.part2.cs`. | The search works, but a reader misses the context. |

**The important case is reflection.** A reflective call site is invisible to the
text search **and** to the compiler. Steps 3 and 4 of the oracle ladder exist
because of this case. See [`oracle-first-refactor`](../oracle-first-refactor/SKILL.md).

---

## The comparison procedure

Run all three methods against the same question. Then compare the result sets.
Each difference teaches you something about the code base.

### Step 1 — Text search

```bash
rg -n --stats '\bOldApi\b' > /tmp/sites-rg.txt
```

For C#, include generated files. Do not filter them away.

### Step 2 — Semantic index

Use the language server or the index of the project.

```bash
# C++: needs compile_commands.json
clangd --check=path/to/file.cpp
# Any language with an index:
codegraph explore "OldApi call sites"
```

Record the count.

### Step 3 — The compiler

Break the member on purpose, on a branch. The build then lists every call site.

```bash
# C++
cmake --build build 2>&1 | rg 'error:' | sort -u > /tmp/sites-cc.txt
# C#  - promote the obsolete warning; do NOT rely on [Obsolete(error: true)]
dotnet build --no-restore -warnaserror:CS0618 2>&1 | rg 'error CS0618' | sort -u > /tmp/sites-cc.txt
```

The procedure for the breakage is in
[`oracle-first-refactor`](../oracle-first-refactor/SKILL.md). Do not repeat it
here.

### Step 4 — Compare and explain

```bash
diff <(cut -d: -f1,2 /tmp/sites-rg.txt | sort -u) \
     <(cut -d: -f1,2 /tmp/sites-cc.txt | sort -u)
```

Explain **each** difference. Every difference has a cause. Find the cause. It is
one of these three:

| Direction | Cause |
| --- | --- |
| Only the compiler found it | A macro, a template, an alias, or ADL. |
| Only the text search found it | A different type with the same name; a line behind a build setting you did not build; a comment, a string, or dead code. |
| Neither found it | Reflection, a string key, or a serialization contract. Find these by hand, and write a test. |

**The second row is the dangerous one.** A missed site fails loudly at the next
build. A false site invites an engineer — or an agent working from text-search
output — to change code that was already correct. In the recorded fo-dicom run,
2 of the 8 text-search sites were uses of the *replacement* class, which has the
same short name as the deprecated one. Acting on them would have put the
deprecated type back.

### Step 5 — Name the configurations

The compiler is sound **only for what you build**. State which configurations
you built. If the project has a build matrix, then full recall needs the full
matrix.

---

## The recall-reporting rule

**Never state a count without the method and the blind spots.**

Bad report:

> I found 14 call sites and updated them all.

Good report:

> Method and result:
> - `rg` found 14 sites.
> - The semantic index found 23 sites.
> - The build found 23 errors in the default configuration, and 2 more with
>   `WITH_OPENSSL=ON`.
>
> Configurations built: `default`, `WITH_OPENSSL=ON`. The matrix also has
> `WITH_ICU=ON`, which I did not build.
>
> Blind spots that remain: one reflective call in `PluginLoader.cs` uses the
> member name as a string. The compiler cannot see it. I added a test that
> fails if the member is absent.
>
> Recall: complete for the two configurations that I built. Not proven for the
> rest of the matrix.

The last sentence is the most important part. Say what you proved. Then say
what you did not prove.

---

## After the list: the fix needs the oracle too

The list of call sites is not the end. **Run the oracle again after each attempt
at the fix.** An edit can look correct and change no count. Measured on
fo-dicom 4.0.8, where 6 sites used an obsolete class, and a replacement class
with the same name must take its place:

| Attempt | What happened | Why |
| --- | --- | --- |
| A `using X = Replacement;` alias at file scope | The source changed. **The warning count did not.** | C# looks for a simple name in the innermost namespace first, then further out. A type in that namespace comes before an alias at file scope. The obsolete class continued to win. |
| The same alias, moved inside the namespace | `CS0576`: an alias must not hide a type of the same namespace. | The language closes this door on purpose. |
| The replacement named in full at each site | 4 of 6 sites compiled. The other 2 had to go back, because the field they share gave `CS0052`, inconsistent accessibility. | The replacement was `internal`, and the field was `protected` on a public class. To swap it would leak an internal type. To remove the field is a breaking change. |

Two rules follow. Both are free.

1. **A fix is not done when you save the edit. It is done when the count
   falls.** A text search reports the first attempt above as finished.
2. **A complete list is not one uniform job.** The compiler gave every site, and
   it was correct. Then it showed that two sites need a different kind of
   change. Completeness is free. Uniformity is not.

### Trap: a red build hides warnings

If the build has an error, the compiler can stop before the stage that reports
some warnings. In the run above, `CS0675` left the output while an unrelated
`CS0052` was in it. Nobody had fixed `CS0675`.

**Triage warnings only on a green build.** On a red build, your list is not the
list.

## Rules for the agent

1. Do not report a refactor as complete after a text search alone.
2. Escalate to the compiler before you claim completeness.
3. Show the comparison. Do not describe it.
4. Name the configurations that you built.
5. List the blind spots that remain, even when the list is empty. Say that it is
   empty, and say why.
6. Write a test for each call site that no tool can see.
7. Run the oracle again after each attempt at the fix. Report the count, not
   the edit.

## Related skills

| Skill | Relation |
| --- | --- |
| [`oracle-first-refactor`](../oracle-first-refactor/SKILL.md) | Holds the deliberate-breakage technique that makes step 3 work. |
| [`legacy-build-container`](../legacy-build-container/SKILL.md) | Produces the build that step 3 needs. |
| [`brutally-honest-code-review`](../brutally-honest-code-review/SKILL.md) | Reviews the diff that the agent produced. |
