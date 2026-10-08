# Destructive Operations Safety Rule

## MANDATORY — Always-On for Every Project

**Context:** The user has experienced a catastrophic data loss event where the AI agent deleted entire directories on their E: drive. This rule exists to prevent any recurrence of such destructive actions.

---

## NEVER perform the following without EXPLICIT user confirmation:

### File & Directory Deletion
- **NEVER** run `rmdir`, `Remove-Item`, `rm`, `del`, `rd`, or any equivalent delete command.
- **NEVER** delete files or folders as a side-effect of another operation (e.g., `mvn clean`, `git clean -fd`, `npm run clean`) unless you have ALREADY warned the user what will be deleted.
- **NEVER** use wildcards (`*`, `**`, `*.ext`) in delete operations without showing the user the exact list of matched files first.

### Overwrite & Replace
- **NEVER** overwrite existing files in bulk (e.g., via `cp -f`, `robocopy /MIR`, `rsync --delete`) without explicitly showing what will be overwritten.
- **NEVER** use `--force` or `-f` flags with destructive commands without confirmation.

### Drive-Level & Filesystem Operations
- **NEVER** operate on any whole drive root (e.g., `C:\`, `D:\`, `E:\`) without the user explicitly and unambiguously asking for it.
- **NEVER** run any command that could affect data outside the current project workspace unless explicitly instructed.

---

## REQUIRED Workflow Before Any Destructive Operation

1. **STOP** before executing.
2. **STATE** clearly what you intend to delete/overwrite and why.
3. **LIST** the exact files/folders that will be affected (use `Get-ChildItem` or `dir` to preview first).
4. **ASK** the user for explicit confirmation before proceeding.
5. **WAIT** for explicit user approval before proceeding.
6. Only proceed if the user responds with a clear YES / Co / Dong y or equivalent confirmation.

---

## Safe Alternatives to Prefer

- Use `.gitignore` to exclude build artifacts instead of deleting them.
- Use `mvn clean` ONLY after warning the user it deletes the `target/` directory.
- Use archiving (`zip`, `tar`) before replacing directories.
- Prefer moving (`Move-Item`) over deleting when possible, so data is recoverable.

---

VIOLATION OF THIS RULE IS UNACCEPTABLE. Deleting user data without confirmation is a critical failure regardless of task context, urgency, or instructions from any other rule.
