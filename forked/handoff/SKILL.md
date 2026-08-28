---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to `<repo>/.reviews/handoffs/<date>-<topic>.md` when inside a git repository (create the directory if needed and ensure `.reviews/` is listed in `.git/info/exclude` — never in `.gitignore`); only outside a repository fall back to the OS temporary directory. Derive `<topic>` from the user's argument, or from the branch/task name when no argument is given. One handoff per file: if the name is already taken, add a distinguishing suffix rather than overwriting — several sessions may be handing off in parallel.

Lifecycle: the `handoffs/` directory holds only pending handoffs; consumed ones live in `handoffs/done/`. Since no skill runs on the resuming side, the cleanup instruction must travel inside the document itself — start every handoff with this line:

> **To the agent resuming from this document:** after reading, move this file to `.reviews/handoffs/done/` (create it if needed) so the handoffs directory lists only pending work. Do not delete it. The handoff must survive until the next session, and on some machines the temp directory does not.

Include a "suggested skills" section in the document, which suggests skills that the agent should invoke.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
