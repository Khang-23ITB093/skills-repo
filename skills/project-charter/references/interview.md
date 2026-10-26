# Interview Question Bank

Question bank for Phase 1 of `project-charter`. Read this when conducting the interview.

## Protocol

- **Explore before asking.** Every question below has a "detect first" note. If Phase 0 settled it,
  pre-fill it and do not ask — just state the finding and let the user correct it.
- **5 rounds maximum**: goal & scope → architecture → code & quality → working agreement → skills.
- **Recommended answer first, with its evidence.** Phrase each question so that "yes" or "default"
  accepts your recommendation.
- **Round, then confirm.** Restate the round's outcome in ≤ 5 bullets before moving on.
- **Stop at what matters.** If a question would not change a single file or decision, drop it.
- **Anchor to a file.** Every answer must land in `charter.md`, a rule file, or `AGENTS.md`. If an
  answer lands nowhere, you asked the wrong question.
- If the user says "hỏi từng câu một" / "one at a time", switch to presenting **one question per
  message**, still with the recommendation first.
- If the user says "default hết" / "all defaults", accept every recommendation, list them explicitly in
  the confirmation, and continue — never accept a default that contradicts something they already said.

---

## Round 1 — Goal & scope

**Q1.1 — One-sentence objective.**
Detect first: `README.md`, existing docs, the user's opening message.
> What is this project for, in one sentence?
> Recommended: `<derived from README>` — this becomes the first line of `AGENTS.md` and `charter.md`.

**Q1.2 — Success criteria — how will we know it worked?**
> Recommended: `<derived>`, or name 1–3 concrete, checkable outcomes.

**Q1.3 — Project type.**
Options: `web API` · `desktop app` · `mobile` · `CLI tool` · `library` · `fullstack` · `data/ML pipeline`
Detect first: manifests, entry points, UI framework presence.

**Q1.4 — Explicitly out of scope.**
> What must this project **not** become? (This is the cheapest way to prevent scope drift.)
> Recommended: `<none stated>` — but always ask. An empty answer is a real answer.

**Q1.5 — Priority / deadline pressure.**
> Ship speed vs. correctness vs. learning? Recommended: `<balanced>`.

---

## Round 2 — Architecture

**Q2.1 — Architectural style.**
Options: `layered` · `hexagonal/ports-adapters` · `clean` · `modular monolith` · `microservices` ·
`event-driven` · `MVC` · `none yet`
Detect first: top-level folders (`controllers/`, `services/`, `domain/`, `adapters/`), existing
architecture docs.
> Recommended: `<inferred from the folder structure>`, because `<evidence>`.

**Q2.2 — Module boundaries and the dependency rule.**
> Which layer may import which? Name the forbidden direction.
> Recommended: `<e.g. "controllers → services → repositories; repositories never import services">`.

**Q2.3 — Data & persistence.**
> Database, schema owner, migration policy, and whether data is disposable during development.
> Detect first: `schema.sql`, migrations folder, ORM config, connection strings (names only).
> Recommended: `<detected>`.

**Q2.4 — Protocols, integrations, and hard technical constraints.**
> Anything with a fixed contract: network protocol, ports, MTU, auth scheme, message format, external
> API, hardware.
> Detect first: existing `*_FLOW.md`, `*_PROTOCOL.md`, dependency list.
> Recommended: `<detected or "none">`.

**Q2.5 — Where is architecture written down?**
> Recommended: `.agents/context/architecture.md` as the index, plus `docs/adr/` for decisions if the
> project already uses ADRs. If architecture docs already exist, link them — do not duplicate.

**Q2.6 — Frozen / non-negotiable interfaces.**
> What must never change silently? (public API, DB schema, file format, wire protocol.)
> Recommended: `<none>`.

---

## Round 3 — Code & quality

**Q3.1 — Language, version, build tool.**
Detect first: manifests and lockfiles. Pre-fill; just confirm.

**Q3.2 — The canonical commands.**
Detect first: `package.json` scripts, `Makefile`, CI workflow steps, `pom.xml` plugins.
> Build / test / lint / typecheck — the exact commands to run.
> Recommended: `<detected commands>`. **Required** — it goes into `AGENTS.md`.

**Q3.3 — Definition of Done.**
> What must be true before a task is finished? (build passes, tests added, lint clean, docs updated,
> manual smoke test performed.)
> Recommended: `build + tests pass, lint clean, no new warnings, tests added for new behaviour`.

**Q3.4 — Test strategy and coverage bar.**
Options: `unit only` · `unit + integration` · `+ E2E` · `manual for now`
> Recommended: `<detected runner>`, unit + integration; coverage `<measure and hold, do not regress>`.

**Q3.5 — Style rules.**
Detect first: `.editorconfig`, `.prettierrc*`, `.eslintrc*`, `ruff.toml`, `checkstyle.xml`.
> Formatter, naming, error-handling style, logging approach.
> Recommended: `<detected>`; where none exists, propose one and write it down.

**Q3.6 — Dependency policy.**
> When may a new dependency be added? Who approves it?
> Recommended: `only with approval; prefer the standard library; no abandoned packages`.

**Q3.7 — Forbidden patterns.**
> What is banned in this codebase? (e.g. god classes, silent catches, raw SQL in controllers,
> `any`, global mutable state, blocking the UI thread.)
> Recommended: `<stack-typical list>` — this list is the most valuable part of the charter.

**Q3.8 — Measurable constraints.**
> Any hard numbers with a command that checks them? (response time, bundle size, coverage %.)
> Rule: a number without a command is an aspiration, not a constraint. Recommended: `none yet`.

---

## Round 4 — Working agreement (how to work with me)

This round is the heart of the user's request. Ask all of it.

**Q4.1 — Language and verbosity.**
> Which language should I reply in, and how detailed?
> Recommended: `<same language the user writes>` · concise, tables over prose, no filler.

**Q4.2 — The approval gate.**
Options: `always plan first, wait for approval` · `plan only for large/architectural changes` ·
`just do it, report after`.
> Recommended: **always plan first** — plan → approval → implement → verify → report.

**Q4.3 — Approval keywords.**
> Which exact words count as approval?
> Recommended: `duyệt`, `ok`, `làm đi`, `approve`, `lgtm`, `proceed`, `go ahead`. Anything else —
> including "chắc là ổn" — is **not** approval.

**Q4.4 — Autonomy threshold.**
> What may I decide alone, and what must I ask about?
> Recommended: decide alone on internal implementation details, formatting, and test structure; **ask
> first** about architecture, public interfaces, schemas, new dependencies, and deleting things.

**Q4.5 — Git workflow.**
Detect first: `git config user.name/user.email`, existing commit-message style, branches.
> Author identity, commit convention, branch naming, when to commit, whether to push.
> Recommended: the user's own name/email; Conventional Commits; commit only when asked or at a
> verified milestone; **never push without asking**; no AI attribution trailers or watermarks.

**Q4.6 — Command permissions.**
> What may I run without asking? (installs, migrations, servers, network calls, containers.)
> Recommended: read-only and test commands freely; ask before installing anything, running migrations,
> starting long-running servers, or any command that changes data.

**Q4.7 — Destructive operations and secrets.**
> Recommended: **never** delete files/folders/branches without explicit confirmation of that exact
> path; **never** hardcode secrets, print them, or commit `.env`; refer to environment variable names
> only.

**Q4.8 — Model / cost policy (optional).**
> Should cheap tasks use a cheap model? Is there a cross-review step for risky changes?
> Recommended: `<skip unless the user has a routing skill installed>`.

**Q4.9 — End-of-task report format.**
> What should the final message contain?
> Recommended: what changed (files), how it was verified (exact commands + result), what is left, and
> what I need from you.

---

## Round 5 — Skills & hosts

**Q5.1 — Which hosts must this project work on?** (multi-select)
Options: `Antigravity` · `Claude Code` · `Codex` · `Cursor` · `DeepSeek Harness` · `other`
> This decides the `CLAUDE.md` bridge and the `.claude/skills/` mirror. Recommended: all hosts the user
> actually uses. **Required** before writing anything.
> Detect first: which host config directories exist on this machine.

**Q5.2 — Should I select project skills?**
Options: `yes — propose, then wait for my approval` · `yes — install obvious matches automatically` ·
`no, keep global only`.
> Recommended: **propose, then wait for approval for everything.**

**Q5.3 — Context budget.**
> How many project skills is too many?
> Recommended: ≤ 10 active project skills. Everything else stays in the library, available on request.

**Q5.4 — Download policy.**
> May I recommend skills from the internet, or use only the local library?
> Recommended: local library first; **recommend** external ones with source + license + pinned commit,
> and never download without explicit approval.

**Q5.5 — Which skill sources are trusted?**
> Recommended default trusted list: `anthropics/skills`, `obra/superpowers`, `addyosmani/agent-skills`,
> `mattpocock/skills`, `affaan-m/ECC`, plus the user's own `SKILLS_HOME` repo.

**Q5.6 — Where is the skills library?** (only when the `SKILLS_HOME` environment variable is unset)
> Ask for the one path, echo it back, and use it for the rest of the session. Never guess, and never
> write the path into a committed file — the manifest and registry record `env:SKILLS_HOME` instead.

---

## Closing the interview

Summarise in ≤ 10 bullets: objective, stack, architecture rule, canonical commands, definition of done,
top forbidden patterns, approval gate + keywords, git rules, target hosts, chosen skills.

Then ask one confirmation question. **This is not the approval gate** — the only approval gate is
SKILL.md Phase 2c, where the user also sees the file plan and the skill bundle:

> "Đây là những gì tôi hiểu. Có gì sai hoặc thiếu không? Nếu đúng hết, tôi sẽ trình plan file + skill
> bundle để bạn duyệt."

An answer here is a correction round, never permission to write. Continue to the Phase 2 plan and stop
there.
