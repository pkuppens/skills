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

**Use when:** you must change or remove a member, and you must know every place
that uses it.

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
# C#
dotnet build --no-restore 2>&1 | rg 'error CS0619' | sort -u > /tmp/sites-cc.txt
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
| Only the text search found it | The line is behind a build condition that you did not build, or it is in a comment, a string, or dead code. |
| Neither found it | Reflection, a string key, or a serialization contract. Find these by hand, and write a test. |

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

## Rules for the agent

1. Do not report a refactor as complete after a text search alone.
2. Escalate to the compiler before you claim completeness.
3. Show the comparison. Do not describe it.
4. Name the configurations that you built.
5. List the blind spots that remain, even when the list is empty. Say that it is
   empty, and say why.
6. Write a test for each call site that no tool can see.

## Related skills

| Skill | Relation |
| --- | --- |
| [`oracle-first-refactor`](../oracle-first-refactor/SKILL.md) | Holds the deliberate-breakage technique that makes step 3 work. |
| [`legacy-build-container`](../legacy-build-container/SKILL.md) | Produces the build that step 3 needs. |
| [`brutally-honest-code-review`](../brutally-honest-code-review/SKILL.md) | Reviews the diff that the agent produced. |
