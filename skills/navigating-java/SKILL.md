---
name: navigating-java
description: Structural navigation of Java codebases — find definitions, callers, implementations, type hierarchies and Maven module structure through symbol-level tools instead of text search. Use whenever working in a Java project and you need to locate a symbol, understand an unfamiliar class or module, trace who calls something before changing a signature, find implementations of an interface, check what a rename or deletion would break, or assess a change's blast radius. Read this BEFORE grepping Java code or opening files to "get oriented".
---

# Navigating Java

## Overview

Text search lies in Java. `rg -w save` cannot tell `OrderRepository.save` from `UserCache.save`, misses calls through an interface or superclass, drowns overloads together, and sees nothing of dependency injection. Symbol-level tools answer the question you actually have — *who calls this method* — instead of the question grep can answer — *what text looks like this*.

Grep is not banned; it has a different job. Code structure → symbol tools. Strings, resources, configs, comments → grep. The expensive mistakes (missed caller on a signature change, "unused" code that a config file references by name) come from using one where the other belongs.

## Backend Selection

Work down this list; announce the tier when it affects confidence:

1. **Serena MCP** (`mcp__serena__*` tools) — preferred. First use in a repo: `activate_project` with the repo path. The Java language server warms up on the first query; a slow first answer is normal, not broken.
2. **Built-in LSP tool** (Claude Code harness) — definitions/references/diagnostics if present.
3. **CLI fallback** (`ctags`, `rg`, `mvn`, `javap`) — recipes below. Reference results at this tier are *approximate*: say so when reporting them.

## Question → Tool (Serena tier)

| You want | Tool | Notes |
|---|---|---|
| Shape of an unfamiliar file/class | `get_symbols_overview` | ALWAYS before reading the file. Then read only the bodies you need (`find_symbol` with `include_body`) — a 1500-line class costs nothing if you only load two methods. |
| Where is X defined | `find_symbol` / `find_declaration` | `name_path` syntax: `Class/method`, `Class/Inner/method`. |
| Who calls / uses X | `find_referencing_symbols` | Overloaded methods resolve as `load[0]`, `load[1]` — the tool errors with the list; query the variant you mean, or each in turn. Large results return per-file counts first: drill into files, don't raise the size cap. |
| What implements / extends X | `find_implementations` | |
| Rename a symbol | `rename_symbol` | Never search-replace a Java identifier. |
| Did my edit break compilation | `get_diagnostics_for_file` | Cheapest post-edit check; run it on every file you touched before reaching for Maven. |
| Edit one method surgically | `replace_symbol_body`, `insert_after_symbol` | Keeps the diff and your context minimal. |

## Maven Structure

- **Module map:** the reactor is the root `pom.xml` `<modules>` list. For the real resolved graph of one module: `mvn -o -q dependency:tree -pl <module>`. Prefer `-o` (offline) — structure questions never need the network.
- **Test mirror convention:** `src/test/java` mirrors `src/main/java`. The tests for a class live at the mirrored path; when you change a class, its mirror is part of the blast radius even if no symbol reference says so (fixtures, resources, naming-convention discovery).
- **Generated sources** live under `target/generated-sources`. Never edit them; a reference pointing there means "change the generator's input and rebuild", and they vanish on `mvn clean` — code that only compiles because of them needs the generating plugin to run first.

## What Symbol Tools Cannot See

An LSP sees typed references. Java routinely references things by *string*, and every one of these is invisible to it:

- **Reflection**: `Class.forName("com.x.Y")`, `getMethod("name")`.
- **DI by name**: `@Named("beanName")`, Spring XML, qualifier strings, properties keys.
- **ServiceLoader**: implementations registered as FQN lines in `META-INF/services/*`.
- **Jackson/JAXB/config binding**: field and property names appearing in JSON/YAML/XML.
- **Lambdas**: `find_implementations` on a functional interface will not list lambda call sites — find references to the *methods that accept* the interface instead.

**The rule that follows:** "zero references" from the symbol tool is necessary but not sufficient before deleting or renaming anything non-private. Always pair it with a string sweep that includes resources:

```
rg -n --no-ignore-vcs -g '!target' 'ClassName|fully.qualified.ClassName' -g '*.{java,xml,yaml,yml,properties,json}'
```

Only when both come back empty is it dead.

## CLI Fallback Recipes (no LSP available)

- **File shape:** `ctags -x --language-force=Java <file>` — one line per symbol with line numbers; the overview-before-read discipline survives without an LSP.
- **Definition:** `rg -n '\b(class|interface|enum|record|@interface) X\b' --type java`
- **References (approximate):** `rg -nw X --type java`, then check each hit's imports/package to filter same-name strangers. Report these as *text matches, not resolved references*.
- **Implementations:** `rg -n '(implements|extends)[^{]*\bX\b' --type java` — plus the lambda caveat above.
- **Ground truth for a signature change:** let the compiler enumerate the breakage — `mvn -o -q compile -pl <module> -am`. javac is the one reference-finder that cannot miss a typed caller. This is a cheap iteration tier, not the full-verify budget.
- **Compiled/classpath questions:** `javap -p -classpath target/classes com.x.Y` shows the actual signatures the rest of the build sees.

## Discipline

1. **Overview before read.** Never open a Java file top-to-bottom to "get oriented" — symbols overview first, then load only the bodies the task needs. Context spent reading is context unavailable for reasoning.
2. **Symbol query before grep** for anything that is code; grep for anything that is text (strings, configs, resources, comments).
3. **References before edit.** Changing any non-private signature starts with enumerating its callers — including overloads and the test mirror — and stating the count. Editing first and discovering callers by compile error is navigation debt with interest.
4. **Rename = `rename_symbol`** (or, without LSP, references-list-driven edits + compile). Search-replace renames are how `save` in the wrong class gets rewritten.
5. **Diagnostics after edit**, per file touched, before running any build — it is the cheapest feedback loop that exists at this tier.
6. **Deletion needs two empties**: symbol references AND the resource string sweep.

## Interaction with Other Skills

- **`adversarial-code-review` / `review`** — reviewers and verifiers should navigate this way inside their worktrees; a verifier checking "does anything else call this" uses the reference query, not grep.
- **`writing-plans`** — the Files/Interfaces sections of a plan come from these queries (callers, implementations, module deps), not from memory.
- **`codebase-design`** — for *changing* boundaries once navigation has shown you where they are.
