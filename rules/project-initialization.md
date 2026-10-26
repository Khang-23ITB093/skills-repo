# Project Initialization Routine

This rule governs the mandatory behavior of the agent when entering a new workspace or project for the
first time. It is the entry point that hands off to the **`project-charter`** skill.

## 1. Project Analysis & Scaffold Check

When you start a conversation in a project, check whether a **charter** exists:

- `.agents/context/charter.md` — the charter's own record, and the only reliable marker; and
- `AGENTS.md` at the workspace root (always present in a chartered repo, but also common elsewhere).

`AGENTS.md` alone, `.claude/` alone, or a `GEMINI.md` / `.cursor/rules/` written by another tool are **not**
a charter — they are an inherited configuration. Treat the project as unchartered, run the skill, and let
it merge those files instead of overwriting them.

**If no charter exists**, do not improvise a scaffold. Invoke the **`project-charter`** skill, which runs
the full flow: recon → interview → approved plan → write → validate → handoff. Creating `AGENTS.md` and
`.agents/` by hand, without the interview, produces a file that documents nothing the user agreed to.

**If a charter exists**, read it before the first code change: `AGENTS.md`,
`.agents/context/charter.md`, `.agents/context/architecture.md`, then only the rule files whose topic
the task touches.

## 2. Capability & Tech Stack Analysis

Analyze the stack (look for `pom.xml`, `package.json`, `build.gradle`, `requirements.txt`,
`pyproject.toml`, `Cargo.toml`, `go.mod`, …) and the tooling, git state, and existing docs. This
analysis **pre-fills** the charter interview — it is never a reason to ask the user something the repo
already answers.

## 3. Skill & Rule Selection

Determine which globally available skills and rules the project actually needs, justify each choice
with repo evidence, and present the bundle for approval before installing anything. The full procedure
is in `skills/project-charter/references/skill-selection.md`.

Never install the whole library into a project. Every installed skill competes for the model's
attention on every request.

## 4. Git Hygiene

- **The charter is committed** — `AGENTS.md`, `CLAUDE.md`, `.agents/rules/`, `.agents/context/`,
  `.agents/skills/REGISTRY.md`, `.agents/skills.manifest.json` — because that shared knowledge is what
  makes the process reproducible for the whole team. Say which files you propose to commit and let the
  user decide when; never commit silently (the skill's Q4.5 answer governs).
- **Do not commit vendored skills**: ignore the *contents* of the skills folders, never the folders
  themselves:

  ```gitignore
  .agents/skills/*
  !.agents/skills/REGISTRY.md
  .claude/skills/
  ```

  A bare `.agents/skills/` also hides `REGISTRY.md`, and Git cannot re-include a file whose parent
  directory is excluded — the registry would silently never be committed. Third-party code has its own
  license terms and drifts from upstream; `skills.manifest.json` records what to reinstall.

> Superseded: the earlier instruction to ignore the whole `.agents/` directory. Ignoring the charter
> loses the architecture and working agreement for everyone who clones the repo.

Always ensure the project carries the necessary context — rules, architecture and skills — for any
agent to continue the same way it started.
