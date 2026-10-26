---
name: project-charter
description: >-
  Use when the user says "khởi tạo dự án", "bắt đầu dự án", "setup project", "onboard dự án",
  "chuẩn hóa quy trình", "charter", or "làm việc với tôi như thế nào", or asks which skills a
  project should install — and whenever a repo has no AGENTS.md / .agents/ config, is inherited,
  or still has no charter before the first significant code change. Recons the repo, interviews
  the user about goals, architecture, code conventions and collaboration, then writes a committed
  Project Charter (root AGENTS.md, .agents/rules/, .agents/context/, CLAUDE.md bridge) and
  selects the project's skills from the local library, so every later session follows the same
  process and architecture.
license: MIT
metadata:
  version: "1.0.0"
  origin: skills-repo
  scope: global
---

# Project Charter

A **Project Charter** is the durable, committed agreement that makes every later AI session behave the
same way: same process, same architecture, same definition of done. This skill produces it and keeps it
true.

Without a charter, each new session re-invents conventions, drifts from the architecture, and asks
questions the repo could already answer. The charter is the single source of truth the agent reloads
instead of guessing.

## What this skill produces

| Artifact | Purpose | Committed? |
|---|---|---|
| `AGENTS.md` (repo root) | The constitution: non-negotiables + index. Read natively by Codex, Cursor, Antigravity, Copilot and DSH; Claude Code reaches it through the `CLAUDE.md` import. | Yes |
| `CLAUDE.md` (one line: `@AGENTS.md`) | Bridge so Claude Code reads the same constitution. | Yes |
| `.agents/rules/*.md` | Detailed always-on rules (flat, numbered). Auto-loaded by Antigravity; read on demand everywhere else. | Yes |
| `.agents/context/charter.md` | The interview answers: goal, architecture, conventions, working agreement. | Yes |
| `.agents/context/architecture.md` | Architecture of record + index of decisions. | Yes |
| `.agents/skills/<name>/` | Skills selected for this project. | **No** — vendored, gitignored |
| `.agents/skills/REGISTRY.md` + `.agents/skills.manifest.json` | Inventory + provenance of selected skills. | Yes |
| `.gitignore` entry | `.agents/skills/*` excluded except `REGISTRY.md` (third-party code is never committed). | Yes |

Read `references/project-layout.md` before writing anything, for exact paths, per-host discovery,
and the hard size limits.

## Hard rules

1. **Never ask what the repo can answer.** Recon first (Phase 0). Facts are your job, not the user's.
2. **One theme per round, recommended answer first.** Every question carries a default so "default
   everything" is a valid reply.
3. **No writing before approval.** Phase 2 ends with an explicit plan; you may not create, edit or
   delete project files until the user approves.
4. **Never overwrite silently.** If `AGENTS.md`, `.agents/`, or another agent's config exists, read it
   and propose a **merge**. Stop and ask before any overwrite.
5. **No secrets.** Never write credentials, tokens, connection strings, or `.env` values into any
   charter file. Refer to variable names only.
6. **Respect the limits.** `AGENTS.md` ≤ 100 lines; each rule file ≤ 24 KB; `.agents/rules/` flat — no
   nested folders; total always-on rules well under Antigravity's 20,000-token budget.
7. **Do not delete** files, folders, or skills without explicit confirmation of that exact path.
8. **Portable frontmatter only.** In any `SKILL.md` you write, use only `name`, `description`, `license`,
   `compatibility`, `metadata`, `allowed-tools`. Never `disable-model-invocation`, `paths`,
   `context: fork`, `agent`, `hooks`, `argument-hint`, `when_to_use`, or `${CLAUDE_*}` substitutions.
   The one exception: `.agents/rules/*.md` also carries Antigravity's `trigger:` key (see
   `references/project-layout.md` §5).

## Phase 0 — Recon (no questions yet)

Detect, then report in two lines. Never ask about anything found here.

1. **Mode**
   - *Re-charter*: `.agents/context/charter.md` exists → jump to "Re-charter / drift check" below.
   - *Inherited*: source files **or** an existing agent config (`AGENTS.md`, `CLAUDE.md`, `.claude/`,
     `.cursor/rules/`, `.cursorrules`, `.github/copilot-instructions.md`, `GEMINI.md`) exist, but there is
     no charter → run the interview and **merge** that config; never overwrite it.
   - *Greenfield*: no manifest, no source files, no agent config.
   - `.git` alone does not decide the mode: a repo with history can still be greenfield for this purpose.
2. **Hosts in play.** Check which host config this machine has and ask (once, in Phase 1) which hosts must
   work: Antigravity (`~/.gemini/config`), Claude Code (`~/.claude`), Codex (`~/.codex` / `~/.agents`),
   Cursor (`~/.cursor`), DSH (`~/.dsh`). If a host directory cannot be read (sandbox), ask instead of
   probing. This decides whether the `CLAUDE.md` bridge and the `.claude/skills/` mirror are needed.
3. **Stack.** Manifests (`package.json`, `pom.xml`, `build.gradle*`, `pyproject.toml`,
   `requirements.txt`, `Cargo.toml`, `go.mod`, `*.csproj`, `Gemfile`, `composer.json`, `pubspec.yaml`),
   lockfiles, framework configs, entry points (`src/main/`, `main.*`, `app/`, `cmd/`), tooling
   (`.eslintrc*`, `.prettierrc*`, `tsconfig.json`, `Makefile`, `Dockerfile`, `.github/workflows/`),
   test layout (`tests/`, `*_test.go`, `*.spec.ts`, `pytest.ini`).
4. **Existing knowledge.** `README.md`, `PROGRESS.md`, `docs/`, `docs/adr/`, `schema.sql`, existing rules
   files, plus any `*ARCHITECTURE*.md`, `*_FLOW.md` or `*_PROTOCOL*.md` the project has. These become the
   source for pre-filled interview answers and for `.agents/context/architecture.md` — never re-ask what
   they state.
5. **Git truth.** `git remote -v`, default branch, `git config user.name` / `user.email`, recent
   `git log --oneline -10` for commit-message style.
6. **Skills library.** `SKILLS_HOME` is the `SKILLS_HOME` environment variable when it is set; otherwise
   ask once in round 5 — never guess a path. Confirm it holds `skills/` and `_external/`, and list the
   global skill directories that exist. Needed for Phase 2's skill selection.

## Phase 1 — Interview

Full question bank, defaults and phrasing: **read `references/interview.md`**.

Protocol:

- Ask by **theme, 5 rounds maximum**: (1) goal & scope, (2) architecture, (3) code & quality,
  (4) working agreement, (5) skills & hosts.
- Within a round, present the questions as a numbered list, each with your **recommended default**
  first and the evidence behind it ("detected `pom.xml` → Java 21 + Maven").
- The user may answer `default all`, answer selectively, or ask for one-question-at-a-time mode.
- **Skip anything already answered** by Phase 0 or by an earlier answer.
- Write the user's language. If they write Vietnamese, ask in Vietnamese.
- A round is done when every question in it has an answer *or* an accepted default. Do not proceed on
  a guess that materially changes the architecture — mark it as an open question instead.

Keep the transcript short: confirm, don't lecture. Restate a round's outcome in ≤ 5 bullets before the
next round.

## Phase 2 — Charter plan + skill bundle (approval gate)

Present both, then **stop and wait**. Do not write in this turn.

### 2a. Charter plan

```
## Charter plan: <project name>
Mode: greenfield | inherited | re-charter     Hosts: <list>
Will create:
  - AGENTS.md                        (~N lines)
  - CLAUDE.md                        (only if Claude Code is a target)
  - .agents/context/charter.md
  - .agents/context/architecture.md
  - .agents/rules/00-project-protocol.md
  - .agents/rules/10-architecture.md
  - .agents/rules/20-code-standards.md
  - .agents/rules/30-collaboration.md
  - .agents/rules/40-git-workflow.md
  - .agents/rules/50-security-safety.md
  - .agents/skills/REGISTRY.md, .agents/skills.manifest.json
Will modify: .gitignore (.agents/skills/* + !.agents/skills/REGISTRY.md, .claude/skills/)
Will NOT touch: <existing docs, existing config, source code>
```

Only generate the rule files that carry project-specific content. If a rule would only restate a
global rule, omit it and point to the global rule instead — the charter holds **deltas**, not a copy of
the universal policy. Templates: `references/templates.md`.

Also list **Blocking open questions** carried over from Phase 1. If that list is not empty, stop and
resolve those items with the user now: a plan approved over an unresolved blocking question is not
approval, and carrying it into Phase 3 produces a charter nobody agreed to.

### 2b. Skill bundle

Follow `references/skill-selection.md`. Produce a table with **every row justified by evidence**, split
into three actions:

| Skill | Why | Evidence | Source / License | Action |
|---|---|---|---|---|
| `react-patterns` | core UI stack | 84 `.tsx`, `next.config.ts` | ECC / MIT | **Install** |
| `postgres-patterns` | DB present | `schema.sql`, `postgres` dep | ECC / MIT | **Install** |
| `playwright` | E2E expected | user asked for browser tests | local repo | **Install** |
| `terraform-patterns` | not used | no `.tf` files | ECC / MIT | Skip |

Separate them clearly:

- **Install now** — already present in the local library (`skills/` or `_external/`); will be copied on
  approval.
- **Recommend downloading** — not in the library. Give the exact source repo (trusted list only),
  license, pinned commit, the reason, and the command the user can run. Never download or run an
  unapproved source.
- **Skip** — considered and rejected, with the reason. This section prevents re-litigating later.

Budget: default **≤ 10 project skills**. Everything else stays in the library and is listed in the
router section of `AGENTS.md` as available-on-demand.

### 2c. Ask

End with one question: approve, adjust, or approve-with-changes. Then wait for explicit approval. One
keyword set for the whole skill: `duyệt`, `ok`, `làm đi`, `approve`, `lgtm`, `proceed`, `go ahead` — plus
whatever the user chose in Phase 1 (Q4.3). Anything else, including "chắc là ổn", is not approval.

## Phase 3 — Write

Write exactly what was approved. Nothing more.

- **`AGENTS.md`** — constitution, ≤ 100 lines, no YAML frontmatter: identity + stack, the plan gate and
  definition of done, 5–10 non-negotiables, an index pointing to `.agents/rules/` and
  `.agents/context/`, the skill router, and the session-restart phrase.
- **`CLAUDE.md`** — only when Claude Code is a target host, and it is exactly one line: `@AGENTS.md`. No
  comment, no heading, no extra text. Never a symlink (Edit/Write refuse to write through symlinks, and
  Windows clones without `core.symlinks` break them).
- **`.agents/rules/*.md`** — flat, numbered, one topic each. Frontmatter `name` + `description`, plus
  `trigger: always_on` for the core protocol and `trigger: model_decision` for stack-specific detail, so
  Antigravity's always-on token budget is not exhausted. Other hosts ignore this frontmatter.
- **`.agents/context/charter.md`** — the interview answers, dated, with an "Open questions" section that
  stays honest about what is still undecided.
- **`.agents/context/architecture.md`** — architecture of record, module boundaries and dependency
  rules, plus a decision index. If the project already has architecture docs, **link** them rather than
  duplicating; this file is the index, not a second copy.
- **Skills** — copy approved skills into `.agents/skills/<name>/`, and mirror into
  `.claude/skills/<name>/` when Claude Code is a target (Claude Code does not read `.agents/skills/`).
- **Existing config** — when `AGENTS.md`/`CLAUDE.md` already existed, write the approved merge: move
  anything that lived only in `CLAUDE.md` into `AGENTS.md`, then reduce `CLAUDE.md` to the import.
- **`.gitignore`** — ignore the folder's contents, not the folder: `.agents/skills/*`,
  `!.agents/skills/REGISTRY.md`, and `.claude/skills/` when the mirror is used. Run
  `git ls-files .agents/skills .claude/skills` first; if anything there is already tracked, stop and ask.
- **Manifest + registry** — write provenance for each installed skill.
- **Commit** — the charter is committed, but never silently: list the files you propose to commit, and
  commit only when the user asks (Q4.5).

## Phase 4 — Validate (gate)

Resolve this skill's own directory (the folder holding this `SKILL.md`) and run:

```
python3 "<skill-dir>/scripts/validate_charter.py" <project-root> [--claude]
```

On Windows without `python3`, use `py -3`. Requires Python ≥ 3.7, standard library only. Pass `--claude`
whenever Claude Code is a target host, so the bridge and the mirror are enforced rather than assumed.
Never hardcode `python skills/...`: the current directory is usually the project, not `SKILLS_HOME`.

Then confirm, and report any failure honestly rather than declaring success:

- [ ] `AGENTS.md` exists, ≤ 100 lines, no frontmatter, references only files that exist.
- [ ] `CLAUDE.md`, if present, is exactly one line `@AGENTS.md` — not a symlink, no comment.
- [ ] `.agents/rules/` is flat; every file ≤ 24 KB with valid `name` + `description`.
- [ ] `.agents/context/charter.md` has no "Open questions" left that block implementation.
- [ ] Every installed skill has `SKILL.md`, `name` equal to its folder name, and a manifest row.
- [ ] No secrets, tokens, absolute personal paths, or credentials anywhere in the charter.
- [ ] `.gitignore` ignores `.agents/skills/*` but not `REGISTRY.md`; the charter itself is not ignored.
      Confirm with `git check-ignore -v` — a global excludes file that ignores `.agents/` defeats the
      charter silently, and the validator names the file and line that matched.
- [ ] Total always-on rule content is comfortably under 20,000 tokens.

Detailed checklist: `references/validation.md`.

## Phase 5 — Handoff

Report in the user's language:

1. What was created, with sizes.
2. The skill set installed, and what was recommended for download.
3. **The working agreement in 5 bullets** — how future sessions will behave.
4. The restart phrase for a new session.

Phrase to give the user, adapt to their language:

> **"Đọc `AGENTS.md`, `.agents/context/charter.md` và `.agents/context/architecture.md` rồi tiếp tục công việc theo đúng charter."**

## Phase 6 — Ongoing enforcement (every later session)

This is the part that delivers the user's actual goal — identical process across sessions.

On entering a project **that has a charter**:

1. Read `AGENTS.md`, `.agents/context/charter.md`, `.agents/context/architecture.md` before the first
   code change.
2. Read only the rule files whose topic the task touches.
3. Follow the plan gate: plan → approval → implement → verify → report.
4. **Drift check.** If the request contradicts the charter (wrong layer, new dependency, changed
   interface, a forbidden pattern), say so explicitly and offer the choices: adjust the work, or update
   the charter. Never silently deviate.
5. **Architecture change → record it first.** Any change to a module boundary, public interface, data
   schema, or dependency direction requires a decision entry in `.agents/context/architecture.md`
   (or an ADR under `docs/adr/` if the project uses them) *before* the code change.
6. **Keep the charter true.** After a feature that changes conventions, update the charter in the same
   work session. A stale charter is worse than none.
7. Note durable mistakes in the global `mistake-memory` ledger when the user corrects you.

## Re-charter / drift check

When a charter already exists, do **not** run the full interview. Instead:

1. Read the charter and the rules.
2. Verify them against reality: do the listed commands exist and pass? Do the referenced paths exist? Do
   the module boundaries match the code? Are the installed skills still present?
3. Report drift as a short list, then ask a **targeted** set of questions — only about the drifted items.
4. Propose a merge plan and wait for approval before editing.

## Anti-patterns

- Asking the user for the framework when `package.json` answers it.
- Dumping a 400-line `AGENTS.md` — overflow is the enemy; Codex truncates at 32 KiB, and long files are
  re-read every session.
- Copying all global rules into the project instead of the project-specific deltas.
- Installing 30 skills "just in case" — every skill competes for the model's attention.
- Writing a charter that restates the code (`function X on line 12`) instead of the rules
  (`services must not import from controllers`).
- Declaring the gate passed without running the validator.
- Documenting a slash command as the only way to trigger this skill: command syntax differs on every
  host. The description match is the portable trigger.
- Ignoring `.agents/skills/` as a whole and expecting `REGISTRY.md` to stay committed — Git cannot
  re-include a file inside an excluded directory.
- Writing `CLAUDE.md` as the import plus commentary — the file is exactly `@AGENTS.md`.

## Reference files

| Read this | When |
|---|---|
| `references/interview.md` | Phase 1 — the question bank, defaults and phrasing |
| `references/project-layout.md` | Before writing: exact paths, per-host discovery, size limits |
| `references/skill-selection.md` | Phase 2b — how to pick and install skills |
| `references/templates.md` | Phase 3 — the file templates to fill in |
| `references/validation.md` | Phase 4 — the full validation checklist |
| `scripts/validate_charter.py` | Phase 4 — automated structural validation |
