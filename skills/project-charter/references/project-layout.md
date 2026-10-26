# Project Layout & Host Compatibility

Read this before writing any charter file. It is the authority on where files go and what each host
actually reads. Facts verified 2026-10-26 against vendor documentation; unverified points are flagged.

## 1. Canonical layout

```text
<project-root>/
├── AGENTS.md                     # THE constitution. ≤100 lines, no frontmatter. Committed.
├── CLAUDE.md                     # Only if Claude Code is a target. Exactly "@AGENTS.md". Committed.
├── .gitignore                    # must contain: .agents/skills/* + !.agents/skills/REGISTRY.md
│                                 #   (+ .claude/skills/ when the mirror is used)
└── .agents/
    ├── context/
    │   ├── charter.md            # interview answers + open questions. Committed.
    │   └── architecture.md       # architecture of record + decision index. Committed.
    ├── rules/                    # FLAT, numbered, one topic per file. Committed.
    │   ├── 00-project-protocol.md
    │   ├── 10-architecture.md
    │   ├── 20-code-standards.md
    │   ├── 30-collaboration.md
    │   ├── 40-git-workflow.md
    │   └── 50-security-safety.md
    ├── skills/                   # only its CONTENTS are ignored (`.agents/skills/*`)
    │   ├── <skill-name>/SKILL.md # vendored third-party — never committed
    │   └── REGISTRY.md           # human inventory — re-included, always committed
    └── skills.manifest.json      # machine provenance. Committed.
```

When Claude Code is a target host, also mirror the selected skills:

```text
<project-root>/.claude/skills/<skill-name>/SKILL.md
```

**Why the mirror exists:** Claude Code does not read `.agents/skills/` — it reads `.claude/skills/`
(project), `~/.claude/skills/` (user), and plugin dirs. Codex, Cursor and Antigravity all read
`.agents/skills/`. Mirroring is the only way one selection serves all four. Copy byte-identical files;
do not rely on symlinks.

## 2. What each host reads

| Path | Codex | Cursor | Antigravity | Claude Code | DSH |
|---|---|---|---|---|---|
| `AGENTS.md` (root, and per directory) | ✅ root→cwd, concatenated | ✅ rules type | ✅ + subdirs, cumulative | ⚠️ only if no `CLAUDE.md`/`CLAUDE.local.md` above | ✅ verified in practice |
| `CLAUDE.md` | ❌ | ⚠️ compat | ❌ | ✅ | ❌ |
| `.agents/rules/*.md` | ❌ | ❌ | ✅ (flat only) | ❌ | ❌ |
| `.agents/skills/<n>/SKILL.md` | ✅ | ✅ | ✅ | ❌ | ⚠️ unverified |
| `.claude/skills/<n>/SKILL.md` | ⚠️ no | ✅ compat | ❌ | ✅ | ❌ |
| `.claude/rules/*.md` | ❌ | ❌ | ❌ | ✅ | ❌ |
| `.cursor/rules/*.mdc` | ❌ | ✅ (`.md` is ignored) | ❌ | ❌ | ❌ |
| `.github/copilot-instructions.md` | ❌ | ❌ | ❌ | ❌ | ❌ (Copilot only) |

**Consequence — the one rule that matters:** put the **always-on core in root `AGENTS.md`**, because it
is the only file every target host reads natively. `.agents/rules/*.md` carries the detail: Antigravity
auto-loads it, every other host reads it on demand because `AGENTS.md` points at it.

Do **not** split the always-on core across `.cursor/rules/`, `.claude/rules/` and `.agents/rules/` —
each is read by exactly one host, and duplicated prose drifts.

## 3. AGENTS.md vs CLAUDE.md bridge

Claude Code reads `AGENTS.md` natively (v2.1.277+) but in its default `claude-md-or-agents-md` mode only
when no `CLAUDE.md`/`CLAUDE.local.md` exists in the directory or above. If any team member creates a
`CLAUDE.md`, the constitution silently stops being read.

Prevent it with a one-line import — **the officially recommended bridge**:

```markdown
@AGENTS.md
```

Rules:
- Use the **import**, not a symlink. Claude Code's Edit/Write refuse to write *through* a symlink, and
  on Windows a committed symlink checks out as a plain text file unless `core.symlinks` is enabled.
- Never create `CLAUDE.local.md` in a project that relies on `AGENTS.md` — its presence suppresses
  `AGENTS.md` under the default mode.
- Skip `CLAUDE.md` entirely if Claude Code is not a target host.

## 4. Hard limits — respect these or content is silently dropped

| Limit | Value | Applies to |
|---|---|---|
| `AGENTS.md` truncation | **32 KiB** (Codex `project_doc_max_bytes`, default) | Codex concatenates root→cwd and stops at the cap |
| Rule file size | **24,000 bytes** | Antigravity truncates after `@`-includes expand |
| Always-on rules budget | **20,000 tokens** aggregate | Antigravity; on overflow it auto-demotes the largest files to pointer stubs |
| `.agents/rules/` nesting | **flat only** | Antigravity ignores nested subdirectories unless registered in `.agents/rules.json` |
| `SKILL.md` size | **< 500 lines** (~5,000 tokens) | Agent Skills spec; skill bodies stay in context across turns |
| `description` | **≤ 1,024 chars** | Portable spec cap; Claude Code truncates listing at 1,536 |
| `name` | **≤ 64 chars**, `a-z0-9-`, no `--`, **must equal the folder name** | Portable spec |
| Reference depth | **one level** from `SKILL.md` | Spec guidance; avoid nested chains |

Practical targets: `AGENTS.md` **≤ 100 lines**; each rule file **≤ 150 lines**; total rule content
**≤ 3,000 tokens**.

## 5. Frontmatter portability

**Safe everywhere (the portable six):** `name`, `description`, `license`, `compatibility`, `metadata`,
`allowed-tools`.
- `metadata` must be a map of **string → string**.
- Antigravity documents only `name` (optional, defaults to the folder name) and `description`
  (required). The others are ignored there — safe but ineffective.
- Claude Code's strictest path (claude.ai upload / Skills API) **hard-errors** on any key outside those
  six, so staying inside them can never break a build even though Claude Code itself tolerates more.

**Never use in a shared file:** `disable-model-invocation`, `user-invocable`, `paths`, `context: fork`,
`agent`, `background`, `hooks`, `model`, `effort`, `shell`, `arguments`, `argument-hint`,
`when_to_use`, `disallowed-tools`, `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PROJECT_DIR}`,
`${CLAUDE_PLUGIN_ROOT}`, `$ARGUMENTS`, `!`cmd``, `@[label](path)`.

**Rule-file frontmatter** (Antigravity dialect, harmless elsewhere):

```yaml
---
name: 10-architecture
description: >-
  Module boundaries, the dependency rule, and when an architecture decision must be recorded.
trigger: always_on
---
```

`trigger: always_on` is for the short, universally relevant core — `00-project-protocol`,
`10-architecture`, `30-collaboration`, `40-git-workflow`, `50-security-safety`, each roughly ≤ 40 lines.
Use `trigger: model_decision` for stack or language detail (typically `20-code-standards`): Antigravity
then injects the description and reads the body only when relevant, protecting the 20,000-token budget.
A missing frontmatter or an unrecognised `trigger` value causes Antigravity to **discard the rule
silently**, so keep the key spelled exactly.

## 6. Where skills live, per host

| Host | Project | Global |
|---|---|---|
| Antigravity | `<root>/.agents/skills/` (`.agent/skills/` is legacy compat only) | `~/.gemini/config/skills/` · CLI: `~/.gemini/antigravity-cli/skills/` |
| Claude Code | `<root>/.claude/skills/` (and in any parent up to repo root) | `~/.claude/skills/` |
| Codex | `.agents/skills/` from cwd up to repo root | `~/.agents/skills/` |
| Cursor | `.agents/skills/` **and** `.cursor/skills/` | `~/.agents/skills/` **and** `~/.cursor/skills/` |
| DSH | unverified | `~/.dsh/skills/` (verified in practice) — bundled skills also ship in the app's `runtime/office-skills/` |

`~/.agents/skills/` is the closest thing to a universal user-level location (Codex, Cursor, and
Antigravity-compatible tooling). Claude Code needs its own copy.

Because the discovery sets differ, a project that must run on several hosts gets skills duplicated into
`.agents/skills/` **and** `.claude/skills/`. Keep the two copies identical — drift between them is a
real failure mode, so re-sync rather than hand-editing one.

**Give skills unique names.** Precedence rules conflict across hosts (the Agent Skills client guide says
project overrides user; Claude Code documents enterprise > personal > project; Codex does not merge
duplicates at all). Unique names make precedence irrelevant.

## 7. What is NOT portable — do not build on it

| Capability | Why it fails elsewhere |
|---|---|
| Slash commands | `/name`, `$name`, `/skill:name` differ per host. Never document a command as the only trigger — the description match is the portable one. |
| Hooks | Event names, payload casing (snake_case vs Antigravity's camelCase), decision vocabularies and config filenames all differ. Optional hardening only. |
| Subagents | Same concept, incompatible definitions (`.claude/agents/`, `.codex/agents/*.toml`, `.cursor/agents/*.md`). Never required for the core flow. |
| Background jobs, scheduled tasks, MCP | Not guaranteed. MCP is the most portable extension point, but DSH support is unverified. |
| Enforcement | **No host enforces rules.** Every mechanism is advisory context. Phrase rules as verifiable instructions ("run `npm test` before committing") and verify them in the workflow instead of assuming they bind. |

## 8. Ragged edges to state honestly

- Claude Code never lists `.agents/` as a skill location and documents that it ignores instruction files
  there. Applying that to skills is a strong inference, not an explicit statement — which is exactly why
  the `.claude/skills/` mirror is mandatory whenever Claude Code is a target host, not optional.
- Antigravity is absent from the official Agent Skills client showcase despite calling skills an open
  standard, and documents narrower frontmatter than the spec.
- DSH loads global skills from `~/.dsh/skills/<name>/SKILL.md` (verified in practice 2026-10-27); its
  project-level skill directory is undocumented, while its `SKILL.md` shape (name + description, catalog of
  summaries) and its reading of `AGENTS.md` are verified in practice.

When a layout choice depends on an unverified point, say so and let the user decide rather than
asserting it.
