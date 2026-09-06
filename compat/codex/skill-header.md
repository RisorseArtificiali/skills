## Codex host mapping

Use the tools actually exposed by this session. `Skill` means locate and read
the installed `SKILL.md`; resolve `superpowers:name` by the bare skill name,
preferring this toolkit's installed fork. Resolve bundled files from the real
skill directory, not the project's working directory. `Read`/`Bash` mean file
reading and shell execution; `TodoWrite` means the available plan tool or a
Markdown checklist. `AskUserQuestion` means the available question widget
(only in its supported mode), otherwise a concise question in chat. Wait for
answers at interactive gates and honor existing user decisions.

For fresh subagents use `spawn_agent` with `fork_turns: "none"` when supported;
omit model and reasoning overrides to inherit the session. Resume an idle
implementer with `followup_task` when available. Respect the live concurrency
limit; serialize writes and builds within one worktree. If subagents are
unavailable, disclose the missing fresh-context review rather than simulating it.
Host tool definitions and user instructions govern over upstream host examples.
