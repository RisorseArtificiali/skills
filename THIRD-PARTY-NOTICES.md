**English** · [Italiano](THIRD-PARTY-NOTICES_IT.md)

# Third-party notices

The `forked/` directory contains skills derived from MIT-licensed upstream
repositories, kept as pinned snapshots — some modified locally. The upstream
license texts are retained below, per their terms. `skills/` contains original
work (repo MIT license applies).

## Derivation map

Verified on 2026-08-28 by diffing each fork against its base snapshot commit:
"byte-identical" means no differences at all. The reasons behind each change
are described in [`forked/README.md`](forked/README.md).

| Skill | Upstream repo | Base snapshot | Local changes |
|---|---|---|---|
| forked/subagent-driven-development | https://github.com/obra/superpowers | `44c9b2d` (2026-07-28, pre-v6.3.0) | added "Model Selection — always inherit" (2026-08-27 maintainer policy, replacing upstream's model tiering; the fix-loop wording was updated to match: rounds 4–5 re-dispatch a fresh implementer with fuller context instead of a more capable model) and "Fast, safe test iteration (Maven projects only)" |
| forked/writing-plans | https://github.com/obra/superpowers | `44c9b2d` (2026-07-28) | added the "Deviation Protocol" section and a per-task "Guardrails" block (neither existed upstream) |
| forked/doubt-driven-development | https://github.com/addyosmani/agent-skills | `7829ffd` (2026-07-26) | none — byte-identical to the snapshot. Upstream has since restructured its repository; our copy keeps the standalone-friendly `references/` paths (an earlier revision of this file wrongly listed those path differences as our local changes — they are upstream's later drift) |
| forked/grilling | https://github.com/mattpocock/skills | `4128367` (2026-07-28) | replaced the question flow: upstream maps a "design tree" and asks the whole open "frontier" as one batched round of numbered questions; this copy asks one question at a time, each with the agent's recommended answer, and keeps the facts-vs-decisions split |
| forked/handoff | https://github.com/mattpocock/skills | `4128367` (2026-07-28) | handoff storage moved from the OS temporary directory to `<repo>/.reviews/handoffs/<date>-<topic>.md` (kept out of version control via `.git/info/exclude`); topic derived from the command argument or branch name; one file per handoff; a pending/`done/` lifecycle whose cleanup instruction travels inside the handoff document itself |

Upstream skills used unmodified are not vendored here; see README for the list.

## License texts


### 1. obra/superpowers — MIT

```
MIT License

Copyright (c) 2025 Jesse Vincent

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 2. mattpocock/skills — MIT

```
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 3. addyosmani/agent-skills — MIT

```
MIT License

Copyright (c) 2025 Addy Osmani

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 4. DietrichGebert/ponytail — MIT

```
MIT License

Copyright (c) 2026 DietrichGebert

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
