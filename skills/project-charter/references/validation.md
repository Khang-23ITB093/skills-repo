# Validation Checklist

Run this as the Phase 4 gate. It is a **gate, not a formality** — report failures honestly instead of
declaring success. Automated checks: `scripts/validate_charter.py`.

## A. Existence and shape

- [ ] `AGENTS.md` exists at the project root, has **no YAML frontmatter** (first line is a heading).
- [ ] `AGENTS.md` is **≤ 100 lines** (hard cap 32 KiB for Codex truncation).
- [ ] `CLAUDE.md` exists **only if** Claude Code is a target host, and its content is the `@AGENTS.md`
      import. It is a **regular file, not a symlink**. No `CLAUDE.local.md` exists.
- [ ] `.agents/context/charter.md` exists and every interview section is filled.
- [ ] `.agents/context/architecture.md` exists with the module/dependency rule.
- [ ] `.agents/skills/REGISTRY.md` and `.agents/skills.manifest.json` exist.

## B. Rules

- [ ] `.agents/rules/` is **flat** — no subdirectories (Antigravity ignores nested dirs).
- [ ] Every rule file is **≤ 24 KB**.
- [ ] Every rule file starts with valid YAML frontmatter containing `name` and `description`.
- [ ] `trigger:` values are exactly `always_on`, `model_decision`, `glob`, or `manual` — a typo causes
      Antigravity to discard the file **silently** (there is no error to notice later).
- [ ] `always_on` is limited to the short, universally relevant core (`00`, `10`, `30`, `40`, `50`, each
      ≈ ≤ 40 lines); stack or language detail (`20-code-standards`) uses `model_decision` to protect the
      20,000-token budget.
- [ ] Total rule content is well under budget — target ≤ 3,000 tokens.
- [ ] Rule files contain **project deltas**, not copies of the global rules.

## C. Skills

- [ ] Every installed skill folder contains `SKILL.md`.
- [ ] Frontmatter `name` **equals the folder name**.
- [ ] Frontmatter uses portable keys: `name`, `description`, `license`, `compatibility`, `metadata`,
      `allowed-tools`. Non-portable keys in a **vendored** skill are a warning, not a failure — editing a
      vendored skill is forbidden, so report them and move on.
- [ ] No skill file contains `${CLAUDE_*}` or `$ARGUMENTS` in an executable block.
- [ ] When Claude Code is a target, each skill is mirrored in `.claude/skills/<name>/` and the copies are
      **byte-identical** (the validator compares hashes).
- [ ] Daily-skill count is **≤ 10** — a hard cap, so the validator fails above it.
- [ ] Every installed skill has a manifest row, and the manifest matches what is on disk in both
      directions.
- [ ] No installed skill's `scripts/` contains anything unrelated to its stated purpose.
- [ ] External skills appear under "recommended, not installed" — not as installed.
- [ ] Selecting **zero** project skills is allowed (global-only answer): the skills directory may be
      absent, and the registry is then expected to be absent too.
- [ ] Install is **verified**, not smoke-tested: validator passes, copies are byte-identical, and the
      skills appear in the host's catalog from the next session (most hosts snapshot at session start).

## D. Safety

- [ ] No secrets: scan the charter for credential **assignments** (`API_KEY=…`, `TOKEN=…`, `SECRET=…`,
      `PASSWORD=…` with a value), `sk-…`, `AIza…`, `ghp_…`, `Bearer …`, `BEGIN … PRIVATE KEY`, and
      connection strings carrying `user:pass@`. Bare words like "token" or "password" in prose are fine —
      variable *names* are exactly what the charter should contain.
- [ ] No absolute personal paths (`C:\Users\<name>\...`, `/home/<name>/...`) in committed charter files.
- [ ] `.gitignore` ignores `.agents/skills/*` and re-includes `!.agents/skills/REGISTRY.md` (plus
      `.claude/skills/` when used) — never the directory itself.
- [ ] The charter files are **not** ignored — verify with real Git, not by eye:
      `git check-ignore -v AGENTS.md .agents/skills/REGISTRY.md .agents/context/charter.md`.
      A **global** excludes file (`~/.gitignore_global`) that ignores `.agents/` silently defeats the
      whole charter on that machine. The validator names the file and line that matched: fix the global
      file, or add an explicit `!.agents/` re-include to the project `.gitignore`.
- [ ] No file was deleted or overwritten without explicit confirmation.

## E. Consistency

- [ ] Every path referenced from `AGENTS.md` actually exists.
- [ ] The commands written in `AGENTS.md` (build/test/lint) exist and run.
- [ ] The architecture rule does not contradict the actual folder structure.
- [ ] `.agents/context/charter.md` has no **Open questions** that block implementation.
- [ ] `REGISTRY.md` and `skills.manifest.json` agree with what is on disk.
- [ ] The working agreement in `30-collaboration.md` matches what the user actually said in the
      interview — re-read the answers rather than trusting your summary.
- [ ] Always-on rule content stays under the token budget — the validator estimates bytes / 4 and fails
      past 20,000 tokens; aim for ≤ 3,000.
- [ ] No unfilled `<placeholder>` is left in a committed charter file — the validator lists the files
      that still look templated.
- [ ] The charter is listed for the user's commit decision: name the files (`AGENTS.md`,
      `.agents/context/`, `.agents/rules/`, `.agents/skills/REGISTRY.md`, `.agents/skills.manifest.json`)
      and commit only when they say so.

## F. Report

State the result as a short table, then either hand off (Phase 5) or list what must be fixed. Never
mark the gate passed while a box is unchecked; instead say which items failed and what you propose.

```
| Check | Result |
|---|---|
| AGENTS.md shape | PASS (78 lines, no frontmatter) |
| Rules flat + sizes | PASS (6 files, max 3.1 KB) |
| Skills + manifest | PASS (4 daily, all mirrored) |
| No secrets | PASS |
| Referenced paths exist | FAIL — `.agents/rules/60-api.md` referenced but missing |
```

## G. Later sessions — drift check

Not a one-time gate. Re-run the relevant parts when:

- a new dependency, module, or service appears;
- a build/test command changes;
- the user corrects the agent's behaviour (record it, then update the charter);
- a session finds the charter contradicts the code.

Report drift as a short list and propose a minimal merge. Never silently edit the charter, and never
leave a charter that you know is false.
