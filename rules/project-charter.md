# Project Charter Rule

## MANDATORY — Always-On Directive for All Projects

Every project must have a **Project Charter** before implementation work begins. The charter is the
durable agreement that makes each session behave the same way — same process, same architecture, same
definition of done.

Use the `project-charter` skill to create or verify it.

---

## 1. Entering a project

At the start of work in any project, determine which case applies:

| State | Required action |
|---|---|
| No `.agents/context/charter.md` | **Run the `project-charter` interview** (greenfield or inherited mode). An `AGENTS.md`, `.claude/`, `GEMINI.md` or `.cursor/rules/` written by another tool marks the repo as *inherited*: run the skill and merge, never overwrite. |
| Charter present | **Read it first**: `AGENTS.md`, `.agents/context/charter.md`, `.agents/context/architecture.md`. Then only the rule files whose topic the task touches. |
| Charter present but contradicts the code | Report the drift and propose a minimal merge. Do not silently follow the stale file, and do not silently ignore it. |

Never begin a non-trivial code change in a project with no charter, and never ask questions the repo
can already answer — recon first.

---

## 2. Hard constraints

- **No writing before approval.** Present the charter plan and the skill bundle, then stop. Create,
  edit and delete nothing until the user explicitly approves.
- **Charter holds deltas.** Project-specific rules only. Universal policy stays in the global rules —
  do not copy it into the project.
- **Never overwrite silently.** If `AGENTS.md`, `.agents/`, `.claude/`, or another agent's config
  already exists, propose a merge and wait.
- **No secrets** in any charter file. Reference environment variable names only.
- **Respect the limits.** `AGENTS.md` ≤ 100 lines (hard truncation at 32 KiB); each rule file ≤ 24 KB;
  `.agents/rules/` flat; always-on rules well under 20,000 tokens.
- **Vendored skills are never committed.** Gitignore the *contents* of `.agents/skills/` (and
  `.claude/skills/`), never the directory itself:

  ```gitignore
  .agents/skills/*
  !.agents/skills/REGISTRY.md
  .claude/skills/
  ```

  Excluding `.agents/skills/` wholesale would also exclude `REGISTRY.md`, which Git cannot re-include
  from inside an excluded directory. The charter, the registry and `skills.manifest.json` are committed.

---

## 3. Portability requirements

The charter must work on Antigravity, Claude Code, Codex, Cursor and DeepSeek Harness.

- Always-on guidance goes in root **`AGENTS.md`** — the only file every host reads natively.
- When Claude Code is a target, add **`CLAUDE.md` containing exactly `@AGENTS.md`**. Never a symlink,
  and never `CLAUDE.local.md` (its presence suppresses `AGENTS.md`).
- Detail goes in `.agents/rules/*.md` (Antigravity auto-loads; other hosts read on demand via the
  `AGENTS.md` index).
- Skills are installed to `.agents/skills/` and, when Claude Code is a target host, mirrored to
  `.claude/skills/` — Claude Code does not read `.agents/skills/`.
- Frontmatter uses only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` in
  `SKILL.md` files; `.agents/rules/*.md` additionally carries Antigravity's `trigger:` key. Never
  Claude-only keys, and never `${CLAUDE_*}` or `$ARGUMENTS` in executable blocks.
- Never document a slash command as the only trigger — command syntax differs per host; the
  description match is the portable trigger.

---

## 4. Ongoing enforcement

- **Drift check.** If a request contradicts the charter (wrong layer, new dependency, changed
  interface, a forbidden pattern), surface it and offer choices: adjust the work, or update the
  charter. Never deviate silently.
- **Architecture change → record first.** A change to a module boundary, public interface, data
  schema, or dependency direction requires an entry in `.agents/context/architecture.md` (or an ADR)
  **before** the code change.
- **Keep the charter true.** Update it in the same session as the change that made it stale.
- **Record corrections.** When the user corrects a recurring mistake, add it to the `mistake-memory`
  ledger and update the relevant rule.
